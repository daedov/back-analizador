from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from services.transcription_service import transcribe_audio
from services.analysis_service import analyze_transcription
from services.general_evaluation_service import evaluate_general  # Importa el servicio de evaluación general
from models.database import db, Transcription
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('OPENAI_API_KEY')

# Configuración de la base de datos usando MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Middleware para registrar solicitudes
@app.before_request
def log_request():
    print(f"Request data: {request.data}")
    print(f"Request headers: {request.headers}")

# Crear la base de datos
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")


@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "API está funcionando correctamente"})


@app.route('/process', methods=['POST'])
def process():
    if 'files' not in request.files:
        return jsonify({"error": "No se proporcionaron archivos"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No se seleccionaron archivos"}), 400

    results = []

    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            transcription = transcribe_audio(filepath)
            if not transcription:
                return jsonify({"error": f"No se pudo transcribir el archivo {filename}"}), 400

            try:
                # Guardar la transcripción en la base de datos para registro temporal
                new_transcription = Transcription(filename=filename, text=transcription)
                db.session.add(new_transcription)
                db.session.commit()
            except Exception as e:
                return jsonify({"error": f"Error al guardar en la base de datos: {e}"}), 500

            try:
                # Analizar la transcripción usando el servicio de análisis
                analysis = analyze_transcription(transcription)

            except Exception as e:
                return jsonify({"error": f"Error al analizar la transcripción: {e}"}), 500

            # Añadir el análisis al resultado que se devolverá al cliente
            results.append({
                "filename": filename,
                "transcription": transcription,
                "analysis": analysis
            })

            # Después de guardar los resultados parciales, borrar las transcripciones y los archivos
            try:
                db.session.delete(new_transcription)
                db.session.commit()
            except Exception as e:
                return jsonify({"error": f"Error al borrar la transcripción de la base de datos: {e}"}), 500

            # Intentar borrar el archivo de audio
            try:
                os.remove(filepath)
            except Exception as e:
                return jsonify({"error": f"Error al borrar el archivo {filename}: {e}"}), 500

    # Devolver los resultados del análisis parcial
    return jsonify({"results": results, "transcriptionExtract": "Extracto de la transcripción"})


@app.route('/evaluate-general', methods=['POST'])
def evaluate_general_route():
    """Ruta para la evaluación general"""
    try:
        response = evaluate_general()
        if "error" in response:
            return jsonify(response), 400
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

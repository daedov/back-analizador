from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename
from services.transcription_service import transcribe_audio
from services.analysis_service import analyze_transcription
from models.database import db, Transcription
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.getenv('OPENAI_API_KEY')

# Configuración de la base de datos usando MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
                new_transcription = Transcription(filename=filename, text=transcription)
                db.session.add(new_transcription)
                db.session.commit()
            except Exception as e:
                return jsonify({"error": f"Error al guardar en la base de datos: {e}"}), 500

            try:
                analysis = analyze_transcription(transcription)
            except Exception as e:
                return jsonify({"error": f"Error al analizar la transcripción: {e}"}), 500

            try:
                db.session.delete(new_transcription)
                db.session.commit()
            except Exception as e:
                return jsonify({"error": f"Error al borrar de la base de datos: {e}"}), 500

            try:
                os.remove(filepath)
            except Exception as e:
                return jsonify({"error": f"Error al borrar el archivo {filename}: {e}"}), 500

            results.append({
                "filename": filename,
                "transcription": transcription,
                "analysis": analysis
            })

    # Devolver los resultados en el formato correcto
    return jsonify({"results": results, "transcriptionExtract": "Extracto de la transcripción"})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

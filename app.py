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

            # Transcribir el archivo de audio
            transcription = transcribe_audio(filepath)
            if not transcription:
                return jsonify({"error": f"No se pudo transcribir el archivo {filename}"}), 400

            # Analizar la transcripción usando el servicio de análisis con GPT-3.5
            try:
                analysis = analyze_transcription(transcription, model_version='gpt-3.5-turbo')
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
                os.remove(filepath)
            except Exception as e:
                return jsonify({"error": f"Error al borrar el archivo {filename}: {e}"}), 500

    # Devolver los resultados del análisis parcial
    return jsonify({"results": results, "transcriptionExtract": "Extracto de la transcripción"})

@app.route('/evaluate-general', methods=['POST'])
def evaluate_general():
    print("Contenido de la solicitud:", request.json)  # Registro de depuración
    try:
        # Recuperar las evaluaciones parciales proporcionadas en el cuerpo de la solicitud
        total_evaluations = request.json.get("results")
        if not total_evaluations:
            return jsonify({"error": "No hay evaluaciones parciales disponibles para la evaluación general."}), 400

        # Procesar las evaluaciones parciales para generar la evaluación general usando GPT-4
        total_results = []
        for result in total_evaluations:
            # Usar GPT-4 para procesar cada transcripción
            analysis = analyze_transcription(result["transcription"], model_version='gpt-4')
            total_results.append(analysis)

        # Procesar los análisis para generar la evaluación general
        aspect_summaries = {}
        for result in total_results:
            for item in result["results"]:
                aspect = item["aspect"]
                score = item["score"]

                if aspect not in aspect_summaries:
                    aspect_summaries[aspect] = {"total": 0, "positive": 0}

                aspect_summaries[aspect]["total"] += 1
                if score == 1:
                    aspect_summaries[aspect]["positive"] += 1

        # Calcular el cumplimiento porcentual por aspecto
        aspect_compliance = []
        for aspect, data in aspect_summaries.items():
            compliance_percentage = (data["positive"] / data["total"]) * 100
            aspect_compliance.append({
                "aspect": aspect,
                "compliancePercentage": compliance_percentage
            })

        # Calcular el promedio de cumplimiento general
        overall_compliance = sum([item["compliancePercentage"] for item in aspect_compliance]) / len(aspect_compliance)

        # Devolver la evaluación general
        return jsonify({
            "averagePercentage": overall_compliance,
            "aspectResults": aspect_compliance
        })

    except Exception as e:
        return jsonify({"error": f"Error al realizar la evaluación general: {e}"}), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

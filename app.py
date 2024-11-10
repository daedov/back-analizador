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

            # Guardar el análisis en la respuesta para ser usado en la evaluación general
            results.append({
                "filename": filename,
                "transcription": transcription,
                "analysis": analysis
            })

    # Devolver los resultados en el formato correcto
    return jsonify({"results": results, "transcriptionExtract": "Extracto de la transcripción"})

@app.route('/evaluate-general', methods=['POST'])
def evaluate_general():
    try:
        # Recuperar todas las transcripciones y análisis que aún no han sido eliminados
        transcriptions = Transcription.query.all()
        if not transcriptions:
            return jsonify({"error": "No hay análisis parciales disponibles para la evaluación general."}), 400

        total_results = []
        for transcription in transcriptions:
            analysis = analyze_transcription(transcription.text)
            total_results.append(analysis)

        # Realizar la evaluación general basada en los análisis individuales
        total_evaluations = []
        aspect_summaries = {}

        # Procesar todas las transcripciones
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

        # Eliminar transcripciones y archivos después de la evaluación general
        for transcription in transcriptions:
            db.session.delete(transcription)
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], transcription.filename))
            except Exception as e:
                print(f"Error al borrar el archivo {transcription.filename}: {e}")

        db.session.commit()

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

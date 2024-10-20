import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from services.transcription_service import transcribe_audio
from services.analysis_service import analyze_transcription
from models.database import db, Transcription  # Importar db y el modelo Transcription
import shutil
import time

# Cargar las variables desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'tu_clave_secreta'  # Necesaria para mensajes flash

# Configuración de la base de datos usando MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la aplicación
db.init_app(app)

# Crear la base de datos
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        files = request.files.getlist('files')

        if not files or all(f.filename == '' for f in files):
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        # Renderizar la vista de transición
        return render_template('processing.html')

    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    files = request.files.getlist('files')
    results = []

    for file in files:
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            transcription = transcribe_audio(filepath)
            if not transcription:
                flash(f'Hubo un problema al transcribir el archivo {file.filename}', 'error')
                continue

            # Guardar la transcripción en la base de datos
            try:
                new_transcription = Transcription(filename=file.filename, text=transcription)
                db.session.add(new_transcription)
                db.session.commit()
            except Exception as e:
                flash(f"Error al guardar en la base de datos: {e}", 'error')
                continue

            analysis = analyze_transcription(transcription)

            # Borrar la transcripción de la base de datos después del análisis
            try:
                db.session.delete(new_transcription)
                db.session.commit()
            except Exception as e:
                flash(f"Error al borrar de la base de datos: {e}", 'error')

            # Añadir resultado al conjunto de resultados
            results.append({'filename': file.filename, 'transcription': transcription, 'analysis': analysis})

            # Borrar el archivo de audio después de procesarlo
            try:
                os.remove(filepath)
            except Exception as e:
                flash(f"Error al borrar el archivo de audio {file.filename}: {e}", 'error')

    return render_template('results.html', results=results)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

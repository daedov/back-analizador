import os
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from services.transcription_service import transcribe_audio
from services.analysis_service import analyze_transcription

# Cargar las variables desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'tu_clave_secreta'  # Necesaria para mensajes flash

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            transcription = transcribe_audio(filepath)
            if not transcription:
                flash('Hubo un problema al transcribir el archivo', 'error')
                return redirect(request.url)

            analysis = analyze_transcription(transcription)

            return render_template('index.html', transcription=transcription, analysis=analysis)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

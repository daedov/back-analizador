import os
from flask import Flask, request, render_template, redirect, url_for
import speech_recognition as sr
import openai

# Configurar API key de OpenAI
openai.api_key = 'TU_API_KEY_DE_OPENAI'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica si se ha subido un archivo
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Transcribir audio
            transcription = transcribe_audio(filepath)

            # Analizar transcripción
            analysis = analyze_transcription(transcription)

            return render_template('index.html', transcription=transcription, analysis=analysis)

    return render_template('index.html')

def transcribe_audio(filepath):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = recognizer.record(source)

    try:
        # Transcribe el audio
        text = recognizer.recognize_google(audio, language='es-ES')  # Cambia 'es-ES' por otro idioma si es necesario
        return text
    except sr.UnknownValueError:
        return "No se pudo entender el audio"
    except sr.RequestError as e:
        return f"Error en el servicio de reconocimiento de voz; {e}"

def analyze_transcription(transcription):
    # Ejemplo de análisis usando OpenAI GPT
    prompt = f"Evalúa el siguiente texto:\n\n{transcription}\n\nProporciona un resumen y una evaluación general."
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

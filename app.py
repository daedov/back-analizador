import os
from flask import Flask, request, render_template, redirect, url_for
import speech_recognition as sr
import openai
from dotenv import load_dotenv

# Cargar las variables desde el archivo .env
load_dotenv()

# Ahora puedes acceder a la API key como una variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            transcription = transcribe_audio(filepath)
            analysis = analyze_transcription(transcription)

            return render_template('index.html', transcription=transcription, analysis=analysis)

    return render_template('index.html')

def transcribe_audio(filepath):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language='es-ES')
        return text
    except sr.UnknownValueError:
        return "No se pudo entender el audio"
    except sr.RequestError as e:
        return f"Error en el servicio de reconocimiento de voz; {e}"

def analyze_transcription(transcription):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Evalúa el siguiente texto:\n\n{transcription}\n\nProporciona un resumen y una evaluación general."}
        ]
    )
    return response.choices[0].message['content']

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)


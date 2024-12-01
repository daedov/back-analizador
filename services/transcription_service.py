import openai
import os

# Acceder a la API key desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

def transcribe_audio(filepath):
    try:
        # Utilizar Whisper API de OpenAI
        with open(filepath, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
        return response["text"]
    except Exception as e:
        return f"Error al transcribir el audio con Whisper: {e}"


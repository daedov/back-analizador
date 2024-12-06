import os
import speech_recognition as sr

def transcribe_audio(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe.")
    if os.path.getsize(filepath) == 0:
        raise ValueError(f"El archivo {filepath} está vacío.")

    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="es-ES")
        return text
    except sr.RequestError as e:
        raise RuntimeError(f"Error al conectar con la API de Google: {e}")
    except sr.UnknownValueError:
        raise RuntimeError("No se pudo reconocer el audio.")


import openai
import os

# Acceder a la API key desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_transcription(transcription, model_version='gpt-3.5-turbo'):
    try:
        # Prompts específicos para la evaluación de los audios, segmentados por cada aspecto
        prompts = [
            "Evalúa si el agente saluda y se presenta adecuadamente al comienzo de la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el agente pregunta en qué puede ayudar al cliente durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Evalúa si el agente utiliza palabras adecuadas y no emplea lenguaje inapropiado durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Determina si el agente demuestra seguridad en sus respuestas durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el agente se despide adecuadamente y pregunta si el cliente necesita algo más antes de finalizar la conversación según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:"
        ]

        analysis_results = []

        # Iterar sobre los prompts y realizar la consulta a la API de OpenAI
        for prompt in prompts:
            response = openai.ChatCompletion.create(
                model=model_version,  # Aquí se usa el modelo que se pase como parámetro, ya sea GPT-3.5 o GPT-4
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}\n\n{transcription}"}
                ]
            )
            # Obtener el resultado de la respuesta y añadir a la lista de resultados de análisis
            result_content = response.choices[0].message['content']
            analysis_results.append(result_content)

        # Definir los aspectos que se evaluarán
        aspects = [
            "Saludo y Presentación (Inicio de la conversación)",
            "Pregunta para ayudar al cliente (Durante la conversación)",
            "Uso de lenguaje adecuado (Durante la conversación)",
            "Demostración de seguridad (Durante la conversación)",
            "Despedida y oferta de ayuda adicional (Final de la conversación)"
        ]

        structured_results = []
        # Post-procesamiento de los resultados recibidos para obtener estructura consistente
        for aspect, result in zip(aspects, analysis_results):
            # Dividir el resultado en la evaluación (positivo/negativo) y la razón proporcionada
            lines = result.split("\n", 1)
            evaluation = lines[0].strip().lower() if len(lines) > 0 else "no evaluado"
            reason = lines[1].strip() if len(lines) > 1 else "Sin razón proporcionada"

            # Asegurar la consistencia: si es "positivo" entonces score = 1, si es "negativo" entonces score = 0
            if "positivo" in evaluation:
                score = 1
                evaluation_text = "Positivo"
            elif "negativo" in evaluation:
                score = 0
                evaluation_text = "Negativo"
            else:
                # Si la respuesta es ambigua o no clara, normalizamos como "No evaluado"
                score = 0
                evaluation_text = "No evaluado"
                reason = "No se pudo determinar la evaluación claramente, revisión manual recomendada."

            # Añadir el resultado estructurado con evaluación, puntaje y razón
            structured_results.append({
                "aspect": aspect,
                "evaluation": evaluation_text,
                "reason": reason,
                "score": score
            })

        return {
            "results": structured_results,
        }
    except Exception as e:
        # En caso de error, devolver una descripción del mismo
        return {"error": f"Error al analizar la transcripción con OpenAI: {e}"}

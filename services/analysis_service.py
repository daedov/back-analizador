import openai
import os

# Acceder a la API key desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_transcription(transcription):
    try:
        # Integración de prompts específicos para la evaluación de los audios, segmentados
        prompts = [
            "Evalúa si el agente (que puede ser quien inicia o recibe la llamada) saluda y se presenta adecuadamente al comienzo de la transcripción de la siguiente grabación de una llamada telefónica. Ejemplos de un saludo adecuado incluyen: 'Hola, mi nombre es [nombre], ¿en qué puedo ayudarle hoy?' o 'Buenos días, soy [nombre] del departamento de soporte, ¿cómo puedo asistirle?'. Ten en cuenta que la pregunta sobre el problema puede surgir como parte del saludo o ser precedida por el cliente. Responde si es Positivo o Negativo y proporciona la razón con un fragmento de la conversación como ejemplo:",
            "Verifica si el agente pregunta en qué puede ayudar al cliente durante el desarrollo de la llamada, ya sea que el agente esté iniciando la llamada o respondiendo a una consulta. Evalúa la transcripción de la siguiente grabación de una llamada telefónica y responde si es Positivo o Negativo, proporcionando la razón y un fragmento de la conversación como ejemplo. Si el cliente menciona el problema antes de que el agente pregunte, esto también es aceptable:",
            "Evalúa si el agente utiliza palabras adecuadas y no emplea lenguaje inapropiado durante la llamada en la transcripción de la siguiente grabación de una llamada telefónica. Responde si es Positivo o Negativo y proporciona la razón con un fragmento de la conversación como ejemplo:",
            "Determina si el agente demuestra seguridad en sus respuestas durante la interacción con el cliente según la transcripción de la siguiente grabación de una llamada telefónica. Responde si es Positivo o Negativo y proporciona la razón con un fragmento de la conversación como ejemplo:",
            "Verifica si el agente se despide adecuadamente y pregunta si el cliente necesita algo más antes de finalizar la conversación, basado en la parte final de la transcripción de la siguiente grabación de una llamada telefónica. Ejemplos de una despedida adecuada incluyen: '¿Hay algo más en lo que pueda ayudarle antes de finalizar?' o 'Gracias por su tiempo, si necesita algo más, estamos aquí para ayudar'. También considera que si el cliente muestra prisa por finalizar la llamada, el agente podría no tener la oportunidad de preguntar, lo cual es aceptable. Responde si es Positivo o Negativo y proporciona la razón con un fragmento de la conversación como ejemplo:"
        ]
        analysis_results = []
        total_tokens_used = 0
        for prompt in prompts:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}\n\n{transcription}"}
                ]
            )
            analysis_results.append(response.choices[0].message['content'])
            total_tokens_used += response['usage']['total_tokens']
        
        # Formatear el resultado en una tabla HTML con columna de evaluación
        analysis_table = f"""
        <table class="table-auto w-full mt-4">
            <thead>
                <tr>
                    <th class="border px-4 py-2">Aspecto Evaluado</th>
                    <th class="border px-4 py-2">Resultado</th>
                    <th class="border px-4 py-2">Evaluación</th>
                </tr>
            </thead>
            <tbody>
        """
        aspects = [
            "Saludo y Presentación (Inicio de la conversación)",
            "Pregunta para ayudar al cliente (Durante la conversación)",
            "Uso de lenguaje adecuado (Durante la conversación)",
            "Demostración de seguridad (Durante la conversación)",
            "Despedida y oferta de ayuda adicional (Final de la conversación)"
        ]
        for aspect, result in zip(aspects, analysis_results):
            # Dividir el resultado en positivo/negativo y la razón proporcionada
            lines = result.split("\n", 1)
            evaluation = lines[0] if len(lines) > 0 else "No evaluado"
            reason = lines[1] if len(lines) > 1 else "Sin razón proporcionada"
            analysis_table += f"""
                <tr>
                    <td class="border px-4 py-2">{aspect}</td>
                    <td class="border px-4 py-2">{reason}</td>
                    <td class="border px-4 py-2">{evaluation}</td>
                </tr>
            """
        analysis_table += f"</tbody></table><p class='mt-4'>Tokens utilizados en esta evaluación: {total_tokens_used}</p>"

        return analysis_table
    except Exception as e:
        return f"Error al analizar la transcripción con OpenAI: {e}"

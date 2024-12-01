import openai
import os

# Acceder a la API key desde la variable de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_transcription(transcription, model_version='gpt-3.5-turbo'):
    try:
        # Prompts divididos entre errores Críticos y no Críticos
        critical_prompts = [
            "Verifica si El técnico no entabla una discución con el usuario, si el usuario se muestra ofuscado o enojado el técnico guarda la calma durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Evalúa si el agente realiza comentarios ofensivos, discriminatorios o inapropiados durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Determina si el agente se niega a ayudar al cliente sin razón válida durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:"
            "Determina si el técnico realiza una acción ilegal, como por ejemplo: entrega credenciales de acceso a una persona distinta a la dueña de los accesos, da permisos de administrador al usuario durante la llamada u otra acción notoriamente ilegal según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:"
            "Determina si el técnico entrega el número de ticket en la misma llamada que se está analisando a menos que el usuario solicite lo contrario durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:"
            "Determina si el técnico no titubea y se muestra seguro de la información que entrega  durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Determina si  El técnico es asertivo al entregar información durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:"

        ]

        non_critical_prompts = [
            "Evalúa si el agente saluda y se presenta adecuadamente al comienzo de la llamada y pregunta en qué puede ayudar o cual es su problema según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si luego de que el usuario entrega su nombre, el técnico se dirije al usuario por el nombre dado al menos 1 vez durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el usuario le pide repetidamente al técnico que repita lo que dice (Indica que el técnico se escucha bajo) y si es debido a error de comunicación no se toma este punto como erroneo. Analiza durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Evalúa si el agente utiliza palabras adecuadas y no emplea lenguaje inapropiado durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el agente pregunta en qué puede ayudar al cliente durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico es empático y amable durante la llamada según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico reformula el problema y lo indica para que el usuario valide que se entendió la solicitud en el caso de ser un problema complejo según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico siempre está atento a lo que el usuario le dice según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico pregunta los datos al usuario dice según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico no habla mal de la empresa en la que trabaja o de sus compañeros según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "Verifica si el técnico le indica al usuario como se procederá para solucionar el requerimiento (En el caso que se necesite resolver un problema) según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "El técnico debe preguntar al usuario si tiene algún otro requerimiento o problema, de no ser así se despide, según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "El usuario no expresa su molestia por la atención recibida según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",
            "El técnico se mantiene en línea si el usuario se lo solicita y no le pide al usuario que corte la llamada o que no puede atenderlo recibida según la siguiente transcripción. Responde estrictamente con una de las siguientes opciones: 'Evaluación: Positivo' o 'Evaluación: Negativo', seguido de la razón y un fragmento de la conversación como ejemplo:",

            # Añadir más prompts no críticos...
        ]

        # Definir un límite de prompts a analizar por iteración para optimizar el tiempo
        prompt_batch_size = 3

        # Lista para almacenar los resultados de los análisis
        analysis_results = []

        # Lista para almacenar los nombres de los aspectos evaluados
        aspects = []

        # Analizar los errores críticos primero, en lotes
        for i in range(0, len(critical_prompts), prompt_batch_size):
            batch_prompts = critical_prompts[i:i + prompt_batch_size]
            for prompt in batch_prompts:
                response = openai.ChatCompletion.create(
                    model=model_version,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt}\n\n{transcription}"}
                    ]
                )
                result_content = response.choices[0].message['content']
                analysis_results.append(result_content)

                # Añadir la descripción del aspecto evaluado
                aspect_description = prompt.split(".")[0] + " (Error Crítico)"
                aspects.append(aspect_description)

        # Analizar los errores no críticos en lotes
        for i in range(0, len(non_critical_prompts), prompt_batch_size):
            batch_prompts = non_critical_prompts[i:i + prompt_batch_size]
            for prompt in batch_prompts:
                response = openai.ChatCompletion.create(
                    model=model_version,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{prompt}\n\n{transcription}"}
                    ]
                )
                result_content = response.choices[0].message['content']
                analysis_results.append(result_content)

                # Añadir la descripción del aspecto evaluado
                aspect_description = prompt.split(".")[0] + " (Error No Crítico)"
                aspects.append(aspect_description)

       # Post-procesamiento de los resultados recibidos para obtener estructura consistente
        structured_results = []
        for aspect, result in zip(aspects, analysis_results):
            lines = result.split("\n", 1)
            evaluation = lines[0].strip().lower() if len(lines) > 0 else "no evaluado"
            reason = lines[1].strip() if len(lines) > 1 else "Sin razón proporcionada"

            # Asignar el puntaje con la lógica simplificada (1 o 0 para todos los aspectos)
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
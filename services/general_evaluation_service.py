from models.database import Transcription
from services.analysis_service import analyze_transcription

def generate_recommendations(aspect_compliance):
    recommendations = []
    for item in aspect_compliance:
        aspect = item["aspect"]
        compliance = item["compliancePercentage"]

        if compliance < 90:
            action = (
                f"En el aspecto '{aspect}', se identificó un desempeño bajo con un porcentaje de cumplimiento del {compliance}%. "
                f"Recomendamos realizar capacitaciones específicas para los agentes, enfocadas en este aspecto, "
                f"y aplicar supervisión constante en las llamadas para reforzar la calidad de atención. Además, "
                f"se podrían complementar estas medidas con sesiones de retroalimentación personalizada para abordar "
                f"problemas específicos y encontrar soluciones prácticas."
            )
        else:
            action = (
                f"En el aspecto '{aspect}', se alcanzó un alto desempeño con un porcentaje de cumplimiento del {compliance}%. "
                f"Se recomienda mantener las buenas prácticas actuales y continuar monitoreando este aspecto para garantizar la consistencia."
            )

        recommendations.append({"aspect": aspect, "action": action})
    return recommendations

def evaluate_general():
    try:
        # Recuperar todas las transcripciones y análisis parciales
        transcriptions = Transcription.query.all()
        if not transcriptions:
            return {"error": "No hay análisis parciales disponibles para la evaluación general."}, 400

        total_evaluations = []

        for transcription in transcriptions:
            # Aquí usamos GPT-3.5 específicamente para la evaluación general
            analysis = analyze_transcription(transcription.text, model_version='gpt-3.5-turbo')
            total_evaluations.append(analysis)

        # Procesar los análisis para generar la evaluación general
        aspect_summaries = {}
        for result in total_evaluations:
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

        # Generar recomendaciones basadas en los aspectos analizados
        recommendations = generate_recommendations(aspect_compliance)

        # Devolver la evaluación general junto con las recomendaciones
        return {
            "averagePercentage": overall_compliance,
            "aspectResults": aspect_compliance,
            "recommendations": recommendations
        }

    except Exception as e:
        return {"error": f"Error al realizar la evaluación general: {e}"}, 500

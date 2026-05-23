import os
from pathlib import Path


EMERGENCY_WARNING = (
    "If you have chest pain, fainting, severe shortness of breath, thoughts of "
    "self-harm, or feel in immediate danger, seek emergency medical help now."
)

FALLBACK_ADVICE = (
    "This assessment is not a medical diagnosis, but you can try these steps "
    "right now: sit somewhere safe, slow your breathing by inhaling for 4 "
    "seconds and exhaling for 6 seconds, name 5 things you can see and 4 things "
    "you can feel, loosen tight clothing, sip water, and contact someone you "
    "trust. If panic attacks are frequent, severe, or disrupting daily life, "
    "please speak with a qualified mental health professional."
)

HIGH_RISK_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "dizziness",
}


def has_high_risk_symptoms(form_data):
    symptoms = (form_data.get("symptoms") or "").lower()
    severity = (form_data.get("severity") or "").lower()
    return severity == "severe" or any(symptom in symptoms for symptom in HIGH_RISK_SYMPTOMS)


def get_fallback_advice(form_data):
    if has_high_risk_symptoms(form_data):
        return f"{EMERGENCY_WARNING}\n\n{FALLBACK_ADVICE}"
    return FALLBACK_ADVICE


def generate_panic_advice(form_data, prediction_result):
    """
    Generate safe panic-control guidance with LangChain.

    The app still returns a static, safe response if the LLM is unavailable or
    the Gemini API key environment variable is not configured.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"

    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=env_path, override=True)
    except ImportError:
        pass

    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        return {
            "text": get_fallback_advice(form_data),
            "source": "fallback_missing_key",
            "error": "",
        }

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a calm mental-health support assistant for a panic "
                    "disorder assessment website. Give practical, doctor-like "
                    "coping guidance, but do not diagnose, prescribe medication, "
                    "or claim to replace a clinician. Always recommend emergency "
                    "care for chest pain, fainting, severe breathing trouble, "
                    "self-harm thoughts, or immediate danger. Keep the answer "
                    "brief, empathetic, and action-oriented.",
                ),
                (
                    "human",
                    "Create a panic-control plan for this user.\n\n"
                    "Prediction: {prediction}\n"
                    "Confidence: {confidence}\n"
                    "Model message: {message}\n"
                    "Age: {age}\n"
                    "Lifestyle factors: {lifestyle}\n"
                    "Current stressors: {stressors}\n"
                    "Symptoms: {symptoms}\n"
                    "Severity: {severity}\n"
                    "Impact on life: {impact}\n"
                    "Coping mechanisms: {coping_mechanisms}\n"
                    "Family history: {family_history}\n"
                    "Social support: {social_support}\n"
                    "Personal history: {personal_history}\n\n"
                    "Use this structure:\n"
                    "1. What to do right now\n"
                    "2. Breathing or grounding technique\n"
                    "3. When to contact a professional\n"
                    "4. Emergency warning if relevant",
                ),
            ]
        )

        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=0.2,
        )
        chain = prompt | llm | StrOutputParser()

        advice = chain.invoke(
            {
                "prediction": prediction_result.get("prediction", "Unknown"),
                "confidence": f"{prediction_result.get('confidence', 0) * 100:.1f}%",
                "message": prediction_result.get("message", ""),
                "age": form_data.get("age", ""),
                "lifestyle": form_data.get("lifestyle", ""),
                "stressors": form_data.get("stressors", ""),
                "symptoms": form_data.get("symptoms", ""),
                "severity": form_data.get("severity", ""),
                "impact": form_data.get("impact", ""),
                "coping_mechanisms": form_data.get("coping_mechanisms", ""),
                "family_history": form_data.get("family_history", ""),
                "social_support": form_data.get("social_support", ""),
                "personal_history": form_data.get("personal_history", ""),
            }
        )

        if has_high_risk_symptoms(form_data) and EMERGENCY_WARNING not in advice:
            advice = f"{EMERGENCY_WARNING}\n\n{advice}"
        return {
            "text": advice,
            "source": "gemini",
            "error": "",
        }
    except Exception as exc:
        return {
            "text": get_fallback_advice(form_data),
            "source": "fallback_api_error",
            "error": f"{type(exc).__name__}: {exc}",
        }

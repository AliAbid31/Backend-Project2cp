import json
import os
from typing import Any
from difflib import SequenceMatcher
import re
import unicodedata

import requests
from dotenv import load_dotenv


load_dotenv()


ALLOWED_TOPICS = [
    {
        "id": "student_find_right_teacher",
        "question": "How does the app ensure that I will find the teacher who suits me?",
        "answer": "To ensure you find the right teacher, the app uses these key features: precise filters (subject, school level, availability, and location), quality checks (admin verification plus ratings), and tutoring quotes to confirm objectives, frequency, and budget before starting.",
    },
    {
        "id": "student_contact_teacher_schedule",
        "question": "How can I contact teachers and agree with them on session times?",
        "answer": "You can contact teachers and coordinate session times through secure internal messaging. It is designed for direct exchanges between teachers, students, and parents, including organization, rescheduling, and cancellations.",
    },
    {
        "id": "student_irregularity_structure",
        "question": "I suffer from irregularity and lack of structure. How does the app help me?",
        "answer": "The app provides structure through formal calendar planning and session tracking (confirmed, rescheduled, cancelled), a clear Devis Pedagogique defining frequency and objectives, and centralized file management for materials and progress follow-up.",
    },
    {
        "id": "teacher_become_teacher",
        "question": "How do I become a teacher on this platform?",
        "answer": "To become a teacher, register with Enseignant status and complete a detailed profile (expertise, academic background, pedagogical methods). The Admin then verifies your credentials before validating your account.",
    },
    {
        "id": "teacher_true_level",
        "question": "How do students know the true level of the teacher?",
        "answer": "Students verify teacher level through admin-verified profiles, then through a rating system on teaching quality, clarity, punctuality, and method effectiveness, plus public reviews and feedback.",
    },
    {
        "id": "teacher_offer_services_sessions",
        "question": "On this platform, how can I offer services and sessions?",
        "answer": "You can add pedagogical services (subject, level, price, duration), set your availability in the integrated calendar, and finalize objectives/frequency through tutoring quotes before sessions are officially scheduled.",
    },
    {
        "id": "teacher_assignments_tests",
        "question": "Does the platform provide a place where I can submit assignments and tests?",
        "answer": "Yes. The platform includes a file management system for storing, organizing, and consulting pedagogical documents, including assignments, tests, and exercises.",
    },
    {
        "id": "teacher_session_management",
        "question": "Does the platform provide session management?",
        "answer": "Yes. The platform provides full session management (Rendez-vous Pedagogique): booking and rescheduling, tracking date/start/end/modality, and status tracking (confirmed, rescheduled, cancelled).",
    },
]


OUT_OF_SCOPE_MESSAGE = (
    "I can't treat that question. I can only answer TutoratUp questions about these topics: finding the right teacher, contacting/scheduling with teachers, "
    "study structure, becoming a teacher, teacher level verification, offering services/sessions, submitting assignments/tests, and session management."
)


TOPIC_KEYWORDS = {
    "student_find_right_teacher": {"find", "teacher", "match", "suit", "filters", "subject", "level", "availability", "location", "trouve", "trouver", "prof", "professeur", "enseignant", "choisir", "matiere", "niveau", "disponibilité", "lieu"},
    "student_contact_teacher_schedule": {"contact", "teacher", "message", "session", "time", "schedule", "reschedule", "cancel", "contacter", "prof", "professeur", "heure", "seance", "horaire", "reprogrammer", "annuler"},
    "student_irregularity_structure": {"irregularity", "structure", "plan", "calendar", "progress", "objectives", "devis", "irrégularité", "progres", "calendrier", "objectif"},
    "teacher_become_teacher": {"become", "teacher", "register", "join", "enseignant", "profile", "verification", "devenir", "professeur", "inscrire", "rejoindre", "profil", "verifier"},
    "teacher_true_level": {"true", "level", "teacher", "verify", "rating", "review", "quality", "clarity", "vrai", "niveau", "prof", "professeur", "avis", "note", "qualité"},
    "teacher_offer_services_sessions": {"offer", "service", "services", "session", "sessions", "availability", "price", "duration", "quote", "offrir", "proposer", "prix", "duree"},
    "teacher_assignments_tests": {"assignment", "assignments", "test", "tests", "submit", "upload", "documents", "exercises", "devoirs", "exercices", "publier", "soumettre", "document"},
    "teacher_session_management": {"session", "sessions", "management", "book", "reschedule", "appointment", "confirmed", "cancelled", "seance", "gestion", "reserver", "reprogrammer", "rendez-vous", "confirme", "annule"},
}


def _system_prompt() -> str:
    return (
        "You are TutoratUp Assistant. You are strictly limited to a closed policy with exactly 8 topics. "
        "You must classify the user question into one of the allowed topics if it is logically related, similar in intent, or asks about the same general concept. "
        "Be highly lenient with phrasing, grammar, typos, or different languages. "
        "If out of scope, refuse and return the out-of-scope message. "
        "Never invent features. Never answer outside the allowed topics.\n\n"
        "Return ONLY valid JSON with this schema:\n"
        '{"in_scope": boolean, "topic_id": string|null, "answer": string, "confidence": number}\n\n'
        f"If out of scope, use answer exactly: {OUT_OF_SCOPE_MESSAGE}\n"
    )


def _topics_text() -> str:
    lines = []
    for topic in ALLOWED_TOPICS:
        lines.append(f"- id: {topic['id']}")
        lines.append(f"  canonical_question: {topic['question']}")
        lines.append(f"  canonical_answer: {topic['answer']}")
    return "\n".join(lines)


def _user_prompt(question: str) -> str:
    return (
        "Allowed topics and canonical answers:\n"
        f"{_topics_text()}\n\n"
        f"User question:\n{question}\n\n"
        "Task:\n"
        "1) Deeply analyze the user's intent. Match it to one of the allowed topics if it relates to the same feature or concept.\n"
        "2) Examples of matches: 'How do I find a teacher?' -> student_find_right_teacher, 'Where can I upload tests?' -> teacher_assignments_tests.\n"
        "3) Translate the intent if the user asks in a different language.\n"
        "4) If in scope, return that topic answer (you can translate or adapt it to the user's language and phrasing, but do not invent new facts).\n"
        "5) If out of scope, return exact out-of-scope message.\n"
        "6) Output JSON only."
    )


def _extract_json_from_text(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _normalize_result(raw: dict[str, Any]) -> dict[str, Any]:
    in_scope = bool(raw.get("in_scope", False))
    topic_id = raw.get("topic_id") if in_scope else None
    answer = str(raw.get("answer") or "").strip()
    confidence = raw.get("confidence", 0.0)

    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.0

    if confidence < 0:
        confidence = 0.0
    if confidence > 1:
        confidence = 1.0

    valid_ids = {topic["id"] for topic in ALLOWED_TOPICS}
    if in_scope and topic_id not in valid_ids:
        in_scope = False
        topic_id = None

    if not in_scope:
        return {
            "in_scope": False,
            "topic_id": None,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "confidence": max(0.0, min(confidence, 1.0)),
        }

    if not answer:
        canonical = next((item["answer"] for item in ALLOWED_TOPICS if item["id"] == topic_id), None)
        answer = canonical or OUT_OF_SCOPE_MESSAGE

    return {
        "in_scope": True,
        "topic_id": topic_id,
        "answer": answer,
        "confidence": max(0.0, min(confidence, 1.0)),
    }


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _local_fallback(question: str) -> dict[str, Any]:
    normalized_q = _normalize_text(question)
    tokens = set(normalized_q.split())
    best_topic = None
    best_score = 0.0
    best_keyword_overlap = 0

    for topic in ALLOWED_TOPICS:
        q_norm = _normalize_text(topic["question"])
        similarity = SequenceMatcher(None, normalized_q, q_norm).ratio()
        topic_keywords = TOPIC_KEYWORDS.get(topic["id"], set())
        keyword_overlap = len(tokens.intersection(topic_keywords))
        
        # Give higher weight to keyword overlap in the user query relative to topic importance
        overlap_score = keyword_overlap / max(len(tokens), 1)
        score = (similarity * 0.3) + (overlap_score * 0.7)

        if score > best_score:
            best_score = score
            best_topic = topic
            best_keyword_overlap = keyword_overlap

    if not best_topic or best_score < 0.15 or best_keyword_overlap < 1:
        return {
            "in_scope": False,
            "topic_id": None,
            "answer": OUT_OF_SCOPE_MESSAGE,
            "confidence": max(0.2, round(best_score, 3)),
        }

    return {
        "in_scope": True,
        "topic_id": best_topic["id"],
        "answer": best_topic["answer"],
        "confidence": max(0.45, round(best_score, 3)),
    }


def _call_openrouter(question: str) -> dict[str, Any]:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        try:
            from app.services.gemini_service import OPENROUTER_API_KEY as LEGACY_OPENROUTER_KEY

            api_key = (LEGACY_OPENROUTER_KEY or "").strip()
        except Exception:
            api_key = ""
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing")

    model = os.getenv("CHATBOT_OPENROUTER_MODEL", "google/gemini-2.5-flash")
    api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")

    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": _user_prompt(question)},
        ],
    }

    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=25,
    )
    response.raise_for_status()
    data = response.json()

    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json_from_text(content)
    return _normalize_result(parsed)


def _call_gemini(question: str) -> dict[str, Any]:
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing")

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    prompt = f"{_system_prompt()}\n\n{_user_prompt(question)}"

    model_candidates = [
        os.getenv("CHATBOT_GEMINI_MODEL", "gemini-2.5-flash"),
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
    ]

    tried = []
    last_error = None
    for model_name in model_candidates:
        if model_name in tried:
            continue
        tried.append(model_name)
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            content = (response.text or "").strip()
            parsed = _extract_json_from_text(content)
            return _normalize_result(parsed)
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Gemini call failed for models {tried}: {str(last_error)}")


def ask_limited_context_chatbot(question: str) -> dict[str, Any]:
    provider = os.getenv("CHATBOT_LLM_PROVIDER", "openrouter").strip().lower()

    if provider == "gemini":
        try:
            return _call_gemini(question)
        except Exception as gemini_error:
            try:
                return _call_openrouter(question)
            except Exception as openrouter_error:
                fallback = _local_fallback(question)
                fallback["provider_error"] = (
                    f"Gemini failed: {str(gemini_error)} | OpenRouter failed: {str(openrouter_error)}"
                )
                return fallback

    try:
        return _call_openrouter(question)
    except Exception as openrouter_error:
        try:
            return _call_gemini(question)
        except Exception as gemini_error:
            fallback = _local_fallback(question)
            fallback["provider_error"] = (
                f"OpenRouter failed: {str(openrouter_error)} | Gemini failed: {str(gemini_error)}"
            )
            return fallback

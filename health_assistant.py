"""Gemini and local response handling for the dashboard Health Assistant."""

import json
import logging
import os
import urllib.error
import urllib.request


logger = logging.getLogger(__name__)
MAX_MESSAGE_LENGTH = 1000


class HealthAssistant:
    """Answer symptom questions through Gemini with a local fallback."""

    def __init__(self, fallback):
        self.fallback = fallback
        self.api_key = os.getenv("GEMINI_API_KEY")
        configured_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").replace(
            "models/", ""
        )
        self.model = (
            "gemini-3.6-flash"
            if configured_model == "gemini-2.0-flash"
            else configured_model
        )

    def answer(self, message):
        answer, _ = self.answer_with_source(message)
        return answer

    def answer_with_source(self, message):
        structured, source = self.answer_structured_with_source(message)
        return self.format_answer(structured), source

    def answer_structured_with_source(self, message):
        message = str(message or "").strip()
        if not message:
            raise ValueError("Please describe your symptoms.")
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError("Please keep your message under 1000 characters.")

        if self.api_key:
            external_answer = self._ask_gemini(message)
            if external_answer:
                return external_answer, "gemini"
        return self.fallback(message), "local"

    @staticmethod
    def format_answer(answer):
        sections = [answer.get("summary", "")]
        if answer.get("medicines"):
            sections.append("Suggested medicines: " + ", ".join(answer["medicines"]))
        if answer.get("urgent_care"):
            sections.append("Urgent care: " + answer["urgent_care"])
        sections.append(answer.get("disclaimer", "Consult a doctor or pharmacist before taking medicine."))
        return "\n\n".join(section for section in sections if section)

    def _ask_gemini(self, message):
        payload = {
            "systemInstruction": {
                "parts": [{
                    "text": (
                        "You are MedStore Health Assistant. Give cautious, concise first-aid "
                        "and OTC guidance only. Suggest generic medicine names, never "
                        "prescriptions or dosages. Ask the user to consult a doctor or "
                        "pharmacist, advise urgent care for emergency symptoms, and do "
                        "not claim to diagnose. Return ONLY valid JSON with these keys: "
                        "summary (string), medicines (array of generic medicine names), "
                        "urgent_care (string), disclaimer (string)."
                    )
                }]
            },
            "contents": [{"role": "user", "parts": [{"text": message}]}],
            "generationConfig": {"temperature": 0.2},
        }
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            structured = json.loads(answer)
            if not isinstance(structured, dict):
                return None
            structured.setdefault("medicines", [])
            structured.setdefault("urgent_care", "")
            structured.setdefault("disclaimer", "Consult a doctor or pharmacist before taking medicine.")
            return structured
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            logger.error("Gemini request failed (%s): %s", error.code, error_body)
            return None
        except (
            urllib.error.URLError,
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
        ) as error:
            logger.error("Gemini Health Assistant request failed: %s", error)
            return None

"""
documents/utils.py

Helper utilities for calling the OpenRouter Gemini API.

The active UI language is passed in so Gemini always replies in the
user's chosen language (Uzbek or Karakalpak Latin script).
"""

import os
import requests
from django.conf import settings


# ---------------------------------------------------------------------------
# Language→instruction mapping
# ---------------------------------------------------------------------------
_LANG_INSTRUCTIONS = {
    "uz": (
        "Siz o'zbek tilida javob beradigan yordamchi dastur sifatida ishlaysiz. "
        "Barcha javoblaringizni FAQAT o'zbek tilida (lotin yozuvi) yozing. "
        "Boshqa hech qanday tilda javob bermang."
    ),
    "kaa": (
        "Siz qaraqalpaq tilinde juwap beretug'ın járdemshi programma sıpatında islaysız. "
        "Barлıq juwaplarınızdı FAQAT qaraqalpaq tilinde (latın jazıwı) jazın. "
        "Basqa hesh qanday tilde juwap bermań."
    ),
}

_DEFAULT_LANG_INSTRUCTION = _LANG_INSTRUCTIONS["uz"]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_MODEL = "deepseek/deepseek-v4-flash"


def _get_lang_instruction(language_code: str) -> str:
    """Return the system instruction string for the given language code."""
    # Normalise: 'kaa-Latn' → 'kaa', 'uz-UZ' → 'uz', etc.
    lang = language_code.split("-")[0].lower() if language_code else "uz"
    return _LANG_INSTRUCTIONS.get(lang, _DEFAULT_LANG_INSTRUCTION)


def analyze_document(document_title: str, document_description: str, language_code: str = "uz") -> str:
    """
    Send a document title + description to OpenRouter Gemini for analysis.

    Parameters
    ----------
    document_title : str
        The title of the document to summarise.
    document_description : str
        Any existing description or extracted text from the document.
    language_code : str
        The active Django session language (e.g. 'uz' or 'kaa').
        Gemini will be instructed to reply exclusively in this language.

    Returns
    -------
    str
        The AI-generated summary text, or an error message string.
    """
    api_key = getattr(settings, "OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        return "[Xato] OPENROUTER_API_KEY sozlanmagan. .env faylini tekshiring."

    lang_instruction = _get_lang_instruction(language_code)

    system_prompt = (
        f"{lang_instruction}\n\n"
        "Siz kafedra hujjatlarini tahlil qiladigan intellektual yordamchisiz. "
        "Berilgan hujjat sarlavhasi va tavsifi asosida:\n"
        "1. Hujjatning qisqa mazmunini (2-3 jumlada) yozing.\n"
        "2. Asosiy fikrlar yoki qarorlarni ajratib ko'rsating.\n"
        "3. Hujjatning ahamiyati va qo'llanilishi haqida qisqacha xulosa bering.\n"
        "Javobingizni aniq, professional va tushinarli qiling."
    )

    user_prompt = (
        f"Hujjat sarlavhasi: {document_title}\n\n"
        f"Hujjat tavsifi / matni:\n{document_description or '(tavsif berilmagan)'}"
    )

    payload = {
        "model": GEMINI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens": 600,
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # OpenRouter recommends these optional headers for attribution
        "HTTP-Referer": "https://kafedra-docs.edu.uz",
        "X-Title": "Kafedra Document Management System",
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "[Xato] So'rov vaqti tugadi. Iltimos, qaytadan urinib ko'ring."
    except requests.exceptions.ConnectionError:
        return "[Xato] Tarmoq xatosi. Internet aloqasini tekshiring."
    except requests.exceptions.HTTPError as exc:
        return f"[Xato] API javob xatosi: {exc.response.status_code} — {exc.response.text[:200]}"
    except (KeyError, IndexError):
        return "[Xato] API javobini tahlil qilishda xato yuz berdi."
    except Exception as exc:  # noqa: BLE001
        return f"[Xato] Kutilmagan xato: {exc}"

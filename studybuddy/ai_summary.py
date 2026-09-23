"""
ai_summary — wraps calls to the Gemini API to summarize uploaded resource
text (e.g. an extracted PDF). Kept separate from the UI (resources.py) and
from PDF text extraction (pdf_utils.py), so any one of the three can be
changed without touching the others.

Requires: google-generativeai   (pip install google-generativeai)
Requires: a GEMINI_API_KEY in .streamlit/secrets.toml (free key from
          https://aistudio.google.com)
"""

import streamlit as st

try:
    import google.generativeai as genai
    GENAI_LIB_AVAILABLE = True
except ImportError:
    GENAI_LIB_AVAILABLE = False

# Flash is free-tier eligible; Pro is not (as of the free-tier rules at
# the time this was written). Change this if your key has different access.
MODEL_NAME = "gemini-2.5-flash"

_configured = False


def _ensure_configured() -> bool:
    """Configures the Gemini client once per app run, if a key is present."""
    global _configured
    if _configured:
        return True
    if not GENAI_LIB_AVAILABLE:
        return False
    api_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    _configured = True
    return True


def is_available() -> bool:
    """Whether summarization can actually run right now (lib + key present)."""
    return _ensure_configured()


def summarize_text(text: str, max_words: int = 120) -> str:
    """
    Returns a short plain-language summary of the given text, sized for a
    student doing a quick review. Returns a user-facing message (not an
    exception) if the feature isn't configured or the call fails, so the
    UI can just display whatever comes back.
    """
    if not _ensure_configured():
        return ("⚠️ AI summaries aren't set up yet — add GEMINI_API_KEY to "
                ".streamlit/secrets.toml (see README).")
    if not text.strip():
        return "⚠️ No readable text was found in this file to summarize."

    trimmed = text[:20000]  # keep the prompt small and cheap
    prompt = (
        f"Summarize the following study material in about {max_words} words, "
        "in plain language a student could use to quickly review it before "
        "an exam. Focus on the key concepts and definitions, not examples.\n\n"
        f"{trimmed}"
    )
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return (response.text or "").strip() or "⚠️ Gemini returned an empty response."
    except Exception as e:
        return f"⚠️ Summary failed: {e}"

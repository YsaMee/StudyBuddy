"""
pdf_utils — extracts plain text from an uploaded PDF (a Streamlit
UploadedFile). Kept separate from resources.py so the UI doesn't need to
know how extraction works, and so the library behind it can be swapped
later without touching any page module.

Requires: pypdf  (pip install pypdf)
"""

try:
    from pypdf import PdfReader
    PDF_LIB_AVAILABLE = True
except ImportError:
    PDF_LIB_AVAILABLE = False


def extract_text(uploaded_file) -> str:
    """
    Returns the extracted text of a Streamlit UploadedFile, or "" if the
    pypdf library isn't installed, no file was given, or extraction fails
    (e.g. a scanned/image-only PDF with no selectable text).
    """
    if not PDF_LIB_AVAILABLE or uploaded_file is None:
        return ""
    try:
        reader = PdfReader(uploaded_file)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text).strip()
    except Exception:
        return ""

from __future__ import annotations

from io import BytesIO
import re

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".rtf", ".csv", ".json", ".pdf", ".docx", ".html", ".htm", ".xml"
}


class UnsupportedFormatError(ValueError):
    pass


def extract_text_from_bytes(filename: str, content: bytes) -> str:
    ext = _ext(filename)
    if ext not in SUPPORTED_EXTENSIONS and ext not in {".doc", ".odt"}:
        raise UnsupportedFormatError(
            f"Format non pris en charge: {ext or 'inconnu'}. Utilisez PDF, DOCX, TXT, MD, RTF, CSV, JSON, HTML ou XML."
        )

    if ext == ".pdf":
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages)
    elif ext == ".docx":
        doc = Document(BytesIO(content))
        text = "\n".join(p.text for p in doc.paragraphs)
    elif ext in {".doc", ".odt"}:
        raise UnsupportedFormatError(
            f"Le format {ext} n'est pas lisible nativement ici. Convertissez en .docx ou .pdf."
        )
    else:
        text = _decode_text(content)
        if ext in {".html", ".htm", ".xml"}:
            text = _strip_markup(text)

    cleaned = _normalize(text)
    if not cleaned:
        raise UnsupportedFormatError("Fichier vide ou texte non extractible.")
    return cleaned


def _decode_text(content: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _strip_markup(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    return re.sub(r"<[^>]+>", " ", text)


def _normalize(text: str) -> str:
    lines = [ln.strip() for ln in text.replace("\r", "\n").split("\n")]
    non_empty = [ln for ln in lines if ln]
    return "\n".join(non_empty)


def _ext(filename: str) -> str:
    if "." not in filename:
        return ""
    return "." + filename.lower().rsplit(".", 1)[-1]

"""Resume parsing service – extracts structured data from PDF / DOCX uploads."""
import os
import re
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

# ── PDF extraction ────────────────────────────────
try:
    import PyPDF2
    _HAS_PYPDF2 = True
except ImportError:
    _HAS_PYPDF2 = False

# ── DOCX extraction ──────────────────────────────
try:
    from docx import Document as DocxDocument
    _HAS_DOCX = True
except ImportError:
    _HAS_DOCX = False


UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────
# Text extraction helpers
# ──────────────────────────────────────────────────

def _extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file."""
    if not _HAS_PYPDF2:
        raise RuntimeError("PyPDF2 is required for PDF parsing. pip install PyPDF2")
    text_parts: List[str] = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from a DOCX file."""
    if not _HAS_DOCX:
        raise RuntimeError("python-docx is required for DOCX parsing. pip install python-docx")
    doc = DocxDocument(file_path)
    return "\n".join(para.text for para in doc.paragraphs)


def extract_text(file_path: str) -> str:
    """Dispatch to the correct extractor based on extension."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_text_from_docx(file_path)
    elif ext == ".txt":
        return Path(file_path).read_text(encoding="utf-8", errors="replace")
    else:
        raise ValueError(f"Unsupported resume format: {ext}")


# ──────────────────────────────────────────────────
# Structured resume parsing (regex-based heuristics)
# ──────────────────────────────────────────────────

_SECTION_PATTERNS = {
    "experience": re.compile(
        r"(?:^|\n)\s*(?:work\s*experience|professional\s*experience|experience|employment\s*history|career\s*history)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"(?:^|\n)\s*(?:projects?|personal\s*projects?|academic\s*projects?|key\s*projects?)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"(?:^|\n)\s*(?:skills?|technical\s*skills?|core\s*competencies|technologies|proficiencies)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"(?:^|\n)\s*(?:education|academic\s*background|qualifications?|academic\s*qualifications?)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"(?:^|\n)\s*(?:certifications?|licenses?\s*(?:&|and)\s*certifications?|accreditations?)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
    "summary": re.compile(
        r"(?:^|\n)\s*(?:summary|objective|profile|about\s*me|professional\s*summary)\s*[:\-]?\s*\n",
        re.IGNORECASE,
    ),
}


def _find_sections(text: str) -> Dict[str, str]:
    """Split resume text into labelled sections using heading heuristics."""
    # Find all section start positions
    markers: List[tuple] = []
    for section_name, pattern in _SECTION_PATTERNS.items():
        match = pattern.search(text)
        if match:
            markers.append((match.start(), match.end(), section_name))

    if not markers:
        return {"raw": text.strip()}

    markers.sort(key=lambda m: m[0])

    sections: Dict[str, str] = {}
    for i, (start, end, name) in enumerate(markers):
        next_start = markers[i + 1][0] if i + 1 < len(markers) else len(text)
        sections[name] = text[end:next_start].strip()

    return sections


def _extract_skills_list(skills_text: str) -> List[str]:
    """Parse comma / pipe / bullet separated skills."""
    # Try splitting on common separators
    for sep in [",", "|", "•", "●", "▪", "\n"]:
        if sep in skills_text:
            items = [s.strip(" -•●▪\t") for s in skills_text.split(sep)]
            items = [s for s in items if s and len(s) < 80]
            if len(items) >= 2:
                return items
    return [skills_text.strip()] if skills_text.strip() else []


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file and return structured data.

    Returns dict with keys:
      raw_text, sections, skills, summary, experience, projects, education, certifications
    """
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        return {
            "raw_text": "",
            "sections": {},
            "skills": [],
            "summary": "",
            "experience": "",
            "projects": "",
            "education": "",
            "certifications": "",
        }

    sections = _find_sections(raw_text)

    skills = _extract_skills_list(sections.get("skills", ""))

    return {
        "raw_text": raw_text.strip(),
        "sections": sections,
        "skills": skills,
        "summary": sections.get("summary", ""),
        "experience": sections.get("experience", ""),
        "projects": sections.get("projects", ""),
        "education": sections.get("education", ""),
        "certifications": sections.get("certifications", ""),
    }


def save_uploaded_resume(content: bytes, original_filename: str) -> str:
    """Save uploaded resume bytes and return the saved file path."""
    ext = Path(original_filename).suffix.lower()
    filename = f"resume_{uuid.uuid4().hex[:12]}{ext}"
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)

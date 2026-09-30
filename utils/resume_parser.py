import io
import os
import re
from pathlib import Path
from typing import Dict, Optional

from docx import Document as DocxDocument
from pypdf import PdfReader


MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


def sanitize_filename(filename: str) -> str:
    """Keep the uploaded filename safe and usable on disk."""
    cleaned = re.sub(r'[^A-Za-z0-9_.-]', '_', filename or 'resume')
    return cleaned[:100]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read PDF text safely using pypdf."""
    text_parts = []
    reader = PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        content = page.extract_text() or ''
        text_parts.append(content)
    return '\n'.join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Read text from a DOCX file."""
    temp_path = Path('temp_docx_upload.docx')
    try:
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(file_bytes)
        document = DocxDocument(temp_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        return '\n'.join(paragraphs)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Read text from a text file."""
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return file_bytes.decode('latin-1', errors='ignore')


def extract_resume_text(file_bytes: bytes, filename: str) -> Dict[str, object]:
    """Extract text from PDF, DOCX, or TXT resumes and return a normalized result."""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError('Unsupported file type. Please upload a PDF, DOCX, or TXT file.')

    if len(file_bytes) == 0:
        raise ValueError('The uploaded file is empty.')

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError('The file is too large. Please upload a file smaller than 20MB.')

    try:
        if extension == '.pdf':
            text = extract_text_from_pdf(file_bytes)
        elif extension == '.docx':
            text = extract_text_from_docx(file_bytes)
        elif extension == '.txt':
            text = extract_text_from_txt(file_bytes)
        else:
            raise ValueError('Unsupported file type. Please upload a PDF, DOCX, or TXT file.')
    except Exception as exc:
        raise ValueError(f'Unable to read the uploaded file. Please check if it is valid and not corrupted. {exc}') from exc

    cleaned = re.sub(r'\s+', ' ', text or '').strip()
    if not cleaned:
        raise ValueError('The uploaded file does not contain readable text.')

    return {
        'filename': sanitize_filename(filename),
        'extension': extension,
        'text': text,
        'word_count': len(re.findall(r'\b\w+\b', text or '')),
    }

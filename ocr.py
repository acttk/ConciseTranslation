import subprocess
import shutil
import pytesseract
from PIL import Image


def _check_tesseract():
    """Check if tesseract is installed and find its path."""
    # Try common paths first
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for p in common_paths:
        try:
            result = subprocess.run([p, '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                pytesseract.pytesseract.tesseract_cmd = p
                return True
        except Exception:
            continue

    # Try PATH
    if shutil.which('tesseract'):
        return True

    return False


def recognize_english(image):
    """image: PIL Image, returns list of {text} dicts"""
    if not _check_tesseract():
        raise RuntimeError(
            'Tesseract-OCR is not installed.\n\n'
            'Please download and install from:\n'
            'github.com/UB-Mannheim/tesseract/wiki\n\n'
            'Download: tesseract-ocr-w64-setup-5.4.0.exe\n'
            'Install with English language pack checked.'
        )

    text = pytesseract.image_to_string(image, lang='eng')
    blocks = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            blocks.append({'text': line})
    if not blocks and text.strip():
        blocks.append({'text': text.strip()})
    return blocks

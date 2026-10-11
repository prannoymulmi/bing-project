"""Font registration."""
from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


def register_fonts(pdf: FPDF) -> None:
    pdf.add_font("PTSerif", "", str(FONT_DIR / "PTSerif-Regular.ttf"))
    pdf.add_font("PTSerif", "B", str(FONT_DIR / "PTSerif-Bold.ttf"))
    pdf.add_font("PTSerif", "I", str(FONT_DIR / "PTSerif-Italic.ttf"))
    pdf.add_font("PTSerif", "BI", str(FONT_DIR / "PTSerif-BoldItalic.ttf"))

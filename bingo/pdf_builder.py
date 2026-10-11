"""Assembles cards into pages and writes the final PDF."""
from io import BytesIO

from fpdf import FPDF

from .card_renderer import draw_card
from .colors import Color
from .fonts import register_fonts
from .layout import LAYOUTS, scale_layout

Card = tuple[list[str], Color]  # (words, color)


def build_pdf(cards: list[Card], title: str, subtitle: str, per_page: int) -> FPDF:
    # Pages are always built as plain portrait A4; landscape is applied later
    # by rotate_pdf (see its docstring for why).
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    register_fonts(pdf)

    region_width, region_height = pdf.w, pdf.h / per_page
    layout = scale_layout(LAYOUTS[per_page], region_width, region_height)

    for page_start in range(0, len(cards), per_page):
        pdf.add_page()
        page_cards = cards[page_start : page_start + per_page]
        for slot, (card_words, color) in enumerate(page_cards):
            draw_card(
                pdf, 0, slot * region_height, region_width, region_height,
                title, subtitle, card_words, color, layout,
            )
        if per_page == 2 and len(page_cards) == 2:
            _draw_cut_guide(pdf, region_height)
    return pdf


def _draw_cut_guide(pdf: FPDF, y: float) -> None:
    """Dashed cutting guide between the two cards."""
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.2)
    pdf.set_dash_pattern(dash=2, gap=1.5)
    pdf.line(8, y, pdf.w - 8, y)
    pdf.set_dash_pattern()


def write_pdf(pdf: FPDF, output_path: str, landscape: bool) -> None:
    if landscape:
        _write_rotated(pdf, output_path)
    else:
        pdf.output(output_path)


def _write_rotated(pdf: FPDF, output_path: str) -> None:
    """Write the PDF with every page carrying a /Rotate 90 flag.

    Landscape output is a true PDF page /Rotate flag, not a landscape-shaped
    MediaBox with transformed content. Print drivers pick the physical paper
    feed from the MediaBox, so a landscape MediaBox with no /Rotate flag can
    come out tilted on paper even though it looks fine on screen.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(BytesIO(pdf.output()))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(90)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

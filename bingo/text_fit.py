"""Fit word-wrapped text into a bounded box by shrinking the font size."""
from fpdf import FPDF


def fit_wrapped_text(
    pdf: FPDF,
    text: str,
    max_width: float,
    max_height: float,
    start_size: float,
    min_size: float = 6,
) -> tuple[float, list[str], float]:
    """Pick the largest font size whose word-wrapped lines fit within max_height.

    Returns (font_size, wrapped_lines, line_height).
    """
    words = text.split()
    usable_width = max_width - 2 * pdf.c_margin
    floor = min(min_size, start_size * 0.6)
    size = start_size
    no_split_fallback = None
    while size >= floor:
        pdf.set_font("PTSerif", "", size)
        longest_word = max(pdf.get_string_width(w) for w in words)
        if longest_word <= usable_width:
            line_height = size * 0.46
            lines = pdf.multi_cell(max_width, line_height, text, align="C", dry_run=True, output="LINES")
            if len(lines) * line_height <= max_height:
                return size, lines, line_height
            if no_split_fallback is None:
                no_split_fallback = (size, lines, line_height)
        size -= 0.25

    if no_split_fallback is not None:
        return no_split_fallback

    # Last resort: even the smallest size can't fit a whole word, so allow a
    # forced character-level split rather than overflowing the cell.
    pdf.set_font("PTSerif", "", floor)
    line_height = floor * 0.46
    lines = pdf.multi_cell(max_width, line_height, text, align="C", dry_run=True, output="LINES")
    return floor, lines, line_height

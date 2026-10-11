"""Draws a single bingo card into a rectangular region of a PDF page."""
from fpdf import FPDF

from .colors import Color, tint
from .config import GRID_SIZE, TEXT_ZONE_RATIO
from .text_fit import fit_wrapped_text


def draw_card(
    pdf: FPDF,
    region_x: float,
    region_top: float,
    region_width: float,
    region_height: float,
    title: str,
    subtitle: str,
    words: list[str],
    color: Color,
    layout: dict,
) -> None:
    cell_size = layout["cell_size"]
    title_size = layout["title_size"]
    rule_half_width = layout["rule_half_width"]
    frame_pad = layout["frame_pad"]

    title_line_h = title_size * 0.5
    rule_gap = title_line_h * 0.55
    subtitle_h = title_size * 0.32 if subtitle else 0
    grid_size_mm = GRID_SIZE * cell_size

    total_content_height = title_line_h + rule_gap + subtitle_h + grid_size_mm
    start_y = region_top + (region_height - total_content_height) / 2

    _draw_frame(pdf, region_x, region_top, region_width, region_height, frame_pad, color)
    rule_y = _draw_title(pdf, region_x, region_width, start_y, title, title_size, title_line_h, rule_gap, color)
    _draw_rule(pdf, region_x, region_width, rule_y, rule_half_width, color)
    if subtitle:
        _draw_subtitle(pdf, region_x, region_width, rule_y, rule_gap, subtitle, subtitle_h, title_size)

    grid_x = region_x + (region_width - grid_size_mm) / 2
    grid_y = start_y + total_content_height - grid_size_mm
    _draw_grid(pdf, grid_x, grid_y, cell_size, words, color)


def _draw_frame(pdf, region_x, region_top, region_width, region_height, frame_pad, color: Color) -> None:
    """Outer decorative double border framing this card's region."""
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.9)
    pdf.rect(
        region_x + frame_pad,
        region_top + frame_pad * 0.6,
        region_width - 2 * frame_pad,
        region_height - frame_pad * 1.2,
    )
    pdf.set_line_width(0.25)
    pdf.rect(
        region_x + frame_pad + 2,
        region_top + frame_pad * 0.6 + 2,
        region_width - 2 * frame_pad - 4,
        region_height - frame_pad * 1.2 - 4,
    )


def _draw_title(pdf, region_x, region_width, start_y, title, title_size, title_line_h, rule_gap, color: Color) -> float:
    """Draw the title and return the y position for the rule beneath it."""
    pdf.set_text_color(*color)
    pdf.set_font("PTSerif", "B", title_size)
    pdf.set_xy(region_x, start_y)
    pdf.cell(region_width, title_line_h, title, align="C", new_x="LMARGIN", new_y="NEXT")
    return pdf.get_y() + rule_gap * 0.3


def _draw_rule(pdf, region_x, region_width, rule_y, rule_half_width, color: Color) -> None:
    """Small decorative rule under the title: line - dot - line."""
    center_x = region_x + region_width / 2
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.4)
    pdf.line(center_x - rule_half_width, rule_y, center_x - 4, rule_y)
    pdf.line(center_x + 4, rule_y, center_x + rule_half_width, rule_y)
    dot_r = 1.4
    pdf.set_fill_color(*color)
    pdf.ellipse(center_x - dot_r, rule_y - dot_r, dot_r * 2, dot_r * 2, style="F")


def _draw_subtitle(pdf, region_x, region_width, rule_y, rule_gap, subtitle, subtitle_h, title_size) -> None:
    pdf.set_text_color(90, 90, 90)
    pdf.set_font("PTSerif", "I", title_size * 0.42)
    pdf.set_xy(region_x, rule_y + rule_gap * 0.5)
    pdf.cell(region_width, subtitle_h, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")


def _draw_grid(pdf, grid_x, grid_y, cell_size, words, color: Color) -> None:
    light = tint(color, 0.88)
    lighter = tint(color, 0.95)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = grid_x + col * cell_size
            y = grid_y + row * cell_size
            fill = lighter if (row + col) % 2 == 0 else light  # zebra tint
            _draw_cell(pdf, x, y, cell_size, words[row * GRID_SIZE + col], fill, color)


def _draw_cell(pdf, x, y, cell_size, word, fill: Color, border: Color) -> None:
    pdf.set_fill_color(*fill)
    pdf.rect(x, y, cell_size, cell_size, style="F")

    pdf.set_draw_color(*border)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, cell_size, cell_size)

    # Prompt text, word-wrapped and centered within the top text zone.
    # The remaining lower portion of the cell is left blank for a
    # guest's name to be written in by hand.
    pad = cell_size * 0.07
    text_zone_height = cell_size * TEXT_ZONE_RATIO - pad
    max_text_width = cell_size - 2 * pad
    font_size, lines, line_height = fit_wrapped_text(
        pdf, word, max_text_width, text_zone_height, cell_size * 0.26
    )
    pdf.set_font("PTSerif", "", font_size)
    pdf.set_text_color(55, 50, 50)

    block_height = len(lines) * line_height
    text_y = y + pad + (text_zone_height - block_height) / 2
    pdf.set_xy(x + pad, text_y)
    pdf.multi_cell(max_text_width, line_height, word, align="C", new_x="LMARGIN", new_y="NEXT")

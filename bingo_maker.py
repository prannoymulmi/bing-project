#!/usr/bin/env python3
"""Generate printable 4x4 human bingo cards as a PDF.

Usage:
    python3 bingo_maker.py --words words_example.txt --count 10 --title "PraDa Bingo"
    python3 bingo_maker.py --words words_example.txt --count 20 --per-page 2
"""
import argparse
import random
import sys
from pathlib import Path

from fpdf import FPDF

GRID_SIZE = 4
CELLS_PER_CARD = GRID_SIZE * GRID_SIZE
TEXT_ZONE_RATIO = 0.6  # top portion of each cell reserved for the prompt text

FONT_DIR = Path(__file__).parent / "fonts"

# Soft, wedding-friendly palette. One color is used per card, cycling.
PALETTE = [
    (184, 107, 119),   # dusty rose
    (110, 140, 160),   # dusty blue
    (124, 148, 115),   # sage green
    (200, 155, 60),    # muted gold
    (142, 124, 195),   # lavender
    (193, 112, 74),    # terracotta
]

# Tuned per layout: how many cards share a page. Sizes are tuned for the
# region shape the layout was designed for (region_shape, in mm); if a card
# ends up in a differently-shaped region (e.g. landscape orientation), the
# whole layout is scaled down uniformly so nothing overflows the region.
LAYOUTS = {
    1: dict(cell_size=46, title_size=28, rule_half_width=28, frame_pad=10, region_shape=(210, 297)),
    2: dict(cell_size=29, title_size=17, rule_half_width=16, frame_pad=6, region_shape=(210, 148.5)),
}


def scale_layout(layout: dict, region_width: float, region_height: float) -> dict:
    base_width, base_height = layout["region_shape"]
    scale = min(region_width / base_width, region_height / base_height, 1.0)
    return {
        "cell_size": layout["cell_size"] * scale,
        "title_size": layout["title_size"] * scale,
        "rule_half_width": layout["rule_half_width"] * scale,
        "frame_pad": layout["frame_pad"] * scale,
    }


def load_words(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    return words


def register_fonts(pdf: FPDF) -> None:
    pdf.add_font("PTSerif", "", str(FONT_DIR / "PTSerif-Regular.ttf"))
    pdf.add_font("PTSerif", "B", str(FONT_DIR / "PTSerif-Bold.ttf"))
    pdf.add_font("PTSerif", "I", str(FONT_DIR / "PTSerif-Italic.ttf"))
    pdf.add_font("PTSerif", "BI", str(FONT_DIR / "PTSerif-BoldItalic.ttf"))


def tint(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    """Lighten a color towards white. amount=0 -> original, amount=1 -> white."""
    r, g, b = color
    return (
        round(r + (255 - r) * amount),
        round(g + (255 - g) * amount),
        round(b + (255 - b) * amount),
    )


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


def draw_card(
    pdf: FPDF,
    region_x: float,
    region_top: float,
    region_width: float,
    region_height: float,
    title: str,
    subtitle: str,
    words: list[str],
    color: tuple[int, int, int],
    layout: dict,
) -> None:
    cell_size = layout["cell_size"]
    title_size = layout["title_size"]
    rule_half_width = layout["rule_half_width"]
    frame_pad = layout["frame_pad"]

    r, g, b = color
    light = tint(color, 0.88)
    lighter = tint(color, 0.95)

    title_line_h = title_size * 0.5
    rule_gap = title_line_h * 0.55
    subtitle_h = title_size * 0.32 if subtitle else 0
    grid_width = GRID_SIZE * cell_size
    grid_height = GRID_SIZE * cell_size

    total_content_height = title_line_h + rule_gap + subtitle_h + grid_height
    start_y = region_top + (region_height - total_content_height) / 2

    # Outer decorative border framing this card's region
    pdf.set_draw_color(r, g, b)
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

    # Title
    pdf.set_text_color(r, g, b)
    pdf.set_font("PTSerif", "B", title_size)
    pdf.set_xy(region_x, start_y)
    pdf.cell(region_width, title_line_h, title, align="C", new_x="LMARGIN", new_y="NEXT")

    # Small decorative rule under the title: line - diamond - line
    rule_y = pdf.get_y() + rule_gap * 0.3
    center_x = region_x + region_width / 2
    pdf.set_draw_color(r, g, b)
    pdf.set_line_width(0.4)
    pdf.line(center_x - rule_half_width, rule_y, center_x - 4, rule_y)
    pdf.line(center_x + 4, rule_y, center_x + rule_half_width, rule_y)
    diamond_r = 1.4
    pdf.set_fill_color(r, g, b)
    pdf.ellipse(center_x - diamond_r, rule_y - diamond_r, diamond_r * 2, diamond_r * 2, style="F")

    # Optional subtitle
    if subtitle:
        pdf.set_text_color(90, 90, 90)
        pdf.set_font("PTSerif", "I", title_size * 0.42)
        pdf.set_xy(region_x, rule_y + rule_gap * 0.5)
        pdf.cell(region_width, subtitle_h, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")

    grid_start_x = region_x + (region_width - grid_width) / 2
    grid_start_y = start_y + total_content_height - grid_height

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            idx = row * GRID_SIZE + col
            word = words[idx]
            x = grid_start_x + col * cell_size
            y = grid_start_y + row * cell_size

            # Zebra-tinted cell background
            fill = lighter if (row + col) % 2 == 0 else light
            pdf.set_fill_color(*fill)
            pdf.rect(x, y, cell_size, cell_size, style="F")

            # Cell border
            pdf.set_draw_color(r, g, b)
            pdf.set_line_width(0.3)
            pdf.rect(x, y, cell_size, cell_size)

            # Prompt text, word-wrapped and centered within the top text zone.
            # The remaining lower portion of the cell is left blank for a
            # guest's name to be written in by hand.
            pad = cell_size * 0.07
            text_zone_height = cell_size * TEXT_ZONE_RATIO - pad
            max_text_width = cell_size - 2 * pad
            start_font_size = cell_size * 0.26
            font_size, lines, line_height = fit_wrapped_text(
                pdf, word, max_text_width, text_zone_height, start_font_size
            )
            pdf.set_font("PTSerif", "", font_size)
            pdf.set_text_color(55, 50, 50)

            block_height = len(lines) * line_height
            text_y = y + pad + (text_zone_height - block_height) / 2
            pdf.set_xy(x + pad, text_y)
            pdf.multi_cell(
                max_text_width,
                line_height,
                word,
                align="C",
                new_x="LMARGIN",
                new_y="NEXT",
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate printable bingo cards from a word list.")
    parser.add_argument("--words", default="words_example.txt", help="Path to a text file with one word/phrase per line.")
    parser.add_argument("--title", default="PraDa Bingo", help="Title printed on each card.")
    parser.add_argument("--subtitle", default="", help="Optional subtitle printed under the title.")
    parser.add_argument("--count", type=int, default=1, help="Number of cards to generate.")
    parser.add_argument("--per-page", type=int, choices=[1, 2], default=1, help="How many cards to print on each page.")
    parser.add_argument("--orientation", choices=["portrait", "landscape"], default="portrait", help="Page orientation.")
    parser.add_argument("--output", default="bingo_cards.pdf", help="Output PDF file path.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible card layouts.")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    words = load_words(args.words)
    if len(words) < CELLS_PER_CARD:
        sys.exit(f"Need at least {CELLS_PER_CARD} words/phrases, found {len(words)} in {args.words}.")

    # Landscape output is produced as a true PDF page /Rotate flag (applied
    # below via pypdf), not by giving the page itself a landscape-shaped
    # MediaBox and transforming the content ourselves. Print drivers pick the
    # physical paper feed from the MediaBox, so a landscape-shaped MediaBox
    # with no /Rotate flag can come out tilted on paper even though it looks
    # fine on screen. Pages are therefore always built as plain portrait A4
    # here, exactly like the default; rotation (if requested) is applied as a
    # final post-processing step, uniformly for any --per-page value.
    rotate_output = args.orientation == "landscape"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    register_fonts(pdf)

    page_width = pdf.w
    page_height = pdf.h
    region_width, region_height = page_width, page_height / args.per_page
    layout = scale_layout(LAYOUTS[args.per_page], region_width, region_height)

    cards = []
    for i in range(args.count):
        card_words = random.sample(words, CELLS_PER_CARD)
        random.shuffle(card_words)
        cards.append((card_words, PALETTE[i % len(PALETTE)]))

    for page_start in range(0, len(cards), args.per_page):
        pdf.add_page()
        page_cards = cards[page_start : page_start + args.per_page]
        for slot, (card_words, color) in enumerate(page_cards):
            draw_card(
                pdf,
                0,
                slot * region_height,
                region_width,
                region_height,
                args.title,
                args.subtitle,
                card_words,
                color,
                layout,
            )
        if args.per_page == 2 and len(page_cards) == 2:
            # Dashed cutting guide between the two cards
            pdf.set_draw_color(180, 180, 180)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=2, gap=1.5)
            pdf.line(8, region_height, page_width - 8, region_height)
            pdf.set_dash_pattern()

    if rotate_output:
        from io import BytesIO

        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(BytesIO(pdf.output()))
        writer = PdfWriter()
        for page in reader.pages:
            page.rotate(90)
            writer.add_page(page)
        with open(args.output, "wb") as f:
            writer.write(f)
    else:
        pdf.output(args.output)

    print(f"Wrote {args.count} card(s) to {args.output}")


if __name__ == "__main__":
    main()

"""Command-line interface."""
import argparse
import random
import sys

from .config import CELLS_PER_CARD, PALETTE
from .pdf_builder import build_pdf, write_pdf
from .words import load_words, pick_card_words


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate printable bingo cards from a word list.")
    parser.add_argument("--words", default="words_example.txt", help="Path to a text file with one word/phrase per line.")
    parser.add_argument("--title", default="PraDa Bingo", help="Title printed on each card.")
    parser.add_argument("--subtitle", default="", help="Optional subtitle printed under the title.")
    parser.add_argument("--count", type=int, default=1, help="Number of cards to generate.")
    parser.add_argument("--per-page", type=int, choices=[1, 2], default=1, help="How many cards to print on each page.")
    parser.add_argument("--orientation", choices=["portrait", "landscape"], default="portrait", help="Page orientation.")
    parser.add_argument("--output", default="bingo_cards.pdf", help="Output PDF file path.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible card layouts.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    words = load_words(args.words)
    if len(words) < CELLS_PER_CARD:
        sys.exit(f"Need at least {CELLS_PER_CARD} words/phrases, found {len(words)} in {args.words}.")

    cards = [(pick_card_words(words), PALETTE[i % len(PALETTE)]) for i in range(args.count)]
    pdf = build_pdf(cards, args.title, args.subtitle, args.per_page)
    write_pdf(pdf, args.output, landscape=args.orientation == "landscape")

    print(f"Wrote {args.count} card(s) to {args.output}")

#!/usr/bin/env python3
"""Generate printable 4x4 human bingo cards as a PDF.

Usage:
    python3 bingo_maker.py --words words_example.txt --count 10 --title "PraDa Bingo"
    python3 bingo_maker.py --words words_example.txt --count 20 --per-page 2
"""
from bingo.cli import main

if __name__ == "__main__":
    main()

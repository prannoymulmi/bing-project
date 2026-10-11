"""Word list loading and per-card word selection."""
import random

from .config import CELLS_PER_CARD


def load_words(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def pick_card_words(words: list[str]) -> list[str]:
    """Return CELLS_PER_CARD distinct words in random order."""
    card_words = random.sample(words, CELLS_PER_CARD)
    random.shuffle(card_words)
    return card_words

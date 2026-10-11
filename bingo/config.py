"""Constants shared across the bingo package."""

GRID_SIZE = 4
CELLS_PER_CARD = GRID_SIZE * GRID_SIZE
TEXT_ZONE_RATIO = 0.6  # top portion of each cell reserved for the prompt text

# Soft, wedding-friendly palette. One color is used per card, cycling.
PALETTE = [
    (184, 107, 119),   # dusty rose
    (110, 140, 160),   # dusty blue
    (124, 148, 115),   # sage green
    (200, 155, 60),    # muted gold
    (142, 124, 195),   # lavender
    (193, 112, 74),    # terracotta
]

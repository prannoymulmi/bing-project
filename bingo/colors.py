"""Color helpers."""

Color = tuple[int, int, int]


def tint(color: Color, amount: float) -> Color:
    """Lighten a color towards white. amount=0 -> original, amount=1 -> white."""
    r, g, b = color
    return (
        round(r + (255 - r) * amount),
        round(g + (255 - g) * amount),
        round(b + (255 - b) * amount),
    )

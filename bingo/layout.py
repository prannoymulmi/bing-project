"""Page layouts: how big a card is for a given number of cards per page."""

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

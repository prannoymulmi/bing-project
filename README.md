# PraDa Bingo

Generate printable 4x4 wedding icebreaker bingo cards as a PDF. Each box has a
prompt (e.g. "Has a pet") plus a blank line for writing a guest's name.
Cards use an elegant PT Serif typeface, a soft color frame, and a
zebra-tinted grid, cycling through a wedding-friendly color palette across
cards (`fonts/` holds the embedded PT Serif font files, licensed under the
SIL Open Font License — see `fonts/OFL.txt`; `bingo_maker.py` holds the
`PALETTE` of colors — edit either to restyle).

## Setup (one-time)

```bash
cd /Users/prannoy/Projects/bingo-project
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Generate cards

```bash
./venv/bin/python bingo_maker.py --words words_example.txt --count 20 --output bingo_cards.pdf
```

This creates `bingo_cards.pdf` with 20 pages, one card per page, each with a
different random arrangement of 16 prompts drawn from your 20-word list.

## Options

| Flag | Default | Description |
|---|---|---|
| `--words` | `words_example.txt` | Path to a text file with one prompt per line (needs 16+ lines). |
| `--title` | `PraDa Bingo` | Title printed at the top of each card. |
| `--subtitle` | *(none)* | Optional subtitle under the title. |
| `--count` | `1` | Number of cards to generate. |
| `--per-page` | `1` | `1` for one card per page, `2` to print two cards per A4 page (with a dashed cutting guide between them). |
| `--orientation` | `portrait` | `portrait` or `landscape`. Landscape takes the normal portrait page(s) (unchanged layout, cards and title included) and rotates them 90° via the PDF's standard `/Rotate` flag, so printers pick the correct paper feed instead of printing it tilted. Works the same way for `--per-page 1` or `2`. |
| `--output` | `bingo_cards.pdf` | Output PDF path. |
| `--seed` | *(none)* | Set an integer to make the shuffle reproducible. |

## Examples

Custom title and 30 cards:

```bash
./venv/bin/python bingo_maker.py --words words_example.txt --title "Sam & Alex's Bingo" --count 30 --output wedding_bingo.pdf
```

Use your own word list:

```bash
./venv/bin/python bingo_maker.py --words my_words.txt --count 50
```

Print two cards per sheet to save paper (cut along the dashed line):

```bash
./venv/bin/python bingo_maker.py --words words_example.txt --count 30 --per-page 2
```

Landscape, single card rotated 90° to fill the page:

```bash
./venv/bin/python bingo_maker.py --words words_example.txt --count 30 --orientation landscape
```

Then print `bingo_cards.pdf` as needed.

## Word list

`words_example.txt` is pre-filled with 20 wedding icebreaker prompts
(including a "Knows how the couple first met" prompt that appears twice, by
design). Edit this file directly, or point `--words` at your
own file, to change the prompts.

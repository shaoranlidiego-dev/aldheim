#!/usr/bin/env python3
"""Genera el retrato piloto del Guerrero (128x128, tres cuartos) en docs/art/wip/ (no se importa en el juego).

Salidas: warrior_portrait_pilot.png (128x128, PNG con transparencia), vista ampliada x6 y comparación con la referencia.
Uso: python3 tools/make_warrior_pilot.py   (requiere Pillow y numpy)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image  # noqa: E402

from warrior_art import pilot, preview  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "art" / "wip"
REF = Path(__file__).resolve().parent.parent / "docs" / "art" / "reference" / "warrior_reference_2.png"


def main() -> None:
	OUT.mkdir(parents=True, exist_ok=True)
	img = pilot.build("full")
	img.save(OUT / "warrior_portrait_pilot.png")
	preview.zoom(img, 6).save(OUT / "warrior_portrait_pilot_x6.png")
	ref = Image.open(REF).convert("RGB").crop((798, 56, 958, 208))   # retrato "Neutral" de la referencia
	ref = ref.resize((ref.width * 4, ref.height * 4), Image.NEAREST)
	mine = preview.zoom(img, 5).convert("RGB")
	board = Image.new("RGB", (ref.width + mine.width + 30, max(ref.height, mine.height) + 20), (18, 22, 34))
	board.paste(ref, (10, 10))
	board.paste(mine, (ref.width + 20, 10))
	board.save(OUT / "warrior_portrait_pilot_vs_reference.png")
	print("Escrito", OUT)


if __name__ == "__main__":
	main()

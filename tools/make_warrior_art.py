#!/usr/bin/env python3
"""Genera todo el arte del Guerrero (sprites jugables y retratos). Arte original, sin imágenes de terceros.

Salidas:
  assets/characters/warrior/sprites/warrior_sheet.png            hoja jugable (cuadros de 44x44)
  docs/art/archive/portraits_procedural_v1/warrior_<expr>.png    retratos procedurales ANTIGUOS (archivo)

Los retratos del juego ya NO salen de aquí: vienen de la referencia aprobada (tools/extract_warrior_portraits.py).
`all` solo regenera los sprites, para no pisar los retratos de assets/.

Uso: python3 tools/make_warrior_art.py [sprites|portraits]   (requiere Pillow y numpy)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from warrior_art import sheet  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent / "assets" / "characters" / "warrior"


def make_sprites() -> None:
	out = ROOT / "sprites" / "warrior_sheet.png"
	out.parent.mkdir(parents=True, exist_ok=True)
	img = sheet.build()
	img.save(out)
	print("Escrito", out, img.size)


def make_portraits() -> None:
	from warrior_art import portrait

	out_dir = ROOT.parent.parent.parent / "docs" / "art" / "archive" / "portraits_procedural_v1"
	out_dir.mkdir(parents=True, exist_ok=True)
	for name in portrait.EXPRESSIONS:
		img = portrait.render(name)
		img.save(out_dir / f"warrior_{name}.png")
		print("Escrito", out_dir / f"warrior_{name}.png", img.size)


if __name__ == "__main__":
	what = sys.argv[1] if len(sys.argv) > 1 else "all"
	if what in ("all", "sprites"):
		make_sprites()
	if what == "portraits":
		make_portraits()

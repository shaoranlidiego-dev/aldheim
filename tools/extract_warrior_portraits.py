#!/usr/bin/env python3
"""Extrae los 8 retratos del Guerrero desde la lámina de referencia (docs/art/reference/warrior_reference_2.png).

Procedimiento (aprobado con la prueba piloto neutral):
  1. Recorte cuadrado de 146x146 px dentro del marco dorado de cada recuadro (sin marco, sin sombra del marco, sin etiqueta).
  2. Reducción a 128x128 con Lanczos.
  3. Cuantización a 64 colores por retrato, sin tramado. El fondo azul se conserva opaco.

Salida de trabajo: docs/art/wip/portraits_ref/warrior_<expresión>.png (no toca assets/).
Con --install: archiva los retratos actuales de assets/ en docs/art/archive/portraits_procedural_v1/ (si no existe el
archivo) y copia los nuevos a assets/characters/warrior/portraits/.

Uso: python3 tools/extract_warrior_portraits.py [--install]   (requiere Pillow y numpy)
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "docs" / "art" / "reference" / "warrior_reference_2.png"
WORK = ROOT / "docs" / "art" / "wip" / "portraits_ref"
ASSETS = ROOT / "assets" / "characters" / "warrior" / "portraits"
ARCHIVE = ROOT / "docs" / "art" / "archive" / "portraits_procedural_v1"

SIDE = 146       # lado del recorte (px de la lámina)
SIZE = 128       # lado final
COLORS = 64

# Marcos dorados de la lámina: x de la línea izquierda y derecha de cada columna; y de la línea superior e inferior de cada fila.
COLUMNS = [(798, 956), (979, 1137), (1162, 1320), (1344, 1502)]
ROWS = [(56, 207), (241, 392)]
NAMES = [["neutral", "sonriente", "determinado", "enojado"], ["triste", "sorprendido", "herido", "agotado"]]
# El recorte se centra en el marco y termina 3 px antes de la línea inferior (las 2 filas previas a la línea son sombra del marco).
BOTTOM_MARGIN = 3


def tile_box(row: int, col: int):
	xl, xr = COLUMNS[col]
	_, yb = ROWS[row]
	x0 = (xl + xr) // 2 - SIDE // 2 + 1   # centrado en el marco (neutral: x 805..950, igual que la prueba aprobada)
	y1 = yb - BOTTOM_MARGIN          # última fila incluida
	return x0, y1 - SIDE + 1, SIDE


def crop_tile(ref: Image.Image, row: int, col: int) -> Image.Image:
	x, y, s = tile_box(row, col)
	return ref.crop((x, y, x + s, y + s))


def downscale(img: Image.Image) -> Image.Image:
	return img.resize((SIZE, SIZE), Image.LANCZOS)


def quantize(img: Image.Image) -> Image.Image:
	return img.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")


def check_crop(name: str, crop: Image.Image) -> list:
	"""Devuelve una lista de problemas (vacía = recorte limpio)."""
	a = np.asarray(crop).astype(int)
	problems = []
	gold = (a[:, :, 0] > 150) & (a[:, :, 1] > 90) & (a[:, :, 2] < 125) & (a[:, :, 0] - a[:, :, 2] > 70)
	# Un resto de marco sería una línea dorada continua a lo largo del borde; el dorado de la armadura es contenido real.
	for label, line in (("superior", gold[0]), ("superior+1", gold[1]), ("inferior", gold[-1]), ("inferior-1", gold[-2]),
	                    ("izquierdo", gold[:, 0]), ("izquierdo+1", gold[:, 1]), ("derecho", gold[:, -1]), ("derecho-1", gold[:, -2])):
		if line.mean() > 0.30:
			problems.append(f"línea dorada continua en el borde {label} ({line.mean() * 100:.0f}%)")
	lum = a.mean(axis=2)
	rows = lum.mean(axis=1)
	if rows[-1] < 0.6 * rows[-6:-1].mean():
		problems.append(f"última fila oscura (sombra del marco): {rows[-1]:.0f} vs {rows[-6:-1].mean():.0f}")
	cols = lum.mean(axis=0)
	for side, c, ref_c in (("izquierda", cols[0], cols[1:6].mean()), ("derecha", cols[-1], cols[-6:-1].mean())):
		if c < 0.6 * ref_c and ref_c > 50:
			problems.append(f"columna {side} oscura: {c:.0f} vs {ref_c:.0f}")
	return problems


def process(ref: Image.Image):
	results = {}
	for r in range(2):
		for c in range(4):
			name = NAMES[r][c]
			crop = crop_tile(ref, r, c)
			issues = check_crop(name, crop)
			small = downscale(crop)
			q = quantize(small)
			colors = len({tuple(p) for p in np.asarray(q).reshape(-1, 3)})
			results[name] = (crop, small, q, issues, colors)
	return results


def main() -> None:
	install = "--install" in sys.argv
	ref = Image.open(REF).convert("RGB")
	WORK.mkdir(parents=True, exist_ok=True)
	results = process(ref)
	bad = False
	for name, (crop, small, q, issues, colors) in results.items():
		q.save(WORK / f"warrior_{name}.png")
		x, y, s = tile_box(*next((r, c) for r in range(2) for c in range(4) if NAMES[r][c] == name))
		err = np.abs(np.asarray(small, dtype=np.float32) - np.asarray(q, dtype=np.float32))
		print(f"{name:12s} recorte ({x},{y}) {s}px -> {q.size}, colores {colors}, error medio {err.mean():.2f}/255"
		      + (f"  PROBLEMAS: {issues}" if issues else "  limpio"))
		bad |= bool(issues) or colors != COLORS
	if bad:
		print("Hay problemas de recorte o de paleta: no se instala nada.")
		sys.exit(1)
	if install:
		ARCHIVE.mkdir(parents=True, exist_ok=True)
		for name in results:
			src = ASSETS / f"warrior_{name}.png"
			dst = ARCHIVE / src.name
			if src.exists() and not dst.exists():
				shutil.copy2(src, dst)
			shutil.copy2(WORK / f"warrior_{name}.png", src)
		print("Instalados en", ASSETS, "(originales archivados en", ARCHIVE, ")")


if __name__ == "__main__":
	main()

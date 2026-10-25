#!/usr/bin/env python3
"""Extrae retratos del Guerrero desde la lámina de referencia (docs/art/reference/warrior_reference_2.png).

FASE 1A (piloto): solo el retrato "neutral". Salida en docs/art/wip/; no toca assets/ ni el juego.
Pasos: recorte cuadrado dentro del marco dorado (sin marco ni etiqueta) -> reducción a 128x128 por interpolación
Lanczos -> cuantización a una paleta limitada, sin tramado. El fondo azul se conserva opaco.

Uso: python3 tools/extract_warrior_portraits.py   (requiere Pillow y numpy)
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "docs" / "art" / "reference" / "warrior_reference_2.png"
OUT = ROOT / "docs" / "art" / "wip"

# Coordenadas dentro de la lámina (x, y, lado). Marco dorado del neutral: x 798-799 y 956, y 56-57 y 208.
# Se recortan 148x148 px bien dentro del marco (1-4 px de margen) para no arrastrar píxeles dorados.
TILES = {"neutral": (804, 59, 148)}
SIZE = 128
PALETTE_SIZES = (32, 48, 64)


def crop_tile(ref: Image.Image, name: str) -> Image.Image:
	x, y, side = TILES[name]
	return ref.crop((x, y, x + side, y + side))


def downscale(img: Image.Image, size: int = SIZE) -> Image.Image:
	return img.resize((size, size), Image.LANCZOS)


def quantize(img: Image.Image, colors: int) -> Image.Image:
	q = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
	return q.convert("RGB")


def psnr_mae(a: Image.Image, b: Image.Image):
	x, y = np.asarray(a, dtype=np.float32), np.asarray(b, dtype=np.float32)
	mse = float(((x - y) ** 2).mean())
	psnr = 99.0 if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)
	err = np.abs(x - y).max(axis=2)
	return psnr, float(np.abs(x - y).mean()), float((err > 24).mean() * 100), float(err.max())


def sharpness(img: Image.Image) -> float:
	g = np.asarray(img.convert("L"), dtype=np.float32)
	return float((np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean()) / 2)


def color_count(img: Image.Image) -> int:
	return len({tuple(p) for p in np.asarray(img.convert("RGB")).reshape(-1, 3)})


def main() -> None:
	OUT.mkdir(parents=True, exist_ok=True)
	ref = Image.open(REF).convert("RGB")
	tile = crop_tile(ref, "neutral")
	small = downscale(tile)
	variants = {n: quantize(small, n) for n in PALETTE_SIZES}
	chosen = variants[48]
	chosen.save(OUT / "warrior_portrait_neutral_ref_pilot_128.png")

	# Pérdida por reducción: volver a ampliar a 148 y comparar con el recorte original.
	back = small.resize(tile.size, Image.LANCZOS)
	r_psnr, r_mae, r_bad, _ = psnr_mae(tile, back)
	print(f"Recorte original {tile.size}: {color_count(tile)} colores, nitidez {sharpness(tile):.2f}")
	print(f"Reducido a {small.size}: {color_count(small)} colores, nitidez {sharpness(small):.2f}")
	print(f"  pérdida por reducción (148->128->148): PSNR {r_psnr:.1f} dB, error medio {r_mae:.2f}/255, píxeles con error>24: {r_bad:.1f}%")
	for n, q in variants.items():
		p, m, bad, mx = psnr_mae(small, q)
		print(f"  cuantizado a {n} colores (reales: {color_count(q)}): PSNR {p:.1f} dB, error medio {m:.2f}/255, "
		      f"píxeles con error>24: {bad:.1f}%, error máx {mx:.0f}, nitidez {sharpness(q):.2f}")

	# Tablero comparativo: original / reducido a color / 48 colores / mapa de error de la cuantización.
	z = 4
	diff = np.abs(np.asarray(small, dtype=np.float32) - np.asarray(chosen, dtype=np.float32)).max(axis=2)
	heat = Image.fromarray(np.clip(diff * 6, 0, 255).astype(np.uint8)).convert("RGB")
	tiles = [tile.resize((tile.width * z, tile.height * z), Image.NEAREST),
	         small.resize((SIZE * z, SIZE * z), Image.NEAREST),
	         chosen.resize((SIZE * z, SIZE * z), Image.NEAREST),
	         heat.resize((SIZE * z, SIZE * z), Image.NEAREST)]
	w = sum(t.width for t in tiles) + 10 * (len(tiles) + 1)
	board = Image.new("RGB", (w, max(t.height for t in tiles) + 20), (14, 18, 28))
	x = 10
	for t in tiles:
		board.paste(t, (x, 10))
		x += t.width + 10
	board.save(OUT / "warrior_portrait_neutral_ref_pilot_compare.png")

	# Variantes de paleta lado a lado (x5).
	row = [variants[n].resize((SIZE * 5, SIZE * 5), Image.NEAREST) for n in PALETTE_SIZES]
	pal = Image.new("RGB", (sum(t.width for t in row) + 40, row[0].height + 20), (14, 18, 28))
	x = 10
	for t in row:
		pal.paste(t, (x, 10))
		x += t.width + 10
	pal.save(OUT / "warrior_portrait_neutral_ref_pilot_palettes.png")


if __name__ == "__main__":
	main()

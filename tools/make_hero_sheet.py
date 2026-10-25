#!/usr/bin/env python3
"""Genera la hoja de sprites PROVISIONAL del héroe (arte original, pixel a pixel).

Salida: assets/characters/hero_sheet.png  (48x64 px, cuadros de 16x16)
  Columnas: 0 = paso A, 1 = quieto, 2 = paso B
  Filas:    0 = abajo, 1 = izquierda, 2 = derecha, 3 = arriba   (orden de RPG Maker)

Uso: python3 tools/make_hero_sheet.py   (requiere Pillow)
Este dibujo es solo un reemplazo temporal: ver README para cambiarlo por arte definitivo.
"""
from pathlib import Path
from PIL import Image

FRAME = 16
PALETTE = {
	".": None,
	"o": (0x2A, 0x1F, 0x2D),  # contorno
	"h": (0x6B, 0x3F, 0x2A),  # pelo
	"H": (0x8F, 0x5A, 0x3A),  # brillo del pelo
	"s": (0xF2, 0xC3, 0x94),  # piel
	"S": (0xD3, 0x9A, 0x6E),  # sombra de piel
	"e": (0x2A, 0x1F, 0x2D),  # ojo
	"t": (0x3B, 0x6F, 0xB6),  # túnica
	"T": (0x27, 0x4B, 0x82),  # túnica oscura / pantalón
	"r": (0xC0, 0x39, 0x2B),  # bufanda / capa
	"R": (0x8E, 0x2A, 0x20),  # bufanda oscura
	"g": (0xE0, 0xB3, 0x41),  # cinturón dorado
	"b": (0x4A, 0x30, 0x20),  # botas
}

# Filas 1..12 (cabeza y torso). Cada cadena se centra automáticamente en 16 columnas.
UPPER = {
	"down": ["oooooo", "ohhhhhho", "ohhHHHHhho", "ohhhhhhhho", "ohssssssho", "osesssseso",
	         "osssssssso", "oSssssSo", "orrrrrrrro", "o" + "t" * 10 + "o", "os" + "t" * 8 + "so",
	         "o" + "g" * 10 + "o"],
	"up": ["oooooo", "ohhhhhho", "ohhHHHHhho", "ohhhhhhhho", "ohhhhhhhho", "ohhhhhhhho",
	       "ohhhhhhhho", "ohhhhhho", "oRRRRRRRRo", "o" + "r" * 10 + "o", "o" + "r" * 10 + "o",
	       "o" + "r" * 10 + "o"],
	"left": ["oooooo", "ohhhhhho", "ohhHHHhhho", "ohhhhhhhho", "ossshhhhho", "ossehhhhho",
	         "osssshhhho", "oSsssho", "orrrrrro", "ottttttTTo", "osttttTTo", "oggggggggo"],
}


def centered(row: str) -> str:
	return row.center(FRAME, ".")


def draw_frame(direction: str, step: int) -> Image.Image:
	"""step: 0 = paso A, 1 = quieto, 2 = paso B."""
	img = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
	source = "left" if direction == "right" else direction
	rows = [centered("")] + [centered(r) for r in UPPER[source]]
	for y, row in enumerate(rows):
		assert len(row) == FRAME, (direction, y, row)
		for x, ch in enumerate(row):
			if PALETTE[ch]:
				img.putpixel((x, y), PALETTE[ch] + (255,))

	def leg(x: int, bottom: int) -> None:
		"""Pierna de 2 px de ancho desde la fila 13 hasta `bottom` (bota en la última)."""
		for y in range(13, bottom + 1):
			for dx in range(2):
				img.putpixel((x + dx, y), PALETTE["b" if y == bottom else "T"] + (255,))
		for dx in range(2):
			img.putpixel((x + dx, bottom + 1), PALETTE["o"] + (255,))

	if direction in ("down", "up"):
		left_end, right_end = {0: (13, 14), 1: (14, 14), 2: (14, 13)}[step]
		leg(5, left_end)
		leg(9, right_end)
	else:
		if step == 1:
			leg(7, 14)
		else:
			leg(5 if step == 0 else 9, 14)
			leg(9 if step == 0 else 5, 13)
	if direction == "right":
		img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
	return img


def main() -> None:
	order = ["down", "left", "right", "up"]
	sheet = Image.new("RGBA", (FRAME * 3, FRAME * len(order)), (0, 0, 0, 0))
	for row, direction in enumerate(order):
		for col in range(3):
			sheet.paste(draw_frame(direction, col), (col * FRAME, row * FRAME))
	out = Path(__file__).resolve().parent.parent / "assets" / "characters" / "hero_sheet.png"
	out.parent.mkdir(parents=True, exist_ok=True)
	sheet.save(out)
	print("Escrito", out, sheet.size)


if __name__ == "__main__":
	main()

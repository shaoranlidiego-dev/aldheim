#!/usr/bin/env python3
"""Genera la hoja de sprites del Guerrero de Aldheim (arte original, píxel a píxel).

Referencia artística aprobada: docs/art/reference/warrior_reference.png (solo como guía visual;
ningún píxel de la referencia se copia a los sprites).

Salida: assets/characters/warrior/sprites/warrior_sheet.png  (128x128, cuadros de 32x32)
  Columnas: 0 = quieto A, 1 = quieto B (respiración), 2 = paso A, 3 = paso B
  Filas:    0 = abajo, 1 = izquierda, 2 = derecha, 3 = arriba   (orden de RPG Maker)

Para ampliar (ataque, defensa, daño...) se agregan filas/hojas nuevas y se declaran en
tools/build_warrior_frames.gd; ver docs/art/warrior.md.

Uso: python3 tools/make_warrior_sheet.py   (requiere Pillow)
"""
from pathlib import Path
from PIL import Image

W = 32
C = {
	"line": (0x14, 0x16, 0x1F),
	"skin": (0xFD, 0xC9, 0xA1), "skin_d": (0xEF, 0xAC, 0x7F), "skin_dd": (0xD6, 0x84, 0x5E),
	"eye": (0x29, 0x29, 0x34), "iris": (0x5A, 0x34, 0x20),
	"hair": (0x6A, 0x3F, 0x26), "hair_d": (0x45, 0x27, 0x16), "hair_l": (0x92, 0x5E, 0x3A),
	"blue": (0x4B, 0x86, 0xCB), "blue_d": (0x2F, 0x5C, 0xA0), "blue_dd": (0x1F, 0x3E, 0x75),
	"steel": (0x4D, 0x56, 0x67), "steel_l": (0x8A, 0x96, 0xAB), "steel_h": (0xCF, 0xD6, 0xE2),
	"steel_d": (0x32, 0x37, 0x48),
	"slate": (0x49, 0x47, 0x64), "slate_d": (0x2E, 0x2D, 0x42),
	"gold": (0xE3, 0xAD, 0x5E), "gold_d": (0xA8, 0x74, 0x3A),
	"red": (0xAE, 0x25, 0x2A),
	"boot": (0x5A, 0x3A, 0x26), "boot_l": (0x8A, 0x5A, 0x38),
	"belt": (0x4A, 0x30, 0x20),
}


class Draw:
	def __init__(self, img):
		self.px = img.load()

	def p(self, x, y, col):
		if 0 <= x < W and 0 <= y < W:
			self.px[x, y] = C[col] + (255,)

	def rect(self, x0, y0, x1, y1, col):
		for y in range(y0, y1 + 1):
			for x in range(x0, x1 + 1):
				self.p(x, y, col)

	def sym(self, x, y, col):
		self.p(x, y, col)
		self.p(W - 1 - x, y, col)

	def srow(self, y, x0, x1, col):
		for x in range(x0, x1 + 1):
			self.sym(x, y, col)


# ---------------------------------------------------------------- vistas frontal y trasera
def legs_front(d, phase, back=False):
	"""phase: 0 quieto, 1 pierna izq. levantada, 2 pierna der. levantada (izq./der. de pantalla)."""
	for side in (0, 1):
		lift = (phase == 1 and side == 0) or (phase == 2 and side == 1)
		x0 = 11 if side == 0 else 17
		bottom = 29 if lift else 30
		d.rect(x0, 25, x0 + 3, bottom - 3, "slate")
		d.rect(x0, 25, x0, bottom - 3, "slate_d") if side == 0 else d.rect(x0 + 3, 25, x0 + 3, bottom - 3, "slate_d")
		d.rect(x0 - 1, bottom - 2, x0 + 4, bottom, "boot")
		d.rect(x0 - 1, bottom - 2, x0 + 4, bottom - 2, "boot_l")
		d.rect(x0, bottom - 3, x0 + 3, bottom - 3, "steel")


def hair_front(d, o):
	rows = {2: 13, 3: 11, 4: 9, 5: 8, 6: 8, 7: 7, 8: 7, 9: 7, 10: 7, 11: 7, 12: 7, 13: 8}
	for y, x0 in rows.items():
		d.srow(y + o, x0, 15, "hair")
	for x, y in ((12, 3), (10, 5), (11, 5), (9, 7), (13, 4), (14, 3)):
		d.sym(x, y + o, "hair_l")
	for x, y in ((8, 8), (9, 10), (7, 11), (8, 12), (13, 9)):
		d.sym(x, y + o, "hair_d")
	# flequillo irregular sobre la frente
	for x in (9, 10, 13, 14):
		d.sym(x, 10 + o, "hair")
	d.sym(12, 9 + o, "skin_d")


def face_front(d, o):
	d.srow(10 + o, 11, 12, "skin")
	d.srow(10 + o, 15, 15, "skin")
	for y in (11, 12):
		d.srow(y + o, 9, 15, "skin")
	d.srow(13 + o, 10, 15, "skin")
	d.srow(14 + o, 12, 15, "skin_d")
	d.sym(9, 11 + o, "skin_d")
	d.sym(9, 12 + o, "skin_d")
	for x in (11, 12):
		d.sym(x, 11 + o, "eye")
		d.sym(x, 12 + o, "iris")
	d.sym(11, 11 + o, "eye")
	d.sym(15, 14 + o, "skin_dd")


def draw_front(d, dy, swing, phase):
	o = dy
	legs_front(d, phase)
	# capa asomando por los costados
	d.srow(20 + o, 8, 9, "blue_d")
	d.srow(21 + o, 8, 9, "blue_dd")
	# brazos
	for side, s in ((0, swing), (1, -swing)):
		x0 = 4 if side == 0 else 24
		d.rect(x0, 20 + o + s, x0 + 3, 24 + o + s, "steel")
		d.rect(x0, 23 + o + s, x0 + 3, 23 + o + s, "gold")
		d.rect(x0, 24 + o + s, x0 + 3, 24 + o + s, "steel_d")
		d.rect(x0 + 1, 25 + o + s, x0 + 2, 26 + o + s, "skin")
	# torso
	for y in range(17, 24):
		d.srow(y + o, 10, 15, "steel")
	d.srow(18 + o, 11, 15, "steel_l")
	d.srow(19 + o, 11, 14, "steel_l")
	d.srow(20 + o, 12, 14, "steel_h") if False else None
	for x, y in ((11, 18), (12, 18)):
		d.sym(x, y + o, "steel_h")
	d.srow(21 + o, 10, 15, "steel")
	d.srow(23 + o, 10, 15, "belt")
	d.rect(14, 22 + o, 17, 23 + o, "gold")
	d.rect(15, 22 + o, 16, 22 + o, "gold_d")
	d.rect(15, 19 + o, 16, 19 + o, "gold")
	d.rect(15, 20 + o, 16, 20 + o, "red")
	# faldón corto
	d.srow(24 + o, 10, 15, "slate")
	d.srow(25 + o, 11, 15, "slate_d")
	# hombreras
	for side in (0, 1):
		x0 = 5 if side == 0 else 21
		d.rect(x0 + 1, 16 + o, x0 + 3, 16 + o, "steel_h")
		d.rect(x0, 17 + o, x0 + 4, 18 + o, "steel_l")
		d.rect(x0 + (1 if side == 0 else 0), 17 + o, x0 + (2 if side == 0 else 3), 17 + o, "steel_h")
		d.rect(x0, 19 + o, x0 + 4, 19 + o, "gold")
		d.rect(x0 + 1, 20 + o, x0 + 3, 20 + o, "steel_d")
	# bufanda
	d.srow(15 + o, 9, 15, "blue")
	d.srow(16 + o, 8, 15, "blue_d")
	d.srow(17 + o, 9, 14, "blue_dd")
	d.rect(19, 17 + o, 23, 20 + o, "blue_d")
	d.rect(20, 21 + o, 22, 22 + o, "blue_dd")
	d.rect(19, 17 + o, 19, 20 + o, "blue")
	hair_front(d, o)
	face_front(d, o)


def draw_back(d, dy, swing, phase):
	o = dy
	legs_front(d, phase, back=True)
	for side, s in ((0, swing), (1, -swing)):
		x0 = 4 if side == 0 else 24
		d.rect(x0, 20 + o + s, x0 + 3, 24 + o + s, "steel")
		d.rect(x0, 23 + o + s, x0 + 3, 23 + o + s, "gold")
		d.rect(x0 + 1, 25 + o + s, x0 + 2, 26 + o + s, "skin_d")
	# capa
	for y in range(16, 28):
		d.srow(y + o, 9, 15, "blue")
	for y in range(16, 28):
		d.sym(9, y + o, "blue_dd")
		d.sym(10, y + o, "blue_d")
		d.sym(12, y + o, "blue_d") if y % 3 else None
	d.srow(28 + o, 9, 15, "gold")
	d.srow(27 + o, 9, 9, "gold_d")
	for y in range(18, 28, 2):
		d.sym(9, y + o, "gold")
	# emblema (flor de lis simplificada)
	for x, y in ((15, 19), (16, 19), (14, 20), (15, 20), (16, 20), (17, 20), (15, 21), (16, 21),
	             (14, 22), (15, 22), (16, 22), (17, 22), (15, 23), (16, 23), (15, 24), (16, 24)):
		d.p(x, y + o, "gold")
	# hombreras
	for side in (0, 1):
		x0 = 5 if side == 0 else 21
		d.rect(x0 + 1, 16 + o, x0 + 3, 16 + o, "steel_h")
		d.rect(x0, 17 + o, x0 + 4, 18 + o, "steel_l")
		d.rect(x0, 19 + o, x0 + 4, 19 + o, "gold")
		d.rect(x0 + 1, 20 + o, x0 + 3, 20 + o, "steel_d")
	d.srow(15 + o, 10, 15, "blue_d")
	# pelo
	rows = {2: 13, 3: 11, 4: 9, 5: 8, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7, 11: 7, 12: 7, 13: 8, 14: 10}
	for y, x0 in rows.items():
		d.srow(y + o, x0, 15, "hair")
	for x, y in ((11, 4), (12, 4), (10, 6), (9, 8), (13, 3)):
		d.sym(x, y + o, "hair_l")
	for x, y in ((10, 7), (13, 8), (9, 10), (12, 11), (15, 10), (8, 12), (14, 13), (11, 13)):
		d.sym(x, y + o, "hair_d")
	d.srow(15 + o, 14, 15, "skin_d")


# ---------------------------------------------------------------- vista lateral (mira a la izquierda)
def draw_side(d, dy, swing, phase):
	o = dy
	# piernas: lejana (oscura) y cercana
	def leg(xc, lift, far):
		bottom = 29 if lift else 30
		cp, cb = ("slate_d", "belt") if far else ("slate", "boot")
		d.rect(xc, 25, xc + 3, bottom - 3, cp)
		d.rect(xc - 1, bottom - 2, xc + 4, bottom, cb)
		d.rect(xc - 2, bottom - 1, xc - 1, bottom, cb)
		if not far:
			d.rect(xc - 1, bottom - 2, xc + 4, bottom - 2, "boot_l")
			d.rect(xc, bottom - 3, xc + 3, bottom - 3, "steel")
	if phase == 0:
		leg(15, False, True)
		leg(12, False, False)
	elif phase == 1:
		leg(18, True, True)
		leg(9, False, False)
	else:
		leg(9, False, True)
		leg(17, True, False)
	# capa detrás: se ensancha hacia abajo y hacia atrás
	for y in range(17, 28):
		x1 = 20 + (y - 17) // 3
		d.rect(17, y + o, x1, y + o, "blue_d")
		d.p(17, y + o, "blue")
		d.p(x1, y + o, "blue_dd")
		d.p(x1 - 1, y + o, "blue_dd") if y > 20 else None
	d.rect(18, 28 + o, 23, 28 + o, "gold")
	# torso
	d.rect(11, 17 + o, 19, 23 + o, "steel")
	d.rect(12, 18 + o, 15, 21 + o, "steel_l")
	d.rect(12, 18 + o, 13, 18 + o, "steel_h")
	d.rect(11, 23 + o, 19, 23 + o, "belt")
	d.rect(11, 22 + o, 12, 23 + o, "gold")
	d.rect(11, 24 + o, 19, 25 + o, "slate")
	# brazo cercano
	ax = 11 + swing * 2
	d.rect(ax, 20 + o, ax + 3, 24 + o, "steel_l")
	d.rect(ax, 23 + o, ax + 3, 23 + o, "gold")
	d.rect(ax, 24 + o, ax + 3, 24 + o, "steel_d")
	d.rect(ax, 25 + o, ax + 2, 26 + o, "skin")
	# hombrera
	d.rect(11, 16 + o, 16, 16 + o, "steel_h")
	d.rect(10, 17 + o, 17, 18 + o, "steel_l")
	d.rect(10, 19 + o, 17, 19 + o, "gold")
	d.rect(11, 20 + o, 16, 20 + o, "steel_d")
	# bufanda
	d.rect(10, 15 + o, 19, 16 + o, "blue_d")
	d.rect(12, 17 + o, 18, 17 + o, "blue_dd")
	d.rect(10, 15 + o, 14, 15 + o, "blue")
	d.rect(19, 16 + o, 25, 17 + o, "blue_d")
	d.rect(21, 18 + o, 26, 19 + o, "blue_dd")
	# cabeza: pelo atrás y arriba
	hair_rows = {2: (12, 17), 3: (10, 19), 4: (9, 20), 5: (8, 21), 6: (8, 22), 7: (8, 22), 8: (8, 22),
	             9: (8, 22), 10: (14, 22), 11: (14, 22), 12: (14, 21), 13: (16, 21), 14: (17, 21)}
	for y, (x0, x1) in hair_rows.items():
		d.rect(x0, y + o, x1, y + o, "hair")
	for x, y in ((12, 3), (13, 3), (11, 5), (10, 6), (15, 4)):
		d.p(x, y + o, "hair_l")
	for x, y in ((17, 7), (19, 9), (16, 11), (20, 12), (18, 13), (21, 6)):
		d.p(x, y + o, "hair_d")
	# cara en perfil
	d.rect(9, 10 + o, 13, 12 + o, "skin")
	d.rect(10, 13 + o, 14, 13 + o, "skin")
	d.rect(11, 14 + o, 14, 14 + o, "skin_d")
	d.p(8, 12 + o, "skin")
	d.p(9, 13 + o, "skin_d")
	d.rect(14, 10 + o, 14, 12 + o, "skin_d")
	d.p(10, 11 + o, "eye")
	d.p(10, 12 + o, "iris")
	d.p(11, 11 + o, "eye")
	d.p(11, 12 + o, "iris")
	d.p(10, 14 + o, "skin_dd")
	# flequillo
	d.rect(8, 9 + o, 13, 9 + o, "hair")
	d.rect(9, 10 + o, 10, 10 + o, "hair")
	d.p(13, 10 + o, "hair")
	d.p(8, 10 + o, "hair_d")


def outline(img):
	src = img.copy().load()
	dst = img.load()
	for y in range(W):
		for x in range(W):
			if src[x, y][3] == 0:
				for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
					nx, ny = x + dx, y + dy
					if 0 <= nx < W and 0 <= ny < W and src[nx, ny][3] > 0:
						dst[x, y] = C["line"] + (255,)
						break


def frame(direction: str, column: int) -> Image.Image:
	"""column: 0 quieto A, 1 quieto B, 2 paso A, 3 paso B."""
	img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
	d = Draw(img)
	dy = {0: 0, 1: 1, 2: 1, 3: 1}[column]
	swing = {0: 0, 1: 0, 2: 1, 3: -1}[column]
	phase = {0: 0, 1: 0, 2: 1, 3: 2}[column]
	if direction == "down":
		draw_front(d, dy, swing, phase)
	elif direction == "up":
		draw_back(d, dy, swing, phase)
	else:
		draw_side(d, dy, swing, phase)
	outline(img)
	if direction == "right":
		img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
	return img


def main() -> None:
	order = ["down", "left", "right", "up"]
	sheet = Image.new("RGBA", (W * 4, W * len(order)), (0, 0, 0, 0))
	for row, direction in enumerate(order):
		for col in range(4):
			sheet.paste(frame(direction, col), (col * W, row * W))
	out = Path(__file__).resolve().parent.parent / "assets/characters/warrior/sprites/warrior_sheet.png"
	out.parent.mkdir(parents=True, exist_ok=True)
	sheet.save(out)
	print("Escrito", out, sheet.size)


if __name__ == "__main__":
	main()

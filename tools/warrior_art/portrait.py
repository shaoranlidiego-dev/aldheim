"""Retratos de diálogo del Guerrero (128x128, uno por expresión, fondo transparente)."""
import math
from dataclasses import dataclass, field

from PIL import Image, ImageChops

from .raster import Canvas, add_outline

SIZE = 128
CX = 64.0


@dataclass
class Expr:
	brow_out: float = -1.0   # altura del extremo exterior de la ceja (negativo = más alta)
	brow_in: float = 0.0     # altura del extremo interior
	brow_in_r: float | None = None  # ceja derecha distinta (herido); None = igual a la izquierda
	eye_open: float = 1.0    # apertura del ojo (0.4 cansado .. 1.25 asombrado)
	eye_shape: str = "open"  # "open" | "happy"
	look: tuple = (0.0, 0.0)
	mouth: str = "line"
	blush: float = 0.0
	extras: tuple = field(default_factory=tuple)  # "blood", "sweat", "tear", "bags", "scratch", "wrinkle"
	tilt: float = 0.0        # inclinación de la cabeza (px de desplazamiento lateral del mentón)


EXPRESSIONS = {
	"neutral": Expr(brow_out=-1, brow_in=1.0, eye_open=1.0, mouth="line"),
	"sonriente": Expr(brow_out=-3, brow_in=-2, eye_shape="happy", mouth="smile", blush=1.0),
	"determinado": Expr(brow_out=-1, brow_in=4.0, eye_open=0.85, mouth="firm", extras=("wrinkle",)),
	"enojado": Expr(brow_out=-4, brow_in=5.5, eye_open=0.8, mouth="snarl", extras=("wrinkle",)),
	"triste": Expr(brow_out=3, brow_in=-3.5, eye_open=0.85, look=(0.0, 1.4), mouth="frown", extras=("tear",)),
	"sorprendido": Expr(brow_out=-7, brow_in=-7, eye_open=1.3, mouth="o"),
	"herido": Expr(brow_out=-3, brow_in=4.0, brow_in_r=1.0, eye_open=0.6, mouth="grimace", extras=("blood", "scratch")),
	"agotado": Expr(brow_out=2.5, brow_in=0.5, eye_open=0.42, look=(0.0, 1.0), mouth="tired", extras=("sweat", "bags"), tilt=2.0),
}


def _spike(cx, cy, rx, ry, ang, length, half):
	a0, a1, am = math.radians(ang - half), math.radians(ang + half), math.radians(ang)
	b0 = (cx + rx * math.cos(a0), cy + ry * math.sin(a0))
	b1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
	tip = (cx + (rx + length) * math.cos(am), cy + (ry + length) * math.sin(am))
	return [b0, tip, b1]


def _strokes(c, mask, strokes, color, width):
	m = c.blank()
	for pts in strokes:
		c.limb(tuple(pts), width, m)
	c.clip(mask, m, color)


def _hair(c, mask, dark, light, high):
	c.shape(mask, "hair", "hair_l", "hair_d", depth=1.6)
	_strokes(c, mask, dark, "hair_d", 1.3)
	_strokes(c, mask, light, "hair_l", 1.5)
	_strokes(c, mask, high, "hair_h", 1.0)


def _body(c: Canvas) -> None:
	# capa azul detrás de los hombros
	for sd in (-1, 1):
		c.shape(c.poly([(CX + sd * 30, 96), (CX + sd * 62, 100), (CX + sd * 64, 128), (CX + sd * 30, 128)]), "blue_d", "blue", "blue_dd", depth=1.4)
	c.fill(c.minus(c.blank(), c.blank()), "blue")
	# cuello
	c.shape(c.poly([(54, 80), (74, 80), (76, 104), (52, 104)]), "skin_d", None, "skin_dd", depth=1.2)
	# peto y correa de cuero con medallón
	chest = c.poly([(34, 108), (94, 108), (100, 128), (28, 128)])
	c.shape(chest, "steel", "steel_l", "steel_d", depth=1.6)
	c.clip(chest, c.poly([(64, 100), (110, 100), (110, 128), (64, 128)]), "steel_d")
	strap = c.limb([(30, 104), (96, 128)], 8)
	c.shape(c.inter(strap, c.poly([(0, 100), (128, 100), (128, 128), (0, 128)])), "leather", "leather_l", "leather_d", depth=1.2)
	c.shape(c.ellipse(60, 118, 6.5, 6.5), "gold", "gold_l", "gold_d", depth=1.2)
	c.fill(c.ellipse(60, 118, 3.0, 3.0), "red_l")
	# hombreras de acero con borde cobrizo y un remache dorado
	for sd in (-1, 1):
		px = CX + sd * 43
		dome = c.ellipse(px, 116, 21, 17)
		c.shape(dome, "steel", "steel_h", "steel_d", depth=2.0)
		c.clip(dome, c.poly([(px - sd * 4, 100), (px + sd * 30, 100), (px + sd * 30, 134), (px + sd * 8, 134)]), "steel_d")
		c.clip(dome, c.ellipse(px - sd * 7, 110, 10, 5), "steel_l")
		rim = c.minus(dome, ImageChops.offset(dome, 0, 9))
		c.fill(rim, "copper")
		c.fill(c.inter(rim, c.ellipse(px - sd * 8, 99, 11, 5)), "copper_l")
		c.fill(c.minus(c.limb([(px - sd * 17, 119), (px, 124), (px + sd * 17, 119)], 3.0), c.blank()), "copper_d")
		c.fill(c.ellipse(px - sd * 4, 111, 1.6, 1.6), "gold_l")
	# bufanda gruesa con pliegues
	wrap = c.union(c.ellipse(CX, 101, 34, 11), c.ellipse(CX - 16, 106, 15, 9), c.ellipse(CX + 16, 107, 16, 9))
	c.shape(wrap, "blue", "blue_l", "blue_d", depth=1.8)
	c.clip(wrap, c.poly([(0, 104), (128, 104), (128, 128), (0, 128)]), "blue_d")
	for pts in (((38, 98), (50, 110)), ((54, 96), (62, 108)), ((74, 98), (68, 109)), ((88, 98), (78, 110))):
		c.clip(wrap, c.limb(pts, 2.2), "blue_dd")
	for pts in (((44, 96), (56, 100)), ((70, 95), (88, 98))):
		c.clip(wrap, c.limb(pts, 1.8), "blue_l")
	tail = c.poly([(CX + 12, 104), (CX + 34, 108), (CX + 38, 128), (CX + 18, 128), (CX + 16, 116)])
	c.shape(tail, "blue", "blue_l", "blue_dd", depth=1.5)
	c.clip(tail, c.limb([(CX + 24, 108), (CX + 28, 128)], 2.0), "blue_d")


def _face(c: Canvas, e: Expr) -> None:
	t = e.tilt
	face = c.union(
		c.ellipse(CX, 55, 27, 29),
		c.poly([(37, 62), (91, 62), (82 + t, 80), (CX + t, 90), (46 + t, 80)]),
	)
	for sd in (-1, 1):
		ear = c.ellipse(CX + sd * 27.5, 60, 4.5, 7)
		c.shape(ear, "skin_d", "skin", "skin_dd", depth=1.0)
	c.shape(face, "skin", "skin_l", "skin_d", depth=1.6)
	c.clip(face, c.poly([(84, 20), (100, 20), (100, 96), (78, 96)]), "skin_d")
	c.clip(face, c.ellipse(CX + 4, 92, 30, 10), "skin_dd")
	c.clip(face, c.limb([(42, 70), (50, 84)], 2.4), "skin_d")
	for sd in (-1, 1):
		if e.blush:
			c.fill(c.inter(face, c.ellipse(CX + sd * 17, 70, 7.5, 4.0)), "blush")
		elif True:
			c.fill(c.inter(face, c.ellipse(CX + sd * 18, 70, 6, 3.0)), "skin_d")


def _eye(c: Canvas, e: Expr, sd: int, face_mask) -> None:
	ex, ey = CX + sd * 13.5, 59
	if e.eye_shape == "happy":
		pts = [(ex - 7.0, ey + 1.5), (ex - 3.5, ey - 3.0), (ex, ey - 4.2), (ex + 3.5, ey - 3.0), (ex + 7.0, ey + 1.5)]
		c.fill(c.limb(pts, 2.6), "eye")
		c.fill(c.inter(face_mask, c.ellipse(ex, ey + 4.0, 8.0, 3.4)), "skin_l")
		return
	o = e.eye_open
	ry = 5.2 * o
	white = c.ellipse(ex, ey, 7.6, ry)
	c.fill(white, "white")
	c.fill(c.inter(white, c.ellipse(ex + sd * 0.5, ey - ry + 2.6, 8.4, 3.2)), "skin_l") if False else None
	iris = c.ellipse(ex + e.look[0], ey + e.look[1], 4.6, min(4.8, ry + 0.6))
	c.fill(c.inter(white, iris), "iris")
	c.fill(c.inter(white, c.ellipse(ex + e.look[0], ey + e.look[1] + 1.8, 3.6, 2.2)), "iris_l")
	c.fill(c.inter(white, c.ellipse(ex + e.look[0], ey + e.look[1], 2.3, 2.5)), "eye")
	c.fill(c.ellipse(ex - 1.6 + e.look[0], ey - 1.8 + e.look[1] * 0.4, 1.1, 1.1), "white")
	c.fill(c.ellipse(ex + 1.9 + e.look[0], ey + 1.6 + e.look[1], 0.6, 0.6), "white")
	# párpado superior grueso y pestañas
	top = [(ex - 8.2, ey - 0.4), (ex - 5.0, ey - ry - 0.6), (ex, ey - ry - 1.4), (ex + 5.0, ey - ry - 0.6), (ex + 8.2, ey - 0.2)]
	c.fill(c.limb(top, 2.4), "eye")
	c.fill(c.limb([(ex - 6.4, ey + ry + 0.5), (ex, ey + ry + 1.3), (ex + 6.4, ey + ry + 0.5)], 0.9), "skin_dd")
	if e.eye_open < 0.7:
		c.fill(c.inter(face_mask, c.ellipse(ex, ey - ry - 2.5, 9.0, 2.6)), "skin_d")


def _brows(c: Canvas, e: Expr) -> None:
	for sd in (-1, 1):
		ex = CX + sd * 13.5
		bi = e.brow_in if (sd == -1 or e.brow_in_r is None) else e.brow_in_r
		out_pt = (ex + sd * 9.5, 47 + e.brow_out)
		in_pt = (ex - sd * 8.0, 47 + bi)
		mid = ((out_pt[0] + in_pt[0]) / 2, min(out_pt[1], in_pt[1]) - 1.0)
		m = c.limb([out_pt, mid, in_pt], 3.4)
		c.shape(m, "hair_d", "hair", None, depth=0.8)


def _mouth(c: Canvas, e: Expr) -> None:
	m = e.mouth
	cx = CX + e.tilt * 0.5
	if m == "line":
		c.fill(c.limb([(cx - 8, 78), (cx, 79.4), (cx + 8, 78)], 1.8), "skin_dd")
		c.fill(c.limb([(cx - 4, 81.6), (cx + 4, 81.6)], 1.0), "skin_d")
	elif m == "firm":
		c.fill(c.limb([(cx - 9, 80), (cx - 4, 78), (cx + 4, 78), (cx + 9, 80)], 2.0), "skin_dd")
		c.fill(c.limb([(cx - 4, 83), (cx + 4, 83)], 1.0), "skin_d")
	elif m == "smile":
		mouth = c.poly([(cx - 11, 73), (cx + 11, 73), (cx + 8, 82), (cx, 85.5), (cx - 8, 82)])
		c.fill(mouth, "mouth")
		c.fill(c.inter(mouth, c.poly([(cx - 12, 73), (cx + 12, 73), (cx + 12, 77.6), (cx - 12, 77.6)])), "tooth")
		c.fill(c.inter(mouth, c.ellipse(cx, 84.5, 5.5, 2.6)), "red_l")
		c.fill(c.limb([(cx - 12, 72.4), (cx - 8, 82.5), (cx, 86.5), (cx + 8, 82.5), (cx + 12, 72.4)], 1.4), "skin_dd")
	elif m == "snarl":
		mouth = c.poly([(cx - 10, 76), (cx + 10, 75), (cx + 8, 85), (cx - 8, 85)])
		c.fill(mouth, "mouth")
		c.fill(c.inter(mouth, c.poly([(cx - 11, 74), (cx + 11, 74), (cx + 11, 79.4), (cx - 11, 79.4)])), "tooth")
		c.fill(c.inter(mouth, c.poly([(cx - 8, 82.6), (cx + 8, 82.6), (cx + 8, 86), (cx - 8, 86)])), "tooth")
		c.fill(c.limb([(cx - 11, 76.5), (cx - 9, 85.5), (cx + 9, 85.5), (cx + 11, 76)], 1.3), "skin_dd")
	elif m == "frown":
		c.fill(c.limb([(cx - 9, 83), (cx - 4, 79), (cx + 4, 79), (cx + 9, 83)], 2.0), "skin_dd")
		c.fill(c.limb([(cx - 3, 86), (cx + 3, 86)], 1.0), "skin_d")
	elif m == "o":
		mouth = c.ellipse(cx, 80, 5.2, 6.6)
		c.shape(mouth, "mouth", None, "eye", depth=1.0)
		c.fill(c.inter(mouth, c.ellipse(cx, 84, 3.6, 2.4)), "red_l")
		c.fill(c.limb([(cx - 5.4, 80), (cx - 3, 86), (cx + 3, 86), (cx + 5.4, 80)], 1.2), "skin_dd")
	elif m == "grimace":
		mouth = c.poly([(cx - 10, 77), (cx + 10, 75.5), (cx + 8, 82), (cx + 3, 80.6), (cx - 2, 84), (cx - 8, 81)])
		c.fill(mouth, "mouth")
		c.fill(c.inter(mouth, c.poly([(cx - 11, 74), (cx + 11, 74), (cx + 11, 79), (cx - 11, 79)])), "tooth")
		c.fill(c.limb([(cx - 10, 77), (cx - 2, 84), (cx + 8, 82)], 1.2), "skin_dd")
	elif m == "tired":
		mouth = c.ellipse(cx, 80, 6.4, 3.0)
		c.fill(mouth, "mouth")
		c.fill(c.inter(mouth, c.poly([(cx - 8, 76), (cx + 8, 76), (cx + 8, 79), (cx - 8, 79)])), "tooth")
		c.fill(c.limb([(cx - 7, 78.4), (cx, 83.4), (cx + 7, 78.4)], 1.2), "skin_dd")


def _hair_layers(c: Canvas, e: Expr) -> None:
	cx, cy, rx, ry = CX, 43, 35, 28
	back = c.union(
		c.ellipse(cx, cy, rx, ry),
		c.poly([(27, 42), (22, 64), (30, 84), (39, 70), (40, 46)]),
		c.poly([(101, 42), (106, 64), (98, 84), (89, 70), (88, 46)]),
	)
	spikes = [(-160, 8, 11), (-132, 11, 10), (-104, 9, 9), (-84, 14, 9), (-58, 12, 10), (-30, 10, 10), (-6, 7, 10)]
	for ang, length, half in spikes:
		back = ImageChops.lighter(back, c.poly(_spike(cx, cy, rx, ry, ang, length, half)))
	_hair(c, back,
	      [[(34, 34), (30, 56)], [(94, 34), (98, 56)], [(54, 14), (50, 30)], [(76, 14), (82, 30)], [(64, 10), (66, 26)], [(44, 20), (40, 34)], [(88, 22), (92, 34)], [(70, 16), (72, 28)], [(58, 18), (56, 28)]],
	      [[(40, 22), (52, 12)], [(58, 12), (74, 10)], [(82, 14), (92, 22)], [(46, 26), (60, 18)], [(68, 20), (84, 22)]],
	      [[(44, 18), (54, 11)], [(60, 11), (70, 10)], [(86, 16), (91, 21)]])
	return back


def _fringe(c: Canvas, e: Expr, face_mask) -> None:
	locks = [
		[(33, 32), (46, 30), (41, 60)],
		[(44, 30), (58, 30), (50, 50)],
		[(54, 30), (70, 30), (62, 46)],
		[(66, 30), (82, 30), (78, 52)],
		[(78, 30), (95, 33), (91, 66)],
		[(36, 38), (46, 40), (33, 76)],
		[(92, 40), (96, 46), (95, 74)],
	]
	m = c.poly([(36, 26), (92, 26), (96, 36), (32, 36)])
	for lock in locks:
		c.poly(lock, m)
	# sombra de la melena sobre la frente
	shadow = ImageChops.offset(m, 0, 10)
	c.fill(c.minus(c.inter(shadow, face_mask), m), "skin_d")
	_hair(c, m,
	      [[(48, 34), (50, 46)], [(60, 34), (62, 42)], [(80, 34), (79, 48)], [(40, 40), (36, 58)], [(92, 44), (94, 64)]],
	      [[(40, 31), (52, 29)], [(58, 29), (72, 29)], [(76, 30), (90, 33)]],
	      [[(44, 30), (50, 28.6)], [(60, 28.4), (68, 28.2)], [(80, 29), (88, 31.4)]])


def render(name: str) -> Image.Image:
	e = EXPRESSIONS[name]
	c = Canvas(SIZE, 4)
	_body(c)
	_hair_layers(c, e)
	face_mask = c.union(c.ellipse(CX, 55, 27, 29), c.poly([(37, 62), (91, 62), (82 + e.tilt, 80), (CX + e.tilt, 90), (46 + e.tilt, 80)]))
	_face(c, e)
	_eye(c, e, -1, face_mask)
	_eye(c, e, 1, face_mask)
	c.fill(c.limb([(CX, 64), (CX - 1.6, 71)], 1.4), "skin_d")
	c.fill(c.ellipse(CX - 1.0, 72.2, 3.0, 1.1), "skin_dd")
	c.fill(c.ellipse(CX - 3.6, 66, 1.0, 2.0), "skin_l")
	_mouth(c, e)
	_fringe(c, e, face_mask)
	_brows(c, e)
	_extras(c, e, face_mask)
	return add_outline(c.to_pixels())


def _extras(c: Canvas, e: Expr, face_mask) -> None:
	ex = e.extras
	if "wrinkle" in ex:
		c.fill(c.inter(face_mask, c.limb([(CX - 3, 50), (CX - 2, 56)], 1.1)), "skin_dd")
		c.fill(c.inter(face_mask, c.limb([(CX + 3, 50), (CX + 2, 56)], 1.1)), "skin_dd")
	if "bags" in ex:
		for sd in (-1, 1):
			c.fill(c.inter(face_mask, c.limb([(CX + sd * 20, 67), (CX + sd * 13, 69.4), (CX + sd * 7, 67)], 1.4)), "skin_dd")
	if "sweat" in ex:
		for x, y, r in ((90, 40, 3.2), (96, 56, 2.6), (34, 44, 2.4)):
			c.fill(c.union(c.ellipse(x, y, r, r * 1.3), c.poly([(x, y - r * 2.4), (x - r * 0.8, y - r * 0.4), (x + r * 0.8, y - r * 0.4)])), "sweat")
	if "tear" in ex:
		c.fill(c.union(c.ellipse(CX - 16, 73, 2.0, 2.8), c.poly([(CX - 16, 66), (CX - 17.8, 71), (CX - 14.2, 71)])), "sweat")
		c.fill(c.limb([(CX - 16, 63), (CX - 16, 68)], 1.2), "sweat")
	if "blood" in ex:
		c.fill(c.inter(face_mask, c.limb([(90, 34), (89, 46), (88.5, 58), (88, 68)], 2.6)), "blood")
		c.fill(c.ellipse(88, 69, 1.8, 1.8), "blood")
	if "scratch" in ex:
		c.fill(c.inter(face_mask, c.limb([(42, 66), (53, 71)], 1.4)), "blood")
		c.fill(c.inter(face_mask, c.limb([(42, 69), (51, 74)], 1.0)), "skin_dd")

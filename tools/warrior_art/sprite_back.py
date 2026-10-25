"""Vista trasera (mirando hacia arriba): capa azul con emblema dorado, cabello y hombreras."""
from . import parts
from .hair import shade_hair
from .pose import Pose
from .raster import SPRITE_MARGIN, SPRITE_SIZE, Canvas

CX = 20.0


def _emblem(c: Canvas, cape, cy: float) -> None:
	"""Flor de lis dorada simplificada (pétalo central y dos curvos), recortada dentro de la capa."""
	m = c.union(
		c.limb([(CX, cy - 4.2), (CX, cy + 1.4)], 1.7),
		c.poly([(CX, cy - 5.2), (CX + 1.2, cy - 3.4), (CX - 1.2, cy - 3.4)]),
		c.limb([(CX - 1.0, cy + 0.4), (CX - 3.2, cy - 0.6), (CX - 3.8, cy - 2.8)], 1.3),
		c.limb([(CX + 1.0, cy + 0.4), (CX + 3.2, cy - 0.6), (CX + 3.8, cy - 2.8)], 1.3),
		c.limb([(CX - 3.2, cy + 1.8), (CX + 3.2, cy + 1.8)], 1.2),
		c.poly([(CX - 0.8, cy + 2.4), (CX + 0.8, cy + 2.4), (CX + 1.2, cy + 4.4), (CX - 1.2, cy + 4.4)]),
	)
	c.shape(m, "gold", "gold_l", None, depth=0.5)


def draw(c: Canvas, p: Pose) -> None:
	by = p.bob
	sw = p.sway
	parts.legs(c, p)
	# --- capa larga con dobladillo dorado ---
	top = 19.0 + by
	hem = 34.2 + by * 0.4
	cape = c.poly([
		(13.6, top), (26.4, top), (28.6 + 0.4 * sw, 26 + by), (29.4 + 1.0 * sw, hem - 1.0),
		(26.6 + 1.0 * sw, hem), (23.4 + 0.8 * sw, hem - 0.8), (20.0 + 0.6 * sw, hem + 0.2),
		(16.6 + 0.4 * sw, hem - 0.8), (13.4 + 0.2 * sw, hem), (10.6, hem - 1.0), (11.4, 26 + by),
	])
	c.shape(cape, "blue", "blue_l", "blue_d", depth=1.0)
	c.clip(cape, c.poly([(26, top), (30, top), (30.5, hem + 1), (24, hem + 1)]), "blue_d")
	c.clip(cape, c.poly([(10, top), (14.4, top), (13.4, hem + 1), (9.6, hem + 1)]), "blue_d")
	for x0, x1 in ((16.4, 16.0), (23.8, 24.4)):
		c.clip(cape, c.limb([(x0, 22 + by), (x1 + 0.4 * sw, hem - 2)], 0.8), "blue_d")
	c.clip(cape, c.limb([(18.4, 21 + by), (18.0 + 0.3 * sw, hem - 3)], 0.7), "blue_l")
	hem_band = c.minus(cape, c.poly([(0, 0), (40, 0), (40, hem - 2.0), (0, hem - 2.0)]))
	c.fill(hem_band, "gold")
	c.fill(c.minus(hem_band, c.poly([(0, 0), (40, 0), (40, hem - 1.2), (0, hem - 1.2)])), "gold_d")
	_emblem(c, cape, 26.4 + by)
	parts.arms(c, p)
	parts.pauldrons(c, p)
	# --- bufanda (vista trasera) ---
	c.shape(c.ellipse(CX, 18.4 + by, 8.2, 3.1), "blue", "blue_l", "blue_d")
	c.shape(c.ellipse(CX, 19.6 + by, 6.6, 1.8), "blue_d", "blue", "blue_dd", depth=0.7)
	# --- cabeza: solo pelo ---
	hy = by + 0.9
	hair = c.union(
		c.ellipse(CX, 8.2 + hy, 8.8, 6.6),
		c.poly([(11.8, 10 + hy), (13.4, 14.2 + hy), (17.6, 15.0 + hy), (22.4, 15.0 + hy), (26.6, 14.2 + hy), (28.2, 10 + hy)]),
		c.poly([(10.8, 4.6 + hy), (10.2, 1.8 + hy), (13.8, 3 + hy)]),
		c.poly([(13.6, 3 + hy), (15.6, 0.4 + hy), (18.2, 2.4 + hy)]),
		c.poly([(17.6, 2.4 + hy), (21.6, 0.0 + hy), (23.4, 2.2 + hy)]),
		c.poly([(22.6, 2.4 + hy), (27.6 + 0.5 * sw, 0.6 + hy), (26.8, 4 + hy)]),
		c.poly([(26.8, 3.6 + hy), (30.6 + 0.6 * sw, 3.4 + hy), (29.6, 7 + hy)]),
	)
	strokes_d = [[(14, 6 + hy), (14.6, 14 + hy)], [(18, 5 + hy), (18.4, 15 + hy)], [(22.2, 5 + hy), (21.8, 15.4 + hy)],
	             [(26, 6 + hy), (25.4, 14 + hy)], [(20, 9 + hy), (19.6, 13 + hy)], [(16, 11 + hy), (16.6, 14.4 + hy)], [(24, 11 + hy), (23.6, 14.4 + hy)]]
	strokes_l = [[(13, 5 + hy), (17, 3.4 + hy)], [(19, 4 + hy), (24, 4.6 + hy)], [(12.4, 9 + hy), (13.2, 13 + hy)]]
	shade_hair(c, hair, strokes_d, strokes_l, [[(14.6, 4.4 + hy), (17.0, 3.8 + hy)], [(19.6, 3.6 + hy), (22.6, 4.0 + hy)]])


def render(p: Pose):
	c = Canvas(SPRITE_SIZE, margin=SPRITE_MARGIN)
	draw(c, p)
	return c.to_pixels()

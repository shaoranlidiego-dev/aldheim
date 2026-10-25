"""Vista frontal (mirando hacia abajo) del Guerrero, cuadro de 40x40."""
from .hair import shade_hair
from . import parts
from .pose import Pose
from .raster import SPRITE_MARGIN, SPRITE_SIZE, Canvas

CX = 20.0


def draw(c: Canvas, p: Pose) -> None:
	by = p.bob
	sw = p.sway
	# --- capa asomando por los costados ---
	for sd in (-1, 1):
		x = lambda dx: CX + sd * dx
		cape = c.poly([(x(8.4), 20.5 + by), (x(11.4 + 0.6 * sw * sd), 27 + by), (x(11.0 + 0.8 * sw * sd), 32.6 + by),
		               (x(7.0), 31 + by), (x(6.0), 22 + by)])
		c.shape(cape, "blue_d", "blue", "blue_dd")
	parts.legs(c, p)
	# --- falda de placas y torso ---
	for sd in (-1, 1):
		x = lambda dx: CX + sd * dx
		plate = c.poly([(x(0.4), 28.6 + by), (x(5.8), 28.6 + by), (x(5.4), 32.2 + by * 0.5), (x(0.8), 32.8 + by * 0.5)])
		c.shape(plate, "steel_d", "steel", "steel_dd")
		c.fill(c.inter(plate, c.poly([(x(0.2), 31.4 + by * 0.5), (x(6), 31.2 + by * 0.5), (x(6), 33.4), (x(0.2), 33.4)])), "copper")
	torso = c.poly([(14.4, 19.4 + by), (25.6, 19.4 + by), (26.0, 26 + by), (24.8, 29.2 + by), (15.2, 29.2 + by), (14.0, 26 + by)])
	c.shape(torso, "steel_d", "steel", "steel_dd")
	chest = c.poly([(15.4, 19.8 + by), (24.6, 19.8 + by), (24.2, 25.4 + by), (20, 27.2 + by), (15.8, 25.4 + by)])
	c.shape(chest, "steel", "steel_l", "steel_d")
	c.clip(chest, c.poly([(20, 19 + by), (26, 19 + by), (26, 28 + by), (20, 28 + by)]), "steel_d")
	c.clip(chest, c.limb([(15.6, 25.2 + by), (20, 27.1 + by), (24.4, 25.2 + by)], 0.9), "copper")
	c.fill(c.poly([(20, 21.2 + by), (21.6, 23.2 + by), (20, 25.2 + by), (18.4, 23.2 + by)]), "gold")
	c.fill(c.ellipse(20, 23.2 + by, 0.7, 0.7), "red_l")
	belt = c.poly([(13.8, 27.4 + by), (26.2, 27.4 + by), (25.8, 29.6 + by), (14.2, 29.6 + by)])
	c.shape(belt, "leather", "leather_l", "leather_d", depth=0.8)
	c.shape(c.poly([(18.6, 27.4 + by), (21.4, 27.4 + by), (21.4, 29.6 + by), (18.6, 29.6 + by)]), "gold", "gold_l", "gold_d", depth=0.6)
	parts.arms(c, p)
	parts.pauldrons(c, p)
	# --- bufanda ---
	c.shape(c.ellipse(CX, 18.4 + by, 8.2, 3.1), "blue", "blue_l", "blue_d")
	c.shape(c.union(c.ellipse(CX - 2.6, 19.6 + by, 3.4, 2.3), c.ellipse(CX + 1.4, 20.0 + by, 3.0, 2.0)), "blue_d", "blue", "blue_dd", depth=0.8)
	tail = c.poly([(22.4, 19.4 + by), (27.6, 19.8 + by), (28.4 + 0.5 * sw, 25.4 + by), (27.2 + sw, 28.2 + by), (24.2 + 0.6 * sw, 25.6 + by)])
	c.shape(tail, "blue", "blue_l", "blue_dd")
	c.clip(tail, c.limb([(25.6, 20 + by), (26.2, 27 + by)], 0.7), "blue_d")
	# --- cabeza ---
	hy = by + 0.9
	back_hair = c.union(
		c.ellipse(CX, 7.4 + hy, 8.8, 6.6),
		c.poly([(11.2, 6 + hy), (9.4, 8.6 + hy), (10.2, 12.4 + hy), (13.4, 10 + hy)]),
		c.poly([(28.8, 6 + hy), (30.6, 8.6 + hy), (29.8, 12.4 + hy), (26.6, 10 + hy)]),
		c.poly([(10.6, 4.6 + hy), (10.0, 1.8 + hy), (13.6, 3 + hy)]),
		c.poly([(13.4, 3 + hy), (15.4, 0.2 + hy), (18, 2.4 + hy)]),
		c.poly([(17.4, 2.4 + hy), (21.4, -0.4 + hy), (23.2, 2.2 + hy)]),
		c.poly([(22.4, 2.4 + hy), (27.4 + 0.5 * sw, 0.4 + hy), (26.6, 4 + hy)]),
		c.poly([(26.6, 3.6 + hy), (30.4 + 0.6 * sw, 3.4 + hy), (29.4, 7 + hy)]),
	)
	shade_hair(c, back_hair, [[(12, 4 + hy), (14, 8 + hy)], [(27, 4 + hy), (25, 8 + hy)]], [])
	face = c.union(
		c.ellipse(CX, 10.2 + hy, 6.5, 5.7),
		c.poly([(13.6, 10.8 + hy), (26.4, 10.8 + hy), (24.8, 14.6 + hy), (20, 16.6 + hy), (15.2, 14.6 + hy)]),
	)
	c.shape(c.union(c.ellipse(13.6, 11.4 + hy, 1.3, 1.7), c.ellipse(26.4, 11.4 + hy, 1.3, 1.7)), "skin_d", None, "skin_dd", depth=0.5)
	c.shape(face, "skin", "skin_l", "skin_d")
	c.clip(face, c.poly([(22.6, 4 + hy), (28, 4 + hy), (28, 17 + hy), (21.4, 17 + hy)]), "skin_d")
	c.fill(c.inter(face, c.ellipse(20, 17.2 + hy, 6.4, 2.0)), "skin_dd")
	for sd in (-1, 1):
		ex, ey = CX + sd * 3.0, 11.9 + hy
		c.fill(c.ellipse(ex, ey, 1.3, 1.7), "eye")
		c.fill(c.ellipse(ex, ey + 0.7, 0.9, 0.7), "iris_l")
		c.fill(c.ellipse(ex - 0.45, ey - 0.8, 0.38, 0.38), "white")
		c.fill(c.limb([(ex - sd * 2.0, ey - 3.0 + 0.0), (ex + sd * 1.3, ey - 2.3)], 0.9), "hair_d")
		c.fill(c.ellipse(ex + sd * 1.8, ey + 1.7, 1.0, 0.6), "blush")
	c.fill(c.ellipse(CX, 13.8 + hy, 0.5, 0.35), "skin_dd")
	c.fill(c.limb([(18.9, 15.0 + hy), (21.1, 15.0 + hy)], 0.5), "skin_dd")
	fringe = c.union(
		c.poly([(12.4, 6.6 + hy), (27.6, 6.6 + hy), (27.4, 9 + hy), (26.0, 8.0 + hy), (25.2, 11.2 + hy), (23.6, 8.2 + hy),
		        (22.2, 10.4 + hy), (20.6, 7.8 + hy), (19.4, 10.0 + hy), (17.4, 7.8 + hy), (16.2, 11.0 + hy), (14.8, 8.2 + hy),
		        (13.0, 10.2 + hy)]),
		c.poly([(12.0, 7 + hy), (14.2, 9 + hy), (13.6, 13.2 + hy), (11.8, 12 + hy)]),
		c.poly([(28.0, 7 + hy), (25.8, 9 + hy), (26.4, 13.2 + hy), (28.2, 12 + hy)]),
	)
	shade_hair(c, fringe,
	           [[(15, 7 + hy), (16, 10 + hy)], [(21, 7 + hy), (21.4, 9.6 + hy)], [(24.4, 7 + hy), (25, 10.4 + hy)]],
	           [[(13.4, 7.4 + hy), (17.6, 7.2 + hy)]], [[(14.6, 6.9 + hy), (17.0, 6.8 + hy)]])


def render(p: Pose) -> "Image.Image":
	c = Canvas(SPRITE_SIZE, margin=SPRITE_MARGIN)
	draw(c, p)
	return c.to_pixels()

"""Vista lateral (mirando a la izquierda). La derecha es su espejo. Piernas y brazos con cinemática simple."""
import math

from .hair import shade_hair
from .pose import Pose
from .raster import SPRITE_MARGIN, SPRITE_SIZE, Canvas

HIP_X = 19.8
THIGH, SHIN = 3.8, 4.3


def _leg(c: Canvas, hip, swing: float, lift: float, far: bool) -> None:
	theta = math.radians(30 * swing)
	bend = math.radians(55 * lift)
	knee = (hip[0] - math.sin(theta) * THIGH, hip[1] + math.cos(theta) * THIGH)
	t2 = theta - bend
	ankle = (knee[0] - math.sin(t2) * SHIN, knee[1] + math.cos(t2) * SHIN)
	cloth, steel, leather = ("cloth_d", "steel_d", "leather_d") if far else ("cloth", "steel_d", "leather")
	c.shape(c.limb([hip, knee], 4.6), cloth, None, "cloth_d" if not far else "line")
	shin = c.limb([knee, ankle], 4.3)
	c.shape(shin, steel, None if far else "steel", "steel_dd")
	if not far:
		c.fill(c.ellipse(knee[0], knee[1], 1.9, 1.7), "steel")
		c.fill(c.inter(c.ellipse(knee[0], knee[1], 1.9, 1.7), c.ellipse(knee[0] + 0.5, knee[1] + 0.9, 2.0, 1.2)), "copper")
		c.fill(c.inter(shin, c.ellipse(ankle[0] + 0.2, ankle[1] - 2.2, 2.4, 0.8)), "copper")
	ax, ay = ankle
	boot = c.union(c.poly([(ax + 1.8, ay - 2.4), (ax - 1.6, ay - 2.4), (ax - 4.0, ay + 0.4), (ax - 3.6, ay + 1.7), (ax + 2.0, ay + 1.7)]),
	               c.ellipse(ax - 1.6, ay + 0.6, 2.6, 1.3))
	c.shape(boot, leather, None if far else "leather_l", "leather_d" if not far else "line", depth=0.8)


def _arm(c: Canvas, shoulder, swing: float, far: bool) -> None:
	a1 = math.radians(32 * swing)
	elbow = (shoulder[0] - math.sin(a1) * 3.6, shoulder[1] + math.cos(a1) * 3.6)
	a2 = a1 - math.radians(22)
	hand = (elbow[0] - math.sin(a2) * 3.4, elbow[1] + math.cos(a2) * 3.4)
	sleeve, plate = ("cloth_d", "steel_d") if far else ("cloth", "steel_d")
	c.shape(c.limb([shoulder, elbow], 4.0), sleeve, None, "line" if far else "cloth_d")
	fore = c.limb([elbow, hand], 4.2)
	c.shape(fore, plate, None if far else "steel", "steel_dd")
	if not far:
		c.fill(c.inter(fore, c.ellipse(elbow[0] - (hand[0] - elbow[0]) * 0.25, elbow[1] + 0.9, 2.6, 0.8)), "copper")
	c.shape(c.ellipse(hand[0], hand[1] + 0.6, 1.8, 1.7), "skin_d" if far else "skin", None if far else "skin_l", "skin_d", depth=0.6)


def draw(c: Canvas, p: Pose) -> None:
	by = p.bob
	sw = p.sway
	hip_y = 29.0 + by
	_leg(c, (HIP_X + 0.8, hip_y), p.swing_r, p.lift_r, far=True)
	# capa detrás del cuerpo, con ondulación
	cape = c.poly([(21.6, 19.2 + by), (24.4, 20 + by), (28.0 + sw * 0.8, 24 + by), (31.2 + sw * 1.4, 32.4 + by * 0.5),
	               (28.2 + sw * 1.2, 31.4 + by * 0.5), (25.6 + sw, 33.6 + by * 0.5), (22.4, 31.4 + by * 0.5), (21.0, 26 + by)])
	c.shape(cape, "blue_d", "blue", "blue_dd")
	c.clip(cape, c.limb([(23.4, 21 + by), (26.4 + sw * 0.8, 31.4)], 0.8), "blue")
	c.clip(cape, c.limb([(26.6 + sw * 0.6, 24 + by), (29.0 + sw * 1.2, 32)], 0.9), "blue_dd")
	hem = c.minus(cape, c.poly([(0, 0), (40, 0), (40, 31.0), (0, 31.0)]))
	c.fill(hem, "gold_d")
	c.fill(c.limb([(22.4, 31.2 + by * 0.5), (25.6 + sw, 33.0 + by * 0.5), (28.2 + sw * 1.2, 31.0 + by * 0.5), (31.0 + sw * 1.4, 32.2 + by * 0.5)], 0.6), "gold")
	_arm(c, (HIP_X + 1.2, 20.8 + by), p.arm_r, far=True)
	# torso
	torso = c.poly([(16.0, 19.4 + by), (23.8, 19.4 + by), (24.2, 26 + by), (23.2, 29.4 + by), (16.8, 29.4 + by), (15.8, 26 + by)])
	c.shape(torso, "steel_d", "steel", "steel_dd")
	chest = c.poly([(16.2, 19.8 + by), (21.6, 19.8 + by), (21.4, 25.6 + by), (17.4, 26.6 + by), (16.0, 24.4 + by)])
	c.shape(chest, "steel", "steel_l", "steel_d")
	c.clip(chest, c.limb([(16.2, 25.4 + by), (21.2, 25.4 + by)], 0.9), "copper")
	c.fill(c.poly([(17.2, 21.6 + by), (18.4, 23 + by), (17.2, 24.4 + by), (16.4, 23 + by)]), "gold")
	c.shape(c.poly([(15.6, 27.4 + by), (24.4, 27.4 + by), (24.2, 29.6 + by), (15.8, 29.6 + by)]), "leather", "leather_l", "leather_d", depth=0.7)
	c.shape(c.poly([(16.4, 27.4 + by), (18.4, 27.4 + by), (18.4, 29.6 + by), (16.4, 29.6 + by)]), "gold", "gold_l", "gold_d", depth=0.5)
	c.shape(c.poly([(16.2, 29.4 + by), (23.4, 29.4 + by), (22.6, 32.4 + by * 0.5), (17.2, 32.8 + by * 0.5)]), "steel_d", "steel", "steel_dd")
	c.fill(c.minus(c.poly([(16.2, 29.4 + by), (23.4, 29.4 + by), (22.6, 32.4 + by * 0.5), (17.2, 32.8 + by * 0.5)]),
	               c.poly([(0, 0), (40, 0), (40, 31.4), (0, 31.4)])), "copper")
	_leg(c, (HIP_X - 0.2, hip_y), p.swing_l, p.lift_l, far=False)
	_arm(c, (HIP_X - 0.2, 20.8 + by), p.arm_l, far=False)
	# hombrera cercana
	dome = c.ellipse(HIP_X - 0.2, 20.8 + by, 3.9, 3.4)
	c.shape(dome, "steel", "steel_h", "steel_d")
	c.clip(dome, c.ellipse(HIP_X + 0.8, 22.2 + by, 3.4, 2.6), "steel_d")
	rim = c.minus(dome, c.ellipse(HIP_X - 0.2, 19.8 + by, 3.9, 3.4))
	c.fill(rim, "copper")
	c.fill(c.inter(rim, c.ellipse(HIP_X - 1.4, 22.8 + by, 2.0, 1.6)), "copper_l")
	c.fill(c.ellipse(HIP_X - 1.0, 20.3 + by, 0.5, 0.5), "gold_l")
	# bufanda con cola al viento
	tail = c.poly([(21.4, 17.8 + by), (25, 17.6 + by), (29.6 + sw * 1.4, 19.0 + by), (31.0 + sw * 1.6, 21.6 + by),
	               (27.4 + sw * 1.0, 21.2 + by), (24.4, 21.4 + by), (21.8, 20.8 + by)])
	c.shape(tail, "blue", "blue_l", "blue_dd")
	c.clip(tail, c.limb([(24, 19.2 + by), (29 + sw * 1.2, 20.0 + by)], 0.7), "blue_d")
	c.shape(c.ellipse(19.0, 17.8 + by, 4.9, 2.6), "blue", "blue_l", "blue_d")
	c.shape(c.ellipse(17.4, 18.9 + by, 2.8, 1.5), "blue_d", "blue", "blue_dd", depth=0.7)
	# cabeza en perfil
	hy = by + 0.9
	back_hair = c.union(
		c.ellipse(20.8, 7.8 + hy, 8.4, 6.6),
		c.poly([(15.6, 9 + hy), (27.6, 9 + hy), (27.2, 14 + hy), (24.4, 16.0 + hy), (19.4, 14 + hy)]),
		c.poly([(13.6, 3.6 + hy), (15.6, 0.6 + hy), (18.6, 2.6 + hy)]),
		c.poly([(18.0, 2.4 + hy), (22.4, 0.2 + hy), (24.2, 2.8 + hy)]),
		c.poly([(23.4, 2.8 + hy), (28.6 + sw * 0.6, 1.8 + hy), (27.4, 5.2 + hy)]),
		c.poly([(26.6, 5 + hy), (31.8 + sw * 1.0, 5.2 + hy), (28.4, 9.4 + hy)]),
		c.poly([(25.4, 10 + hy), (30.2 + sw * 1.2, 12.4 + hy), (25.2, 14.6 + hy)]),
	)
	shade_hair(c, back_hair, [[(23, 5 + hy), (25.5, 12 + hy)], [(20.6, 6 + hy), (22.8, 13 + hy)], [(26, 7 + hy), (28, 10 + hy)]],
	           [[(16, 3.8 + hy), (20, 3.4 + hy)]], [[(17, 3.4 + hy), (19.6, 3.0 + hy)]])
	face = c.union(
		c.ellipse(16.8, 10.6 + hy, 5.2, 5.5),
		c.poly([(12.4, 11.6 + hy), (20.4, 11.6 + hy), (19.2, 15.4 + hy), (15.8, 16.4 + hy), (13.0, 14.6 + hy)]),
		c.ellipse(11.7, 12.4 + hy, 1.0, 1.0),
	)
	c.shape(c.ellipse(20.0, 11.8 + hy, 1.2, 1.6), "skin_d", None, "skin_dd", depth=0.5)
	c.shape(face, "skin", "skin_l", "skin_d")
	c.clip(face, c.poly([(17.4, 4 + hy), (23, 4 + hy), (23, 17 + hy), (16.4, 17 + hy)]), "skin_d")
	ex, ey = 14.2, 11.8 + hy
	c.fill(c.ellipse(ex, ey, 1.05, 1.6), "eye")
	c.fill(c.ellipse(ex - 0.2, ey + 0.8, 0.7, 0.6), "iris_l")
	c.fill(c.ellipse(ex - 0.5, ey - 0.9, 0.34, 0.34), "white")
	c.fill(c.limb([(12.2, ey - 3.0), (15.6, ey - 2.4)], 0.9), "hair_d")
	c.fill(c.limb([(12.6, 14.8 + hy), (14.2, 14.8 + hy)], 0.5), "skin_dd")
	c.fill(c.ellipse(16.0, 13.6 + hy, 0.9, 0.6), "blush")
	fringe = c.union(
		c.poly([(11.8, 6.4 + hy), (23, 6.0 + hy), (22.6, 9 + hy), (20.6, 8.2 + hy), (19.4, 11 + hy), (17.6, 8.4 + hy),
		        (16.4, 10.8 + hy), (14.8, 8.4 + hy), (13.2, 10.4 + hy), (11.4, 9.6 + hy)]),
		c.poly([(19.8, 7 + hy), (23.2, 8 + hy), (22.4, 13.6 + hy), (19.6, 12 + hy)]),
	)
	shade_hair(c, fringe, [[(15.4, 7 + hy), (16.2, 10 + hy)], [(19, 7 + hy), (19.6, 11 + hy)]], [[(13.4, 7.2 + hy), (18, 6.6 + hy)]],
	           [])


def render(p: Pose):
	c = Canvas(SPRITE_SIZE, margin=SPRITE_MARGIN)
	draw(c, p)
	return c.to_pixels()

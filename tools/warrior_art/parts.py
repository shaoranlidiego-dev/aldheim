"""Piezas compartidas por las vistas frontal y trasera."""
from .pose import Pose
from .raster import Canvas

CX = 20.0


def legs(c: Canvas, p: Pose) -> None:
	by = p.bob
	for sd, swing, lift in ((-1, p.swing_l, p.lift_l), (1, p.swing_r, p.lift_r)):
		fx = CX + sd * 3.5
		fy = 37.0 + 0.8 * swing - 2.4 * lift
		hip = (CX + sd * 3.4, 29.0 + by)
		thigh = c.limb([hip, (fx, (hip[1] + fy) / 2 - 1.0)], 4.6)
		c.shape(thigh, "cloth", None, "cloth_d")
		greave = c.limb([(fx, fy - 4.6), (fx, fy - 1.4)], 4.6)
		c.shape(greave, "steel_d", "steel", "steel_dd")
		c.fill(c.inter(greave, c.poly([(fx - 3, fy - 4.9), (fx + 3, fy - 4.9), (fx + 3, fy - 3.7), (fx - 3, fy - 3.7)])), "copper")
		boot = c.union(c.ellipse(fx, fy - 0.1, 3.0, 2.2), c.poly([(fx - 2.4, fy - 2.6), (fx + 2.4, fy - 2.6), (fx + 2.8, fy), (fx - 2.8, fy)]))
		c.shape(boot, "leather", "leather_l", "leather_d")


def arms(c: Canvas, p: Pose) -> None:
	by = p.bob
	for sd, arm in ((-1, p.arm_l), (1, p.arm_r)):
		sx = CX + sd * 8.2
		hx = sx + sd * 0.7
		hy = 28.0 + by + 1.5 * arm
		ey = 24.6 + by + 0.6 * arm
		upper = c.limb([(sx, 21 + by), (sx + sd * 0.4, ey)], 3.8)
		c.shape(upper, "cloth", "steel_d", "cloth_d")
		fore = c.limb([(sx + sd * 0.4, ey), (hx, hy - 1.6)], 4.2)
		c.shape(fore, "steel_d", "steel", "steel_dd")
		c.fill(c.inter(fore, c.ellipse(hx, ey + 1.0, 3, 0.9)), "copper")
		c.shape(c.ellipse(hx, hy, 1.9, 1.7), "skin", "skin_l", "skin_d", depth=0.6)


def pauldrons(c: Canvas, p: Pose) -> None:
	by = p.bob
	for sd in (-1, 1):
		x = lambda dx: CX + sd * dx
		dome = c.ellipse(x(8.5), 19.9 + by, 4.1, 3.4)
		c.shape(dome, "steel", "steel_h", "steel_d")
		c.clip(dome, c.ellipse(x(9.8), 21.3 + by, 3.7, 2.6), "steel_d")
		rim = c.minus(dome, c.ellipse(x(8.5), 18.9 + by, 4.1, 3.4))
		c.fill(rim, "copper")
		c.fill(c.inter(rim, c.ellipse(x(8.5) - sd * 1.3, 22 + by, 2.2, 1.8)), "copper_l")
		c.fill(c.ellipse(x(8.2), 19.4 + by, 0.55, 0.55), "gold_l")

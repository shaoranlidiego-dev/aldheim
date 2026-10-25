"""Retrato piloto del Guerrero (128x128, vista de tres cuartos). Trabajo en curso: docs/art/wip/."""
from PIL import Image

from .painter import Material, Painter, bezier, cleanup, dither_edges, smooth

N, S = 128, 3

MATERIALS = {
	"skin": Material(["#392a47", "#6c4350", "#ad6a56", "#dc9066", "#f5bb8a", "#ffe1b4"], [-0.05, 0.25, 0.48, 0.66, 0.86]),
	"hair": Material(["#160d1a", "#2e1b22", "#4b2b1e", "#6e4023", "#965a2b", "#c4853f"], [0.02, 0.30, 0.56, 0.76, 0.92]),
	"cloth": Material(["#0a1436", "#142a64", "#22459a", "#3a70c6", "#6aa3e8"], [0.05, 0.34, 0.60, 0.84]),
	"steel": Material(["#0d101c", "#1c2236", "#323e5a", "#56688a", "#93a4c4", "#e4ecfa"], [0.10, 0.36, 0.58, 0.76, 0.90], spec=0.80, spec_pow=34),
	"copper": Material(["#35190f", "#74401e", "#b3652c", "#e29646", "#ffd37e"], [0.05, 0.32, 0.58, 0.82]),
	"leather": Material(["#1a100e", "#38211a", "#5b3a24", "#84573a"], [0.1, 0.4, 0.66]),
	"gold": Material(["#4a2c10", "#8f5e1e", "#d49a3a", "#f6cd6a", "#fff0a8"], [0.05, 0.32, 0.58, 0.82]),
}

FACE = [(38, 34), (44, 26), (56, 21), (70, 21), (82, 26), (88, 36), (89, 48), (88, 58), (86, 68), (83, 78), (77, 86),
        (69, 90.5), (60, 91.5), (53, 90), (46, 85), (42, 76), (38, 62), (37, 48)]
NECK = [(52, 78), (80, 74), (84, 104), (48, 108)]


def face_relief(p: Painter):
	r = p.zeros()
	for cx, cy, sx, sy, amp, ang in (
		(66, 60, 2.6, 8, 3.5, 0.08),     # puente de la nariz
		(71, 70, 4.2, 3.6, 4.6, 0),      # punta
		(64.5, 72.5, 2.6, 2.0, 2.2, 0),  # ala izquierda
		(77, 71.5, 2.6, 2.0, 2.0, 0),    # ala derecha
		(54, 49, 8, 2.6, 3.2, -0.12),    # arco de la ceja cercana
		(77, 48, 6, 2.6, 2.6, 0.12),     # ceja lejana
		(54, 55.5, 6.5, 4.2, -2.0, 0),   # cuenca cercana
		(77, 54.5, 5, 3.6, -1.8, 0),     # cuenca lejana
		(46, 66, 6, 5, 2.8, 0),          # pómulo cercano
		(83, 63, 3.6, 5, 2.0, 0),        # pómulo lejano
		(69, 80, 6.5, 2.0, 2.6, 0),      # labios
		(69, 84.2, 5, 1.4, -2.2, 0),     # surco bajo el labio
		(66, 87.5, 6, 3.5, 3.0, 0),      # mentón
		(45, 80, 4.5, 6, 2.6, -0.7),     # ángulo de la mandíbula
	):
		p.bump(r, cx, cy, sx, sy, amp, ang)
	return r


import random

# Mechón = (raíz, ctrl1, ctrl2, punta, (ancho raíz, medio, punta), sesgo de luz). Se pintan de atrás hacia adelante.
# Mechón principal = (raíz, ctrl1, ctrl2, punta), n hebras, separación en la raíz, ancho de hebra, sesgo de luz.
BACK_FLOWS = [
	(((86, 62), (98, 70), (96, 82), (90, 96)), 5, 12, 6.5, -0.32),
	(((42, 56), (30, 68), (32, 82), (40, 94)), 5, 10, 6.0, -0.34),
	(((40, 40), (26, 46), (24, 58), (30, 72)), 6, 12, 6.5, -0.26),
	(((88, 40), (100, 46), (104, 58), (98, 72)), 6, 12, 6.5, -0.26),
]
CAP = [(34, 52), (30, 34), (40, 18), (56, 10), (76, 10), (92, 18), (102, 34), (100, 54), (93, 46), (88, 36), (76, 31),
       (62, 30), (50, 34), (44, 42), (39, 54)]
TOP_FLOWS = [
	(((44, 30), (39, 26), (36, 22), (36, 17)), 6, 11, 6.2, -0.14),
	(((54, 22), (50, 14), (54, 8), (62, 4)), 6, 12, 6.5, -0.04),
	(((66, 20), (66, 12), (74, 8), (86, 8)), 7, 14, 6.5, 0.02),
	(((80, 24), (88, 18), (96, 20), (104, 28)), 6, 12, 6.5, -0.06),
	(((90, 36), (98, 38), (102, 46), (102, 60)), 5, 10, 6.0, -0.16),
]
FRONT_FLOWS = [
	(((90, 40), (94, 48), (94, 58), (90, 70)), 3, 6, 5.5, -0.08),
	(((46, 30), (40, 38), (40, 50), (44, 62)), 4, 8, 6.0, -0.02),
	(((55, 26), (50, 34), (58, 40), (51, 52)), 4, 8, 6.0, 0.04),
	(((66, 25), (62, 32), (70, 38), (62, 48)), 4, 9, 6.0, 0.08),
	(((79, 26), (82, 35), (74, 42), (65, 50)), 4, 9, 6.0, 0.10),
	(((87, 32), (91, 40), (88, 48), (82, 56)), 3, 6, 5.5, 0.0),
]


def _jitter(rng, pts, amount):
	return tuple((x + rng.uniform(-amount, amount), y + rng.uniform(-amount, amount)) for x, y in pts)


def paint_flows(p: Painter, flows, seed: int, shadow: float, groove: bool = True):
	rng = random.Random(seed)
	for guide, n, spread, width, bias in flows:
		root, c1, c2, tip = guide
		dx, dy = c1[0] - root[0], c1[1] - root[1]
		ln = max(1e-6, (dx * dx + dy * dy) ** 0.5)
		nx, ny = -dy / ln, dx / ln
		order = list(range(n))
		rng.shuffle(order)
		for k in order:
			u = (k / max(1, n - 1) - 0.5) * spread
			f = rng.uniform(0.82, 1.06)
			off = (1.0, 0.85, 0.45, 0.12)
			pts = []
			for idx, (x, y) in enumerate((root, c1, c2, tip)):
				if idx == 3:
					x, y = root[0] + (x - root[0]) * f, root[1] + (y - root[1]) * f
				pts.append((x + nx * u * off[idx], y + ny * u * off[idx]))
			ctrl = _jitter(rng, pts, 1.1)
			w = width * rng.uniform(0.85, 1.15)
			m = p.ribbon(ctrl, (w * 1.1, w, 1.2))
			b = bias + rng.uniform(-0.07, 0.07)
			p.paint(m, "hair", sigma=1.5, depth=3.6, bias=b, shadow=shadow)
			if groove and rng.random() < 0.7:
				hi = tuple((x - 1.1, y - 1.1) for x, y in bezier_slice(ctrl, 0.25, 0.7))
				p.lighten(p.ribbon(hi, (0.9, 1.0, 0.4)), 1, "hair")


def bezier_slice(ctrl, t0, t1):
	pts = bezier(*ctrl, steps=20)
	a, b = int(t0 * 20), int(t1 * 20)
	sub = pts[a:b + 1]
	k = len(sub) - 1
	return (sub[0], sub[k // 3], sub[2 * k // 3], sub[k])


def _face_planes(p: Painter) -> None:
	"""Sombras y luces de forma colocadas a mano sobre la piel (como haría un artista)."""
	dk = lambda pts, n=1: p.darken(p.poly(smooth(pts, 2)), n, "skin")
	lt = lambda pts, n=1: p.lighten(p.poly(smooth(pts, 2)), n, "skin")
	dk([(78, 66), (88, 62), (90, 82), (80, 88), (73, 80)])                    # hueco del pómulo lejano
	dk([(43, 84), (56, 93), (72, 93), (82, 87), (78, 92), (60, 97), (44, 91)])  # debajo de la mandíbula
	dk([(37, 60), (42, 70), (44, 84), (38, 76)])                              # contorno cercano de la mejilla
	lt([(44, 62), (53, 63), (55, 73), (46, 75)])                              # pómulo cercano iluminado
	lt([(64, 52), (67, 52), (68, 66), (65, 66)])                              # puente nasal
	lt([(60, 86), (70, 86), (71, 90), (60, 90)])                              # mentón


def ribbon_paint(p, ctrl, widths, mat, **kw):
	m = p.ribbon(ctrl, widths)
	p.paint(m, mat, **kw)
	return m


def paint_body(p: Painter, rng) -> None:
	# capa azul detrás del hombro lejano
	cape = p.poly(smooth([(90, 88), (112, 94), (128, 108), (128, 128), (92, 128), (98, 106)], 2))
	p.paint(cape, "cloth", sigma=6, depth=9, bias=-0.30, shadow=0)
	for ctrl in (((98, 96), (106, 106), (108, 118), (104, 130)), ((110, 98), (118, 108), (120, 120), (118, 132))):
		p.darken(p.ribbon(ctrl, (2.2, 3, 2)), 1, "cloth")
	# hombrera lejana: cúpula con dos láminas y ribete de cobre
	far = p.poly(smooth([(84, 110), (92, 100), (106, 96), (120, 100), (128, 110), (128, 128), (88, 128)], 2))
	p.paint(far, "steel", sigma=7, depth=11, bias=-0.36, shadow=1.4)
	for k, (a, b, c, d) in enumerate((((90, 108), (100, 100), (114, 100), (128, 110)), ((92, 120), (102, 112), (116, 112), (128, 122)))):
		p.paint(p.ribbon((a, b, c, d), (6.5, 7.5, 6.5)), "steel", sigma=2.4, depth=4.5, bias=-0.34 + 0.04 * k, shadow=1.0)
		p.paint(p.ribbon(((a[0], a[1] + 3.6), (b[0], b[1] + 3.8), (c[0], c[1] + 3.8), (d[0], d[1] + 3.6)), (3.0, 3.4, 3.0)), "copper", sigma=1.2, depth=2.8, shadow=0.6)
	# peto oscuro con correa de cuero
	chest = p.poly(smooth([(34, 100), (60, 98), (92, 98), (104, 116), (108, 128), (24, 128)], 2))
	p.paint(chest, "steel", sigma=8, depth=9, bias=-0.38, shadow=0)
	strap = ribbon_paint(p, ((38, 100), (58, 112), (82, 124), (104, 134)), (8.5, 8.5, 8.5), "leather", sigma=2.2, depth=3.2, shadow=1.4)
	p.darken(p.ribbon(((40, 104), (60, 116), (84, 128), (104, 138)), (1.0, 1.0, 1.0)), 1, "leather")
	# hombrera cercana: cúpula con láminas y ribete de cobre
	dome = p.poly(smooth([(-6, 112), (0, 100), (12, 92), (28, 92), (42, 100), (50, 114), (48, 128), (-6, 128)], 2))
	p.paint(dome, "steel", sigma=8, depth=15, bias=-0.34, shadow=1.8)
	for k, (a, b, c, d) in enumerate((((-2, 106), (12, 98), (30, 98), (44, 108)),
	                                   ((0, 116), (14, 108), (32, 108), (47, 120)),
	                                   ((0, 126), (14, 118), (32, 118), (48, 130)))):
		lame = p.ribbon((a, b, c, d), (7.5, 8.5, 7.5))
		p.paint(lame, "steel", sigma=2.8, depth=5.0, bias=-0.30 + 0.05 * (2 - k), shadow=1.2)
		p.paint(p.ribbon(((a[0], a[1] + 4.2), (b[0], b[1] + 4.4), (c[0], c[1] + 4.4), (d[0], d[1] + 4.2)), (3.4, 3.8, 3.4)), "copper", sigma=1.3, depth=3.2, shadow=0.7)
	for cx, cy in ((6, 104), (22, 99), (38, 104)):
		p.paint(p.ellipse(cx, cy, 1.5, 1.5), "gold", sigma=0.6, depth=1.5, shadow=0.4)
	# medallón dorado sobre la correa
	p.paint(p.ellipse(46, 122, 7.5, 7.5), "copper", sigma=1.5, depth=3.2, shadow=1.4)
	p.paint(p.ellipse(46, 122, 5.2, 5.2), "gold", sigma=1.2, depth=2.6, shadow=0.6)
	p.paint(p.ellipse(46, 122, 2.0, 2.0), "cloth", sigma=0.6, depth=1.2, shadow=0.3, bias=0.2)


def paint_scarf(p: Painter) -> None:
	def cloth(ctrl, widths, bias=0.0, depth=6.5, sigma=3.0):
		m = p.ribbon(ctrl, widths)
		p.paint(m, "cloth", sigma=sigma, depth=depth, bias=bias, shadow=1.6)
		return m
	cloth(((34, 96), (50, 90), (74, 88), (98, 98)), (14, 17, 13), -0.18)                   # vuelta trasera
	cloth(((36, 100), (48, 114), (82, 118), (98, 104)), (16, 20, 15), 0.0)                  # vuelta delantera
	cloth(((44, 98), (56, 110), (74, 112), (86, 102)), (11, 15, 11), 0.08, depth=5.5)       # pliegue alto
	cloth(((78, 106), (88, 116), (84, 128), (74, 138)), (15, 15, 12), 0.04)                 # cola colgante
	for ctrl in (((50, 104), (58, 112), (70, 112), (80, 104)), ((84, 110), (90, 118), (86, 128), (78, 136)),
	             ((40, 104), (46, 112), (58, 118), (70, 118))):
		p.darken(p.ribbon(ctrl, (1.6, 2.2, 1.4)), 1, "cloth")
	for ctrl in (((46, 98), (56, 106), (72, 108), (84, 100)), ((80, 112), (86, 118), (84, 126), (78, 132))):
		p.lighten(p.ribbon(tuple((x - 1.5, y - 1.8) for x, y in ctrl), (1.4, 1.8, 1.2)), 1, "cloth")


def paint_ear(p: Painter) -> None:
	ear = p.ellipse(38.5, 62, 4.6, 8.6)
	p.paint(ear, "skin", sigma=2.2, depth=5, bias=-0.15, shadow=0)


def build(stage: str = "face") -> Image.Image:
	p = Painter(N, S, MATERIALS)
	rng = random.Random(5)
	if stage != "face":
		blob = smooth([(30, 60), (26, 40), (36, 22), (52, 12), (72, 8), (92, 14), (104, 30), (106, 52), (100, 70), (90, 80),
		               (86, 60), (84, 36), (60, 30), (42, 46), (38, 72)], 2)
		p.paint(p.poly(blob), "hair", sigma=6, depth=10, bias=-0.55, shadow=0)
		paint_flows(p, BACK_FLOWS, 11, 0, groove=False)
	if stage == "full":
		paint_body(p, rng)
	neck = p.poly(NECK)
	p.paint(neck, "skin", sigma=5, depth=8, bias=-0.12, shadow=0)
	p.darken(p.poly([(40, 86), (90, 78), (92, 100), (40, 104)]), 0)
	if stage == "full":
		paint_scarf(p)
		paint_ear(p)
	face = p.poly(smooth(FACE, 2))
	p.paint(face, "skin", sigma=13, depth=30, relief=face_relief(p), bias=-0.04, shadow=0)
	_face_planes(p)
	if stage != "face":
		cap = p.poly(smooth(CAP, 2))
		p.paint(cap, "hair", sigma=5, depth=9, bias=-0.1, shadow=2.4)
		paint_flows(p, TOP_FLOWS, 23, 1.2)
		paint_flows(p, FRONT_FLOWS, 37, 2.4)
	if stage == "full":
		for ctrl, widths in ((((45, 51.5), (51, 46.5), (60, 45.5), (65.5, 50)), (3.6, 4.2, 2.6)),
		                     (((70, 49), (75, 45), (83, 45.5), (87.5, 50.5)), (3.4, 3.8, 2.4))):
			p.paint(p.ribbon(ctrl, widths), "hair", sigma=0.9, depth=2.2, bias=-0.18, shadow=0, rim=False)
	keys = cleanup(p.reduce())
	if stage == 'full':
		keys = dither_edges(keys, {p.mat_id['cloth']})
	img = p.to_image(keys)
	return features(img) if stage == 'full' else img


# ---- rasgos pintados a mano, píxel por píxel (plantillas) -----------------------------------
LEGEND = {
	"L": "#150b18", "C": "#5e2d40", "w": "#efe2d6", "s": "#c3aab4", "I": "#2c1816", "R": "#5b3720",
	"g": "#9d6129", "P": "#0d080f", "H": "#fff3df", "k": "#8a4650", "m": "#451a28", "n": "#78393f", "l": "#c0705f",
	"t": "#f7c9a0", "c": "#9a4c52", "h": "#e0907c",
}

NEAR_EYE = [
	"....LLLLLL.....",
	"..LLLLLLLLLLL..",
	".LwwIIIIIIIIwL.",
	"LwwwIRRHRRIwwwL",
	".LwwIRRPPRRIwL.",
	"..LwwIgRRgIwL..",
	"...LLwwIIIwLk..",
	"....kkLLLLkk...",
]
FAR_EYE = [
	"...LLLLLL..",
	".LLLLLLLLL.",
	"LwIIIIIIIwL",
	"LwIRRHRRIwL",
	".LIRPPRgILk",
	"..LIgRRILk.",
	"...LLLLLkk.",
]


def stamp(img: Image.Image, x0: int, y0: int, rows, skip=".") -> None:
	px = img.load()
	for dy, row in enumerate(rows):
		for dx, ch in enumerate(row):
			if ch == skip:
				continue
			c = LEGEND[ch].lstrip("#")
			px[x0 + dx, y0 + dy] = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


NOSTRILS = ["..mmm.", ".mmmm."]
MOUTH = [
	"..nnnn..........",
	".nmmmmmmmmmmnn..",
	"..nclllllllln...",
	"...chhhlllll....",
]


def features(img: Image.Image) -> Image.Image:
	stamp(img, 44, 53, ["LL", ".L"])  # pestañas del ojo cercano
	stamp(img, 47, 51, NEAR_EYE)
	stamp(img, 72, 50, FAR_EYE)
	stamp(img, 64, 73, NOSTRILS)
	stamp(img, 75, 72, ["mmm", ".mm"])
	stamp(img, 62, 79, MOUTH)
	return img

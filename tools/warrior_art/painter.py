"""Motor de pintura de pixel art con volumen: cada forma se "infla" en un mapa de alturas, se ilumina con una
luz cálida arriba-izquierda y se cuantiza a la rampa de color de su material (tela, cuero, metal, piel, pelo).

Se trabaja a `scale`x y se reduce a píxeles reales por moda; luego se limpian píxeles huérfanos y se añade un
contorno de color selectivo (cada material se contornea con su propio tono más oscuro).
"""
import math

import numpy as np
from PIL import Image, ImageDraw

LIGHT = np.array([-0.50, -0.65, 0.58])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = (LIGHT + np.array([0, 0, 1.0])) / np.linalg.norm(LIGHT + np.array([0, 0, 1.0]))


def hexc(s: str):
	s = s.lstrip("#")
	return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gblur(a: np.ndarray, sigma: float) -> np.ndarray:
	if sigma <= 0:
		return a
	ky = np.fft.fftfreq(a.shape[0])[:, None]
	kx = np.fft.fftfreq(a.shape[1])[None, :]
	g = np.exp(-2 * (np.pi ** 2) * (sigma ** 2) * (kx ** 2 + ky ** 2))
	return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def smooth(pts, iterations: int = 2, closed: bool = True):
	"""Chaikin: redondea un polígono dibujado a mano con pocos puntos."""
	pts = list(pts)
	for _ in range(iterations):
		out = []
		n = len(pts)
		rng = range(n) if closed else range(n - 1)
		for i in rng:
			p, q = pts[i], pts[(i + 1) % n]
			out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
			out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
		pts = out
	return pts


def bezier(p0, p1, p2, p3, steps: int = 40):
	pts = []
	for i in range(steps + 1):
		t = i / steps
		u = 1 - t
		pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
		            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
	return pts


class Material:
	def __init__(self, ramp, thresholds, spec=None, spec_pow=24.0, ao=1):
		self.ramp = [hexc(c) for c in ramp]
		self.th = thresholds
		self.spec = spec          # umbral del brillo especular (None = sin brillo)
		self.spec_pow = spec_pow


class Painter:
	def __init__(self, n: int, scale: int, materials: dict):
		self.n, self.s = n, scale
		self.N = n * scale
		self.mats = list(materials.values())
		self.mat_id = {k: i for i, k in enumerate(materials)}
		self.mat = -np.ones((self.N, self.N), dtype=np.int16)
		self.tone = np.zeros((self.N, self.N), dtype=np.int16)

	# ---- máscaras -------------------------------------------------------------------
	def blank(self):
		return Image.new("L", (self.N, self.N), 0)

	def _sc(self, p):
		return (p[0] * self.s, p[1] * self.s)

	def poly(self, pts, mask=None):
		m = mask or self.blank()
		ImageDraw.Draw(m).polygon([self._sc(p) for p in pts], fill=255)
		return m

	def ellipse(self, cx, cy, rx, ry, mask=None):
		m = mask or self.blank()
		s = self.s
		ImageDraw.Draw(m).ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=255)
		return m

	def ribbon(self, ctrl, widths, mask=None, steps: int = 48):
		"""Cinta curva (Bézier cúbica) con ancho variable: widths = (raíz, medio, punta)."""
		m = mask or self.blank()
		pts = bezier(*ctrl, steps=steps)
		left, right = [], []
		for i, p in enumerate(pts):
			a = pts[max(i - 1, 0)]
			b = pts[min(i + 1, len(pts) - 1)]
			dx, dy = b[0] - a[0], b[1] - a[1]
			ln = math.hypot(dx, dy) or 1.0
			nx, ny = -dy / ln, dx / ln
			t = i / steps
			w0, w1, w2 = widths
			w = (w0 * (1 - 2 * t) + w1 * 2 * t) if t < 0.5 else (w1 * (2 - 2 * t) + w2 * (2 * t - 1))
			left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
			right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
		ImageDraw.Draw(m).polygon([self._sc(p) for p in left + right[::-1]], fill=255)
		return m

	def arr(self, mask):
		return np.asarray(mask, dtype=np.float32) / 255.0

	def shift(self, a, dx, dy):
		return np.roll(np.roll(a, int(round(dy * self.s)), axis=0), int(round(dx * self.s)), axis=1)

	# ---- relieve ---------------------------------------------------------------------
	def bump(self, rel, cx, cy, sx, sy, amp, angle=0.0):
		ys, xs = np.mgrid[0:self.N, 0:self.N].astype(np.float32)
		dx, dy = xs / self.s - cx, ys / self.s - cy
		ca, sa = math.cos(angle), math.sin(angle)
		u, v = dx * ca + dy * sa, -dx * sa + dy * ca
		rel += amp * np.exp(-(u * u / (2 * sx * sx) + v * v / (2 * sy * sy)))
		return rel

	def zeros(self):
		return np.zeros((self.N, self.N), dtype=np.float32)

	# ---- pintura ---------------------------------------------------------------------
	def paint(self, mask, mat: str, sigma: float = 3.0, depth: float = 4.0, relief=None, bias: float = 0.0,
	          shadow: float = 1.6, rim: bool = True, tone_cap: int | None = None, under=None):
		"""Pinta `mask` con el material. `depth` = grosor del relieve en px; `sigma` = suavidad del inflado."""
		m = self.arr(mask)
		sel = m > 0.5
		h = gblur(m, sigma * self.s) * depth * self.s
		if relief is not None:
			h = h + relief * self.s
		gy, gx = np.gradient(h)
		nz = np.ones_like(h)
		norm = np.sqrt(gx * gx + gy * gy + nz * nz)
		nxv, nyv, nzv = -gx / norm, -gy / norm, nz / norm
		v = nxv * LIGHT[0] + nyv * LIGHT[1] + nzv * LIGHT[2] + bias
		material = self.mats[self.mat_id[mat]]
		tone = np.digitize(v, material.th)
		if material.spec is not None:
			sp = np.clip(nxv * HALF[0] + nyv * HALF[1] + nzv * HALF[2], 0, 1) ** material.spec_pow
			tone = np.where(sp > material.spec, len(material.ramp) - 1, tone)
		tone = np.clip(tone, 0, len(material.ramp) - 1 if tone_cap is None else tone_cap)
		if shadow:
			moved = self.shift(m, shadow, shadow) > 0.5
			cast = moved & ~sel & (self.mat >= 0)
			self.tone[cast] = np.maximum(self.tone[cast] - 1, 0)
		if rim:
			lit = self.shift(m, 1.0, 1.0) < 0.5
			edge = sel & lit
			tone = np.where(edge & (tone < len(material.ramp) - 2), tone + 1, tone)
		self.mat[sel] = self.mat_id[mat]
		self.tone[sel] = tone[sel]

	def darken(self, region_mask, steps: int = 1, only_mat: str | None = None):
		"""Oscurece lo ya pintado dentro de una región (sombras proyectadas, oclusión)."""
		r = self.arr(region_mask) > 0.5
		r &= self.mat >= 0
		if only_mat:
			r &= self.mat == self.mat_id[only_mat]
		self.tone[r] = np.maximum(self.tone[r] - steps, 0)

	def lighten(self, region_mask, steps: int = 1, only_mat: str | None = None):
		r = self.arr(region_mask) > 0.5
		r &= self.mat >= 0
		if only_mat:
			r &= self.mat == self.mat_id[only_mat]
		for i, mt in enumerate(self.mats):
			sel = r & (self.mat == i)
			self.tone[sel] = np.minimum(self.tone[sel] + steps, len(mt.ramp) - 1)

	# ---- reducción a píxeles ---------------------------------------------------------
	def reduce(self):
		s, n = self.s, self.n
		key = np.where(self.mat >= 0, self.mat * 16 + self.tone, -1).reshape(n, s, n, s).transpose(0, 2, 1, 3).reshape(n, n, s * s)
		opaque = (key >= 0).sum(-1)
		best = np.full((n, n), -1, dtype=np.int32)
		best_cnt = np.zeros((n, n), dtype=np.int32)
		for k in np.unique(key[key >= 0]):
			cnt = (key == k).sum(-1)
			upd = cnt > best_cnt
			best[upd] = k
			best_cnt[upd] = cnt[upd]
		best[opaque * 2 <= s * s] = -1
		return best  # (n, n) con -1 = transparente; si no, mat*16 + tono

	def to_image(self, keys, outline_darken: float = 0.55) -> Image.Image:
		n = self.n
		img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
		px = img.load()
		for y in range(n):
			for x in range(n):
				k = int(keys[y, x])
				if k >= 0:
					px[x, y] = self.mats[k // 16].ramp[k % 16] + (255,)
		# contorno selectivo
		out = img.copy().load()
		for y in range(n):
			for x in range(n):
				if keys[y, x] >= 0:
					continue
				for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
					nx, ny = x + dx, y + dy
					if 0 <= nx < n and 0 <= ny < n and keys[ny, nx] >= 0:
						k = int(keys[ny, nx])
						base = self.mats[k // 16].ramp[0]
						out[x, y] = tuple(int(c * outline_darken) for c in base) + (255,)
						break
		return img


def cleanup(keys: np.ndarray, passes: int = 1) -> np.ndarray:
	"""Elimina píxeles huérfanos (ningún vecino de 4 conectados comparte tono) y rellena agujeros de 1 px."""
	n = keys.shape[0]
	k = keys.copy()
	for _ in range(passes):
		src = k.copy()
		for y in range(1, n - 1):
			for x in range(1, n - 1):
				c = src[y, x]
				nb = [src[y - 1, x], src[y + 1, x], src[y, x - 1], src[y, x + 1]]
				if c not in nb:
					vals, counts = np.unique(nb, return_counts=True)
					j = counts.argmax()
					if counts[j] >= 3:
						k[y, x] = vals[j]
	return k


def dither_edges(keys: np.ndarray, mat_ids, min_tone: int = 1) -> np.ndarray:
	"""Tramado de ajedrez de 1 px en el límite entre dos tonos consecutivos del mismo material.

	Suaviza los planos anchos de piel y tela como lo haría un artista, sin introducir colores nuevos.
	"""
	n = keys.shape[0]
	out = keys.copy()
	for y in range(1, n - 1):
		for x in range(1, n - 1):
			k = keys[y, x]
			if k < 0 or (x + y) % 2:
				continue
			m, t = k // 16, k % 16
			if m not in mat_ids or t < min_tone:
				continue
			for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
				q = keys[y + dy, x + dx]
				if q >= 0 and q // 16 == m and q % 16 == t + 1:
					out[y, x] = q
					break
	return out

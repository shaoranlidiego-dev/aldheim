"""Motor de dibujo: formas a alta resolución -> reducción por moda -> píxeles nítidos con paleta fija.

Las coordenadas se expresan en píxeles finales (flotantes); internamente se dibuja a `scale`x.
Cada pieza se dibuja como máscara y se pinta con luz arriba-izquierda: borde claro arriba-izquierda,
borde oscuro abajo-derecha, más sombras recortadas dentro de la silueta.
"""
from collections import Counter

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from .palette import PALETTE


class Canvas:
	def __init__(self, size: int, scale: int = 8, margin: float = 0):
		self.m = margin  # desplazamiento de las coordenadas de dibujo (margen transparente)
		self.n = size
		self.s = scale
		self.hi = size * scale
		self.img = Image.new("RGBA", (self.hi, self.hi), (0, 0, 0, 0))
		self.draw = ImageDraw.Draw(self.img)

	# ---- máscaras (unen formas con `|`) --------------------------------------------------
	def blank(self) -> Image.Image:
		return Image.new("L", (self.hi, self.hi), 0)

	def _pt(self, p):
		return ((p[0] + self.m) * self.s, (p[1] + self.m) * self.s)

	def poly(self, pts, mask=None) -> Image.Image:
		m = mask or self.blank()
		ImageDraw.Draw(m).polygon([self._pt(p) for p in pts], fill=255)
		return m

	def ellipse(self, cx, cy, rx, ry, mask=None) -> Image.Image:
		m = mask or self.blank()
		s, o = self.s, self.m
		ImageDraw.Draw(m).ellipse([(cx + o - rx) * s, (cy + o - ry) * s, (cx + o + rx) * s, (cy + o + ry) * s], fill=255)
		return m

	def limb(self, pts, width, mask=None) -> Image.Image:
		"""Trazo grueso con extremos redondeados a lo largo de una polilínea."""
		m = mask or self.blank()
		d = ImageDraw.Draw(m)
		s = self.s
		d.line([self._pt(p) for p in pts], fill=255, width=int(width * s))
		r = width * s / 2
		for p in (pts[0], pts[-1]) + tuple(pts[1:-1]):
			x, y = self._pt(p)
			d.ellipse([x - r, y - r, x + r, y + r], fill=255)
		return m

	@staticmethod
	def union(*masks) -> Image.Image:
		out = masks[0]
		for m in masks[1:]:
			out = ImageChops.lighter(out, m)
		return out

	@staticmethod
	def inter(a, b) -> Image.Image:
		return ImageChops.darker(a, b)

	@staticmethod
	def minus(a, b) -> Image.Image:
		return ImageChops.subtract(a, b)

	# ---- pintura -------------------------------------------------------------------------
	def fill(self, mask, color: str) -> None:
		self.img.paste(PALETTE[color] + (255,), (0, 0), mask)

	def shape(self, mask, base: str, light: str | None = None, shade: str | None = None, depth: float = 1.0) -> None:
		"""Pinta la máscara con color base y bordes de luz (arriba-izq.) y sombra (abajo-der.)."""
		self.fill(mask, base)
		d = max(1, int(depth * self.s))
		if light:
			self.fill(ImageChops.subtract(mask, ImageChops.offset(mask, d, d)), light)
		if shade:
			self.fill(ImageChops.subtract(mask, ImageChops.offset(mask, -d, -d)), shade)

	def clip(self, mask, region, color: str) -> None:
		"""Pinta `region` solo dentro de `mask` (sombras y detalles que no se salen de la pieza)."""
		self.fill(ImageChops.darker(mask, region), color)

	# ---- reducción a píxeles --------------------------------------------------------------
	def to_pixels(self) -> Image.Image:
		s, n = self.s, self.n
		arr = np.asarray(self.img).reshape(n, s, n, s, 4).transpose(0, 2, 1, 3, 4).reshape(n, n, s * s, 4)
		out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
		px = out.load()
		for y in range(n):
			for x in range(n):
				block = [tuple(v) for v in arr[y, x]]
				opaque = [v for v in block if v[3] > 0]
				if len(opaque) * 2 < len(block):
					continue
				px[x, y] = Counter(opaque).most_common(1)[0][0]
		return out


def add_outline(img: Image.Image, color: str = "line") -> Image.Image:
	"""Contorno externo de 1 px. Devuelve una imagen del mismo tamaño (deja margen al dibujar)."""
	src = img.copy().load()
	dst = img.copy()
	px = dst.load()
	w, h = img.size
	for y in range(h):
		for x in range(w):
			if src[x, y][3] == 0:
				for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
					nx, ny = x + dx, y + dy
					if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
						px[x, y] = PALETTE[color] + (255,)
						break
	return dst


SPRITE_SIZE = 44    # cuadro jugable: 40 px de dibujo + 2 px de margen transparente por lado
SPRITE_MARGIN = 2

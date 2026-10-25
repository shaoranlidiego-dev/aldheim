"""Pelo castaño desordenado: tres vistas, con mechones, luces cobrizas y sombras."""
from .raster import Canvas


def _strands(c: Canvas, mask, strokes, color: str, width: float = 0.6) -> None:
	"""Trazos finos recortados dentro del pelo (mechones)."""
	m = c.blank()
	for pts in strokes:
		c.limb(tuple(pts), width, m)
	c.clip(mask, m, color)


def shade_hair(c: Canvas, mask, dark_strokes, light_strokes, high_strokes=()) -> None:
	c.shape(mask, "hair", "hair_l", "hair_d", depth=1.0)
	_strands(c, mask, dark_strokes, "hair_d")
	_strands(c, mask, light_strokes, "hair_l", 0.7)
	_strands(c, mask, high_strokes, "hair_h", 0.5)

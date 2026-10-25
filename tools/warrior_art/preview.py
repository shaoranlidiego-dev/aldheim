"""Vista previa ampliada con vecino más cercano (para evaluar píxeles)."""
from PIL import Image


def zoom(img: Image.Image, factor: int, bg=(26, 32, 48)) -> Image.Image:
	base = Image.new("RGBA", img.size, bg + (255,))
	base.alpha_composite(img)
	return base.resize((img.width * factor, img.height * factor), Image.NEAREST)

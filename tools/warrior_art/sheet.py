"""Hoja de sprites jugables: 8 columnas x 4 filas de 44x44 (40 de dibujo + 2 px de margen).

Columnas: 0-1 quieto (respiración), 2-7 caminar (6 cuadros).
Filas (orden RPG Maker): 0 abajo, 1 izquierda, 2 derecha (espejo de izquierda), 3 arriba.
"""
from PIL import Image

from . import sprite_back, sprite_front, sprite_side
from .pose import WALK_FRAMES, idle_pose, walk_pose
from .raster import SPRITE_SIZE, add_outline

FRAME = SPRITE_SIZE
COLUMNS = 2 + WALK_FRAMES
DIRECTIONS = ["down", "left", "right", "up"]


def _frame(direction: str, col: int) -> Image.Image:
	pose = idle_pose(col) if col < 2 else walk_pose(col - 2)
	module = {"down": sprite_front, "up": sprite_back, "left": sprite_side, "right": sprite_side}[direction]
	img = add_outline(module.render(pose))
	return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if direction == "right" else img


def build() -> Image.Image:
	sheet = Image.new("RGBA", (FRAME * COLUMNS, FRAME * len(DIRECTIONS)), (0, 0, 0, 0))
	for row, direction in enumerate(DIRECTIONS):
		for col in range(COLUMNS):
			sheet.paste(_frame(direction, col), (col * FRAME, row * FRAME))
	return sheet

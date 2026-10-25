class_name Board
extends Node2D
## Tablero cuadriculado: dibuja la grilla y convierte entre píxeles y casillas.
## No conoce a las unidades; solo terreno y resaltados.

const TILE_SIZE := 80
const NO_CELL := Vector2i(-1, -1)

const COLOR_LIGHT := Color("3b4252")
const COLOR_DARK := Color("333947")
const COLOR_BLOCKED := Color("14161c")
const COLOR_REACHABLE := Color(0.3, 0.7, 1.0, 0.35)
const COLOR_GRID := Color(1, 1, 1, 0.12)

@export var columns := 8
@export var rows := 12

## Casillas intransitables (Vector2i -> true).
var blocked: Dictionary = {}
## Casillas resaltadas como alcanzables (Vector2i -> true).
var reachable: Dictionary = {}


func _ready() -> void:
	_build_demo_terrain()
	queue_redraw()


func _build_demo_terrain() -> void:
	for cell in [Vector2i(3, 4), Vector2i(4, 4), Vector2i(3, 5), Vector2i(1, 7), Vector2i(6, 7), Vector2i(5, 8)]:
		blocked[cell] = true


func is_inside(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < columns and cell.y < rows


func is_walkable(cell: Vector2i) -> bool:
	return is_inside(cell) and not blocked.has(cell)


## Centro de la casilla en coordenadas locales del tablero.
func cell_to_local(cell: Vector2i) -> Vector2:
	return (Vector2(cell) + Vector2(0.5, 0.5)) * TILE_SIZE


## Casilla bajo una posición local; NO_CELL si queda fuera del tablero.
func local_to_cell(pos: Vector2) -> Vector2i:
	var cell := Vector2i((pos / TILE_SIZE).floor())
	return cell if is_inside(cell) else NO_CELL


func set_reachable(cells: Array) -> void:
	reachable.clear()
	for cell in cells:
		reachable[cell] = true
	queue_redraw()


func clear_reachable() -> void:
	set_reachable([])


func _draw() -> void:
	for y in rows:
		for x in columns:
			var cell := Vector2i(x, y)
			var rect := Rect2(Vector2(cell) * TILE_SIZE, Vector2(TILE_SIZE, TILE_SIZE))
			var color := COLOR_LIGHT if (x + y) % 2 == 0 else COLOR_DARK
			if blocked.has(cell):
				color = COLOR_BLOCKED
			draw_rect(rect, color)
			if reachable.has(cell):
				draw_rect(rect, COLOR_REACHABLE)
	for x in columns + 1:
		draw_line(Vector2(x * TILE_SIZE, 0), Vector2(x * TILE_SIZE, rows * TILE_SIZE), COLOR_GRID)
	for y in rows + 1:
		draw_line(Vector2(0, y * TILE_SIZE), Vector2(columns * TILE_SIZE, y * TILE_SIZE), COLOR_GRID)

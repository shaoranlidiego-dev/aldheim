class_name Unit
extends Node2D
## Ficha sobre el tablero. Por ahora solo sabe su casilla y moverse por ella.

signal move_finished

const STEP_TIME := 0.15

@export var move_range := 4
@export var color := Color("e0b341")

var cell := Vector2i.ZERO
var _board: Board


func place(board: Board, new_cell: Vector2i) -> void:
	_board = board
	cell = new_cell
	position = board.cell_to_local(cell)


## Recorre el camino casilla a casilla y emite `move_finished` al terminar.
func move_along(path: Array[Vector2i]) -> void:
	var tween := create_tween()
	for step in path:
		tween.tween_property(self, "position", _board.cell_to_local(step), STEP_TIME)
	if not path.is_empty():
		cell = path[path.size() - 1]
	await tween.finished
	move_finished.emit()


func _draw() -> void:
	var radius := Board.TILE_SIZE * 0.36
	draw_circle(Vector2.ZERO, radius, color)
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 32, Color.WHITE, 3.0)

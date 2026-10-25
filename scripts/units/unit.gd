class_name Unit
extends Node2D
## Unidad sobre el tablero. La lógica usa solo `cell` (coordenadas de la cuadrícula);
## el sprite es puramente visual y sigue a `position`.

signal move_finished

const STEP_TIME := 0.15

@export var move_range := 4

var cell := Vector2i.ZERO
var facing := Vector2i.DOWN
var _board: Board

@onready var _sprite: AnimatedSprite2D = $Sprite


func place(board: Board, new_cell: Vector2i) -> void:
	_board = board
	cell = new_cell
	position = board.cell_to_local(cell)
	_play("idle")


## Recorre el camino casilla a casilla y emite `move_finished` al terminar.
func move_along(path: Array[Vector2i]) -> void:
	var tween := create_tween()
	var previous := cell
	for step in path:
		tween.tween_callback(_face_and_walk.bind(step - previous))
		tween.tween_property(self, "position", _board.cell_to_local(step), STEP_TIME)
		previous = step
	if not path.is_empty():
		cell = path[path.size() - 1]
	await tween.finished
	_play("idle")
	move_finished.emit()


func _face_and_walk(direction: Vector2i) -> void:
	facing = direction
	_play("walk")


## Reproduce `<estado>_<dirección>` (p. ej. "walk_left") según `facing`.
func _play(state: String) -> void:
	_sprite.play("%s_%s" % [state, _direction_name(facing)])


static func _direction_name(direction: Vector2i) -> String:
	if direction.x < 0:
		return "left"
	if direction.x > 0:
		return "right"
	if direction.y < 0:
		return "up"
	return "down"

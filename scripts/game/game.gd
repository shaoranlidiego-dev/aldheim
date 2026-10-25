extends Node2D
## Controlador principal: interpreta toques/clics y coordina tablero y unidad.
## Flujo: tocar la ficha -> se ven las casillas alcanzables -> tocar una para mover.

const START_CELL := Vector2i(1, 1)

@onready var board: Board = $Board
@onready var player: Unit = $Board/Player
@onready var status_label: Label = $Hud/StatusLabel

var _reachable: Dictionary = {}
var _selected := false
var _moving := false


func _ready() -> void:
	player.place(board, START_CELL)
	_set_status("Toca la ficha para seleccionarla.")


func _unhandled_input(event: InputEvent) -> void:
	# En Android el toque se emula como clic izquierdo (ver project.godot).
	if _moving:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_on_tap(board.local_to_cell(board.to_local(get_global_mouse_position())))


func _on_tap(cell: Vector2i) -> void:
	if cell == player.cell:
		if _selected:
			_deselect()
		else:
			_select()
	elif _selected and _reachable.has(cell):
		_move_player(cell)
	else:
		_deselect()


func _select() -> void:
	_reachable = Pathfinding.explore(board, player.cell, player.move_range)
	var cells: Array = _reachable.keys()
	cells.erase(player.cell)
	board.set_reachable(cells)
	_selected = true
	_set_status("Elegí una casilla azul para moverte.")


func _deselect() -> void:
	_selected = false
	_reachable.clear()
	board.clear_reachable()
	_set_status("Toca la ficha para seleccionarla.")


func _move_player(target: Vector2i) -> void:
	var path := Pathfinding.build_path(_reachable, player.cell, target)
	_moving = true
	_deselect()
	_set_status("Moviendo...")
	player.move_along(path)
	await player.move_finished
	_moving = false
	_set_status("Casilla (%d, %d). Toca la ficha para moverla de nuevo." % [player.cell.x, player.cell.y])


func _set_status(text: String) -> void:
	status_label.text = text

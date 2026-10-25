class_name Pathfinding
extends RefCounted
## Búsqueda en anchura sobre la grilla (4 direcciones). Sin estado.

const DIRECTIONS: Array[Vector2i] = [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]


## Devuelve un diccionario casilla -> casilla previa para todo lo alcanzable
## en hasta `max_steps` pasos. El origen apunta a sí mismo.
static func explore(board: Board, start: Vector2i, max_steps: int) -> Dictionary:
	var came_from: Dictionary = {start: start}
	var frontier: Array[Vector2i] = [start]
	var distance: Dictionary = {start: 0}
	while not frontier.is_empty():
		var current: Vector2i = frontier.pop_front()
		if distance[current] >= max_steps:
			continue
		for dir in DIRECTIONS:
			var next: Vector2i = current + dir
			if came_from.has(next) or not board.is_walkable(next):
				continue
			came_from[next] = current
			distance[next] = distance[current] + 1
			frontier.append(next)
	return came_from


## Camino desde `start` (excluido) hasta `target` (incluido). Vacío si no hay.
static func build_path(came_from: Dictionary, start: Vector2i, target: Vector2i) -> Array[Vector2i]:
	var path: Array[Vector2i] = []
	if not came_from.has(target):
		return path
	var current := target
	while current != start:
		path.push_front(current)
		current = came_from[current]
	return path

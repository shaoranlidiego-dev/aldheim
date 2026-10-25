extends SceneTree
## Genera resources/characters/warrior/warrior_frames.tres (SpriteFrames) desde la hoja de sprites.
## Uso (tras importar el proyecto una vez): godot --headless --script res://tools/build_warrior_frames.gd
## Volver a ejecutarlo cada vez que cambie la hoja warrior_sheet.png o la tabla ANIMATIONS.
##
## Hoja actual: cuadros de 32x32, 4 columnas x 4 filas.
##   Columnas: 0 quieto A, 1 quieto B, 2 paso A, 3 paso B
##   Filas (RPG Maker): 0 abajo, 1 izquierda, 2 derecha, 3 arriba

const SHEET_PATH := "res://assets/characters/warrior/sprites/warrior_sheet.png"
const OUTPUT_PATH := "res://resources/characters/warrior/warrior_frames.tres"
const FRAME_SIZE := Vector2i(32, 32)
const DIRECTIONS: Array[String] = ["down", "left", "right", "up"]  # fila = índice

## Animaciones implementadas: nombre base -> columnas de la hoja, fps y bucle.
## Cada una se crea como "<nombre>_<dirección>" (p. ej. walk_left).
const ANIMATIONS := {
	"idle": {"columns": [0, 1], "fps": 2.0, "loop": true},
	"walk": {"columns": [2, 0, 3, 0], "fps": 8.0, "loop": true},
}
## Previstas, aún sin arte (ver docs/art/warrior.md): attack_1, attack_2, guard, hurt, defeated,
## run, special, celebrate, point, talk. Se agregan aquí cuando existan sus cuadros.


func _init() -> void:
	var sheet: Texture2D = load(SHEET_PATH)
	if sheet == null:
		push_error("No se pudo cargar %s (¿falta importar el proyecto?)" % SHEET_PATH)
		quit(1)
		return
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	for row in DIRECTIONS.size():
		for anim_name in ANIMATIONS:
			var spec: Dictionary = ANIMATIONS[anim_name]
			var anim := "%s_%s" % [anim_name, DIRECTIONS[row]]
			frames.add_animation(anim)
			frames.set_animation_speed(anim, spec["fps"])
			frames.set_animation_loop(anim, spec["loop"])
			for col in spec["columns"]:
				var atlas := AtlasTexture.new()
				atlas.atlas = sheet
				atlas.region = Rect2(Vector2(col, row) * Vector2(FRAME_SIZE), Vector2(FRAME_SIZE))
				frames.add_frame(anim, atlas)
	if ResourceSaver.save(frames, OUTPUT_PATH) != OK:
		push_error("No se pudo guardar %s" % OUTPUT_PATH)
		quit(1)
		return
	print("Guardado ", OUTPUT_PATH, " con ", frames.get_animation_names().size(), " animaciones")
	quit()

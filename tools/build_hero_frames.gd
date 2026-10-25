extends SceneTree
## Genera resources/characters/hero_frames.tres (SpriteFrames) a partir de la hoja de sprites.
## Uso: godot --headless --script res://tools/build_hero_frames.gd
## Se ejecuta de nuevo cada vez que se reemplaza assets/characters/hero_sheet.png.
##
## Diseño de la hoja: cuadros de FRAME_SIZE, 3 columnas (paso A, quieto, paso B)
## y 4 filas en el orden de DIRECTIONS.

const SHEET_PATH := "res://assets/characters/hero_sheet.png"
const OUTPUT_PATH := "res://resources/characters/hero_frames.tres"
const FRAME_SIZE := Vector2i(16, 16)
const DIRECTIONS: Array[String] = ["down", "left", "right", "up"]
const WALK_FPS := 8.0
## Orden de columnas usado al caminar: A, quieto, B, quieto.
const WALK_COLUMNS: Array[int] = [0, 1, 2, 1]
const IDLE_COLUMN := 1


func _init() -> void:
	var sheet: Texture2D = load(SHEET_PATH)
	if sheet == null:
		push_error("No se pudo cargar %s (¿falta importar el proyecto?)" % SHEET_PATH)
		quit(1)
		return
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	for row in DIRECTIONS.size():
		var dir := DIRECTIONS[row]
		_add_animation(frames, "idle_" + dir, sheet, row, [IDLE_COLUMN], 1.0)
		_add_animation(frames, "walk_" + dir, sheet, row, WALK_COLUMNS, WALK_FPS)
	var err := ResourceSaver.save(frames, OUTPUT_PATH)
	if err != OK:
		push_error("No se pudo guardar %s (error %d)" % [OUTPUT_PATH, err])
		quit(1)
		return
	print("Guardado ", OUTPUT_PATH, " con ", frames.get_animation_names().size(), " animaciones")
	quit()


func _add_animation(frames: SpriteFrames, anim: String, sheet: Texture2D, row: int, columns: Array[int], fps: float) -> void:
	frames.add_animation(anim)
	frames.set_animation_speed(anim, fps)
	frames.set_animation_loop(anim, true)
	for col in columns:
		var atlas := AtlasTexture.new()
		atlas.atlas = sheet
		atlas.region = Rect2(Vector2(col, row) * Vector2(FRAME_SIZE), Vector2(FRAME_SIZE))
		frames.add_frame(anim, atlas)

extends Node
## Estado global da partida, transições de cena com fade e utilitários de game feel.
## Autoload "Game".

signal hp_changed(hp: int, max_hp: int)

const SCENE_TITLE := "res://scenes/ui/title.tscn"
const SCENE_INTRO := "res://scenes/ui/intro.tscn"
const SCENE_ATO1 := "res://scenes/levels/ato1_sao_miguel.tscn"
const MAX_HP := 3

var hp: int = MAX_HP
var checkpoint := Vector2.ZERO
var has_checkpoint := false
var deaths := 0
var screenshot_dir := ""

var _layer: CanvasLayer
var _fade: ColorRect
var _transitioning := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_layer = CanvasLayer.new()
	_layer.layer = 100
	add_child(_layer)
	_fade = ColorRect.new()
	_fade.color = Color(0.04, 0.03, 0.08, 1.0)
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.modulate.a = 0.0
	_layer.add_child(_fade)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--shots="):
			screenshot_dir = arg.trim_prefix("--shots=")
	if screenshot_dir != "":
		_run_screenshots.call_deferred()


func reset_run() -> void:
	hp = MAX_HP
	has_checkpoint = false
	checkpoint = Vector2.ZERO
	deaths = 0
	hp_changed.emit(hp, MAX_HP)


func change_scene(path: String, fade_out := 0.5, fade_in := 0.7) -> void:
	if _transitioning:
		return
	_transitioning = true
	await fade_to_black(fade_out)
	get_tree().paused = false
	get_tree().change_scene_to_file(path)
	await get_tree().process_frame
	await get_tree().process_frame
	await fade_from_black(fade_in)
	_transitioning = false


func fade_to_black(duration: float) -> void:
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 1.0, duration)
	await tw.finished


func fade_from_black(duration: float) -> void:
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 0.0, duration)
	await tw.finished


func damage(amount: int) -> bool:
	hp = maxi(0, hp - amount)
	hp_changed.emit(hp, MAX_HP)
	return hp == 0


func heal(amount: int) -> void:
	hp = mini(MAX_HP, hp + amount)
	hp_changed.emit(hp, MAX_HP)


func hit_stop(duration := 0.06, time_scale := 0.05) -> void:
	if Engine.time_scale < 1.0:
		return
	Engine.time_scale = time_scale
	await get_tree().create_timer(duration, true, false, true).timeout
	Engine.time_scale = 1.0


func shake(amount: float) -> void:
	get_tree().call_group("camera", "shake", amount)


func toggle_fullscreen() -> void:
	var mode := DisplayServer.window_get_mode()
	if mode == DisplayServer.WINDOW_MODE_FULLSCREEN or mode == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("fullscreen"):
		toggle_fullscreen()


## Modo de captura (godot --path . -- --shots=/pasta): tira prints do título e da fase e sai.
func _run_screenshots() -> void:
	await get_tree().create_timer(1.2).timeout
	_snap("01_titulo")
	get_tree().change_scene_to_file(SCENE_ATO1)
	await get_tree().create_timer(1.6).timeout
	_snap("02_fase_cartao")
	Input.action_press("move_right")
	await get_tree().create_timer(1.1).timeout
	Input.action_release("move_right")
	Input.action_press("attack")
	await get_tree().create_timer(0.12).timeout
	Input.action_release("attack")
	await get_tree().create_timer(1.6).timeout
	_snap("03_fase_jogo")
	Input.action_press("move_right")
	Input.action_press("jump")
	await get_tree().create_timer(0.25).timeout
	Input.action_release("jump")
	await get_tree().create_timer(0.9).timeout
	Input.action_release("move_right")
	await get_tree().create_timer(0.3).timeout
	_snap("04_fase_pulo")
	get_tree().quit()


func _snap(name: String) -> void:
	var img := get_viewport().get_texture().get_image()
	var err := img.save_png(screenshot_dir.path_join(name + ".png"))
	print("screenshot ", name, " -> ", err)

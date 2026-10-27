extends CanvasLayer
## Menu de pausa (Esc). Enter volta ao jogo, Q volta ao título.


func _ready() -> void:
	visible = false
	process_mode = Node.PROCESS_MODE_ALWAYS


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause"):
		_set_paused(not get_tree().paused)
		get_viewport().set_input_as_handled()
	elif get_tree().paused:
		if event.is_action_pressed("ui_accept") or event.is_action_pressed("jump"):
			_set_paused(false)
		elif event is InputEventKey and event.pressed and (event as InputEventKey).keycode == KEY_Q:
			_set_paused(false)
			Game.change_scene(Game.SCENE_TITLE)


func _set_paused(p: bool) -> void:
	get_tree().paused = p
	visible = p
	Audio.play_sfx("ui_mover", -6.0)

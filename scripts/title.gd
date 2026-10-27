extends Node2D
## Tela de título: menu, cursor de lança e brilho pulsante no nome do jogo.

var _idx := 0
var _items: Array[Label] = []

@onready var cursor: Sprite2D = $UI/Cursor
@onready var titulo: Label = $UI/Titulo


func _ready() -> void:
	Game.reset_run()
	_items = [$UI/Menu/Iniciar, $UI/Menu/Sair]
	Audio.play_music("tema", 2.5)
	Audio.play_ambience("vento", -18.0)
	$Backdrop.set_autoscroll(true)
	$Backdrop/Capim/Sprite.position.y = 252.0
	var tw := create_tween().set_loops()
	tw.tween_property(titulo, "modulate", Color(1.45, 1.38, 1.2), 1.8).set_trans(Tween.TRANS_SINE)
	tw.tween_property(titulo, "modulate", Color(1.0, 1.0, 1.0), 1.8).set_trans(Tween.TRANS_SINE)
	var blink := create_tween().set_loops()
	blink.tween_property(cursor, "modulate:a", 0.25, 0.45)
	blink.tween_property(cursor, "modulate:a", 1.0, 0.45)


func _process(_delta: float) -> void:
	_update_cursor()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_down") or event.is_action_pressed("ui_up"):
		_idx = (_idx + 1) % _items.size()
		Audio.play_sfx("ui_mover", -8.0)
		_update_cursor()
	elif event.is_action_pressed("ui_accept") or event.is_action_pressed("jump") or event.is_action_pressed("attack"):
		Audio.play_sfx("ui_confirmar", -6.0)
		if _idx == 0:
			Game.change_scene(Game.SCENE_INTRO, 0.8, 0.8)
		else:
			get_tree().quit()


func _update_cursor() -> void:
	var l := _items[_idx]
	cursor.global_position = l.global_position + Vector2(-22.0, l.size.y / 2.0)

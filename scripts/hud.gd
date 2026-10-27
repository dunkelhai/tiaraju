extends CanvasLayer
## HUD: corações, mensagens curtas e cartão de título do ato.

const HEART_FULL := preload("res://assets/ui/coracao_cheio.png")
const HEART_EMPTY := preload("res://assets/ui/coracao_vazio.png")

@onready var hearts: HBoxContainer = $Hearts
@onready var message: Label = $Message
@onready var card: VBoxContainer = $Card

var _msg_tween: Tween


func _ready() -> void:
	Game.hp_changed.connect(_on_hp_changed)
	_on_hp_changed(Game.hp, Game.MAX_HP)
	message.modulate.a = 0.0
	card.modulate.a = 0.0


func _on_hp_changed(hp: int, _max_hp: int) -> void:
	for i in hearts.get_child_count():
		var h := hearts.get_child(i) as TextureRect
		h.texture = HEART_FULL if i < hp else HEART_EMPTY


func show_message(text: String, hold := 2.2) -> void:
	message.text = text
	if _msg_tween:
		_msg_tween.kill()
	_msg_tween = create_tween()
	_msg_tween.tween_property(message, "modulate:a", 1.0, 0.3)
	_msg_tween.tween_interval(hold)
	_msg_tween.tween_property(message, "modulate:a", 0.0, 0.7)


func show_card(title: String, subtitle: String, hold := 2.6) -> void:
	$Card/Title.text = title
	$Card/Subtitle.text = subtitle
	var tw := create_tween()
	tw.tween_property(card, "modulate:a", 1.0, 1.0)
	tw.tween_interval(hold)
	tw.tween_property(card, "modulate:a", 0.0, 1.2)

extends Control
## Introdução narrativa: páginas com efeito de máquina de escrever sobre o lamento.

const PAGES := [
	"1750.\nPortugal e Espanha assinam o Tratado de Madri.",
	"Os Sete Povos das Missões — São Miguel, São Borja, São Nicolau, São Luiz Gonzaga, São Lourenço, São João Batista e Santo Ângelo — passam à Coroa portuguesa.",
	"Trinta mil guaranis recebem a ordem de abandonar suas casas, suas lavouras e seus mortos.",
	"Sepé Tiaraju, corregedor de São Miguel, responde aos exércitos que chegam:",
	"\"Esta terra tem dono.\"\n\nKo'ã yvy oguereko ijára.",
	"São Miguel Arcanjo, 1756.",
]
const CHARS_PER_SEC := 30.0
const AUTO_ADVANCE := 3.2

var _page := -1
var _typing := false
var _chars := 0.0
var _wait := 0.0
var _busy := false
var _finishing := false

@onready var label: Label = $Texto


func _ready() -> void:
	Audio.play_music("lamento", 2.0)
	label.modulate.a = 1.0
	_next()


func _process(delta: float) -> void:
	if _typing:
		_chars += delta * CHARS_PER_SEC
		var n := int(_chars)
		if n != label.visible_characters:
			label.visible_characters = n
			if n % 3 == 0:
				Audio.play_sfx("tecla", -22.0, 0.3)
		if n >= label.text.length():
			_typing = false
			label.visible_characters = -1
			_wait = AUTO_ADVANCE
	elif not _busy:
		_wait -= delta
		if _wait <= 0.0:
			_advance()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_finish()
	elif event.is_action_pressed("ui_accept") or event.is_action_pressed("jump") or event.is_action_pressed("attack"):
		if _typing:
			_typing = false
			label.visible_characters = -1
			_wait = AUTO_ADVANCE
		elif not _busy:
			_advance()


func _next() -> void:
	_page += 1
	if _page >= PAGES.size():
		_finish()
		return
	label.text = PAGES[_page]
	label.visible_characters = 0
	_chars = 0.0
	_typing = true


func _advance() -> void:
	_busy = true
	var tw := create_tween()
	tw.tween_property(label, "modulate:a", 0.0, 0.5)
	await tw.finished
	_next()
	var tw2 := create_tween()
	tw2.tween_property(label, "modulate:a", 1.0, 0.4)
	await tw2.finished
	_busy = false


func _finish() -> void:
	if _finishing:
		return
	_finishing = true
	_busy = true
	set_process(false)
	Game.change_scene(Game.SCENE_ATO1, 1.2, 1.4)

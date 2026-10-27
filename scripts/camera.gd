extends Camera2D
class_name GameCamera
## Câmera com suavização manual, antecipação na direção do olhar e tremor.

var target: Node2D
var lookahead := 26.0

var _look := 0.0
var _shake := 0.0
var _pos := Vector2.ZERO


func _ready() -> void:
	add_to_group("camera")
	position_smoothing_enabled = false
	process_callback = Camera2D.CAMERA2D_PROCESS_PHYSICS


func snap_to(p: Vector2) -> void:
	_pos = p
	global_position = p.round()
	reset_smoothing()


func _physics_process(delta: float) -> void:
	if target == null or not is_instance_valid(target):
		return
	var want_look := 0.0
	if target is Player:
		want_look = (target as Player).facing * lookahead
	_look = lerpf(_look, want_look, 1.0 - exp(-delta * 3.0))
	var goal := target.global_position + Vector2(_look, -28.0)
	_pos.x = lerpf(_pos.x, goal.x, 1.0 - exp(-delta * 7.0))
	_pos.y = lerpf(_pos.y, goal.y, 1.0 - exp(-delta * 5.0))
	var off := Vector2.ZERO
	if _shake > 0.0:
		_shake = maxf(0.0, _shake - delta * 16.0)
		off = Vector2(randf_range(-_shake, _shake), randf_range(-_shake, _shake))
	global_position = (_pos + off).round()


func shake(amount: float) -> void:
	_shake = maxf(_shake, amount)

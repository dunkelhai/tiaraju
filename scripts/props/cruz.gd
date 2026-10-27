extends Area2D
## Cruz missioneira: checkpoint. Acende em dourado quando Sepé passa.

var active := false

@onready var sprite: Sprite2D = $Sprite
@onready var light: PointLight2D = $Light


func _ready() -> void:
	area_entered.connect(_on_area_entered)
	light.energy = 0.0


func _on_area_entered(area: Area2D) -> void:
	if active or not (area.get_parent() is Player):
		return
	active = true
	sprite.frame = 1
	sprite.modulate = Color(1.4, 1.3, 1.0)
	Audio.play_sfx("cruz", -4.0)
	create_tween().tween_property(light, "energy", 0.9, 0.8)
	var level := get_tree().current_scene
	if level.has_method("checkpoint_reached"):
		level.checkpoint_reached(global_position)

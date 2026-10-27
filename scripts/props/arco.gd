extends Area2D
## Arco de arenito: meta da fase.


func _ready() -> void:
	area_entered.connect(_on_area_entered)


func _on_area_entered(area: Area2D) -> void:
	if not (area.get_parent() is Player):
		return
	var level := get_tree().current_scene
	if level.has_method("finish"):
		level.finish()

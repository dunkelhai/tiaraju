extends Area2D
## Cuia de chimarrão: recupera um coração.

@onready var sprite: Sprite2D = $Sprite


func _ready() -> void:
	area_entered.connect(_on_area_entered)
	var tw := create_tween().set_loops().set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(sprite, "position:y", -3.0, 0.9)
	tw.tween_property(sprite, "position:y", 0.0, 0.9)


func _on_area_entered(area: Area2D) -> void:
	if not (area.get_parent() is Player):
		return
	set_deferred("monitoring", false)
	Game.heal(1)
	Audio.play_sfx("coleta", -6.0)
	$Particles.restart()
	sprite.visible = false
	await get_tree().create_timer(0.6).timeout
	queue_free()

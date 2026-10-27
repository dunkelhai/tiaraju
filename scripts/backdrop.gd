extends Node2D
## Cenário em parallax: céu com lua, coxilhas, ruínas de São Miguel e capim em primeiro plano.


func set_autoscroll(on: bool) -> void:
	$Coxilhas.autoscroll = Vector2(-3.0, 0.0) if on else Vector2.ZERO
	$Ruinas.autoscroll = Vector2(-9.0, 0.0) if on else Vector2.ZERO
	$Capim.autoscroll = Vector2(-28.0, 0.0) if on else Vector2.ZERO

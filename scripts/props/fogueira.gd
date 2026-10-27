extends Node2D
## Fogueira: chamas animadas, luz tremulante e brasas.

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var light: PointLight2D = $Light

var _t := 0.0
var _seed := 0.0


func _ready() -> void:
	sprite.sprite_frames = SpriteSheets.strip(preload("res://assets/sprites/fogueira.png"), 16, 16, 8.0)
	sprite.play("default")
	sprite.modulate = Color(1.5, 1.25, 1.0)
	_seed = randf() * 100.0


func _process(delta: float) -> void:
	_t += delta
	light.energy = 1.15 + 0.18 * sin(_t * 9.0 + _seed) + 0.1 * sin(_t * 23.0 + _seed * 2.0)
	light.texture_scale = 1.7 + 0.08 * sin(_t * 7.0 + _seed)

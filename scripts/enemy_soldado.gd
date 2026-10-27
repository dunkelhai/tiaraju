extends CharacterBody2D
class_name Soldado
## Soldado luso-espanhol: patrulha, percebe Sepé e dá um bote de baioneta.

const WALK := 34.0
const LUNGE_SPEED := 155.0
const GRAVITY := 1100.0
const DETECT_X := 96.0
const DETECT_Y := 30.0
const MAX_HP := 2

enum State { PATROL, ALERT, LUNGE, RECOVER, HURT, DEAD }

var state := State.PATROL
var hp := MAX_HP
var dir := -1
var _timer := 0.0
var _player: Node2D

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var floor_ray: RayCast2D = $FloorRay
@onready var wall_ray: RayCast2D = $WallRay
@onready var hurtbox: Area2D = $Hurtbox
@onready var body_damage: Area2D = $BodyDamage
@onready var bayonet: Area2D = $Bayonet
@onready var particles: CPUParticles2D = $Particles
@onready var flash_mat: ShaderMaterial = sprite.material


func _ready() -> void:
	add_to_group("enemy")
	sprite.sprite_frames = SpriteSheets.build(preload("res://assets/sprites/soldado.png"), SpriteSheets.SOLDADO)
	sprite.material = sprite.material.duplicate()
	flash_mat = sprite.material
	sprite.play("walk")
	bayonet.monitorable = false
	dir = -1 if randf() < 0.5 else 1
	_apply_facing()


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y = minf(velocity.y + GRAVITY * delta, 420.0)
	if _player == null:
		_player = get_tree().get_first_node_in_group("player")
	match state:
		State.PATROL:
			velocity.x = dir * WALK
			if is_on_floor() and (not _floor_ahead() or wall_ray.is_colliding()):
				dir = -dir
				_apply_facing()
				velocity.x = dir * WALK
			if _sees_player():
				state = State.ALERT
				_timer = 0.4
				dir = 1 if _player.global_position.x > global_position.x else -1
				_apply_facing()
				sprite.play("alert")
		State.ALERT:
			velocity.x = move_toward(velocity.x, 0.0, 500.0 * delta)
			_timer -= delta
			if _timer <= 0.0:
				state = State.LUNGE
				_timer = 0.36
				bayonet.set_deferred("monitorable", true)
				sprite.play("lunge")
				Audio.play_sfx("ataque", -14.0)
		State.LUNGE:
			velocity.x = dir * LUNGE_SPEED
			_timer -= delta
			if is_on_wall() or (is_on_floor() and not _floor_ahead()):
				_timer = 0.0
			if _timer <= 0.0:
				state = State.RECOVER
				_timer = 0.9
				bayonet.set_deferred("monitorable", false)
				sprite.play("idle")
		State.RECOVER:
			velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
			_timer -= delta
			if _timer <= 0.0:
				state = State.PATROL
				sprite.play("walk")
		State.HURT:
			velocity.x = move_toward(velocity.x, 0.0, 500.0 * delta)
			_timer -= delta
			if _timer <= 0.0:
				state = State.PATROL
				sprite.play("walk")
		State.DEAD:
			velocity.x = move_toward(velocity.x, 0.0, 250.0 * delta)
	move_and_slide()


func _apply_facing() -> void:
	sprite.flip_h = dir < 0
	floor_ray.position.x = 10 * dir
	wall_ray.target_position.x = 12 * dir
	bayonet.position.x = 17 * dir
	floor_ray.force_raycast_update()
	wall_ray.force_raycast_update()


func _floor_ahead() -> bool:
	floor_ray.force_raycast_update()
	return floor_ray.is_colliding()


func _sees_player() -> bool:
	if _player == null or not is_instance_valid(_player):
		return false
	if _player.get("state") == Player.State.DEAD:
		return false
	var d := _player.global_position - global_position
	return absf(d.x) < DETECT_X and absf(d.y) < DETECT_Y


func take_hit(from_dir: int) -> void:
	if state == State.DEAD:
		return
	hp -= 1
	velocity = Vector2(from_dir * 130.0, -100.0)
	flash_mat.set_shader_parameter("flash", 1.0)
	var tw := create_tween()
	tw.tween_method(func(v: float) -> void: flash_mat.set_shader_parameter("flash", v), 1.0, 0.0, 0.25)
	bayonet.set_deferred("monitorable", false)
	if hp <= 0:
		_die(from_dir)
	else:
		state = State.HURT
		_timer = 0.4
		sprite.play("hurt")


func _die(from_dir: int) -> void:
	state = State.DEAD
	hp = 0
	hurtbox.set_deferred("monitorable", false)
	body_damage.set_deferred("monitorable", false)
	velocity = Vector2(from_dir * 100.0, -170.0)
	particles.restart()
	Audio.play_sfx("inimigo_morre", -6.0)
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", from_dir * 1.3, 0.5).set_trans(Tween.TRANS_SINE)
	tw.parallel().tween_property(sprite, "modulate:a", 0.0, 0.7).set_delay(0.5)
	tw.tween_callback(queue_free)

extends CharacterBody2D
class_name Player
## Sepé Tiaraju: corre, pula e estoca com a lança.
## Game feel: coyote time, jump buffer, pulo variável, squash & stretch, hit-stop e tremor de câmera.

signal died

const SPEED := 112.0
const ACCEL := 1100.0
const FRICTION := 1400.0
const AIR_ACCEL := 700.0
const JUMP_VELOCITY := -310.0
const GRAVITY := 900.0
const FALL_GRAVITY := 1200.0
const MAX_FALL := 340.0
const COYOTE := 0.10
const JUMP_BUFFER := 0.12
const ATTACK_TIME := 0.27
const ATTACK_COOLDOWN := 0.1
const HURT_TIME := 0.3
const INVULN_TIME := 1.1

enum State { NORMAL, ATTACK, HURT, DEAD }

var state := State.NORMAL
var facing := 1
var controls_enabled := true

var _coyote := 0.0
var _buffer := 0.0
var _attack_t := 0.0
var _cooldown := 0.0
var _hurt_t := 0.0
var _invuln := 0.0
var _was_on_floor := false
var _hit_this_swing: Array[Node] = []

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var attack_box: Area2D = $AttackBox
@onready var hurtbox: Area2D = $Hurtbox
@onready var dust: CPUParticles2D = $Dust


func _ready() -> void:
	add_to_group("player")
	sprite.sprite_frames = SpriteSheets.build(preload("res://assets/sprites/sepe.png"), SpriteSheets.SEPE)
	sprite.play("idle")
	sprite.frame_changed.connect(_on_frame_changed)
	attack_box.monitoring = false


func _physics_process(delta: float) -> void:
	var on_floor := is_on_floor()
	if not on_floor:
		var g := GRAVITY if velocity.y < 0.0 else FALL_GRAVITY
		velocity.y = minf(velocity.y + g * delta, MAX_FALL)
	if state == State.DEAD:
		velocity.x = move_toward(velocity.x, 0.0, 200.0 * delta)
		move_and_slide()
		return

	_coyote = COYOTE if on_floor else maxf(0.0, _coyote - delta)
	_buffer = maxf(0.0, _buffer - delta)
	_cooldown = maxf(0.0, _cooldown - delta)
	if _invuln > 0.0:
		_invuln -= delta
		sprite.visible = _invuln <= 0.0 or int(_invuln * 20.0) % 2 == 0

	var dir := 0.0
	if controls_enabled and state != State.HURT:
		dir = Input.get_axis("move_left", "move_right")
		if Input.is_action_just_pressed("jump"):
			_buffer = JUMP_BUFFER
		if Input.is_action_just_pressed("attack") and _cooldown <= 0.0 and state == State.NORMAL:
			_start_attack()

	if state == State.HURT:
		_hurt_t -= delta
		velocity.x = move_toward(velocity.x, 0.0, FRICTION * 0.4 * delta)
		if _hurt_t <= 0.0:
			state = State.NORMAL
	else:
		var target := dir * SPEED
		if state == State.ATTACK and on_floor:
			target = facing * 22.0
		var accel: float
		if dir != 0.0:
			accel = ACCEL if on_floor else AIR_ACCEL
		else:
			accel = FRICTION if on_floor else AIR_ACCEL * 0.5
		velocity.x = move_toward(velocity.x, target, accel * delta)
		if dir != 0.0 and state == State.NORMAL:
			facing = 1 if dir > 0.0 else -1

	if state == State.NORMAL and _buffer > 0.0 and _coyote > 0.0:
		_buffer = 0.0
		_coyote = 0.0
		velocity.y = JUMP_VELOCITY
		_squash(Vector2(0.78, 1.25))
		dust.restart()
		Audio.play_sfx("pulo", -8.0)
	if controls_enabled and Input.is_action_just_released("jump") and velocity.y < -80.0:
		velocity.y *= 0.45

	if state == State.ATTACK:
		_attack_t -= delta
		if attack_box.monitoring:
			_check_attack_hits()
		if _attack_t <= 0.0:
			_end_attack()

	var fall_speed := velocity.y
	move_and_slide()
	var now_floor := is_on_floor()
	if now_floor and not _was_on_floor and fall_speed > 140.0:
		_squash(Vector2(1.3, 0.72))
		dust.restart()
		Audio.play_sfx("aterrissar", -12.0)
	_was_on_floor = now_floor
	if state != State.HURT and _invuln <= 0.0:
		_check_damage()
	_update_animation(now_floor, dir)


func _update_animation(on_floor: bool, dir: float) -> void:
	sprite.flip_h = facing < 0
	attack_box.scale.x = facing
	match state:
		State.ATTACK:
			_play("attack")
		State.HURT:
			_play("hurt")
		_:
			if not on_floor:
				_play("jump" if velocity.y < 0.0 else "fall")
			elif absf(velocity.x) > 12.0 and dir != 0.0:
				_play("run")
			else:
				_play("idle")


func _play(anim: String) -> void:
	if sprite.animation != anim:
		sprite.play(anim)


func _on_frame_changed() -> void:
	if sprite.animation == "attack":
		attack_box.monitoring = sprite.frame >= 1
	elif sprite.animation == "run" and (sprite.frame == 1 or sprite.frame == 4) and is_on_floor():
		Audio.play_sfx("passo", -20.0, 0.25)


func _start_attack() -> void:
	state = State.ATTACK
	_attack_t = ATTACK_TIME
	_cooldown = ATTACK_TIME + ATTACK_COOLDOWN
	_hit_this_swing.clear()
	sprite.play("attack")
	Audio.play_sfx("ataque", -10.0)


func _end_attack() -> void:
	if state == State.ATTACK:
		state = State.NORMAL
	attack_box.monitoring = false


func _check_attack_hits() -> void:
	for area in attack_box.get_overlapping_areas():
		var enemy := area.get_parent()
		if enemy in _hit_this_swing or not enemy.has_method("take_hit"):
			continue
		_hit_this_swing.append(enemy)
		enemy.take_hit(facing)
		velocity.x -= facing * 35.0
		Audio.play_sfx("golpe", -4.0)
		Game.shake(2.5)
		Game.hit_stop(0.05)


func _check_damage() -> void:
	for area in hurtbox.get_overlapping_areas():
		if area.is_in_group("enemy_damage"):
			take_damage(area.global_position)
			return


func take_damage(from: Vector2) -> void:
	if _invuln > 0.0 or state == State.DEAD:
		return
	var away := signf(global_position.x - from.x)
	if away == 0.0:
		away = -facing
	attack_box.monitoring = false
	var dead := Game.damage(1)
	velocity = Vector2(away * 150.0, -180.0)
	Game.shake(4.0)
	Game.hit_stop(0.08)
	if dead:
		die()
	else:
		state = State.HURT
		_hurt_t = HURT_TIME
		_invuln = INVULN_TIME
		Audio.play_sfx("dano", -4.0)


func die() -> void:
	if state == State.DEAD:
		return
	state = State.DEAD
	sprite.visible = true
	sprite.play("hurt")
	attack_box.monitoring = false
	velocity = Vector2(-facing * 70.0, -230.0)
	Audio.play_sfx("morte", -2.0)
	Game.shake(6.0)
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", -facing * 1.45, 0.5).set_trans(Tween.TRANS_SINE)
	died.emit()


func _squash(s: Vector2) -> void:
	sprite.scale = s
	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw.tween_property(sprite, "scale", Vector2.ONE, 0.22)

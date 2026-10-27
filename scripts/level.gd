extends Node2D
## Monta a fase a partir do mapa ASCII (scripts/levels/*.gd), cuida de checkpoint, morte, meta e cartão de título.

const TILE := 16
const TILESET_TEX := preload("res://assets/tiles/tileset.png")
const SepeScene := preload("res://scenes/player/sepe.tscn")
const SoldadoScene := preload("res://scenes/enemies/soldado.tscn")
const CruzScene := preload("res://scenes/props/cruz.tscn")
const FogueiraScene := preload("res://scenes/props/fogueira.tscn")
const ErvaScene := preload("res://scenes/props/erva.tscn")
const ArcoScene := preload("res://scenes/props/arco.tscn")

## Coordenadas no atlas (ver assets/tiles/tileset.txt, gerado por tools/gen_tiles.py).
const T := {
	"grass_a": Vector2i(0, 0), "grass_b": Vector2i(1, 0), "grass_c": Vector2i(2, 0),
	"grass_l": Vector2i(3, 0), "grass_r": Vector2i(4, 0),
	"dirt_a": Vector2i(5, 0), "dirt_b": Vector2i(6, 0), "dirt_l": Vector2i(7, 0), "dirt_r": Vector2i(8, 0),
	"stone_top": Vector2i(0, 1), "stone_a": Vector2i(1, 1), "stone_b": Vector2i(2, 1),
	"stone_l": Vector2i(3, 1), "stone_r": Vector2i(4, 1), "stone_tl": Vector2i(5, 1), "stone_tr": Vector2i(6, 1),
	"stone_single": Vector2i(7, 1), "stone_bottom": Vector2i(8, 1),
	"deco_grass_a": Vector2i(0, 2), "deco_grass_b": Vector2i(1, 2), "deco_flowers": Vector2i(2, 2),
	"deco_rock": Vector2i(3, 2), "deco_shards": Vector2i(4, 2), "deco_rubble": Vector2i(5, 2), "deco_bush": Vector2i(6, 2),
	"ledge_l": Vector2i(0, 3), "ledge_m": Vector2i(1, 3), "ledge_r": Vector2i(2, 3),
	"stone_bl": Vector2i(3, 3), "stone_br": Vector2i(4, 3),
}
const DECOS := ["deco_grass_a", "deco_grass_b", "deco_grass_a", "deco_flowers", "deco_rock", "deco_shards", "deco_rubble", "deco_bush"]

@export var map_script: GDScript
@export var act_title := "Ato I"
@export var act_subtitle := "São Miguel Arcanjo, 1756"

var player: Player
var map: PackedStringArray
var width := 0
var height := 0

var _finished := false
var _rng := RandomNumberGenerator.new()

@onready var ground: TileMapLayer = $Ground
@onready var deco: TileMapLayer = $Deco
@onready var solids: StaticBody2D = $Solids
@onready var ledges: StaticBody2D = $Ledges
@onready var entities: Node2D = $Entities
@onready var camera: GameCamera = $Camera
@onready var hud: CanvasLayer = $HUD


func _ready() -> void:
	_rng.seed = 1756
	var ts := _build_tileset()
	ground.tile_set = ts
	deco.tile_set = ts
	_build()
	Audio.play_music("tema", 2.0)
	Audio.play_ambience("vento", -16.0)
	if not Game.has_checkpoint:
		hud.show_card(act_title, act_subtitle)


func _process(_delta: float) -> void:
	if player and player.state != Player.State.DEAD and player.global_position.y > (height + 2) * TILE:
		player.die()


# ------------------------------------------------------------------ construção
func _build_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)
	var src := TileSetAtlasSource.new()
	src.texture = TILESET_TEX
	src.texture_region_size = Vector2i(TILE, TILE)
	var cols := int(TILESET_TEX.get_width() / float(TILE))
	var rows := int(TILESET_TEX.get_height() / float(TILE))
	for y in rows:
		for x in cols:
			src.create_tile(Vector2i(x, y))
	ts.add_source(src, 0)
	return ts


func _build() -> void:
	map = map_script.get_script_constant_map()["ROWS"]
	height = map.size()
	for r in map:
		width = maxi(width, r.length())
	for y in height:
		for x in width:
			var ch := _at(x, y)
			match ch:
				"#":
					ground.set_cell(Vector2i(x, y), 0, _ground_tile(x, y))
					if _at(x, y - 1) == "." and _rng.randf() < 0.38:
						deco.set_cell(Vector2i(x, y - 1), 0, T[DECOS[_rng.randi() % DECOS.size()]])
				"=":
					ground.set_cell(Vector2i(x, y), 0, _stone_tile(x, y))
				"-":
					ground.set_cell(Vector2i(x, y), 0, _ledge_tile(x, y))
				"P":
					_spawn_player(x, y)
				"E":
					_spawn(SoldadoScene, x, y)
				"C":
					_spawn(CruzScene, x, y)
					_spawn(FogueiraScene, x, y, Vector2(14, 0))
				"F":
					_spawn(FogueiraScene, x, y)
				"h":
					_spawn(ErvaScene, x, y, Vector2(0, -8))
				"G":
					_spawn(ArcoScene, x, y, Vector2(8, 0))
	_build_collisions()
	camera.limit_left = 0
	camera.limit_right = width * TILE
	camera.limit_top = -160
	camera.limit_bottom = height * TILE


func _at(x: int, y: int) -> String:
	if y < 0 or y >= height or x < 0:
		return "."
	var row := map[y]
	if x >= row.length():
		return "."
	return row[x]


func _solid(x: int, y: int) -> bool:
	var ch := _at(x, y)
	return ch == "#" or ch == "="


func _pick(a: String, b: String, c: String = "") -> Vector2i:
	var r := _rng.randf()
	if c != "" and r < 0.2:
		return T[c]
	return T[a] if r < 0.65 else T[b]


func _ground_tile(x: int, y: int) -> Vector2i:
	var up := not _solid(x, y - 1)
	var left := not _solid(x - 1, y)
	var right := not _solid(x + 1, y)
	if up:
		if left:
			return T["grass_l"]
		if right:
			return T["grass_r"]
		return _pick("grass_a", "grass_b", "grass_c")
	if left:
		return T["dirt_l"]
	if right:
		return T["dirt_r"]
	return _pick("dirt_a", "dirt_b")


func _stone_tile(x: int, y: int) -> Vector2i:
	var up := not _solid(x, y - 1)
	var down := not _solid(x, y + 1)
	var left := not _solid(x - 1, y)
	var right := not _solid(x + 1, y)
	if up and left and right:
		return T["stone_single"]
	if up and left:
		return T["stone_tl"]
	if up and right:
		return T["stone_tr"]
	if up:
		return T["stone_top"]
	if down and left:
		return T["stone_bl"]
	if down and right:
		return T["stone_br"]
	if down:
		return T["stone_bottom"]
	if left:
		return T["stone_l"]
	if right:
		return T["stone_r"]
	return _pick("stone_a", "stone_b")


func _ledge_tile(x: int, y: int) -> Vector2i:
	var left := _at(x - 1, y) != "-"
	var right := _at(x + 1, y) != "-"
	if left and not right:
		return T["ledge_l"]
	if right and not left:
		return T["ledge_r"]
	return T["ledge_m"]


func _build_collisions() -> void:
	for y in height:
		var x := 0
		while x < width:
			if _solid(x, y):
				var x0 := x
				while x < width and _solid(x, y):
					x += 1
				_add_rect(solids, x0, y, x - x0, TILE, 0)
			elif _at(x, y) == "-":
				var x0 := x
				while x < width and _at(x, y) == "-":
					x += 1
				_add_rect(ledges, x0, y, x - x0, 6, 0, true)
			else:
				x += 1


func _add_rect(body: StaticBody2D, tx: int, ty: int, w: int, h_px: int, y_off: int, one_way := false) -> void:
	var shape := RectangleShape2D.new()
	shape.size = Vector2(w * TILE, h_px)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2((tx + w / 2.0) * TILE, ty * TILE + y_off + h_px / 2.0)
	cs.one_way_collision = one_way
	cs.one_way_collision_margin = 6.0
	body.add_child(cs)


func _cell_pos(x: int, y: int) -> Vector2:
	return Vector2((x + 0.5) * TILE, (y + 1) * TILE)


func _spawn(scene: PackedScene, x: int, y: int, offset := Vector2.ZERO) -> Node:
	var n: Node2D = scene.instantiate()
	n.position = _cell_pos(x, y) + offset
	entities.add_child(n)
	return n


func _spawn_player(x: int, y: int) -> void:
	player = SepeScene.instantiate()
	player.position = Game.checkpoint if Game.has_checkpoint else _cell_pos(x, y)
	entities.add_child(player)
	player.died.connect(_on_player_died)
	camera.target = player
	camera.snap_to(player.position + Vector2(26, -28))


# ------------------------------------------------------------------ eventos
func checkpoint_reached(pos: Vector2) -> void:
	Game.checkpoint = pos
	Game.has_checkpoint = true
	Game.heal(Game.MAX_HP)
	hud.show_message("Ponto de descanso")


func _on_player_died() -> void:
	Game.deaths += 1
	await get_tree().create_timer(1.3).timeout
	Game.hp = Game.MAX_HP
	Game.change_scene(scene_file_path, 0.6, 0.8)


func finish() -> void:
	if _finished:
		return
	_finished = true
	player.controls_enabled = false
	Audio.play_sfx("cruz", -2.0)
	hud.show_message("Sepé segue para o Caiboaté... Continua.", 3.5)
	await get_tree().create_timer(4.2).timeout
	Game.reset_run()
	Game.change_scene(Game.SCENE_TITLE, 1.2, 1.0)

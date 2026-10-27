class_name SpriteSheets
## Monta SpriteFrames a partir dos spritesheets gerados por tools/gen_sprites.py.
## Cada animação: [primeiro frame, quantidade, fps, loop].

const FRAME := Vector2i(40, 32)
const SEPE := {
	"idle": [0, 2, 2.5, true],
	"run": [2, 6, 12.0, true],
	"jump": [8, 1, 1.0, false],
	"fall": [9, 1, 1.0, false],
	"hurt": [10, 1, 1.0, false],
	"attack": [11, 3, 12.0, false],
}
const SOLDADO := {
	"idle": [0, 2, 2.0, true],
	"walk": [2, 6, 9.0, true],
	"alert": [8, 1, 1.0, false],
	"lunge": [9, 2, 8.0, false],
	"hurt": [11, 1, 1.0, false],
}


static func build(texture: Texture2D, anims: Dictionary, frame_size: Vector2i = FRAME) -> SpriteFrames:
	var sf := SpriteFrames.new()
	if sf.has_animation("default") and not anims.has("default"):
		sf.remove_animation("default")
	var cols := int(texture.get_width() / float(frame_size.x))
	for anim_name in anims:
		var d: Array = anims[anim_name]
		if sf.has_animation(anim_name):
			sf.clear(anim_name)
		else:
			sf.add_animation(anim_name)
		sf.set_animation_speed(anim_name, d[2])
		sf.set_animation_loop(anim_name, d[3])
		for i in range(d[1]):
			var idx: int = d[0] + i
			var at := AtlasTexture.new()
			at.atlas = texture
			var col := idx % cols
			var row := int(floor(idx / float(cols)))
			at.region = Rect2(Vector2(col * frame_size.x, row * frame_size.y), Vector2(frame_size))
			sf.add_frame(anim_name, at)
	return sf


static func strip(texture: Texture2D, frame_w: int, frame_h: int, fps: float, loop := true) -> SpriteFrames:
	var n := int(texture.get_width() / float(frame_w))
	return build(texture, {"default": [0, n, fps, loop]}, Vector2i(frame_w, frame_h))

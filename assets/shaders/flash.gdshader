// Flash branco ao levar dano (uniform "flash" vai de 1.0 a 0.0 por tween).
shader_type canvas_item;

uniform float flash : hint_range(0.0, 1.0) = 0.0;

void fragment() {
	vec4 tex = texture(TEXTURE, UV);
	COLOR = vec4(mix(tex.rgb, vec3(1.6, 1.5, 1.4), flash), tex.a) * COLOR;
}

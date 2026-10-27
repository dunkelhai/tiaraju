extends Node
## Música, ambiente e efeitos. Todos os .wav são sintetizados por tools/compose.py.
## Autoload "Audio".

const MUSIC := {
	"tema": "res://assets/audio/tema_esta_terra_tem_dono.wav",
	"lamento": "res://assets/audio/lamento.wav",
}
const AUDIO_DIR := "res://assets/audio/"
const POOL_SIZE := 10

var _music: AudioStreamPlayer
var _music_name := ""
var _ambience := {}
var _pool: Array[AudioStreamPlayer] = []
var _streams := {}
var _music_tween: Tween


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_bus("Music", -3.0)
	_ensure_bus("SFX", -2.0)
	_ensure_bus("Ambience", -6.0)
	_music = AudioStreamPlayer.new()
	_music.bus = "Music"
	add_child(_music)
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_pool.append(p)


func _ensure_bus(bus_name: String, volume_db: float) -> void:
	if AudioServer.get_bus_index(bus_name) != -1:
		return
	var idx := AudioServer.bus_count
	AudioServer.add_bus(idx)
	AudioServer.set_bus_name(idx, bus_name)
	AudioServer.set_bus_send(idx, "Master")
	AudioServer.set_bus_volume_db(idx, volume_db)


func _stream(path: String, loop := false) -> AudioStream:
	if not _streams.has(path):
		var s: AudioStream = load(path)
		if s is AudioStreamWAV and loop:
			var wav := s as AudioStreamWAV
			var bytes_per_frame := 2 * (2 if wav.stereo else 1)
			wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
			wav.loop_begin = 0
			wav.loop_end = int(wav.data.size() / float(bytes_per_frame))
		_streams[path] = s
	return _streams[path]


func play_music(name: String, fade := 1.5) -> void:
	if _music_name == name and _music.playing:
		return
	_music_name = name
	var stream := _stream(MUSIC[name], true)
	if _music_tween:
		_music_tween.kill()
	_music_tween = create_tween()
	if _music.playing:
		_music_tween.tween_property(_music, "volume_db", -40.0, fade * 0.5)
	_music_tween.tween_callback(func() -> void:
		_music.stream = stream
		_music.volume_db = -40.0
		_music.play())
	_music_tween.tween_property(_music, "volume_db", 0.0, fade)


func stop_music(fade := 1.0) -> void:
	_music_name = ""
	if _music_tween:
		_music_tween.kill()
	_music_tween = create_tween()
	_music_tween.tween_property(_music, "volume_db", -40.0, fade)
	_music_tween.tween_callback(_music.stop)


func play_ambience(name: String, volume_db := -12.0) -> void:
	if _ambience.has(name):
		return
	var p := AudioStreamPlayer.new()
	p.bus = "Ambience"
	p.stream = _stream(AUDIO_DIR + "amb_%s.wav" % name, true)
	p.volume_db = -40.0
	add_child(p)
	p.play()
	_ambience[name] = p
	create_tween().tween_property(p, "volume_db", volume_db, 2.0)


func stop_ambience(name: String) -> void:
	if not _ambience.has(name):
		return
	var p: AudioStreamPlayer = _ambience[name]
	_ambience.erase(name)
	var tw := create_tween()
	tw.tween_property(p, "volume_db", -40.0, 1.0)
	tw.tween_callback(p.queue_free)


func play_sfx(name: String, volume_db := 0.0, pitch_var := 0.07) -> void:
	var p := _free_player()
	p.stream = _stream(AUDIO_DIR + "sfx_%s.wav" % name)
	p.volume_db = volume_db
	p.pitch_scale = randf_range(1.0 - pitch_var, 1.0 + pitch_var)
	p.play()


func _free_player() -> AudioStreamPlayer:
	for p in _pool:
		if not p.playing:
			return p
	return _pool[randi() % _pool.size()]

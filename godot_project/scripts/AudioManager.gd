extends Node

## Autoload: Sistema completo de audio (música con crossfade + pool de SFX + buses Master/Music/SFX)

const SFX_POOL_SIZE := 8
const MIN_SFX_INTERVAL_MS := {
	"hit": 45,
	"crit": 55,
	"swing": 55,
	"loot": 60,
	"ui": 35,
}

var _tracks := {}
var _sfx_streams := {}
var _sfx_pool: Array[AudioStreamPlayer] = []
var _sfx_cursor: int = 0
var _last_sfx_ms: Dictionary = {}

var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _active_music: AudioStreamPlayer
var _current_track: String = ""
var _fade_tween: Tween

var master_volume: float = 0.85
var music_volume: float = 0.70
var sfx_volume: float = 0.85
var muted: bool = false

func _exit_tree() -> void:
	stop_all()
	if _music_a: _music_a.stream = null
	if _music_b: _music_b.stream = null
	for p in _sfx_pool:
		if is_instance_valid(p):
			p.stream = null
	_tracks.clear()
	_sfx_streams.clear()

func stop_all() -> void:
	if _fade_tween and _fade_tween.is_valid():
		_fade_tween.kill()
	if _music_a and is_instance_valid(_music_a):
		_music_a.stop()
	if _music_b and is_instance_valid(_music_b):
		_music_b.stop()
	for p in _sfx_pool:
		if is_instance_valid(p):
			p.stop()

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_buses()
	_load_streams()
	_build_players()
	var ss = get_node_or_null("/root/SaveSystem")
	if ss and ss.has_method("load_settings_only"):
		ss.load_settings_only()
		apply_settings_dict(ss.settings)
	else:
		_apply_bus_volumes()

func _ensure_buses() -> void:
	if AudioServer.get_bus_index("Music") == -1:
		var idx := AudioServer.bus_count
		AudioServer.add_bus(idx)
		AudioServer.set_bus_name(idx, "Music")
		AudioServer.set_bus_send(idx, "Master")
	if AudioServer.get_bus_index("SFX") == -1:
		var idx2 := AudioServer.bus_count
		AudioServer.add_bus(idx2)
		AudioServer.set_bus_name(idx2, "SFX")
		AudioServer.set_bus_send(idx2, "Master")

func _load_streams() -> void:
	for track_id in ["menu_theme", "ambient", "boss_theme"]:
		var p := "res://assets/audio/%s.wav" % track_id
		if ResourceLoader.exists(p):
			var st = load(p)
			if st is AudioStreamWAV:
				st.loop_mode = AudioStreamWAV.LOOP_FORWARD
				st.loop_begin = 0
				var bytes_per_sample := 2 if st.format == AudioStreamWAV.FORMAT_16_BITS else 1
				var channels := 2 if st.stereo else 1
				st.loop_end = maxi(1, int(st.data.size() / maxi(1, bytes_per_sample * channels)))
			_tracks[track_id] = st

	var sfx_ids := [
		"hit", "crit", "swing", "skill_q", "skill_e", "skill_r", "dash",
		"levelup", "evolution", "upgrade", "loot", "boss", "boss_defeat",
		"player_hurt", "gameover", "ui"
	]
	for sid in sfx_ids:
		var p2 := "res://assets/audio/%s.wav" % sid
		if ResourceLoader.exists(p2):
			_sfx_streams[sid] = load(p2)

func _build_players() -> void:
	_music_a = AudioStreamPlayer.new()
	_music_a.name = "MusicDeckA"
	_music_a.bus = "Music" if AudioServer.get_bus_index("Music") != -1 else "Master"
	add_child(_music_a)

	_music_b = AudioStreamPlayer.new()
	_music_b.name = "MusicDeckB"
	_music_b.bus = "Music" if AudioServer.get_bus_index("Music") != -1 else "Master"
	add_child(_music_b)
	_active_music = _music_a

	var sfx_bus := "SFX" if AudioServer.get_bus_index("SFX") != -1 else "Master"
	for i in range(SFX_POOL_SIZE):
		var sp := AudioStreamPlayer.new()
		sp.name = "SFXChannel_%d" % i
		sp.bus = sfx_bus
		add_child(sp)
		_sfx_pool.append(sp)

func play_music(track_id: String, crossfade_sec: float = 0.65) -> void:
	if not _tracks.has(track_id):
		if track_id != "ambient" and _tracks.has("ambient"):
			track_id = "ambient"
		else:
			return
	if _current_track == track_id and _active_music != null and _active_music.playing:
		return
	_current_track = track_id
	var next_deck := _music_b if _active_music == _music_a else _music_a
	var prev_deck := _active_music
	_active_music = next_deck

	if _fade_tween and _fade_tween.is_valid():
		_fade_tween.kill()

	next_deck.stream = _tracks[track_id]
	var target_db := -5.5 if track_id == "boss_theme" else -7.5
	if crossfade_sec <= 0.02 or prev_deck == null or not prev_deck.playing:
		if prev_deck:
			prev_deck.stop()
		next_deck.volume_db = target_db
		next_deck.play()
		return

	next_deck.volume_db = -36.0
	next_deck.play()
	_fade_tween = create_tween()
	_fade_tween.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	_fade_tween.tween_property(next_deck, "volume_db", target_db, crossfade_sec)
	_fade_tween.parallel().tween_property(prev_deck, "volume_db", -40.0, crossfade_sec)
	_fade_tween.tween_callback(func():
		if is_instance_valid(prev_deck):
			prev_deck.stop()
	)

func stop_music() -> void:
	_current_track = ""
	if _music_a: _music_a.stop()
	if _music_b: _music_b.stop()

func get_current_track() -> String:
	return _current_track

func play_sfx(sfx_id: String, pitch_min: float = 0.96, pitch_max: float = 1.04, volume_offset_db: float = 0.0) -> void:
	if muted or master_volume <= 0.001 or sfx_volume <= 0.001:
		return
	if not _sfx_streams.has(sfx_id):
		return
	var now_ms := Time.get_ticks_msec()
	var min_gap: int = int(MIN_SFX_INTERVAL_MS.get(sfx_id, 20))
	var last_ms: int = int(_last_sfx_ms.get(sfx_id, -9999))
	if now_ms - last_ms < min_gap:
		return
	_last_sfx_ms[sfx_id] = now_ms

	if _sfx_pool.is_empty():
		return
	var ch := _sfx_pool[_sfx_cursor]
	_sfx_cursor = (_sfx_cursor + 1) % _sfx_pool.size()
	ch.stream = _sfx_streams[sfx_id]
	ch.pitch_scale = randf_range(pitch_min, pitch_max) if pitch_max > pitch_min else pitch_min
	ch.volume_db = volume_offset_db
	ch.play()

func set_master_volume(val: float) -> void:
	master_volume = clampf(val, 0.0, 1.0)
	_apply_bus_volumes()

func set_music_volume(val: float) -> void:
	music_volume = clampf(val, 0.0, 1.0)
	_apply_bus_volumes()

func set_sfx_volume(val: float) -> void:
	sfx_volume = clampf(val, 0.0, 1.0)
	_apply_bus_volumes()

func set_muted(is_muted: bool) -> void:
	muted = is_muted
	_apply_bus_volumes()

func apply_settings_dict(s: Dictionary) -> void:
	if s.has("master_volume"):
		master_volume = clampf(float(s["master_volume"]), 0.0, 1.0)
	if s.has("music_volume"):
		music_volume = clampf(float(s["music_volume"]), 0.0, 1.0)
	if s.has("sfx_volume"):
		sfx_volume = clampf(float(s["sfx_volume"]), 0.0, 1.0)
	if s.has("audio_muted"):
		muted = bool(s["audio_muted"])
	_apply_bus_volumes()

func _apply_bus_volumes() -> void:
	_ensure_buses()
	var master_idx := AudioServer.get_bus_index("Master")
	var music_idx := AudioServer.get_bus_index("Music")
	var sfx_idx := AudioServer.get_bus_index("SFX")

	if master_idx != -1:
		var m_mute := muted or master_volume <= 0.001
		AudioServer.set_bus_mute(master_idx, m_mute)
		AudioServer.set_bus_volume_db(master_idx, linear_to_db(maxf(0.0001, master_volume)))
	if music_idx != -1:
		AudioServer.set_bus_mute(music_idx, music_volume <= 0.001)
		AudioServer.set_bus_volume_db(music_idx, linear_to_db(maxf(0.0001, music_volume)))
	if sfx_idx != -1:
		AudioServer.set_bus_mute(sfx_idx, sfx_volume <= 0.001)
		AudioServer.set_bus_volume_db(sfx_idx, linear_to_db(maxf(0.0001, sfx_volume)))

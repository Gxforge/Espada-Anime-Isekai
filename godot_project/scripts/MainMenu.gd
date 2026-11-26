extends Control

@onready var prompt: Label = $Prompt
@onready var fade: ColorRect = $Fade
var _ready_to_start := false
var _starting := false

var _music: AudioStreamPlayer

func _ready() -> void:
	get_tree().paused = false
	if has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").load_settings_only()
	fade.color = Color(0, 0, 0, 1)
	if prompt:
		prompt.text = "✦  Presiona cualquier tecla  ✦"
		prompt.add_theme_color_override("font_color", Color(1.0, 0.93, 0.68))
		prompt.add_theme_color_override("font_outline_color", Color(0.02, 0.04, 0.12, 0.96))
		prompt.add_theme_constant_override("outline_size", 6)
		var pill := StyleBoxFlat.new()
		pill.bg_color = Color(0.03, 0.06, 0.14, 0.72)
		pill.border_color = Color(0.98, 0.80, 0.32, 0.65)
		pill.set_border_width_all(1)
		pill.set_corner_radius_all(18)
		pill.content_margin_left = 22
		pill.content_margin_right = 22
		pill.content_margin_top = 6
		pill.content_margin_bottom = 6
		prompt.add_theme_stylebox_override("normal", pill)
	var tw = create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.6)
	tw.tween_callback(func(): _ready_to_start = true)
	var blink = create_tween().set_loops()
	blink.tween_property(prompt, "modulate:a", 0.68, 0.85)
	blink.tween_property(prompt, "modulate:a", 1.0, 0.85)
	_play_music()

func _unhandled_input(event: InputEvent) -> void:
	if _starting or not _ready_to_start:
		return
	var pressed := false
	if event is InputEventKey and event.pressed and not event.echo:
		pressed = true
	elif event is InputEventMouseButton and event.pressed:
		pressed = true
	elif event is InputEventJoypadButton and event.pressed:
		pressed = true
	if pressed:
		_start_game()

func _start_game() -> void:
	_starting = true
	var am := get_node_or_null("/root/AudioManager")
	if am and am.has_method("play_sfx"):
		am.play_sfx("evolution", 1.0, 1.0)
	var tw = create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.4)
	tw.tween_callback(func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))

func _play_music() -> void:
	var am := get_node_or_null("/root/AudioManager")
	if am and am.has_method("play_music"):
		am.play_music("menu_theme", 0.5)
		return
	if not ResourceLoader.exists("res://assets/audio/ambient.wav"):
		return
	_music = AudioStreamPlayer.new()
	var st = load("res://assets/audio/ambient.wav")
	if st is AudioStreamWAV:
		st.loop_mode = AudioStreamWAV.LOOP_FORWARD
		st.loop_end = int(st.data.size() / 2)
	_music.stream = st
	_music.volume_db = -8.0
	add_child(_music)
	_music.play()

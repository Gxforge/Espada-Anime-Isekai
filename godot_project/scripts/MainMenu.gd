extends Control

@onready var prompt: Label = $Prompt
@onready var fade: ColorRect = $Fade
var _ready_to_start := false
var _starting := false

var _music: AudioStreamPlayer

func _ready() -> void:
	fade.color = Color(0,0,0,1)
	var tw = create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.6)
	tw.tween_callback(func(): _ready_to_start = true)
	# blink prompt
	var blink = create_tween().set_loops()
	blink.tween_property(prompt, "modulate:a", 0.35, 0.8)
	blink.tween_property(prompt, "modulate:a", 1.0, 0.8)
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
	var tw = create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.4)
	tw.tween_callback(func(): get_tree().change_scene_to_file("res://scenes/Main.tscn"))


func _play_music() -> void:
	if not ResourceLoader.exists("res://assets/audio/ambient.wav"): return
	_music = AudioStreamPlayer.new()
	var st = load("res://assets/audio/ambient.wav")
	if st is AudioStreamWAV:
		st.loop_mode = AudioStreamWAV.LOOP_FORWARD
		st.loop_end = st.data.size() / 2
	_music.stream = st
	_music.volume_db = -8.0
	add_child(_music)
	_music.play()

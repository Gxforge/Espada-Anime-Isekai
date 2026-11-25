extends Control

@onready var bar: ProgressBar = $Panel/VBox/ProgressBar
@onready var label: Label = $Panel/VBox/Label
@onready var tip: Label = $Panel/VBox/Tip

var _progress := 0.0
var _done := false

func _ready() -> void:
	bar.value = 0
	label.text = "Cargando Forja de Almas 3D..."
	tip.text = "Consejo: usa Q, E, R y Shift para dominar el combate."
	# start threaded load
	var path = "res://scenes/MainMenu.tscn"
	var err = ResourceLoader.load_threaded_request(path)
	if err != OK:
		# fallback
		get_tree().change_scene_to_file(path)

func _process(delta: float) -> void:
	if _done: return
	_progress = min(100.0, _progress + delta * 55.0)
	bar.value = _progress
	var path = "res://scenes/MainMenu.tscn"
	var status = ResourceLoader.load_threaded_get_status(path)
	if status == ResourceLoader.THREAD_LOAD_LOADED and _progress >= 90.0:
		_done = true
		bar.value = 100
		var scene = ResourceLoader.load_threaded_get(path)
		await get_tree().create_timer(0.25).timeout
		get_tree().change_scene_to_packed(scene)
	elif status == ResourceLoader.THREAD_LOAD_FAILED:
		_done = true
		get_tree().change_scene_to_file(path)

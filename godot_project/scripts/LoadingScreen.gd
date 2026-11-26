extends Control

@onready var bar: ProgressBar = $Panel/VBox/ProgressBar
@onready var label: Label = $Panel/VBox/Label
@onready var tip: Label = $Panel/VBox/Tip

var _progress := 0.0
var _done := false

func _ready() -> void:
	var panel_node: Panel = get_node_or_null("Panel")
	if panel_node:
		var psb := StyleBoxFlat.new()
		psb.bg_color = Color(0.04, 0.07, 0.16, 0.88)
		psb.border_color = Color(0.38, 0.72, 1.0, 0.55)
		psb.set_border_width_all(2)
		psb.set_corner_radius_all(14)
		panel_node.add_theme_stylebox_override("panel", psb)
	if bar:
		var bbg := StyleBoxFlat.new()
		bbg.bg_color = Color(0.06, 0.09, 0.18, 0.95)
		bbg.set_corner_radius_all(8)
		var bfill := StyleBoxFlat.new()
		bfill.bg_color = Color(0.22, 0.68, 0.98, 0.96)
		bfill.set_corner_radius_all(8)
		bar.add_theme_stylebox_override("background", bbg)
		bar.add_theme_stylebox_override("fill", bfill)
		bar.value = 0
	if label:
		label.text = "Forjando el Santuario de Almas..."
		label.add_theme_color_override("font_color", Color(0.98, 0.92, 0.62))
		label.add_theme_font_size_override("font_size", 18)
	if tip:
		tip.text = "Consejo: limpia 8 enemigos por oleada, equipa Reliquias y domina Q, E, R y Shift."
		tip.add_theme_font_size_override("font_size", 13)
		tip.add_theme_color_override("font_color", Color(0.84, 0.91, 1.0))

	var am := get_node_or_null("/root/AudioManager")
	if am and am.has_method("play_music"):
		am.play_music("menu_theme", 0.5)

	var path := "res://scenes/MainMenu.tscn"
	var err := ResourceLoader.load_threaded_request(path)
	if err != OK:
		get_tree().change_scene_to_file(path)

func _process(delta: float) -> void:
	if _done:
		return
	_progress = min(100.0, _progress + delta * 62.0)
	if bar:
		bar.value = _progress
	var path := "res://scenes/MainMenu.tscn"
	var status := ResourceLoader.load_threaded_get_status(path)
	if status == ResourceLoader.THREAD_LOAD_LOADED and _progress >= 90.0:
		_done = true
		if bar:
			bar.value = 100
		var scene := ResourceLoader.load_threaded_get(path)
		await get_tree().create_timer(0.22).timeout
		get_tree().change_scene_to_packed(scene)
	elif status == ResourceLoader.THREAD_LOAD_FAILED:
		_done = true
		get_tree().change_scene_to_file(path)

extends Control

@onready var logo: TextureRect = $Logo
@onready var fade: ColorRect = $Fade

func _ready() -> void:
	fade.color = Color(0,0,0,1)
	logo.modulate.a = 0.0
	var tw = create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.6)
	tw.parallel().tween_property(logo, "modulate:a", 1.0, 0.8)
	tw.tween_interval(1.6)
	tw.tween_property(fade, "color:a", 1.0, 0.5)
	tw.tween_callback(func(): get_tree().change_scene_to_file("res://scenes/LoadingScreen.tscn"))

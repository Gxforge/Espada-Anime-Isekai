extends Node3D

var target_pos: Vector3
var damage: float
var attacker: Node3D
var fall_progress: float = 0.0
var exploded: bool = false
var linger: float = 1.1
var start_y: float = 18.0

func setup(target: Vector3, dmg: float, atk: Node3D) -> void:
	target_pos = target
	damage = dmg
	attacker = atk
	start_y = global_position.y

func _physics_process(delta: float) -> void:
	if not exploded:
		fall_progress += delta * 3.4
		if fall_progress >= 0.0:
			var t: float = clamp(fall_progress, 0.0, 1.0)
			global_position.y = lerp(start_y, 2.2, t)
			if fall_progress >= 1.0:
				exploded = true
				_explode()
	else:
		linger -= delta
		if linger <= 0.0:
			queue_free()

func _explode() -> void:
	for e in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(e):
			continue
		if e.global_position.distance_to(target_pos) <= 5.2:
			if e.has_method("take_damage"):
				e.take_damage(damage, attacker, true, 7.5)

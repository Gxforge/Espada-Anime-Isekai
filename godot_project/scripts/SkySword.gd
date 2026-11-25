extends Node3D

var target_pos: Vector3
var damage: float
var attacker: Node3D
var fall_progress: float = 0.0
var exploded: bool = false
var linger: float = 1.2
var start_y: float = 18.0

func setup(target: Vector3, dmg: float, atk: Node3D, delay: float = 0.0) -> void:
	target_pos = target
	damage = dmg
	attacker = atk
	start_y = global_position.y
	fall_progress = -delay

func _physics_process(delta: float) -> void:
	if not exploded:
		fall_progress += delta * 3.4
		if fall_progress >= 0.0:
			var t: float = clamp(fall_progress, 0.0, 1.0)
			global_position.y = lerp(start_y, 0.5, t)
			if fall_progress >= 1.0:
				exploded = true
				_explode()
	else:
		linger -= delta
		# fade out
		for c in get_children():
			if c is Node3D:
				c.scale = c.scale.lerp(Vector3.ONE * 0.01, delta * 2.0)
		if linger <= 0.0:
			queue_free()

func _explode() -> void:
	_spawn_impact_ring()
	for e in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(e):
			continue
		if e.global_position.distance_to(target_pos) <= 5.2:
			if e.has_method("take_damage"):
				e.take_damage(damage, attacker, true, 7.5)

func _spawn_impact_ring() -> void:
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.5
	torus.outer_radius = 0.9
	ring.mesh = torus
	var mat := StandardMaterial3D.new()
	var col: Color = attacker.current_tier.get("aura_color", Color.CYAN) if is_instance_valid(attacker) and "current_tier" in attacker else Color.CYAN
	mat.albedo_color = Color(col, 0.8)
	mat.emission_enabled = true
	mat.emission = col
	mat.emission_energy_multiplier = 3.0
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	ring.material_override = mat
	get_tree().current_scene.add_child(ring)
	ring.global_position = Vector3(target_pos.x, 0.15, target_pos.z)
	var tw := get_tree().current_scene.create_tween()
	tw.tween_property(ring, "scale", Vector3(5.2, 1.0, 5.2), 0.35)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.35)
	tw.tween_callback(ring.queue_free)

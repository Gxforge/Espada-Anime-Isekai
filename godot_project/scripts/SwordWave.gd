extends Node3D

var velocity: Vector3 = Vector3.ZERO
var damage: float = 10.0
var life: float = 1.6
var attacker: Node3D
var hit_ids: Dictionary = {}

func setup(vel: Vector3, dmg: float, atk: Node3D) -> void:
	velocity = vel
	damage = dmg
	attacker = atk

func _physics_process(delta: float) -> void:
	life -= delta
	global_position += velocity * delta
	for e in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(e):
			continue
		var id := e.get_instance_id()
		if hit_ids.has(id):
			continue
		if global_position.distance_to(e.global_position) <= 2.8:
			hit_ids[id] = true
			if e.has_method("take_damage"):
				e.take_damage(damage, attacker, false, 6.5)
	if life <= 0.0:
		queue_free()

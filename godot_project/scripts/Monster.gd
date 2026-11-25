extends CharacterBody3D
class_name Monster

@export var monster_id: String = "slime"

var def: Dictionary
var hp: int = 50
var max_hp: int = 50
var damage: int = 5
var speed: float = 3.0
var attack_range: float = 2.0
var attack_cooldown_def: float = 1.2
var xp_reward: int = 10
var gold_reward: int = 5
var is_boss: bool = false

var attack_cd: float = 0.8
var attack_anim: float = 0.0
var hit_flash: float = 0.0
var knockback_vel: Vector3 = Vector3.ZERO
var bleed_timer: float = 0.0

var player: Node3D = null

@onready var model_holder: Node3D = $ModelHolder

func setup(monster_def: Dictionary, wave: int, player_ref: Node3D) -> void:
	def = monster_def
	player = player_ref
	is_boss = bool(def.get("is_boss", false))
	var wave_scale := 1.0 + (wave - 1) * 0.24
	max_hp = int(round(float(def["base_hp"]) * wave_scale))
	hp = max_hp
	damage = int(round(float(def["base_damage"]) * (1.0 + (wave - 1) * 0.16)))
	speed = float(def["speed"])
	attack_range = float(def["attack_range"])
	attack_cooldown_def = float(def["attack_cooldown"])
	xp_reward = int(def["xp_reward"])
	gold_reward = int(def["gold_reward"])
	var s := float(def.get("scale", 1.0))
	model_holder.scale = Vector3.ONE * s
	_load_model()

func _load_model() -> void:
	for c in model_holder.get_children():
		c.queue_free()
	var Builder = load("res://scripts/MonsterBuilder.gd")
	var built: Node3D = Builder.build_monster(str(def.get("id", "slime")))
	for child in built.get_children():
		built.remove_child(child)
		model_holder.add_child(child)
	built.queue_free()

func _physics_process(delta: float) -> void:
	if not is_instance_valid(player):
		return
	if hit_flash > 0.0:
		hit_flash = max(0.0, hit_flash - delta)
		if hit_flash <= 0.0:
			_set_flash(false)
	if bleed_timer > 0.0:
		bleed_timer = max(0.0, bleed_timer - delta)
		hp -= int(max(1, max_hp * 0.04 * delta))
		if hp <= 0:
			_die(player)
			return

	# knockback decay
	if knockback_vel.length_squared() > 0.01:
		global_position += knockback_vel * delta
		knockback_vel = knockback_vel.lerp(Vector3.ZERO, min(1.0, delta * 8.0))

	var to_player: Vector3 = player.global_position - global_position
	to_player.y = 0
	var dist := to_player.length()
	if dist > 0.05:
		var target_rot := atan2(to_player.x, to_player.z)
		rotation.y = lerp_angle(rotation.y, target_rot, delta * 6.0)

	var moving := false
	if dist > attack_range:
		var dir := to_player.normalized()
		velocity = dir * speed
		moving = true
		attack_anim = 0.0
	else:
		velocity = Vector3.ZERO
		attack_cd -= delta
		if attack_cd <= 0.0:
			attack_cd = attack_cooldown_def
			attack_anim = 0.01

	if attack_anim > 0.0:
		attack_anim += delta * 2.6
		if attack_anim >= 0.5 and (attack_anim - delta * 2.6) < 0.5:
			if dist <= attack_range + 0.7 and is_instance_valid(player) and player.has_method("take_player_damage"):
				player.take_player_damage(damage)
		if attack_anim >= 1.0:
			attack_anim = 0.0

	move_and_slide()
	# simple idle/move bob
	var t := Time.get_ticks_msec() / 1000.0
	if moving:
		model_holder.position.y = abs(sin(t * 8.0)) * 0.08
	else:
		model_holder.position.y = sin(t * 2.5) * 0.04

func take_damage(amount: float, attacker: Node3D, is_heavy: bool = false, knockback: float = 5.5) -> void:
	if hp <= 0:
		return
	var final_dmg := amount
	var is_crit := randf() < float(attacker.stats.get("crit_chance", 0.1))
	if is_crit:
		final_dmg *= float(attacker.stats.get("crit_mult", 1.8))
	final_dmg = max(1.0, round(final_dmg))
	hp -= int(final_dmg)
	hit_flash = 0.14
	_set_flash(true)

	# knockback
	if is_instance_valid(attacker):
		var dir: Vector3 = (global_position - attacker.global_position)
		dir.y = 0
		if dir.length_squared() > 0.001:
			dir = dir.normalized()
		else:
			dir = Vector3.BACK
		knockback_vel = dir * knockback

	# lifesteal
	if is_instance_valid(attacker) and attacker.has_method("gain_experience"):
		var loh := int(attacker.stats.get("life_on_hit", 0))
		if loh > 0:
			attacker.player_hp = min(attacker.player_max_hp, attacker.player_hp + loh)
			attacker.hp_changed.emit(attacker.player_hp, attacker.player_max_hp)

	# special effects
	if is_instance_valid(attacker):
		var eff := str(attacker.current_tier.get("special_effect", "none"))
		if eff == "bleed" and is_crit:
			bleed_timer = 3.0
		elif eff == "lightning":
			_chain_lightning(attacker, final_dmg * 0.45)

	if hp <= 0:
		_die(attacker)

func _chain_lightning(attacker: Node3D, dmg: float) -> void:
	var best: Node3D = null
	var best_d := 6.5
	for e in get_tree().get_nodes_in_group("enemies"):
		if e == self or not is_instance_valid(e):
			continue
		var d := global_position.distance_to(e.global_position)
		if d < best_d and e.hp > 0:
			best_d = d
			best = e
	if best and best.has_method("take_damage"):
		best.take_damage(dmg, attacker, false, 2.0)

func _die(attacker: Node3D) -> void:
	if not is_inside_tree():
		return
	if is_instance_valid(attacker) and attacker.has_method("gain_experience"):
		var xp_mult := float(attacker.stats.get("xp_mult", 1.0))
		var xp_gain := int(round(xp_reward * xp_mult))
		var gold_gain := int(round(gold_reward * (1.0 + int(attacker.upgrades.get("soulMagnet", 0)) * 0.12)))
		attacker.gain_experience(xp_gain)
		attacker.add_gold(gold_gain)
		attacker.add_kill()
	# spawn simple loot visual
	_spawn_loot_orbs()
	queue_free()

func _spawn_loot_orbs() -> void:
	var root := get_tree().current_scene
	for i in range(2):
		var orb := MeshInstance3D.new()
		var s := SphereMesh.new()
		s.radius = 0.18
		s.height = 0.36
		orb.mesh = s
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color("#38bdf8") if i == 0 else Color("#facc15")
		mat.emission_enabled = true
		mat.emission = mat.albedo_color
		mat.emission_energy_multiplier = 2.0
		orb.material_override = mat
		orb.global_position = global_position + Vector3(randf_range(-0.3,0.3), 0.8, randf_range(-0.3,0.3))
		root.add_child(orb)
		var tw := root.create_tween()
		tw.tween_property(orb, "global_position:y", 0.2, 0.5).set_trans(Tween.TRANS_BOUNCE)
		tw.tween_callback(orb.queue_free)

func _set_flash(active: bool) -> void:
	for c in model_holder.get_children():
		if c is MeshInstance3D:
			var mat: StandardMaterial3D = c.material_override
			if mat:
				mat.emission_energy_multiplier = 2.5 if active else 0.35

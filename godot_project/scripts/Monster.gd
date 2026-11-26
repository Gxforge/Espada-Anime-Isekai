extends CharacterBody3D
class_name Monster

signal boss_phase_changed(phase: int)
signal boss_defeated_reward(summary: Dictionary)

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
var _dead: bool = false

var attack_cd: float = 0.8
var attack_anim: float = 0.0
var hit_flash: float = 0.0
var knockback_vel: Vector3 = Vector3.ZERO
var bleed_timer: float = 0.0
var bleed_accum: float = 0.0
var burn_timer: float = 0.0
var burn_dps: float = 0.0
var burn_accum: float = 0.0
var regen_accum: float = 0.0
var enraged: bool = false

var player: Node3D = null

# Boss AI (Malakor, Señor del Abismo — 2 Phases)
var boss_phase: int = 1
var boss_state: String = "chase"
var boss_timer: float = 0.0
var boss_target: Vector3 = Vector3.ZERO
var boss_meteor_targets: Array[Vector3] = []
var boss_telegraph: MeshInstance3D = null
var boss_extra_telegraphs: Array[MeshInstance3D] = []

# HP bar
var hp_bar_bg: MeshInstance3D
var hp_bar_fill: MeshInstance3D

# Distinct AI
var ai_timer: float = 0.0
var dash_dir: Vector3 = Vector3.ZERO
var circling: int = 1

@onready var model_holder: Node3D = get_node_or_null("ModelHolder")

func _ready() -> void:
	add_to_group("enemies")
	add_to_group("monsters")

func _exit_tree() -> void:
	_clear_telegraph()

func setup(monster_def: Dictionary, wave: int, player_ref: Node3D) -> void:
	def = monster_def
	player = player_ref
	_dead = false
	monster_id = str(def.get("id", monster_id))
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
	if model_holder == null:
		model_holder = Node3D.new()
		model_holder.name = "ModelHolder"
		add_child(model_holder)
	var s := float(def.get("scale", 1.0))
	model_holder.scale = Vector3.ONE * s
	_load_model()
	_create_hp_bar()
	if is_boss:
		boss_phase = 1
		boss_state = "chase"
		boss_timer = 1.9
		_spawn_boss_entrance_vfx()

func _spawn_boss_entrance_vfx() -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	var root := get_tree().current_scene
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.6; torus.outer_radius = 1.1
	ring.mesh = torus
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.95, 0.15, 0.25, 0.9)
	mat.emission_enabled = true
	mat.emission = Color("#ef4444")
	mat.emission_energy_multiplier = 4.0
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	ring.material_override = mat
	root.add_child(ring)
	ring.global_position = Vector3(global_position.x, 0.12, global_position.z)
	var tw := root.create_tween()
	tw.tween_property(ring, "scale", Vector3(5.5, 1.0, 5.5), 0.55)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.55)
	tw.tween_callback(ring.queue_free)

func _load_model() -> void:
	for c in model_holder.get_children():
		c.queue_free()
	var built: Node3D = null
	if ResourceLoader.exists("res://scripts/ModelLoader.gd"):
		var ML = load("res://scripts/ModelLoader.gd")
		built = ML.build_monster_visual(def)
	if built == null:
		var Builder = load("res://scripts/MonsterBuilder.gd")
		built = Builder.build_monster(str(def.get("id", "slime")))
	if built.name == "MonsterOBJ":
		model_holder.add_child(built)
	else:
		for child in built.get_children():
			built.remove_child(child)
			model_holder.add_child(child)
		built.queue_free()

func _physics_process(delta: float) -> void:
	if _dead or not is_instance_valid(player):
		return
	if hit_flash > 0.0:
		hit_flash = max(0.0, hit_flash - delta)
		if hit_flash <= 0.0:
			_set_flash(false)

	# Bleed DoT (accumulated cleanly so fractional ticks apply accurately)
	if bleed_timer > 0.0:
		bleed_timer = max(0.0, bleed_timer - delta)
		bleed_accum += float(max_hp) * 0.05 * delta
		if bleed_accum >= 1.0:
			var bdmg := int(bleed_accum)
			bleed_accum -= float(bdmg)
			hp -= bdmg
			if hp <= 0:
				_die(player)
				return

	# Solar Burn DoT
	if burn_timer > 0.0:
		burn_timer = max(0.0, burn_timer - delta)
		burn_accum += burn_dps * delta
		_set_flash(int(Time.get_ticks_msec() / 100) % 2 == 0)
		if burn_accum >= 1.0:
			var fdmg := int(burn_accum)
			burn_accum -= float(fdmg)
			hp -= fdmg
			if hp <= 0:
				_die(player)
				return

	# Mineral Golem / Troll regeneration
	if monster_id in ["copper_golem", "troll"] and hp > 0 and hp < max_hp:
		regen_accum += float(max_hp) * 0.015 * delta
		if regen_accum >= 1.0:
			var rpts := int(regen_accum)
			regen_accum -= float(rpts)
			hp = mini(max_hp, hp + rpts)

	# Knockback decay
	if knockback_vel.length_squared() > 0.01:
		global_position += knockback_vel * delta
		knockback_vel = knockback_vel.lerp(Vector3.ZERO, min(1.0, delta * 8.0))
		var flat := Vector2(global_position.x, global_position.z)
		if flat.length() > 25.5:
			flat = flat.normalized() * 25.5
			global_position.x = flat.x
			global_position.z = flat.y

	var to_player: Vector3 = player.global_position - global_position
	to_player.y = 0
	var dist := to_player.length()
	if dist > 0.05 and boss_state != "charge":
		var target_rot := atan2(to_player.x, to_player.z)
		rotation.y = lerp_angle(rotation.y, target_rot, delta * 6.5)

	ai_timer -= delta
	var moving := false
	if is_boss:
		moving = _boss_ai(delta, dist, to_player)
	else:
		moving = _basic_ai(delta, dist, to_player)

	if not is_on_floor():
		velocity.y -= 24.0 * delta
	else:
		velocity.y = maxf(velocity.y, -1.0)

	move_and_slide()
	_update_hp_bar()

	# Procedural animation per species
	var t := Time.get_ticks_msec() / 1000.0
	var hover_offset := 0.35 + sin(t * 5.5) * 0.14 if monster_id in ["crimson_drake", "wraith"] else 0.0
	var bob := 0.0
	var sway := 0.0
	var lunge := 0.0
	if moving:
		bob = abs(sin(t * 10.0)) * 0.12
		sway = sin(t * 10.0) * 0.08
		model_holder.rotation.z = lerp(model_holder.rotation.z, sway, delta * 8.0)
		model_holder.rotation.x = lerp(model_holder.rotation.x, 0.08, delta * 8.0)
	else:
		bob = sin(t * 2.5) * 0.04
		model_holder.rotation.z = lerp(model_holder.rotation.z, 0.0, delta * 6.0)
		model_holder.rotation.x = lerp(model_holder.rotation.x, 0.0, delta * 6.0)
	if attack_anim > 0.0:
		lunge = sin(attack_anim * PI) * 0.45
		model_holder.rotation.x = lerp(model_holder.rotation.x, -0.35 * sin(attack_anim * PI), delta * 12.0)
	model_holder.position.y = hover_offset + bob
	model_holder.position.z = -lunge

func take_damage_and_report_crit(amount: float, attacker: Node3D, is_heavy: bool = false, knockback: float = 5.5, can_trigger_effects: bool = true) -> bool:
	var crit_chance := 0.1
	if is_instance_valid(attacker) and attacker.get("stats") != null:
		crit_chance = float(attacker.stats.get("crit_chance", 0.1))
	var is_crit := randf() < crit_chance
	_apply_damage_internal(amount, attacker, is_heavy, knockback, can_trigger_effects, is_crit)
	return is_crit

func take_damage(amount: float, attacker: Node3D, is_heavy: bool = false, knockback: float = 5.5, can_trigger_effects: bool = true) -> void:
	var crit_chance := 0.1
	if is_instance_valid(attacker) and attacker.get("stats") != null:
		crit_chance = float(attacker.stats.get("crit_chance", 0.1))
	var is_crit := randf() < crit_chance
	_apply_damage_internal(amount, attacker, is_heavy, knockback, can_trigger_effects, is_crit)

func _apply_damage_internal(amount: float, attacker: Node3D, _is_heavy: bool, knockback: float, can_trigger_effects: bool, is_crit: bool) -> void:
	if _dead or hp <= 0:
		return
	var final_dmg := amount
	if is_crit and is_instance_valid(attacker) and attacker.get("stats") != null:
		final_dmg *= float(attacker.stats.get("crit_mult", 1.85))
	final_dmg = max(1.0, round(final_dmg))
	hp -= int(final_dmg)
	hit_flash = 0.14
	_set_flash(true)

	# Boss Phase 2 check (< 50% HP)
	if is_boss and boss_phase == 1 and hp > 0 and hp <= int(max_hp * 0.5):
		_enter_boss_phase_two()

	# Floating damage text
	if is_instance_valid(attacker) and attacker.has_signal("floating_text_requested"):
		var slash_col: Color = Color("#facc15") if is_crit else Color("#e2e8f0")
		if not is_crit and attacker.get("current_tier") != null:
			slash_col = attacker.current_tier.get("slash_color", Color("#e2e8f0"))
		var txt := "¡%d!" % int(final_dmg) if is_crit else "%d" % int(final_dmg)
		attacker.floating_text_requested.emit(global_position + Vector3(0, 2.2 if not is_boss else 3.4, 0), txt, slash_col, is_crit)

	# Knockback (reduced for Golem & Boss)
	if is_instance_valid(attacker):
		var kb_resist := 0.35 if is_boss else (0.50 if monster_id in ["copper_golem", "troll"] else 1.0)
		var dir: Vector3 = global_position - attacker.global_position
		dir.y = 0
		dir = dir.normalized() if dir.length_squared() > 0.001 else Vector3.BACK
		knockback_vel = dir * knockback * kb_resist

	# Lifesteal & Hit SFX
	if is_instance_valid(attacker) and attacker.get("stats") != null:
		var loh := int(attacker.stats.get("life_on_hit", 0))
		if loh > 0 and attacker.player_hp > 0:
			attacker.player_hp = mini(attacker.player_max_hp, attacker.player_hp + loh)
			attacker.hp_changed.emit(attacker.player_hp, attacker.player_max_hp)
	if is_instance_valid(attacker) and attacker.has_method("play_sfx"):
		attacker.play_sfx("crit" if is_crit else "hit")

	# Chain lightning & bleed hooks
	if can_trigger_effects and is_instance_valid(attacker) and attacker.get("current_tier") != null:
		var eff := str(attacker.current_tier.get("special_effect", "none"))
		if eff == "bleed" and is_crit:
			bleed_timer = 3.0
		elif eff == "lightning" and is_inside_tree():
			_chain_lightning(attacker, final_dmg * 0.45, 3)

	if hp <= 0:
		_die(attacker)

func _enter_boss_phase_two() -> void:
	boss_phase = 2
	speed *= 1.22
	boss_phase_changed.emit(2)
	if is_instance_valid(player):
		if player.has_method("play_sfx"):
			player.play_sfx("boss", 1.08, 1.12)
		if player.has_signal("log_added"):
			player.log_added.emit("¡FURIA DEL ABISMO! ¡Malakor desata su Fase II!", "boss")
	_spawn_boss_entrance_vfx()

func apply_burn(dps: float, duration: float) -> void:
	burn_dps = max(burn_dps, dps)
	burn_timer = max(burn_timer, duration)

func apply_bleed(duration: float = 3.0) -> void:
	bleed_timer = max(bleed_timer, duration)

func _chain_lightning(attacker: Node3D, dmg: float, max_targets: int = 3) -> void:
	if not is_inside_tree():
		return
	var hit_ids: Dictionary = {get_instance_id(): true}
	var current: Node3D = self
	for _i in range(max_targets):
		var best: Node3D = null
		var best_d := 6.5
		for e in get_tree().get_nodes_in_group("enemies"):
			if not is_instance_valid(e) or e == current:
				continue
			var id := e.get_instance_id()
			if hit_ids.has(id):
				continue
			if e.hp <= 0 or e.get("_dead") == true:
				continue
			var d := current.global_position.distance_to(e.global_position)
			if d < best_d:
				best_d = d
				best = e
		if best == null:
			break
		hit_ids[best.get_instance_id()] = true
		_spawn_lightning_arc(current.global_position + Vector3.UP, best.global_position + Vector3.UP)
		if best.has_method("take_damage"):
			best.take_damage(dmg, attacker, false, 1.5, false)
		current = best

func _spawn_lightning_arc(from: Vector3, to: Vector3) -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	var mesh := ImmediateMesh.new()
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.5, 0.9, 1.0, 0.9)
	mat.emission_enabled = true
	mat.emission = Color(0.4, 0.8, 1.0)
	mat.emission_energy_multiplier = 3.0
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mi.material_override = mat
	get_tree().current_scene.add_child(mi)
	mesh.surface_begin(Mesh.PRIMITIVE_LINES, mat)
	mesh.surface_add_vertex(from)
	mesh.surface_add_vertex(to)
	mesh.surface_end()
	var tw := get_tree().current_scene.create_tween()
	tw.tween_property(mat, "albedo_color:a", 0.0, 0.2)
	tw.tween_callback(mi.queue_free)

func _die(attacker: Node3D) -> void:
	if _dead:
		return
	_dead = true
	hp = 0
	_clear_telegraph()

	var xp_gain := xp_reward
	var gold_gain := gold_reward
	var dropped_names: Array[String] = []

	if is_instance_valid(attacker) and attacker.has_method("gain_experience"):
		var xp_mult := float(attacker.stats.get("xp_mult", 1.0)) if attacker.get("stats") != null else 1.0
		var gold_mult := float(attacker.stats.get("gold_mult", 1.0)) if attacker.get("stats") != null else (1.0 + int(attacker.upgrades.get("soulMagnet", 0)) * 0.12)
		xp_gain = int(round(float(xp_reward) * xp_mult))
		gold_gain = int(round(float(gold_reward) * gold_mult))
		if is_boss:
			xp_gain = int(round(float(xp_gain) * 1.6))
			gold_gain = int(round(float(gold_gain) * 1.6))
			if "bosses_defeated" in attacker:
				attacker.bosses_defeated += 1
				if attacker.has_method("notify_boss_defeated"):
					attacker.notify_boss_defeated()

		# RPG Loot & Material Drops
		dropped_names = _grant_rpg_loot(attacker)

		attacker.gain_experience(xp_gain)
		attacker.add_gold(gold_gain)
		attacker.add_kill()

		if is_boss:
			if attacker.has_method("play_sfx"):
				attacker.play_sfx("boss_defeat", 1.0, 1.0)
			var loot_txt := (", Botín: " + ", ".join(dropped_names)) if not dropped_names.is_empty() else ""
			if attacker.has_signal("log_added"):
				attacker.log_added.emit(
					"¡JEFE DERROTADO! %s cayó. +%d EXP • +%d Oro%s" % [str(def.get("name", "Malakor")), xp_gain, gold_gain, loot_txt],
					"boss"
				)
			boss_defeated_reward.emit({
				"boss_name": str(def.get("name", "Malakor, Señor del Abismo")),
				"xp": xp_gain,
				"gold": gold_gain,
				"loot": dropped_names,
			})

	if is_inside_tree():
		_spawn_loot_orbs()
		if is_boss:
			_spawn_boss_defeat_vfx()
		queue_free()

func _grant_rpg_loot(attacker: Node3D) -> Array[String]:
	var obtained: Array[String] = []
	var mat_id := str(def.get("drop_material", ""))
	var chance := float(def.get("drop_chance", 0.55))
	if is_boss:
		if attacker.has_method("add_material"):
			attacker.add_material("corazon_abismo", 1)
			obtained.append("Corazón de Malakor")
		if attacker.has_method("add_consumable"):
			attacker.add_consumable("potion_hp", 1)
			attacker.add_consumable("elixir_xp", 1)
			obtained.append("Poción Vital + Elixir")
		if attacker.has_method("add_item"):
			var boss_relic := _pick_boss_relic_drop(attacker)
			if boss_relic != "":
				var added: bool = attacker.add_item(boss_relic)
				if added:
					var gd = attacker._get_gamedata() if attacker.has_method("_get_gamedata") else null
					var rname := str(gd.get_relic_by_id(boss_relic).get("name", boss_relic)) if gd else boss_relic
					obtained.append(rname)
	else:
		if mat_id != "" and randf() <= chance and attacker.has_method("add_material"):
			attacker.add_material(mat_id, 1)
			obtained.append(mat_id)
		if randf() < 0.16 and attacker.has_method("add_consumable"):
			attacker.add_consumable("potion_hp", 1)
		elif int(attacker.wave) >= 2 and randf() < 0.06 and attacker.has_method("add_consumable"):
			attacker.add_consumable("elixir_xp", 1)
		# Rare random relic drop (7% chance on regular monsters)
		if randf() < 0.07 and attacker.has_method("add_item"):
			var pool := ["grip_oak", "rune_wind", "relic_magnet", "grip_crusader", "rune_storm"]
			var pick: String = pool[randi() % pool.size()]
			attacker.add_item(pick)
	return obtained

func _pick_boss_relic_drop(attacker: Node3D) -> String:
	var priority := ["relic_malakor", "rune_void", "grip_draconic", "relic_chalice", "rune_storm", "grip_crusader"]
	if attacker.get("inventory_items") != null:
		for rid in priority:
			if not attacker.inventory_items.has(rid):
				return rid
	return "relic_malakor"

func _spawn_boss_defeat_vfx() -> void:
	var root := get_tree().current_scene
	if root == null:
		return
	for i in range(16):
		var orb := MeshInstance3D.new()
		var s := SphereMesh.new(); s.radius = 0.24; s.height = 0.48
		orb.mesh = s
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(1.0, 0.82, 0.22, 0.92) if i % 2 == 0 else Color(0.92, 0.35, 0.95, 0.92)
		mat.emission_enabled = true
		mat.emission = mat.albedo_color
		mat.emission_energy_multiplier = 4.2
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		orb.material_override = mat
		root.add_child(orb)
		orb.global_position = global_position + Vector3(0, 1.1, 0)
		var ang := TAU * float(i) / 16.0
		var target := orb.global_position + Vector3(cos(ang) * 4.8, randf_range(0.8, 3.2), sin(ang) * 4.8)
		var tw := root.create_tween()
		tw.tween_property(orb, "global_position", target, 0.85).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.85)
		tw.tween_callback(orb.queue_free)

func _spawn_loot_orbs() -> void:
	var root := get_tree().current_scene
	if root == null:
		return
	var count := 4 if is_boss else 2
	for i in range(count):
		var orb := MeshInstance3D.new()
		var s := SphereMesh.new()
		s.radius = 0.18
		s.height = 0.36
		orb.mesh = s
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color("#38bdf8") if i % 2 == 0 else Color("#facc15")
		mat.emission_enabled = true
		mat.emission = mat.albedo_color
		mat.emission_energy_multiplier = 2.2
		orb.material_override = mat
		root.add_child(orb)
		orb.global_position = global_position + Vector3(randf_range(-0.45, 0.45), 0.85, randf_range(-0.45, 0.45))
		var dest := player.global_position + Vector3(0, 1.2, 0) if is_instance_valid(player) else orb.global_position
		var tw := root.create_tween()
		tw.tween_property(orb, "global_position:y", 1.35, 0.18).set_trans(Tween.TRANS_QUAD)
		tw.tween_property(orb, "global_position", dest, 0.28).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		tw.tween_callback(orb.queue_free)

func _set_flash(active: bool) -> void:
	if model_holder == null:
		return
	for c in model_holder.get_children():
		if c is MeshInstance3D and c.material_override is StandardMaterial3D:
			var mat: StandardMaterial3D = c.material_override
			mat.emission_energy_multiplier = 2.5 if active else (1.1 if enraged else 0.35)
		elif c is Node3D:
			for sub in c.get_children():
				if sub is MeshInstance3D and sub.material_override is StandardMaterial3D:
					var smat: StandardMaterial3D = sub.material_override
					smat.emission_energy_multiplier = 2.5 if active else (1.1 if enraged else 0.25)

func _basic_ai(delta: float, dist: float, to_player: Vector3) -> bool:
	var dir := to_player.normalized() if dist > 0.001 else Vector3.FORWARD
	var move_speed := speed
	var want_dist := attack_range
	var moving := false

	match monster_id:
		"slime":
			move_speed = speed * 0.92
			if ai_timer <= 0.0 and is_on_floor() and dist < 8.5:
				velocity.y = 5.6
				ai_timer = randf_range(1.5, 2.6)
		"goblin":
			move_speed = speed * 1.15
			if dist < 4.4 and dist > attack_range:
				var side := Vector3(-dir.z, 0, dir.x) * float(circling)
				dir = (dir * 0.45 + side * 0.88).normalized()
				if ai_timer <= 0.0:
					circling *= -1
					ai_timer = randf_range(0.8, 1.5)
		"skeleton":
			if dist > 2.4 and dist < 6.2 and ai_timer <= 0.0:
				dash_dir = dir
				ai_timer = 1.45
				velocity.x = dash_dir.x * speed * 2.2
				velocity.z = dash_dir.z * speed * 2.2
				return true
			if ai_timer > 0.85:
				velocity.x = move_toward(velocity.x, 0.0, speed * 2.0 * delta)
				velocity.z = move_toward(velocity.z, 0.0, speed * 2.0 * delta)
				return velocity.length() > 0.2
		"copper_golem", "troll":
			move_speed = speed * 0.86
		"orc_berserker", "orc":
			if not enraged and hp <= int(max_hp * 0.5):
				enraged = true
				_set_flash(false)
			move_speed = speed * (1.35 if enraged else 0.98)
		"crimson_drake", "wraith":
			move_speed = speed * 1.08
			if dist < 10.5 and dist > 2.4 and ai_timer <= 0.0:
				dash_dir = dir
				ai_timer = 2.1
				velocity.x = dash_dir.x * speed * 2.65
				velocity.z = dash_dir.z * speed * 2.65
				return true
			if ai_timer > 1.55:
				return velocity.length() > 0.2
		_:
			pass

	if dist > want_dist:
		velocity.x = dir.x * move_speed
		velocity.z = dir.z * move_speed
		moving = true
		attack_anim = 0.0
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed * 6.0 * delta)
		velocity.z = move_toward(velocity.z, 0.0, speed * 6.0 * delta)
		var atk_rate := 1.3 if enraged else 1.0
		attack_cd -= delta * atk_rate
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
	return moving

func _boss_ai(delta: float, dist: float, to_player: Vector3) -> bool:
	boss_timer -= delta
	match boss_state:
		"chase":
			if dist > attack_range * 0.92:
				var dir := to_player.normalized() if dist > 0.001 else Vector3.FORWARD
				velocity.x = dir.x * speed
				velocity.z = dir.z * speed
			else:
				velocity.x = 0.0
				velocity.z = 0.0
				# Active melee cleave between special patterns
				attack_cd -= delta * (1.25 if boss_phase == 2 else 1.0)
				if attack_cd <= 0.0:
					attack_cd = attack_cooldown_def
					attack_anim = 0.01
			if attack_anim > 0.0:
				attack_anim += delta * 2.8
				if attack_anim >= 0.5 and (attack_anim - delta * 2.8) < 0.5:
					if dist <= attack_range + 0.8 and is_instance_valid(player) and player.has_method("take_player_damage"):
						player.take_player_damage(damage)
				if attack_anim >= 1.0:
					attack_anim = 0.0

			if boss_timer <= 0.0:
				attack_anim = 0.0
				var roll := randf()
				if boss_phase >= 2 and roll < 0.38:
					_start_boss_meteors()
				elif dist < 6.2 and roll < 0.72:
					_start_boss_slam()
				else:
					_start_boss_charge()
			return Vector2(velocity.x, velocity.z).length() > 0.1

		"telegraph_slam":
			velocity.x = 0.0; velocity.z = 0.0
			_update_telegraph_pulse()
			if boss_timer <= 0.0:
				_do_boss_slam()
			return false

		"telegraph_charge":
			velocity.x = 0.0; velocity.z = 0.0
			_update_telegraph_pulse()
			if boss_timer <= 0.0:
				boss_state = "charge"
				boss_timer = 0.48
				var dir := boss_target - global_position
				dir.y = 0
				boss_target = dir.normalized() if dir.length() >= 0.1 else Vector3.FORWARD
				_clear_telegraph()
			return false

		"charge":
			velocity.x = boss_target.x * speed * 3.1
			velocity.z = boss_target.z * speed * 3.1
			if boss_timer <= 0.0:
				boss_state = "recover"
				boss_timer = 1.0 if boss_phase == 2 else 1.2
				velocity.x = 0.0; velocity.z = 0.0
			elif dist < 2.6 and is_instance_valid(player) and player.has_method("take_player_damage"):
				player.take_player_damage(int(round(float(damage) * 1.25)))
				boss_state = "recover"
				boss_timer = 1.05
				velocity.x = 0.0; velocity.z = 0.0
			return Vector2(velocity.x, velocity.z).length() > 0.1

		"telegraph_meteor":
			velocity.x = 0.0; velocity.z = 0.0
			_update_telegraph_pulse()
			if boss_timer <= 0.0:
				_do_boss_meteors()
			return false

		"recover":
			velocity.x = 0.0; velocity.z = 0.0
			if boss_timer <= 0.0:
				boss_state = "chase"
				boss_timer = randf_range(1.3, 2.2) if boss_phase == 2 else randf_range(1.8, 3.0)
			return false
	return false

func _start_boss_slam() -> void:
	boss_state = "telegraph_slam"
	boss_timer = 0.82 if boss_phase == 2 else 0.95
	_spawn_telegraph(global_position, 4.4, Color(1.0, 0.18, 0.12, 0.38))

func _start_boss_charge() -> void:
	boss_state = "telegraph_charge"
	boss_timer = 0.65 if boss_phase == 2 else 0.78
	boss_target = player.global_position if is_instance_valid(player) else global_position + Vector3.FORWARD
	var to_t := boss_target - global_position
	to_t.y = 0
	var dir := to_t.normalized() if to_t.length() > 0.1 else Vector3.FORWARD
	_spawn_lane_telegraph(global_position, dir, 9.5, 2.2, Color(1.0, 0.55, 0.12, 0.36))

func _start_boss_meteors() -> void:
	boss_state = "telegraph_meteor"
	boss_timer = 0.92
	_clear_telegraph()
	boss_meteor_targets.clear()
	var base := player.global_position if is_instance_valid(player) else global_position
	for i in range(3):
		var ang := (float(i) / 3.0) * TAU + randf() * 0.5
		var r := 0.6 if i == 0 else 3.4
		var pt := base + Vector3(cos(ang) * r, 0, sin(ang) * r)
		pt.x = clampf(pt.x, -23.0, 23.0)
		pt.z = clampf(pt.z, -23.0, 23.0)
		boss_meteor_targets.append(pt)
		var tg := _make_telegraph_disc(pt, 2.35, Color(0.88, 0.22, 0.95, 0.38))
		if tg:
			boss_extra_telegraphs.append(tg)

func _do_boss_slam() -> void:
	_clear_telegraph()
	boss_state = "recover"
	boss_timer = 1.15 if boss_phase == 2 else 1.35
	if is_inside_tree() and get_tree().current_scene != null:
		var ring := MeshInstance3D.new()
		var torus := TorusMesh.new(); torus.inner_radius = 0.5; torus.outer_radius = 0.95
		ring.mesh = torus
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(1.0, 0.2, 0.1, 0.85)
		mat.emission_enabled = true; mat.emission = Color(1, 0.2, 0.1); mat.emission_energy_multiplier = 4.0
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		ring.material_override = mat
		get_tree().current_scene.add_child(ring)
		ring.global_position = Vector3(global_position.x, 0.1, global_position.z)
		var tw := get_tree().current_scene.create_tween()
		tw.tween_property(ring, "scale", Vector3(4.5, 1, 4.5), 0.35)
		tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.35)
		tw.tween_callback(ring.queue_free)
	if is_instance_valid(player) and global_position.distance_to(player.global_position) <= 4.5:
		if player.has_method("take_player_damage"):
			player.take_player_damage(int(round(float(damage) * 1.4)))

func _do_boss_meteors() -> void:
	var pts := boss_meteor_targets.duplicate()
	_clear_telegraph()
	boss_state = "recover"
	boss_timer = 1.15
	for pt in pts:
		if is_inside_tree() and get_tree().current_scene != null:
			var pillar := MeshInstance3D.new()
			var cyl := CylinderMesh.new()
			cyl.top_radius = 0.9; cyl.bottom_radius = 1.9; cyl.height = 5.5
			pillar.mesh = cyl
			var mat := StandardMaterial3D.new()
			mat.albedo_color = Color(0.92, 0.22, 0.95, 0.82)
			mat.emission_enabled = true; mat.emission = Color("#d946ef"); mat.emission_energy_multiplier = 4.2
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			pillar.material_override = mat
			get_tree().current_scene.add_child(pillar)
			pillar.global_position = Vector3(pt.x, 2.75, pt.z)
			var tw := get_tree().current_scene.create_tween()
			tw.tween_property(pillar, "scale", Vector3(1.25, 1.3, 1.25), 0.32)
			tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.32)
			tw.tween_callback(pillar.queue_free)
		if is_instance_valid(player) and Vector2(player.global_position.x - pt.x, player.global_position.z - pt.z).length() <= 2.35:
			if player.has_method("take_player_damage"):
				player.take_player_damage(int(round(float(damage) * 1.25)))

func _make_telegraph_disc(pos: Vector3, radius: float, color: Color) -> MeshInstance3D:
	if not is_inside_tree() or get_tree().current_scene == null:
		return null
	var disc := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = radius; cyl.bottom_radius = radius; cyl.height = 0.06
	disc.mesh = cyl
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.emission_enabled = true
	mat.emission = Color(color.r, color.g, color.b)
	mat.emission_energy_multiplier = 2.4
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	disc.material_override = mat
	get_tree().current_scene.add_child(disc)
	disc.global_position = Vector3(pos.x, 0.08, pos.z)
	return disc

func _spawn_telegraph(pos: Vector3, radius: float, color: Color) -> void:
	_clear_telegraph()
	boss_telegraph = _make_telegraph_disc(pos, radius, color)

func _spawn_lane_telegraph(origin: Vector3, dir: Vector3, length: float, width: float, color: Color) -> void:
	_clear_telegraph()
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	boss_telegraph = MeshInstance3D.new()
	var bx := BoxMesh.new()
	bx.size = Vector3(width, 0.06, length)
	boss_telegraph.mesh = bx
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.emission_enabled = true
	mat.emission = Color(color.r, color.g, color.b)
	mat.emission_energy_multiplier = 2.4
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	boss_telegraph.material_override = mat
	get_tree().current_scene.add_child(boss_telegraph)
	var center := origin + dir * (length * 0.5)
	boss_telegraph.global_position = Vector3(center.x, 0.08, center.z)
	boss_telegraph.rotation.y = atan2(dir.x, dir.z)

func _update_telegraph_pulse() -> void:
	var s := 1.0 + sin(Time.get_ticks_msec() / 70.0) * 0.06
	if boss_telegraph and is_instance_valid(boss_telegraph):
		boss_telegraph.scale = Vector3(s, 1, s)
	for tg in boss_extra_telegraphs:
		if tg and is_instance_valid(tg):
			tg.scale = Vector3(s, 1, s)

func _clear_telegraph() -> void:
	if boss_telegraph and is_instance_valid(boss_telegraph):
		boss_telegraph.queue_free()
	boss_telegraph = null
	for tg in boss_extra_telegraphs:
		if tg and is_instance_valid(tg):
			tg.queue_free()
	boss_extra_telegraphs.clear()

func _create_hp_bar() -> void:
	if hp_bar_bg and is_instance_valid(hp_bar_bg):
		hp_bar_bg.queue_free()
	hp_bar_bg = MeshInstance3D.new()
	var bg := BoxMesh.new()
	bg.size = Vector3(1.65 if is_boss else 1.2, 0.14 if is_boss else 0.11, 0.02)
	hp_bar_bg.mesh = bg
	var bgm := StandardMaterial3D.new()
	bgm.albedo_color = Color(0.06, 0.07, 0.11, 0.88)
	bgm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bgm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bgm.no_depth_test = true
	hp_bar_bg.material_override = bgm
	hp_bar_bg.position = Vector3(0, 3.6 if is_boss else 2.2, 0)
	add_child(hp_bar_bg)

	hp_bar_fill = MeshInstance3D.new()
	var fm := BoxMesh.new()
	fm.size = Vector3(1.58 if is_boss else 1.14, 0.09 if is_boss else 0.075, 0.03)
	hp_bar_fill.mesh = fm
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.95, 0.22, 0.28, 0.96) if is_boss else Color(0.22, 0.88, 0.38, 0.95)
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.no_depth_test = true
	hp_bar_fill.material_override = mat
	hp_bar_fill.position = Vector3(0, 0, 0.01)
	hp_bar_bg.add_child(hp_bar_fill)

func _update_hp_bar() -> void:
	if hp_bar_bg == null or not is_instance_valid(hp_bar_bg):
		return
	var ratio := clampf(float(hp) / float(maxi(1, max_hp)), 0.0, 1.0)
	hp_bar_bg.visible = hp < max_hp or is_boss
	if not hp_bar_bg.visible:
		return
	var half_w := 0.79 if is_boss else 0.57
	hp_bar_fill.scale.x = max(0.01, ratio)
	hp_bar_fill.position.x = -half_w * (1.0 - ratio)
	if is_boss and boss_phase == 2 and hp_bar_fill.material_override is StandardMaterial3D:
		(hp_bar_fill.material_override as StandardMaterial3D).albedo_color = Color("#e879f9")
	if is_inside_tree() and get_viewport():
		var cam := get_viewport().get_camera_3d()
		if cam:
			hp_bar_bg.look_at(cam.global_position, Vector3.UP, true)

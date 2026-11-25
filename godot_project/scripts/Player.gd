extends CharacterBody3D
class_name Player

signal hp_changed(current: int, max_hp: int)
signal xp_changed(current: int, required: int, level: int)
signal gold_changed(gold: int)
signal kills_changed(kills: int)
signal wave_changed(wave: int, wave_kills: int)
signal evolution_changed(tier: Dictionary)
signal log_added(text: String, kind: String)
signal cooldowns_changed(cds: Dictionary)

@export var move_speed: float = 8.2
@export var arena_radius: float = 25.5

var sword_level: int = 1
var current_xp: int = 0
var gold: int = 60
var kills: int = 0
var wave: int = 1
var wave_kills: int = 0
var player_max_hp: int = 220
var player_hp: int = 220

var upgrades := {
	"sharpness": 0, "swiftness": 0, "vampirism": 0,
	"criticalMastery": 0, "soulMagnet": 0, "bladeSize": 0
}

var cooldowns := {"whirlwind": 0.0, "swordWave": 0.0, "ultimate": 0.0, "dash": 0.0}
var cd_max := {"whirlwind": 4.0, "swordWave": 4.5, "ultimate": 10.0, "dash": 1.8}

var attack_cooldown: float = 0.0
var attack_anim: float = 0.0
var combo_step: int = 0
var whirlwind_timer: float = 0.0
var whirlwind_tick: float = 0.0
var dash_timer: float = 0.0
var dash_dir: Vector3 = Vector3.FORWARD
var auto_hunt: bool = false
var wielder_mode: String = "living_sword" # or knight_wielder

var current_tier: Dictionary
var stats: Dictionary

@onready var sword_pivot: Node3D = $SwordPivot
@onready var sword_mesh_holder: Node3D = $SwordPivot/SwordMeshHolder
@onready var knight_holder: Node3D = $KnightHolder
@onready var aura_light: OmniLight3D = $AuraLight
@onready var slash_ring: MeshInstance3D = $SlashRing

func _ready() -> void:
	current_tier = GameData.get_sword_for_level(sword_level)
	_recalc_stats()
	_refresh_sword_visual()
	_emit_all()

func _physics_process(delta: float) -> void:
	_tick_cooldowns(delta)
	_handle_movement(delta)
	_handle_combat(delta)
	_update_sword_anim(delta)

func _tick_cooldowns(delta: float) -> void:
	for k in cooldowns.keys():
		if cooldowns[k] > 0.0:
			cooldowns[k] = max(0.0, cooldowns[k] - delta)
	if attack_cooldown > 0.0:
		attack_cooldown = max(0.0, attack_cooldown - delta)
	if attack_anim > 0.0:
		attack_anim = max(0.0, attack_anim - delta)
	if dash_timer > 0.0:
		dash_timer = max(0.0, dash_timer - delta)
	cooldowns_changed.emit(cooldowns)

func _handle_movement(delta: float) -> void:
	var input_dir := Vector3.ZERO
	if Input.is_action_pressed("move_forward"):
		input_dir.z -= 1.0
	if Input.is_action_pressed("move_back"):
		input_dir.z += 1.0
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1.0
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1.0

	var moving := false
	if dash_timer > 0.0:
		velocity = dash_dir * 24.0
		moving = true
	elif input_dir.length_squared() > 0.001:
		input_dir = input_dir.normalized()
		var target_angle := atan2(input_dir.x, input_dir.z)
		rotation.y = lerp_angle(rotation.y, target_angle, 12.0 * delta)
		velocity = input_dir * move_speed
		moving = true
	elif auto_hunt:
		var target := _find_nearest_enemy()
		if target:
			var to_t: Vector3 = target.global_position - global_position
			to_t.y = 0
			var dist := to_t.length()
			if dist > 0.05:
				rotation.y = lerp_angle(rotation.y, atan2(to_t.x, to_t.z), 10.0 * delta)
			if dist > float(stats["range"]) * 0.72:
				velocity = to_t.normalized() * 7.6
				moving = true
			else:
				velocity = Vector3.ZERO
				perform_attack()
				if cooldowns["whirlwind"] <= 0.0: perform_skill("whirlwind")
				elif cooldowns["swordWave"] <= 0.0: perform_skill("wave")
		else:
			velocity = Vector3.ZERO
	else:
		velocity.x = move_toward(velocity.x, 0, move_speed)
		velocity.z = move_toward(velocity.z, 0, move_speed)

	if not moving and dash_timer <= 0.0 and not (auto_hunt and _find_nearest_enemy()):
		velocity.x = move_toward(velocity.x, 0, move_speed * 4.0 * delta)
		velocity.z = move_toward(velocity.z, 0, move_speed * 4.0 * delta)

	move_and_slide()
	# Clamp to arena
	var flat := Vector2(global_position.x, global_position.z)
	if flat.length() > arena_radius:
		flat = flat.normalized() * arena_radius
		global_position.x = flat.x
		global_position.z = flat.y

func _handle_combat(delta: float) -> void:
	if Input.is_action_just_pressed("attack"):
		_aim_at_mouse()
		perform_attack()
	if Input.is_action_just_pressed("skill_whirlwind"):
		perform_skill("whirlwind")
	if Input.is_action_just_pressed("skill_wave"):
		perform_skill("wave")
	if Input.is_action_just_pressed("skill_ultimate"):
		perform_skill("ultimate")
	if Input.is_action_just_pressed("skill_dash"):
		perform_skill("dash")

	if whirlwind_timer > 0.0:
		whirlwind_timer = max(0.0, whirlwind_timer - delta)
		whirlwind_tick += delta
		sword_pivot.rotation.y += 24.0 * delta
		if whirlwind_tick >= 0.22:
			whirlwind_tick = 0.0
			_spawn_shockwave(global_position, current_tier["slash_color"], float(stats["range"]) * 1.2)
			_deal_aoe_damage(float(stats["range"]) * 1.25, float(stats["damage"]) * 0.75, 4.0)

func _aim_at_mouse() -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var mouse_pos := get_viewport().get_mouse_position()
	var from := cam.project_ray_origin(mouse_pos)
	var dir := cam.project_ray_normal(mouse_pos)
	var plane := Plane(Vector3.UP, 0.0)
	var hit = plane.intersects_ray(from, dir)
	if hit:
		var to_hit: Vector3 = hit - global_position
		to_hit.y = 0
		if to_hit.length() > 0.2:
			rotation.y = atan2(to_hit.x, to_hit.z)

func perform_attack() -> void:
	if attack_cooldown > 0.0:
		return
	var atk_speed := float(stats["attack_speed"])
	attack_cooldown = 0.42 / max(0.1, atk_speed)
	attack_anim = 0.28
	combo_step = (combo_step + 1) % 3
	_show_slash()
	_apply_melee_damage()

func perform_skill(skill: String) -> void:
	if cooldowns.get(skill, 0.0) > 0.0:
		return
	match skill:
		"whirlwind":
			cooldowns["whirlwind"] = cd_max["whirlwind"]
			whirlwind_timer = 1.1
			whirlwind_tick = 0.0
			_spawn_shockwave(global_position, current_tier["aura_color"], float(stats["range"]) * 1.4)
			log_added.emit("¡Torbellino desatado!", "skill")
		"wave":
			cooldowns["swordWave"] = cd_max["swordWave"]
			_spawn_wave_projectile()
			_spawn_shockwave(global_position + Vector3(sin(rotation.y),0,cos(rotation.y))*1.5, current_tier["slash_color"], 3.0)
			log_added.emit("¡Onda Cortante lanzada!", "skill")
		"ultimate":
			cooldowns["ultimate"] = cd_max["ultimate"]
			_spawn_ultimate_swords()
			_spawn_shockwave(global_position, current_tier["aura_color"], 6.0)
			log_added.emit("¡Lluvia de Espadas Celestiales!", "skill")
		"dash":
			cooldowns["dash"] = cd_max["dash"]
			dash_timer = 0.22
			dash_dir = Vector3(sin(rotation.y), 0, cos(rotation.y))
	cooldowns_changed.emit(cooldowns)

func _apply_melee_damage() -> void:
	var dmg := float(stats["damage"])
	var rng := float(stats["range"])
	var combo_mult := 1.35 if combo_step == 2 else 1.0
	var forward := Vector3(sin(rotation.y), 0, cos(rotation.y))
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy):
			continue
		var to_e: Vector3 = enemy.global_position - global_position
		to_e.y = 0
		var dist := to_e.length()
		var hit_radius: float = rng + (1.3 if enemy.is_boss else 0.75)
		if dist <= hit_radius:
			var dot := forward.dot(to_e.normalized()) if dist > 0.001 else 1.0
			if combo_step == 2 or dist < 2.2 or dot > -0.35:
				enemy.take_damage(dmg * combo_mult, self, combo_step == 2)

func _deal_aoe_damage(radius: float, dmg: float, knockback: float) -> void:
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy):
			continue
		var dist := global_position.distance_to(enemy.global_position)
		if dist <= radius:
			enemy.take_damage(dmg, self, false, knockback)

func _spawn_wave_projectile() -> void:
	var CG = load("res://scripts/CustomGeometry.gd")
	var scene_root := get_tree().current_scene
	var proj := Node3D.new()
	proj.name = "SwordWave"
	var mesh_inst := MeshInstance3D.new()
	mesh_inst.mesh = CG.create_crescent_wave(2.3, 0.85)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(current_tier["slash_color"], 0.95)
	mat.emission_enabled = true
	mat.emission = current_tier["slash_color"]
	mat.emission_energy_multiplier = 3.0
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	mesh_inst.material_override = mat
	proj.add_child(mesh_inst)
	scene_root.add_child(proj)
	proj.global_position = global_position + Vector3(0, 1.3, 0)
	proj.rotation.y = rotation.y
	var script := preload("res://scripts/SwordWave.gd")
	proj.set_script(script)
	proj.setup(Vector3(sin(rotation.y), 0, cos(rotation.y)) * 20.0, float(stats["damage"]) * 1.9, self)

func _spawn_ultimate_swords() -> void:
	var SwordBuilderScript = load("res://scripts/SwordBuilder.gd")
	var scene_root := get_tree().current_scene
	for i in range(7):
		var angle := (float(i) / 7.0) * TAU
		var dist := 2.5 if i == 0 else 5.2
		var target := global_position + Vector3(sin(angle) * dist, 0, cos(angle) * dist)
		var node := Node3D.new()
		node.name = "SkySword_%d" % i
		var sword_visual: Node3D = SwordBuilderScript.build_sword(str(current_tier["id"]), sword_level)
		sword_visual.scale = Vector3.ONE * 1.6
		# Point blade downward
		sword_visual.rotation.z = PI
		node.add_child(sword_visual)
		scene_root.add_child(node)
		node.global_position = target + Vector3(0, 18.0 + i * 2.2, 0)
		var script := preload("res://scripts/SkySword.gd")
		node.set_script(script)
		node.setup(target, float(stats["damage"]) * 2.5, self, float(i) * 0.08)

func take_player_damage(amount: int) -> void:
	if dash_timer > 0.0:
		return
	player_hp -= amount
	if player_hp <= 0:
		player_hp = player_max_hp
		global_position = Vector3.ZERO
		log_added.emit("¡La Forja Ancestral ha restaurado tu energía vital!", "upgrade")
	hp_changed.emit(player_hp, player_max_hp)

func gain_experience(amount: int) -> void:
	current_xp += amount
	var required := GameData.get_xp_required(sword_level)
	var old_tier := current_tier
	var leveled := false
	while current_xp >= required:
		current_xp -= required
		sword_level += 1
		required = GameData.get_xp_required(sword_level)
		leveled = true
	if leveled:
		player_max_hp = 220 + (sword_level - 1) * 28
		player_hp = player_max_hp
		current_tier = GameData.get_sword_for_level(sword_level)
		_recalc_stats()
		_refresh_sword_visual()
		var evolved := str(current_tier["id"]) != str(old_tier["id"])
		if evolved:
			log_added.emit("¡METAMORFOSIS AL NIVEL %d! Tu espada ha evolucionado a %s." % [sword_level, str(current_tier["name"]).to_upper()], "evolution")
			evolution_changed.emit(current_tier)
		else:
			log_added.emit("¡Tu espada subió al Nivel %d! El filo y poder aumentan." % sword_level, "levelup")
		hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, GameData.get_xp_required(sword_level), sword_level)

func add_gold(amount: int) -> void:
	gold += amount
	gold_changed.emit(gold)

func add_kill() -> void:
	kills += 1
	wave_kills += 1
	kills_changed.emit(kills)
	if wave_kills >= 8:
		wave_kills = 0
		wave += 1
		wave_changed.emit(wave, wave_kills)
		log_added.emit("¡Oleada %d iniciada! Monstruos más fuertes emergen." % wave, "boss")
	else:
		wave_changed.emit(wave, wave_kills)

func buy_upgrade(key: String, base_cost: int) -> bool:
	if not upgrades.has(key):
		return false
	var lvl: int = int(upgrades[key])
	var cost := int(round(base_cost * pow(1.45, lvl)))
	if gold < cost:
		return false
	gold -= cost
	upgrades[key] = lvl + 1
	_recalc_stats()
	if key == "bladeSize":
		_refresh_sword_visual()
	gold_changed.emit(gold)
	log_added.emit("Mejora forjada: %s Nv.%d" % [key, lvl + 1], "upgrade")
	return true

func jump_to_level(target_level: int) -> void:
	var old_tier := current_tier
	sword_level = max(1, target_level)
	current_xp = 0
	player_max_hp = 220 + (sword_level - 1) * 28
	player_hp = player_max_hp
	current_tier = GameData.get_sword_for_level(sword_level)
	_recalc_stats()
	_refresh_sword_visual()
	var evolved := str(current_tier["id"]) != str(old_tier["id"])
	if evolved:
		log_added.emit("¡EVOLUCIÓN ACTIVADA (Nivel %d): %s!" % [sword_level, str(current_tier["name"])], "evolution")
		evolution_changed.emit(current_tier)
	else:
		log_added.emit("Nivel de la espada ajustado a Nivel %d." % sword_level, "levelup")
	hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, GameData.get_xp_required(sword_level), sword_level)

func toggle_auto_hunt() -> void:
	auto_hunt = not auto_hunt

func toggle_wielder_mode() -> void:
	wielder_mode = "knight_wielder" if wielder_mode == "living_sword" else "living_sword"
	_refresh_sword_visual()

func _recalc_stats() -> void:
	current_tier = GameData.get_sword_for_level(sword_level)
	var level_bonus := 1.0 + (sword_level - int(current_tier["min_level"])) * 0.14
	var sharp_mult := 1.0 + int(upgrades["sharpness"]) * 0.18
	var dmg := int(round(float(current_tier["base_damage"]) * level_bonus * sharp_mult))
	var atk_speed := float(current_tier["attack_speed"]) * (1.0 + int(upgrades["swiftness"]) * 0.08)
	var crit: float = minf(0.95, float(current_tier["crit_chance"]) + int(upgrades["criticalMastery"]) * 0.04)
	var crit_mult := 1.85 + int(upgrades["criticalMastery"]) * 0.15 + (0.65 if str(current_tier["id"]) == "celestial" else 0.0)
	var rng := float(current_tier["range"]) * (1.0 + int(upgrades["bladeSize"]) * 0.06)
	var life_on_hit := int(upgrades["vampirism"]) * 3 + (14 if str(current_tier["id"]) == "obsidian" else 0)
	var xp_mult := 1.0 + int(upgrades["soulMagnet"]) * 0.15 + (0.15 if str(current_tier["id"]) == "wood" else 0.0)
	stats = {
		"damage": dmg, "attack_speed": atk_speed, "crit_chance": crit,
		"crit_mult": crit_mult, "range": rng, "life_on_hit": life_on_hit, "xp_mult": xp_mult
	}

func _refresh_sword_visual() -> void:
	for c in sword_mesh_holder.get_children():
		c.queue_free()
	var SwordBuilderScript = load("res://scripts/SwordBuilder.gd")
	var built: Node3D = SwordBuilderScript.build_sword(str(current_tier["id"]), sword_level)
	var blade_pivot_node: Node3D = built.get_node_or_null("BladePivot")
	var scale_mult := 1.0 + int(upgrades["bladeSize"]) * 0.06
	var base_scale := (0.88 * scale_mult) if wielder_mode == "knight_wielder" else (1.12 * scale_mult)
	if blade_pivot_node:
		for child in blade_pivot_node.get_children():
			blade_pivot_node.remove_child(child)
			sword_mesh_holder.add_child(child)
			child.scale = child.scale * base_scale
	else:
		sword_mesh_holder.add_child(built)
		built.scale = Vector3.ONE * base_scale
	built.queue_free()
	# knight visibility
	knight_holder.visible = wielder_mode == "knight_wielder"
	if wielder_mode == "knight_wielder":
		sword_pivot.position = Vector3(0.6, 1.2, 0.3)
	else:
		sword_pivot.position = Vector3(0, 1.55, 0)
	aura_light.light_color = current_tier["aura_color"]
	slash_ring.visible = false

func _update_sword_anim(delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	var moving := Vector2(velocity.x, velocity.z).length() > 0.5
	var speed_factor: float = clamp(Vector2(velocity.x, velocity.z).length() / move_speed, 0.0, 1.5)

	# Base bob/lean
	var bob: float = sin(t * (8.0 if moving else 2.8)) * (0.08 if moving else 0.04)
	var lean: float = 0.0
	if moving:
		lean = clamp(speed_factor * 0.22, 0.0, 0.28)

	if wielder_mode == "living_sword":
		var base_y := 1.55 + (sin(t * 3.5) * 0.18 if whirlwind_timer <= 0.0 else 0.0)
		sword_pivot.position.y = lerp(sword_pivot.position.y, base_y + bob, delta * 8.0)
		sword_pivot.rotation.x = lerp_angle(sword_pivot.rotation.x, lean, delta * 8.0)
		sword_pivot.position.x = lerp(sword_pivot.position.x, 0.0, delta * 8.0)
		knight_holder.position.y = lerp(knight_holder.position.y, 0.0, delta * 8.0)
	else:
		sword_pivot.position.y = lerp(sword_pivot.position.y, 1.2 + bob * 0.5, delta * 8.0)
		sword_pivot.position.x = lerp(sword_pivot.position.x, 0.6, delta * 8.0)
		sword_pivot.rotation.x = lerp_angle(sword_pivot.rotation.x, lean * 0.5, delta * 8.0)
		knight_holder.position.y = lerp(knight_holder.position.y, bob * 0.35, delta * 8.0)
		knight_holder.rotation.x = lerp_angle(knight_holder.rotation.x, lean * 0.6, delta * 8.0)

	if dash_timer > 0.0:
		sword_mesh_holder.rotation.x = lerp_angle(sword_mesh_holder.rotation.x, 1.25, delta * 16.0)
		sword_mesh_holder.rotation.z = lerp_angle(sword_mesh_holder.rotation.z, 0.0, delta * 16.0)
		sword_mesh_holder.rotation.y = lerp_angle(sword_mesh_holder.rotation.y, 0.0, delta * 16.0)
		sword_pivot.rotation.x = lerp_angle(sword_pivot.rotation.x, 0.55, delta * 12.0)
		sword_pivot.position.z = lerp(sword_pivot.position.z, -0.35, delta * 12.0)
	elif whirlwind_timer > 0.0:
		sword_mesh_holder.rotation.x = lerp_angle(sword_mesh_holder.rotation.x, PI * 0.46, delta * 14.0)
		sword_mesh_holder.rotation.z = lerp_angle(sword_mesh_holder.rotation.z, 0.0, delta * 14.0)
		sword_mesh_holder.rotation.y += delta * 28.0
		sword_pivot.rotation.y += delta * 18.0
	elif attack_anim > 0.0:
		var p: float = 1.0 - (attack_anim / 0.28)
		var windup: float = smoothstep(0.0, 0.25, p)
		var swing: float = smoothstep(0.25, 0.75, p)
		var recover: float = smoothstep(0.75, 1.0, p)
		if combo_step == 0:
			# Right-to-left horizontal slash
			var ang: float = lerp(-1.55, 1.55, swing) - windup * 0.3 + recover * 0.1
			sword_mesh_holder.rotation.z = ang
			sword_mesh_holder.rotation.x = lerp(0.55, 1.05, sin(p * PI))
			sword_mesh_holder.rotation.y = lerp(-0.35, 0.35, swing)
			sword_pivot.rotation.y = lerp(sword_pivot.rotation.y, -0.25 + swing * 0.5, delta * 10.0)
		elif combo_step == 1:
			# Left-to-right horizontal slash
			var ang2: float = lerp(1.55, -1.55, swing) + windup * 0.3 - recover * 0.1
			sword_mesh_holder.rotation.z = ang2
			sword_mesh_holder.rotation.x = lerp(0.55, 1.0, sin(p * PI))
			sword_mesh_holder.rotation.y = lerp(0.35, -0.35, swing)
			sword_pivot.rotation.y = lerp(sword_pivot.rotation.y, 0.25 - swing * 0.5, delta * 10.0)
		else:
			# Overhead slam
			sword_mesh_holder.rotation.x = lerp(-1.15, 1.75, swing) - windup * 0.4
			sword_mesh_holder.rotation.z = lerp(0.0, 0.15, sin(p * PI))
			sword_mesh_holder.rotation.y = 0.0
			sword_pivot.position.y += sin(p * PI) * 0.03
		# small lunge feel
		sword_pivot.position.z = lerp(sword_pivot.position.z, -sin(p * PI) * 0.25, delta * 12.0)
	else:
		var idle_x := 0.22 if wielder_mode == "living_sword" else 0.35
		sword_mesh_holder.rotation.x = lerp_angle(sword_mesh_holder.rotation.x, idle_x, delta * 10.0)
		sword_mesh_holder.rotation.z = lerp_angle(sword_mesh_holder.rotation.z, sin(t * 2.8) * 0.12, delta * 10.0)
		sword_mesh_holder.rotation.y = lerp_angle(sword_mesh_holder.rotation.y, sin(t * 1.6) * 0.06, delta * 8.0)
		sword_pivot.rotation.y = lerp_angle(sword_pivot.rotation.y, 0.0, delta * 8.0)
		sword_pivot.position.z = lerp(sword_pivot.position.z, 0.0, delta * 8.0)

	# slash ring fade
	if slash_ring.visible:
		var mat: StandardMaterial3D = slash_ring.material_override
		if mat:
			mat.albedo_color.a = max(0.0, mat.albedo_color.a - delta * 4.0)
			if mat.albedo_color.a <= 0.01:
				slash_ring.visible = false

func _spawn_shockwave(pos: Vector3, color: Color, max_radius: float = 4.0) -> void:
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.3
	torus.outer_radius = 0.6
	ring.mesh = torus
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(color, 0.85)
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 2.5
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	ring.material_override = mat
	get_tree().current_scene.add_child(ring)
	ring.global_position = Vector3(pos.x, 0.08, pos.z)
	var tw := get_tree().current_scene.create_tween()
	tw.tween_property(ring, "scale", Vector3(max_radius, 1.0, max_radius), 0.3)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.3)
	tw.tween_callback(ring.queue_free)

func _show_slash() -> void:
	var CG = load("res://scripts/CustomGeometry.gd")
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(current_tier["slash_color"], 0.9)
	mat.emission_enabled = true
	mat.emission = current_tier["slash_color"]
	mat.emission_energy_multiplier = 3.0
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	slash_ring.material_override = mat
	var crescent = CG.create_crescent_wave(float(stats["range"]) * 0.85, 1.1)
	slash_ring.mesh = crescent
	slash_ring.visible = true
	# Orient slash by combo step for web-like feel
	if combo_step == 0:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, -0.35)
	elif combo_step == 1:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, 0.35)
	else:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, PI * 0.5)
	slash_ring.position = Vector3(0, 1.25, 0.0)
	slash_ring.scale = Vector3(1.0, 1.0, 1.0)

func _find_nearest_enemy() -> Node3D:
	var nearest: Node3D = null
	var best := INF
	for e in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(e):
			continue
		var d := global_position.distance_to(e.global_position)
		if d < best:
			best = d
			nearest = e
	return nearest

func _emit_all() -> void:
	hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, GameData.get_xp_required(sword_level), sword_level)
	gold_changed.emit(gold)
	kills_changed.emit(kills)
	wave_changed.emit(wave, wave_kills)

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
signal player_died()
signal inventory_changed()
signal floating_text_requested(world_pos: Vector3, text: String, color: Color, is_big: bool)

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
var bosses_defeated: int = 0

var upgrades := {
	"sharpness": 0, "swiftness": 0, "vampirism": 0,
	"criticalMastery": 0, "soulMagnet": 0, "bladeSize": 0
}

# RPG Inventory & Relic Equipment
var materials: Dictionary = {}
var inventory_items: Array = []
var equipped := {"grip": "", "rune": "", "relic": ""}
var consumables := {"potion_hp": 2, "elixir_xp": 0}

var cooldowns := {"whirlwind": 0.0, "swordWave": 0.0, "ultimate": 0.0, "dash": 0.0}
var cd_max := {"whirlwind": 4.0, "swordWave": 4.5, "ultimate": 10.0, "dash": 1.8}

var attack_cooldown: float = 0.0
var attack_anim: float = 0.0
var combo_step: int = 0
var copper_hit_counter: int = 0
var whirlwind_timer: float = 0.0
var whirlwind_tick: float = 0.0
var dash_timer: float = 0.0

var _sfx_player: AudioStreamPlayer
var _sfx := {}
var _gd_fallback: Node = null
var dash_dir: Vector3 = Vector3.FORWARD
var auto_hunt: bool = false
var wielder_mode: String = "living_sword" # or knight_wielder
var crystal_shard_timer: float = 0.0
var gold_regen_timer: float = 0.0
var celestial_nova_timer: float = 0.0
var is_dead: bool = false
var invuln_timer: float = 0.0
var _potion_key_was_down: bool = false

var current_tier: Dictionary
var stats: Dictionary

@onready var sword_pivot: Node3D = get_node_or_null("SwordPivot")
@onready var sword_mesh_holder: Node3D = get_node_or_null("SwordPivot/SwordMeshHolder")
@onready var knight_holder: Node3D = get_node_or_null("KnightHolder")
@onready var aura_light: OmniLight3D = get_node_or_null("AuraLight")
@onready var slash_ring: MeshInstance3D = get_node_or_null("SlashRing")
var ground_aura_ring: MeshInstance3D

func _get_gamedata() -> Node:
	if is_inside_tree():
		var gd := get_node_or_null("/root/GameData")
		if gd != null:
			return gd
	if _gd_fallback == null:
		_gd_fallback = load("res://scripts/GameData.gd").new()
	return _gd_fallback

func _exit_tree() -> void:
	if _sfx_player != null and is_instance_valid(_sfx_player):
		_sfx_player.stop()
		_sfx_player.stream = null
	if _gd_fallback != null and is_instance_valid(_gd_fallback):
		_gd_fallback.free()
		_gd_fallback = null

func _ready() -> void:
	var gd := _get_gamedata()
	current_tier = gd.get_sword_for_level(sword_level)
	_ensure_ground_aura_ring()
	_recalc_stats()
	player_hp = player_max_hp
	_refresh_sword_visual()
	_init_sfx()
	_emit_all()

func _ensure_ground_aura_ring() -> void:
	if ground_aura_ring != null:
		return
	ground_aura_ring = MeshInstance3D.new()
	ground_aura_ring.name = "GroundAuraRing"
	var torus := TorusMesh.new()
	torus.inner_radius = 1.12
	torus.outer_radius = 1.30
	torus.ring_segments = 32
	torus.rings = 8
	ground_aura_ring.mesh = torus
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.52, 0.94, 0.67, 0.72)
	mat.emission_enabled = true
	mat.emission = Color("#86efac")
	mat.emission_energy_multiplier = 1.8
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ground_aura_ring.material_override = mat
	ground_aura_ring.position = Vector3(0, 0.05, 0)
	add_child(ground_aura_ring)

func _physics_process(delta: float) -> void:
	if invuln_timer > 0.0:
		invuln_timer = max(0.0, invuln_timer - delta)
	if is_dead:
		velocity = Vector3.ZERO
		move_and_slide()
		return
	_tick_cooldowns(delta)
	_handle_movement(delta)
	_handle_combat(delta)
	_process_sword_effects(delta)
	_update_sword_anim(delta)

func _init_sfx() -> void:
	_sfx_player = AudioStreamPlayer.new()
	_sfx_player.name = "SFXPlayer"
	add_child(_sfx_player)
	for k in ["hit", "crit", "swing", "skill_q", "skill_e", "skill_r", "dash", "levelup", "evolution", "upgrade", "loot", "boss", "boss_defeat", "player_hurt", "gameover", "ui"]:
		var p := "res://assets/audio/%s.wav" % k
		if ResourceLoader.exists(p):
			_sfx[k] = load(p)

func play_sfx(sfx_name: String, pitch_min: float = 0.96, pitch_max: float = 1.04) -> void:
	if is_inside_tree():
		var am := get_node_or_null("/root/AudioManager")
		if am and am.has_method("play_sfx"):
			am.play_sfx(sfx_name, pitch_min, pitch_max)
			return
	if _sfx_player == null or not _sfx.has(sfx_name):
		return
	_sfx_player.stream = _sfx[sfx_name]
	_sfx_player.pitch_scale = randf_range(pitch_min, pitch_max)
	_sfx_player.play()

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
				if cooldowns["whirlwind"] <= 0.0:
					perform_skill("whirlwind")
				elif cooldowns["swordWave"] <= 0.0:
					perform_skill("swordWave")
		else:
			velocity = Vector3.ZERO
	else:
		velocity.x = move_toward(velocity.x, 0, move_speed)
		velocity.z = move_toward(velocity.z, 0, move_speed)

	if not moving and dash_timer <= 0.0 and not (auto_hunt and _find_nearest_enemy()):
		velocity.x = move_toward(velocity.x, 0, move_speed * 4.0 * delta)
		velocity.z = move_toward(velocity.z, 0, move_speed * 4.0 * delta)

	move_and_slide()
	var flat := Vector2(global_position.x, global_position.z)
	if flat.length() > arena_radius:
		flat = flat.normalized() * arena_radius
		global_position.x = flat.x
		global_position.z = flat.y

func _handle_combat(delta: float) -> void:
	if Input.is_action_just_pressed("attack"):
		var hovered := get_viewport().gui_get_hovered_control() if get_viewport() else null
		if hovered == null:
			_aim_at_mouse()
			perform_attack()
	if Input.is_action_just_pressed("skill_whirlwind"):
		perform_skill("whirlwind")
	if Input.is_action_just_pressed("skill_wave"):
		perform_skill("swordWave")
	if Input.is_action_just_pressed("skill_ultimate"):
		perform_skill("ultimate")
	if Input.is_action_just_pressed("skill_dash"):
		perform_skill("dash")

	var h_down := Input.is_physical_key_pressed(KEY_H)
	if h_down and not _potion_key_was_down:
		use_consumable("potion_hp")
	_potion_key_was_down = h_down

	if whirlwind_timer > 0.0:
		whirlwind_timer = max(0.0, whirlwind_timer - delta)
		whirlwind_tick += delta
		if sword_pivot:
			sword_pivot.rotation.y += 24.0 * delta
		if whirlwind_tick >= 0.22:
			whirlwind_tick = 0.0
			_spawn_shockwave(global_position, current_tier["slash_color"], float(stats["range"]) * 1.2)
			_deal_aoe_damage(float(stats["range"]) * 1.25, float(stats["damage"]) * 0.75, 4.0)

func _aim_at_mouse() -> void:
	if not is_inside_tree() or get_viewport() == null:
		return
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
	if attack_cooldown > 0.0 or is_dead:
		return
	var atk_speed := float(stats["attack_speed"])
	attack_cooldown = 0.42 / max(0.1, atk_speed)
	attack_anim = 0.28
	combo_step = (combo_step + 1) % 3
	var pitch_base := 0.92 + float(combo_step) * 0.08
	play_sfx("swing", pitch_base, pitch_base + 0.04)
	_show_slash()
	_apply_melee_damage()

func _canonical_skill(skill: String) -> String:
	match skill:
		"wave":
			return "swordWave"
		_:
			return skill

func get_effective_cd_max(skill: String) -> float:
	skill = _canonical_skill(skill)
	var base: float = float(cd_max.get(skill, 4.0))
	var cdr: float = clampf(float(stats.get("cd_reduction", 0.0)), 0.0, 0.45)
	return maxf(0.4, base * (1.0 - cdr))

func perform_skill(skill: String) -> void:
	if is_dead:
		return
	skill = _canonical_skill(skill)
	if cooldowns.get(skill, 0.0) > 0.0:
		return
	var eff_cd := get_effective_cd_max(skill)
	match skill:
		"whirlwind":
			cooldowns["whirlwind"] = eff_cd
			whirlwind_timer = 1.1
			whirlwind_tick = 0.0
			_spawn_shockwave(global_position, current_tier["aura_color"], float(stats["range"]) * 1.4)
			play_sfx("skill_q")
			log_added.emit("¡Torbellino desatado!", "skill")
		"swordWave":
			cooldowns["swordWave"] = eff_cd
			_spawn_wave_projectile()
			_spawn_shockwave(global_position + Vector3(sin(rotation.y), 0, cos(rotation.y)) * 1.5, current_tier["slash_color"], 3.0)
			play_sfx("skill_e")
			log_added.emit("¡Onda Cortante lanzada!", "skill")
		"ultimate":
			cooldowns["ultimate"] = eff_cd
			_spawn_ultimate_swords()
			_spawn_shockwave(global_position, current_tier["aura_color"], 6.0)
			play_sfx("skill_r")
			log_added.emit("¡Lluvia de Espadas Celestiales!", "skill")
		"dash":
			cooldowns["dash"] = eff_cd
			dash_timer = 0.22
			invuln_timer = maxf(invuln_timer, 0.25)
			dash_dir = Vector3(sin(rotation.y), 0, cos(rotation.y))
			_spawn_shockwave(global_position, Color("#38bdf8"), 2.4)
			play_sfx("dash")
		_:
			return
	cooldowns_changed.emit(cooldowns)

func _apply_melee_damage() -> void:
	if not is_inside_tree():
		return
	var dmg := float(stats["damage"])
	var rng := float(stats["range"])
	var combo_mult := 1.35 if combo_step == 2 else 1.0
	var forward := Vector3(sin(rotation.y), 0, cos(rotation.y))
	var any_hit := false
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy) or enemy.get("hp") == null or int(enemy.hp) <= 0:
			continue
		var to_e: Vector3 = enemy.global_position - global_position
		to_e.y = 0
		var dist := to_e.length()
		var hit_radius: float = rng + (1.35 if enemy.is_boss else 0.78)
		if dist <= hit_radius:
			var dot := forward.dot(to_e.normalized()) if dist > 0.001 else 1.0
			if combo_step == 2 or dist < 2.2 or dot > -0.35:
				var final_dmg := dmg * combo_mult
				var did_crit: bool = false
				if enemy.has_method("take_damage_and_report_crit"):
					did_crit = bool(enemy.take_damage_and_report_crit(final_dmg, self, combo_step == 2))
				else:
					did_crit = randf() < float(stats.get("crit_chance", 0.1))
					enemy.take_damage(final_dmg, self, combo_step == 2)
				if is_instance_valid(enemy) and int(enemy.hp) > 0:
					_on_sword_hit(enemy, final_dmg, did_crit)
				elif is_instance_valid(enemy):
					# Still trigger ground AoE sword passives at impact position even if lethal
					_on_sword_hit(enemy, final_dmg, did_crit)
				any_hit = true
	if any_hit:
		_after_any_hit()

func _deal_aoe_damage(radius: float, dmg: float, knockback: float) -> void:
	if not is_inside_tree():
		return
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy):
			continue
		var dist := global_position.distance_to(enemy.global_position)
		if dist <= radius:
			enemy.take_damage(dmg, self, false, knockback)

func _spawn_wave_projectile() -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
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
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	var scene_root := get_tree().current_scene
	for i in range(7):
		var angle := (float(i) / 7.0) * TAU
		var dist := 2.5 if i == 0 else 5.2
		var target := global_position + Vector3(sin(angle) * dist, 0, cos(angle) * dist)
		var node := Node3D.new()
		node.name = "SkySword_%d" % i
		var sword_visual: Node3D = null
		if ResourceLoader.exists("res://scripts/ModelLoader.gd"):
			sword_visual = load("res://scripts/ModelLoader.gd").build_sword_visual(current_tier, sword_level)
		if sword_visual == null:
			sword_visual = load("res://scripts/SwordBuilder.gd").build_sword(str(current_tier["id"]), sword_level)
		sword_visual.scale = Vector3.ONE * 1.6
		sword_visual.rotation.z = PI
		node.add_child(sword_visual)
		scene_root.add_child(node)
		node.global_position = target + Vector3(0, 18.0 + i * 2.2, 0)
		var script := preload("res://scripts/SkySword.gd")
		node.set_script(script)
		node.setup(target, float(stats["damage"]) * 2.5, self, float(i) * 0.08)

func take_player_damage(amount: int) -> void:
	if dash_timer > 0.0 or is_dead or invuln_timer > 0.0:
		return
	var dmg_taken := maxi(1, amount)
	player_hp -= dmg_taken
	floating_text_requested.emit(global_position + Vector3(0, 2.3, 0), "-%d" % dmg_taken, Color("#fb7185"), false)
	if player_hp <= 0:
		player_hp = 0
		is_dead = true
		play_sfx("gameover", 1.0, 1.0)
		hp_changed.emit(player_hp, player_max_hp)
		log_added.emit("Has caído en batalla...", "boss")
		player_died.emit()
		return
	play_sfx("player_hurt", 0.94, 1.05)
	hp_changed.emit(player_hp, player_max_hp)

func respawn_player() -> void:
	is_dead = false
	_recalc_stats()
	player_hp = player_max_hp
	global_position = Vector3.ZERO
	velocity = Vector3.ZERO
	invuln_timer = 2.2
	play_sfx("evolution", 1.0, 1.0)
	hp_changed.emit(player_hp, player_max_hp)
	log_added.emit("¡La Forja Ancestral te restaura!", "upgrade")
	if is_inside_tree() and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(self)

func add_xp(amount: int) -> void:
	gain_experience(amount)

func gain_experience(amount: int) -> void:
	var gd := _get_gamedata()
	current_xp += maxi(0, amount)
	var required: int = int(gd.get_xp_required(sword_level))
	var old_tier := current_tier
	var leveled := false
	while current_xp >= required:
		current_xp -= required
		sword_level += 1
		required = int(gd.get_xp_required(sword_level))
		leveled = true
	if leveled:
		current_tier = gd.get_sword_for_level(sword_level)
		_recalc_stats()
		player_hp = player_max_hp
		_refresh_sword_visual()
		var evolved := str(current_tier["id"]) != str(old_tier.get("id", ""))
		if evolved:
			play_sfx("evolution", 1.0, 1.0)
			log_added.emit("¡METAMORFOSIS AL NIVEL %d! Tu espada ha evolucionado a %s." % [sword_level, str(current_tier["name"]).to_upper()], "evolution")
			evolution_changed.emit(current_tier)
		else:
			play_sfx("levelup", 1.0, 1.0)
			log_added.emit("¡Tu espada subió al Nivel %d! El filo y poder aumentan." % sword_level, "levelup")
		hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, int(gd.get_xp_required(sword_level)), sword_level)

func add_gold(amount: int) -> void:
	gold = maxi(0, gold + amount)
	gold_changed.emit(gold)

func add_kill() -> void:
	kills += 1
	wave_kills += 1
	kills_changed.emit(kills)
	if wave_kills >= 8:
		wave_kills = 0
		wave += 1
		wave_changed.emit(wave, wave_kills)
		if wave % 3 == 0:
			play_sfx("boss", 0.95, 1.0)
			log_added.emit("¡OLEADA %d! ¡El Jefe Supremo Malakor emerge del Abismo!" % wave, "boss")
		else:
			play_sfx("levelup", 0.92, 0.96)
			log_added.emit("¡Oleada %d iniciada! Monstruos más fuertes emergen." % wave, "boss")
	else:
		wave_changed.emit(wave, wave_kills)

func buy_upgrade(key: String, base_cost: int) -> bool:
	if not upgrades.has(key):
		return false
	var lvl: int = int(upgrades[key])
	var max_level := 10
	if lvl >= max_level:
		log_added.emit("Mejora al máximo: %s" % key, "upgrade")
		return false
	var cost := int(round(base_cost * pow(1.45, lvl)))
	if gold < cost:
		return false
	gold -= cost
	upgrades[key] = lvl + 1
	_recalc_stats()
	if key == "bladeSize":
		_refresh_sword_visual()
	play_sfx("upgrade")
	gold_changed.emit(gold)
	inventory_changed.emit()
	log_added.emit("Mejora forjada: %s Nv.%d" % [key, lvl + 1], "upgrade")
	return true

# --- RPG Inventory, Materials, Relics & Consumables ---

func add_material(mat_id: String, count: int = 1) -> void:
	if mat_id == "" or count <= 0:
		return
	materials[mat_id] = int(materials.get(mat_id, 0)) + count
	var gd := _get_gamedata()
	var mdef: Dictionary = gd.get_material_by_id(mat_id)
	var mname := str(mdef.get("name", mat_id))
	play_sfx("loot", 0.98, 1.08)
	inventory_changed.emit()
	log_added.emit("Material obtenido: +%d %s" % [count, mname], "loot")

func add_item(item_id: String) -> bool:
	var gd := _get_gamedata()
	var rdef: Dictionary = gd.get_relic_by_id(item_id)
	if rdef.is_empty():
		return false
	if inventory_items.has(item_id):
		# Duplicate relic converts into Essence Gold bonus!
		var bonus_gold := maxi(25, int(rdef.get("recipe_gold", 60)) / 2)
		add_gold(bonus_gold)
		log_added.emit("Reliquia repetida fundida en +%d Oro (%s)" % [bonus_gold, str(rdef["name"])], "loot")
		return false
	inventory_items.append(item_id)
	play_sfx("evolution", 1.08, 1.12)
	# Auto-equip if that slot is currently empty!
	var slot := str(rdef.get("slot", ""))
	if slot in equipped and str(equipped[slot]) == "":
		equipped[slot] = item_id
		_recalc_stats()
		hp_changed.emit(player_hp, player_max_hp)
		log_added.emit("¡Reliquia equipada automáticamente: %s!" % str(rdef["name"]), "loot")
	else:
		log_added.emit("¡Nueva reliquia en inventario: %s!" % str(rdef["name"]), "loot")
	inventory_changed.emit()
	return true

func add_consumable(cons_id: String, count: int = 1) -> void:
	if not consumables.has(cons_id) or count <= 0:
		return
	consumables[cons_id] = int(consumables.get(cons_id, 0)) + count
	inventory_changed.emit()

func equip_relic(item_id: String) -> bool:
	if not inventory_items.has(item_id):
		return false
	var gd := _get_gamedata()
	var rdef: Dictionary = gd.get_relic_by_id(item_id)
	if rdef.is_empty():
		return false
	var slot := str(rdef.get("slot", ""))
	if not equipped.has(slot):
		return false
	equipped[slot] = item_id
	var prev_max := player_max_hp
	_recalc_stats()
	if player_max_hp > prev_max:
		player_hp = mini(player_max_hp, player_hp + (player_max_hp - prev_max))
	else:
		player_hp = mini(player_max_hp, player_hp)
	play_sfx("ui", 1.05, 1.10)
	hp_changed.emit(player_hp, player_max_hp)
	inventory_changed.emit()
	log_added.emit("Equipado [%s]: %s" % [str(rdef.get("slot_label", slot)), str(rdef["name"])], "upgrade")
	return true

func unequip_slot(slot: String) -> bool:
	if not equipped.has(slot) or str(equipped[slot]) == "":
		return false
	equipped[slot] = ""
	_recalc_stats()
	player_hp = mini(player_max_hp, player_hp)
	play_sfx("ui", 0.90, 0.95)
	hp_changed.emit(player_hp, player_max_hp)
	inventory_changed.emit()
	return true

func can_craft_relic(item_id: String) -> bool:
	if inventory_items.has(item_id):
		return false
	var gd := _get_gamedata()
	var rdef: Dictionary = gd.get_relic_by_id(item_id)
	if rdef.is_empty():
		return false
	if gold < int(rdef.get("recipe_gold", 0)):
		return false
	var rmats: Dictionary = rdef.get("recipe_mats", {})
	for mk in rmats.keys():
		if int(materials.get(mk, 0)) < int(rmats[mk]):
			return false
	return true

func craft_relic(item_id: String) -> bool:
	if not can_craft_relic(item_id):
		return false
	var gd := _get_gamedata()
	var rdef: Dictionary = gd.get_relic_by_id(item_id)
	var cost_g := int(rdef.get("recipe_gold", 0))
	var rmats: Dictionary = rdef.get("recipe_mats", {})
	gold -= cost_g
	for mk in rmats.keys():
		materials[mk] = maxi(0, int(materials.get(mk, 0)) - int(rmats[mk]))
		if int(materials[mk]) == 0:
			materials.erase(mk)
	play_sfx("upgrade", 1.02, 1.08)
	gold_changed.emit(gold)
	add_item(item_id)
	inventory_changed.emit()
	return true

func buy_consumable(cons_id: String) -> bool:
	var gd := _get_gamedata()
	var cdef: Dictionary = gd.CONSUMABLE_DEFINITIONS.get(cons_id, {})
	if cdef.is_empty():
		return false
	var cost := int(cdef.get("cost_gold", 50))
	if gold < cost:
		return false
	gold -= cost
	consumables[cons_id] = int(consumables.get(cons_id, 0)) + 1
	play_sfx("upgrade", 1.08, 1.14)
	gold_changed.emit(gold)
	inventory_changed.emit()
	log_added.emit("Comprado: %s" % str(cdef["name"]), "upgrade")
	return true

func use_consumable(cons_id: String) -> bool:
	if is_dead:
		return false
	var cnt := int(consumables.get(cons_id, 0))
	if cnt <= 0:
		return false
	var gd := _get_gamedata()
	var cdef: Dictionary = gd.CONSUMABLE_DEFINITIONS.get(cons_id, {})
	if cdef.is_empty():
		return false
	if cons_id == "potion_hp":
		if player_hp >= player_max_hp:
			log_added.emit("Tu vida ya está al máximo.", "upgrade")
			return false
		consumables[cons_id] = cnt - 1
		var heal := maxi(25, int(round(float(player_max_hp) * float(cdef.get("heal_ratio", 0.45)))))
		player_hp = mini(player_max_hp, player_hp + heal)
		play_sfx("loot", 1.12, 1.18)
		floating_text_requested.emit(global_position + Vector3(0, 2.4, 0), "+%d HP" % heal, Color("#4ade80"), true)
		hp_changed.emit(player_hp, player_max_hp)
		inventory_changed.emit()
		log_added.emit("Usaste %s (+%d Vida)" % [str(cdef["name"]), heal], "upgrade")
		return true
	elif cons_id == "elixir_xp":
		consumables[cons_id] = cnt - 1
		var req: int = int(gd.get_xp_required(sword_level))
		var bonus_xp := maxi(20, int(round(float(req) * float(cdef.get("xp_ratio", 0.65)))))
		play_sfx("levelup", 1.06, 1.12)
		floating_text_requested.emit(global_position + Vector3(0, 2.5, 0), "+%d EXP" % bonus_xp, Color("#38bdf8"), true)
		inventory_changed.emit()
		log_added.emit("Usaste %s (+%d EXP)" % [str(cdef["name"]), bonus_xp], "levelup")
		gain_experience(bonus_xp)
		return true
	return false

func jump_to_level(target_level: int) -> void:
	var gd := _get_gamedata()
	var old_tier := current_tier
	sword_level = max(1, target_level)
	current_xp = 0
	current_tier = gd.get_sword_for_level(sword_level)
	_recalc_stats()
	player_hp = player_max_hp
	_refresh_sword_visual()
	var evolved := str(current_tier["id"]) != str(old_tier.get("id", ""))
	if evolved:
		play_sfx("evolution", 1.0, 1.0)
		log_added.emit("¡EVOLUCIÓN ACTIVADA (Nivel %d): %s!" % [sword_level, str(current_tier["name"])], "evolution")
		evolution_changed.emit(current_tier)
	else:
		play_sfx("levelup", 1.0, 1.0)
		log_added.emit("Nivel de la espada ajustado a Nivel %d." % sword_level, "levelup")
	hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, int(gd.get_xp_required(sword_level)), sword_level)

func toggle_auto_hunt() -> void:
	auto_hunt = not auto_hunt
	play_sfx("ui")
	log_added.emit("Auto-Caza: %s" % ("ACTIVADO" if auto_hunt else "DESACTIVADO"), "upgrade")

func toggle_wielder_mode() -> void:
	wielder_mode = "knight_wielder" if wielder_mode == "living_sword" else "living_sword"
	_refresh_sword_visual()
	play_sfx("ui")
	log_added.emit("Modo Portador: %s" % ("Caballero 3D" if wielder_mode == "knight_wielder" else "Espada Viviente"), "upgrade")

func _get_relic_bonuses() -> Dictionary:
	var gd := _get_gamedata()
	var b := {
		"dmg_mult": 0.0,
		"atk_speed_mult": 0.0,
		"crit_chance": 0.0,
		"crit_mult": 0.0,
		"range_mult": 0.0,
		"life_on_hit": 0,
		"xp_mult": 0.0,
		"gold_mult": 0.0,
		"cd_reduction": 0.0,
		"max_hp_bonus": 0,
	}
	for slot in ["grip", "rune", "relic"]:
		var rid := str(equipped.get(slot, ""))
		if rid == "":
			continue
		var rdef: Dictionary = gd.get_relic_by_id(rid)
		if rdef.is_empty():
			continue
		var rstats: Dictionary = rdef.get("stats", {})
		for sk in rstats.keys():
			if b.has(sk):
				b[sk] += rstats[sk]
	return b

func _recalc_stats() -> void:
	var gd := _get_gamedata()
	current_tier = gd.get_sword_for_level(sword_level)
	var rb := _get_relic_bonuses()

	player_max_hp = 220 + (sword_level - 1) * 28 + int(rb["max_hp_bonus"])
	player_hp = clampi(player_hp, 0 if is_dead else 1, player_max_hp)

	var level_bonus := 1.0 + (sword_level - int(current_tier["min_level"])) * 0.14
	var sharp_mult := 1.0 + int(upgrades["sharpness"]) * 0.18 + float(rb["dmg_mult"])
	var dmg := int(round(float(current_tier["base_damage"]) * level_bonus * sharp_mult))
	var atk_speed := float(current_tier["attack_speed"]) * (1.0 + int(upgrades["swiftness"]) * 0.08 + float(rb["atk_speed_mult"]))
	var crit: float = minf(0.95, float(current_tier["crit_chance"]) + int(upgrades["criticalMastery"]) * 0.04 + float(rb["crit_chance"]))
	var crit_mult := 1.85 + int(upgrades["criticalMastery"]) * 0.15 + (0.65 if str(current_tier["id"]) == "celestial" else 0.0) + float(rb["crit_mult"])
	var rng := float(current_tier["range"]) * (1.0 + int(upgrades["bladeSize"]) * 0.06 + float(rb["range_mult"]))
	var life_on_hit := int(upgrades["vampirism"]) * 3 + (14 if str(current_tier["id"]) == "obsidian" else 0) + int(rb["life_on_hit"])
	var xp_mult := 1.0 + int(upgrades["soulMagnet"]) * 0.15 + (0.15 if str(current_tier["id"]) == "wood" else 0.0) + float(rb["xp_mult"])
	var gold_mult := 1.0 + int(upgrades["soulMagnet"]) * 0.12 + float(rb["gold_mult"])
	var cdr := clampf(float(rb["cd_reduction"]), 0.0, 0.45)

	stats = {
		"damage": dmg,
		"attack_speed": atk_speed,
		"crit_chance": crit,
		"crit_mult": crit_mult,
		"range": rng,
		"life_on_hit": life_on_hit,
		"xp_mult": xp_mult,
		"gold_mult": gold_mult,
		"cd_reduction": cdr,
		"max_hp_bonus": int(rb["max_hp_bonus"]),
	}

func _refresh_sword_visual() -> void:
	if sword_mesh_holder == null:
		return
	for c in sword_mesh_holder.get_children():
		c.queue_free()
	var scale_mult := 1.0 + int(upgrades["bladeSize"]) * 0.06
	var base_scale := (0.88 * scale_mult) if wielder_mode == "knight_wielder" else (1.12 * scale_mult)

	var built: Node3D = null
	var used_obj := false
	if ResourceLoader.exists("res://scripts/ModelLoader.gd"):
		var ML = load("res://scripts/ModelLoader.gd")
		built = ML.build_sword_visual(current_tier, sword_level)
		used_obj = built != null and built.name == "SwordOBJ"
	if built == null:
		var SwordBuilderScript = load("res://scripts/SwordBuilder.gd")
		built = SwordBuilderScript.build_sword(str(current_tier["id"]), sword_level)

	if used_obj:
		sword_mesh_holder.add_child(built)
		built.scale = Vector3.ONE * base_scale
	else:
		var blade_pivot_node: Node3D = built.get_node_or_null("BladePivot")
		if blade_pivot_node:
			for child in blade_pivot_node.get_children():
				blade_pivot_node.remove_child(child)
				sword_mesh_holder.add_child(child)
				child.scale = child.scale * base_scale
			built.queue_free()
		else:
			sword_mesh_holder.add_child(built)
			built.scale = Vector3.ONE * base_scale

	_ensure_knight_visual()
	if knight_holder:
		knight_holder.visible = wielder_mode == "knight_wielder"
	if sword_pivot:
		if wielder_mode == "knight_wielder":
			sword_pivot.position = Vector3(0.6, 1.2, 0.3)
		else:
			sword_pivot.position = Vector3(0, 1.55, 0)
	if aura_light:
		aura_light.light_color = current_tier["aura_color"]
	if ground_aura_ring and ground_aura_ring.material_override is StandardMaterial3D:
		var gmat: StandardMaterial3D = ground_aura_ring.material_override
		var acol: Color = current_tier["aura_color"]
		gmat.albedo_color = Color(acol.r, acol.g, acol.b, 0.72)
		gmat.emission = acol
	if slash_ring:
		slash_ring.visible = false

func _ensure_knight_visual() -> void:
	if knight_holder == null or knight_holder.has_node("KnightOBJ"):
		return
	if not ResourceLoader.exists("res://scripts/ModelLoader.gd"):
		return
	var ML = load("res://scripts/ModelLoader.gd")
	var knight: Node3D = ML.build_knight_visual()
	if knight:
		for c in knight_holder.get_children():
			c.queue_free()
		knight_holder.add_child(knight)

func _update_sword_anim(delta: float) -> void:
	if sword_pivot == null or sword_mesh_holder == null:
		return
	var t := Time.get_ticks_msec() / 1000.0
	var moving := Vector2(velocity.x, velocity.z).length() > 0.5
	var speed_factor: float = clamp(Vector2(velocity.x, velocity.z).length() / move_speed, 0.0, 1.5)

	var bob: float = sin(t * (8.0 if moving else 2.8)) * (0.08 if moving else 0.04)
	var lean: float = clamp(speed_factor * 0.22, 0.0, 0.28) if moving else 0.0

	if wielder_mode == "living_sword":
		var base_y := 1.55 + (sin(t * 3.5) * 0.18 if whirlwind_timer <= 0.0 else 0.0)
		sword_pivot.position.y = lerp(sword_pivot.position.y, base_y + bob, delta * 8.0)
		sword_pivot.rotation.x = lerp_angle(sword_pivot.rotation.x, lean, delta * 8.0)
		sword_pivot.position.x = lerp(sword_pivot.position.x, 0.0, delta * 8.0)
		if knight_holder:
			knight_holder.position.y = lerp(knight_holder.position.y, 0.0, delta * 8.0)
	else:
		sword_pivot.position.y = lerp(sword_pivot.position.y, 1.2 + bob * 0.5, delta * 8.0)
		sword_pivot.position.x = lerp(sword_pivot.position.x, 0.6, delta * 8.0)
		sword_pivot.rotation.x = lerp_angle(sword_pivot.rotation.x, lean * 0.5, delta * 8.0)
		if knight_holder:
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
			var ang: float = lerp(-1.55, 1.55, swing) - windup * 0.3 + recover * 0.1
			sword_mesh_holder.rotation.z = ang
			sword_mesh_holder.rotation.x = lerp(0.55, 1.05, sin(p * PI))
			sword_mesh_holder.rotation.y = lerp(-0.35, 0.35, swing)
			sword_pivot.rotation.y = lerp(sword_pivot.rotation.y, -0.25 + swing * 0.5, delta * 10.0)
		elif combo_step == 1:
			var ang2: float = lerp(1.55, -1.55, swing) + windup * 0.3 - recover * 0.1
			sword_mesh_holder.rotation.z = ang2
			sword_mesh_holder.rotation.x = lerp(0.55, 1.0, sin(p * PI))
			sword_mesh_holder.rotation.y = lerp(0.35, -0.35, swing)
			sword_pivot.rotation.y = lerp(sword_pivot.rotation.y, 0.25 - swing * 0.5, delta * 10.0)
		else:
			sword_mesh_holder.rotation.x = lerp(-1.15, 1.75, swing) - windup * 0.4
			sword_mesh_holder.rotation.z = lerp(0.0, 0.15, sin(p * PI))
			sword_mesh_holder.rotation.y = 0.0
			sword_pivot.position.y += sin(p * PI) * 0.03
		sword_pivot.position.z = lerp(sword_pivot.position.z, -sin(p * PI) * 0.25, delta * 12.0)
	else:
		var idle_x := 0.22 if wielder_mode == "living_sword" else 0.35
		sword_mesh_holder.rotation.x = lerp_angle(sword_mesh_holder.rotation.x, idle_x, delta * 10.0)
		sword_mesh_holder.rotation.z = lerp_angle(sword_mesh_holder.rotation.z, sin(t * 2.8) * 0.12, delta * 10.0)
		sword_mesh_holder.rotation.y = lerp_angle(sword_mesh_holder.rotation.y, sin(t * 1.6) * 0.06, delta * 8.0)
		sword_pivot.rotation.y = lerp_angle(sword_pivot.rotation.y, 0.0, delta * 8.0)
		sword_pivot.position.z = lerp(sword_pivot.position.z, 0.0, delta * 8.0)

	if slash_ring and slash_ring.visible:
		var mat: StandardMaterial3D = slash_ring.material_override
		if mat:
			mat.albedo_color.a = max(0.0, mat.albedo_color.a - delta * 4.0)
			if mat.albedo_color.a <= 0.01:
				slash_ring.visible = false

# --- Canonical 8-Sword Special Effects ---

func _on_sword_hit(enemy: Node3D, dmg: float, is_crit: bool) -> void:
	var eff := str(current_tier.get("special_effect", "none"))
	var epos: Vector3 = enemy.global_position if is_instance_valid(enemy) else global_position
	match eff:
		"solar_burn", "gold":
			if is_instance_valid(enemy) and enemy.has_method("apply_burn"):
				enemy.apply_burn(max(5.0, dmg * 0.25), 2.5)
			_spawn_fire_patch(epos)
		"lifesteal_magma", "obsidian":
			_spawn_magma_eruption(epos, dmg * 0.45)
		"cosmic_nova", "celestial":
			_spawn_dimensional_wave(epos, dmg * 0.35)
			if is_crit:
				_spawn_cosmic_nova(epos, dmg * 0.6)
		"bleed", "iron":
			if is_crit and is_instance_valid(enemy) and enemy.has_method("apply_bleed"):
				enemy.apply_bleed(3.0)

func _after_any_hit() -> void:
	var eff := str(current_tier.get("special_effect", "none"))
	if eff in ["sparks", "copper"]:
		copper_hit_counter += 1
		if copper_hit_counter >= 3:
			copper_hit_counter = 0
			_spawn_copper_sparks()
			_deal_aoe_damage(float(stats["range"]) * 1.15, float(stats["damage"]) * 0.35, 3.0)
	elif eff in ["arcane_shards", "crystal"]:
		_spawn_crystal_shard()

func _process_sword_effects(delta: float) -> void:
	var eff := str(current_tier.get("special_effect", "none"))
	if eff in ["solar_burn", "gold"]:
		gold_regen_timer -= delta
		if gold_regen_timer <= 0.0:
			gold_regen_timer = 1.0
			if player_hp > 0 and player_hp < player_max_hp:
				player_hp = mini(player_max_hp, player_hp + 4)
				hp_changed.emit(player_hp, player_max_hp)
	elif eff in ["arcane_shards", "crystal"]:
		crystal_shard_timer -= delta
		if crystal_shard_timer <= 0.0:
			crystal_shard_timer = 1.7
			_spawn_crystal_shard()
	elif eff in ["cosmic_nova", "celestial"]:
		celestial_nova_timer -= delta
		if celestial_nova_timer <= 0.0:
			celestial_nova_timer = 4.8
			if _find_nearest_enemy() != null:
				_spawn_cosmic_nova(global_position + Vector3(sin(rotation.y), 0, cos(rotation.y)) * 2.0, float(stats["damage"]) * 0.5)

func _spawn_copper_sparks() -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	for i in range(10):
		var p := MeshInstance3D.new()
		var s := SphereMesh.new()
		s.radius = 0.08; s.height = 0.16
		p.mesh = s
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(1.0, 0.6, 0.2, 0.95)
		mat.emission_enabled = true
		mat.emission = Color(1.0, 0.45, 0.1)
		mat.emission_energy_multiplier = 4.0
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		p.material_override = mat
		get_tree().current_scene.add_child(p)
		p.global_position = global_position + Vector3(0, 1.0, 0)
		var ang := randf() * TAU
		var dist := randf_range(1.0, float(stats["range"]) * 1.1)
		var target := p.global_position + Vector3(sin(ang) * dist, randf_range(-0.2, 0.6), cos(ang) * dist)
		var tw := get_tree().current_scene.create_tween()
		tw.tween_property(p, "global_position", target, 0.25)
		tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.25)
		tw.tween_callback(p.queue_free)

func _spawn_fire_patch(pos: Vector3) -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	var ring := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.8; cyl.bottom_radius = 0.8; cyl.height = 0.05
	ring.mesh = cyl
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1.0, 0.45, 0.1, 0.7)
	mat.emission_enabled = true
	mat.emission = Color(1.0, 0.3, 0.0)
	mat.emission_energy_multiplier = 2.5
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	ring.material_override = mat
	get_tree().current_scene.add_child(ring)
	ring.global_position = Vector3(pos.x, 0.05, pos.z)
	var tw := get_tree().current_scene.create_tween()
	tw.tween_property(ring, "scale", Vector3(1.6, 1.0, 1.6), 0.4)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.6)
	tw.tween_callback(ring.queue_free)

func _spawn_magma_eruption(pos: Vector3, dmg: float) -> void:
	_deal_aoe_damage_at(pos, 2.4, dmg, 2.5)
	if not is_inside_tree() or get_tree().current_scene == null:
		return
	for i in range(6):
		var p := MeshInstance3D.new()
		var s := SphereMesh.new(); s.radius = 0.12; s.height = 0.24
		p.mesh = s
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(1.0, 0.25, 0.0, 0.9)
		mat.emission_enabled = true; mat.emission = Color(1.0, 0.2, 0.0); mat.emission_energy_multiplier = 3.0
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		p.material_override = mat
		get_tree().current_scene.add_child(p)
		p.global_position = pos + Vector3(0, 0.2, 0)
		var ang := randf() * TAU
		var tgt := p.global_position + Vector3(sin(ang) * randf_range(0.5, 1.8), randf_range(0.8, 1.8), cos(ang) * randf_range(0.5, 1.8))
		var tw := get_tree().current_scene.create_tween()
		tw.tween_property(p, "global_position", tgt, 0.25)
		tw.tween_property(p, "global_position", Vector3(tgt.x, 0.1, tgt.z), 0.2)
		tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 0.2)
		tw.tween_callback(p.queue_free)

func _spawn_dimensional_wave(pos: Vector3, dmg: float) -> void:
	_spawn_shockwave(pos, Color(0.4, 0.9, 1.0), 3.5)
	_deal_aoe_damage_at(pos, 3.0, dmg, 2.0)

func _spawn_cosmic_nova(pos: Vector3, dmg: float) -> void:
	_spawn_shockwave(pos, Color(0.8, 0.5, 1.0), 5.0)
	_deal_aoe_damage_at(pos, 4.5, dmg, 4.0)

func _spawn_crystal_shard() -> void:
	if not is_inside_tree():
		return
	var target := _find_nearest_enemy()
	if target == null:
		return
	if get_tree().current_scene == null:
		if target.has_method("take_damage"):
			target.take_damage(float(stats["damage"]) * 0.45, self, false, 1.5, false)
		return
	var shard := MeshInstance3D.new()
	var box := BoxMesh.new(); box.size = Vector3(0.12, 0.12, 0.5)
	shard.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.8, 0.5, 1.0, 0.95)
	mat.emission_enabled = true; mat.emission = Color(0.85, 0.4, 1.0); mat.emission_energy_multiplier = 3.0
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	shard.material_override = mat
	get_tree().current_scene.add_child(shard)
	var start := global_position + Vector3(0, 1.8, 0)
	shard.global_position = start
	var end := target.global_position + Vector3(0, 1.0, 0)
	shard.look_at(end, Vector3.UP)
	var tw := get_tree().current_scene.create_tween()
	tw.tween_property(shard, "global_position", end, 0.22)
	tw.tween_callback(func():
		if is_instance_valid(target) and target.has_method("take_damage"):
			target.take_damage(float(stats["damage"]) * 0.45, self, false, 1.5, false)
		shard.queue_free()
	)

func _deal_aoe_damage_at(pos: Vector3, radius: float, dmg: float, knockback: float) -> void:
	if not is_inside_tree():
		return
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy):
			continue
		var dist := pos.distance_to(enemy.global_position)
		if dist <= radius:
			enemy.take_damage(dmg, self, false, knockback, false)

func _spawn_shockwave(pos: Vector3, color: Color, max_radius: float = 4.0) -> void:
	if not is_inside_tree() or get_tree().current_scene == null:
		return
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
	if slash_ring == null:
		return
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
	if combo_step == 0:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, -0.35)
	elif combo_step == 1:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, 0.35)
	else:
		slash_ring.rotation = Vector3(PI * 0.5, 0.0, PI * 0.5)
	slash_ring.position = Vector3(0, 1.25, 0.0)
	slash_ring.scale = Vector3.ONE

func _find_nearest_enemy() -> Node3D:
	if not is_inside_tree():
		return null
	var nearest: Node3D = null
	var best := INF
	for e in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(e) or (e.get("hp") != null and int(e.hp) <= 0):
			continue
		var d := global_position.distance_to(e.global_position)
		if d < best:
			best = d
			nearest = e
	return nearest

func _emit_all() -> void:
	var gd := _get_gamedata()
	hp_changed.emit(player_hp, player_max_hp)
	xp_changed.emit(current_xp, int(gd.get_xp_required(sword_level)), sword_level)
	gold_changed.emit(gold)
	kills_changed.emit(kills)
	wave_changed.emit(wave, wave_kills)
	inventory_changed.emit()

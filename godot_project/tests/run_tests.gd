extends SceneTree

var failures: Array[String] = []
var passes: int = 0

var _did_run: bool = false
var _exit_code: int = 0

func _process(_delta: float) -> bool:
	if _did_run:
		var autoload_am := root.get_node_or_null("AudioManager")
		if autoload_am and autoload_am.has_method("stop_all"):
			autoload_am.stop_all()
		quit(_exit_code)
		return true
	_did_run = true
	print("=== RUNNING TESTS ===")
	test_gamedata_swords()
	test_gamedata_monsters()
	test_gamedata_rpg_items()
	test_xp_curve()
	test_model_files_exist()
	test_model_resources_load()
	test_canonical_skill_ids()
	test_upgrade_max_level()
	test_monster_builder()
	test_sword_builder()
	test_player_new_features()
	test_monster_boss_ai()
	test_hud_pause_and_cooldowns()
	test_boot_flow_scenes_exist()
	test_audio_assets_exist()
	test_monster_distinct_ai()
	test_export_presets()

	# Real runtime behavioral tests
	test_runtime_combat_and_progression()
	test_runtime_rpg_inventory_and_crafting()
	test_runtime_malakor_phases_and_rewards()
	test_save_roundtrip_and_v1_migration()
	test_save_settings_and_audio_manager()
	test_arena_decor_quality_levels()
	test_hud_layout_and_overlays_all_resolutions()
	test_pilot_sword_3d_glb_and_pbr()
	test_evolution_catalog_and_validator()
	test_evolution_permanent_branching_rules()
	test_skill_catalog_and_progression()
	test_sword_stats_calculator_17_attributes()
	test_save_v3_permanent_evolution_survival()
	test_player_evolution_integration()
	test_evolution_skill_ui_panels()
	test_skill_slots_world_events_and_energy()

	print("=== RESULTS: %d passed, %d failed ===" % [passes, failures.size()])
	for f in failures:
		print("FAIL: ", f)
	_exit_code = 1 if failures.size() > 0 else 0
	return false

func assert_true(cond: bool, msg: String) -> void:
	if cond:
		passes += 1
	else:
		failures.append(msg)

func assert_eq(a, b, msg: String) -> void:
	if a == b:
		passes += 1
	else:
		failures.append("%s (expected %s, got %s)" % [msg, str(b), str(a)])

func test_gamedata_swords() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	assert_eq(gd.SWORD_EVOLUTIONS.size(), 8, "8 sword evolutions")
	var ids = []
	for t in gd.SWORD_EVOLUTIONS:
		ids.append(str(t["id"]))
		assert_true(t.has("model_path"), "sword has model_path")
		assert_true(ResourceLoader.exists(str(t["model_path"])), "sword model exists: %s" % str(t["model_path"]))
	assert_eq(ids, ["wood", "copper", "iron", "silver", "gold", "crystal", "obsidian", "celestial"], "sword ids order")
	gd.free()

func test_gamedata_monsters() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	assert_eq(gd.MONSTER_DEFINITIONS.size(), 7, "7 monsters")
	var ids = []
	for m in gd.MONSTER_DEFINITIONS:
		ids.append(str(m["id"]))
		assert_true(ResourceLoader.exists(str(m["model_path"])), "monster model exists: %s" % str(m["model_path"]))
	assert_eq(ids, ["slime", "goblin", "skeleton", "copper_golem", "orc_berserker", "crimson_drake", "demon_lord"], "monster ids")
	gd.free()

func test_gamedata_rpg_items() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	assert_eq(gd.MATERIAL_DEFINITIONS.size(), 7, "7 RPG monster materials")
	assert_eq(gd.RELIC_DEFINITIONS.size(), 9, "9 craftable/droppable RPG relics")
	assert_eq(gd.CONSUMABLE_DEFINITIONS.size(), 2, "2 battle consumables")
	assert_eq(gd.UPGRADE_DEFINITIONS.size(), 6, "6 forge upgrade definitions")
	for m_id in ["slime", "goblin", "skeleton", "copper_golem", "orc_berserker", "crimson_drake", "demon_lord"]:
		var mat_key: String = gd.get_drop_material_for_monster(m_id)
		assert_true(gd.MATERIAL_DEFINITIONS.has(mat_key), "valid material mapping for %s" % m_id)
	gd.free()

func test_xp_curve() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	assert_eq(gd.get_xp_required(1), 35, "xp lvl1")
	assert_eq(gd.get_xp_required(2), 55, "xp lvl2")
	assert_eq(gd.get_xp_required(5), 148, "xp lvl5")
	gd.free()

func test_model_files_exist() -> void:
	var expected = [
		"res://assets/models/hero_knight_wielder.obj",
		"res://assets/models/sword_wood_nv1.obj", "res://assets/models/sword_copper_nv5.obj",
		"res://assets/models/sword_iron_nv10.obj", "res://assets/models/sword_silver_nv15.obj",
		"res://assets/models/sword_gold_nv20.obj", "res://assets/models/sword_crystal_nv25.obj",
		"res://assets/models/sword_obsidian_nv30.obj", "res://assets/models/sword_celestial_nv35.obj",
		"res://assets/models/monster_slime.obj", "res://assets/models/monster_goblin.obj",
		"res://assets/models/monster_skeleton.obj", "res://assets/models/monster_copper_golem.obj",
		"res://assets/models/monster_orc_berserker.obj", "res://assets/models/monster_crimson_drake.obj",
		"res://assets/models/monster_demon_lord.obj",
	]
	assert_eq(expected.size(), 16, "16 model paths")
	for p in expected:
		assert_true(ResourceLoader.exists(p), "exists: %s" % p)

func test_model_resources_load() -> void:
	var paths = [
		"res://assets/models/hero_knight_wielder.obj",
		"res://assets/models/sword_celestial_nv35.obj",
		"res://assets/models/monster_demon_lord.obj",
	]
	for p in paths:
		var r = load(p)
		assert_true(r != null, "loads: %s" % p)
		if r is Mesh:
			var aabb = r.get_aabb()
			assert_true(aabb.size.y > 0.1, "aabb y > 0.1: %s" % p)

func test_canonical_skill_ids() -> void:
	var f = FileAccess.open("res://scripts/Player.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find('"swordWave"') != -1, "Player has swordWave")
	assert_true(src.find("func _canonical_skill") != -1, "Player has canonical skill mapper")

func test_upgrade_max_level() -> void:
	var f = FileAccess.open("res://scripts/Player.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("max_level") != -1, "buy_upgrade has max_level")

func test_monster_builder() -> void:
	var MB = load("res://scripts/MonsterBuilder.gd")
	var node = MB.build_monster("slime")
	assert_true(node != null, "MonsterBuilder builds slime")
	node.free()

func test_sword_builder() -> void:
	var SB = load("res://scripts/SwordBuilder.gd")
	var node = SB.build_sword("wood", 1)
	assert_true(node != null, "SwordBuilder builds wood sword")
	node.free()

func test_player_new_features() -> void:
	var f = FileAccess.open("res://scripts/Player.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("signal player_died") != -1, "Player has player_died signal")
	assert_true(src.find("func respawn_player") != -1, "Player has respawn_player")
	assert_true(src.find("is_dead") != -1, "Player has is_dead")
	assert_true(src.find("_canonical_skill") != -1, "Player has canonical skill")

func test_monster_boss_ai() -> void:
	var f = FileAccess.open("res://scripts/Monster.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("func _boss_ai") != -1, "Monster has boss AI")
	assert_true(src.find("telegraph_slam") != -1, "Boss has slam telegraph")
	assert_true(src.find("telegraph_charge") != -1, "Boss has charge telegraph")
	assert_true(src.find("telegraph_meteor") != -1, "Boss has Phase 2 meteor telegraph")

func test_hud_pause_and_cooldowns() -> void:
	var f = FileAccess.open("res://scripts/HUD.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("_build_pause") != -1 or src.find("_build_pause_ui") != -1, "HUD has pause UI")
	assert_true(src.find("_build_bottom_skills") != -1 or src.find("cd_nodes") != -1, "HUD has cooldown UI")
	assert_true(src.find("get_tree().paused") != -1, "HUD toggles pause")

func test_boot_flow_scenes_exist() -> void:
	for p in ["res://scenes/Boot.tscn", "res://scenes/LoadingScreen.tscn", "res://scenes/MainMenu.tscn", "res://scenes/Main.tscn"]:
		assert_true(ResourceLoader.exists(p) or FileAccess.file_exists(p), "scene exists: %s" % p)
	for p in ["res://scripts/Boot.gd", "res://scripts/LoadingScreen.gd", "res://scripts/MainMenu.gd"]:
		assert_true(ResourceLoader.exists(p) or FileAccess.file_exists(p), "script exists: %s" % p)
	for ui_img in ["logo.png", "title.png", "menu_bg.png", "loading_bg.png", "portrait.png", "skill_attack.png", "skill_q.png", "skill_e.png", "skill_r.png", "skill_shift.png"]:
		var up := "res://assets/ui/%s" % ui_img
		assert_true(ResourceLoader.exists(up) or FileAccess.file_exists(up), "ui asset exists: %s" % ui_img)

func test_audio_assets_exist() -> void:
	var all_audio := [
		"menu_theme.wav", "ambient.wav", "boss_theme.wav",
		"hit.wav", "crit.wav", "swing.wav", "skill_q.wav", "skill_e.wav", "skill_r.wav", "dash.wav",
		"levelup.wav", "evolution.wav", "upgrade.wav", "loot.wav",
		"boss.wav", "boss_defeat.wav", "player_hurt.wav", "gameover.wav", "ui.wav"
	]
	for n in all_audio:
		var p = "res://assets/audio/%s" % n
		assert_true(ResourceLoader.exists(p) or FileAccess.file_exists(p), "audio exists: %s" % n)
		var stream = load(p)
		assert_true(stream != null, "audio stream loads: %s" % n)

func test_monster_distinct_ai() -> void:
	var f = FileAccess.open("res://scripts/Monster.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("func _basic_ai") != -1, "Monster has basic_ai")
	for id in ["slime", "goblin", "skeleton", "copper_golem", "orc_berserker", "crimson_drake", "troll", "wraith", "orc"]:
		assert_true(src.find('"%s"' % id) != -1, "Monster AI handles %s" % id)
	assert_true(src.find("func _spawn_boss_defeat_vfx") != -1, "boss defeat vfx")

func test_export_presets() -> void:
	var f = FileAccess.open("res://export_presets.cfg", FileAccess.READ)
	if f == null:
		assert_true(false, "export_presets.cfg readable")
		return
	var src = f.get_as_text()
	f.close()
	assert_true(src.find("Windows Desktop") != -1, "has Windows preset")
	assert_true(src.find("Linux") != -1, "has Linux preset")
	assert_true(src.find("ForjaDeAlmas3D.exe") != -1, "windows exe name")
	assert_true(src.find("ForjaDeAlmas3D.x86_64") != -1, "linux binary name")

# --- REAL RUNTIME BEHAVIORAL TESTS ---
func _make_test_player(world: Node3D) -> Player:
	var p: Player = load("res://scripts/Player.gd").new()
	var pivot := Node3D.new()
	pivot.name = "VisualPivot"
	p.add_child(pivot)
	world.add_child(p)
	p.position = Vector3.ZERO
	return p

func _make_test_monster(world: Node3D, def: Dictionary, wave: int, p: Player, pos: Vector3) -> CharacterBody3D:
	var m: CharacterBody3D = load("res://scenes/Monster.tscn").instantiate()
	world.add_child(m)
	m.position = pos
	m.setup(def, wave, p)
	return m

func test_runtime_combat_and_progression() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)

	assert_eq(p.sword_level, 1, "initial sword level 1")
	assert_eq(p.player_hp, 220, "initial player hp 220")

	# Spawn monster right in front of player (facing +Z by default at yaw=0)
	var slime_def: Dictionary = gd.MONSTER_DEFINITIONS[0]
	var m := _make_test_monster(world, slime_def, 1, p, Vector3(0.0, 0.0, 2.0))
	var start_hp: int = m.hp
	p.perform_attack()
	assert_true(m.hp < start_hp, "perform_attack damages monster in front arc")

	# Skills & legacy wave alias -> canonical swordWave
	p.perform_skill("whirlwind")
	assert_true(float(p.cooldowns["whirlwind"]) > 0.0, "whirlwind enters cooldown")
	p.perform_skill("wave")
	assert_true(float(p.cooldowns["swordWave"]) > 0.0, "legacy 'wave' maps to canonical 'swordWave'")
	p.perform_skill("dash")
	assert_true(float(p.cooldowns["dash"]) > 0.0, "dash enters cooldown")
	assert_true(p.invuln_timer > 0.0, "dash grants brief invulnerability")

	# Level progression & PERMANENT evolution branching
	var evo_state := {"count": 0, "last_id": ""}
	p.evolution_changed.connect(func(t):
		evo_state["count"] += 1
		evo_state["last_id"] = str(t.get("form_id", ""))
	)
	var pts_before := int(p.skill_manager.skill_points)
	p.add_xp(500) # Enough to cross Nv.5
	assert_true(p.sword_level >= 5, "add_xp advances sword_level >= 5")
	assert_true(int(p.skill_manager.skill_points) > pts_before, "level-up grants Skill Points")
	assert_true(int(p.evolution_manager.evolution_xp) > 0, "level-up grants Evolution Essence")
	# Branching is MANUAL and PERMANENT: no auto form change from level anymore
	assert_eq(str(p.evolution_manager.current_form_id), "wood_origin_ancestral_blade", "form stays Stage 01 until a manual permanent commit")
	assert_eq(int(evo_state["count"]), 0, "no auto evolution_changed on level up")
	var skip_res := p.try_evolve("awakening_ironwood_storm_edge")
	assert_true(not bool(skip_res.get("ok", true)), "cannot skip stages (non-direct form rejected)")
	p.add_material("slime_gel", 2)
	var evo_res := p.try_evolve("wood_mineral_copper_root")
	assert_true(bool(evo_res.get("ok", false)), "manual permanent evolution to direct child succeeds")
	assert_eq(int(evo_state["count"]), 1, "evolution_changed emitted on permanent commit")
	assert_eq(str(evo_state["last_id"]), "wood_mineral_copper_root", "signal carries new form id")
	assert_eq(str(p.evolution_manager.current_form_id), "wood_mineral_copper_root", "current_form_id updated")
	assert_true(p.evolution_manager.is_form_discarded("wood_verdant_living_bough"), "sibling branch sealed permanently")
	assert_true(not bool(p.try_evolve("wood_verdant_living_bough").get("ok", true)), "sealed sibling cannot be chosen later")
	assert_eq(str(p.current_tier.get("form_id", "")), "wood_mineral_copper_root", "legacy tier view reflects committed form")
	assert_true(int(p.stats["damage"]) > 0, "stats recalculated after evolution")

	# Forge upgrades
	p.gold = 500
	var base_dmg := int(p.stats["damage"])
	assert_true(p.buy_upgrade("sharpness", 25), "buy_upgrade sharpness succeeds")
	assert_eq(int(p.upgrades["sharpness"]), 1, "sharpness level 1")
	assert_true(int(p.stats["damage"]) > base_dmg, "sharpness increases damage")

	# Player death & respawn
	var died_state := {"died": false}
	p.player_died.connect(func(): died_state["died"] = true)
	p.invuln_timer = 0.0
	p.dash_timer = 0.0
	p.take_player_damage(99999)
	assert_true(bool(died_state["died"]), "lethal damage emits player_died")
	assert_true(p.is_dead, "player flagged is_dead")
	p.respawn_player()
	assert_true(not p.is_dead, "respawn clears is_dead")
	assert_eq(p.player_hp, p.player_max_hp, "respawn restores full HP")

	world.free()
	gd.free()

func test_runtime_rpg_inventory_and_crafting() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)

	# Craft grip_oak (needs 40g + 3 gel_cristalino) — auto-equips when grip slot is empty
	var hp_before := p.player_max_hp
	var xp_mult_before := float(p.stats["xp_mult"])
	p.gold = 200
	p.add_material("gel_cristalino", 3)
	assert_eq(int(p.materials["gel_cristalino"]), 3, "add_material tracks count")
	assert_true(p.can_craft_relic("grip_oak"), "can_craft_relic true when materials & gold met")
	assert_true(p.craft_relic("grip_oak"), "craft_relic succeeds")
	assert_eq(p.gold, 160, "craft_relic deducts recipe gold")
	assert_true(not p.materials.has("gel_cristalino"), "craft_relic consumes exact materials")
	assert_true(p.inventory_items.has("grip_oak"), "crafted relic added to inventory_items")

	# Equipping & unequipping modifies live stats
	assert_true(p.equip_relic("grip_oak"), "equip_relic equips grip slot")
	assert_eq(str(p.equipped["grip"]), "grip_oak", "grip slot holds grip_oak")
	assert_true(p.player_max_hp == hp_before + 35, "grip_oak raises max HP by +35")
	assert_true(float(p.stats["xp_mult"]) > xp_mult_before, "grip_oak raises xp_mult")

	# Equipping damage relic increases damage
	var dmg_before := int(p.stats["damage"])
	p.add_item("grip_crusader")
	assert_true(p.equip_relic("grip_crusader"), "equip_relic swaps grip to grip_crusader")
	assert_true(int(p.stats["damage"]) > dmg_before, "grip_crusader raises damage")

	p.unequip_slot("grip")
	assert_eq(str(p.equipped["grip"]), "", "unequip_slot clears slot")
	assert_eq(int(p.stats["damage"]), dmg_before, "unequip restores base damage")

	# Consumables: potion heals missing HP, elixir grants XP
	p.player_hp = 80
	assert_true(p.use_consumable("potion_hp"), "use_consumable potion_hp succeeds when hurt")
	assert_true(p.player_hp > 80, "potion_hp restores HP")
	assert_true(p.buy_consumable("elixir_xp"), "buy_consumable elixir_xp succeeds")
	var xp_before := p.current_xp
	var lvl_before := p.sword_level
	assert_true(p.use_consumable("elixir_xp"), "use_consumable elixir_xp succeeds")
	assert_true(p.sword_level > lvl_before or p.current_xp > xp_before, "elixir_xp grants XP")

	world.free()

func test_runtime_malakor_phases_and_rewards() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)

	var boss_def: Dictionary = gd.MONSTER_DEFINITIONS[6] # demon_lord Malakor
	var boss := _make_test_monster(world, boss_def, 3, p, Vector3(0.0, 0.0, 6.0))
	assert_eq(boss.boss_phase, 1, "Malakor starts in Phase 1")
	p.stats["crit_chance"] = 0.0 # Deterministic non-crit damage for phase threshold check

	var tracker := {"phase": 1, "reward_events": 0}
	boss.boss_phase_changed.connect(func(ph): tracker["phase"] = ph)
	boss.boss_defeated_reward.connect(func(_s): tracker["reward_events"] += 1)

	# Drop below 50% HP -> Phase 2
	var half_dmg := int(boss.max_hp * 0.55)
	boss.take_damage(half_dmg, p)
	assert_eq(boss.boss_phase, 2, "Malakor enters Phase 2 at <= 50% HP")
	assert_eq(int(tracker["phase"]), 2, "boss_phase_changed(2) signal emitted")

	# Lethal hit + duplicate lethal call (anti-double-reward check)
	var kills_before := p.kills
	boss.take_damage(boss.hp + 500, p, true)
	boss.take_damage(999, p, true)
	assert_eq(p.kills, kills_before + 1, "anti-duplicate _dead guard counts 1 kill")
	assert_eq(p.bosses_defeated, 1, "bosses_defeated incremented once")
	assert_eq(int(tracker["reward_events"]), 1, "boss_defeated_reward emitted once")
	assert_true(int(p.materials.get("corazon_abismo", 0)) >= 1, "Malakor guarantees Corazon de Malakor drop")
	assert_true(p.evolution_manager.has_world_event("defeated_malakor"), "Malakor defeat records permanent evolution world event")

	world.free()
	gd.free()

func test_save_roundtrip_and_v1_migration() -> void:
	var ss = load("res://scripts/SaveSystem.gd").new()
	assert_eq(ss.SAVE_VERSION, 3, "SaveSystem SAVE_VERSION is 3")

	var world := Node3D.new()
	root.add_child(world)
	var p1 := _make_test_player(world)
	p1.jump_to_level(12)
	p1.gold = 777
	p1.kills = 42
	p1.wave = 4
	p1.wave_kills = 5
	p1.bosses_defeated = 1
	p1.wielder_mode = "knight_wielder"
	p1.auto_hunt = true
	p1.upgrades["sharpness"] = 3
	p1.upgrades["vampirism"] = 2
	p1.add_material("escama_escarlata", 4)
	p1.add_item("rune_wind")
	p1.equip_relic("rune_wind")
	p1.consumables["potion_hp"] = 5
	# v3: commit a permanent evolution + learn a skill before saving
	p1.add_material("slime_gel", 2)
	var evo_res := p1.try_evolve("wood_mineral_copper_root")
	assert_true(bool(evo_res.get("ok", false)), "p1 permanent evolution committed pre-save")
	assert_true(bool(p1.skill_manager.unlock_skill("phys_pas_edge", p1.evolution_manager.get_current_stage(), p1.evolution_manager.get_current_lineage()).get("ok", false)), "p1 learned phys_pas_edge pre-save")

	var tmp_v2 := "user://unit_test_save_v2.json"
	ss.save_game(p1, tmp_v2)

	var p2 := _make_test_player(world)
	assert_true(ss.load_game(p2, tmp_v2), "load_game v2 succeeds")
	assert_eq(p2.sword_level, 12, "roundtrip sword_level")
	assert_eq(p2.gold, 777, "roundtrip gold")
	assert_eq(p2.kills, 42, "roundtrip kills")
	assert_eq(p2.wave, 4, "roundtrip wave")
	assert_eq(p2.bosses_defeated, 1, "roundtrip bosses_defeated")
	assert_eq(p2.wielder_mode, "knight_wielder", "roundtrip wielder_mode")
	assert_eq(p2.auto_hunt, true, "roundtrip auto_hunt")
	assert_eq(int(p2.upgrades["sharpness"]), 3, "roundtrip sharpness")
	assert_eq(int(p2.materials.get("escama_escarlata", 0)), 4, "roundtrip materials")
	assert_true(p2.inventory_items.has("rune_wind"), "roundtrip inventory_items")
	assert_eq(str(p2.equipped["rune"]), "rune_wind", "roundtrip equipped rune")
	assert_eq(int(p2.consumables["potion_hp"]), 5, "roundtrip consumables")
	# v3: permanent evolution & skill progression survive the roundtrip verbatim
	assert_eq(str(p2.evolution_manager.current_form_id), "wood_mineral_copper_root", "v3 roundtrip preserves committed permanent form (NOT level-derived)")
	assert_true(p2.evolution_manager.is_form_discarded("wood_verdant_living_bough"), "v3 roundtrip preserves sealed sibling branches")
	assert_true(p2.skill_manager.is_unlocked("phys_pas_edge"), "v3 roundtrip preserves learned skills")
	assert_eq(int(p2.skill_manager.skill_points), int(p1.skill_manager.skill_points), "roundtrip skill points")
	assert_eq(str(p2.skill_manager.equipped_slots.get("Q", "")), "whirlwind", "roundtrip active slot assignment")
	assert_eq(str(p2.current_tier.get("form_id", "")), "wood_mineral_copper_root", "legacy tier view reflects restored evolution")

	# Legacy v1 migration test
	var tmp_v1 := "user://unit_test_save_v1.json"
	var v1_payload := {
		"version": 1,
		"sword_level": 6,
		"current_xp": 20,
		"gold": 310,
		"kills": 15,
		"wave": 2,
		"wave_kills": 3,
		"wielder_mode": "living_sword",
		"upgrades": {"sharpness": 2},
		"settings": {"volume": 0.42, "quality": "low", "audio_muted": false}
	}
	var wf := FileAccess.open(tmp_v1, FileAccess.WRITE)
	wf.store_string(JSON.stringify(v1_payload))
	wf.close()

	var p3 := _make_test_player(world)
	assert_true(ss.load_game(p3, tmp_v1), "v1 save migrates cleanly into v2 loader")
	assert_eq(p3.sword_level, 6, "migrated v1 sword_level")
	assert_eq(p3.gold, 310, "migrated v1 gold")
	assert_eq(int(p3.upgrades["sharpness"]), 2, "migrated v1 sharpness")
	assert_eq(int(p3.consumables.get("potion_hp", 0)), 2, "migrated v1 gets default potions")
	assert_eq(str(p3.evolution_manager.current_form_id), "wood_mineral_copper_root", "v1 migration synthesizes level-appropriate evolution state")
	assert_true(int(p3.skill_manager.skill_points) >= 1, "v1 migration grants skill points")
	assert_true(absf(float(ss.settings["master_volume"]) - 0.42) < 0.001, "migrated v1 volume -> master_volume")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_v2))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_v1))
	world.free()
	ss.free()

func test_save_settings_and_audio_manager() -> void:
	var ss = load("res://scripts/SaveSystem.gd").new()
	var tmp_cfg := "user://unit_test_settings.json"
	ss.settings["quality"] = "high"
	ss.settings["audio_muted"] = true
	ss.settings["master_volume"] = 0.65
	ss.settings["music_volume"] = 0.40
	ss.settings["sfx_volume"] = 0.90
	ss.save_settings(tmp_cfg)

	var ss2 = load("res://scripts/SaveSystem.gd").new()
	ss2.load_settings_only(tmp_cfg)
	assert_eq(str(ss2.settings["quality"]), "high", "persisted quality setting")
	assert_eq(bool(ss2.settings["audio_muted"]), true, "persisted audio_muted setting")
	assert_true(absf(float(ss2.settings["music_volume"]) - 0.40) < 0.001, "persisted music_volume")
	assert_true(absf(float(ss2.settings["sfx_volume"]) - 0.90) < 0.001, "persisted sfx_volume")

	var am = load("res://scripts/AudioManager.gd").new()
	root.add_child(am)
	am.apply_settings_dict(ss2.settings)
	assert_true(AudioServer.get_bus_index("Music") != -1, "AudioManager creates Music bus")
	assert_true(AudioServer.get_bus_index("SFX") != -1, "AudioManager creates SFX bus")
	assert_eq(am.muted, true, "AudioManager applies muted state")
	am.set_muted(false)

	DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_cfg))
	am.free()
	ss.free()
	ss2.free()

func test_arena_decor_quality_levels() -> void:
	var decor = load("res://scripts/ArenaDecor.gd").new()
	root.add_child(decor)
	decor.apply_quality("low")
	decor.apply_quality("high")
	decor.update_decor(1.25, Color(0.3, 0.8, 1.0))
	assert_true(decor.get_child_count() >= 10, "ArenaDecor builds 3D sanctuary landmarks")
	decor.free()

func test_hud_layout_and_overlays_all_resolutions() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)
	var hud = load("res://scripts/HUD.gd").new()
	root.add_child(hud)
	hud.connect_player(p)
	hud.boss_panel.visible = true
	hud.ui_root.set_anchors_preset(Control.PRESET_TOP_LEFT)

	var resolutions := [
		Vector2(1280, 720),
		Vector2(1366, 768),
		Vector2(1600, 900),
		Vector2(1920, 1080),
	]
	for res in resolutions:
		hud.ui_root.size = res
		hud._layout_responsive()
		var tag := "%dx%d" % [int(res.x), int(res.y)]

		var panels: Array = [
			["TopLeft", hud.top_left_panel],
			["QuickPills", hud.quick_pills_bar],
			["Objective", hud.objective_panel],
			["TopCenter", hud.top_center_panel],
			["TopRight", hud.top_right_bar],
			["Minimap", hud.minimap_panel],
			["Forge", hud.forge_panel],
			["BottomSkills", hud.bottom_skills_panel],
			["Log", hud.log_panel_box],
			["Branding", hud.branding_label],
			["BossBar", hud.boss_panel],
		]

		# 1. Every HUD panel strictly inside viewport bounds
		for item in panels:
			var ctrl: Control = item[1]
			var r := Rect2(ctrl.position, ctrl.size)
			var inside: bool = r.position.x >= 0.0 and r.position.y >= 0.0 and (r.position.x + r.size.x) <= res.x + 0.5 and (r.position.y + r.size.y) <= res.y + 0.5
			assert_true(inside, "HUD %s within bounds at %s (%s)" % [str(item[0]), tag, str(r)])

		# 2. Zero pairwise overlaps among primary HUD panels
		for i in range(panels.size()):
			for j in range(i + 1, panels.size()):
				var r1 := Rect2(panels[i][1].position, panels[i][1].size).grow(-1.0)
				var r2 := Rect2(panels[j][1].position, panels[j][1].size).grow(-1.0)
				assert_true(not r1.intersects(r2), "No overlap %s vs %s at %s" % [str(panels[i][0]), str(panels[j][0]), tag])

		# 3. Modal overlays fit cleanly within viewport at every resolution
		for ov_pair in [["Settings", hud.settings_panel], ["Inventory", hud.inventory_panel], ["Stats", hud.stats_panel], ["GameOver", hud.game_over_panel]]:
			var ov: Control = ov_pair[1]
			var orct := Rect2(ov.position, ov.size)
			var ov_ok: bool = orct.position.x >= 16.0 and orct.position.y >= 16.0 and (orct.position.x + orct.size.x) <= res.x - 16.0 and (orct.position.y + orct.size.y) <= res.y - 16.0
			assert_true(ov_ok, "Modal %s fits cleanly at %s" % [str(ov_pair[0]), tag])

	# Verify overlay content generation & mutual exclusion
	hud._toggle_inventory()
	assert_true(hud.inventory_panel.visible, "Inventory modal opens")
	assert_true(hud.inv_left_box.get_child_count() > 3, "Inventory left column populated")
	assert_true(hud.inv_right_box.get_child_count() > 8, "Inventory right column populated")

	hud._toggle_stats()
	assert_true(hud.stats_panel.visible and not hud.inventory_panel.visible, "Stats modal replaces Inventory modal")
	assert_true(hud.stats_label.text.find("ATRIBUTOS DE COMBATE") != -1, "Stats text populated")

	hud._toggle_settings()
	assert_true(hud.settings_panel.visible and not hud.stats_panel.visible, "Settings modal replaces Stats modal")

	hud.free()
	world.free()

func _collect_meshes_recursive(n: Node, out: Array) -> void:
	if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
		out.append(n)
	for c in n.get_children():
		_collect_meshes_recursive(c, out)

func test_pilot_sword_3d_glb_and_pbr() -> void:
	var base_dir := "res://assets/models/swords/wood_ancestral"
	var pbr_maps := [
		"%s/wood_ancestral_basecolor.png" % base_dir,
		"%s/wood_ancestral_roughness.png" % base_dir,
		"%s/wood_ancestral_metallic.png" % base_dir,
		"%s/wood_ancestral_normal.png" % base_dir,
		"%s/wood_ancestral_emission.png" % base_dir,
	]
	for mp in pbr_maps:
		assert_true(ResourceLoader.exists(mp), "Pilot PBR map exists: %s" % mp)
		var tex = load(mp)
		assert_true(tex is Texture2D, "Pilot PBR map loads as Texture2D: %s" % mp)
		if tex is Texture2D:
			assert_eq((tex as Texture2D).get_width(), 2048, "Pilot PBR map width 2048 (remaster): %s" % mp)
			assert_eq((tex as Texture2D).get_height(), 2048, "Pilot PBR map height 2048 (remaster): %s" % mp)

	var glb_path := "%s/sword_01_wood_ancestral.glb" % base_dir
	assert_true(ResourceLoader.exists(glb_path), "Pilot GLB exists")
	var packed = load(glb_path)
	assert_true(packed is PackedScene, "Pilot GLB imports as PackedScene")

	var gd = root.get_node_or_null("GameData")
	var ml = load("res://scripts/ModelLoader.gd")
	var built: Node3D = ml.build_sword_visual(gd.SWORD_EVOLUTIONS[0], 1)
	assert_true(built != null and built.name == "SwordGLB", "Stage 01 builds SwordGLB via ModelLoader")
	var meshes: Array = []
	_collect_meshes_recursive(built, meshes)
	assert_eq(meshes.size(), 7, "Pilot GLB preserves 7 individual modeled sub-parts")
	for mi in meshes:
		var m: Mesh = (mi as MeshInstance3D).mesh
		assert_true((mi as MeshInstance3D).material_override == null, "Pilot GLB sub-part preserves authored PBR material without flat override: %s" % mi.name)
		var arrays := m.surface_get_arrays(0)
		var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
		var norms: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
		assert_true(uvs.size() > 0, "Sub-part has UVs: %s" % mi.name)
		assert_true(norms.size() > 0, "Sub-part has normals: %s" % mi.name)
		var surf_mat: Material = m.surface_get_material(0)
		assert_true(surf_mat is BaseMaterial3D, "Sub-part has authored BaseMaterial3D: %s" % mi.name)
	built.free()

# --- PHASE B: PERMANENT EVOLUTION & 72-SKILL SYSTEM ---

func test_evolution_catalog_and_validator() -> void:
	var cat := EvolutionCatalog.new(true)
	assert_eq(cat.get_total_form_count(), 118, "evolution catalog loads 118 forms")
	assert_eq(cat.eras.size(), 6, "catalog defines 6 Eras")
	assert_eq(str(cat.root_form_id), "wood_origin_ancestral_blade", "root form id")
	assert_true(cat.has_form("wood_origin_ancestral_blade"), "root form exists")
	assert_eq(cat.resolve_id("wood"), "wood_origin_ancestral_blade", "legacy alias 'wood' resolves to canonical form")
	for st in range(1, 25):
		assert_true(cat.get_forms_for_stage(st).size() >= 1, "stage %02d has forms" % st)
	var root: Dictionary = cat.get_form("wood_origin_ancestral_blade")
	assert_eq(int(root.get("stage", 0)), 1, "root is Stage 01")
	assert_eq(str(root.get("model_path", "")), "res://assets/models/swords/wood_ancestral/sword_01_wood_ancestral.glb", "root uses the verified pilot GLB")
	assert_true(root.get("aura_color") is Color, "catalog colors normalized to Color objects")
	assert_eq(cat.get_next_forms("wood_origin_ancestral_blade").size(), 3, "root offers 3 permanent branches")
	assert_true(str(root.get("protagonist_identity", "")) == "sentient_sword", "root preserves sentient sword identity")
	var val := EvolutionValidator.validate_graph(cat)
	if not bool(val.get("valid", false)):
		for e in val.get("errors", []):
			print("  GRAPH ERROR: ", e)
	assert_true(bool(val.get("valid", false)), "automated graph validation passes (no dead ends, no orphans, no cycles)")
	assert_eq(int(val.get("stats", {}).get("total_forms", 0)), 118, "validator counts 118 forms")
	assert_eq(int(val.get("stats", {}).get("hybrid_forms", 0)), 5, "validator counts 5 milestone hybrid forms")
	assert_true(bool(cat.get_form("hybrid_celestial_abyss_eclipse").get("is_hybrid", false)), "milestone hybrid form flagged")
	var hybrid: Dictionary = cat.get_form("hybrid_celestial_abyss_eclipse")
	assert_true((hybrid.get("parent_forms", []) as Array).size() >= 2, "hybrid form has multiple parents")

func test_evolution_permanent_branching_rules() -> void:
	var em := EvolutionManager.new()
	assert_eq(str(em.current_form_id), "wood_origin_ancestral_blade", "manager starts at root form")
	assert_eq(em.get_available_branch_options().size(), 3, "3 branch options at root")
	var ctx := {"sword_level": 1, "materials": {}, "unlocked_skills": {}}
	var ev := em.evaluate_unlock_conditions("wood_mineral_copper_root", ctx)
	assert_true(not bool(ev.get("can_evolve", true)), "unlock blocked at low level")
	assert_true((ev.get("reasons", []) as Array).size() >= 1, "blocked reasons reported")
	assert_true((ev.get("checks", []) as Array).size() >= 3, "structured condition checks reported (5-condition evaluator)")
	ctx["sword_level"] = 3
	ctx["materials"] = {"slime_gel": 2}
	em.add_evolution_xp(40)
	var ev2 := em.evaluate_unlock_conditions("wood_mineral_copper_root", ctx)
	assert_true(bool(ev2.get("can_evolve", false)), "conditions met -> can evolve")
	assert_true(not bool(em.commit_permanent_evolution("awakening_ironwood_storm_edge", ctx).get("ok", true)), "cannot skip stages")
	var res := em.commit_permanent_evolution("wood_mineral_copper_root", ctx, ctx["materials"])
	assert_true(bool(res.get("ok", false)), "permanent commit succeeds")
	assert_eq(int(ctx["materials"].get("slime_gel", 0)), 0, "required materials consumed on commit")
	assert_eq(str(em.current_form_id), "wood_mineral_copper_root", "current_form_id committed")
	assert_eq(em.evolution_history.size(), 2, "evolution history records the choice")
	assert_eq(em.get_current_stage(), 2, "current stage advanced to 02")
	assert_true(em.is_form_discarded("wood_verdant_living_bough"), "sibling sealed (verdant bough)")
	assert_true(em.is_form_discarded("wood_charred_ash_thorn"), "sibling sealed (ash thorn)")
	assert_true(not bool(em.evaluate_unlock_conditions("wood_verdant_living_bough", ctx).get("can_evolve", true)), "sealed sibling evaluated as locked")
	assert_true(not bool(em.commit_permanent_evolution("wood_verdant_living_bough", ctx).get("ok", true)), "commit to sealed sibling rejected")
	assert_true(em.is_form_in_history("wood_mineral_copper_root"), "history contains current form")
	var d := em.to_dict()
	var em2 := EvolutionManager.new()
	em2.from_dict(d)
	assert_eq(str(em2.current_form_id), str(em.current_form_id), "state roundtrip: form id")
	assert_eq(em2.evolution_history.size(), em.evolution_history.size(), "state roundtrip: history")
	assert_eq(em2.discarded_form_ids.size(), em.discarded_form_ids.size(), "state roundtrip: discarded branches")
	assert_eq(int(em2.evolution_xp), int(em.evolution_xp), "state roundtrip: evolution essence")

func test_skill_catalog_and_progression() -> void:
	var sc := SkillCatalog.new(true)
	var v := sc.validate_catalog()
	if not bool(v.get("valid", false)):
		for e in v.get("errors", []):
			print("  SKILL ERROR: ", e)
	assert_true(bool(v.get("valid", false)), "skill catalog validates (prereqs, trees, types)")
	assert_eq(int(v.get("total_skills", 0)), 72, "72 skills")
	assert_eq(int(v.get("active_skills", 0)), 36, "36 active skills")
	assert_eq(int(v.get("passive_skills", 0)), 36, "36 passive skills")
	assert_eq(sc.trees.size(), 6, "6 skill trees")
	assert_true(sc.has_skill("wave"), "legacy 'wave' alias resolves")
	assert_eq(sc.canonical_id("wave"), "swordWave", "'wave' -> canonical 'swordWave'")
	assert_true(sc.has_skill("whirlwind") and sc.has_skill("swordWave") and sc.has_skill("ultimate") and sc.has_skill("dash"), "canonical starter skills present in catalog")
	var sm := SkillTreeManager.new()
	assert_eq(sm.unlocked_skills.size(), 4, "4 starter skills pre-unlocked")
	assert_true(sm.is_unlocked("whirlwind") and sm.is_unlocked("swordWave") and sm.is_unlocked("ultimate") and sm.is_unlocked("dash"), "starter skills canonical")
	var chk := sm.can_unlock_skill("phys_pas_edge", 1, "origin")
	assert_true(bool(chk.get("ok", false)), "tier-1 passive unlockable with starter points")
	assert_true(not bool(sm.can_unlock_skill("phys_pas_tempo", 1, "origin").get("ok", true)), "prerequisite gate blocks chained skill")
	assert_true(not bool(sm.can_unlock_skill("leg_pas_spark", 1, "origin").get("ok", true)), "min_stage gate blocks stage-locked skill")
	var locked := sm.can_unlock_skill("phys_act_quake", 15, "origin")
	var found_lineage_block := false
	for r in locked.get("reasons", []):
		if str(r).find("linaje") != -1:
			found_lineage_block = true
	assert_true(found_lineage_block, "lineage-exclusivity gate reports origin lineage lock")
	var allowed := sm.can_unlock_skill("phys_act_quake", 15, "blessed")
	var blocked_in_allowed := false
	for r in allowed.get("reasons", []):
		if str(r).find("linaje") != -1:
			blocked_in_allowed = true
	assert_true(not blocked_in_allowed, "blessed lineage passes exclusivity check for blessed/cursed skill")
	sm.add_skill_points(10)
	assert_eq(int(sm.skill_points), 11, "add_skill_points accumulates (1 starter + 10)")
	assert_true(bool(sm.unlock_skill("phys_pas_edge", 1, "origin").get("ok", false)), "unlock_skill succeeds")
	assert_true(sm.is_unlocked("phys_pas_edge"), "passive learned")
	assert_eq(int(sm.skill_points), 10, "cost deducted on unlock")
	var mods := sm.get_aggregated_passive_modifiers("origin")
	assert_true(absf(float(mods.get("physical_damage_pct", 0.0)) - 0.08) < 0.0001, "passive modifiers aggregated (+8% phys damage)")
	assert_true(sm.equip_active_skill("Q", "whirlwind"), "active slot assignment works")
	assert_eq(str(sm.get_equipped_skill_for_slot("Q")), "whirlwind", "slot holds assigned skill")
	assert_true(not sm.equip_active_skill("Q", "phys_pas_edge"), "cannot equip passive into active slot")
	assert_true(not sm.equip_active_skill("Z", "whirlwind"), "invalid slot rejected")
	var sd := sm.to_dict()
	var sm2 := SkillTreeManager.new()
	sm2.from_dict(sd)
	assert_true(sm2.is_unlocked("phys_pas_edge"), "skill state roundtrip preserves unlocks")
	assert_eq(str(sm2.equipped_slots.get("Q", "")), "whirlwind", "skill state roundtrip preserves slots")

func test_sword_stats_calculator_17_attributes() -> void:
	var cat := EvolutionCatalog.new(true)
	var form := cat.get_form("wood_origin_ancestral_blade")
	var calc := SwordStatsCalculator.calculate_stats(form, 1, {}, {}, {})
	for k in ["physical_damage", "elemental_damage", "attack_speed", "attack_range", "crit_chance", "crit_damage", "armor_penetration", "life_steal", "max_hp", "defense", "elemental_resistance", "energy_regen", "max_energy", "move_speed", "cdr", "status_chance", "soul_absorption"]:
		assert_true(calc.has(k), "17-stat key present: %s" % k)
	assert_true(int(calc["damage"]) > 0, "legacy 'damage' key derived (phys + 0.45*elem)")
	assert_eq(int(calc["max_hp"]), 120, "Stage 01 form base HP")
	assert_true(int(calc["max_energy"]) == 100, "Stage 01 base energy")
	var c10 := SwordStatsCalculator.calculate_stats(form, 10, {}, {}, {})
	assert_true(float(c10["physical_damage"]) > float(calc["physical_damage"]), "sword level scaling raises physical damage")
	assert_true(int(c10["max_hp"]) > int(calc["max_hp"]), "sword level scaling raises max HP")
	var cU := SwordStatsCalculator.calculate_stats(form, 1, {"sharpness": 5.0, "vitality": 3.0}, {}, {})
	assert_true(float(cU["physical_damage"]) > float(calc["physical_damage"]), "forge sharpness raises damage")
	assert_true(int(cU["max_hp"]) > int(calc["max_hp"]), "vitality raises max HP")
	var cR := SwordStatsCalculator.calculate_stats(form, 1, {}, {"max_hp": 35.0, "damage_pct": 0.2}, {})
	assert_eq(int(cR["max_hp"]), int(calc["max_hp"]) + 35, "equipped relic max_hp bonus applied")
	assert_true(float(cR["physical_damage"]) > float(calc["physical_damage"]), "equipped relic damage_pct applied")
	var cP := SwordStatsCalculator.calculate_stats(form, 1, {}, {}, {"physical_damage_pct": 0.08, "crit_chance_add": 0.05})
	assert_true(float(cP["physical_damage"]) > float(calc["physical_damage"]), "unlocked passive modifiers applied")
	assert_true(absf(float(cP["crit_chance"]) - (float(calc["crit_chance"]) + 0.05)) < 0.0001, "passive crit additive")
	var cC := SwordStatsCalculator.calculate_stats(form, 1, {"fortune": 10.0}, {"crit_chance": 0.9}, {"crit_chance_add": 0.5})
	assert_true(float(cC["crit_chance"]) <= 0.85, "crit chance clamped to 0.85")
	var cD := SwordStatsCalculator.calculate_stats(form, 40, {}, {"cd_reduction": 0.6}, {"cdr_add": 0.4})
	assert_true(float(cD["cdr"]) <= 0.45, "cdr clamped to 0.45")
	# Blessed vs cursed trade-offs differ on the same stage
	var blessed := cat.get_form("blessed_auric_bastion_claymore")
	var cursed := cat.get_form("cursed_abyssal_guillotine_edge")
	var cb := SwordStatsCalculator.calculate_stats(blessed, 1, {}, {}, {})
	var cc := SwordStatsCalculator.calculate_stats(cursed, 1, {}, {}, {})
	assert_true(float(cb["physical_damage"]) != float(cc["physical_damage"]), "branch trade-offs produce distinct stat profiles")

func test_save_v3_permanent_evolution_survival() -> void:
	var ss = load("res://scripts/SaveSystem.gd").new()
	var world := Node3D.new()
	root.add_child(world)
	var p1 := _make_test_player(world)
	p1.jump_to_level(9)
	p1.add_material("slime_gel", 2)
	assert_true(bool(p1.try_evolve("wood_mineral_copper_root").get("ok", false)), "permanent evolution committed pre-save")
	var tmp_v3 := "user://unit_test_save_v3.json"
	assert_true(ss.save_game(p1, tmp_v3), "v3 save succeeds")

	# CRITICAL ACCEPTANCE: a v3 save's evolution_state must NEVER be re-derived from
	# sword_level. Tamper the file so sword_level points at a different legacy tier.
	var rf := FileAccess.open(tmp_v3, FileAccess.READ)
	var raw = JSON.parse_string(rf.get_as_text())
	rf.close()
	assert_true(typeof(raw) == TYPE_DICTIONARY and (raw as Dictionary).has("evolution_state"), "v3 payload contains evolution_state")
	(raw as Dictionary)["sword_level"] = 1
	(raw as Dictionary)["current_xp"] = 0
	var wf := FileAccess.open(tmp_v3, FileAccess.WRITE)
	wf.store_string(JSON.stringify(raw))
	wf.close()

	var p2 := _make_test_player(world)
	assert_true(ss.load_game(p2, tmp_v3), "tampered v3 load succeeds")
	assert_eq(int(p2.sword_level), 1, "tampered level loaded verbatim")
	assert_eq(str(p2.evolution_manager.current_form_id), "wood_mineral_copper_root", "PERMANENT choice survives: form NOT reconstructed from level")
	assert_true(p2.evolution_manager.is_form_discarded("wood_charred_ash_thorn"), "discarded branches survive reload")
	assert_true(p2.evolution_manager.evolution_history.size() >= 2, "evolution history survives reload")

	# Legacy v2 payload (no evolution_state) migrates with a level-mapped initial state
	var v2_payload := {
		"version": 2, "sword_level": 21, "current_xp": 0, "gold": 100, "kills": 3,
		"wave": 2, "wave_kills": 1, "wielder_mode": "living_sword",
		"upgrades": {"sharpness": 1}, "bosses_defeated": 1,
	}
	var tmp_v2 := "user://unit_test_save_v2_migration.json"
	var wf2 := FileAccess.open(tmp_v2, FileAccess.WRITE)
	wf2.store_string(JSON.stringify(v2_payload))
	wf2.close()
	var p3 := _make_test_player(world)
	assert_true(ss.load_game(p3, tmp_v2), "v2 payload migrates into v3")
	assert_eq(str(p3.evolution_manager.current_form_id), "blessed_auric_bastion_claymore", "v2 migration maps level-appropriate initial form")
	assert_true(int((p3.evolution_manager.evolution_history[0] as Dictionary).get("migrated_from_v2", 0)) == 1, "migration flagged in evolution history")
	assert_true(p3.evolution_manager.has_world_event("defeated_malakor"), "v2 boss history becomes world event")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_v3))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_v2))
	world.free()
	ss.free()

func test_player_evolution_integration() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)
	assert_true(p.evolution_manager != null and p.skill_manager != null, "player evolution & skill managers initialized")
	assert_eq(str(p.current_tier.get("form_id", "")), "wood_origin_ancestral_blade", "player starts as Stage 01 pilot form")
	assert_eq(int(p.stats["max_energy"]), 100, "energy baseline from form stats")
	var e0 := float(p.energy)
	p.perform_skill("whirlwind")
	assert_true(float(p.energy) < e0, "active skill drains spiritual energy")
	var pts0 := int(p.skill_manager.skill_points)
	p.add_xp(120)
	assert_true(p.sword_level >= 3, "leveled up via XP")
	assert_true(int(p.skill_manager.skill_points) > pts0, "skill points granted on level up")
	assert_eq(str(p.evolution_manager.current_form_id), "wood_origin_ancestral_blade", "no auto form change from level")
	p.add_material("slime_gel", 2)
	var res := p.try_evolve("wood_mineral_copper_root")
	assert_true(bool(res.get("ok", false)), "player.try_evolve commits permanent evolution")
	assert_eq(str(p.current_tier.get("id", "")), "copper", "legacy view id switches to copper alias")
	assert_true(int(p.stats["damage"]) > 0, "stats recalculated for the new form")
	var ess0 := int(p.evolution_manager.evolution_xp)
	p.add_kill()
	assert_true(int(p.evolution_manager.evolution_xp) > ess0, "kills grant evolution essence")
	assert_eq(str(p.evolution_manager.get_current_lineage()), str(p.evolution_manager.catalog.get_form("wood_mineral_copper_root").get("lineage", "")), "current lineage matches committed form lineage")
	world.free()

func test_evolution_skill_ui_panels() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)
	var hud = load("res://scripts/HUD.gd").new()
	root.add_child(hud)
	hud.connect_player(p)
	assert_true(hud.evolution_panel != null and hud.skill_panel != null, "Evolution & Skill modal panels built")
	assert_true(not hud.evolution_panel.visible and not hud.skill_panel.visible, "new modals hidden by default")
	hud._toggle_evolution()
	assert_true(hud.evolution_panel.visible, "Evolution modal opens via toggle")
	assert_true(hud.evolution_list_vb.get_child_count() > 0, "Evolution rows populated")
	var era1_count: int = p.evolution_manager.catalog.get_forms_for_era(1).size()
	assert_eq(hud.evolution_list_vb.get_child_count(), era1_count, "Era I rows match catalog forms")
	hud._toggle_skill_tree()
	assert_true(hud.skill_panel.visible and not hud.evolution_panel.visible, "Skill modal replaces Evolution modal")
	var tree_skills: int = p.skill_manager.catalog.get_skills_for_tree("physical_mastery").size()
	assert_eq(hud.skill_list_vb.get_child_count(), tree_skills, "Skill rows match catalog tree")
	hud._close_sub_modals()
	assert_true(not hud.skill_panel.visible and not hud.evolution_panel.visible, "_close_sub_modals closes the new modals")
	hud.ui_root.size = Vector2(1280, 720)
	hud._layout_responsive()
	for pair in [["Evolution", hud.evolution_panel], ["SkillTree", hud.skill_panel]]:
		var ov: Control = pair[1]
		var ok: bool = ov.position.x >= 16.0 and ov.position.y >= 16.0 and (ov.position.x + ov.size.x) <= 1264.0 and (ov.position.y + ov.size.y) <= 704.0
		assert_true(ok, "Modal %s fits cleanly at 1280x720" % str(pair[0]))
	# Evolution rows rebuild after committing a permanent evolution in-game
	hud._toggle_evolution()
	assert_true(hud.evolution_panel.visible, "Evolution modal reopens")
	hud._close_sub_modals()
	hud.free()
	world.free()

func test_skill_slots_world_events_and_energy() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var p := _make_test_player(world)
	var sm = p.skill_manager

	# Learn an extra active skill and EQUIP it into Q — input routing must follow the loadout
	assert_true(bool(sm.unlock_skill("def_act_bark", 1, "origin").get("ok", false)), "learn def_act_bark with starter skill point")
	assert_true(sm.equip_active_skill("Q", "def_act_bark"), "equip def_act_bark into Q slot")
	assert_eq(str(sm.equipped_slots["Q"]), "def_act_bark", "Q slot holds newly equipped skill")
	p.perform_slot("Q")
	assert_true(float(p.cooldowns.get("def_act_bark", 0.0)) > 0.0, "perform_slot(Q) casts the EQUIPPED skill, not a hardcoded one")
	assert_true(float(p.energy) < float(p.stats["max_energy"]), "equipped skill drained spiritual energy")
	p.perform_slot("E")
	assert_true(float(p.cooldowns.get("swordWave", 0.0)) > 0.0, "E slot defaults to canonical swordWave")
	assert_eq(str(sm.get_equipped_skill_for_slot("SHIFT")), "dash", "SHIFT slot keeps dash by default")

	# HUD slot binding & label reflection
	var hud = load("res://scripts/HUD.gd").new()
	root.add_child(hud)
	hud.connect_player(p)
	assert_eq(str(hud.cd_nodes["Q"]["skill"]), "def_act_bark", "HUD Q cooldown curtain bound to equipped skill")
	assert_eq(str(hud.slot_skill_ids["Q"]), "def_act_bark", "slot_skill_ids reflects loadout")
	var name_lbl: Label = hud.slot_nodes["Q"]["name"]
	assert_true(name_lbl.text.find("Corteza") != -1, "HUD slot label shows equipped skill name (got '%s')" % name_lbl.text)

	# Live world events feed permanent evolution conditions
	for i in range(24):
		p.add_kill()
	assert_true(p.wave >= 3, "waves advanced via kills")
	assert_true(p.evolution_manager.has_world_event("wave_3_cleared"), "wave_3_cleared world event recorded live")
	assert_true(int(p.evolution_manager.evolution_xp) > 0, "kills grant evolution essence")
	p.notify_boss_defeated()
	assert_true(p.evolution_manager.has_world_event("defeated_malakor"), "notify_boss_defeated records world event")

	# Spiritual energy HUD & nav pills
	assert_true(hud.energy_bar != null and hud.energy_text != null, "energy bar & text built in bottom skills panel")
	hud._process(0.016)
	assert_true(absf(float(hud.energy_bar.value) - float(p.energy)) < 0.5, "energy bar mirrors live player energy")
	assert_true(str(hud.energy_text.text).find("⚡") != -1, "energy text shows bolt glyph")
	assert_true(str(hud.evo_pill_btn.text).find("Etapa") != -1, "evo pill shows live stage")
	assert_true(str(hud.skills_pill_btn.text).find("Pts:") != -1, "skills pill shows live skill points")
	hud.free()
	world.free()


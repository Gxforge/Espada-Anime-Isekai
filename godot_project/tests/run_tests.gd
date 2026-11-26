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

	# Level progression & evolution signal
	var evo_state := {"count": 0, "last_id": ""}
	p.evolution_changed.connect(func(t):
		evo_state["count"] += 1
		evo_state["last_id"] = str(t["id"])
	)
	p.add_xp(500) # Enough to cross Nv.5 Copper evolution
	assert_true(p.sword_level >= 5, "add_xp advances sword_level >= 5")
	assert_true(int(evo_state["count"]) >= 1, "evolution_changed signal emitted on tier up")
	assert_eq(str(p.current_tier["id"]), str(gd.get_sword_for_level(p.sword_level)["id"]), "active sword tier matches level")

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

	world.free()
	gd.free()

func test_save_roundtrip_and_v1_migration() -> void:
	var ss = load("res://scripts/SaveSystem.gd").new()
	assert_eq(ss.SAVE_VERSION, 2, "SaveSystem SAVE_VERSION is 2")

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

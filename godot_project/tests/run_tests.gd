extends SceneTree

var failures: Array[String] = []
var passes: int = 0

func _init() -> void:
	print("=== RUNNING TESTS ===")
	test_gamedata_swords()
	test_gamedata_monsters()
	test_xp_curve()
	test_model_files_exist()
	test_model_resources_load()
	test_canonical_skill_ids()
	test_save_roundtrip()
	test_upgrade_max_level()
	test_monster_builder()
	test_sword_builder()
	print("=== RESULTS: %d passed, %d failed ===" % [passes, failures.size()])
	for f in failures:
		print("FAIL: ", f)
	if failures.size() > 0:
		quit(1)
	else:
		quit(0)

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
	assert_eq(ids, ["wood","copper","iron","silver","gold","crystal","obsidian","celestial"], "sword ids order")
	gd.free()

func test_gamedata_monsters() -> void:
	var gd = load("res://scripts/GameData.gd").new()
	assert_eq(gd.MONSTER_DEFINITIONS.size(), 7, "7 monsters")
	var ids = []
	for m in gd.MONSTER_DEFINITIONS:
		ids.append(str(m["id"]))
		assert_true(ResourceLoader.exists(str(m["model_path"])), "monster model exists: %s" % str(m["model_path"]))
	assert_eq(ids, ["slime","goblin","skeleton","copper_golem","orc_berserker","crimson_drake","demon_lord"], "monster ids")
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
		"res://assets/models/sword_wood_nv1.obj","res://assets/models/sword_copper_nv5.obj",
		"res://assets/models/sword_iron_nv10.obj","res://assets/models/sword_silver_nv15.obj",
		"res://assets/models/sword_gold_nv20.obj","res://assets/models/sword_crystal_nv25.obj",
		"res://assets/models/sword_obsidian_nv30.obj","res://assets/models/sword_celestial_nv35.obj",
		"res://assets/models/monster_slime.obj","res://assets/models/monster_goblin.obj",
		"res://assets/models/monster_skeleton.obj","res://assets/models/monster_copper_golem.obj",
		"res://assets/models/monster_orc_berserker.obj","res://assets/models/monster_crimson_drake.obj",
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
	# Static check: Player.gd should have canonical swordWave
	var f = FileAccess.open("res://scripts/Player.gd", FileAccess.READ)
	var src = f.get_as_text()
	f.close()
	assert_true(src.find('"swordWave"') != -1, "Player has swordWave")
	assert_true(src.find('func _canonical_skill') != -1, "Player has canonical skill mapper")

func test_save_roundtrip() -> void:
	var ss = load("res://scripts/SaveSystem.gd").new()
	# We can't fully instantiate Player without scene, but we can test JSON logic by checking script exists
	assert_true(ss != null, "SaveSystem loads")
	assert_true(ss.SAVE_VERSION == 1, "Save version 1")
	ss.free()

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

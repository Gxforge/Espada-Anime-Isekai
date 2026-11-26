extends Node

const SAVE_PATH := "user://savegame.json"
const SAVE_VERSION := 3

var settings := {
	"quality": "medium",
	"audio_muted": false,
	"master_volume": 0.85,
	"music_volume": 0.70,
	"sfx_volume": 0.85,
}

func save_game(player: Node, custom_path: String = SAVE_PATH) -> bool:
	if player == null:
		return false
	var data := serialize_player(player)
	return _write_json_atomic(custom_path, data)

func serialize_player(player: Node) -> Dictionary:
	var mats := {}
	if player.get("materials") != null:
		mats = player.materials.duplicate(true)
	var items: Array = []
	if player.get("inventory_items") != null:
		items = player.inventory_items.duplicate(true)
	var eq := {"grip": "", "rune": "", "relic": ""}
	if player.get("equipped") != null:
		for k in eq.keys():
			eq[k] = str(player.equipped.get(k, ""))
	var cons := {"potion_hp": 2, "elixir_xp": 0}
	if player.get("consumables") != null:
		cons = player.consumables.duplicate(true)

	# v3: permanent evolution & skill progression are stored verbatim and NEVER
	# reconstructed from player level alone.
	var evo_state := {}
	if player.get("evolution_manager") != null and player.evolution_manager != null:
		evo_state = player.evolution_manager.to_dict()
	var skill_state := {}
	if player.get("skill_manager") != null and player.skill_manager != null:
		skill_state = player.skill_manager.to_dict()

	return {
		"version": SAVE_VERSION,
		"sword_level": int(player.sword_level),
		"current_xp": int(player.current_xp),
		"gold": int(player.gold),
		"kills": int(player.kills),
		"wave": int(player.wave),
		"wave_kills": int(player.wave_kills),
		"player_hp": int(player.player_hp),
		"player_max_hp": int(player.player_max_hp),
		"wielder_mode": str(player.wielder_mode),
		"auto_hunt": bool(player.get("auto_hunt") if player.get("auto_hunt") != null else false),
		"upgrades": player.upgrades.duplicate(true),
		"materials": mats,
		"inventory_items": items,
		"equipped": eq,
		"consumables": cons,
		"bosses_defeated": int(player.get("bosses_defeated") if player.get("bosses_defeated") != null else 0),
		"evolution_state": evo_state,
		"skill_state": skill_state,
		"settings": settings.duplicate(true),
	}

func _write_json_atomic(target_path: String, data: Dictionary) -> bool:
	var json := JSON.stringify(data)
	var tmp_path := target_path + ".tmp"
	var f := FileAccess.open(tmp_path, FileAccess.WRITE)
	if f == null:
		push_warning("SaveSystem: cannot open temp save file")
		return false
	f.store_string(json)
	f.close()
	var err := DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp_path), ProjectSettings.globalize_path(target_path))
	if err != OK:
		var f2 := FileAccess.open(target_path, FileAccess.WRITE)
		if f2 == null:
			return false
		f2.store_string(json)
		f2.close()
		if FileAccess.file_exists(tmp_path):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(tmp_path))
	return true

func load_game(player: Node, custom_path: String = SAVE_PATH) -> bool:
	if player == null or not FileAccess.file_exists(custom_path):
		return false
	var f := FileAccess.open(custom_path, FileAccess.READ)
	if f == null:
		return false
	var text := f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("SaveSystem: invalid save file")
		return false
	# Migrate v1/v2 payloads up to the current v3 schema before applying
	var d: Dictionary = SaveMigration.migrate_save_dict(parsed)
	if d.has("settings"):
		_apply_settings(d.get("settings", {}))
	# Only apply player progression if save actually contains player data (not a settings-only file)
	if d.has("sword_level"):
		_apply_to_player(player, d)
	return true

func _apply_to_player(player: Node, d: Dictionary) -> void:
	player.sword_level = maxi(1, int(d.get("sword_level", 1)))
	player.current_xp = maxi(0, int(d.get("current_xp", 0)))
	player.gold = maxi(0, int(d.get("gold", 60)))
	player.kills = maxi(0, int(d.get("kills", 0)))
	player.wave = maxi(1, int(d.get("wave", 1)))
	player.wave_kills = clampi(int(d.get("wave_kills", 0)), 0, 7)
	var wm := str(d.get("wielder_mode", "living_sword"))
	player.wielder_mode = wm if wm in ["living_sword", "knight_wielder"] else "living_sword"
	if "auto_hunt" in player:
		player.auto_hunt = bool(d.get("auto_hunt", false))

	var upg = d.get("upgrades", {})
	if typeof(upg) == TYPE_DICTIONARY:
		for k in player.upgrades.keys():
			if upg.has(k):
				player.upgrades[k] = clampi(int(upg[k]), 0, 10)

	# RPG inventory migration-safe load (v1, v2 & v3)
	if player.get("materials") != null:
		player.materials.clear()
		var mats = d.get("materials", {})
		if typeof(mats) == TYPE_DICTIONARY:
			for mk in mats.keys():
				var cnt := maxi(0, int(mats[mk]))
				if cnt > 0:
					player.materials[str(mk)] = cnt

	if player.get("inventory_items") != null:
		player.inventory_items.clear()
		var inv = d.get("inventory_items", [])
		if typeof(inv) == TYPE_ARRAY:
			for it in inv:
				var sid := str(it)
				if sid != "" and not player.inventory_items.has(sid):
					player.inventory_items.append(sid)

	if player.get("equipped") != null:
		for slot in ["grip", "rune", "relic"]:
			player.equipped[slot] = ""
		var eq = d.get("equipped", {})
		if typeof(eq) == TYPE_DICTIONARY:
			for slot in ["grip", "rune", "relic"]:
				var rid := str(eq.get(slot, ""))
				if rid != "" and player.inventory_items.has(rid):
					player.equipped[slot] = rid

	if player.get("consumables") != null:
		var cons = d.get("consumables", {"potion_hp": 2, "elixir_xp": 0})
		if typeof(cons) == TYPE_DICTIONARY:
			for ck in ["potion_hp", "elixir_xp"]:
				if cons.has(ck):
					player.consumables[ck] = maxi(0, int(cons[ck]))

	if "bosses_defeated" in player:
		player.bosses_defeated = maxi(0, int(d.get("bosses_defeated", 0)))

	# v3: restore permanent evolution state & skill progression.
	# If a v3 evolution_state exists it is applied VERBATIM: permanent branch choices,
	# evolution history and discarded sibling forms are never re-derived from level.
	if player.get("evolution_manager") != null and player.evolution_manager != null:
		player.evolution_manager.from_dict(d.get("evolution_state", {}))
		if int(player.get("bosses_defeated")) > 0:
			player.evolution_manager.record_world_event("defeated_malakor")
	if player.get("skill_manager") != null and player.skill_manager != null:
		player.skill_manager.from_dict(d.get("skill_state", {}))

	var gd = get_node_or_null("/root/GameData") if is_inside_tree() else null
	if gd == null and player.has_method("_get_gamedata"):
		gd = player._get_gamedata()
	# Authoritative form comes from the persisted evolution state (not from level)
	if player.get("evolution_manager") != null and player.evolution_manager != null:
		player.current_tier = player.evolution_manager.get_legacy_tier_view()
	elif gd:
		player.current_tier = gd.get_sword_for_level(player.sword_level)
	player._recalc_stats()
	var saved_hp := int(d.get("player_hp", player.player_max_hp))
	player.player_hp = clampi(saved_hp, 1, player.player_max_hp)
	if player.is_inside_tree():
		player._refresh_sword_visual()
	player.hp_changed.emit(player.player_hp, player.player_max_hp)
	var req: int = int(gd.get_xp_required(player.sword_level)) if gd else 100
	player.xp_changed.emit(player.current_xp, req, player.sword_level)
	player.gold_changed.emit(player.gold)
	player.kills_changed.emit(player.kills)
	player.wave_changed.emit(player.wave, player.wave_kills)
	if player.has_signal("inventory_changed"):
		player.inventory_changed.emit()

func _apply_settings(s) -> void:
	if typeof(s) != TYPE_DICTIONARY:
		return
	if s.has("quality"):
		var q := str(s["quality"])
		if q in ["low", "medium", "high"]:
			settings["quality"] = q
	if s.has("audio_muted"):
		settings["audio_muted"] = bool(s["audio_muted"])
	if s.has("master_volume"):
		settings["master_volume"] = clampf(float(s["master_volume"]), 0.0, 1.0)
	elif s.has("volume"):
		settings["master_volume"] = clampf(float(s["volume"]), 0.0, 1.0)
	if s.has("music_volume"):
		settings["music_volume"] = clampf(float(s["music_volume"]), 0.0, 1.0)
	if s.has("sfx_volume"):
		settings["sfx_volume"] = clampf(float(s["sfx_volume"]), 0.0, 1.0)

	var am = get_node_or_null("/root/AudioManager") if is_inside_tree() else null
	if am and am.has_method("apply_settings_dict"):
		am.apply_settings_dict(settings)
	else:
		var m_idx := AudioServer.get_bus_index("Master")
		if m_idx != -1:
			var muted := bool(settings.get("audio_muted", false)) or float(settings.get("master_volume", 0.85)) <= 0.001
			AudioServer.set_bus_mute(m_idx, muted)
			AudioServer.set_bus_volume_db(m_idx, linear_to_db(maxf(0.0001, float(settings.get("master_volume", 0.85)))))

func save_settings(custom_path: String = SAVE_PATH) -> bool:
	var data := {}
	if FileAccess.file_exists(custom_path):
		var f := FileAccess.open(custom_path, FileAccess.READ)
		if f:
			var parsed = JSON.parse_string(f.get_as_text())
			f.close()
			if typeof(parsed) == TYPE_DICTIONARY:
				data = parsed
	data["version"] = SAVE_VERSION
	data["settings"] = settings.duplicate(true)
	return _write_json_atomic(custom_path, data)

func load_settings_only(custom_path: String = SAVE_PATH) -> void:
	if not FileAccess.file_exists(custom_path):
		return
	var f := FileAccess.open(custom_path, FileAccess.READ)
	if f == null:
		return
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) == TYPE_DICTIONARY:
		_apply_settings(parsed.get("settings", {}))

func delete_save(custom_path: String = SAVE_PATH) -> void:
	if FileAccess.file_exists(custom_path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(custom_path))

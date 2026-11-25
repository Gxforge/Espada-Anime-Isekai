extends Node

const SAVE_PATH := "user://savegame.json"
const SAVE_VERSION := 1

var settings := {"quality": "medium", "audio_muted": false}

func save_game(player: Node) -> bool:
	if player == null:
		return false
	var data := {
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
		"upgrades": player.upgrades.duplicate(true),
		"settings": settings.duplicate(true),
	}
	var json := JSON.stringify(data)
	var tmp_path := SAVE_PATH + ".tmp"
	var f := FileAccess.open(tmp_path, FileAccess.WRITE)
	if f == null:
		push_warning("SaveSystem: cannot open temp save file")
		return false
	f.store_string(json)
	f.close()
	# atomic-ish replace
	var err := DirAccess.rename_absolute(tmp_path, SAVE_PATH)
	if err != OK:
		# fallback: direct write
		var f2 := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
		if f2 == null:
			return false
		f2.store_string(json)
		f2.close()
	return true

func load_game(player: Node) -> bool:
	if player == null or not FileAccess.file_exists(SAVE_PATH):
		return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		return false
	var text := f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("SaveSystem: invalid save file")
		return false
	var d: Dictionary = parsed
	_apply_to_player(player, d)
	_apply_settings(d.get("settings", {}))
	return true

func _apply_to_player(player: Node, d: Dictionary) -> void:
	player.sword_level = maxi(1, int(d.get("sword_level", 1)))
	player.current_xp = maxi(0, int(d.get("current_xp", 0)))
	player.gold = maxi(0, int(d.get("gold", 60)))
	player.kills = maxi(0, int(d.get("kills", 0)))
	player.wave = maxi(1, int(d.get("wave", 1)))
	player.wave_kills = clampi(int(d.get("wave_kills", 0)), 0, 7)
	player.player_max_hp = maxi(1, int(d.get("player_max_hp", 220)))
	player.player_hp = clampi(int(d.get("player_hp", player.player_max_hp)), 1, player.player_max_hp)
	var wm := str(d.get("wielder_mode", "living_sword"))
	player.wielder_mode = wm if wm in ["living_sword", "knight_wielder"] else "living_sword"
	var upg = d.get("upgrades", {})
	if typeof(upg) == TYPE_DICTIONARY:
		for k in player.upgrades.keys():
			if upg.has(k):
				player.upgrades[k] = clampi(int(upg[k]), 0, 99)
	var gd = get_node_or_null("/root/GameData")
	if gd:
		player.current_tier = gd.get_sword_for_level(player.sword_level)
	else:
		player.current_tier = player.current_tier
	player._recalc_stats()
	player._refresh_sword_visual()
	player.hp_changed.emit(player.player_hp, player.player_max_hp)
	var req = gd.get_xp_required(player.sword_level) if gd else 100
	player.xp_changed.emit(player.current_xp, req, player.sword_level)
	player.gold_changed.emit(player.gold)
	player.kills_changed.emit(player.kills)
	player.wave_changed.emit(player.wave, player.wave_kills)

func _apply_settings(s) -> void:
	if typeof(s) != TYPE_DICTIONARY:
		return
	if s.has("quality"): settings["quality"] = str(s["quality"])
	if s.has("audio_muted"): settings["audio_muted"] = bool(s["audio_muted"])
	AudioServer.set_bus_mute(0, bool(settings.get("audio_muted", false)))

func save_settings() -> bool:
	# save settings into existing save if any; else write settings-only file
	var data := {}
	if FileAccess.file_exists(SAVE_PATH):
		var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
		if f:
			var parsed = JSON.parse_string(f.get_as_text())
			f.close()
			if typeof(parsed) == TYPE_DICTIONARY:
				data = parsed
	data["version"] = SAVE_VERSION
	data["settings"] = settings.duplicate(true)
	var f2 := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f2 == null: return false
	f2.store_string(JSON.stringify(data))
	f2.close()
	return true

func load_settings_only() -> void:
	if not FileAccess.file_exists(SAVE_PATH): return
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null: return
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) == TYPE_DICTIONARY:
		_apply_settings(parsed.get("settings", {}))

func delete_save() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(SAVE_PATH)

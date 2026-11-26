extends RefCounted
class_name SaveMigration

## Migrates legacy v1 and v2 save payloads cleanly to Save Schema v3 while strictly
## preserving permanent evolution decisions in v3+ saves without ever reconstructing
## the sword solely from player level.

const CURRENT_SAVE_VERSION := 3

static func migrate_save_dict(raw: Dictionary) -> Dictionary:
	if raw.is_empty():
		return {}
	var d: Dictionary = raw.duplicate(true)
	var ver: int = int(d.get("version", 1))

	# Settings-only save payload (no player run data)
	if not d.has("sword_level") and not d.has("evolution_state"):
		d["version"] = CURRENT_SAVE_VERSION
		return d

	# v1 -> v2 defaults
	if ver < 2:
		if not d.has("materials"):
			d["materials"] = {}
		if not d.has("inventory_items"):
			d["inventory_items"] = []
		if not d.has("equipped"):
			d["equipped"] = {"grip": "", "rune": "", "relic": ""}
		if not d.has("consumables"):
			d["consumables"] = {"potion_hp": 2, "elixir_xp": 0}
		if not d.has("bosses_defeated"):
			d["bosses_defeated"] = 0
		ver = 2

	# v2 -> v3 migration: ONLY synthesize initial evolution_state if missing (legacy save)!
	# If evolution_state already exists, preserve permanent choices verbatim!
	if not d.has("evolution_state") or typeof(d["evolution_state"]) != TYPE_DICTIONARY:
		var lvl: int = maxi(1, int(d.get("sword_level", 1)))
		var mapped_form: String = _map_legacy_level_once(lvl)
		var mapped_stage: int = _legacy_stage_for_form(mapped_form)
		var evs: Dictionary = {}
		if int(d.get("wave", 1)) >= 3:
			evs["wave_3_cleared"] = true
		if int(d.get("bosses_defeated", 0)) > 0:
			evs["defeated_malakor"] = true
		d["evolution_state"] = {
			"current_form_id": mapped_form,
			"evolution_xp": maxi(0, (lvl - 1) * 25),
			"evolution_history": [{
				"stage": mapped_stage,
				"era": int((mapped_stage - 1) / 4) + 1,
				"form_id": mapped_form,
				"level_at_choice": lvl,
				"migrated_from_v2": true,
			}],
			"discarded_form_ids": [],
			"world_events": evs,
		}

	if not d.has("skill_state") or typeof(d["skill_state"]) != TYPE_DICTIONARY:
		var lvl_pts: int = maxi(1, int(d.get("sword_level", 1)))
		d["skill_state"] = {
			"skill_points": lvl_pts,
			"unlocked_skills": {
				"whirlwind": 1,
				"swordWave": 1,
				"ultimate": 1,
				"dash": 1,
			},
			"equipped_slots": {
				"Q": "whirlwind",
				"E": "swordWave",
				"R": "ultimate",
				"SHIFT": "dash",
			},
		}

	d["version"] = CURRENT_SAVE_VERSION
	return d

static func _map_legacy_level_once(lvl: int) -> String:
	if lvl >= 35:
		return "hybrid_celestial_abyss_eclipse"
	elif lvl >= 30:
		return "cursed_abyssal_guillotine_edge"
	elif lvl >= 25:
		return "arcane_crystal_cipher_sword"
	elif lvl >= 20:
		return "blessed_auric_bastion_claymore"
	elif lvl >= 15:
		return "spiritual_silver_anima_saber"
	elif lvl >= 10:
		return "awakening_ironwood_storm_edge"
	elif lvl >= 5:
		return "wood_mineral_copper_root"
	return "wood_origin_ancestral_blade"

static func _legacy_stage_for_form(fid: String) -> int:
	match fid:
		"wood_mineral_copper_root": return 2
		"awakening_ironwood_storm_edge": return 3
		"spiritual_silver_anima_saber": return 5
		"arcane_crystal_cipher_sword": return 5
		"blessed_auric_bastion_claymore": return 6
		"cursed_abyssal_guillotine_edge": return 9
		"hybrid_celestial_abyss_eclipse": return 16
		_: return 1

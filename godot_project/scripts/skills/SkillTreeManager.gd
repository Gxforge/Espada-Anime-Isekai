extends RefCounted
class_name SkillTreeManager

## Runtime skill progression, prerequisites, branch-exclusive locks, active slot assignment,
## and passive modifier aggregation for the 72-Skill / 6-Tree System.

signal skill_unlocked(skill_id: String, skill_def: Dictionary)
signal skill_points_changed(points: int)
signal active_loadout_changed(loadout: Dictionary)

const STARTER_ACTIVE_SKILLS := ["whirlwind", "swordWave", "ultimate", "dash"]

var catalog: SkillCatalog
var skill_points: int = 1
var unlocked_skills: Dictionary = {}  # skill_id -> rank (1)
var equipped_slots: Dictionary = {
	"Q": "whirlwind",
	"E": "swordWave",
	"R": "ultimate",
	"SHIFT": "dash",
}

func _init(p_catalog: SkillCatalog = null) -> void:
	catalog = p_catalog if p_catalog != null else SkillCatalog.new(true)
	reset_to_defaults()

func reset_to_defaults() -> void:
	skill_points = 1
	unlocked_skills.clear()
	for sid in STARTER_ACTIVE_SKILLS:
		unlocked_skills[sid] = 1
	equipped_slots = {
		"Q": "whirlwind",
		"E": "swordWave",
		"R": "ultimate",
		"SHIFT": "dash",
	}

func add_skill_points(amount: int) -> void:
	if amount <= 0:
		return
	skill_points += amount
	skill_points_changed.emit(skill_points)

func is_unlocked(skill_id: String) -> bool:
	var cid: String = catalog.canonical_id(skill_id)
	return int(unlocked_skills.get(cid, 0)) > 0

func can_unlock_skill(skill_id: String, current_stage: int, current_lineage: String) -> Dictionary:
	var cid: String = catalog.canonical_id(skill_id)
	if not catalog.has_skill(cid):
		return {"ok": false, "reasons": ["Habilidad inexistente."]}
	if is_unlocked(cid):
		return {"ok": false, "reasons": ["Ya aprendida."]}

	var sdef: Dictionary = catalog.get_skill(cid)
	var reasons: Array[String] = []

	var cost: int = int(sdef.get("cost_points", 1))
	if skill_points < cost:
		reasons.append("Requiere %d Pts de Habilidad (tienes %d)" % [cost, skill_points])

	var min_st: int = int(sdef.get("min_stage", 1))
	if current_stage < min_st:
		reasons.append("Requiere Etapa Evolutiva %02d (actual: %02d)" % [min_st, current_stage])

	for pre_v in sdef.get("prereq_skills", []):
		var pre_id: String = str(pre_v)
		if not is_unlocked(pre_id):
			var pre_def: Dictionary = catalog.get_skill(pre_id)
			reasons.append("Requiere '%s'" % str(pre_def.get("name", pre_id)))

	var allowed: Array = sdef.get("allowed_lineages", [])
	if not allowed.is_empty() and not allowed.has(current_lineage):
		reasons.append("Exclusiva de linaje: %s" % ", ".join(PackedStringArray(allowed)))

	return {"ok": reasons.is_empty(), "reasons": reasons}

func unlock_skill(skill_id: String, current_stage: int, current_lineage: String) -> Dictionary:
	var cid: String = catalog.canonical_id(skill_id)
	var check: Dictionary = can_unlock_skill(cid, current_stage, current_lineage)
	if not bool(check.get("ok", false)):
		return check
	var sdef: Dictionary = catalog.get_skill(cid)
	var cost: int = int(sdef.get("cost_points", 1))
	skill_points -= cost
	unlocked_skills[cid] = 1
	skill_points_changed.emit(skill_points)
	skill_unlocked.emit(cid, sdef)
	return {"ok": true, "skill": sdef}

func equip_active_skill(slot_key: String, skill_id: String) -> bool:
	if not slot_key in ["Q", "E", "R", "SHIFT"]:
		return false
	var cid: String = catalog.canonical_id(skill_id)
	if not is_unlocked(cid):
		return false
	var sdef: Dictionary = catalog.get_skill(cid)
	if str(sdef.get("type", "")) != "active":
		return false
	equipped_slots[slot_key] = cid
	active_loadout_changed.emit(equipped_slots.duplicate(true))
	return true

func get_equipped_skill_for_slot(slot_key: String) -> String:
	return str(equipped_slots.get(slot_key, ""))

func get_aggregated_passive_modifiers(current_lineage: String = "") -> Dictionary:
	var mods := {
		"physical_damage_pct": 0.0,
		"elemental_damage_pct": 0.0,
		"attack_speed_pct": 0.0,
		"attack_range_add": 0.0,
		"crit_chance_add": 0.0,
		"crit_damage_add": 0.0,
		"armor_penetration_add": 0.0,
		"life_steal_add": 0.0,
		"max_hp_pct": 0.0,
		"defense_add": 0.0,
		"elemental_resistance_add": 0.0,
		"energy_regen_pct": 0.0,
		"max_energy_add": 0,
		"move_speed_pct": 0.0,
		"cdr_add": 0.0,
		"status_chance_add": 0.0,
		"soul_absorption_add": 0.0,
	}
	for sid_v in unlocked_skills.keys():
		var sid: String = str(sid_v)
		if int(unlocked_skills[sid]) <= 0:
			continue
		var sdef: Dictionary = catalog.get_skill(sid)
		if str(sdef.get("type", "")) != "passive":
			continue
		var allowed: Array = sdef.get("allowed_lineages", [])
		if current_lineage != "" and not allowed.is_empty() and not allowed.has(current_lineage):
			continue
		var eff: Dictionary = sdef.get("effect_data", {})
		for ek in eff.keys():
			if mods.has(ek):
				mods[ek] = float(mods[ek]) + float(eff[ek])
	return mods

func to_dict() -> Dictionary:
	return {
		"skill_points": skill_points,
		"unlocked_skills": unlocked_skills.duplicate(true),
		"equipped_slots": equipped_slots.duplicate(true),
	}

func from_dict(d: Dictionary) -> void:
	if d.is_empty():
		return
	skill_points = maxi(0, int(d.get("skill_points", 1)))
	unlocked_skills.clear()
	for sid in STARTER_ACTIVE_SKILLS:
		unlocked_skills[sid] = 1
	var unl = d.get("unlocked_skills", {})
	if typeof(unl) == TYPE_DICTIONARY:
		for k in unl.keys():
			var cid: String = catalog.canonical_id(str(k))
			if int(unl[k]) > 0 and catalog.has_skill(cid):
				unlocked_skills[cid] = int(unl[k])
	var eq = d.get("equipped_slots", {})
	if typeof(eq) == TYPE_DICTIONARY:
		for sk in ["Q", "E", "R", "SHIFT"]:
			if eq.has(sk):
				var cid: String = catalog.canonical_id(str(eq[sk]))
				if is_unlocked(cid):
					equipped_slots[sk] = cid

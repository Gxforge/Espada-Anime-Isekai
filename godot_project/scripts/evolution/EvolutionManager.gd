extends RefCounted
class_name EvolutionManager

## Runtime state & permanent decision engine for the 24-Stage Evolution System.
## Decisions are strictly permanent and irreversible: choosing one branch records
## the chosen form in `evolution_history` and locks out unchosen sibling forms in
## `discarded_form_ids`. State is persisted directly in Save v3 and NEVER reconstructed
## solely from player level.

signal form_evolved(old_form_id: String, new_form: Dictionary, stage: int)
signal evolution_xp_changed(current_evo_xp: int)
signal world_event_recorded(event_id: String)

var catalog: EvolutionCatalog
var current_form_id: String = "wood_origin_ancestral_blade"
var evolution_xp: int = 0
var evolution_history: Array = []
var discarded_form_ids: Array = []
var world_events: Dictionary = {}

func _init(p_catalog: EvolutionCatalog = null) -> void:
	catalog = p_catalog if p_catalog != null else EvolutionCatalog.new(true)
	reset_to_origin()

func reset_to_origin() -> void:
	current_form_id = catalog.root_form_id
	evolution_xp = 0
	discarded_form_ids = []
	world_events = {}
	evolution_history = [{
		"stage": 1,
		"era": 1,
		"form_id": current_form_id,
		"level_at_choice": 1,
	}]

func get_current_form() -> Dictionary:
	return catalog.get_form(current_form_id)

func get_current_stage() -> int:
	var f: Dictionary = get_current_form()
	return int(f.get("stage", 1))

func get_current_era() -> int:
	var f: Dictionary = get_current_form()
	return int(f.get("era", 1))

func get_current_lineage() -> String:
	var f: Dictionary = get_current_form()
	return str(f.get("lineage", "origin"))

func add_evolution_xp(amount: int) -> void:
	if amount <= 0:
		return
	evolution_xp += amount
	evolution_xp_changed.emit(evolution_xp)

func record_world_event(event_id: String) -> void:
	if event_id == "":
		return
	if not world_events.has(event_id):
		world_events[event_id] = true
		world_event_recorded.emit(event_id)

func has_world_event(event_id: String) -> bool:
	return bool(world_events.get(event_id, false))

func is_form_in_history(form_id: String) -> bool:
	var cid: String = catalog.resolve_id(form_id)
	for entry in evolution_history:
		if str(entry.get("form_id", "")) == cid:
			return true
	return false

func is_form_discarded(form_id: String) -> bool:
	var cid: String = catalog.resolve_id(form_id)
	return discarded_form_ids.has(cid)

func get_available_branch_options() -> Array:
	return catalog.get_next_forms(current_form_id)

## Evaluates all 5 mandatory unlock condition categories against current player context.
## context keys:
##   "sword_level": int
##   "materials": Dictionary
##   "unlocked_skills": Dictionary / Array
func evaluate_unlock_conditions(target_form_id: String, context: Dictionary) -> Dictionary:
	var cid: String = catalog.resolve_id(target_form_id)
	if cid == "":
		return {"can_evolve": false, "reasons": ["Forma inexistente."], "checks": []}

	# Must be an immediate child of current_form_id (no skipping stages or reversing permanent branches!)
	var cur: Dictionary = get_current_form()
	var next_ids: Array = cur.get("next_forms", [])
	if not next_ids.has(cid):
		return {"can_evolve": false, "reasons": ["No pertenece a las ramas directas de tu forma actual."], "checks": []}
	if is_form_discarded(cid):
		return {"can_evolve": false, "reasons": ["Rama descartada permanentemente en una elección previa."], "checks": []}

	var target: Dictionary = catalog.get_form(cid)
	var ucond: Dictionary = target.get("unlock_conditions", {})
	var reasons: Array[String] = []
	var checks: Array = []

	# 1. Minimum Sword Level
	var req_lvl: int = int(ucond.get("min_level", 1))
	var cur_lvl: int = int(context.get("sword_level", 1))
	var ok_lvl: bool = cur_lvl >= req_lvl
	checks.append({"type": "min_level", "ok": ok_lvl, "label": "Nivel mínimo %d (actual: %d)" % [req_lvl, cur_lvl]})
	if not ok_lvl:
		reasons.append("Requiere Nivel %d" % req_lvl)

	# 2. Evolution Resonance XP
	var req_exp: int = int(ucond.get("min_evolution_xp", 0))
	var ok_exp: bool = evolution_xp >= req_exp
	checks.append({"type": "min_evolution_xp", "ok": ok_exp, "label": "Esencia Evolutiva %d/%d" % [evolution_xp, req_exp]})
	if not ok_exp:
		reasons.append("Falta Esencia Evolutiva (%d/%d)" % [evolution_xp, req_exp])

	# 3. Special Materials
	var req_mats: Dictionary = ucond.get("required_materials", {})
	var player_mats: Dictionary = context.get("materials", {})
	for mk in req_mats.keys():
		var need_cnt: int = int(req_mats[mk])
		var have_cnt: int = int(player_mats.get(mk, 0))
		var ok_m: bool = have_cnt >= need_cnt
		checks.append({"type": "material", "ok": ok_m, "label": "Material %s: %d/%d" % [str(mk), have_cnt, need_cnt]})
		if not ok_m:
			reasons.append("Falta %s (%d/%d)" % [str(mk), have_cnt, need_cnt])

	# 4. Required Mastered Skills
	var req_skills: Array = ucond.get("required_skills", [])
	var unlocked_sk = context.get("unlocked_skills", {})
	for sk_v in req_skills:
		var sk_id: String = str(sk_v)
		var has_sk: bool = false
		if typeof(unlocked_sk) == TYPE_DICTIONARY:
			has_sk = int(unlocked_sk.get(sk_id, 0)) > 0
		elif typeof(unlocked_sk) == TYPE_ARRAY:
			has_sk = (unlocked_sk as Array).has(sk_id)
		checks.append({"type": "skill", "ok": has_sk, "label": "Habilidad requerida: %s" % sk_id})
		if not has_sk:
			reasons.append("Requiere habilidad '%s'" % sk_id)

	# 5. World Events / Boss Milestones
	var req_events: Array = ucond.get("required_events", [])
	for ev_v in req_events:
		var ev_id: String = str(ev_v)
		var ok_ev: bool = has_world_event(ev_id)
		checks.append({"type": "event", "ok": ok_ev, "label": "Hito del mundo: %s" % ev_id})
		if not ok_ev:
			reasons.append("Requiere hito '%s'" % ev_id)

	return {
		"can_evolve": reasons.is_empty(),
		"reasons": reasons,
		"checks": checks,
	}

## Commits a permanent, non-reversible evolution choice, consuming required materials.
func commit_permanent_evolution(target_form_id: String, context: Dictionary, consume_materials_into: Variant = null) -> Dictionary:
	var cid: String = catalog.resolve_id(target_form_id)
	var eval_res: Dictionary = evaluate_unlock_conditions(cid, context)
	if not bool(eval_res.get("can_evolve", false)):
		return {"ok": false, "reasons": eval_res.get("reasons", ["Condiciones incompletas."])}

	var old_id: String = current_form_id
	var old_form: Dictionary = get_current_form()
	var target: Dictionary = catalog.get_form(cid)

	# Deduct required materials if a mutable materials dictionary was supplied
	if typeof(consume_materials_into) == TYPE_DICTIONARY:
		var mats_dict: Dictionary = consume_materials_into
		var req_mats: Dictionary = target.get("unlock_conditions", {}).get("required_materials", {})
		for mk in req_mats.keys():
			var need_cnt: int = int(req_mats[mk])
			mats_dict[mk] = maxi(0, int(mats_dict.get(mk, 0)) - need_cnt)
			if int(mats_dict[mk]) == 0:
				mats_dict.erase(mk)

	# Permanently mark unchosen sibling options at this fork as discarded!
	for sib_v in old_form.get("next_forms", []):
		var sib_id: String = str(sib_v)
		if sib_id != cid and not discarded_form_ids.has(sib_id):
			discarded_form_ids.append(sib_id)

	current_form_id = cid
	var new_stage: int = int(target.get("stage", 1))
	var new_era: int = int(target.get("era", 1))
	evolution_history.append({
		"stage": new_stage,
		"era": new_era,
		"form_id": cid,
		"from_form_id": old_id,
		"level_at_choice": int(context.get("sword_level", 1)),
	})

	form_evolved.emit(old_id, target, new_stage)
	return {"ok": true, "new_form": target, "old_form_id": old_id}

func to_dict() -> Dictionary:
	return {
		"current_form_id": current_form_id,
		"evolution_xp": evolution_xp,
		"evolution_history": evolution_history.duplicate(true),
		"discarded_form_ids": discarded_form_ids.duplicate(true),
		"world_events": world_events.duplicate(true),
	}

## Backward-compatible tier view consumed by combat code, HUD, ModelLoader and legacy tests.
## The authoritative evolution state ALWAYS lives in evolution_state (save v3); this view
## simply mirrors the currently committed permanent form.
func get_legacy_tier_view() -> Dictionary:
	var f: Dictionary = catalog.get_form(current_form_id)
	if f.is_empty():
		return {}
	var bs: Dictionary = f.get("base_stats", {})
	var alias: String = str(f.get("legacy_alias", ""))
	if alias == "":
		# Derive the legacy visual family from the authored model filename so
		# ModelLoader/SwordBuilder fallbacks and VFX hooks keep working for every form.
		var fname := str(f.get("model_path", "")).get_file().get_basename()
		for fam in ["wood", "copper", "iron", "silver", "gold", "crystal", "obsidian", "celestial"]:
			if fname.begins_with("sword_" + fam) or fname.contains(fam):
				alias = fam
				break
	var stg: int = int(f.get("stage", 1))
	# Cosmetic "next evolution level" hint: the minimum level among direct children
	var next_lvl = null
	if stg < 24:
		var best := 999
		for nid_v in f.get("next_forms", []):
			var nf: Dictionary = catalog.get_form(str(nid_v))
			if not nf.is_empty():
				best = mini(best, int(nf.get("unlock_conditions", {}).get("min_level", best)))
		if best < 999:
			next_lvl = best
	return {
		"id": alias if alias != "" else str(f.get("id", "")),
		"form_id": str(f.get("id", "")),
		"tier_index": stg - 1,
		"stage": stg,
		"era": int(f.get("era", 1)),
		"lineage": str(f.get("lineage", "origin")),
		"min_level": int(f.get("unlock_conditions", {}).get("min_level", 1)),
		"next_evolution_level": next_lvl,
		"name": str(f.get("name", "")),
		"subtitle": str(f.get("subtitle", "")),
		"material_name": str(f.get("lineage_name", "")),
		"description": str(f.get("description", "")),
		"passive_name": str(f.get("passive_name", "")),
		"passive_description": str(f.get("passive_description", "")),
		"base_damage": float(bs.get("physical_damage", 18.0)),
		"attack_speed": float(bs.get("attack_speed", 1.15)),
		"range": float(bs.get("attack_range", 3.1)),
		"crit_chance": float(bs.get("crit_chance", 0.10)),
		"blade_color": f.get("blade_color", Color("#9c6635")),
		"edge_color": f.get("edge_color", Color("#c48f5a")),
		"guard_color": f.get("guard_color", Color("#5c3a1e")),
		"aura_color": f.get("aura_color", Color("#86efac")),
		"slash_color": f.get("slash_color", Color("#d4a373")),
		"special_effect": str(f.get("special_effect", "none")),
		"model_path": str(f.get("model_path", "")),
		"legacy_obj_path": str(f.get("model_path", "")),
		"protagonist_identity": str(f.get("protagonist_identity", "sentient_sword")),
	}

func from_dict(d: Dictionary) -> void:
	if d.is_empty():
		return
	var loaded_id: String = catalog.resolve_id(str(d.get("current_form_id", catalog.root_form_id)))
	if loaded_id == "":
		loaded_id = catalog.root_form_id
	current_form_id = loaded_id
	evolution_xp = maxi(0, int(d.get("evolution_xp", 0)))

	evolution_history = []
	var hist = d.get("evolution_history", [])
	if typeof(hist) == TYPE_ARRAY and not (hist as Array).is_empty():
		for item in hist:
			if typeof(item) == TYPE_DICTIONARY:
				evolution_history.append((item as Dictionary).duplicate(true))
	else:
		var cur_f: Dictionary = get_current_form()
		evolution_history.append({
			"stage": int(cur_f.get("stage", 1)),
			"era": int(cur_f.get("era", 1)),
			"form_id": current_form_id,
			"level_at_choice": 1,
		})

	discarded_form_ids = []
	var disc = d.get("discarded_form_ids", [])
	if typeof(disc) == TYPE_ARRAY:
		for did in disc:
			var sdid: String = str(did)
			if sdid != "" and not discarded_form_ids.has(sdid):
				discarded_form_ids.append(sdid)

	world_events = {}
	var evs = d.get("world_events", {})
	if typeof(evs) == TYPE_DICTIONARY:
		for ek in evs.keys():
			if bool(evs[ek]):
				world_events[str(ek)] = true

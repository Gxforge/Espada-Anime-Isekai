extends RefCounted
class_name EvolutionValidator

## Automated integrity validator for the 24-Stage / 6-Era Permanent Evolution Graph.
## Ensures:
##  1. All 6 Eras and all 24 Stages exist and have reachable sword forms.
##  2. Protagonist sentient-sword identity is preserved on every node.
##  3. Zero broken parent_forms / next_forms references.
##  4. Zero cycles (strictly monotonically increasing stage on every edge).
##  5. Zero dead-end branches before Stage 24 (every node at stage < 24 has 2..5 valid next_forms).
##  6. Every node is reachable from root_form_id ("wood_origin_ancestral_blade").
##  7. Every node defines all 17 base attributes and all 5 unlock condition keys.

const REQUIRED_STATS := [
	"physical_damage", "elemental_damage", "attack_speed", "attack_range",
	"crit_chance", "crit_damage", "armor_penetration", "life_steal",
	"max_hp", "defense", "elemental_resistance", "energy_regen",
	"max_energy", "move_speed", "cdr", "status_chance", "soul_absorption",
]

const REQUIRED_CONDITION_KEYS := [
	"min_level", "min_evolution_xp", "required_materials", "required_skills", "required_events",
]

static func validate_graph(catalog: EvolutionCatalog) -> Dictionary:
	var errors: Array[String] = []
	var warnings: Array[String] = []

	if catalog == null:
		return {"valid": false, "errors": ["Catalog is null"], "warnings": [], "stats": {}}

	if catalog.eras.size() != 6:
		errors.append("Expected 6 canonical Eras, found %d" % catalog.eras.size())

	if not catalog.has_form(catalog.root_form_id):
		errors.append("Root form '%s' does not exist in catalog" % catalog.root_form_id)

	# Verify all 24 stages exist
	for st in range(1, 25):
		var stage_forms: Array = catalog.get_forms_for_stage(st)
		if stage_forms.is_empty():
			errors.append("Stage %02d has 0 sword forms" % st)

	# Per-form structural & bidirectional graph validation
	var all_forms: Array = catalog.get_all_forms()
	var hybrid_count: int = 0
	var lineages_seen: Dictionary = {}

	for f in all_forms:
		var fid: String = str(f.get("id", ""))
		var st: int = int(f.get("stage", 0))
		var era_num: int = int(f.get("era", 0))
		var lin: String = str(f.get("lineage", ""))
		lineages_seen[lin] = true
		if bool(f.get("is_hybrid", false)):
			hybrid_count += 1

		if st < 1 or st > 24:
			errors.append("Form '%s' has invalid stage %d" % [fid, st])
		var expected_era: int = int((st - 1) / 4) + 1
		if era_num != expected_era:
			errors.append("Form '%s' stage %d should belong to Era %d, got %d" % [fid, st, expected_era, era_num])

		if str(f.get("protagonist_identity", "")) != "sentient_sword":
			errors.append("Form '%s' violates sentient_sword protagonist rule" % fid)

		var bstats: Dictionary = f.get("base_stats", {})
		for sk in REQUIRED_STATS:
			if not bstats.has(sk):
				errors.append("Form '%s' missing base_stat '%s'" % [fid, sk])

		var ucond: Dictionary = f.get("unlock_conditions", {})
		for ck in REQUIRED_CONDITION_KEYS:
			if not ucond.has(ck):
				errors.append("Form '%s' missing unlock_condition '%s'" % [fid, ck])

		var next_ids: Array = f.get("next_forms", [])
		if st < 24:
			if next_ids.size() < 2 or next_ids.size() > 5:
				errors.append("Form '%s' (Stage %d) must offer 2..5 permanent branch choices, found %d" % [fid, st, next_ids.size()])
		else:
			if next_ids.size() != 0:
				errors.append("Final Stage 24 form '%s' should have 0 next_forms, found %d" % [fid, next_ids.size()])

		for nid_v in next_ids:
			var nid: String = str(nid_v)
			if not catalog.forms_by_id.has(nid):
				errors.append("Form '%s' references missing next_form '%s'" % [fid, nid])
				continue
			var child: Dictionary = catalog.forms_by_id[nid]
			var child_st: int = int(child.get("stage", 0))
			if child_st <= st:
				errors.append("Cycle / non-increasing stage edge '%s' (st %d) -> '%s' (st %d)" % [fid, st, nid, child_st])
			var c_parents: Array = child.get("parent_forms", [])
			if not c_parents.has(fid):
				errors.append("Missing reverse parent_forms link on '%s' from '%s'" % [nid, fid])

		var parent_ids: Array = f.get("parent_forms", [])
		if st == 1 and not parent_ids.is_empty():
			errors.append("Root form '%s' should have no parent_forms" % fid)
		elif st > 1 and parent_ids.is_empty():
			errors.append("Form '%s' (Stage %d) has no parent_forms (orphan)" % [fid, st])
		for pid_v in parent_ids:
			var pid: String = str(pid_v)
			if not catalog.forms_by_id.has(pid):
				errors.append("Form '%s' references missing parent_form '%s'" % [fid, pid])

	# BFS reachability from root_form_id
	var visited: Dictionary = {}
	var queue: Array[String] = []
	if catalog.has_form(catalog.root_form_id):
		var rid: String = catalog.resolve_id(catalog.root_form_id)
		visited[rid] = true
		queue.append(rid)
	var head: int = 0
	while head < queue.size():
		var cid: String = queue[head]
		head += 1
		var cnode: Dictionary = catalog.forms_by_id.get(cid, {})
		for nid_v in cnode.get("next_forms", []):
			var sn: String = str(nid_v)
			if catalog.forms_by_id.has(sn) and not visited.has(sn):
				visited[sn] = true
				queue.append(sn)

	for f in all_forms:
		var fid: String = str(f.get("id", ""))
		if not visited.has(fid):
			errors.append("Form '%s' (Stage %d) is unreachable from root '%s'" % [fid, int(f.get("stage", 0)), catalog.root_form_id])

	# Reverse reachability: ensure every node can reach Stage 24 (zero dead branches!)
	var can_reach_end: Dictionary = {}
	for f24 in catalog.get_forms_for_stage(24):
		can_reach_end[str(f24.get("id", ""))] = true
	for st in range(23, 0, -1):
		for f in catalog.get_forms_for_stage(st):
			var fid: String = str(f.get("id", ""))
			for nid_v in f.get("next_forms", []):
				if can_reach_end.has(str(nid_v)):
					can_reach_end[fid] = true
					break
			if not can_reach_end.has(fid):
				errors.append("Dead-end branch detected: '%s' (Stage %d) cannot reach Stage 24" % [fid, st])

	return {
		"valid": errors.is_empty(),
		"errors": errors,
		"warnings": warnings,
		"stats": {
			"total_forms": all_forms.size(),
			"reachable_forms": visited.size(),
			"hybrid_forms": hybrid_count,
			"lineages_count": lineages_seen.size(),
			"stages_covered": 24,
			"eras_covered": catalog.eras.size(),
		}
	}

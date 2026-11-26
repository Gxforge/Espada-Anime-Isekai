extends RefCounted
class_name SkillCatalog

## Data-driven registry of the 72 Sword Skills across 6 Trees (12 per tree: 36 Active + 36 Passive).

const DEFAULT_SKILLS_PATH := "res://data/skills/skills_catalog.json"

var trees: Array = []
var skills_by_id: Dictionary = {}
var skills_by_tree: Dictionary = {}

func _init(load_default: bool = true) -> void:
	if load_default:
		load_catalog(DEFAULT_SKILLS_PATH)

func load_catalog(res_path: String) -> bool:
	var raw_data: Dictionary = EvolutionCatalog._read_json_dict(res_path)
	if raw_data.is_empty():
		push_warning("SkillCatalog: failed to read %s" % res_path)
		return false
	trees = raw_data.get("trees", []).duplicate(true)
	skills_by_id.clear()
	skills_by_tree.clear()
	for t in trees:
		var tid: String = str(t.get("id", ""))
		skills_by_tree[tid] = []
	for s in raw_data.get("skills", []):
		if typeof(s) == TYPE_DICTIONARY:
			register_skill(s)
	return skills_by_id.size() > 0

func register_skill(raw_skill: Dictionary) -> bool:
	var sid: String = str(raw_skill.get("id", "")).strip_edges()
	if sid == "":
		return false
	if sid == "wave":
		sid = "swordWave"
	var d: Dictionary = raw_skill.duplicate(true)
	d["id"] = sid
	skills_by_id[sid] = d
	var tid: String = str(d.get("tree_id", ""))
	if not skills_by_tree.has(tid):
		skills_by_tree[tid] = []
	(skills_by_tree[tid] as Array).append(d)
	return true

func canonical_id(skill_id: String) -> String:
	return "swordWave" if skill_id == "wave" else skill_id

func has_skill(skill_id: String) -> bool:
	return skills_by_id.has(canonical_id(skill_id))

func get_skill(skill_id: String) -> Dictionary:
	var cid: String = canonical_id(skill_id)
	if not skills_by_id.has(cid):
		return {}
	return (skills_by_id[cid] as Dictionary).duplicate(true)

func get_skills_for_tree(tree_id: String) -> Array:
	return (skills_by_tree.get(tree_id, []) as Array).duplicate(true)

func get_all_skills() -> Array:
	var out: Array = []
	for t in trees:
		var tid: String = str(t.get("id", ""))
		for s in skills_by_tree.get(tid, []):
			out.append(s)
	return out

func validate_catalog() -> Dictionary:
	var errors: Array[String] = []
	if trees.size() != 6:
		errors.append("Expected 6 skill trees, found %d" % trees.size())
	var active_cnt: int = 0
	var passive_cnt: int = 0
	for t in trees:
		var tid: String = str(t.get("id", ""))
		var arr: Array = skills_by_tree.get(tid, [])
		if arr.size() < 12:
			errors.append("Tree '%s' must have at least 12 skills, found %d" % [tid, arr.size()])
		for s in arr:
			var sid: String = str(s.get("id", ""))
			var stype: String = str(s.get("type", ""))
			if stype == "active":
				active_cnt += 1
			elif stype == "passive":
				passive_cnt += 1
			else:
				errors.append("Skill '%s' has invalid type '%s'" % [sid, stype])
			for pre_v in s.get("prereq_skills", []):
				var pre: String = str(pre_v)
				if not skills_by_id.has(pre):
					errors.append("Skill '%s' references missing prereq '%s'" % [sid, pre])
	return {
		"valid": errors.is_empty(),
		"errors": errors,
		"total_skills": skills_by_id.size(),
		"active_skills": active_cnt,
		"passive_skills": passive_cnt,
		"tree_count": trees.size(),
	}

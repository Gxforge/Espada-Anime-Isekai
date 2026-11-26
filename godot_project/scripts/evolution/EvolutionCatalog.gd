extends RefCounted
class_name EvolutionCatalog

## Data-driven registry of sentient sword evolution forms across 6 Eras and 24 Stages.
## Supports unlimited total forms and external JSON expansion packs without code edits.

const DEFAULT_CATALOG_PATH := "res://data/forms/evolution_catalog.json"

var eras: Array = []
var lineages: Dictionary = {}
var root_form_id: String = "wood_origin_ancestral_blade"
var forms_by_id: Dictionary = {}
var alias_to_id: Dictionary = {}
var forms_by_stage: Dictionary = {}

func _init(load_default: bool = true) -> void:
	for st in range(1, 25):
		forms_by_stage[st] = []
	if load_default:
		load_catalog(DEFAULT_CATALOG_PATH)

func load_catalog(res_path: String) -> bool:
	var raw_data: Dictionary = _read_json_dict(res_path)
	if raw_data.is_empty():
		push_warning("EvolutionCatalog: failed to read %s" % res_path)
		return false
	if raw_data.has("eras") and typeof(raw_data["eras"]) == TYPE_ARRAY:
		eras = raw_data["eras"].duplicate(true)
	if raw_data.has("lineages") and typeof(raw_data["lineages"]) == TYPE_DICTIONARY:
		lineages = raw_data["lineages"].duplicate(true)
	if raw_data.has("root_form_id"):
		root_form_id = str(raw_data["root_form_id"])
	var forms_arr: Array = raw_data.get("forms", [])
	for item in forms_arr:
		if typeof(item) == TYPE_DICTIONARY:
			register_form(item)
	return forms_by_id.size() > 0

func register_form(raw_form: Dictionary) -> bool:
	var fid: String = str(raw_form.get("id", "")).strip_edges()
	if fid == "":
		return false
	var d: Dictionary = raw_form.duplicate(true)
	# Normalize color fields into Godot Color objects for seamless runtime use while keeping hex strings accessible
	for col_key in ["blade_color", "edge_color", "guard_color", "aura_color", "slash_color"]:
		var cv = d.get(col_key, "#ffffff")
		if typeof(cv) == TYPE_STRING:
			d[col_key + "_hex"] = cv
			d[col_key] = Color(cv)
		elif typeof(cv) == TYPE_COLOR:
			d[col_key + "_hex"] = "#" + (cv as Color).to_html(false)
	var st: int = clampi(int(d.get("stage", 1)), 1, 24)
	d["stage"] = st
	# Provide backward-compatible legacy fields expected by existing combat/HUD helpers
	var bs: Dictionary = d.get("base_stats", {})
	if not d.has("base_damage"):
		d["base_damage"] = float(bs.get("physical_damage", 18.0))
	if not d.has("attack_speed"):
		d["attack_speed"] = float(bs.get("attack_speed", 1.15))
	if not d.has("range"):
		d["range"] = float(bs.get("attack_range", 3.1))
	if not d.has("crit_chance"):
		d["crit_chance"] = float(bs.get("crit_chance", 0.10))
	if not d.has("tier_index"):
		d["tier_index"] = st - 1
	var uc: Dictionary = d.get("unlock_conditions", {})
	if not d.has("min_level"):
		d["min_level"] = int(uc.get("min_level", 1))
	if not d.has("next_evolution_level"):
		d["next_evolution_level"] = st * 3 if st < 24 else 999

	# Remove previous stage entry if re-registering an existing ID
	if forms_by_id.has(fid):
		var old_st: int = int(forms_by_id[fid].get("stage", st))
		var old_list: Array = forms_by_stage.get(old_st, [])
		for idx in range(old_list.size() - 1, -1, -1):
			if str(old_list[idx].get("id", "")) == fid:
				old_list.remove_at(idx)

	forms_by_id[fid] = d
	if not forms_by_stage.has(st):
		forms_by_stage[st] = []
	(forms_by_stage[st] as Array).append(d)

	var alias_str: String = str(d.get("legacy_alias", "")).strip_edges()
	if alias_str != "":
		alias_to_id[alias_str] = fid
	return true

func resolve_id(id_or_alias: String) -> String:
	if forms_by_id.has(id_or_alias):
		return id_or_alias
	if alias_to_id.has(id_or_alias):
		return str(alias_to_id[id_or_alias])
	return ""

func has_form(id_or_alias: String) -> bool:
	return resolve_id(id_or_alias) != ""

func get_form(id_or_alias: String) -> Dictionary:
	var cid: String = resolve_id(id_or_alias)
	if cid == "":
		return {}
	return (forms_by_id[cid] as Dictionary).duplicate(true)

func get_all_forms() -> Array:
	var out: Array = []
	for st in range(1, 25):
		for f in forms_by_stage.get(st, []):
			out.append(f)
	return out

func get_forms_for_stage(stage: int) -> Array:
	return (forms_by_stage.get(stage, []) as Array).duplicate(true)

func get_forms_for_era(era_num: int) -> Array:
	var out: Array = []
	for st in range(1, 25):
		for f in forms_by_stage.get(st, []):
			if int(f.get("era", 0)) == era_num:
				out.append(f)
	return out

func get_next_forms(form_id: String) -> Array:
	var cid: String = resolve_id(form_id)
	if cid == "":
		return []
	var cur: Dictionary = forms_by_id[cid]
	var out: Array = []
	var next_ids: Array = cur.get("next_forms", [])
	for nid in next_ids:
		var snid: String = str(nid)
		if forms_by_id.has(snid):
			out.append((forms_by_id[snid] as Dictionary).duplicate(true))
	return out

func get_total_form_count() -> int:
	return forms_by_id.size()

static func _read_json_dict(res_path: String) -> Dictionary:
	if ResourceLoader.exists(res_path):
		var res = load(res_path)
		if res is JSON and typeof((res as JSON).data) == TYPE_DICTIONARY:
			return (res as JSON).data
	if FileAccess.file_exists(res_path):
		var f := FileAccess.open(res_path, FileAccess.READ)
		if f != null:
			var txt: String = f.get_as_text()
			f.close()
			var parsed = JSON.parse_string(txt)
			if typeof(parsed) == TYPE_DICTIONARY:
				return parsed
	return {}

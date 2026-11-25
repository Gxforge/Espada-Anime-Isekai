extends RefCounted
class_name ModelLoader

## Loads OBJ/mesh resources and builds normalized visual nodes.
## Keeps procedural builders as fallback for resilience.

static func load_mesh(path: String) -> Mesh:
	if path == "" or not ResourceLoader.exists(path):
		return null
	var res := load(path)
	if res is Mesh:
		return res
	return null

static func build_mesh_instance(path: String, color: Color = Color.WHITE, emission: Color = Color.BLACK, emission_energy: float = 0.0) -> MeshInstance3D:
	var mesh := load_mesh(path)
	if mesh == null:
		return null
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = 0.45
	mat.metallic = 0.35
	if emission_energy > 0.0:
		mat.emission_enabled = true
		mat.emission = emission
		mat.emission_energy_multiplier = emission_energy
	mi.material_override = mat
	return mi

static func normalize_node(node: Node3D, target_height: float) -> void:
	# Compute combined AABB
	var aabb := _combined_aabb(node)
	if aabb.size.y <= 0.001:
		return
	var scale_factor := target_height / aabb.size.y
	node.scale = Vector3.ONE * scale_factor
	# Recompute after scale for centering
	var aabb2 := _combined_aabb(node)
	# Center XZ and put base at y=0
	var center := aabb2.position + aabb2.size * 0.5
	node.position.x -= center.x
	node.position.z -= center.z
	node.position.y -= aabb2.position.y

static func _combined_aabb(node: Node3D) -> AABB:
	var has := false
	var result := AABB()
	for child in node.get_children():
		if child is MeshInstance3D and child.mesh:
			var aabb: AABB = child.transform * child.mesh.get_aabb()
			if not has:
				result = aabb
				has = true
			else:
				result = result.merge(aabb)
		if child is Node3D:
			var child_aabb := _combined_aabb(child)
			if child_aabb.size != Vector3.ZERO:
				var transformed := AABB(child.transform * child_aabb.position, child_aabb.size * child.transform.basis.get_scale())
				# Simpler: merge by transforming 8 corners is overkill; approximate
				if not has:
					result = child_aabb
					result.position = child.transform * result.position
					has = true
				else:
					var ca := AABB(child.transform * child_aabb.position, child_aabb.size)
					result = result.merge(ca)
	if not has:
		return AABB(Vector3.ZERO, Vector3.ZERO)
	return result

static func build_sword_visual(tier: Dictionary, sword_level: int) -> Node3D:
	var path := str(tier.get("model_path", ""))
	var mi := build_mesh_instance(path, tier.get("blade_color", Color.WHITE), tier.get("aura_color", Color.WHITE), 0.25)
	if mi:
		var wrapper := Node3D.new()
		wrapper.name = "SwordOBJ"
		wrapper.add_child(mi)
		normalize_node(wrapper, 2.6)
		# OBJ swords may be oriented arbitrarily; rotate to point up/forward as needed.
		# Most sword OBJs: blade along +Y. Keep as-is; gameplay pivots handle swing.
		return wrapper
	# fallback
	var SwordBuilderScript = load("res://scripts/SwordBuilder.gd")
	return SwordBuilderScript.build_sword(str(tier.get("id", "wood")), sword_level)

static func build_monster_visual(def: Dictionary) -> Node3D:
	var path := str(def.get("model_path", ""))
	var mi := build_mesh_instance(path, def.get("primary_color", Color.WHITE), def.get("accent_color", Color.WHITE), 0.15)
	if mi:
		var wrapper := Node3D.new()
		wrapper.name = "MonsterOBJ"
		wrapper.add_child(mi)
		# Normalize to a base height; def.scale is applied by Monster.gd on model_holder
		var target_h := 2.0
		if bool(def.get("is_boss", false)):
			target_h = 2.4
		normalize_node(wrapper, target_h)
		return wrapper
	var Builder = load("res://scripts/MonsterBuilder.gd")
	return Builder.build_monster(str(def.get("id", "slime")))

static func build_knight_visual() -> Node3D:
	var path := "res://assets/models/hero_knight_wielder.obj"
	var mi := build_mesh_instance(path, Color(0.75, 0.78, 0.85), Color(0.3, 0.5, 0.8), 0.1)
	if mi:
		var wrapper := Node3D.new()
		wrapper.name = "KnightOBJ"
		wrapper.add_child(mi)
		normalize_node(wrapper, 2.2)
		return wrapper
	return null

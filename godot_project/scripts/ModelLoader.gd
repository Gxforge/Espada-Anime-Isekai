extends RefCounted
class_name ModelLoader

## Loads GLB/glTF PackedScene PBR models as well as legacy OBJ/Mesh resources
## and builds normalized visual nodes. Keeps procedural builders as fallback.

static func load_mesh(path: String) -> Mesh:
	if path == "" or not ResourceLoader.exists(path):
		return null
	var res := load(path)
	if res is Mesh:
		return res
	return null

static func build_glb_scene_instance(path: String, target_height: float = 2.6, preserve_hilt_pivot: bool = true) -> Node3D:
	if path == "" or not (path.ends_with(".glb") or path.ends_with(".gltf")):
		return null
	if not ResourceLoader.exists(path):
		return null
	var res := load(path)
	if not (res is PackedScene):
		return null
	var inst := (res as PackedScene).instantiate()
	if not (inst is Node3D):
		inst.free()
		return null
	var scene_root := inst as Node3D
	var wrapper := Node3D.new()
	wrapper.name = "SwordGLB"
	wrapper.add_child(scene_root)
	var aabb := _combined_aabb_local(scene_root, Transform3D.IDENTITY)
	if aabb.size.y > 0.001:
		var scale_factor := target_height / aabb.size.y
		scene_root.scale = Vector3.ONE * scale_factor
		if not preserve_hilt_pivot:
			var center := (aabb.position + aabb.size * 0.5) * scale_factor
			scene_root.position = Vector3(-center.x, -aabb.position.y * scale_factor, -center.z)
	return wrapper

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
	var aabb := _combined_aabb_local(node, Transform3D.IDENTITY)
	if aabb.size.y <= 0.001:
		return
	var scale_factor := target_height / aabb.size.y
	node.scale = Vector3.ONE * scale_factor
	var scaled_pos := aabb.position * scale_factor
	var scaled_size := aabb.size * scale_factor
	var center := scaled_pos + scaled_size * 0.5
	node.position.x -= center.x
	node.position.z -= center.z
	node.position.y -= scaled_pos.y

static func _combined_aabb_local(node: Node3D, parent_xform: Transform3D) -> AABB:
	var has := false
	var result := AABB()
	if node is MeshInstance3D and (node as MeshInstance3D).mesh:
		var mi := node as MeshInstance3D
		result = _transform_aabb(parent_xform, mi.mesh.get_aabb())
		has = true
	for child in node.get_children():
		if child is Node3D:
			var c3 := child as Node3D
			var sub := _combined_aabb_local(c3, parent_xform * c3.transform)
			if sub.size != Vector3.ZERO:
				if not has:
					result = sub
					has = true
				else:
					result = result.merge(sub)
	if not has:
		return AABB(Vector3.ZERO, Vector3.ZERO)
	return result

static func _transform_aabb(xform: Transform3D, box: AABB) -> AABB:
	var p0 := box.position
	var s := box.size
	var corners := [
		Vector3(p0.x, p0.y, p0.z),
		Vector3(p0.x + s.x, p0.y, p0.z),
		Vector3(p0.x, p0.y + s.y, p0.z),
		Vector3(p0.x, p0.y, p0.z + s.z),
		Vector3(p0.x + s.x, p0.y + s.y, p0.z),
		Vector3(p0.x + s.x, p0.y, p0.z + s.z),
		Vector3(p0.x, p0.y + s.y, p0.z + s.z),
		Vector3(p0.x + s.x, p0.y + s.y, p0.z + s.z),
	]
	var first: Vector3 = xform * corners[0]
	var res := AABB(first, Vector3.ZERO)
	for i in range(1, corners.size()):
		res = res.expand(xform * corners[i])
	return res

static func count_mesh_instances(node: Node) -> int:
	var total := 0
	if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
		total += 1
	for c in node.get_children():
		total += count_mesh_instances(c)
	return total

static func build_sword_visual(tier: Dictionary, sword_level: int) -> Node3D:
	var path := str(tier.get("model_path", ""))
	# 1. Preferred Studio Lexair pipeline: authored multi-part PBR .glb / .gltf PackedScene
	var glb_node := build_glb_scene_instance(path, 2.6, true)
	if glb_node != null:
		return glb_node
	# 2. Legacy OBJ single-mesh compatibility path
	var mi := build_mesh_instance(path, tier.get("blade_color", Color.WHITE), tier.get("aura_color", Color.WHITE), 0.25)
	if mi:
		var wrapper := Node3D.new()
		wrapper.name = "SwordOBJ"
		wrapper.add_child(mi)
		normalize_node(wrapper, 2.6)
		return wrapper
	# 3. Resilience fallback
	var SwordBuilderScript = load("res://scripts/SwordBuilder.gd")
	return SwordBuilderScript.build_sword(str(tier.get("id", "wood")), sword_level)

static func build_monster_visual(def: Dictionary) -> Node3D:
	var path := str(def.get("model_path", ""))
	var glb_node := build_glb_scene_instance(path, 2.4 if bool(def.get("is_boss", false)) else 2.0, false)
	if glb_node != null:
		glb_node.name = "MonsterGLB"
		return glb_node
	var mi := build_mesh_instance(path, def.get("primary_color", Color.WHITE), def.get("accent_color", Color.WHITE), 0.15)
	if mi:
		var wrapper := Node3D.new()
		wrapper.name = "MonsterOBJ"
		wrapper.add_child(mi)
		var target_h := 2.4 if bool(def.get("is_boss", false)) else 2.0
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

extends RefCounted
class_name CustomGeometry

static func make_mat(color: Color, metallic: float = 0.5, roughness: float = 0.5, emission: Color = Color.BLACK, emission_energy: float = 0.0, transparent: bool = false, alpha: float = 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(color.r, color.g, color.b, alpha)
	m.metallic = metallic
	m.roughness = roughness
	if emission_energy > 0.0:
		m.emission_enabled = true
		m.emission = emission
		m.emission_energy_multiplier = emission_energy
	if transparent or alpha < 1.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m

static func add_mesh(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3 = Vector3.ZERO, rot: Vector3 = Vector3.ZERO, scl: Vector3 = Vector3.ONE, mesh_name: String = "") -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.rotation = rot
	mi.scale = scl
	if mesh_name != "":
		mi.name = mesh_name
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	parent.add_child(mi)
	return mi

static func box(size: Vector3) -> BoxMesh:
	var m := BoxMesh.new()
	m.size = size
	return m

static func cyl(r_top: float, r_bottom: float, h: float, segments: int = 12) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = r_top
	m.bottom_radius = r_bottom
	m.height = h
	m.radial_segments = segments
	return m

static func sphere(r: float, hseg: int = 12, vseg: int = 8) -> SphereMesh:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r * 2.0
	m.radial_segments = hseg
	m.rings = vseg
	return m

static func cone(r: float, h: float, segments: int = 8) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = 0.0
	m.bottom_radius = r
	m.height = h
	m.radial_segments = segments
	return m

static func torus(inner_r: float, outer_r: float, ring_seg: int = 12, pipe_seg: int = 8) -> TorusMesh:
	var m := TorusMesh.new()
	m.inner_radius = inner_r
	m.outer_radius = outer_r
	m.ring_segments = ring_seg
	m.rings = pipe_seg
	return m

static func capsule(r: float, h: float) -> CapsuleMesh:
	var m := CapsuleMesh.new()
	m.radius = r
	m.height = h
	return m

static func create_diamond_blade(length: float, base_width: float, mid_width: float, tip_length: float, thickness: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var y0 := 0.0
	var y1 := length * 0.18
	var y2 := length * 0.55
	var y3 := length - tip_length
	var y_tip := length
	var w0 := base_width * 0.5
	var w1 := (base_width * 1.04) * 0.5
	var w2 := mid_width * 0.5
	var w3 := (mid_width * 0.78) * 0.5
	var t0 := thickness * 0.5
	var t1 := thickness * 0.52
	var t2 := thickness * 0.44
	var t3 := thickness * 0.32
	var rings := [
		{"y":y0,"w":w0,"t":t0}, {"y":y1,"w":w1,"t":t1},
		{"y":y2,"w":w2,"t":t2}, {"y":y3,"w":w3,"t":t3},
	]
	for i in range(rings.size() - 1):
		var rA = rings[i]; var rB = rings[i+1]
		var A_l := Vector3(-rA.w, rA.y, 0); var A_f := Vector3(0, rA.y, rA.t)
		var A_r := Vector3(rA.w, rA.y, 0);  var A_b := Vector3(0, rA.y, -rA.t)
		var B_l := Vector3(-rB.w, rB.y, 0); var B_f := Vector3(0, rB.y, rB.t)
		var B_r := Vector3(rB.w, rB.y, 0);  var B_b := Vector3(0, rB.y, -rB.t)
		_add_quad(st, A_l, A_f, B_f, B_l)
		_add_quad(st, A_f, A_r, B_r, B_f)
		_add_quad(st, A_r, A_b, B_b, B_r)
		_add_quad(st, A_b, A_l, B_l, B_b)
	var last = rings[rings.size()-1]
	var tip := Vector3(0, y_tip, 0)
	var L := Vector3(-last.w, last.y, 0); var F := Vector3(0, last.y, last.t)
	var R := Vector3(last.w, last.y, 0);  var Bk := Vector3(0, last.y, -last.t)
	_add_tri(st, L, F, tip); _add_tri(st, F, R, tip)
	_add_tri(st, R, Bk, tip); _add_tri(st, Bk, L, tip)
	# bottom cap
	var f0 = rings[0]
	_add_tri(st, Vector3(-f0.w,f0.y,0), Vector3(f0.w,f0.y,0), Vector3(0,f0.y,f0.t))
	_add_tri(st, Vector3(f0.w,f0.y,0), Vector3(-f0.w,f0.y,0), Vector3(0,f0.y,-f0.t))
	st.generate_normals()
	return st.commit()

static func _add_tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3) -> void:
	st.add_vertex(a); st.add_vertex(b); st.add_vertex(c)

static func _add_quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3) -> void:
	_add_tri(st, a, b, c)
	_add_tri(st, a, c, d)

static func create_crescent_wave(radius: float, width: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var segments := 18
	for i in range(segments):
		var tA := (float(i) / segments - 0.5) * PI * 0.85
		var tB := (float(i + 1) / segments - 0.5) * PI * 0.85
		var taperA := cos((float(i) / segments - 0.5) * PI)
		var taperB := cos((float(i + 1) / segments - 0.5) * PI)
		var rOuterA: float = radius
		var rInnerA: float = radius - width * maxf(0.12, taperA)
		var rOuterB: float = radius
		var rInnerB: float = radius - width * maxf(0.12, taperB)
		var xOA: float = sin(tA) * rOuterA; var zOA: float = cos(tA) * rOuterA
		var xIA: float = sin(tA) * rInnerA; var zIA: float = cos(tA) * rInnerA
		var xOB: float = sin(tB) * rOuterB; var zOB: float = cos(tB) * rOuterB
		var xIB: float = sin(tB) * rInnerB; var zIB: float = cos(tB) * rInnerB
		var OAt := Vector3(xOA, 0.04*taperA, zOA)
		var IAt := Vector3(xIA, 0.04*taperA, zIA)
		var OBt := Vector3(xOB, 0.04*taperB, zOB)
		var IBt := Vector3(xIB, 0.04*taperB, zIB)
		var OAb := Vector3(xOA, -0.04*taperA, zOA)
		var IAb := Vector3(xIA, -0.04*taperA, zIA)
		var OBb := Vector3(xOB, -0.04*taperB, zOB)
		var IBb := Vector3(xIB, -0.04*taperB, zIB)
		_add_quad(st, IAt, OAt, OBt, IBt)
		_add_quad(st, OAb, IAb, IBb, OBb)
	st.generate_normals()
	return st.commit()

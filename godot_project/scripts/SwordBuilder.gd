extends RefCounted
class_name SwordBuilder

const CG = preload("res://scripts/CustomGeometry.gd")

static func build_sword(tier_id: String, level: int = 1) -> Node3D:
	var root := Node3D.new()
	root.name = "Sword_%s_Lv%d" % [tier_id, level]
	var pivot := Node3D.new()
	pivot.name = "BladePivot"
	root.add_child(pivot)
	var sub := maxi(0, (level - 1) % 5)
	var glow := float(sub) * 0.18

	match tier_id:
		"wood":
			_build_wood(pivot, glow)
		"copper":
			_build_copper(pivot, glow)
		"iron":
			_build_iron(pivot, glow)
		"silver":
			_build_silver(pivot, glow)
		"gold":
			_build_gold(pivot, glow)
		"crystal":
			_build_crystal(pivot, glow)
		"obsidian":
			_build_obsidian(pivot, glow)
		"celestial":
			_build_celestial(pivot, glow)
		_:
			_build_wood(pivot, glow)
	return root

static func _build_wood(p: Node3D, glow: float) -> void:
	var oak := CG.make_mat(Color("#9c6635"), 0.05, 0.78)
	var dark := CG.make_mat(Color("#5c3a1e"), 0.05, 0.85)
	var bevel := CG.make_mat(Color("#c48f5a"), 0.08, 0.65, Color("#4ade80"), float(glow)*0.3)
	var rope := CG.make_mat(Color("#d9b98b"), 0.0, 0.9)
	var leaf := CG.make_mat(Color("#22c55e"), 0.0, 0.4, Color("#16a34a"), 0.35 + glow)
	CG.add_mesh(p, CG.cyl(0.065,0.08,0.56), dark, Vector3(0,-0.28,0))
	for i in range(5):
		var r := CG.add_mesh(p, CG.torus(0.056,0.074,14,8), rope, Vector3(0,-0.46+i*0.09,0))
		r.rotation.x = PI/2 + (0.12 if i%2==0 else -0.12)
	CG.add_mesh(p, CG.sphere(0.12,8,6), dark, Vector3(0,-0.6,0))
	CG.add_mesh(p, CG.sphere(0.065,6,4), leaf, Vector3(0,-0.6,0.09))
	CG.add_mesh(p, CG.box(Vector3(0.76,0.13,0.16)), dark, Vector3(0,0.02,0))
	CG.add_mesh(p, CG.box(Vector3(0.12,0.17,0.18)), oak, Vector3(-0.38,0.03,0), Vector3(0,0,0.2))
	CG.add_mesh(p, CG.box(Vector3(0.12,0.17,0.18)), oak, Vector3(0.38,0.03,0), Vector3(0,0,-0.2))
	var blade := CG.create_diamond_blade(2.05,0.28,0.25,0.42,0.11)
	CG.add_mesh(p, blade, bevel, Vector3(0,0.08,0))
	CG.add_mesh(p, CG.box(Vector3(0.08,1.5,0.118)), oak, Vector3(0,0.85,0))
	for i in range(int(glow / 0.18)):
		CG.add_mesh(p, CG.sphere(0.042,6,4), leaf, Vector3(0,0.4+i*0.32,0.065))
		CG.add_mesh(p, CG.sphere(0.042,6,4), leaf, Vector3(0,0.4+i*0.32,-0.065))

static func _build_copper(p: Node3D, glow: float) -> void:
	var copper := CG.make_mat(Color("#e07a45"), 0.86, 0.26, Color("#9a3412"), 0.14 + glow*0.5)
	var dark := CG.make_mat(Color("#7c3f23"), 0.8, 0.42)
	var patina := CG.make_mat(Color("#2dd4bf"), 0.5, 0.35, Color("#0d9488"), 0.45 + glow)
	var leather := CG.make_mat(Color("#3b1f14"), 0.1, 0.75)
	CG.add_mesh(p, CG.cyl(0.065,0.075,0.62), leather, Vector3(0,-0.31,0))
	for i in range(4):
		var r := CG.add_mesh(p, CG.torus(0.06,0.074,18,8), copper, Vector3(0,-0.52+i*0.14,0))
		r.rotation.x = PI/2
	CG.add_mesh(p, CG.cyl(0.13,0.09,0.16,8), dark, Vector3(0,-0.68,0), Vector3(PI/2,0,0))
	var pg := CG.add_mesh(p, CG.sphere(0.075,6,4), patina, Vector3(0,-0.68,0))
	pg.scale = Vector3(1,1,1.4)
	CG.add_mesh(p, CG.box(Vector3(0.34,0.18,0.18)), dark, Vector3(0,0.04,0))
	CG.add_mesh(p, CG.sphere(0.085,6,4), patina, Vector3(0,0.04,0.1))
	CG.add_mesh(p, CG.sphere(0.085,6,4), patina, Vector3(0,0.04,-0.1))
	for side in [-1,1]:
		var h := CG.add_mesh(p, CG.cone(0.085,0.45,8), copper, Vector3(side*0.34,0.09,0))
		h.rotation.z = -side*1.15
	CG.add_mesh(p, CG.box(Vector3(0.32,0.28,0.13)), dark, Vector3(0,0.22,0))
	CG.add_mesh(p, CG.create_diamond_blade(2.32,0.33,0.29,0.48,0.115), copper, Vector3(0,0.12,0))
	CG.add_mesh(p, CG.box(Vector3(0.065,1.65,0.122)), dark, Vector3(0,1.02,0))
	CG.add_mesh(p, CG.box(Vector3(0.025,1.45,0.128)), patina, Vector3(0,0.98,0))

static func _build_iron(p: Node3D, glow: float) -> void:
	var steel := CG.make_mat(Color("#cbd5e1"), 0.92, 0.2)
	var dark := CG.make_mat(Color("#334155"), 0.85, 0.38)
	var gripm := CG.make_mat(Color("#7f1d1d"), 0.15, 0.65)
	var ruby := CG.make_mat(Color("#ef4444"), 0.2, 0.2, Color("#dc2626"), 0.55 + glow)
	CG.add_mesh(p, CG.cyl(0.068,0.078,0.74), gripm, Vector3(0,-0.37,0))
	var wr := CG.add_mesh(p, CG.torus(0.064,0.082,16,8), dark, Vector3(0,-0.37,0)); wr.rotation.x=PI/2
	CG.add_mesh(p, CG.sphere(0.145,8,6), dark, Vector3(0,-0.8,0))
	var spike := CG.add_mesh(p, CG.cone(0.07,0.16,6), steel, Vector3(0,-0.94,0)); spike.rotation.x=PI
	CG.add_mesh(p, CG.box(Vector3(0.96,0.12,0.16)), dark, Vector3(0,0.03,0))
	for side in [-1,1]:
		var fl := CG.add_mesh(p, CG.sphere(0.13,8,6), steel, Vector3(side*0.52,0.03,0)); fl.scale=Vector3(1.3,0.8,0.7)
	CG.add_mesh(p, CG.cyl(0.14,0.08,0.24,6), dark, Vector3(0,0.05,0))
	CG.add_mesh(p, CG.sphere(0.09,6,4), ruby, Vector3(0,0.05,0.13))
	CG.add_mesh(p, CG.sphere(0.09,6,4), ruby, Vector3(0,0.05,-0.13))
	CG.add_mesh(p, CG.create_diamond_blade(2.58,0.37,0.33,0.52,0.125), steel, Vector3(0,0.1,0))
	for side in [-1,1]:
		var hk := CG.add_mesh(p, CG.cone(0.06,0.24,5), dark, Vector3(side*0.24,0.45,0)); hk.rotation.z=-side*0.9
	CG.add_mesh(p, CG.box(Vector3(0.09,1.9,0.132)), dark, Vector3(0,1.12,0))

static func _build_silver(p: Node3D, glow: float) -> void:
	var silver := CG.make_mat(Color("#f1f5f9"), 0.96, 0.14, Color("#1e40af"), 0.15)
	var blue := CG.make_mat(Color("#1e3a8a"), 0.75, 0.3)
	var rune := CG.make_mat(Color("#38bdf8"), 0.2, 0.1, Color("#00f2fe"), 0.95 + glow)
	CG.add_mesh(p, CG.cyl(0.062,0.072,0.76,14), blue, Vector3(0,-0.38,0))
	var moon := CG.add_mesh(p, CG.torus(0.094,0.13,24,10), silver, Vector3(0,-0.84,0)); moon.rotation.z = PI*0.82
	CG.add_mesh(p, CG.sphere(0.075,6,4), rune, Vector3(0,-0.84,0))
	# wings (simplified as flattened boxes)
	for side in [-1,1]:
		var w := CG.add_mesh(p, CG.box(Vector3(0.62,0.22,0.06)), silver, Vector3(side*0.38,0.08,0))
		w.rotation.z = side*0.25
	CG.add_mesh(p, CG.sphere(0.16,8,6), blue, Vector3(0,0.06,0))
	CG.add_mesh(p, CG.sphere(0.095,6,4), rune, Vector3(0,0.06,0.12))
	CG.add_mesh(p, CG.sphere(0.095,6,4), rune, Vector3(0,0.06,-0.12))
	CG.add_mesh(p, CG.create_diamond_blade(2.75,0.36,0.31,0.58,0.12), silver, Vector3(0,0.12,0))
	for i in range(7):
		CG.add_mesh(p, CG.box(Vector3(0.05,0.08,0.02)), rune, Vector3(0,0.38+i*0.28,0.062))
		CG.add_mesh(p, CG.box(Vector3(0.05,0.08,0.02)), rune, Vector3(0,0.38+i*0.28,-0.062))

static func _build_gold(p: Node3D, glow: float) -> void:
	var gold := CG.make_mat(Color("#facc15"), 0.94, 0.16, Color("#d97706"), 0.22 + glow*0.4)
	var bronze := CG.make_mat(Color("#b45309"), 0.88, 0.28)
	var gem := CG.make_mat(Color("#f43f5e"), 0.2, 0.12, Color("#ff2a00"), 0.95 + glow)
	var halo := CG.make_mat(Color("#fef08a"), 0.3, 0.1, Color("#f59e0b"), 1.1)
	CG.add_mesh(p, CG.cyl(0.068,0.082,0.8), bronze, Vector3(0,-0.4,0))
	CG.add_mesh(p, CG.sphere(0.15,8,6), gold, Vector3(0,-0.86,0))
	var hr := CG.add_mesh(p, CG.torus(0.294,0.32,32,12), halo, Vector3(0,0.12,0)); hr.rotation.x=PI/2
	for side in [-1,1]:
		for f in range(3):
			var w := CG.add_mesh(p, CG.box(Vector3(0.55-f*0.08,0.18,0.05)), gold if f%2==0 else halo, Vector3(side*(0.35-f*0.04),0.06+f*0.08,0))
			w.rotation.z = side*(0.25-f*0.22)
	CG.add_mesh(p, CG.sphere(0.12,10,8), gem, Vector3(0,0.08,0))
	CG.add_mesh(p, CG.create_diamond_blade(2.92,0.42,0.36,0.62,0.13), gold, Vector3(0,0.14,0))
	CG.add_mesh(p, CG.box(Vector3(0.08,2.2,0.14)), halo, Vector3(0,1.3,0))

static func _build_crystal(p: Node3D, glow: float) -> void:
	var crystal := CG.make_mat(Color("#d8b4fe"), 0.35, 0.08, Color("#9333ea"), 0.48 + glow*0.5, true, 0.92)
	var arcane := CG.make_mat(Color("#f5d0fe"), 0.2, 0.05, Color("#e879f9"), 1.15)
	var plat := CG.make_mat(Color("#e2e8f0"), 0.92, 0.18)
	CG.add_mesh(p, CG.cyl(0.06,0.07,0.78,8), plat, Vector3(0,-0.39,0))
	var pom := CG.add_mesh(p, CG.sphere(0.15,6,4), arcane, Vector3(0,-0.9,0)); pom.scale=Vector3(0.8,1.4,0.8)
	for side in [-1,1]:
		var h := CG.add_mesh(p, CG.box(Vector3(0.42,0.12,0.12)), crystal, Vector3(side*0.36,0.08,0)); h.rotation.z = side*0.35
	CG.add_mesh(p, CG.sphere(0.15,6,4), arcane, Vector3(0,0.08,0))
	var r1 := CG.add_mesh(p, CG.torus(0.26,0.28,32,12), plat, Vector3(0,0.12,0)); r1.rotation.x=PI/2
	var r2 := CG.add_mesh(p, CG.torus(0.20,0.22,28,12), arcane, Vector3(0,0.12,0)); r2.rotation.x=PI/3
	CG.add_mesh(p, CG.create_diamond_blade(3.1,0.44,0.38,0.7,0.145), crystal, Vector3(0,0.15,0))
	CG.add_mesh(p, CG.create_diamond_blade(2.85,0.18,0.14,0.5,0.16), arcane, Vector3(0,0.2,0))
	for i in range(8):
		var side := 1 if i%2==0 else -1
		var row := i/2
		var sh := CG.add_mesh(p, CG.box(Vector3(0.06,0.28,0.06)), arcane, Vector3(side*0.36,0.55+row*0.55,0))
		sh.rotation.z = -side*0.15

static func _build_obsidian(p: Node3D, glow: float) -> void:
	var obs := CG.make_mat(Color("#18181b"), 0.88, 0.22)
	var magma := CG.make_mat(Color("#ff4500"), 0.2, 0.15, Color("#ff2200"), 1.2 + glow)
	var bone := CG.make_mat(Color("#d6d3d1"), 0.2, 0.55)
	CG.add_mesh(p, CG.cyl(0.072,0.086,0.84,10), obs, Vector3(0,-0.42,0))
	CG.add_mesh(p, CG.sphere(0.16,8,6), magma, Vector3(0,-0.92,0))
	var skull := CG.add_mesh(p, CG.sphere(0.22,8,6), obs, Vector3(0,0.08,0)); skull.scale=Vector3(1.3,1.0,1.1)
	for side in [-1,1]:
		CG.add_mesh(p, CG.sphere(0.045,6,4), magma, Vector3(side*0.1,0.12,0.19))
		var h := CG.add_mesh(p, CG.cone(0.11,0.68,8), bone, Vector3(side*0.44,0.22,0)); h.rotation.z = -side*1.05
	CG.add_mesh(p, CG.create_diamond_blade(3.25,0.48,0.4,0.55,0.15), obs, Vector3(0,0.14,0))
	CG.add_mesh(p, CG.create_diamond_blade(2.95,0.22,0.18,0.45,0.165), magma, Vector3(0,0.18,0))

static func _build_celestial(p: Node3D, glow: float) -> void:
	var astral := CG.make_mat(Color("#38bdf8"), 0.9, 0.08, Color("#0284c7"), 0.75)
	var gold := CG.make_mat(Color("#fef08a"), 0.95, 0.12, Color("#f59e0b"), 0.85)
	var voidm := CG.make_mat(Color("#090514"), 0.3, 0.05, Color("#7e22ce"), 0.5)
	var plasma := CG.make_mat(Color("#67e8f9"), 0.3, 0.05, Color("#22d3ee"), 1.4)
	CG.add_mesh(p, CG.cyl(0.068,0.08,0.88,16), gold, Vector3(0,-0.44,0))
	CG.add_mesh(p, CG.sphere(0.16,12,10), voidm, Vector3(0,0.14,0))
	var r1 := CG.add_mesh(p, CG.torus(0.298,0.32,36,12), plasma, Vector3(0,0.14,0)); r1.rotation.x=0.8
	var r2 := CG.add_mesh(p, CG.torus(0.402,0.42,36,12), gold, Vector3(0,0.14,0)); r2.rotation.y=0.8
	for side in [-1,1]:
		var uw := CG.add_mesh(p, CG.box(Vector3(0.85,0.28,0.05)), gold, Vector3(side*0.55,0.18,0)); uw.rotation.z = side*0.25
		var lw := CG.add_mesh(p, CG.box(Vector3(0.65,0.22,0.04)), plasma, Vector3(side*0.45,-0.02,0)); lw.rotation.z = -side*0.35
	for side in [-1,1]:
		CG.add_mesh(p, CG.create_diamond_blade(3.45,0.22,0.19,0.65,0.12), astral, Vector3(side*0.13,0.22,0))
	CG.add_mesh(p, CG.create_diamond_blade(3.65,0.16,0.14,0.55,0.15), plasma, Vector3(0,0.22,0))
	for s in range(4):
		var a := (float(s)/4.0)*TAU
		CG.add_mesh(p, CG.sphere(0.085,6,4), gold, Vector3(cos(a)*0.48, 1.4+(s%2)*0.7, sin(a)*0.48))

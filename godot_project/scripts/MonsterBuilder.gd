extends RefCounted
class_name MonsterBuilder

const CG = preload("res://scripts/CustomGeometry.gd")

static func build_monster(monster_id: String) -> Node3D:
	var root := Node3D.new()
	root.name = "Monster_%s" % monster_id
	match monster_id:
		"slime": _build_slime(root)
		"goblin": _build_goblin(root)
		"skeleton": _build_skeleton(root)
		"copper_golem": _build_copper_golem(root)
		"orc_berserker": _build_orc_berserker(root)
		"crimson_drake": _build_crimson_drake(root)
		"demon_lord": _build_demon_lord(root)
		_: _build_slime(root)
	return root

static func _build_slime(p: Node3D) -> void:
	var gel := CG.make_mat(Color("#22c55e"), 0.1, 0.15, Color("#15803d"), 0.2, true, 0.84)
	var core := CG.make_mat(Color("#86efac"), 0.1, 0.2, Color("#4ade80"), 0.85)
	var moss := CG.make_mat(Color("#166534"), 0.0, 0.85)
	var white := CG.make_mat(Color.WHITE, 0.0, 0.2)
	var evil := CG.make_mat(Color("#ff2a00"), 0.0, 0.2, Color("#ff1100"), 0.9)
	var body := CG.add_mesh(p, CG.sphere(0.85,16,12), gel, Vector3(0,0.72,0)); body.scale=Vector3(1.12,0.88,1.12)
	CG.add_mesh(p, CG.cyl(0.82,1.02,0.28,16), gel, Vector3(0,0.16,0))
	CG.add_mesh(p, CG.sphere(0.34,8,6), core, Vector3(0,0.72,0))
	for b in range(5):
		var ang := (float(b)/5.0)*TAU
		CG.add_mesh(p, CG.sphere(0.09 + (b%2)*0.04,6,4), core, Vector3(cos(ang)*0.42,0.55+(b%3)*0.18,sin(ang)*0.42))
	for side in [-1,1]:
		CG.add_mesh(p, CG.sphere(0.13,8,6), white, Vector3(side*0.28,0.82,0.76))
		CG.add_mesh(p, CG.sphere(0.07,6,4), evil, Vector3(side*0.28,0.82,0.86))
		var brow := CG.add_mesh(p, CG.box(Vector3(0.24,0.06,0.08)), moss, Vector3(side*0.28,0.96,0.82)); brow.rotation.z = -side*0.35
	CG.add_mesh(p, CG.cone(0.28,0.36,6), moss, Vector3(0,1.48,0))

static func _build_goblin(p: Node3D) -> void:
	var skin := CG.make_mat(Color("#65a30d"), 0.0, 0.65)
	var leather := CG.make_mat(Color("#78350f"), 0.0, 0.8)
	var iron := CG.make_mat(Color("#52525b"), 0.8, 0.4)
	var evil := CG.make_mat(Color("#ff2a00"), 0.0, 0.2, Color("#ff1100"), 0.9)
	var white := CG.make_mat(Color.WHITE, 0.0, 0.3)
	CG.add_mesh(p, CG.box(Vector3(0.72,0.82,0.46)), skin, Vector3(0,1.15,0))
	CG.add_mesh(p, CG.box(Vector3(0.78,0.26,0.52)), leather, Vector3(0,0.82,0))
	CG.add_mesh(p, CG.box(Vector3(0.58,0.54,0.56)), skin, Vector3(0,1.9,0))
	var nose := CG.add_mesh(p, CG.cone(0.1,0.28,6), skin, Vector3(0,1.87,0.36)); nose.rotation.x = PI/2
	for side in [-1,1]:
		var ear := CG.add_mesh(p, CG.cone(0.12,0.52,5), skin, Vector3(side*0.48,1.93,0)); ear.rotation.z = -side*1.15
		CG.add_mesh(p, CG.sphere(0.075,6,4), evil, Vector3(side*0.15,1.95,0.28))
		CG.add_mesh(p, CG.cone(0.035,0.1,5), white, Vector3(side*0.12,1.71,0.29))
	# arms
	for side in [-1,1]:
		CG.add_mesh(p, CG.cyl(0.11,0.09,0.65,8), skin, Vector3(side*0.5,1.17,0))
		CG.add_mesh(p, CG.cyl(0.13,0.1,0.72,8), skin, Vector3(side*0.22,0.36,0))
	# club
	var club := CG.add_mesh(p, CG.cyl(0.06,0.16,0.95,8), leather, Vector3(0.6,0.85,0.35)); club.rotation.x = PI/2
	CG.add_mesh(p, CG.sphere(0.12,6,4), iron, Vector3(0.6,0.85,0.82))
	# shield
	var sh := CG.add_mesh(p, CG.cyl(0.42,0.42,0.08,12), leather, Vector3(-0.7,1.0,0.2)); sh.rotation.z = PI/2

static func _build_skeleton(p: Node3D) -> void:
	var bone := CG.make_mat(Color("#e2e8f0"), 0.1, 0.45)
	var steel := CG.make_mat(Color("#334155"), 0.85, 0.35)
	var soul := CG.make_mat(Color("#38bdf8"), 0.2, 0.1, Color("#00f2fe"), 1.2)
	CG.add_mesh(p, CG.cyl(0.09,0.09,0.95,8), bone, Vector3(0,1.25,0))
	for r in range(4):
		var rib := CG.add_mesh(p, CG.torus(0.28-r*0.02,0.32-r*0.02,14,6), bone, Vector3(0,1.55-r*0.14,0)); rib.rotation.x=PI/2
	CG.add_mesh(p, CG.cyl(0.32,0.24,0.22,8), bone, Vector3(0,0.82,0))
	CG.add_mesh(p, CG.sphere(0.32,10,8), bone, Vector3(0,2.06,0))
	CG.add_mesh(p, CG.box(Vector3(0.34,0.18,0.34)), bone, Vector3(0,1.86,0.08))
	CG.add_mesh(p, CG.cone(0.36,0.35,8), steel, Vector3(0,2.26,0))
	for side in [-1,1]:
		CG.add_mesh(p, CG.sphere(0.075,6,4), soul, Vector3(side*0.12,2.04,0.27))
		var horn := CG.add_mesh(p, CG.cone(0.07,0.42,6), bone, Vector3(side*0.36,2.3,0)); horn.rotation.z = -side*0.85
		CG.add_mesh(p, CG.cyl(0.07,0.06,0.75,6), bone, Vector3(side*0.48,1.27,0))
		CG.add_mesh(p, CG.cyl(0.08,0.07,0.78,6), bone, Vector3(side*0.2,0.37,0))
	# shield and sword
	CG.add_mesh(p, CG.box(Vector3(0.1,0.85,0.58)), steel, Vector3(-0.66,1.17,0.18))
	var sw := CG.add_mesh(p, CG.box(Vector3(0.12,1.2,0.04)), steel, Vector3(0.62,1.0,0.35)); sw.rotation.x = PI/2

static func _build_copper_golem(p: Node3D) -> void:
	var rock := CG.make_mat(Color("#57534e"), 0.15, 0.88)
	var ore := CG.make_mat(Color("#ea580c"), 0.85, 0.25, Color("#c2410c"), 0.65)
	var body := CG.add_mesh(p, CG.sphere(0.82,8,6), rock, Vector3(0,1.55,0)); body.scale=Vector3(1.25,1.05,0.9)
	CG.add_mesh(p, CG.sphere(0.35,6,4), ore, Vector3(0,1.55,0.62))
	for side in [-1,1]:
		var c := CG.add_mesh(p, CG.sphere(0.26,6,4), ore, Vector3(side*0.75,2.15,0)); c.scale=Vector3(0.7,1.7,0.7); c.rotation.z=-side*0.4
		CG.add_mesh(p, CG.sphere(0.44,8,6), rock, Vector3(side*1.05,1.32,0))
		CG.add_mesh(p, CG.cyl(0.3,0.36,0.88,7), rock, Vector3(side*0.42,0.44,0))
	CG.add_mesh(p, CG.box(Vector3(0.62,0.56,0.58)), rock, Vector3(0,2.47,0))
	CG.add_mesh(p, CG.box(Vector3(0.44,0.14,0.12)), ore, Vector3(0,2.49,0.28))

static func _build_orc_berserker(p: Node3D) -> void:
	var skin := CG.make_mat(Color("#15803d"), 0.0, 0.6)
	var armor := CG.make_mat(Color("#27272a"), 0.82, 0.35)
	var red := CG.make_mat(Color("#dc2626"), 0.85, 0.25, Color("#7f1d1d"), 0.35)
	var white := CG.make_mat(Color.WHITE, 0.0, 0.3)
	var evil := CG.make_mat(Color("#ff2a00"), 0.0, 0.2, Color("#ff1100"), 0.9)
	CG.add_mesh(p, CG.box(Vector3(1.05,1.05,0.65)), skin, Vector3(0,1.45,0))
	CG.add_mesh(p, CG.box(Vector3(1.1,0.55,0.7)), armor, Vector3(0,1.42,0))
	for side in [-1,1]:
		CG.add_mesh(p, CG.sphere(0.36,8,6), armor, Vector3(side*0.72,1.88,0))
		var sp := CG.add_mesh(p, CG.cone(0.1,0.36,6), red, Vector3(side*0.9,2.15,0)); sp.rotation.z=-side*0.5
		CG.add_mesh(p, CG.cyl(0.18,0.15,0.78,8), skin, Vector3(side*0.75,1.4,0))
		CG.add_mesh(p, CG.cyl(0.2,0.16,0.85,8), armor, Vector3(side*0.3,0.43,0))
		# axe
		CG.add_mesh(p, CG.cyl(0.05,0.05,1.25,8), armor, Vector3(side*0.85,1.0,0.35), Vector3(PI/2,0,0))
		CG.add_mesh(p, CG.box(Vector3(0.45,0.35,0.08)), red, Vector3(side*0.85,1.0,0.82))
	CG.add_mesh(p, CG.box(Vector3(0.64,0.62,0.64)), skin, Vector3(0,2.3,0))
	for side in [-1,1]:
		CG.add_mesh(p, CG.cone(0.06,0.26,6), white, Vector3(side*0.18,2.18,0.36))
		CG.add_mesh(p, CG.sphere(0.08,6,4), evil, Vector3(side*0.16,2.36,0.33))

static func _build_crimson_drake(p: Node3D) -> void:
	var scale_m := CG.make_mat(Color("#b91c1c"), 0.3, 0.4)
	var belly := CG.make_mat(Color("#f59e0b"), 0.2, 0.45, Color("#d97706"), 0.3)
	var horn := CG.make_mat(Color("#1c1917"), 0.5, 0.3)
	var body := CG.add_mesh(p, CG.cone(0.68,1.55,8), scale_m, Vector3(0,1.85,0)); body.rotation.x = PI*0.35
	CG.add_mesh(p, CG.box(Vector3(0.65,0.85,0.45)), belly, Vector3(0,1.85,0.28))
	var snout := CG.add_mesh(p, CG.cone(0.36,0.82,6), scale_m, Vector3(0,2.45,0.7)); snout.rotation.x = PI/2
	for side in [-1,1]:
		var h := CG.add_mesh(p, CG.cone(0.1,0.68,6), horn, Vector3(side*0.24,2.73,0.3)); h.rotation.x=-0.65; h.rotation.z=-side*0.35
		CG.add_mesh(p, CG.sphere(0.08,6,4), belly, Vector3(side*0.2,2.59,0.67))
		# wings
		var w := CG.add_mesh(p, CG.box(Vector3(1.6,0.6,0.06)), scale_m, Vector3(side*1.1,2.2,0)); w.rotation.z = side*0.25
		CG.add_mesh(p, CG.cone(0.16,0.72,6), horn, Vector3(side*0.38,0.89,0.1))
	for sp in range(5):
		var s := CG.add_mesh(p, CG.cone(0.09,0.34,6), horn, Vector3(0,2.35-sp*0.22,-0.25-sp*0.12)); s.rotation.x=-0.8
	var tail := CG.add_mesh(p, CG.cone(0.26,1.35,6), scale_m, Vector3(0,1.1,-1.1)); tail.rotation.x = -PI*0.42

static func _build_demon_lord(p: Node3D) -> void:
	var armor := CG.make_mat(Color("#18181b"), 0.9, 0.2)
	var flesh := CG.make_mat(Color("#7f1d1d"), 0.25, 0.45)
	var fire := CG.make_mat(Color("#ff4500"), 0.2, 0.15, Color("#ff1100"), 1.15)
	CG.add_mesh(p, CG.box(Vector3(1.25,1.35,0.78)), armor, Vector3(0,1.75,0))
	CG.add_mesh(p, CG.sphere(0.42,8,6), fire, Vector3(0,1.82,0.4))
	for side in [-1,1]:
		CG.add_mesh(p, CG.sphere(0.46,8,6), armor, Vector3(side*0.9,2.28,0))
		var h := CG.add_mesh(p, CG.cone(0.14,0.58,6), fire, Vector3(side*1.15,2.65,0)); h.rotation.z=-side*0.55
		CG.add_mesh(p, CG.cyl(0.22,0.18,0.95,8), flesh, Vector3(side*0.95,1.65,0))
		CG.add_mesh(p, CG.cyl(0.24,0.2,1.05,8), armor, Vector3(side*0.38,0.53,0))
		# wings
		var w := CG.add_mesh(p, CG.box(Vector3(1.9,1.1,0.08)), armor, Vector3(side*1.3,2.2,-0.35)); w.rotation.z = side*0.2
	CG.add_mesh(p, CG.box(Vector3(0.68,0.68,0.68)), flesh, Vector3(0,2.82,0))
	var crown := CG.add_mesh(p, CG.torus(0.32,0.38,16,8), fire, Vector3(0,3.18,0)); crown.rotation.x = PI/2
	for side in [-1,1]:
		var gh := CG.add_mesh(p, CG.cone(0.14,0.85,8), armor, Vector3(side*0.48,3.18,0)); gh.rotation.z=-side*0.75
		CG.add_mesh(p, CG.sphere(0.1,6,4), fire, Vector3(side*0.18,2.86,0.35))
	# boss sword
	var bs := CG.add_mesh(p, CG.box(Vector3(0.35,2.3,0.08)), fire, Vector3(0.95,1.1,0.55)); bs.rotation.x = PI/2

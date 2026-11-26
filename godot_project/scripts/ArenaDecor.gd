extends Node3D
class_name ArenaDecor

## Construye la decoración 3D del Santuario de la Forja de Almas (inspirada en environmentModels.ts)
## Soporta niveles de calidad ("low", "medium", "high") sin afectar colisiones ni gameplay.

var _rune_mat: StandardMaterial3D
var _flames: Array[MeshInstance3D] = []
var _crystals: Array[MeshInstance3D] = []
var _scenic_nodes: Array[Node3D] = []
var _brazier_lights: Array[OmniLight3D] = []
var _player_ring: MeshInstance3D

func _ready() -> void:
	_build_decor()

func _build_decor() -> void:
	var stone_dark := CustomGeometry.make_mat(Color("#1e2430"), 0.12, 0.88)
	var stone_tile := CustomGeometry.make_mat(Color("#2a3242"), 0.16, 0.82)
	var stone_pillar := CustomGeometry.make_mat(Color("#374151"), 0.20, 0.75)
	var iron_anvil := CustomGeometry.make_mat(Color("#1f2937"), 0.88, 0.30)
	_rune_mat = CustomGeometry.make_mat(Color("#38bdf8"), 0.2, 0.25, Color("#0284c7"), 1.35)
	var fire_mat := CustomGeometry.make_mat(Color("#fb923c"), 0.05, 0.15, Color("#ff4500"), 3.2)

	# Outer glowing rune circle
	var outer_torus := TorusMesh.new()
	outer_torus.inner_radius = 16.45
	outer_torus.outer_radius = 16.82
	outer_torus.ring_segments = 48
	outer_torus.rings = 10
	CustomGeometry.add_mesh(self, outer_torus, _rune_mat, Vector3(0, 0.04, 0), Vector3.ZERO, Vector3.ONE, "OuterRuneRing")

	# 12 radial flagstone spokes
	for i in range(12):
		var ang := (float(i) / 12.0) * TAU
		var spoke := CustomGeometry.add_mesh(
			self,
			CustomGeometry.box(Vector3(1.05, 0.07, 21.5)),
			stone_dark,
			Vector3(sin(ang) * 16.8, 0.01, cos(ang) * 16.8),
			Vector3(0, ang, 0),
			Vector3.ONE,
			"Spoke_%d" % i
		)
		spoke.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF

	# Sacred Forge Anvil Altar at North (0, 0, -21.5)
	var altar := Node3D.new()
	altar.name = "SacredForgeAltar"
	altar.position = Vector3(0, 0, -21.5)
	add_child(altar)
	CustomGeometry.add_mesh(altar, CustomGeometry.cyl(3.3, 3.8, 0.44, 8), stone_pillar, Vector3(0, 0.22, 0))
	CustomGeometry.add_mesh(altar, CustomGeometry.cyl(2.2, 2.6, 0.44, 8), stone_tile, Vector3(0, 0.64, 0))
	CustomGeometry.add_mesh(altar, CustomGeometry.box(Vector3(1.3, 0.55, 0.85)), iron_anvil, Vector3(0, 1.14, 0))
	CustomGeometry.add_mesh(altar, CustomGeometry.box(Vector3(1.75, 0.44, 0.78)), iron_anvil, Vector3(0, 1.60, 0))
	CustomGeometry.add_mesh(altar, CustomGeometry.cone(0.34, 1.0, 8), iron_anvil, Vector3(-1.28, 1.60, 0), Vector3(0, 0, PI * 0.5))
	var altar_rune := TorusMesh.new()
	altar_rune.inner_radius = 2.65
	altar_rune.outer_radius = 2.85
	CustomGeometry.add_mesh(altar, altar_rune, _rune_mat, Vector3(0, 0.46, 0))

	# 8 Ancient Stone Pillars + Fire Braziers around perimeter
	for i in range(8):
		var ang := (float(i) / 8.0) * TAU + PI / 8.0
		var radius := 27.5
		var pgrp := Node3D.new()
		pgrp.name = "Pillar_%d" % i
		pgrp.position = Vector3(sin(ang) * radius, 0, cos(ang) * radius)
		pgrp.rotation.y = ang
		add_child(pgrp)

		CustomGeometry.add_mesh(pgrp, CustomGeometry.box(Vector3(2.0, 0.8, 2.0)), stone_pillar, Vector3(0, 0.4, 0))
		CustomGeometry.add_mesh(pgrp, CustomGeometry.cyl(0.70, 0.84, 5.1, 8), stone_pillar, Vector3(0, 3.35, 0))
		CustomGeometry.add_mesh(pgrp, CustomGeometry.cyl(0.79, 0.79, 0.34, 8), _rune_mat, Vector3(0, 2.8, 0))
		CustomGeometry.add_mesh(pgrp, CustomGeometry.box(Vector3(1.85, 0.52, 1.85)), stone_pillar, Vector3(0, 6.15, 0))
		CustomGeometry.add_mesh(pgrp, CustomGeometry.cyl(0.82, 0.44, 0.44, 10), iron_anvil, Vector3(0, 6.62, 0))

		var flame := CustomGeometry.add_mesh(
			pgrp,
			CustomGeometry.sphere(0.46, 6, 4),
			fire_mat,
			Vector3(0, 7.22, 0),
			Vector3.ZERO,
			Vector3(0.85, 1.55, 0.85),
			"Flame"
		)
		flame.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_flames.append(flame)

		if i % 2 == 0:
			var bl := OmniLight3D.new()
			bl.light_color = Color("#fb923c")
			bl.light_energy = 1.15
			bl.omni_range = 11.0
			bl.position = Vector3(0, 7.5, 0)
			pgrp.add_child(bl)
			_brazier_lights.append(bl)

	# Outer floating crystals & scenic pines (radius 32.5..35.5)
	var foliage_mat := CustomGeometry.make_mat(Color("#14532d"), 0.05, 0.88)
	var trunk_mat := CustomGeometry.make_mat(Color("#451a03"), 0.05, 0.92)
	for i in range(16):
		var ang := (float(i) / 16.0) * TAU
		var dist := 32.5 + float(i % 3) * 1.5
		var tx := sin(ang) * dist
		var tz := cos(ang) * dist
		if i % 4 == 0:
			var crystal := CustomGeometry.add_mesh(
				self,
				CustomGeometry.sphere(0.85, 6, 4),
				_rune_mat,
				Vector3(tx, 3.5, tz),
				Vector3.ZERO,
				Vector3(0.68, 2.25, 0.68),
				"Crystal_%d" % i
			)
			crystal.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			_crystals.append(crystal)
			_scenic_nodes.append(crystal)
		else:
			var tree := Node3D.new()
			tree.name = "Pine_%d" % i
			tree.position = Vector3(tx, 0, tz)
			var sc := 0.85 + float(i % 3) * 0.20
			tree.scale = Vector3.ONE * sc
			add_child(tree)
			CustomGeometry.add_mesh(tree, CustomGeometry.cyl(0.26, 0.40, 1.8, 7), trunk_mat, Vector3(0, 0.9, 0))
			for tier in range(3):
				CustomGeometry.add_mesh(
					tree,
					CustomGeometry.cone(1.60 - tier * 0.34, 2.05 - tier * 0.18, 7),
					foliage_mat,
					Vector3(0, 2.1 + tier * 1.12, 0)
				)
			_scenic_nodes.append(tree)

func apply_quality(q: String) -> void:
	var show_scenic := q != "low"
	var show_lights := q == "high"
	for n in _scenic_nodes:
		if is_instance_valid(n):
			n.visible = show_scenic
	for l in _brazier_lights:
		if is_instance_valid(l):
			l.visible = show_lights

func update_decor(time_sec: float, aura_color: Color) -> void:
	if _rune_mat:
		_rune_mat.albedo_color = aura_color.lerp(Color("#38bdf8"), 0.35)
		_rune_mat.emission = aura_color
	for i in range(_flames.size()):
		var fl := _flames[i]
		if is_instance_valid(fl):
			var pulse := 1.0 + sin(time_sec * 8.5 + float(i) * 1.7) * 0.16
			fl.scale = Vector3(0.82 * pulse, 1.50 * pulse, 0.82 * pulse)
			fl.rotation.y = time_sec * 2.2 + float(i)
	for i in range(_crystals.size()):
		var cr := _crystals[i]
		if is_instance_valid(cr):
			cr.position.y = 3.5 + sin(time_sec * 2.1 + float(i)) * 0.42
			cr.rotation.y = time_sec * 0.8 + float(i)

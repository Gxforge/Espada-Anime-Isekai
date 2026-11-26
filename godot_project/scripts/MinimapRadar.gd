extends Control
class_name MinimapRadar

## Radar circular anime RPG con barrido sutil, altar norte, flecha direccional del jugador y enemigos/jefe.

var player_ref: Node3D = null
var world_range: float = 28.0
var _sweep_angle: float = 0.0

func _process(delta: float) -> void:
	_sweep_angle = fmod(_sweep_angle + delta * 1.35, TAU)
	queue_redraw()

func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5 - 3.0
	if r <= 8.0:
		return

	# Deep midnight radar disc
	draw_circle(c, r, Color(0.03, 0.06, 0.14, 0.86))
	draw_arc(c, r, 0.0, TAU, 64, Color(0.38, 0.72, 1.0, 0.78), 2.2, true)
	draw_arc(c, r - 4.0, 0.0, TAU, 56, Color(0.98, 0.80, 0.32, 0.32), 1.2, true)

	# Concentric range rings & crosshairs
	draw_arc(c, r * 0.66, 0.0, TAU, 48, Color(0.35, 0.62, 0.92, 0.18), 1.0, true)
	draw_arc(c, r * 0.33, 0.0, TAU, 36, Color(0.35, 0.62, 0.92, 0.16), 1.0, true)
	draw_line(Vector2(c.x - r + 6, c.y), Vector2(c.x + r - 6, c.y), Color(0.4, 0.65, 0.95, 0.14), 1.0)
	draw_line(Vector2(c.x, c.y - r + 6), Vector2(c.x, c.y + r - 6), Color(0.4, 0.65, 0.95, 0.14), 1.0)

	# Subtle radar sweep line
	var sweep_end := c + Vector2(cos(_sweep_angle), sin(_sweep_angle)) * (r - 6.0)
	draw_line(c, sweep_end, Color(0.35, 0.85, 1.0, 0.24), 1.5, true)

	if player_ref == null or not is_instance_valid(player_ref) or not is_inside_tree():
		draw_circle(c, 4.0, Color(0.28, 0.85, 1.0, 1.0))
		return

	var usable_r := r - 12.0

	# Sacred Forge Altar marker (world 0, 0, -21.5)
	var altar_rel := Vector3(0.0, 0.0, -21.5) - player_ref.global_position
	var av := Vector2(altar_rel.x, altar_rel.z) / world_range * usable_r
	if av.length() > usable_r:
		av = av.normalized() * usable_r
	var ap := c + av
	var d_pts := PackedVector2Array([
		ap + Vector2(0, -4.5), ap + Vector2(4.5, 0),
		ap + Vector2(0, 4.5), ap + Vector2(-4.5, 0)
	])
	draw_colored_polygon(d_pts, Color(0.38, 0.82, 1.0, 0.75))

	# Enemies & Boss
	var enemies := get_tree().get_nodes_in_group("enemies")
	for e in enemies:
		if not is_instance_valid(e):
			continue
		if e.get("hp") != null and int(e.hp) <= 0:
			continue
		var rel: Vector3 = e.global_position - player_ref.global_position
		var v := Vector2(rel.x, rel.z) / world_range * usable_r
		if v.length() > usable_r:
			v = v.normalized() * usable_r
		var ep := c + v
		var is_b: bool = bool(e.get("is_boss"))
		if is_b:
			var pulse := 6.5 + sin(Time.get_ticks_msec() / 120.0) * 1.5
			draw_circle(ep, pulse + 2.5, Color(1.0, 0.2, 0.25, 0.35))
			var b_pts := PackedVector2Array([
				ep + Vector2(0, -pulse), ep + Vector2(pulse, 0),
				ep + Vector2(0, pulse), ep + Vector2(-pulse, 0)
			])
			draw_colored_polygon(b_pts, Color(1.0, 0.72, 0.18, 1.0))
			draw_circle(ep, 2.8, Color(0.95, 0.15, 0.2, 1.0))
		else:
			draw_circle(ep, 4.2, Color(0.1, 0.02, 0.04, 0.85))
			draw_circle(ep, 3.1, Color(0.96, 0.26, 0.34, 0.96))

	# Player directional chevron at center
	var yaw := player_ref.rotation.y
	var fwd := Vector2(sin(yaw), cos(yaw)).normalized()
	var side := Vector2(-fwd.y, fwd.x)
	var arrow := PackedVector2Array([
		c + fwd * 7.0,
		c - fwd * 4.5 + side * 4.8,
		c - fwd * 2.0,
		c - fwd * 4.5 - side * 4.8,
	])
	draw_colored_polygon(arrow, Color(0.32, 0.92, 1.0, 1.0))
	draw_circle(c, 2.0, Color.WHITE)

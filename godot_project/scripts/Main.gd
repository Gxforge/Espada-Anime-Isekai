extends Node3D

@export var monster_scene: PackedScene
@export var max_monsters: int = 7
@export var spawn_interval: float = 1.35

@onready var player: Player = $Player
@onready var camera: Camera3D = $Camera3D
@onready var monsters_root: Node3D = $Monsters
@onready var hud: CanvasLayer = $HUD

var spawn_timer: float = 0.0
var rng := RandomNumberGenerator.new()

var _save_timer: float = 0.0

func _ready() -> void:
	rng.randomize()
	if has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").load_game(player)
	# initial monsters
	for i in range(6):
		_spawn_monster(false)
	_wire_hud()

func _process(delta: float) -> void:
	_update_camera(delta)
	_handle_spawning(delta)
	_save_timer += delta
	if _save_timer >= 15.0:
		_save_timer = 0.0
		if has_node("/root/SaveSystem"):
			get_node("/root/SaveSystem").save_game(player)

func _update_camera(delta: float) -> void:
	if not is_instance_valid(player):
		return
	var target := Vector3(player.global_position.x, 13.2, player.global_position.z + 15.8)
	camera.global_position = camera.global_position.lerp(target, delta * 6.5)
	camera.look_at(Vector3(player.global_position.x, 1.0, player.global_position.z), Vector3.UP)

func _handle_spawning(delta: float) -> void:
	spawn_timer += delta
	var count := get_tree().get_nodes_in_group("enemies").size()
	if count < max_monsters and spawn_timer >= spawn_interval:
		spawn_timer = 0.0
		# boss on every 3rd wave start is handled by wave signal; normal spawn here
		_spawn_monster(false)

func _spawn_monster(force_boss: bool) -> void:
	var wave := player.wave
	if force_boss:
		for e in get_tree().get_nodes_in_group("enemies"):
			if is_instance_valid(e) and e.get("is_boss"):
				return
	var pool: Array = GameData.get_eligible_monsters(wave, force_boss)
	var def: Dictionary = pool[rng.randi_range(0, pool.size() - 1)]
	if force_boss:
		var bosses := GameData.get_eligible_monsters(wave, true)
		def = bosses[0]

	var m: Node3D
	if monster_scene:
		m = monster_scene.instantiate()
	else:
		m = _build_monster_node()
	monsters_root.add_child(m)
	m.add_to_group("enemies")
	var angle := rng.randf() * TAU
	var dist := rng.randf_range(12.0, 22.0)
	var pos := player.global_position + Vector3(sin(angle) * dist, 0, cos(angle) * dist)
	pos.x = clamp(pos.x, -23.0, 23.0)
	pos.z = clamp(pos.z, -23.0, 23.0)
	m.global_position = pos
	if m.has_method("setup"):
		m.setup(def, wave, player)

func _build_monster_node() -> CharacterBody3D:
	var m := CharacterBody3D.new()
	m.set_script(load("res://scripts/Monster.gd"))
	var holder := Node3D.new()
	holder.name = "ModelHolder"
	m.add_child(holder)
	var col := CollisionShape3D.new()
	var shape := CapsuleShape3D.new()
	shape.radius = 0.6
	shape.height = 1.8
	col.shape = shape
	col.position.y = 0.9
	m.add_child(col)
	return m

func _wire_hud() -> void:
	if hud and hud.has_method("connect_player"):
		hud.connect_player(player)
	# wave boss spawn
	player.wave_changed.connect(_on_wave_changed)

func _on_wave_changed(wave: int, _wk: int) -> void:
	if wave % 3 == 0:
		# avoid duplicate boss
		for e in get_tree().get_nodes_in_group("enemies"):
			if is_instance_valid(e) and e.get("is_boss"):
				return
		_spawn_monster(true)

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		if has_node("/root/SaveSystem") and is_instance_valid(player):
			get_node("/root/SaveSystem").save_game(player)
		get_tree().quit()

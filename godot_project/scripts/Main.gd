extends Node3D

@export var monster_scene: PackedScene
@export var max_monsters: int = 7
@export var spawn_interval: float = 1.35

@onready var player: Player = $Player
@onready var camera: Camera3D = $Camera3D
@onready var monsters_root: Node3D = $Monsters
@onready var hud: CanvasLayer = $HUD
@onready var arena_node: Node3D = get_node_or_null("Arena")

var spawn_timer: float = 0.0
var rng := RandomNumberGenerator.new()
var _save_timer: float = 0.0
var _music: AudioStreamPlayer
var arena_decor: Node3D
var _boss_music_active: bool = false

func _ready() -> void:
	rng.randomize()
	_setup_arena_decor()
	if has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").load_game(player)
	for i in range(6):
		_spawn_monster(false)
	_wire_hud()
	_play_music()
	# If loaded onto a boss wave (3, 6, 9...) with 0 wave_kills, spawn Malakor
	if player.wave % 3 == 0 and player.wave_kills == 0:
		_spawn_monster(true)

func _setup_arena_decor() -> void:
	if arena_node == null:
		return
	var DecorScript = load("res://scripts/ArenaDecor.gd")
	if DecorScript:
		arena_decor = DecorScript.new()
		arena_decor.name = "ArenaDecor"
		arena_node.add_child(arena_decor)
		if has_node("/root/SaveSystem"):
			var q := str(get_node("/root/SaveSystem").settings.get("quality", "medium"))
			arena_decor.apply_quality(q)

func _process(delta: float) -> void:
	_update_camera(delta)
	_handle_spawning(delta)
	_update_arena_and_music()
	_save_timer += delta
	if _save_timer >= 15.0:
		_save_timer = 0.0
		if has_node("/root/SaveSystem"):
			get_node("/root/SaveSystem").save_game(player)

func _update_arena_and_music() -> void:
	if arena_decor and is_instance_valid(arena_decor) and is_instance_valid(player):
		var t := Time.get_ticks_msec() / 1000.0
		var acol: Color = player.current_tier.get("aura_color", Color("#38bdf8"))
		arena_decor.update_decor(t, acol)

	var any_boss := false
	for e in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
			any_boss = true
			break
	if any_boss != _boss_music_active:
		_boss_music_active = any_boss
		var am := get_node_or_null("/root/AudioManager")
		if am:
			am.play_music("boss_theme" if any_boss else "ambient", 0.75)

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
		_spawn_monster(false)

func _spawn_monster(force_boss: bool) -> Node3D:
	var wave := player.wave
	if force_boss:
		for e in get_tree().get_nodes_in_group("enemies"):
			if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
				return null
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
	m.add_to_group("monsters")

	var angle := rng.randf() * TAU
	var dist := 13.5 if force_boss else rng.randf_range(12.0, 22.0)
	var pos := player.global_position + Vector3(sin(angle) * dist, 0, cos(angle) * dist)
	pos.x = clamp(pos.x, -22.5, 22.5)
	pos.z = clamp(pos.z, -22.5, 22.5)
	m.global_position = pos
	if m.has_method("setup"):
		m.setup(def, wave, player)
	if force_boss:
		if hud and hud.has_method("notify_boss_spawned"):
			hud.notify_boss_spawned(m)
		if m.has_signal("boss_defeated_reward") and hud and hud.has_method("notify_boss_defeated"):
			m.boss_defeated_reward.connect(hud.notify_boss_defeated)
	return m

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
	player.wave_changed.connect(_on_wave_changed)

func _on_wave_changed(wave: int, wk: int) -> void:
	if wave % 3 == 0 and wk == 0:
		for e in get_tree().get_nodes_in_group("enemies"):
			if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
				return
		_spawn_monster(true)

func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		if has_node("/root/SaveSystem") and is_instance_valid(player):
			get_node("/root/SaveSystem").save_game(player)
		get_tree().quit()

func _play_music() -> void:
	var am := get_node_or_null("/root/AudioManager")
	if am and am.has_method("play_music"):
		am.play_music("ambient", 0.65)
		return
	if not ResourceLoader.exists("res://assets/audio/ambient.wav"):
		return
	_music = AudioStreamPlayer.new()
	_music.name = "Music"
	var st = load("res://assets/audio/ambient.wav")
	if st is AudioStreamWAV:
		st.loop_mode = AudioStreamWAV.LOOP_FORWARD
		st.loop_end = int(st.data.size() / 2)
	_music.stream = st
	_music.volume_db = -10.0
	add_child(_music)
	_music.play()

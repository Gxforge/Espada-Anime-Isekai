extends CanvasLayer

@onready var hp_bar: ProgressBar = $Control/TopBar/HPBar
@onready var hp_label: Label = $Control/TopBar/HPLabel
@onready var xp_bar: ProgressBar = $Control/TopBar/XPBar
@onready var xp_label: Label = $Control/TopBar/XPLabel
@onready var level_label: Label = $Control/TopBar/LevelLabel
@onready var sword_name_label: Label = $Control/TopBar/SwordNameLabel
@onready var gold_label: Label = $Control/TopBar/GoldLabel
@onready var kills_label: Label = $Control/TopBar/KillsLabel
@onready var wave_label: Label = $Control/TopBar/WaveLabel
@onready var log_label: RichTextLabel = $Control/LogPanel/LogLabel
@onready var evo_banner: Panel = $Control/EvoBanner
@onready var evo_banner_label: Label = $Control/EvoBanner/EvoLabel

var player: Player
var log_lines: Array[String] = []
var boss_panel: Panel
var boss_bar: ProgressBar
var boss_label: Label
var game_over_panel: Panel
var game_over_label: Label

func _ready() -> void:
	_style_ui()
	_build_extra_ui()

func _style_ui() -> void:
	var top: Panel = $Control/TopBar
	var log_panel: Panel = $Control/LogPanel
	var forge: Panel = $Control/ForgePanel
	var evo: Panel = $Control/EvoBanner

	_apply_panel_style(top, Color(0.05, 0.07, 0.12, 0.55), Color(0.3, 0.7, 1.0, 0.18), 0)
	_apply_panel_style(log_panel, Color(0.04, 0.05, 0.09, 0.38), Color(1,1,1,0.06), 10)
	_apply_panel_style(forge, Color(0.04, 0.05, 0.09, 0.42), Color(1,1,1,0.08), 10)
	_apply_panel_style(evo, Color(0.12, 0.08, 0.02, 0.72), Color(1.0, 0.75, 0.2, 0.45), 12)

	_style_bar(hp_bar, Color(0.12, 0.02, 0.04, 0.85), Color(0.9, 0.18, 0.25, 0.95), Color(1.0, 0.45, 0.35, 0.95))
	_style_bar(xp_bar, Color(0.02, 0.06, 0.12, 0.85), Color(0.2, 0.65, 1.0, 0.95), Color(0.55, 0.9, 1.0, 0.95))

	for lbl in [level_label, sword_name_label, xp_label, hp_label, gold_label, kills_label, wave_label]:
		if lbl:
			lbl.add_theme_color_override("font_color", Color(0.93, 0.95, 1.0, 0.95))
			lbl.add_theme_color_override("font_outline_color", Color(0,0,0,0.7))
			lbl.add_theme_constant_override("outline_size", 3)

	level_label.add_theme_font_size_override("font_size", 24)
	level_label.add_theme_color_override("font_color", Color(1.0, 0.92, 0.55, 1.0))
	sword_name_label.add_theme_font_size_override("font_size", 14)
	sword_name_label.add_theme_color_override("font_color", Color(0.78, 0.86, 1.0, 0.9))
	xp_label.add_theme_font_size_override("font_size", 12)
	hp_label.add_theme_font_size_override("font_size", 12)
	gold_label.add_theme_font_size_override("font_size", 14)
	gold_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.35, 1.0))
	kills_label.add_theme_font_size_override("font_size", 13)
	wave_label.add_theme_font_size_override("font_size", 13)

	log_label.add_theme_font_size_override("normal_font_size", 12)
	log_label.add_theme_color_override("default_color", Color(0.85, 0.9, 1.0, 0.82))

	evo_banner_label.add_theme_font_size_override("font_size", 28)
	evo_banner_label.add_theme_color_override("font_color", Color(1.0, 0.93, 0.65, 1.0))
	evo_banner_label.add_theme_color_override("font_outline_color", Color(0,0,0,0.8))
	evo_banner_label.add_theme_constant_override("outline_size", 4)

	# Style buttons
	for b in _all_buttons():
		_style_button(b)

func _all_buttons() -> Array[Button]:
	var arr: Array[Button] = []
	var root := $Control
	for n in [root.get_node_or_null("TopBar/AutoHuntBtn"), root.get_node_or_null("TopBar/ModeBtn"), root.get_node_or_null("TopBar/LevelUpBtn"),
		root.get_node_or_null("ForgePanel/SharpBtn"), root.get_node_or_null("ForgePanel/SwiftBtn"), root.get_node_or_null("ForgePanel/CritBtn"),
		root.get_node_or_null("ForgePanel/VampBtn"), root.get_node_or_null("ForgePanel/SoulBtn"), root.get_node_or_null("ForgePanel/SizeBtn")]:
		if n is Button:
			arr.append(n)
	return arr

func _style_button(b: Button) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.12, 0.16, 0.24, 0.72)
	normal.border_color = Color(0.45, 0.65, 0.95, 0.25)
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(6)
	normal.content_margin_left = 8; normal.content_margin_right = 8
	normal.content_margin_top = 4; normal.content_margin_bottom = 4
	var hover := normal.duplicate()
	hover.bg_color = Color(0.2, 0.28, 0.42, 0.85)
	hover.border_color = Color(0.6, 0.8, 1.0, 0.45)
	var pressed := normal.duplicate()
	pressed.bg_color = Color(0.08, 0.12, 0.18, 0.9)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("focus", hover)
	b.add_theme_color_override("font_color", Color(0.92, 0.95, 1.0, 0.95))
	b.add_theme_font_size_override("font_size", 12)

func _apply_panel_style(p: Panel, bg: Color, border: Color, radius: int) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(1 if radius > 0 else 0)
	if radius > 0:
		sb.set_corner_radius_all(radius)
	p.add_theme_stylebox_override("panel", sb)

func _style_bar(bar: ProgressBar, bg: Color, fill_a: Color, fill_b: Color) -> void:
	var bg_sb := StyleBoxFlat.new()
	bg_sb.bg_color = bg
	bg_sb.set_corner_radius_all(5)
	bg_sb.set_border_width_all(1)
	bg_sb.border_color = Color(1,1,1,0.08)
	var fill_sb := StyleBoxFlat.new()
	fill_sb.bg_color = fill_a
	fill_sb.border_color = fill_b
	fill_sb.set_border_width_all(1)
	fill_sb.set_corner_radius_all(5)
	# subtle gradient via shadow not available; use border highlight
	bar.add_theme_stylebox_override("background", bg_sb)
	bar.add_theme_stylebox_override("fill", fill_sb)
	bar.show_percentage = false

func connect_player(p: Player) -> void:
	player = p
	player.hp_changed.connect(_on_hp)
	player.xp_changed.connect(_on_xp)
	player.gold_changed.connect(_on_gold)
	player.kills_changed.connect(_on_kills)
	player.wave_changed.connect(_on_wave)
	player.evolution_changed.connect(_on_evo)
	player.log_added.connect(_on_log)
	if player.has_signal("player_died"):
		player.player_died.connect(_on_player_died)
	_on_hp(player.player_hp, player.player_max_hp)
	_on_xp(player.current_xp, GameData.get_xp_required(player.sword_level), player.sword_level)
	_on_gold(player.gold)
	_on_kills(player.kills)
	_on_wave(player.wave, player.wave_kills)
	evo_banner.visible = false
	if boss_panel: boss_panel.visible = false
	if game_over_panel: game_over_panel.visible = false

func _on_hp(cur: int, max_hp: int) -> void:
	hp_bar.max_value = max_hp
	hp_bar.value = cur
	hp_label.text = "%d / %d" % [cur, max_hp]
	# dynamic color: green->yellow->red
	var ratio := float(cur) / float(maxi(1, max_hp))
	var fill: StyleBoxFlat = hp_bar.get_theme_stylebox("fill")
	if fill:
		if ratio > 0.5:
			fill.bg_color = Color(0.18, 0.78, 0.32, 0.95).lerp(Color(0.95, 0.75, 0.2, 0.95), (1.0 - ratio) * 2.0)
		else:
			fill.bg_color = Color(0.95, 0.75, 0.2, 0.95).lerp(Color(0.9, 0.18, 0.25, 0.95), (0.5 - ratio) * 2.0)

func _on_xp(cur: int, req: int, level: int) -> void:
	xp_bar.max_value = req
	xp_bar.value = cur
	xp_label.text = "EXP %d/%d" % [cur, req]
	level_label.text = "Nv.%d" % level
	var tier = GameData.get_sword_for_level(level)
	sword_name_label.text = str(tier["name"])

func _on_gold(g: int) -> void:
	gold_label.text = "Oro %d" % g

func _on_kills(k: int) -> void:
	kills_label.text = "K %d" % k

func _on_wave(w: int, wk: int) -> void:
	wave_label.text = "Oleada %d  %d/8" % [w, wk]

func _on_evo(tier: Dictionary) -> void:
	evo_banner.visible = true
	evo_banner.modulate.a = 1.0
	evo_banner_label.text = "¡EVOLUCIÓN!  %s" % str(tier["name"])
	var tw := create_tween()
	tw.tween_interval(3.2)
	tw.tween_property(evo_banner, "modulate:a", 0.0, 0.5)
	tw.tween_callback(func(): evo_banner.visible = false; evo_banner.modulate.a = 1.0)

func _on_log(text: String, kind: String) -> void:
	var prefix := ""
	match kind:
		"evolution": prefix = "[EVO] "
		"skill": prefix = "[SKILL] "
		"upgrade": prefix = "[FORJA] "
		"boss": prefix = "[!] "
		"levelup": prefix = "[UP] "
	log_lines.push_front(prefix + text)
	if log_lines.size() > 5:
		log_lines.resize(5)
	log_label.text = "\n".join(log_lines)

func _on_auto_hunt_pressed() -> void:
	if player: player.toggle_auto_hunt()
func _on_mode_pressed() -> void:
	if player: player.toggle_wielder_mode()
func _on_level_up_pressed() -> void:
	if player: player.jump_to_level(player.sword_level + 1)
func _on_upgrade_sharpness_pressed() -> void:
	if player: player.buy_upgrade("sharpness", 25)
func _on_upgrade_swiftness_pressed() -> void:
	if player: player.buy_upgrade("swiftness", 30)
func _on_upgrade_crit_pressed() -> void:
	if player: player.buy_upgrade("criticalMastery", 35)
func _on_upgrade_vamp_pressed() -> void:
	if player: player.buy_upgrade("vampirism", 40)
func _on_upgrade_soul_pressed() -> void:
	if player: player.buy_upgrade("soulMagnet", 30)
func _on_upgrade_size_pressed() -> void:
	if player: player.buy_upgrade("bladeSize", 45)

func _build_extra_ui() -> void:
	var control := $Control
	# Boss HP
	boss_panel = Panel.new()
	boss_panel.name = "BossPanel"
	boss_panel.visible = false
	boss_panel.anchor_left = 0.5; boss_panel.anchor_right = 0.5
	boss_panel.offset_left = -260; boss_panel.offset_right = 260
	boss_panel.offset_top = 78; boss_panel.offset_bottom = 118
	var bsb := StyleBoxFlat.new()
	bsb.bg_color = Color(0.08,0.02,0.02,0.7)
	bsb.border_color = Color(1.0,0.3,0.2,0.5)
	bsb.set_border_width_all(1)
	bsb.set_corner_radius_all(8)
	boss_panel.add_theme_stylebox_override("panel", bsb)
	control.add_child(boss_panel)

	boss_label = Label.new()
	boss_label.text = "BOSS"
	boss_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_label.offset_left = 0; boss_label.offset_right = 520
	boss_label.offset_top = 2; boss_label.offset_bottom = 20
	boss_label.add_theme_font_size_override("font_size", 13)
	boss_label.add_theme_color_override("font_color", Color(1.0,0.75,0.75,1.0))
	boss_panel.add_child(boss_label)

	boss_bar = ProgressBar.new()
	boss_bar.show_percentage = false
	boss_bar.offset_left = 16; boss_bar.offset_right = 504
	boss_bar.offset_top = 22; boss_bar.offset_bottom = 34
	var bg := StyleBoxFlat.new(); bg.bg_color = Color(0.15,0.05,0.05,0.9); bg.set_corner_radius_all(4)
	var fill := StyleBoxFlat.new(); fill.bg_color = Color(0.9,0.15,0.2,0.95); fill.set_corner_radius_all(4)
	boss_bar.add_theme_stylebox_override("background", bg)
	boss_bar.add_theme_stylebox_override("fill", fill)
	boss_panel.add_child(boss_bar)

	# Game Over
	game_over_panel = Panel.new()
	game_over_panel.name = "GameOverPanel"
	game_over_panel.visible = false
	game_over_panel.anchor_left = 0.5; game_over_panel.anchor_right = 0.5
	game_over_panel.anchor_top = 0.5; game_over_panel.anchor_bottom = 0.5
	game_over_panel.offset_left = -220; game_over_panel.offset_right = 220
	game_over_panel.offset_top = -80; game_over_panel.offset_bottom = 80
	var gsb := StyleBoxFlat.new()
	gsb.bg_color = Color(0.03,0.03,0.06,0.88)
	gsb.border_color = Color(1.0,0.4,0.3,0.5)
	gsb.set_border_width_all(1)
	gsb.set_corner_radius_all(12)
	game_over_panel.add_theme_stylebox_override("panel", gsb)
	control.add_child(game_over_panel)

	game_over_label = Label.new()
	game_over_label.text = "HAS CAÍDO\nLa Forja te restaura..."
	game_over_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	game_over_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	game_over_label.anchor_right = 1.0; game_over_label.anchor_bottom = 1.0
	game_over_label.offset_bottom = -40
	game_over_label.add_theme_font_size_override("font_size", 24)
	game_over_label.add_theme_color_override("font_color", Color(1.0,0.85,0.8,1.0))
	game_over_panel.add_child(game_over_label)

	var respawn_btn := Button.new()
	respawn_btn.text = "Reaparecer"
	respawn_btn.anchor_left = 0.5; respawn_btn.anchor_right = 0.5
	respawn_btn.offset_left = -70; respawn_btn.offset_right = 70
	respawn_btn.offset_top = 110; respawn_btn.offset_bottom = 142
	_style_button(respawn_btn)
	respawn_btn.pressed.connect(_on_respawn_pressed)
	game_over_panel.add_child(respawn_btn)

func _process(_delta: float) -> void:
	_update_boss_bar()

func _update_boss_bar() -> void:
	if boss_panel == null:
		return
	var boss: Node3D = null
	for e in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
			boss = e
			break
	if boss:
		boss_panel.visible = true
		boss_bar.max_value = int(boss.get("max_hp"))
		boss_bar.value = int(boss.get("hp"))
		var bname = str(boss.def.get("name", "BOSS")) if boss.get("def") != null else "BOSS"
		boss_label.text = bname
	else:
		boss_panel.visible = false

func _on_player_died() -> void:
	if game_over_panel:
		game_over_panel.visible = true

func _on_respawn_pressed() -> void:
	if player and player.has_method("respawn_player"):
		player.respawn_player()
	if game_over_panel:
		game_over_panel.visible = false

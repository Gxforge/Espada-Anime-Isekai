extends CanvasLayer

# Legacy optional refs kept for scene compatibility
@onready var hp_bar: ProgressBar = get_node_or_null("Control/TopBar/HPBar")
@onready var hp_label: Label = get_node_or_null("Control/TopBar/HPLabel")
@onready var xp_bar: ProgressBar = get_node_or_null("Control/TopBar/XPBar")
@onready var xp_label: Label = get_node_or_null("Control/TopBar/XPLabel")
@onready var level_label: Label = get_node_or_null("Control/TopBar/LevelLabel")
@onready var sword_name_label: Label = get_node_or_null("Control/TopBar/SwordNameLabel")
@onready var gold_label: Label = get_node_or_null("Control/TopBar/GoldLabel")
@onready var kills_label: Label = get_node_or_null("Control/TopBar/KillsLabel")
@onready var wave_label: Label = get_node_or_null("Control/TopBar/WaveLabel")
@onready var log_label: RichTextLabel = get_node_or_null("Control/LogPanel/LogLabel")
@onready var evo_banner: Panel = get_node_or_null("Control/EvoBanner")
@onready var evo_banner_label: Label = get_node_or_null("Control/EvoBanner/EvoLabel")

var player: Player
var log_lines: Array[String] = []

# Primary HUD containers (exposed for automated layout/regression tests)
var ui_root: Control
var top_left_panel: Panel
var portrait_ring: Panel
var top_center_panel: Panel
var top_right_bar: HBoxContainer
var quick_pills_bar: HBoxContainer
var objective_panel: Panel
var forge_panel: Panel
var bottom_skills_panel: Panel
var log_panel_box: Panel
var minimap_panel: Panel
var minimap_radar: Control
var branding_label: Label

# Dynamic labels & bars
var hp_bar_new: ProgressBar
var hp_text: Label
var xp_bar_new: ProgressBar
var xp_text: Label
var lvl_text: Label
var sword_text: Label
var subtitle_text: Label
var gold_text: Label
var kills_top_text: Label
var wave_text: Label
var objective_title: Label
var objective_sub: Label
var objective_text: Label
var objective_bar: ProgressBar

# Quick pills
var auto_btn: Button
var mode_btn: Button
var potion_btn: Button

# Boss UI & Ceremonial Banner
var boss_panel: Panel
var boss_bar: ProgressBar
var boss_label: Label
var boss_hp_label: Label
var alert_banner: Panel
var alert_title: Label
var alert_sub: Label
var _alert_timer: float = 0.0

# Overlays
var modal_backdrop: ColorRect
var game_over_panel: Panel
var game_over_summary: Label
var pause_panel: Panel
var settings_panel: Panel
var inventory_panel: Panel
var stats_panel: Panel
var evolution_panel: Panel
var skill_panel: Panel
var evolution_list_vb: VBoxContainer
var skill_list_vb: VBoxContainer
var evo_era_filter: int = 0
var skill_tree_filter: String = ""
var evo_pill_btn: Button
var skills_pill_btn: Button
var evo_nav_column: VBoxContainer
var stats_label: RichTextLabel
var codex_label: RichTextLabel
var inventory_label: RichTextLabel
var inv_left_box: VBoxContainer
var inv_right_box: VBoxContainer

# Settings widgets
var _quality_btns: Dictionary = {}
var _master_slider: HSlider
var _music_slider: HSlider
var _sfx_slider: HSlider
var _master_val_lbl: Label
var _music_val_lbl: Label
var _sfx_val_lbl: Label
var _mute_btn: Button
var _audio_muted: bool = false

# Skills, Forge, Combo & Floating Numbers
var cd_nodes: Dictionary = {}
var forge_buttons: Dictionary = {}
var combo_label: Label
var combo_timer: float = 0.0
var combo_count: int = 0
var floating_layer: Control
var _floating_items: Array[Dictionary] = []

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	ui_root = get_node_or_null("Control")
	if ui_root == null:
		ui_root = Control.new()
		ui_root.name = "Control"
		ui_root.set_anchors_preset(Control.PRESET_FULL_RECT)
		add_child(ui_root)
	_clear_legacy_children()
	_build_ui()
	ui_root.resized.connect(_layout_responsive)
	_load_settings()
	call_deferred("_layout_responsive")

func _clear_legacy_children() -> void:
	for c in ui_root.get_children():
		ui_root.remove_child(c)
		c.queue_free()

func _build_ui() -> void:
	floating_layer = Control.new()
	floating_layer.name = "FloatingLayer"
	floating_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	floating_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_root.add_child(floating_layer)

	_build_top_left()
	_build_quick_pills()
	_build_top_center()
	_build_top_right()
	_build_objective()
	_build_minimap()
	_build_right_forge()
	_build_bottom_skills()
	_build_log()
	_build_branding()
	_build_boss_bar()
	_build_alert_banner()
	_build_combo()

	# Backdrop behind modal overlays
	modal_backdrop = ColorRect.new()
	modal_backdrop.name = "ModalBackdrop"
	modal_backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	modal_backdrop.color = Color(0.01, 0.02, 0.06, 0.58)
	modal_backdrop.visible = false
	ui_root.add_child(modal_backdrop)

	_build_settings_panel()
	_build_inventory_panel()
	_build_stats_panel()
	_build_evolution_panel()
	_build_skill_panel()
	_build_pause()
	_build_game_over()

func _panel_style(bg: Color, border: Color, radius: int = 12, border_w: int = 1, shadow_size: int = 0) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	if shadow_size > 0:
		sb.shadow_color = Color(0, 0, 0, 0.42)
		sb.shadow_size = shadow_size
	return sb

func _label(parent: Node, text: String, pos: Vector2, sz: Vector2, fs: int = 14, color: Color = Color.WHITE, align: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = sz
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.01, 0.02, 0.06, 0.88))
	l.add_theme_constant_override("outline_size", 3)
	parent.add_child(l)
	return l

func _style_button(b: Button, accent: Color = Color(0.38, 0.68, 1.0, 0.42), bg_alpha: float = 0.86, fs: int = 12) -> void:
	var normal := _panel_style(Color(0.08, 0.12, 0.22, bg_alpha), accent, 9, 1)
	var hover := _panel_style(Color(0.15, 0.23, 0.38, 0.95), Color(accent.r, accent.g, accent.b, 0.88), 9, 1)
	var pressed := _panel_style(Color(0.05, 0.08, 0.15, 0.95), accent, 9, 1)
	var disabled := _panel_style(Color(0.06, 0.07, 0.11, 0.62), Color(0.3, 0.34, 0.42, 0.22), 9, 1)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("focus", hover)
	b.add_theme_stylebox_override("disabled", disabled)
	b.add_theme_color_override("font_color", Color(0.94, 0.97, 1.0))
	b.add_theme_color_override("font_hover_color", Color(1.0, 0.96, 0.78))
	b.add_theme_color_override("font_disabled_color", Color(0.46, 0.50, 0.58))
	b.add_theme_font_size_override("font_size", fs)

func _play_ui_click() -> void:
	var am := get_node_or_null("/root/AudioManager")
	if am and am.has_method("play_sfx"):
		am.play_sfx("ui")
	elif player and player.has_method("play_sfx"):
		player.play_sfx("ui")

# --- TOP LEFT: Portrait, Sword Evolution, HP & Soul EXP ---
func _build_top_left() -> void:
	top_left_panel = Panel.new()
	top_left_panel.name = "TopLeftPanel"
	top_left_panel.position = Vector2(16, 12)
	top_left_panel.size = Vector2(456, 112)
	top_left_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.04, 0.07, 0.16, 0.86), Color(0.38, 0.72, 1.0, 0.58), 16, 2, 6)
	)
	ui_root.add_child(top_left_panel)

	portrait_ring = Panel.new()
	portrait_ring.position = Vector2(12, 14)
	portrait_ring.size = Vector2(84, 84)
	portrait_ring.clip_children = CanvasItem.CLIP_CHILDREN_AND_DRAW
	portrait_ring.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.08, 0.14, 0.28, 0.96), Color(0.45, 0.86, 1.0, 0.95), 42, 3)
	)
	top_left_panel.add_child(portrait_ring)

	var portrait_tex := TextureRect.new()
	portrait_tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait_tex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	portrait_tex.texture = load("res://assets/ui/portrait.png")
	portrait_ring.add_child(portrait_tex)
	portrait_tex.set_anchors_preset(Control.PRESET_FULL_RECT)
	portrait_tex.offset_left = 3.0
	portrait_tex.offset_top = 3.0
	portrait_tex.offset_right = -3.0
	portrait_tex.offset_bottom = -3.0

	var lvl_badge := Panel.new()
	lvl_badge.position = Vector2(106, 10)
	lvl_badge.size = Vector2(66, 24)
	lvl_badge.add_theme_stylebox_override("panel", _panel_style(Color(0.18, 0.13, 0.04, 0.95), Color(0.98, 0.78, 0.25, 0.85), 8, 1))
	top_left_panel.add_child(lvl_badge)
	lvl_text = _label(lvl_badge, "Nv. 1", Vector2(0, 0), Vector2(66, 24), 14, Color(1.0, 0.90, 0.42), HORIZONTAL_ALIGNMENT_CENTER)

	sword_text = _label(top_left_panel, "Espada de Madera Ancestral", Vector2(178, 9), Vector2(266, 24), 14, Color(0.96, 0.98, 1.0))
	sword_text.clip_text = true
	sword_text.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS

	subtitle_text = _label(top_left_panel, "Fase I • Próx. Evolución: Nv. 5", Vector2(106, 33), Vector2(338, 18), 11, Color(0.68, 0.86, 1.0, 0.92))

	_label(top_left_panel, "❤", Vector2(106, 54), Vector2(20, 20), 13, Color(0.32, 0.96, 0.52))
	hp_bar_new = ProgressBar.new()
	hp_bar_new.position = Vector2(126, 57)
	hp_bar_new.size = Vector2(218, 15)
	hp_bar_new.show_percentage = false
	hp_bar_new.add_theme_stylebox_override("background", _panel_style(Color(0.10, 0.05, 0.08, 0.94), Color(1, 1, 1, 0.14), 7))
	hp_bar_new.add_theme_stylebox_override("fill", _panel_style(Color(0.20, 0.88, 0.42, 0.96), Color(0.65, 1, 0.72, 0.45), 7))
	top_left_panel.add_child(hp_bar_new)
	hp_text = _label(top_left_panel, "220 / 220", Vector2(348, 54), Vector2(96, 20), 12, Color(0.92, 1.0, 0.94), HORIZONTAL_ALIGNMENT_RIGHT)

	_label(top_left_panel, "EXP", Vector2(106, 79), Vector2(30, 18), 11, Color(0.55, 0.84, 1.0))
	xp_bar_new = ProgressBar.new()
	xp_bar_new.position = Vector2(138, 82)
	xp_bar_new.size = Vector2(206, 12)
	xp_bar_new.show_percentage = false
	xp_bar_new.add_theme_stylebox_override("background", _panel_style(Color(0.05, 0.08, 0.16, 0.94), Color(1, 1, 1, 0.12), 6))
	xp_bar_new.add_theme_stylebox_override("fill", _panel_style(Color(0.22, 0.68, 1.0, 0.96), Color(0.62, 0.92, 1.0, 0.45), 6))
	top_left_panel.add_child(xp_bar_new)
	xp_text = _label(top_left_panel, "0/35 (0%)", Vector2(348, 78), Vector2(96, 18), 11, Color(0.84, 0.93, 1.0), HORIZONTAL_ALIGNMENT_RIGHT)

func _build_quick_pills() -> void:
	quick_pills_bar = HBoxContainer.new()
	quick_pills_bar.name = "QuickPillsBar"
	quick_pills_bar.position = Vector2(16, 130)
	quick_pills_bar.size = Vector2(456, 30)
	quick_pills_bar.add_theme_constant_override("separation", 6)
	ui_root.add_child(quick_pills_bar)

	auto_btn = Button.new()
	auto_btn.text = "Auto-Caza: OFF"
	auto_btn.custom_minimum_size = Vector2(142, 28)
	_style_button(auto_btn, Color(0.32, 0.78, 1.0, 0.45), 0.84, 11)
	auto_btn.pressed.connect(func():
		if player:
			player.toggle_auto_hunt()
			_refresh_quick_pills()
	)
	quick_pills_bar.add_child(auto_btn)

	mode_btn = Button.new()
	mode_btn.text = "Modo: Espada Viva"
	mode_btn.custom_minimum_size = Vector2(154, 28)
	_style_button(mode_btn, Color(0.98, 0.78, 0.30, 0.45), 0.84, 11)
	mode_btn.pressed.connect(func():
		if player:
			player.toggle_wielder_mode()
			_refresh_quick_pills()
	)
	quick_pills_bar.add_child(mode_btn)

	potion_btn = Button.new()
	potion_btn.text = "Poción [H]: 2"
	potion_btn.custom_minimum_size = Vector2(142, 28)
	_style_button(potion_btn, Color(0.98, 0.42, 0.52, 0.52), 0.84, 11)
	potion_btn.pressed.connect(func():
		if player:
			player.use_consumable("potion_hp")
			_refresh_quick_pills()
	)
	quick_pills_bar.add_child(potion_btn)

	# Evolution & Skill Tree access column (right of the objective panel, no overlaps)
	evo_nav_column = VBoxContainer.new()
	evo_nav_column.name = "EvoNavColumn"
	evo_nav_column.position = Vector2(300, 164)
	evo_nav_column.size = Vector2(160, 60)
	evo_nav_column.add_theme_constant_override("separation", 6)
	ui_root.add_child(evo_nav_column)

	evo_pill_btn = Button.new()
	evo_pill_btn.text = "✦ Evolución [T]"
	evo_pill_btn.custom_minimum_size = Vector2(160, 26)
	_style_button(evo_pill_btn, Color(0.98, 0.78, 0.30, 0.55), 0.9, 11)
	evo_pill_btn.pressed.connect(_toggle_evolution)
	evo_nav_column.add_child(evo_pill_btn)

	skills_pill_btn = Button.new()
	skills_pill_btn.text = "❖ Habilidades [K]"
	skills_pill_btn.custom_minimum_size = Vector2(160, 26)
	_style_button(skills_pill_btn, Color(0.45, 0.85, 1.0, 0.55), 0.9, 11)
	skills_pill_btn.pressed.connect(_toggle_skill_tree)
	evo_nav_column.add_child(skills_pill_btn)

# --- TOP CENTER: Gold, Kills & Wave Status ---
func _build_top_center() -> void:
	top_center_panel = Panel.new()
	top_center_panel.name = "TopCenterPanel"
	top_center_panel.size = Vector2(336, 42)
	top_center_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.05, 0.08, 0.17, 0.84), Color(0.98, 0.78, 0.28, 0.45), 13, 1, 4)
	)
	ui_root.add_child(top_center_panel)

	gold_text = _label(top_center_panel, "★ 60 Oro", Vector2(12, 5), Vector2(104, 32), 14, Color(1.0, 0.86, 0.34))
	kills_top_text = _label(top_center_panel, "✦ 0 Bajas", Vector2(118, 5), Vector2(96, 32), 13, Color(0.88, 0.94, 1.0), HORIZONTAL_ALIGNMENT_CENTER)
	wave_text = _label(top_center_panel, "☠ Oleada 1", Vector2(214, 5), Vector2(110, 32), 14, Color(1.0, 0.76, 0.42), HORIZONTAL_ALIGNMENT_RIGHT)

# --- TOP RIGHT: Navigation Buttons ---
func _build_top_right() -> void:
	top_right_bar = HBoxContainer.new()
	top_right_bar.name = "TopRightBar"
	top_right_bar.size = Vector2(424, 38)
	top_right_bar.alignment = BoxContainer.ALIGNMENT_END
	top_right_bar.add_theme_constant_override("separation", 6)
	ui_root.add_child(top_right_bar)

	var defs := [
		["Ajustes", _toggle_settings],
		["Pausa", _toggle_pause],
		["Inventario", _toggle_inventory],
		["Estadísticas", _toggle_stats],
	]
	for d in defs:
		var b := Button.new()
		b.name = str(d[0]) + "Btn"
		b.text = str(d[0])
		b.custom_minimum_size = Vector2(100, 36)
		_style_button(b, Color(0.42, 0.72, 1.0, 0.48), 0.86, 12)
		b.pressed.connect(d[1])
		top_right_bar.add_child(b)

# --- OBJECTIVE CARD ---
func _build_objective() -> void:
	objective_panel = Panel.new()
	objective_panel.name = "ObjectivePanel"
	objective_panel.position = Vector2(16, 168)
	objective_panel.size = Vector2(276, 94)
	objective_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.04, 0.07, 0.15, 0.78), Color(1.0, 0.76, 0.24, 0.42), 12, 1)
	)
	ui_root.add_child(objective_panel)

	var stripe := ColorRect.new()
	stripe.position = Vector2(0, 10)
	stripe.size = Vector2(4, 74)
	stripe.color = Color(1.0, 0.78, 0.22, 0.92)
	objective_panel.add_child(stripe)

	objective_title = _label(objective_panel, "⚠ OBJETIVO DE OLEADA", Vector2(14, 7), Vector2(250, 20), 12, Color(1.0, 0.84, 0.36))
	objective_sub = _label(objective_panel, "Elimina 8 monstruos para avanzar\na la siguiente oleada.", Vector2(14, 28), Vector2(250, 34), 11, Color(0.86, 0.91, 0.99, 0.92))

	objective_bar = ProgressBar.new()
	objective_bar.position = Vector2(14, 69)
	objective_bar.size = Vector2(182, 12)
	objective_bar.max_value = 8
	objective_bar.value = 0
	objective_bar.show_percentage = false
	objective_bar.add_theme_stylebox_override("background", _panel_style(Color(0.06, 0.09, 0.16, 0.94), Color(1, 1, 1, 0.1), 6))
	objective_bar.add_theme_stylebox_override("fill", _panel_style(Color(0.98, 0.74, 0.22, 0.96), Color(1, 0.9, 0.5, 0.4), 6))
	objective_panel.add_child(objective_bar)

	objective_text = _label(objective_panel, "0 / 8", Vector2(202, 64), Vector2(62, 20), 14, Color(1.0, 0.90, 0.46), HORIZONTAL_ALIGNMENT_RIGHT)

# --- CIRCULAR RADAR MINIMAP ---
func _build_minimap() -> void:
	minimap_panel = Panel.new()
	minimap_panel.name = "Minimap"
	minimap_panel.size = Vector2(152, 152)
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0, 0, 0, 0)
	minimap_panel.add_theme_stylebox_override("panel", st)
	minimap_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_root.add_child(minimap_panel)

	var RadarScript = load("res://scripts/MinimapRadar.gd")
	minimap_radar = RadarScript.new()
	minimap_radar.name = "RadarCanvas"
	minimap_radar.set_anchors_preset(Control.PRESET_FULL_RECT)
	minimap_radar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	minimap_panel.add_child(minimap_radar)

	_label(minimap_panel, "N", Vector2(66, 2), Vector2(20, 16), 11, Color(0.98, 0.88, 0.45), HORIZONTAL_ALIGNMENT_CENTER)
	_label(minimap_panel, "S", Vector2(66, 134), Vector2(20, 16), 10, Color(0.70, 0.82, 0.96, 0.8), HORIZONTAL_ALIGNMENT_CENTER)
	_label(minimap_panel, "O", Vector2(4, 68), Vector2(16, 16), 10, Color(0.70, 0.82, 0.96, 0.8), HORIZONTAL_ALIGNMENT_CENTER)
	_label(minimap_panel, "E", Vector2(132, 68), Vector2(16, 16), 10, Color(0.70, 0.82, 0.96, 0.8), HORIZONTAL_ALIGNMENT_CENTER)

# --- RIGHT FORGE PANEL ---
func _build_right_forge() -> void:
	forge_panel = Panel.new()
	forge_panel.name = "ForgePanel"
	forge_panel.size = Vector2(236, 306)
	forge_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.04, 0.07, 0.15, 0.84), Color(0.98, 0.76, 0.28, 0.42), 14, 1, 5)
	)
	ui_root.add_child(forge_panel)

	_label(forge_panel, "⚒ FORJA DE ALMAS", Vector2(12, 8), Vector2(212, 22), 14, Color(1.0, 0.86, 0.38))

	var upgrades := [
		["sharpness", "Afilar", 25],
		["swiftness", "Ligereza", 30],
		["criticalMastery", "Crítico", 35],
		["vampirism", "Vampiro", 40],
		["soulMagnet", "Almas", 30],
		["bladeSize", "Colosal", 45],
	]
	var y := 35
	for u in upgrades:
		var btn := Button.new()
		btn.position = Vector2(10, y)
		btn.size = Vector2(216, 34)
		btn.text = "%s  Nv.0/10  •  %dg" % [u[1], u[2]]
		_style_button(btn, Color(0.42, 0.68, 0.98, 0.36), 0.88, 12)
		var key: String = str(u[0])
		var base := int(u[2])
		btn.pressed.connect(func(): _on_upgrade_pressed(key, base))
		forge_panel.add_child(btn)
		forge_buttons[key] = btn
		y += 37

	var mejorar := Button.new()
	mejorar.name = "MejorarBtn"
	mejorar.position = Vector2(10, 260)
	mejorar.size = Vector2(216, 36)
	mejorar.text = "⚡ Mejorar Óptimo"
	var mnormal := _panel_style(Color(0.16, 0.50, 0.92, 0.96), Color(0.55, 0.88, 1.0, 0.92), 10, 1)
	var mhover := _panel_style(Color(0.24, 0.60, 1.0, 0.99), Color(0.82, 0.96, 1.0, 1.0), 10, 1)
	mejorar.add_theme_stylebox_override("normal", mnormal)
	mejorar.add_theme_stylebox_override("hover", mhover)
	mejorar.add_theme_stylebox_override("pressed", mnormal)
	mejorar.add_theme_stylebox_override("focus", mhover)
	mejorar.add_theme_color_override("font_color", Color.WHITE)
	mejorar.add_theme_font_size_override("font_size", 14)
	mejorar.pressed.connect(_on_mejorar_pressed)
	forge_panel.add_child(mejorar)

# --- BOTTOM ACTION SKILLS BAR ---
func _build_bottom_skills() -> void:
	bottom_skills_panel = Panel.new()
	bottom_skills_panel.name = "BottomSkillsPanel"
	bottom_skills_panel.size = Vector2(604, 122)
	bottom_skills_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.03, 0.06, 0.14, 0.84), Color(0.38, 0.68, 1.0, 0.42), 16, 1, 6)
	)
	ui_root.add_child(bottom_skills_panel)

	var hbox := HBoxContainer.new()
	hbox.position = Vector2(12, 8)
	hbox.size = Vector2(580, 92)
	hbox.alignment = BoxContainer.ALIGNMENT_CENTER
	hbox.add_theme_constant_override("separation", 10)
	bottom_skills_panel.add_child(hbox)

	var defs := [
		["Click", "Tajo Combo", "basic", "res://assets/ui/skill_attack.png", Color(0.98, 0.76, 0.25, 0.72)],
		["Q", "Torbellino", "whirlwind", "res://assets/ui/skill_q.png", Color(0.28, 0.78, 1.0, 0.72)],
		["E", "Onda Hoja", "swordWave", "res://assets/ui/skill_e.png", Color(0.76, 0.48, 1.0, 0.72)],
		["R", "Lluvia Espadas", "ultimate", "res://assets/ui/skill_r.png", Color(0.98, 0.44, 0.32, 0.78)],
		["Shift", "Impulso", "dash", "res://assets/ui/skill_shift.png", Color(0.28, 0.88, 0.62, 0.72)],
	]

	for s in defs:
		var wrap := VBoxContainer.new()
		wrap.custom_minimum_size = Vector2(106, 92)
		wrap.add_theme_constant_override("separation", 2)
		hbox.add_child(wrap)

		var box := Panel.new()
		box.custom_minimum_size = Vector2(106, 72)
		box.clip_contents = true
		box.add_theme_stylebox_override("panel", _panel_style(Color(0.05, 0.09, 0.20, 0.94), s[4], 12, 2))
		wrap.add_child(box)

		var icon := TextureRect.new()
		if ResourceLoader.exists(str(s[3])):
			icon.texture = load(str(s[3]))
		icon.set_anchors_preset(Control.PRESET_FULL_RECT)
		icon.offset_left = 4.0
		icon.offset_right = -4.0
		icon.offset_top = 4.0
		icon.offset_bottom = -4.0
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		box.add_child(icon)

		# Dark cooldown curtain
		var cd_mask := ColorRect.new()
		cd_mask.color = Color(0.02, 0.03, 0.08, 0.76)
		cd_mask.position = Vector2(0, 72)
		cd_mask.size = Vector2(106, 0)
		cd_mask.mouse_filter = Control.MOUSE_FILTER_IGNORE
		box.add_child(cd_mask)

		var badge_w := 42 if str(s[0]) in ["Click", "Shift"] else 26
		var key_badge := Panel.new()
		key_badge.position = Vector2(4, 4)
		key_badge.size = Vector2(badge_w, 19)
		key_badge.add_theme_stylebox_override("panel", _panel_style(Color(0.06, 0.11, 0.24, 0.92), s[4], 5, 1))
		box.add_child(key_badge)
		_label(key_badge, str(s[0]), Vector2.ZERO, key_badge.size, 10, Color(0.96, 0.98, 1.0), HORIZONTAL_ALIGNMENT_CENTER)

		var cdl := _label(box, "Listo", Vector2(0, 51), Vector2(106, 18), 11, Color(0.52, 1.0, 0.65), HORIZONTAL_ALIGNMENT_CENTER)

		# Transparent clickable button overlay so clicking HUD slots triggers the skill!
		var click_btn := Button.new()
		click_btn.flat = true
		click_btn.set_anchors_preset(Control.PRESET_FULL_RECT)
		var sid := str(s[2])
		click_btn.pressed.connect(func():
			if player == null:
				return
			if sid == "basic":
				player.perform_attack()
			else:
				player.perform_skill(sid)
		)
		box.add_child(click_btn)

		var namel := _label(wrap, str(s[1]), Vector2.ZERO, Vector2(106, 16), 11, Color(0.86, 0.93, 1.0), HORIZONTAL_ALIGNMENT_CENTER)
		namel.custom_minimum_size = Vector2(106, 16)

		if sid != "basic":
			cd_nodes[sid] = {"panel": box, "cd": cdl, "icon": icon, "mask": cd_mask}

	_label(
		bottom_skills_panel,
		"Mover: WASD/Flechas  •  Atacar: Click/Espacio  •  Skills: Q E R Shift  •  Poción: H  •  Pausa: Esc",
		Vector2(8, 101),
		Vector2(588, 18),
		10,
		Color(0.72, 0.83, 0.96, 0.88),
		HORIZONTAL_ALIGNMENT_CENTER
	)

# --- COMBAT LOG & STUDIO BRANDING ---
func _build_log() -> void:
	log_panel_box = Panel.new()
	log_panel_box.name = "LogPanel"
	log_panel_box.size = Vector2(304, 122)
	log_panel_box.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.03, 0.05, 0.11, 0.72), Color(0.38, 0.62, 0.92, 0.24), 12, 1)
	)
	ui_root.add_child(log_panel_box)

	_label(log_panel_box, "✦ CRÓNICAS DE LA FORJA", Vector2(10, 5), Vector2(284, 16), 10, Color(0.98, 0.82, 0.38))
	log_label = RichTextLabel.new()
	log_label.position = Vector2(10, 23)
	log_label.size = Vector2(284, 92)
	log_label.bbcode_enabled = false
	log_label.scroll_active = false
	log_label.add_theme_font_size_override("normal_font_size", 11)
	log_label.add_theme_color_override("default_color", Color(0.86, 0.92, 1.0, 0.92))
	log_label.text = "¡Bienvenido al Santuario de la Forja de Almas!"
	log_panel_box.add_child(log_label)

func _build_branding() -> void:
	branding_label = Label.new()
	branding_label.name = "Branding"
	branding_label.size = Vector2(304, 24)
	branding_label.clip_text = true
	branding_label.text = "STUDIO LEXAIR | Espada Anime Isekai 3D"
	branding_label.add_theme_font_size_override("font_size", 11)
	branding_label.add_theme_color_override("font_color", Color(0.72, 0.84, 0.98, 0.78))
	branding_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	branding_label.add_theme_constant_override("outline_size", 2)
	ui_root.add_child(branding_label)

# --- BOSS BAR & CEREMONIAL ALERT BANNER ---
func _build_boss_bar() -> void:
	boss_panel = Panel.new()
	boss_panel.name = "BossPanel"
	boss_panel.visible = false
	boss_panel.size = Vector2(460, 54)
	boss_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.14, 0.03, 0.05, 0.88), Color(1.0, 0.35, 0.28, 0.75), 12, 2, 6)
	)
	ui_root.add_child(boss_panel)

	boss_label = _label(boss_panel, "☠ MALAKOR, SEÑOR DEL ABISMO • FASE I", Vector2(14, 5), Vector2(330, 20), 12, Color(1.0, 0.84, 0.46))
	boss_hp_label = _label(boss_panel, "1450 / 1450", Vector2(344, 5), Vector2(102, 20), 11, Color(1.0, 0.88, 0.88), HORIZONTAL_ALIGNMENT_RIGHT)

	boss_bar = ProgressBar.new()
	boss_bar.position = Vector2(14, 29)
	boss_bar.size = Vector2(432, 14)
	boss_bar.show_percentage = false
	boss_bar.add_theme_stylebox_override("background", _panel_style(Color(0.08, 0.02, 0.04, 0.94), Color(1, 1, 1, 0.12), 6))
	boss_bar.add_theme_stylebox_override("fill", _panel_style(Color(0.92, 0.16, 0.24, 0.96), Color(1, 0.6, 0.5, 0.45), 6))
	boss_panel.add_child(boss_bar)

func _build_alert_banner() -> void:
	alert_banner = Panel.new()
	alert_banner.name = "AlertBanner"
	alert_banner.visible = false
	alert_banner.size = Vector2(520, 68)
	alert_banner.mouse_filter = Control.MOUSE_FILTER_IGNORE
	alert_banner.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.08, 0.06, 0.18, 0.94), Color(0.98, 0.78, 0.25, 0.88), 14, 2, 8)
	)
	ui_root.add_child(alert_banner)
	alert_title = _label(alert_banner, "¡METAMORFOSIS COMPLETADA!", Vector2(16, 8), Vector2(488, 26), 16, Color(1.0, 0.88, 0.36), HORIZONTAL_ALIGNMENT_CENTER)
	alert_sub = _label(alert_banner, "", Vector2(16, 35), Vector2(488, 24), 12, Color(0.90, 0.95, 1.0), HORIZONTAL_ALIGNMENT_CENTER)

func _show_banner(title_txt: String, sub_txt: String, border_col: Color, dur: float = 4.0) -> void:
	if alert_banner == null:
		return
	alert_banner.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.07, 0.05, 0.16, 0.94), border_col, 14, 2, 8)
	)
	alert_title.text = title_txt
	alert_title.add_theme_color_override("font_color", border_col)
	alert_sub.text = sub_txt
	alert_banner.visible = true
	_alert_timer = dur
	_layout_responsive()

func _build_combo() -> void:
	combo_label = Label.new()
	combo_label.name = "ComboLabel"
	combo_label.size = Vector2(240, 56)
	combo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	combo_label.add_theme_font_size_override("font_size", 42)
	combo_label.add_theme_color_override("font_color", Color(1.0, 0.54, 0.16, 0.96))
	combo_label.add_theme_color_override("font_outline_color", Color(0.08, 0.02, 0.0, 0.92))
	combo_label.add_theme_constant_override("outline_size", 7)
	combo_label.visible = false
	combo_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui_root.add_child(combo_label)

# --- RESPONSIVE GEOMETRY ENGINE (1280x720, 1366x768, 1600x900, 1920x1080) ---
func _layout_responsive() -> void:
	if ui_root == null:
		return
	var vp_size := ui_root.size
	if vp_size.x < 100 or vp_size.y < 100:
		vp_size = get_viewport().get_visible_rect().size
	var W := maxf(1280.0, vp_size.x)
	var H := maxf(720.0, vp_size.y)

	# Top row
	if top_left_panel:
		top_left_panel.position = Vector2(16, 12)
		top_left_panel.size = Vector2(456, 112)
	if quick_pills_bar:
		quick_pills_bar.position = Vector2(16, 128)
		quick_pills_bar.size = Vector2(456, 30)
	if objective_panel:
		objective_panel.position = Vector2(16, 164)
		objective_panel.size = Vector2(276, 94)

	if evo_nav_column:
		evo_nav_column.position = Vector2(300, 164)
		evo_nav_column.size = Vector2(160, 60)

	if top_right_bar:
		top_right_bar.size = Vector2(424, 38)
		top_right_bar.position = Vector2(W - 440, 12)

	if top_center_panel:
		var tc_w := 336.0
		var tc_x := clampf((W - tc_w) * 0.5, 478.0, W - 446.0 - tc_w)
		top_center_panel.size = Vector2(tc_w, 42)
		top_center_panel.position = Vector2(tc_x, 12)

	# Right column: Minimap + Forge
	if minimap_panel:
		var mm_sz := 148.0 if H < 780.0 else 156.0
		minimap_panel.size = Vector2(mm_sz, mm_sz)
		minimap_panel.position = Vector2(W - mm_sz - 16.0, 56.0)

	if forge_panel:
		var mm_bottom := (minimap_panel.position.y + minimap_panel.size.y) if minimap_panel else 212.0
		forge_panel.size = Vector2(236, 306)
		forge_panel.position = Vector2(W - 252.0, mm_bottom + 8.0)

	if combo_label:
		combo_label.size = Vector2(240, 56)
		combo_label.position = Vector2(W - 504.0, 226.0)

	# Bottom-left: Log + Branding
	if branding_label:
		branding_label.size = Vector2(304, 24)
		branding_label.position = Vector2(16, H - 38.0)
	if log_panel_box:
		log_panel_box.size = Vector2(304, 122)
		log_panel_box.position = Vector2(16, H - 168.0)

	# Bottom-center: Skills
	if bottom_skills_panel:
		var bs_w := 604.0
		var bs_x := clampf((W - bs_w) * 0.5, 326.0, W - 258.0 - bs_w)
		bottom_skills_panel.size = Vector2(bs_w, 122)
		bottom_skills_panel.position = Vector2(bs_x, H - 132.0)

	# Boss bar & Alert banner
	if boss_panel:
		var max_bw := minf(460.0, W - 476.0 - 188.0 - 24.0)
		max_bw = maxf(320.0, max_bw)
		boss_panel.size = Vector2(max_bw, 54)
		boss_panel.position = Vector2(clampf((W - max_bw) * 0.5, 480.0, W - 184.0 - max_bw), 60.0)
		if boss_bar:
			boss_bar.size = Vector2(max_bw - 28.0, 14)
		if boss_label:
			boss_label.size = Vector2(max_bw - 126.0, 20)
		if boss_hp_label:
			boss_hp_label.position = Vector2(max_bw - 114.0, 5)

	if alert_banner:
		var ab_w := minf(520.0, W - 520.0)
		ab_w = maxf(360.0, ab_w)
		alert_banner.size = Vector2(ab_w, 68)
		var ab_y := 120.0 if (boss_panel and boss_panel.visible) else 64.0
		alert_banner.position = Vector2((W - ab_w) * 0.5, ab_y)
		if alert_title: alert_title.size = Vector2(ab_w - 32.0, 26)
		if alert_sub: alert_sub.size = Vector2(ab_w - 32.0, 24)

	# Center all modal overlays safely inside [24..W-24, 24..H-24]
	for ov in [settings_panel, inventory_panel, stats_panel, evolution_panel, skill_panel, game_over_panel]:
		if ov != null:
			var ow := minf(ov.custom_minimum_size.x if ov.custom_minimum_size.x > 0 else ov.size.x, W - 48.0)
			var oh := minf(ov.custom_minimum_size.y if ov.custom_minimum_size.y > 0 else ov.size.y, H - 48.0)
			ov.size = Vector2(ow, oh)
			ov.position = Vector2(round((W - ow) * 0.5), round((H - oh) * 0.5))
			var close_btn: Button = ov.get_node_or_null("CloseBtn")
			if close_btn:
				close_btn.position = Vector2(ow - 44.0, 10.0)

# --- MODAL OVERLAYS ---
func _build_overlay_panel(panel_name: String, title: String, target_size: Vector2) -> Panel:
	var p := Panel.new()
	p.name = panel_name
	p.visible = false
	p.custom_minimum_size = target_size
	p.size = target_size
	p.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.04, 0.06, 0.13, 0.97), Color(0.45, 0.74, 1.0, 0.65), 16, 2, 12)
	)
	ui_root.add_child(p)

	_label(p, title, Vector2(22, 12), Vector2(target_size.x - 80, 32), 22, Color(1.0, 0.88, 0.42))

	var close := Button.new()
	close.name = "CloseBtn"
	close.text = "✕"
	close.position = Vector2(target_size.x - 44, 10)
	close.size = Vector2(32, 32)
	_style_button(close, Color(0.95, 0.45, 0.45, 0.55), 0.9, 13)
	close.pressed.connect(func():
		_play_ui_click()
		p.visible = false
		_sync_backdrop()
	)
	p.add_child(close)
	return p

func _sync_backdrop() -> void:
	if modal_backdrop == null:
		return
	var any_open := (
		(settings_panel and settings_panel.visible)
		or (inventory_panel and inventory_panel.visible)
		or (stats_panel and stats_panel.visible)
		or (evolution_panel and evolution_panel.visible)
		or (skill_panel and skill_panel.visible)
		or (pause_panel and pause_panel.visible)
		or (game_over_panel and game_over_panel.visible)
	)
	modal_backdrop.visible = any_open

func _close_sub_modals() -> void:
	if settings_panel: settings_panel.visible = false
	if inventory_panel: inventory_panel.visible = false
	if stats_panel: stats_panel.visible = false
	if evolution_panel: evolution_panel.visible = false
	if skill_panel: skill_panel.visible = false
	_sync_backdrop()

# 4a. ÁRBOL DE EVOLUCIÓN PERMANENTE (6 Eras / 24 Etapas / 118 Formas)
func _build_evolution_panel() -> void:
	evolution_panel = _build_overlay_panel("EvolutionPanel", "✦ Árbol de Evolución Permanente", Vector2(880, 620))
	var info := _label(evolution_panel, "", Vector2(22, 48), Vector2(836, 22), 13, Color(0.72, 0.88, 1.0))
	info.name = "EvoInfo"

	var era_row := HBoxContainer.new()
	era_row.name = "EvoEraRow"
	era_row.position = Vector2(22, 76)
	era_row.size = Vector2(836, 30)
	era_row.add_theme_constant_override("separation", 6)
	evolution_panel.add_child(era_row)

	var scroll := ScrollContainer.new()
	scroll.name = "EvoScroll"
	scroll.position = Vector2(22, 112)
	scroll.size = Vector2(836, 424)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	evolution_panel.add_child(scroll)
	evolution_list_vb = VBoxContainer.new()
	evolution_list_vb.name = "EvoList"
	evolution_list_vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	evolution_list_vb.add_theme_constant_override("separation", 6)
	scroll.add_child(evolution_list_vb)

	var tip := _label(evolution_panel, "Las decisiones de evolución son PERMANENTES: al elegir una rama, las demás se sellan para siempre.", Vector2(22, 566), Vector2(836, 40), 12, Color(1.0, 0.82, 0.45))
	tip.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

func _refresh_evolution_panel() -> void:
	if evolution_panel == null or evolution_list_vb == null:
		return
	while evolution_list_vb.get_child_count() > 0:
		var c := evolution_list_vb.get_child(0)
		evolution_list_vb.remove_child(c)
		c.queue_free()
	var era_row: HBoxContainer = evolution_panel.get_node_or_null("EvoEraRow")
	if era_row != null:
		for ch in era_row.get_children():
			era_row.remove_child(ch)
			ch.queue_free()

	if player == null or player.evolution_manager == null:
		return
	var em = player.evolution_manager
	var cat = em.catalog
	var ctx: Dictionary = player.get_evolution_context()
	var cur_form: Dictionary = em.get_current_form()
	var cur_stage := int(cur_form.get("stage", 1))
	var cur_era := int(cur_form.get("era", 1))
	if evo_era_filter <= 0:
		evo_era_filter = cur_era

	var info: Label = evolution_panel.get_node_or_null("EvoInfo")
	if info:
		info.text = "Forma actual: %s  •  Etapa %02d/24  •  %s  •  Esencia Evolutiva: %d" % [str(cur_form.get("name", "")), cur_stage, str(cur_form.get("lineage_name", "")), int(em.evolution_xp)]

	# Era filter buttons
	for era in cat.eras:
		var era_num := int(era.get("era", 0))
		var eb := Button.new()
		eb.text = str(era.get("name", "Era"))
		eb.custom_minimum_size = Vector2(136, 28)
		eb.disabled = era_num > cur_stage and era_num > cur_era
		_style_button(eb, Color(0.98, 0.78, 0.30, 0.55) if era_num == evo_era_filter else Color(0.35, 0.55, 0.9, 0.4), 0.9, 11)
		eb.pressed.connect(func():
			_play_ui_click()
			evo_era_filter = era_num
			_refresh_evolution_panel()
		)
		era_row.add_child(eb)

	# Form rows for the filtered era
	for f in cat.get_forms_for_era(evo_era_filter):
		var fid := str(f.get("id", ""))
		var stg := int(f.get("stage", 0))
		var is_current := fid == str(em.current_form_id)
		var is_discarded := em.is_form_discarded(fid)
		var in_history := em.is_form_in_history(fid)
		var direct_child := false
		for nid in cur_form.get("next_forms", []):
			if str(nid) == fid:
				direct_child = true
				break

		var row := Panel.new()
		row.custom_minimum_size = Vector2(820, 58)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var accent := Color(0.45, 0.74, 1.0, 0.35)
		var status_txt := ""
		if is_current:
			accent = Color(1.0, 0.82, 0.30, 0.9)
			status_txt = "★ FORMA ACTUAL"
		elif is_discarded:
			accent = Color(0.55, 0.30, 0.32, 0.55)
			status_txt = "✕ DESCARTADA (PERMANENTE)"
		elif in_history:
			accent = Color(0.40, 0.85, 0.55, 0.55)
			status_txt = "✓ RECORRIDA"
		elif direct_child:
			var ev := em.evaluate_unlock_conditions(fid, ctx)
			if bool(ev.get("can_evolve", false)):
				accent = Color(0.45, 1.0, 0.65, 0.8)
				status_txt = "▶ DISPONIBLE — ¡Puedes evolucionar YA!"
			else:
				accent = Color(0.85, 0.55, 0.30, 0.6)
				var reasons: Array = ev.get("reasons", [])
				var r0 := str(reasons[0]) if reasons.size() > 0 else "Bloqueada"
				status_txt = "⚠ BLOQUEADA — %s" % r0
		else:
			accent = Color(0.35, 0.42, 0.6, 0.45)
			status_txt = "• Otra rama del destino"
		row.add_theme_stylebox_override("panel", _panel_style(Color(0.05, 0.08, 0.16, 0.94), accent, 10, 1))
		evolution_list_vb.add_child(row)

		_label(row, "%02d • %s" % [stg, str(f.get("name", ""))], Vector2(14, 6), Vector2(560, 20), 14, Color(0.96, 0.98, 1.0))
		var uc: Dictionary = f.get("unlock_conditions", {})
		_label(row, "Linaje: %s  •  Requisitos: Nv.%d  •  Esencia %d  •  Mats %s" % [str(f.get("lineage_name", "")), int(uc.get("min_level", 1)), int(uc.get("min_evolution_xp", 0)), str(uc.get("required_materials", {})) if not (uc.get("required_materials", {}) as Dictionary).is_empty() else "—"], Vector2(14, 30), Vector2(660, 20), 11, Color(0.70, 0.82, 0.95))
		var st_lbl := _label(row, status_txt, Vector2(586, 8), Vector2(220, 20), 11, accent)
		st_lbl.name = "Status"

		if direct_child and not is_current and not is_discarded:
			var ev2 := em.evaluate_unlock_conditions(fid, ctx)
			var eb2 := Button.new()
			eb2.text = "✦ EVOLUCIONAR"
			eb2.position = Vector2(660, 26)
			eb2.size = Vector2(150, 26)
			eb2.disabled = not bool(ev2.get("can_evolve", false))
			_style_button(eb2, Color(1.0, 0.85, 0.35, 0.85), 0.95, 12)
			var target := fid
			eb2.pressed.connect(func():
				_play_ui_click()
				if player != null:
					player.try_evolve(target)
					_refresh_evolution_panel()
			)
			row.add_child(eb2)

# 4b. ÁRBOL DE HABILIDADES (6 Ramas / 72 Habilidades)
func _build_skill_panel() -> void:
	skill_panel = _build_overlay_panel("SkillPanel", "❖ Árbol de Habilidades (72)", Vector2(900, 620))
	var info := _label(skill_panel, "", Vector2(22, 48), Vector2(856, 22), 13, Color(0.72, 0.88, 1.0))
	info.name = "SkillInfo"

	var tree_row := HBoxContainer.new()
	tree_row.name = "SkillTreeRow"
	tree_row.position = Vector2(22, 76)
	tree_row.size = Vector2(856, 30)
	tree_row.add_theme_constant_override("separation", 5)
	skill_panel.add_child(tree_row)

	var scroll := ScrollContainer.new()
	scroll.name = "SkillScroll"
	scroll.position = Vector2(22, 112)
	scroll.size = Vector2(856, 424)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	skill_panel.add_child(scroll)
	skill_list_vb = VBoxContainer.new()
	skill_list_vb.name = "SkillList"
	skill_list_vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	skill_list_vb.add_theme_constant_override("separation", 6)
	scroll.add_child(skill_list_vb)

	_label(skill_panel, "Las habilidades ACTIVAS se asignan a las ranuras Q / E / R / Shift desde su tarjeta.", Vector2(22, 566), Vector2(856, 40), 12, Color(1.0, 0.82, 0.45))

func _refresh_skill_panel() -> void:
	if skill_panel == null or skill_list_vb == null:
		return
	while skill_list_vb.get_child_count() > 0:
		var c := skill_list_vb.get_child(0)
		skill_list_vb.remove_child(c)
		c.queue_free()
	var tree_row: HBoxContainer = skill_panel.get_node_or_null("SkillTreeRow")
	if tree_row != null:
		for ch in tree_row.get_children():
			tree_row.remove_child(ch)
			ch.queue_free()

	if player == null or player.skill_manager == null:
		return
	var sm = player.skill_manager
	var sc = sm.catalog
	if skill_tree_filter == "":
		skill_tree_filter = "physical_mastery"

	var info: Label = skill_panel.get_node_or_null("SkillInfo")
	if info:
		var cur_f: Dictionary = player.evolution_manager.get_current_form() if player.evolution_manager != null else {}
		info.text = "Puntos de Habilidad: %d  •  Etapa %02d  •  Linaje: %s  •  Aprendidas: %d/72" % [int(sm.skill_points), int(cur_f.get("stage", 1)), str(cur_f.get("lineage_name", "")), sm.unlocked_skills.size()]

	for t in sc.trees:
		var tid := str(t.get("id", ""))
		var tb := Button.new()
		tb.text = "%s %s" % [str(t.get("icon", "✦")), str(t.get("name", ""))]
		tb.custom_minimum_size = Vector2(136, 28)
		_style_button(tb, Color(0.98, 0.78, 0.30, 0.55) if tid == skill_tree_filter else Color(0.35, 0.55, 0.9, 0.4), 0.9, 10)
		tb.pressed.connect(func():
			_play_ui_click()
			skill_tree_filter = tid
			_refresh_skill_panel()
		)
		tree_row.add_child(tb)

	var lineage := ""
	if player.evolution_manager != null:
		lineage = player.evolution_manager.get_current_lineage()

	for s in sc.get_skills_for_tree(skill_tree_filter):
		var sid := str(s.get("id", ""))
		var learned := sm.is_unlocked(sid)
		var chk := sm.can_unlock_skill(sid, player.evolution_manager.get_current_stage() if player.evolution_manager != null else 1, lineage)
		var s_type := str(s.get("type", "active"))
		var is_active := s_type == "active"

		var row := Panel.new()
		row.custom_minimum_size = Vector2(840, 54)
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var acc := Color(0.45, 0.74, 1.0, 0.35)
		if learned:
			acc = Color(0.40, 0.9, 0.55, 0.75)
		elif bool(chk.get("ok", false)):
			acc = Color(1.0, 0.85, 0.4, 0.7)
		row.add_theme_stylebox_override("panel", _panel_style(Color(0.05, 0.08, 0.16, 0.94), acc, 10, 1))
		skill_list_vb.add_child(row)

		var type_txt := "ACTIVA" if is_active else "PASIVA"
		var status_txt := "✓ APRENDIDA" if learned else ("▶ DISPONIBLE" if bool(chk.get("ok", false)) else ("⚠ %s" % (str((chk.get("reasons", ["Bloqueada"])[0])) if (chk.get("reasons", []) as Array).size() > 0 else "Bloqueada")))
		_label(row, "%s  [%s • Rama %s]  Coste: %d Pt(s)" % [str(s.get("name", "")), type_txt, str(s.get("tree_name", "")), int(s.get("cost_points", 1))], Vector2(14, 6), Vector2(640, 20), 13, Color(0.96, 0.98, 1.0))
		_label(row, "%s  •  Etapa mín. %02d  •  %s" % [str(s.get("description", "")), int(s.get("min_stage", 1)), status_txt], Vector2(14, 28), Vector2(700, 20), 11, Color(0.72, 0.84, 0.96))

		if not learned:
			var ub := Button.new()
			ub.text = "✦ APRENDER"
			ub.position = Vector2(710, 24)
			ub.size = Vector2(116, 24)
			ub.disabled = not bool(chk.get("ok", false))
			_style_button(ub, Color(1.0, 0.85, 0.35, 0.85), 0.95, 11)
			var target := sid
			var stage: int = player.evolution_manager.get_current_stage() if player.evolution_manager != null else 1
			ub.pressed.connect(func():
				_play_ui_click()
				if player != null and player.skill_manager != null:
					var res := player.skill_manager.unlock_skill(target, stage, lineage)
					if bool(res.get("ok", false)):
						_on_log("Habilidad aprendida: %s" % str(res.get("skill", {}).get("name", target)), "upgrade")
					else:
						var rr: Array = res.get("reasons", [])
						if rr.size() > 0:
							_on_log(str(rr[0]), "ui")
					_refresh_skill_panel()
			)
			row.add_child(ub)
		elif is_active:
			# Slot assignment for learned active skills
			var slot_row := HBoxContainer.new()
			slot_row.position = Vector2(560, 22)
			slot_row.size = Vector2(280, 26)
			slot_row.add_theme_constant_override("separation", 4)
			row.add_child(slot_row)
			for slot in ["Q", "E", "R", "SHIFT"]:
				var equipped_here := str(sm.equipped_slots.get(slot, "")) == sid
				var sb := Button.new()
				sb.text = slot if not equipped_here else "[%s] ✓" % slot
				sb.custom_minimum_size = Vector2(62, 24)
				_style_button(sb, Color(0.45, 1.0, 0.65, 0.6) if equipped_here else Color(0.35, 0.55, 0.9, 0.4), 0.9, 10)
				var slot_target: String = slot
				sb.pressed.connect(func():
					_play_ui_click()
					if player != null and player.skill_manager != null:
						player.skill_manager.equip_active_skill(slot_target, sid)
						_refresh_skill_panel()
				)
				slot_row.add_child(sb)

func _toggle_evolution() -> void:
	_play_ui_click()
	var next_vis := not evolution_panel.visible if evolution_panel else false
	_close_sub_modals()
	if evolution_panel:
		evo_era_filter = 0
		evolution_panel.visible = next_vis
		if next_vis:
			_refresh_evolution_panel()
	_sync_backdrop()
	_layout_responsive()

func _toggle_skill_tree() -> void:
	_play_ui_click()
	var next_vis := not skill_panel.visible if skill_panel else false
	_close_sub_modals()
	if skill_panel:
		skill_panel.visible = next_vis
		if next_vis:
			_refresh_skill_panel()
	_sync_backdrop()
	_layout_responsive()

# 1. AJUSTES (Quality + Persistent Volume Sliders + Gameplay Toggles)
func _build_settings_panel() -> void:
	settings_panel = _build_overlay_panel("SettingsPanel", "⚙ Ajustes del Santuario", Vector2(560, 430))

	_label(settings_panel, "CALIDAD GRÁFICA", Vector2(22, 54), Vector2(240, 20), 12, Color(0.68, 0.86, 1.0))
	var q_opts := [["Baja", "low"], ["Media", "medium"], ["Alta", "high"]]
	for i in range(q_opts.size()):
		var opt: Array = q_opts[i]
		var qb := Button.new()
		qb.text = "Calidad " + str(opt[0])
		qb.position = Vector2(22 + i * 174, 78)
		qb.size = Vector2(162, 36)
		_style_button(qb, Color(0.42, 0.72, 1.0, 0.5), 0.9, 13)
		var q_key := str(opt[1])
		qb.pressed.connect(func():
			_play_ui_click()
			_apply_quality(q_key)
		)
		settings_panel.add_child(qb)
		_quality_btns[q_key] = qb

	_label(settings_panel, "MEZCLADOR DE AUDIO (PERSISTENTE)", Vector2(22, 128), Vector2(360, 20), 12, Color(0.68, 0.86, 1.0))

	var rows := [
		["Volumen Maestro", "master", 156.0],
		["Música Ambiental / Jefe", "music", 198.0],
		["Efectos de Combate (SFX)", "sfx", 240.0],
	]
	for r in rows:
		var y := float(r[2])
		_label(settings_panel, str(r[0]), Vector2(22, y), Vector2(195, 24), 13, Color(0.92, 0.95, 1.0))
		var sl := HSlider.new()
		sl.position = Vector2(224, y + 3)
		sl.size = Vector2(236, 20)
		sl.min_value = 0.0
		sl.max_value = 100.0
		sl.step = 1.0
		sl.value = 85.0
		settings_panel.add_child(sl)
		var vlbl := _label(settings_panel, "85%", Vector2(468, y), Vector2(64, 24), 13, Color(1.0, 0.88, 0.42), HORIZONTAL_ALIGNMENT_RIGHT)
		var kind := str(r[1])
		sl.value_changed.connect(func(v: float): _on_volume_slider_changed(kind, v))
		if kind == "master":
			_master_slider = sl; _master_val_lbl = vlbl
		elif kind == "music":
			_music_slider = sl; _music_val_lbl = vlbl
		else:
			_sfx_slider = sl; _sfx_val_lbl = vlbl

	_mute_btn = Button.new()
	_mute_btn.position = Vector2(22, 282)
	_mute_btn.size = Vector2(246, 36)
	_mute_btn.text = "▶ Audio Activo (Click Silenciar)"
	_style_button(_mute_btn, Color(0.35, 0.88, 0.62, 0.55), 0.9, 12)
	_mute_btn.pressed.connect(_toggle_audio)
	settings_panel.add_child(_mute_btn)

	var save_cfg_btn := Button.new()
	save_cfg_btn.position = Vector2(284, 282)
	save_cfg_btn.size = Vector2(250, 36)
	save_cfg_btn.text = "★ Guardar Partida y Ajustes"
	_style_button(save_cfg_btn, Color(0.98, 0.78, 0.28, 0.55), 0.9, 12)
	save_cfg_btn.pressed.connect(func():
		_play_ui_click()
		_on_save_pressed()
	)
	settings_panel.add_child(save_cfg_btn)

	_label(settings_panel, "OPCIONES RÁPIDAS DE JUGABILIDAD", Vector2(22, 332), Vector2(340, 20), 12, Color(0.68, 0.86, 1.0))
	var ah_btn := Button.new()
	ah_btn.position = Vector2(22, 358)
	ah_btn.size = Vector2(246, 36)
	ah_btn.text = "Alternar Auto-Caza"
	_style_button(ah_btn, Color(0.38, 0.78, 1.0, 0.5), 0.9, 12)
	ah_btn.pressed.connect(func():
		if player:
			player.toggle_auto_hunt()
			_refresh_quick_pills()
	)
	settings_panel.add_child(ah_btn)

	var wm_btn := Button.new()
	wm_btn.position = Vector2(284, 358)
	wm_btn.size = Vector2(250, 36)
	wm_btn.text = "Cambiar Espada Viva / Caballero"
	_style_button(wm_btn, Color(0.98, 0.78, 0.32, 0.5), 0.9, 12)
	wm_btn.pressed.connect(func():
		if player:
			player.toggle_wielder_mode()
			_refresh_quick_pills()
	)
	settings_panel.add_child(wm_btn)

# 2. INVENTARIO RPG COMPLETO (Equipo Rúnico, Consumibles, Materiales y Taller de Reliquias)
func _build_inventory_panel() -> void:
	inventory_panel = _build_overlay_panel("InventoryPanel", "✦ Inventario RPG y Taller de Reliquias", Vector2(760, 490))

	# Summary header line (kept as inventory_label for compatibility & quick reading)
	inventory_label = RichTextLabel.new()
	inventory_label.position = Vector2(22, 46)
	inventory_label.size = Vector2(716, 24)
	inventory_label.bbcode_enabled = false
	inventory_label.scroll_active = false
	inventory_label.add_theme_font_size_override("normal_font_size", 13)
	inventory_label.add_theme_color_override("default_color", Color(0.86, 0.93, 1.0))
	inventory_panel.add_child(inventory_label)

	var left_scroll := ScrollContainer.new()
	left_scroll.position = Vector2(22, 74)
	left_scroll.size = Vector2(346, 396)
	inventory_panel.add_child(left_scroll)
	inv_left_box = VBoxContainer.new()
	inv_left_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inv_left_box.add_theme_constant_override("separation", 6)
	left_scroll.add_child(inv_left_box)

	var right_scroll := ScrollContainer.new()
	right_scroll.position = Vector2(384, 74)
	right_scroll.size = Vector2(354, 396)
	inventory_panel.add_child(right_scroll)
	inv_right_box = VBoxContainer.new()
	inv_right_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inv_right_box.add_theme_constant_override("separation", 6)
	right_scroll.add_child(inv_right_box)

# 3. ESTADÍSTICAS Y CÓDICE DE EVOLUCIONES
func _build_stats_panel() -> void:
	stats_panel = _build_overlay_panel("StatsPanel", "★ Atributos y Códice de Evolución", Vector2(720, 470))

	stats_label = RichTextLabel.new()
	stats_label.position = Vector2(22, 54)
	stats_label.size = Vector2(332, 394)
	stats_label.bbcode_enabled = false
	stats_label.add_theme_font_size_override("normal_font_size", 13)
	stats_label.add_theme_color_override("default_color", Color(0.90, 0.95, 1.0))
	stats_panel.add_child(stats_label)

	codex_label = RichTextLabel.new()
	codex_label.position = Vector2(372, 54)
	codex_label.size = Vector2(326, 394)
	codex_label.bbcode_enabled = false
	codex_label.add_theme_font_size_override("normal_font_size", 12)
	codex_label.add_theme_color_override("default_color", Color(0.86, 0.92, 1.0))
	stats_panel.add_child(codex_label)

# 4. PAUSA
func _build_pause() -> void:
	pause_panel = Panel.new()
	pause_panel.name = "PausePanel"
	pause_panel.visible = false
	pause_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	pause_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.01, 0.02, 0.06, 0.72), Color(0, 0, 0, 0), 0, 0))
	ui_root.add_child(pause_panel)

	var card := Panel.new()
	card.set_anchors_preset(Control.PRESET_CENTER)
	card.offset_left = -170
	card.offset_right = 170
	card.offset_top = -155
	card.offset_bottom = 155
	card.grow_horizontal = Control.GROW_DIRECTION_BOTH
	card.grow_vertical = Control.GROW_DIRECTION_BOTH
	card.add_theme_stylebox_override("panel", _panel_style(Color(0.04, 0.07, 0.15, 0.96), Color(0.98, 0.80, 0.32, 0.65), 16, 2, 12))
	pause_panel.add_child(card)

	var box := VBoxContainer.new()
	box.position = Vector2(24, 18)
	box.size = Vector2(292, 274)
	box.add_theme_constant_override("separation", 9)
	card.add_child(box)

	var title := _label(box, "✦ PAUSA ✦", Vector2.ZERO, Vector2(292, 36), 28, Color(1.0, 0.90, 0.52), HORIZONTAL_ALIGNMENT_CENTER)
	title.custom_minimum_size = Vector2(292, 36)

	var actions := [
		["▶ Continuar Combate", _on_resume_pressed],
		["★ Guardar Partida", _on_save_pressed],
		["⚙ Ajustes de Audio/Video", _on_pause_settings_pressed],
		["✦ Menú Principal", _on_main_menu_pressed],
		["✕ Salir del Juego", _on_quit_pressed],
	]
	for pair in actions:
		var b := Button.new()
		b.text = str(pair[0])
		b.custom_minimum_size = Vector2(292, 38)
		_style_button(b, Color(0.45, 0.72, 1.0, 0.48), 0.9, 13)
		b.pressed.connect(pair[1])
		box.add_child(b)

# 5. GAME OVER
func _build_game_over() -> void:
	game_over_panel = Panel.new()
	game_over_panel.name = "GameOverPanel"
	game_over_panel.visible = false
	game_over_panel.custom_minimum_size = Vector2(460, 230)
	game_over_panel.size = Vector2(460, 230)
	game_over_panel.add_theme_stylebox_override(
		"panel",
		_panel_style(Color(0.06, 0.02, 0.05, 0.96), Color(1.0, 0.36, 0.32, 0.78), 16, 2, 12)
	)
	ui_root.add_child(game_over_panel)

	_label(game_over_panel, "☠ HAS CAÍDO EN LA ARENA", Vector2(20, 22), Vector2(420, 38), 28, Color(1.0, 0.78, 0.76), HORIZONTAL_ALIGNMENT_CENTER)
	_label(game_over_panel, "La Forja Ancestral conserva el alma y poder de tu hoja.", Vector2(20, 66), Vector2(420, 24), 13, Color(0.88, 0.91, 0.98, 0.92), HORIZONTAL_ALIGNMENT_CENTER)
	game_over_summary = _label(game_over_panel, "Nivel 1 • Oleada 1 • 0 Bajas", Vector2(20, 96), Vector2(420, 24), 13, Color(1.0, 0.86, 0.42), HORIZONTAL_ALIGNMENT_CENTER)

	var btn := Button.new()
	btn.name = "RespawnBtn"
	btn.text = "✦ Reaparecer en la Forja ✦"
	btn.position = Vector2(110, 148)
	btn.size = Vector2(240, 44)
	_style_button(btn, Color(0.98, 0.78, 0.30, 0.85), 0.95, 14)
	btn.pressed.connect(_on_respawn_pressed)
	game_over_panel.add_child(btn)

# --- PLAYER WIRING & REACTIVE UPDATES ---
func connect_player(p: Player) -> void:
	player = p
	if minimap_radar:
		minimap_radar.player_ref = p

	player.hp_changed.connect(_on_hp)
	player.xp_changed.connect(_on_xp)
	player.gold_changed.connect(_on_gold)
	player.kills_changed.connect(_on_kills)
	player.wave_changed.connect(_on_wave)
	player.evolution_changed.connect(_on_evo)
	player.log_added.connect(_on_log)
	if player.has_signal("player_died"):
		player.player_died.connect(_on_player_died)
	if player.has_signal("cooldowns_changed"):
		player.cooldowns_changed.connect(func(_c): _update_cooldowns())
	if player.has_signal("inventory_changed"):
		player.inventory_changed.connect(_on_inventory_changed)
	if player.has_signal("floating_text_requested"):
		player.floating_text_requested.connect(_spawn_floating_text)

	var gd := player._get_gamedata()
	_on_hp(player.player_hp, player.player_max_hp)
	_on_xp(player.current_xp, int(gd.get_xp_required(player.sword_level)), player.sword_level)
	_on_gold(player.gold)
	_on_kills(player.kills)
	_on_wave(player.wave, player.wave_kills)
	_refresh_quick_pills()
	if boss_panel: boss_panel.visible = false
	if game_over_panel: game_over_panel.visible = false
	if pause_panel: pause_panel.visible = false
	_sync_backdrop()
	_layout_responsive()

func _refresh_quick_pills() -> void:
	if player == null:
		return
	if auto_btn:
		auto_btn.text = "Auto-Caza: ON" if player.auto_hunt else "Auto-Caza: OFF"
		_style_button(
			auto_btn,
			Color(0.22, 0.95, 0.85, 0.92) if player.auto_hunt else Color(0.32, 0.78, 1.0, 0.45),
			0.92 if player.auto_hunt else 0.84,
			11
		)
	if mode_btn:
		mode_btn.text = "Modo: Caballero 3D" if player.wielder_mode == "knight_wielder" else "Modo: Espada Viva"
	if potion_btn:
		var p_cnt := int(player.consumables.get("potion_hp", 0))
		potion_btn.text = "Poción [H]: %d" % p_cnt
		potion_btn.disabled = p_cnt <= 0

func _on_inventory_changed() -> void:
	_refresh_quick_pills()
	if inventory_panel and inventory_panel.visible:
		_refresh_inventory()
	if stats_panel and stats_panel.visible:
		_refresh_stats()

func _on_hp(cur: int, max_hp: int) -> void:
	if hp_bar_new:
		hp_bar_new.max_value = maxi(1, max_hp)
		hp_bar_new.value = clampi(cur, 0, max_hp)
		var ratio := float(cur) / float(maxi(1, max_hp))
		var fill: StyleBoxFlat = hp_bar_new.get_theme_stylebox("fill")
		if fill:
			fill.bg_color = (
				Color(0.20, 0.88, 0.42, 0.96) if ratio > 0.5
				else (Color(0.96, 0.76, 0.20, 0.96) if ratio > 0.25 else Color(0.92, 0.20, 0.28, 0.96))
			)
	if hp_text:
		hp_text.text = "%d / %d" % [cur, max_hp]

func _on_xp(cur: int, req: int, level: int) -> void:
	var safe_req := maxi(1, req)
	if xp_bar_new:
		xp_bar_new.max_value = safe_req
		xp_bar_new.value = clampi(cur, 0, safe_req)
	var pct := mini(100, int(round((float(cur) / float(safe_req)) * 100.0)))
	if xp_text:
		xp_text.text = "%d/%d (%d%%)" % [cur, safe_req, pct]
	if lvl_text:
		lvl_text.text = "Nv. %d" % level
	var gd = get_node_or_null("/root/GameData")
	if gd == null and player:
		gd = player._get_gamedata()
	# v3: display the ACTUAL permanent evolution form (never the level-derived tier)
	var tier: Dictionary = {}
	if player != null and player.get("evolution_manager") != null and player.evolution_manager != null:
		tier = player.evolution_manager.get_legacy_tier_view()
	if tier.is_empty() and gd:
		tier = gd.get_sword_for_level(level)
	if not tier.is_empty():
		if sword_text:
			sword_text.text = str(tier["name"])
		if subtitle_text:
			var next_lv = tier.get("next_evolution_level", null)
			if next_lv != null:
				subtitle_text.text = "%s • Próx. Evo: Nv.%d" % [str(tier.get("subtitle", "")).split("•")[0].strip_edges(), int(next_lv)]
			else:
				subtitle_text.text = "Era VI • FORMA SUPREMA FINAL"
		if portrait_ring:
			var acol: Color = tier.get("aura_color", Color(0.45, 0.86, 1.0))
			portrait_ring.add_theme_stylebox_override(
				"panel",
				_panel_style(Color(0.08, 0.14, 0.28, 0.96), Color(acol.r, acol.g, acol.b, 0.95), 42, 3)
			)
	_update_forge_buttons()

func _on_gold(g: int) -> void:
	if gold_text:
		gold_text.text = "★ %d Oro" % g
	_update_forge_buttons()
	if inventory_panel and inventory_panel.visible:
		_refresh_inventory()

func _on_kills(k: int) -> void:
	if kills_top_text:
		kills_top_text.text = "✦ %d Bajas" % k
	if k > 0:
		combo_count += 1
		combo_timer = 2.5
		if combo_label:
			combo_label.text = "%d COMBO!" % combo_count
			combo_label.add_theme_color_override("font_color", Color(1.0, 0.54, 0.16, 0.96))
			combo_label.visible = true

func _on_wave(w: int, wk: int) -> void:
	if wave_text:
		wave_text.text = "☠ Oleada %d" % w
	if objective_bar:
		objective_bar.value = clampi(wk, 0, 8)
	if objective_text:
		objective_text.text = "%d / 8" % wk
	if objective_title and objective_sub:
		if w % 3 == 0:
			objective_title.text = "☠ ALERTA DE JEFE (OLEADA %d)" % w
			objective_sub.text = "¡Derrota a Malakor, Señor del Abismo\ny limpia la oleada para reclamar su reliquia!"
		else:
			objective_title.text = "⚠ OBJETIVO DE OLEADA"
			objective_sub.text = "Elimina 8 monstruos para avanzar\na la siguiente oleada."

func _on_evo(tier: Dictionary) -> void:
	_on_log("¡EVOLUCIÓN! %s" % str(tier["name"]), "evolution")
	_show_banner(
		"✦ ¡METAMORFOSIS: %s! ✦" % str(tier.get("name", "")).to_upper(),
		"%s — %s" % [str(tier.get("passive_name", "")), str(tier.get("passive_description", ""))],
		Color(1.0, 0.84, 0.28, 0.95),
		4.8
	)

func notify_boss_spawned(boss_node: Node3D) -> void:
	var bname := "Malakor, Señor del Abismo"
	if boss_node and boss_node.get("def") != null:
		bname = str(boss_node.def.get("name", bname))
	_show_banner(
		"☠ ¡%s HA EMERGIDO! ☠" % bname.to_upper(),
		"Esquiva sus áreas carmesí con Shift y derrótalo para obtener el Corazón de Malakor.",
		Color(1.0, 0.30, 0.32, 0.95),
		4.5
	)

func notify_boss_defeated(summary: Dictionary) -> void:
	var loot_arr: Array = summary.get("loot", [])
	var loot_str := ", ".join(loot_arr) if not loot_arr.is_empty() else "Botín Abisal"
	_show_banner(
		"★ ¡MALAKOR DERROTADO! ★",
		"+%d EXP  •  +%d Oro  •  %s" % [int(summary.get("xp", 0)), int(summary.get("gold", 0)), loot_str],
		Color(0.95, 0.76, 0.24, 0.96),
		5.2
	)

func _on_log(text: String, kind: String) -> void:
	var prefix := "• "
	match kind:
		"evolution": prefix = "[EVO] "
		"skill": prefix = "[SKILL] "
		"upgrade": prefix = "[FORJA] "
		"boss": prefix = "[JEFE] "
		"levelup": prefix = "[NV] "
		"loot": prefix = "[BOTÍN] "
	log_lines.push_front(prefix + text)
	if log_lines.size() > 6:
		log_lines.resize(6)
	if log_label:
		log_label.text = "\n".join(log_lines)

func _update_forge_buttons() -> void:
	if player == null:
		return
	var base_costs := {"sharpness": 25, "swiftness": 30, "criticalMastery": 35, "vampirism": 40, "soulMagnet": 30, "bladeSize": 45}
	var names := {"sharpness": "Afilar", "swiftness": "Ligereza", "criticalMastery": "Crítico", "vampirism": "Vampiro", "soulMagnet": "Almas", "bladeSize": "Colosal"}
	for k in forge_buttons.keys():
		var b: Button = forge_buttons[k]
		var lvl := int(player.upgrades.get(k, 0))
		if lvl >= 10:
			b.text = "%s  Nv.10/10  •  MÁX" % names[k]
			b.disabled = true
		else:
			var cost := int(round(base_costs[k] * pow(1.45, lvl)))
			b.text = "%s  Nv.%d/10  •  %dg" % [names[k], lvl, cost]
			b.disabled = player.gold < cost

func _on_upgrade_pressed(key: String, base_cost: int) -> void:
	if player:
		player.buy_upgrade(key, base_cost)

func _on_mejorar_pressed() -> void:
	if player == null:
		return
	var base_costs := {"sharpness": 25, "swiftness": 30, "criticalMastery": 35, "vampirism": 40, "soulMagnet": 30, "bladeSize": 45}
	var best_key := ""
	var best_cost := 999999
	for k in base_costs.keys():
		var lvl := int(player.upgrades.get(k, 0))
		if lvl >= 10:
			continue
		var cost := int(round(base_costs[k] * pow(1.45, lvl)))
		if player.gold >= cost and cost < best_cost:
			best_cost = cost
			best_key = k
	if best_key != "":
		player.buy_upgrade(best_key, int(base_costs[best_key]))
	else:
		_play_ui_click()
		_on_log("Oro insuficiente para la siguiente mejora.", "upgrade")

func _process(delta: float) -> void:
	_update_boss_bar()
	_update_cooldowns()
	_update_floating_texts(delta)
	if combo_timer > 0.0:
		combo_timer -= delta
		if combo_timer <= 0.0 and combo_label:
			combo_label.visible = false
			combo_count = 0
	if _alert_timer > 0.0:
		_alert_timer -= delta
		if _alert_timer <= 0.0 and alert_banner:
			alert_banner.visible = false

func _update_boss_bar() -> void:
	if boss_panel == null or not is_inside_tree():
		return
	var boss: Node3D = null
	for e in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
			boss = e
			break
	if boss:
		var was_hidden := not boss_panel.visible
		boss_panel.visible = true
		var cur_hp := int(boss.get("hp"))
		var max_b_hp := maxi(1, int(boss.get("max_hp")))
		var phase := int(boss.get("boss_phase")) if boss.get("boss_phase") != null else 1
		boss_bar.max_value = max_b_hp
		boss_bar.value = cur_hp
		var bname := str(boss.def.get("name", "Malakor")) if boss.get("def") != null else "Malakor"
		boss_label.text = "☠ %s • %s" % [bname.to_upper(), ("FASE II • FURIA ABISAL" if phase >= 2 else "FASE I")]
		boss_hp_label.text = "%d / %d" % [cur_hp, max_b_hp]
		var fill: StyleBoxFlat = boss_bar.get_theme_stylebox("fill")
		if fill:
			fill.bg_color = Color(0.88, 0.20, 0.92, 0.96) if phase >= 2 else Color(0.92, 0.16, 0.24, 0.96)
		if was_hidden:
			_layout_responsive()
	else:
		if boss_panel.visible:
			boss_panel.visible = false
			_layout_responsive()

func _update_cooldowns() -> void:
	if player == null:
		return
	var cds = player.get("cooldowns")
	if cds == null:
		return
	for id in cd_nodes.keys():
		var v := float(cds.get(id, 0.0))
		var max_v := float(player.get_effective_cd_max(id)) if player.has_method("get_effective_cd_max") else float(player.cd_max.get(id, 4.0))
		var node: Dictionary = cd_nodes[id]
		var lbl: Label = node["cd"]
		var box: Panel = node["panel"]
		var mask: ColorRect = node["mask"]
		if v > 0.05:
			lbl.text = "%.1fs" % v
			lbl.add_theme_color_override("font_color", Color(1.0, 0.72, 0.45, 0.98))
			box.modulate = Color(0.82, 0.84, 0.92, 0.95)
			var ratio := clampf(v / maxf(0.1, max_v), 0.0, 1.0)
			var h := 72.0 * ratio
			mask.position = Vector2(0, 72.0 - h)
			mask.size = Vector2(106.0, h)
		else:
			lbl.text = "Listo"
			lbl.add_theme_color_override("font_color", Color(0.48, 1.0, 0.65, 0.98))
			box.modulate = Color.WHITE
			mask.size = Vector2(106.0, 0.0)

# --- FLOATING 2D DAMAGE / HEAL NUMBERS ---
func _spawn_floating_text(world_pos: Vector3, text: String, col: Color, is_big: bool) -> void:
	if floating_layer == null or not is_inside_tree() or get_viewport() == null:
		return
	if _floating_items.size() >= 18:
		var oldest: Dictionary = _floating_items.pop_front()
		if is_instance_valid(oldest["label"]):
			oldest["label"].queue_free()
	var cam := get_viewport().get_camera_3d()
	if cam == null or cam.is_position_behind(world_pos):
		return
	var screen_pos := cam.unproject_position(world_pos) + Vector2(randf_range(-16.0, 16.0), -10.0)
	var l := Label.new()
	l.text = text
	l.position = screen_pos - Vector2(60, 14)
	l.size = Vector2(120, 28)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", 22 if is_big else 15)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0.02, 0.02, 0.05, 0.95))
	l.add_theme_constant_override("outline_size", 5 if is_big else 3)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	floating_layer.add_child(l)
	_floating_items.append({"label": l, "age": 0.0, "dur": 0.78})

func _update_floating_texts(delta: float) -> void:
	for i in range(_floating_items.size() - 1, -1, -1):
		var item: Dictionary = _floating_items[i]
		var lbl: Label = item["label"]
		if not is_instance_valid(lbl):
			_floating_items.remove_at(i)
			continue
		item["age"] = float(item["age"]) + delta
		var t := float(item["age"]) / float(item["dur"])
		if t >= 1.0:
			lbl.queue_free()
			_floating_items.remove_at(i)
		else:
			lbl.position.y -= 36.0 * delta
			lbl.modulate.a = 1.0 - smoothstep(0.55, 1.0, t)

# --- INPUT & PAUSE / OVERLAY TOGGLES ---
func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_T:
			_toggle_evolution()
			return
		elif event.physical_keycode == KEY_K:
			_toggle_skill_tree()
			return
	if event.is_action_pressed("ui_cancel"):
		if settings_panel and settings_panel.visible:
			settings_panel.visible = false
			_sync_backdrop()
		elif inventory_panel and inventory_panel.visible:
			inventory_panel.visible = false
			_sync_backdrop()
		elif stats_panel and stats_panel.visible:
			stats_panel.visible = false
			_sync_backdrop()
		elif evolution_panel and evolution_panel.visible:
			evolution_panel.visible = false
			_sync_backdrop()
		elif skill_panel and skill_panel.visible:
			skill_panel.visible = false
			_sync_backdrop()
		else:
			_toggle_pause()

func _toggle_pause() -> void:
	if game_over_panel and game_over_panel.visible:
		return
	_play_ui_click()
	_close_sub_modals()
	var paused := not get_tree().paused
	get_tree().paused = paused
	if pause_panel:
		pause_panel.visible = paused
	_sync_backdrop()

func _on_resume_pressed() -> void:
	_play_ui_click()
	get_tree().paused = false
	if pause_panel:
		pause_panel.visible = false
	_sync_backdrop()

func _on_pause_settings_pressed() -> void:
	_on_resume_pressed()
	_toggle_settings()

func _on_save_pressed() -> void:
	_play_ui_click()
	if player and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(player)
		_on_log("Partida guardada correctamente.", "upgrade")

func _on_main_menu_pressed() -> void:
	_play_ui_click()
	if player and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(player)
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _on_quit_pressed() -> void:
	if player and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(player)
	get_tree().paused = false
	get_tree().quit()

func _on_player_died() -> void:
	_close_sub_modals()
	if pause_panel:
		pause_panel.visible = false
	get_tree().paused = false
	if game_over_summary and player:
		game_over_summary.text = "Espada Nv. %d  •  Oleada %d  •  %d Bajas" % [player.sword_level, player.wave, player.kills]
	if game_over_panel:
		game_over_panel.visible = true
	_sync_backdrop()
	_layout_responsive()

func _on_respawn_pressed() -> void:
	_play_ui_click()
	if player and player.has_method("respawn_player"):
		player.respawn_player()
	if game_over_panel:
		game_over_panel.visible = false
	_sync_backdrop()

# --- SETTINGS & VOLUME HANDLERS ---
func _apply_quality(q: String) -> void:
	var vp := get_viewport()
	if vp != null:
		match q:
			"low":
				vp.msaa_3d = Viewport.MSAA_DISABLED
				ProjectSettings.set_setting("rendering/lights_and_shadows/directional_shadow/size", 1024)
			"medium":
				vp.msaa_3d = Viewport.MSAA_2X
				ProjectSettings.set_setting("rendering/lights_and_shadows/directional_shadow/size", 2048)
			"high":
				vp.msaa_3d = Viewport.MSAA_4X
				ProjectSettings.set_setting("rendering/lights_and_shadows/directional_shadow/size", 4096)

	var cur_scene := get_tree().current_scene if is_inside_tree() else null
	if cur_scene:
		var we: WorldEnvironment = cur_scene.get_node_or_null("WorldEnvironment")
		if we and we.environment:
			we.environment.glow_enabled = q != "low"
			we.environment.fog_enabled = q != "low"
		var decor := cur_scene.get_node_or_null("Arena/ArenaDecor")
		if decor and decor.has_method("apply_quality"):
			decor.apply_quality(q)

	for k in _quality_btns.keys():
		var btn: Button = _quality_btns[k]
		var active: bool = (str(k) == q)
		_style_button(
			btn,
			Color(0.98, 0.80, 0.28, 0.95) if active else Color(0.42, 0.72, 1.0, 0.35),
			0.96 if active else 0.84,
			13
		)

	var ss = get_node_or_null("/root/SaveSystem")
	if ss:
		ss.settings["quality"] = q
		ss.save_settings()

func _on_volume_slider_changed(kind: String, pct_val: float) -> void:
	var linear := clampf(pct_val / 100.0, 0.0, 1.0)
	var am := get_node_or_null("/root/AudioManager")
	var ss := get_node_or_null("/root/SaveSystem")
	if kind == "master":
		if _master_val_lbl: _master_val_lbl.text = "%d%%" % int(round(pct_val))
		if am: am.set_master_volume(linear)
		if ss: ss.settings["master_volume"] = linear
	elif kind == "music":
		if _music_val_lbl: _music_val_lbl.text = "%d%%" % int(round(pct_val))
		if am: am.set_music_volume(linear)
		if ss: ss.settings["music_volume"] = linear
	elif kind == "sfx":
		if _sfx_val_lbl: _sfx_val_lbl.text = "%d%%" % int(round(pct_val))
		if am: am.set_sfx_volume(linear)
		if ss: ss.settings["sfx_volume"] = linear
	if ss:
		ss.save_settings()

func _toggle_audio() -> void:
	_audio_muted = not _audio_muted
	var am := get_node_or_null("/root/AudioManager")
	if am:
		am.set_muted(_audio_muted)
	else:
		AudioServer.set_bus_mute(0, _audio_muted)
	_refresh_mute_button()
	var ss := get_node_or_null("/root/SaveSystem")
	if ss:
		ss.settings["audio_muted"] = _audio_muted
		ss.save_settings()
	_on_log("Audio: %s" % ("SILENCIADO" if _audio_muted else "ACTIVO"), "upgrade")

func _refresh_mute_button() -> void:
	if _mute_btn == null:
		return
	_mute_btn.text = "✕ Audio Silenciado (Click Activar)" if _audio_muted else "▶ Audio Activo (Click Silenciar)"
	_style_button(
		_mute_btn,
		Color(0.95, 0.42, 0.45, 0.78) if _audio_muted else Color(0.35, 0.88, 0.62, 0.65),
		0.92,
		12
	)

func _load_settings() -> void:
	var ss := get_node_or_null("/root/SaveSystem")
	if ss:
		ss.load_settings_only()
		_audio_muted = bool(ss.settings.get("audio_muted", false))
		var mv := float(ss.settings.get("master_volume", 0.85))
		var muv := float(ss.settings.get("music_volume", 0.70))
		var sv := float(ss.settings.get("sfx_volume", 0.85))
		if _master_slider: _master_slider.set_value_no_signal(round(mv * 100.0))
		if _music_slider: _music_slider.set_value_no_signal(round(muv * 100.0))
		if _sfx_slider: _sfx_slider.set_value_no_signal(round(sv * 100.0))
		if _master_val_lbl: _master_val_lbl.text = "%d%%" % int(round(mv * 100.0))
		if _music_val_lbl: _music_val_lbl.text = "%d%%" % int(round(muv * 100.0))
		if _sfx_val_lbl: _sfx_val_lbl.text = "%d%%" % int(round(sv * 100.0))
		_refresh_mute_button()
		var am := get_node_or_null("/root/AudioManager")
		if am:
			am.apply_settings_dict(ss.settings)
		else:
			AudioServer.set_bus_mute(0, _audio_muted)
		_apply_quality(str(ss.settings.get("quality", "medium")))

# --- OVERLAY TOGGLE HANDLERS ---
func _toggle_settings() -> void:
	_play_ui_click()
	var next_vis := not settings_panel.visible if settings_panel else false
	_close_sub_modals()
	if settings_panel:
		settings_panel.visible = next_vis
	_sync_backdrop()
	_layout_responsive()

func _toggle_inventory() -> void:
	_play_ui_click()
	var next_vis := not inventory_panel.visible if inventory_panel else false
	_close_sub_modals()
	if inventory_panel:
		inventory_panel.visible = next_vis
		if next_vis:
			_refresh_inventory()
	_sync_backdrop()
	_layout_responsive()

func _toggle_stats() -> void:
	_play_ui_click()
	var next_vis := not stats_panel.visible if stats_panel else false
	_close_sub_modals()
	if stats_panel:
		stats_panel.visible = next_vis
		if next_vis:
			_refresh_stats()
	_sync_backdrop()
	_layout_responsive()

# --- POPULATE RPG INVENTORY & CRAFTING ---
func _clear_vbox(vb: VBoxContainer) -> void:
	if vb == null:
		return
	for c in vb.get_children():
		vb.remove_child(c)
		c.queue_free()

func _section_header(parent: VBoxContainer, txt: String, col: Color = Color(1.0, 0.86, 0.38)) -> void:
	var l := Label.new()
	l.text = txt
	l.custom_minimum_size = Vector2(310, 22)
	l.add_theme_font_size_override("font_size", 13)
	l.add_theme_color_override("font_color", col)
	parent.add_child(l)

func _refresh_inventory() -> void:
	if player == null:
		return
	var gd := player._get_gamedata()
	var tier: Dictionary = gd.get_sword_for_level(player.sword_level)
	if inventory_label:
		inventory_label.text = "Espada: %s (Nv.%d)  •  Oro: %dg  •  Reliquias: %d/%d  •  Materiales: %d tipos" % [
			str(tier.get("name", "")), player.sword_level, player.gold,
			player.inventory_items.size(), gd.RELIC_DEFINITIONS.size(), player.materials.size()
		]

	_clear_vbox(inv_left_box)
	_clear_vbox(inv_right_box)
	if inv_left_box == null or inv_right_box == null:
		return

	# LEFT 1: Equipped Relics (3 Slots)
	_section_header(inv_left_box, "✦ EQUIPO RÚNICO ACTIVO (3 RANURAS)")
	var slot_names := [["grip", "Empuñadura"], ["rune", "Runa de Hoja"], ["relic", "Reliquia Abisal"]]
	for sn in slot_names:
		var slot_key := str(sn[0])
		var slot_lbl := str(sn[1])
		var eq_id := str(player.equipped.get(slot_key, ""))
		var row := HBoxContainer.new()
		row.custom_minimum_size = Vector2(320, 32)
		inv_left_box.add_child(row)

		var info := Label.new()
		info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		info.add_theme_font_size_override("font_size", 12)
		if eq_id == "":
			info.text = "• %s: [Vacío]" % slot_lbl
			info.add_theme_color_override("font_color", Color(0.62, 0.68, 0.78))
			row.add_child(info)
		else:
			var rdef: Dictionary = gd.get_relic_by_id(eq_id)
			info.text = "• %s: %s (%s)" % [slot_lbl, str(rdef.get("name", eq_id)), str(rdef.get("desc", ""))]
			info.clip_text = true
			info.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			info.add_theme_color_override("font_color", rdef.get("color", Color.WHITE))
			row.add_child(info)
			var ubtn := Button.new()
			ubtn.text = "Quitar"
			ubtn.custom_minimum_size = Vector2(58, 26)
			_style_button(ubtn, Color(0.95, 0.45, 0.45, 0.45), 0.88, 11)
			ubtn.pressed.connect(func(): player.unequip_slot(slot_key))
			row.add_child(ubtn)

	# LEFT 2: Consumables
	_section_header(inv_left_box, "❤ CONSUMIBLES DE BATALLA", Color(0.45, 0.92, 0.68))
	for cid in ["potion_hp", "elixir_xp"]:
		var cdef: Dictionary = gd.CONSUMABLE_DEFINITIONS[cid]
		var cnt := int(player.consumables.get(cid, 0))
		var cost := int(cdef["cost_gold"])
		var crow := HBoxContainer.new()
		crow.custom_minimum_size = Vector2(320, 30)
		inv_left_box.add_child(crow)

		var clbl := Label.new()
		clbl.text = "%s (x%d)" % [str(cdef["name"]), cnt]
		clbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		clbl.add_theme_font_size_override("font_size", 12)
		clbl.add_theme_color_override("font_color", cdef.get("color", Color.WHITE))
		crow.add_child(clbl)

		var use_b := Button.new()
		use_b.text = "Usar"
		use_b.custom_minimum_size = Vector2(54, 26)
		use_b.disabled = cnt <= 0
		_style_button(use_b, Color(0.35, 0.88, 0.58, 0.55), 0.9, 11)
		var c_id: String = str(cid)
		use_b.pressed.connect(func(): player.use_consumable(c_id))
		crow.add_child(use_b)

		var buy_b := Button.new()
		buy_b.text = "+1 (%dg)" % cost
		buy_b.custom_minimum_size = Vector2(72, 26)
		buy_b.disabled = player.gold < cost
		_style_button(buy_b, Color(0.98, 0.78, 0.28, 0.55), 0.9, 11)
		buy_b.pressed.connect(func(): player.buy_consumable(c_id))
		crow.add_child(buy_b)

	# LEFT 3: Owned Relics Bag
	_section_header(inv_left_box, "✦ BOLSA DE RELIQUIAS OBTENIDAS", Color(0.62, 0.86, 1.0))
	if player.inventory_items.is_empty():
		var empty_l := Label.new()
		empty_l.text = "Derrota monstruos/Malakor o forja reliquias a la derecha."
		empty_l.add_theme_font_size_override("font_size", 11)
		empty_l.add_theme_color_override("font_color", Color(0.65, 0.72, 0.84))
		inv_left_box.add_child(empty_l)
	else:
		for raw_id in player.inventory_items:
			var rid := str(raw_id)
			var rdef: Dictionary = gd.get_relic_by_id(rid)
			if rdef.is_empty():
				continue
			var slot := str(rdef.get("slot", ""))
			var is_eq := str(player.equipped.get(slot, "")) == rid
			var brow := HBoxContainer.new()
			brow.custom_minimum_size = Vector2(320, 30)
			inv_left_box.add_child(brow)

			var blbl := Label.new()
			blbl.text = "[%s] %s — %s" % [str(rdef.get("slot_label", "")), str(rdef["name"]), str(rdef["desc"])]
			blbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			blbl.clip_text = true
			blbl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
			blbl.add_theme_font_size_override("font_size", 11)
			blbl.add_theme_color_override("font_color", rdef.get("color", Color.WHITE))
			brow.add_child(blbl)

			var eq_b := Button.new()
			eq_b.text = "Equipado" if is_eq else "Equipar"
			eq_b.disabled = is_eq
			eq_b.custom_minimum_size = Vector2(72, 25)
			_style_button(eq_b, Color(0.38, 0.82, 1.0, 0.6), 0.9, 11)
			eq_b.pressed.connect(func(): player.equip_relic(rid))
			brow.add_child(eq_b)

	# RIGHT 1: Monster Materials
	_section_header(inv_right_box, "★ MATERIALES DE MONSTRUOS (BOTÍN)", Color(0.75, 0.88, 1.0))
	for mk in gd.MATERIAL_DEFINITIONS.keys():
		var mdef: Dictionary = gd.MATERIAL_DEFINITIONS[mk]
		var mcnt := int(player.materials.get(mk, 0))
		var mlbl := Label.new()
		mlbl.text = "• %s: %d" % [str(mdef["name"]), mcnt]
		mlbl.add_theme_font_size_override("font_size", 12)
		mlbl.add_theme_color_override("font_color", mdef["color"] if mcnt > 0 else Color(0.52, 0.58, 0.68))
		inv_right_box.add_child(mlbl)

	# RIGHT 2: Relic Forge Workshop
	_section_header(inv_right_box, "⚒ TALLER DE RELIQUIAS (FORJAR CON BOTÍN)", Color(1.0, 0.84, 0.36))
	for rdef in gd.RELIC_DEFINITIONS:
		var rid := str(rdef["id"])
		var owned := player.inventory_items.has(rid)
		var card := VBoxContainer.new()
		card.add_theme_constant_override("separation", 2)
		inv_right_box.add_child(card)

		var top_r := HBoxContainer.new()
		card.add_child(top_r)
		var rtitle := Label.new()
		rtitle.text = "%s (%s)" % [str(rdef["name"]), str(rdef["slot_label"])]
		rtitle.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		rtitle.add_theme_font_size_override("font_size", 12)
		rtitle.add_theme_color_override("font_color", rdef.get("color", Color.WHITE))
		top_r.add_child(rtitle)

		var cbtn := Button.new()
		cbtn.custom_minimum_size = Vector2(78, 25)
		cbtn.text = "Obtenida" if owned else "Forjar"
		cbtn.disabled = owned or not player.can_craft_relic(rid)
		_style_button(cbtn, Color(0.98, 0.78, 0.28, 0.65), 0.9, 11)
		cbtn.pressed.connect(func(): player.craft_relic(rid))
		top_r.add_child(cbtn)

		var req_parts: Array[String] = ["%dg" % int(rdef["recipe_gold"])]
		var rmats: Dictionary = rdef["recipe_mats"]
		for mk2 in rmats.keys():
			var mname := str(gd.get_material_by_id(mk2).get("name", mk2))
			req_parts.append("%d/%d %s" % [int(player.materials.get(mk2, 0)), int(rmats[mk2]), mname])
		var sub := Label.new()
		sub.text = "%s  |   Coste: %s" % [str(rdef["desc"]), ", ".join(req_parts)]
		sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		sub.add_theme_font_size_override("font_size", 10)
		sub.add_theme_color_override("font_color", Color(0.74, 0.82, 0.94))
		card.add_child(sub)

# --- POPULATE STATS & EVOLUTION CODEX ---
func _refresh_stats() -> void:
	if player == null or stats_label == null:
		return
	var gd := player._get_gamedata()
	var tier: Dictionary = gd.get_sword_for_level(player.sword_level)
	var st: Dictionary = player.stats
	var lines: Array[String] = []
	lines.append("═══ ATRIBUTOS DE COMBATE ═══")
	lines.append("Espada Actual: %s" % str(tier.get("name", "")))
	lines.append("Nivel de Espada: Nv. %d" % player.sword_level)
	lines.append("Modo Portador: %s" % ("Caballero 3D" if player.wielder_mode == "knight_wielder" else "Espada Viviente"))
	lines.append("Vida (HP): %d / %d" % [player.player_hp, player.player_max_hp])
	lines.append("Daño de Corte: %d" % int(st.get("damage", 18)))
	lines.append("Velocidad de Ataque: %.2fx" % float(st.get("attack_speed", 1.0)))
	lines.append("Prob. Crítico: %.1f%% (x%.2f)" % [float(st.get("crit_chance", 0.1)) * 100.0, float(st.get("crit_mult", 1.85))])
	lines.append("Alcance de Hoja: %.2f m" % float(st.get("range", 3.1)))
	lines.append("Vampirismo / Golpe: +%d HP" % int(st.get("life_on_hit", 0)))
	lines.append("Multiplicador EXP: x%.2f" % float(st.get("xp_mult", 1.0)))
	lines.append("Multiplicador Oro: x%.2f" % float(st.get("gold_mult", 1.0)))
	lines.append("Reducción de CD: %.0f%%" % (float(st.get("cd_reduction", 0.0)) * 100.0))
	lines.append("")
	lines.append("═══ PROGRESO DE CAMPAÑA ═══")
	lines.append("Oleada Actual: %d (%d/8)" % [player.wave, player.wave_kills])
	lines.append("Bajas Totales: %d" % player.kills)
	lines.append("Malakor Derrotados: %d" % player.bosses_defeated)
	lines.append("Oro Acumulado: %d" % player.gold)
	lines.append("")
	lines.append("Pasiva Activa — %s:" % str(tier.get("passive_name", "")))
	lines.append(str(tier.get("passive_description", "")))
	stats_label.text = "\n".join(lines)

	if codex_label:
		var clines: Array[String] = []
		clines.append("═══ RUTA DE LAS 8 EVOLUCIONES ═══")
		for t in gd.SWORD_EVOLUTIONS:
			var min_lv := int(t["min_level"])
			var mark := "★ ACTIVA" if str(t["id"]) == str(tier["id"]) else ("✓" if player.sword_level >= min_lv else "[Bloq.]")
			clines.append("%s  Nv.%d — %s" % [mark, min_lv, str(t["name"])])
			clines.append("    Pasiva: %s" % str(t["passive_name"]))
		clines.append("")
		clines.append("═══ MEJORAS DE FORJA ═══")
		for u in gd.UPGRADE_DEFINITIONS:
			var uk := str(u["key"])
			clines.append("• %s: Nv.%d/10 (%s)" % [str(u["name"]), int(player.upgrades.get(uk, 0)), str(u["desc"])])
		codex_label.text = "\n".join(clines)

# Legacy signal handlers kept for scene connections
func _on_auto_hunt_pressed() -> void:
	if player: player.toggle_auto_hunt()
func _on_mode_pressed() -> void:
	if player: player.toggle_wielder_mode()
func _on_level_up_pressed() -> void:
	if player: player.jump_to_level(player.sword_level + 1)
func _on_upgrade_sharpness_pressed() -> void: _on_upgrade_pressed("sharpness", 25)
func _on_upgrade_swiftness_pressed() -> void: _on_upgrade_pressed("swiftness", 30)
func _on_upgrade_crit_pressed() -> void: _on_upgrade_pressed("criticalMastery", 35)
func _on_upgrade_vamp_pressed() -> void: _on_upgrade_pressed("vampirism", 40)
func _on_upgrade_soul_pressed() -> void: _on_upgrade_pressed("soulMagnet", 30)
func _on_upgrade_size_pressed() -> void: _on_upgrade_pressed("bladeSize", 45)

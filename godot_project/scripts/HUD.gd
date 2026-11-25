extends CanvasLayer

# Keep legacy onready paths optional for scene compatibility
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

# New UI refs
var ui_root: Control
var hp_bar_new: ProgressBar
var hp_text: Label
var xp_bar_new: ProgressBar
var xp_text: Label
var lvl_text: Label
var sword_text: Label
var gold_text: Label
var wave_text: Label
var objective_text: Label
var objective_sub: Label
var boss_panel: Panel
var boss_bar: ProgressBar
var boss_label: Label
var game_over_panel: Panel
var pause_panel: Panel
var cd_nodes: Dictionary = {}
var forge_buttons: Dictionary = {}
var combo_label: Label
var combo_timer: float = 0.0
var combo_count: int = 0
var minimap_panel: Control
var minimap_dots: Array = []
var branding_label: Label
var settings_panel: Panel
var inventory_panel: Panel
var stats_panel: Panel
var stats_label: RichTextLabel
var inventory_label: RichTextLabel

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

func _clear_legacy_children() -> void:
	for c in ui_root.get_children():
		c.queue_free()

func _build_ui() -> void:
	_build_top_left()
	_build_top_center()
	_build_top_right()
	_build_objective()
	_build_right_forge()
	_build_bottom_skills()
	_build_log()
	_build_boss_bar()
	_build_game_over()
	_build_pause()
	_build_combo()
	_build_minimap()
	_build_branding()
	_build_settings_panel()
	_build_inventory_panel()
	_build_stats_panel()

func _panel_style(bg: Color, border: Color, radius: int = 10, border_w: int = 1) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	return sb

func _label(parent: Node, text: String, pos: Vector2, size: Vector2, fs: int = 14, color: Color = Color.WHITE, align: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.size = size
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", fs)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0,0,0,0.75))
	l.add_theme_constant_override("outline_size", 3)
	parent.add_child(l)
	return l

func _build_top_left() -> void:
	var panel := Panel.new()
	panel.position = Vector2(16, 12)
	panel.size = Vector2(360, 86)
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.06,0.08,0.16,0.72), Color(0.35,0.65,1.0,0.35), 14))
	ui_root.add_child(panel)

	# portrait circle
	var portrait := Panel.new()
	portrait.position = Vector2(8, 8)
	portrait.size = Vector2(70, 70)
	portrait.add_theme_stylebox_override("panel", _panel_style(Color(0.15,0.2,0.35,0.9), Color(0.45,0.8,1.0,0.8), 35, 2))
	panel.add_child(portrait)
	var picon := Label.new()
	picon.text = "⚔"
	picon.position = Vector2(0,0); picon.size = Vector2(70,70)
	picon.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	picon.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	picon.add_theme_font_size_override("font_size", 30)
	portrait.add_child(picon)

	lvl_text = _label(panel, "Nv. 1", Vector2(88, 6), Vector2(120, 24), 22, Color(1,0.95,0.7))
	sword_text = _label(panel, "Espada de Madera Ancestral", Vector2(150, 8), Vector2(200, 20), 13, Color(0.85,0.92,1.0,0.95))

	_label(panel, "❤", Vector2(88, 34), Vector2(20, 18), 14, Color(0.3,1.0,0.5))
	hp_bar_new = ProgressBar.new()
	hp_bar_new.position = Vector2(108, 36); hp_bar_new.size = Vector2(170, 14)
	hp_bar_new.show_percentage = false
	hp_bar_new.add_theme_stylebox_override("background", _panel_style(Color(0.12,0.05,0.08,0.9), Color(1,1,1,0.08), 6))
	hp_bar_new.add_theme_stylebox_override("fill", _panel_style(Color(0.2,0.85,0.35,0.95), Color(0.6,1,0.6,0.4), 6))
	panel.add_child(hp_bar_new)
	hp_text = _label(panel, "220 / 220", Vector2(282, 33), Vector2(70, 18), 11, Color(0.9,1,0.9), HORIZONTAL_ALIGNMENT_RIGHT)

	_label(panel, "EXP", Vector2(88, 56), Vector2(30, 16), 11, Color(0.6,0.85,1.0))
	xp_bar_new = ProgressBar.new()
	xp_bar_new.position = Vector2(120, 58); xp_bar_new.size = Vector2(158, 10)
	xp_bar_new.show_percentage = false
	xp_bar_new.add_theme_stylebox_override("background", _panel_style(Color(0.05,0.08,0.14,0.9), Color(1,1,1,0.08), 5))
	xp_bar_new.add_theme_stylebox_override("fill", _panel_style(Color(0.25,0.65,1.0,0.95), Color(0.6,0.9,1.0,0.4), 5))
	panel.add_child(xp_bar_new)
	xp_text = _label(panel, "0%", Vector2(282, 54), Vector2(70, 16), 11, Color(0.75,0.9,1.0), HORIZONTAL_ALIGNMENT_RIGHT)

func _build_top_center() -> void:
	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	panel.position = Vector2(-170, 12)
	panel.size = Vector2(340, 44)
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.06,0.08,0.16,0.65), Color(0.4,0.6,1.0,0.25), 12))
	ui_root.add_child(panel)
	gold_text = _label(panel, "🪙 60", Vector2(20, 6), Vector2(120, 32), 20, Color(1.0,0.86,0.35))
	wave_text = _label(panel, "💀 Oleada 1 / 8", Vector2(150, 6), Vector2(170, 32), 18, Color(0.9,0.92,1.0))

func _build_top_right() -> void:
	var panel := HBoxContainer.new()
	panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	panel.offset_left = -430.0
	panel.offset_right = -16.0
	panel.offset_top = 14.0
	panel.offset_bottom = 54.0
	panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	panel.add_theme_constant_override("separation", 8)
	ui_root.add_child(panel)
	for txt in ["Ajustes", "Pausa", "Inventario", "Estadísticas"]:
		var b := Button.new()
		b.text = txt
		b.custom_minimum_size = Vector2(92, 36)
		_style_button(b)
		panel.add_child(b)
		if txt == "Pausa": b.pressed.connect(_toggle_pause)
		if txt == "Ajustes": b.pressed.connect(_toggle_settings)
		if txt == "Inventario": b.pressed.connect(_toggle_inventory)
		if txt == "Estadísticas": b.pressed.connect(_toggle_stats)

func _build_objective() -> void:
	var panel := Panel.new()
	panel.position = Vector2(16, 112)
	panel.size = Vector2(250, 88)
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.05,0.07,0.14,0.62), Color(1.0,0.75,0.2,0.3), 12))
	ui_root.add_child(panel)
	_label(panel, "⚠ Objetivo Actual", Vector2(12, 8), Vector2(220, 20), 13, Color(1.0,0.82,0.35))
	objective_sub = _label(panel, "Elimina 8 monstruos para\navanzar a la siguiente oleada.", Vector2(12, 30), Vector2(226, 34), 11, Color(0.86,0.9,0.98,0.9))
	objective_text = _label(panel, "0 / 8", Vector2(12, 64), Vector2(100, 20), 18, Color(1.0,0.9,0.45))

func _build_right_forge() -> void:
	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_CENTER_RIGHT)
	panel.offset_left = -236.0
	panel.offset_right = -16.0
	panel.offset_top = -200.0
	panel.offset_bottom = 140.0
	panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	panel.grow_vertical = Control.GROW_DIRECTION_BOTH
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.05,0.07,0.14,0.68), Color(0.45,0.7,1.0,0.22), 12))
	ui_root.add_child(panel)
	_label(panel, "⚒ Forja", Vector2(12, 8), Vector2(120, 24), 18, Color(1.0,0.86,0.4))
	var upgrades = [
		["sharpness","Afilar","25"],["swiftness","Ligereza","30"],["criticalMastery","Crítico","35"],
		["vampirism","Vampiro","40"],["soulMagnet","Almas","30"],["bladeSize","Colosal","45"]
	]
	var y := 40
	for u in upgrades:
		var btn := Button.new()
		btn.position = Vector2(10, y)
		btn.size = Vector2(200, 34)
		btn.text = "%s  Lv.0  %sg" % [u[1], u[2]]
		_style_button(btn)
		var key = u[0]; var base = int(u[2])
		btn.pressed.connect(func(): _on_upgrade_pressed(key, base))
		panel.add_child(btn)
		forge_buttons[key] = btn
		y += 40
	var mejorar := Button.new()
	mejorar.name = "MejorarBtn"
	mejorar.position = Vector2(12, 284)
	mejorar.size = Vector2(196, 38)
	mejorar.text = "Mejorar"
	var mnormal := _panel_style(Color(0.2,0.55,0.95,0.95), Color(0.5,0.85,1.0,0.9), 10)
	var mhover := _panel_style(Color(0.3,0.65,1.0,0.98), Color(0.7,0.92,1.0,1.0), 10)
	mejorar.add_theme_stylebox_override("normal", mnormal)
	mejorar.add_theme_stylebox_override("hover", mhover)
	mejorar.add_theme_stylebox_override("pressed", mnormal)
	mejorar.add_theme_stylebox_override("focus", mhover)
	mejorar.add_theme_color_override("font_color", Color(1,1,1,1))
	mejorar.add_theme_font_size_override("font_size", 18)
	mejorar.pressed.connect(_on_mejorar_pressed)
	panel.add_child(mejorar)

func _build_bottom_skills() -> void:
	var panel := HBoxContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	panel.offset_left = -320.0
	panel.offset_right = 320.0
	panel.offset_top = -132.0
	panel.offset_bottom = -10.0
	panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	panel.alignment = BoxContainer.ALIGNMENT_CENTER
	panel.add_theme_constant_override("separation", 16)
	ui_root.add_child(panel)
	var defs = [
		["Q","Torbellino","whirlwind","res://assets/ui/skill_q.png"],
		["E","Onda Cortante","swordWave","res://assets/ui/skill_e.png"],
		["R","Lluvia de Espadas","ultimate","res://assets/ui/skill_r.png"],
		["Shift","Dash","dash","res://assets/ui/skill_shift.png"],
	]
	for s in defs:
		var wrap := VBoxContainer.new()
		wrap.custom_minimum_size = Vector2(120, 118)
		wrap.add_theme_constant_override("separation", 2)
		panel.add_child(wrap)
		var box := Panel.new()
		box.custom_minimum_size = Vector2(120, 86)
		box.add_theme_stylebox_override("panel", _panel_style(Color(0.06,0.12,0.24,0.82), Color(0.35,0.7,1.0,0.65), 14))
		wrap.add_child(box)
		var icon := TextureRect.new()
		icon.texture = load(s[3])
		icon.position = Vector2(24, 8)
		icon.size = Vector2(72, 56)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		box.add_child(icon)
		var key_badge := Panel.new()
		key_badge.position = Vector2(4,4)
		key_badge.size = Vector2(28 if s[0]!="Shift" else 42, 22)
		key_badge.add_theme_stylebox_override("panel", _panel_style(Color(0.1,0.18,0.35,0.95), Color(0.5,0.8,1.0,0.7), 6))
		box.add_child(key_badge)
		var keyl := _label(key_badge, s[0], Vector2(0,2), key_badge.size, 12, Color(0.95,0.98,1.0), HORIZONTAL_ALIGNMENT_CENTER)
		var cdl := _label(box, "Listo", Vector2(0,64), Vector2(120,18), 12, Color(0.5,1.0,0.6), HORIZONTAL_ALIGNMENT_CENTER)
		var namel := _label(wrap, s[1], Vector2(0,0), Vector2(120,18), 12, Color(0.82,0.9,1.0,0.95), HORIZONTAL_ALIGNMENT_CENTER)
		namel.custom_minimum_size = Vector2(120, 18)
		namel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cd_nodes[s[2]] = {"panel": box, "cd": cdl, "icon": icon}

func _build_log() -> void:
	var panel := Panel.new()
	panel.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	panel.offset_left = 16.0
	panel.offset_right = 336.0
	panel.offset_top = -220.0
	panel.offset_bottom = -90.0
	panel.add_theme_stylebox_override("panel", _panel_style(Color(0.04,0.05,0.09,0.45), Color(1,1,1,0.08), 10))
	ui_root.add_child(panel)
	log_label = RichTextLabel.new()
	log_label.position = Vector2(10,10); log_label.size = Vector2(300,110)
	log_label.bbcode_enabled = false
	log_label.scroll_active = false
	log_label.add_theme_font_size_override("normal_font_size", 12)
	log_label.add_theme_color_override("default_color", Color(0.85,0.9,1.0,0.85))
	panel.add_child(log_label)

func _build_boss_bar() -> void:
	boss_panel = Panel.new()
	boss_panel.visible = false
	boss_panel.set_anchors_preset(Control.PRESET_CENTER_TOP)
	boss_panel.offset_left = -260.0
	boss_panel.offset_right = 260.0
	boss_panel.offset_top = 76.0
	boss_panel.offset_bottom = 122.0
	boss_panel.grow_horizontal = Control.GROW_DIRECTION_BOTH
	boss_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.12,0.03,0.03,0.72), Color(1,0.35,0.25,0.5), 10))
	ui_root.add_child(boss_panel)
	boss_label = _label(boss_panel, "BOSS", Vector2(0,2), Vector2(520,18), 13, Color(1,0.8,0.8), HORIZONTAL_ALIGNMENT_CENTER)
	boss_bar = ProgressBar.new()
	boss_bar.position = Vector2(16,24); boss_bar.size = Vector2(488,12)
	boss_bar.show_percentage = false
	boss_bar.add_theme_stylebox_override("background", _panel_style(Color(0.15,0.05,0.05,0.9), Color(1,1,1,0.08), 4))
	boss_bar.add_theme_stylebox_override("fill", _panel_style(Color(0.9,0.15,0.2,0.95), Color(1,0.5,0.5,0.4), 4))
	boss_panel.add_child(boss_bar)

func _build_game_over() -> void:
	game_over_panel = Panel.new()
	game_over_panel.visible = false
	game_over_panel.set_anchors_preset(Control.PRESET_CENTER)
	game_over_panel.position = Vector2(-220,-90)
	game_over_panel.size = Vector2(440,180)
	game_over_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.03,0.03,0.06,0.88), Color(1.0,0.4,0.3,0.5), 14))
	ui_root.add_child(game_over_panel)
	_label(game_over_panel, "HAS CAÍDO", Vector2(0,30), Vector2(440,36), 34, Color(1.0,0.85,0.8), HORIZONTAL_ALIGNMENT_CENTER)
	_label(game_over_panel, "La Forja Ancestral puede restaurarte", Vector2(0,72), Vector2(440,24), 14, Color(0.85,0.88,0.95,0.9), HORIZONTAL_ALIGNMENT_CENTER)
	var btn := Button.new()
	btn.text = "Reaparecer"
	btn.position = Vector2(150,120); btn.size = Vector2(140,40)
	_style_button(btn)
	btn.pressed.connect(_on_respawn_pressed)
	game_over_panel.add_child(btn)

func _build_pause() -> void:
	pause_panel = Panel.new()
	pause_panel.visible = false
	pause_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	pause_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.02,0.02,0.04,0.72), Color(0,0,0,0), 0, 0))
	ui_root.add_child(pause_panel)
	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_CENTER)
	box.position = Vector2(-140,-120); box.size = Vector2(280,240)
	box.add_theme_constant_override("separation", 10)
	pause_panel.add_child(box)
	var title := _label(box, "PAUSA", Vector2(0,0), Vector2(280,40), 34, Color(1,0.9,0.7), HORIZONTAL_ALIGNMENT_CENTER)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for pair in [["Continuar", _on_resume_pressed], ["Guardar", _on_save_pressed], ["Salir", _on_quit_pressed]]:
		var b := Button.new(); b.text = pair[0]; b.custom_minimum_size = Vector2(280,42); _style_button(b); b.pressed.connect(pair[1]); box.add_child(b)

func _build_combo() -> void:
	combo_label = Label.new()
	combo_label.name = "ComboLabel"
	combo_label.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	combo_label.offset_left = -420.0
	combo_label.offset_right = -30.0
	combo_label.offset_top = 430.0
	combo_label.offset_bottom = 500.0
	combo_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	combo_label.add_theme_font_size_override("font_size", 52)
	combo_label.add_theme_color_override("font_color", Color(1.0, 0.45, 0.15, 0.95))
	combo_label.add_theme_color_override("font_outline_color", Color(0.1,0.02,0.0,0.9))
	combo_label.add_theme_constant_override("outline_size", 8)
	combo_label.visible = false
	add_child(combo_label)

func _style_button(b: Button) -> void:
	var normal := _panel_style(Color(0.12,0.16,0.24,0.78), Color(0.45,0.65,0.95,0.28), 8)
	var hover := _panel_style(Color(0.2,0.28,0.42,0.88), Color(0.6,0.8,1.0,0.45), 8)
	var pressed := _panel_style(Color(0.08,0.12,0.18,0.9), Color(0.4,0.6,0.9,0.4), 8)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("focus", hover)
	b.add_theme_color_override("font_color", Color(0.92,0.95,1.0,0.95))
	b.add_theme_font_size_override("font_size", 12)

func connect_player(p: Player) -> void:
	player = p
	player.hp_changed.connect(_on_hp)
	player.xp_changed.connect(_on_xp)
	player.gold_changed.connect(_on_gold)
	player.kills_changed.connect(_on_kills)
	player.wave_changed.connect(_on_wave)
	player.evolution_changed.connect(_on_evo)
	player.log_added.connect(_on_log)
	if player.has_signal("player_died"): player.player_died.connect(_on_player_died)
	if player.has_signal("cooldowns_changed"): player.cooldowns_changed.connect(func(_c): _update_cooldowns())
	_on_hp(player.player_hp, player.player_max_hp)
	_on_xp(player.current_xp, GameData.get_xp_required(player.sword_level), player.sword_level)
	_on_gold(player.gold)
	_on_kills(player.kills)
	_on_wave(player.wave, player.wave_kills)
	if boss_panel: boss_panel.visible = false
	if game_over_panel: game_over_panel.visible = false
	if pause_panel: pause_panel.visible = false

func _on_hp(cur: int, max_hp: int) -> void:
	if hp_bar_new:
		hp_bar_new.max_value = max_hp; hp_bar_new.value = cur
		var ratio := float(cur) / float(maxi(1,max_hp))
		var fill: StyleBoxFlat = hp_bar_new.get_theme_stylebox("fill")
		if fill:
			fill.bg_color = Color(0.2,0.85,0.35,0.95) if ratio > 0.5 else (Color(0.95,0.75,0.2,0.95) if ratio > 0.25 else Color(0.9,0.18,0.25,0.95))
	if hp_text: hp_text.text = "%d / %d" % [cur, max_hp]

func _on_xp(cur: int, req: int, level: int) -> void:
	if xp_bar_new: xp_bar_new.max_value = req; xp_bar_new.value = cur
	var pct := int((float(cur) / float(maxi(1,req))) * 100.0)
	if xp_text: xp_text.text = "%d%%" % pct
	if lvl_text: lvl_text.text = "Nv. %d" % level
	var tier = GameData.get_sword_for_level(level)
	if sword_text: sword_text.text = str(tier["name"])
	_update_forge_buttons()

func _on_gold(g: int) -> void:
	if gold_text: gold_text.text = "🪙 %d" % g
	_update_forge_buttons()

func _on_kills(_k: int) -> void:
	combo_count += 1
	combo_timer = 2.5
	if combo_label:
		combo_label.text = "%d Combo!" % combo_count
		combo_label.visible = true

func _on_wave(w: int, wk: int) -> void:
	if wave_text: wave_text.text = "💀 Oleada %d / 8" % w
	if objective_text: objective_text.text = "%d / 8" % wk
	if objective_sub: objective_sub.text = "Elimina 8 monstruos para\navanzar a la siguiente oleada."

func _on_evo(tier: Dictionary) -> void:
	_on_log("¡EVOLUCIÓN! %s" % str(tier["name"]), "evolution")
	if combo_label:
		combo_label.text = "¡EVOLUCIÓN!"
		combo_label.add_theme_color_override("font_color", Color(1.0,0.9,0.4,0.98))
		combo_label.visible = true
		combo_timer = 2.2

func _on_log(text: String, kind: String) -> void:
	var prefix := ""
	match kind:
		"evolution": prefix = "[EVO] "
		"skill": prefix = "[SKILL] "
		"upgrade": prefix = "[FORJA] "
		"boss": prefix = "[!] "
		"levelup": prefix = "[UP] "
	log_lines.push_front(prefix + text)
	if log_lines.size() > 5: log_lines.resize(5)
	if log_label: log_label.text = "\n".join(log_lines)

func _update_forge_buttons() -> void:
	if player == null: return
	var base_costs = {"sharpness":25,"swiftness":30,"criticalMastery":35,"vampirism":40,"soulMagnet":30,"bladeSize":45}
	var names = {"sharpness":"Afilar","swiftness":"Ligereza","criticalMastery":"Crítico","vampirism":"Vampiro","soulMagnet":"Almas","bladeSize":"Colosal"}
	for k in forge_buttons.keys():
		var b: Button = forge_buttons[k]
		var lvl = int(player.upgrades.get(k, 0))
		var cost = int(round(base_costs[k] * pow(1.45, lvl)))
		b.text = "%s  Lv.%d  %dg" % [names[k], lvl, cost]
		b.disabled = player.gold < cost or lvl >= 10

func _on_upgrade_pressed(key: String, base_cost: int) -> void:
	if player: player.buy_upgrade(key, base_cost)

func _on_mejorar_pressed() -> void:
	if player == null: return
	var base_costs = {"sharpness":25,"swiftness":30,"criticalMastery":35,"vampirism":40,"soulMagnet":30,"bladeSize":45}
	var best_key := ""
	var best_cost := 999999
	for k in base_costs.keys():
		var lvl = int(player.upgrades.get(k, 0))
		if lvl >= 10: continue
		var cost = int(round(base_costs[k] * pow(1.45, lvl)))
		if player.gold >= cost and cost < best_cost:
			best_cost = cost
			best_key = k
	if best_key != "":
		player.buy_upgrade(best_key, int(base_costs[best_key]))
	else:
		_on_log("No hay mejora asequible", "upgrade")

func _process(delta: float) -> void:
	_update_boss_bar()
	_update_cooldowns()
	if combo_timer > 0.0:
		combo_timer -= delta
		if combo_timer <= 0.0 and combo_label:
			combo_label.visible = false

func _update_boss_bar() -> void:
	if boss_panel == null: return
	var boss: Node3D = null
	for e in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(e) and e.get("is_boss") == true and int(e.get("hp")) > 0:
			boss = e; break
	if boss:
		boss_panel.visible = true
		boss_bar.max_value = int(boss.get("max_hp"))
		boss_bar.value = int(boss.get("hp"))
		var bname = str(boss.def.get("name", "BOSS")) if boss.get("def") != null else "BOSS"
		boss_label.text = bname
	else:
		boss_panel.visible = false

func _update_cooldowns() -> void:
	if player == null: return
	var cds = player.get("cooldowns")
	if cds == null: return
	for id in cd_nodes.keys():
		var v = float(cds.get(id, 0.0))
		var node = cd_nodes[id]
		var lbl: Label = node["cd"]
		var box: Panel = node["panel"]
		if v > 0.05:
			lbl.text = "%.1fs" % v
			lbl.add_theme_color_override("font_color", Color(1.0,0.6,0.5,0.95))
			box.modulate = Color(0.7,0.7,0.8,0.9)
		else:
			lbl.text = "Listo"
			lbl.add_theme_color_override("font_color", Color(0.5,1.0,0.6,0.95))
			box.modulate = Color(1,1,1,1)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_toggle_pause()

func _toggle_pause() -> void:
	if game_over_panel and game_over_panel.visible: return
	var paused := not get_tree().paused
	get_tree().paused = paused
	if pause_panel: pause_panel.visible = paused

func _on_resume_pressed() -> void:
	get_tree().paused = false
	if pause_panel: pause_panel.visible = false

func _on_save_pressed() -> void:
	if player and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(player)
		_on_log("Partida guardada.", "upgrade")

func _on_quit_pressed() -> void:
	if player and has_node("/root/SaveSystem"):
		get_node("/root/SaveSystem").save_game(player)
	get_tree().quit()

func _on_player_died() -> void:
	if game_over_panel: game_over_panel.visible = true

func _on_respawn_pressed() -> void:
	if player and player.has_method("respawn_player"): player.respawn_player()
	if game_over_panel: game_over_panel.visible = false

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


func _build_minimap() -> void:
	minimap_panel = Panel.new()
	minimap_panel.name = "Minimap"
	minimap_panel.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	minimap_panel.offset_left = -192.0
	minimap_panel.offset_right = -22.0
	minimap_panel.offset_top = 84.0
	minimap_panel.offset_bottom = 254.0
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.04,0.07,0.16,0.72)
	st.border_color = Color(0.45,0.62,0.95,0.65)
	st.set_border_width_all(2)
	st.set_corner_radius_all(85)
	minimap_panel.add_theme_stylebox_override("panel", st)
	add_child(minimap_panel)
	var n := Label.new()
	n.text = "N"
	n.position = Vector2(79, 4)
	n.add_theme_font_size_override("font_size", 14)
	n.add_theme_color_override("font_color", Color(0.9,0.95,1.0))
	minimap_panel.add_child(n)
	# center player dot
	var p := ColorRect.new()
	p.color = Color(0.3,0.8,1.0,1.0)
	p.position = Vector2(82,82)
	p.size = Vector2(6,6)
	minimap_panel.add_child(p)
	# precreate dots
	for i in range(12):
		var d := ColorRect.new()
		d.color = Color(1.0,0.3,0.3,0.9)
		d.size = Vector2(5,5)
		d.visible = false
		minimap_panel.add_child(d)
		minimap_dots.append(d)

func _update_minimap() -> void:
	if minimap_panel == null or not is_instance_valid(minimap_panel): return
	if player == null or not is_instance_valid(player): return
	var center := Vector2(85,85)
	var radius := 70.0
	var range_world := 28.0
	var monsters := get_tree().get_nodes_in_group("monsters")
	var idx := 0
	for m in monsters:
		if idx >= minimap_dots.size(): break
		if not is_instance_valid(m): continue
		var rel: Vector3 = m.global_position - player.global_position
		var v := Vector2(rel.x, rel.z) / range_world * radius
		if v.length() > radius:
			v = v.normalized() * radius
		var d: ColorRect = minimap_dots[idx]
		d.visible = true
		d.position = center + v - d.size/2
		d.color = Color(0.85,0.2,0.2,0.95) if not m.is_boss else Color(1.0,0.6,0.1,1.0)
		idx += 1
	for i in range(idx, minimap_dots.size()):
		minimap_dots[i].visible = false

func _build_branding() -> void:
	branding_label = Label.new()
	branding_label.name = "Branding"
	branding_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	branding_label.offset_left = 24.0
	branding_label.offset_right = 390.0
	branding_label.offset_top = -86.0
	branding_label.offset_bottom = -10.0
	branding_label.text = "STUDIO LEXAIR\nEspada Anime Isekai\nForja de Almas 3D"
	branding_label.add_theme_font_size_override("font_size", 14)
	branding_label.add_theme_color_override("font_color", Color(0.8,0.9,1.0,0.85))
	add_child(branding_label)


func _build_overlay_panel(title: String, size: Vector2) -> Panel:
	var p := Panel.new()
	p.visible = false
	p.set_anchors_preset(Control.PRESET_CENTER)
	p.offset_left = -size.x / 2
	p.offset_right = size.x / 2
	p.offset_top = -size.y / 2
	p.offset_bottom = size.y / 2
	p.grow_horizontal = Control.GROW_DIRECTION_BOTH
	p.grow_vertical = Control.GROW_DIRECTION_BOTH
	p.add_theme_stylebox_override("panel", _panel_style(Color(0.06,0.08,0.14,0.95), Color(0.45,0.7,1.0,0.35), 14))
	add_child(p)
	var t := _label(p, title, Vector2(20, 14), Vector2(size.x - 40, 30), 24, Color(1.0,0.9,0.55))
	var close := Button.new()
	close.text = "X"
	close.position = Vector2(size.x - 46, 12)
	close.size = Vector2(34, 34)
	_style_button(close)
	close.pressed.connect(func(): p.visible = false)
	p.add_child(close)
	return p

func _build_settings_panel() -> void:
	settings_panel = _build_overlay_panel("Ajustes", Vector2(520, 360))
	var y := 64.0
	var info := _label(settings_panel, "Calidad / Audio (funcional básico)", Vector2(20,y), Vector2(480,24), 14, Color(0.8,0.9,1.0))
	y += 36
	for opt in [["Calidad Baja","low"],["Calidad Media","medium"],["Calidad Alta","high"]]:
		var b := Button.new()
		b.text = opt[0]
		b.position = Vector2(20, y)
		b.size = Vector2(150, 38)
		_style_button(b)
		var q = opt[1]
		b.pressed.connect(func(): _apply_quality(q))
		settings_panel.add_child(b)
		y += 0
		# place horizontally by changing x
		b.position.x = 20 + (["low","medium","high"].find(opt[1]) * 160)
		b.position.y = 100
	y = 160
	var audio_lbl := _label(settings_panel, "Audio: ON/OFF", Vector2(20,160), Vector2(200,24), 16, Color(0.9,0.95,1.0))
	var audio_btn := Button.new()
	audio_btn.text = "Alternar Audio"
	audio_btn.position = Vector2(20, 190)
	audio_btn.size = Vector2(180, 38)
	_style_button(audio_btn)
	audio_btn.pressed.connect(_toggle_audio)
	settings_panel.add_child(audio_btn)
	var note := _label(settings_panel, "Nota: la configuración se aplica en runtime.\nAudio completo y más opciones se ampliarán.", Vector2(20,250), Vector2(460,60), 13, Color(0.75,0.82,0.92,0.9))
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

func _apply_quality(q: String) -> void:
	var vp := get_viewport()
	if vp == null: return
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
	_on_log("Calidad aplicada: %s" % q, "upgrade")

var _audio_muted := false
func _toggle_audio() -> void:
	_audio_muted = not _audio_muted
	AudioServer.set_bus_mute(0, _audio_muted)
	_on_log("Audio: %s" % ("OFF" if _audio_muted else "ON"), "upgrade")

func _build_inventory_panel() -> void:
	inventory_panel = _build_overlay_panel("Inventario", Vector2(560, 420))
	inventory_label = RichTextLabel.new()
	inventory_label.position = Vector2(20, 56)
	inventory_label.size = Vector2(520, 340)
	inventory_label.bbcode_enabled = false
	inventory_label.add_theme_font_size_override("normal_font_size", 15)
	inventory_label.add_theme_color_override("default_color", Color(0.9,0.94,1.0))
	inventory_panel.add_child(inventory_label)

func _build_stats_panel() -> void:
	stats_panel = _build_overlay_panel("Estadísticas", Vector2(560, 420))
	stats_label = RichTextLabel.new()
	stats_label.position = Vector2(20, 56)
	stats_label.size = Vector2(520, 340)
	stats_label.bbcode_enabled = false
	stats_label.add_theme_font_size_override("normal_font_size", 15)
	stats_label.add_theme_color_override("default_color", Color(0.9,0.94,1.0))
	stats_panel.add_child(stats_label)

func _toggle_settings() -> void:
	if settings_panel: settings_panel.visible = not settings_panel.visible
	if inventory_panel: inventory_panel.visible = false
	if stats_panel: stats_panel.visible = false

func _toggle_inventory() -> void:
	if inventory_panel:
		inventory_panel.visible = not inventory_panel.visible
		if inventory_panel.visible: _refresh_inventory()
	if settings_panel: settings_panel.visible = false
	if stats_panel: stats_panel.visible = false

func _toggle_stats() -> void:
	if stats_panel:
		stats_panel.visible = not stats_panel.visible
		if stats_panel.visible: _refresh_stats()
	if settings_panel: settings_panel.visible = false
	if inventory_panel: inventory_panel.visible = false

func _refresh_inventory() -> void:
	if player == null or inventory_label == null: return
	var tier = GameData.get_sword_for_level(player.sword_level)
	var lines := []
	lines.append("Espada actual: %s (Nv.%d)" % [str(tier.get("name","")), player.sword_level])
	lines.append("Oro: %d" % player.gold)
	lines.append("Kills: %d  |  Oleada: %d" % [player.kills, player.wave])
	lines.append("")
	lines.append("Mejoras:")
	var base_costs = {"sharpness":25,"swiftness":30,"criticalMastery":35,"vampirism":40,"soulMagnet":30,"bladeSize":45}
	var names = {"sharpness":"Afilar","swiftness":"Ligereza","criticalMastery":"Crítico","vampirism":"Vampiro","soulMagnet":"Almas","bladeSize":"Colosal"}
	for k in names.keys():
		var lvl = int(player.upgrades.get(k,0))
		var cost = int(round(base_costs[k] * pow(1.45, lvl)))
		lines.append("- %s: Lv.%d/10 (siguiente: %dg)" % [names[k], lvl, cost])
	inventory_label.text = "\n".join(lines)

func _refresh_stats() -> void:
	if player == null or stats_label == null: return
	var tier = GameData.get_sword_for_level(player.sword_level)
	var lines := []
	lines.append("Nivel espada: %d" % player.sword_level)
	lines.append("HP: %d / %d" % [player.player_hp, player.player_max_hp])
	lines.append("Daño: %d" % player.damage)
	lines.append("Velocidad: %.2f" % player.speed)
	lines.append("Crit: %.1f%%" % (player.crit_chance * 100.0))
	lines.append("Vampirismo: %.1f%%" % (player.lifesteal * 100.0))
	lines.append("Oro: %d | Kills: %d | Oleada: %d" % [player.gold, player.kills, player.wave])
	lines.append("Espada: %s" % str(tier.get("name","")))
	lines.append("Efecto especial: %s" % str(tier.get("special_effect","none")))
	stats_label.text = "\n".join(lines)

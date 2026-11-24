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

func connect_player(p: Player) -> void:
	player = p
	player.hp_changed.connect(_on_hp)
	player.xp_changed.connect(_on_xp)
	player.gold_changed.connect(_on_gold)
	player.kills_changed.connect(_on_kills)
	player.wave_changed.connect(_on_wave)
	player.evolution_changed.connect(_on_evo)
	player.log_added.connect(_on_log)
	# init
	_on_hp(player.player_hp, player.player_max_hp)
	_on_xp(player.current_xp, GameData.get_xp_required(player.sword_level), player.sword_level)
	_on_gold(player.gold)
	_on_kills(player.kills)
	_on_wave(player.wave, player.wave_kills)
	evo_banner.visible = false

func _on_hp(cur: int, max_hp: int) -> void:
	hp_bar.max_value = max_hp
	hp_bar.value = cur
	hp_label.text = "VIDA: %d/%d" % [cur, max_hp]

func _on_xp(cur: int, req: int, level: int) -> void:
	xp_bar.max_value = req
	xp_bar.value = cur
	xp_label.text = "EXP: %d/%d" % [cur, req]
	level_label.text = "NV. %d" % level
	var tier = GameData.get_sword_for_level(level)
	sword_name_label.text = str(tier["name"])

func _on_gold(g: int) -> void:
	gold_label.text = "Oro: %d" % g

func _on_kills(k: int) -> void:
	kills_label.text = "Bajas: %d" % k

func _on_wave(w: int, wk: int) -> void:
	wave_label.text = "Oleada %d (%d/8)" % [w, wk]

func _on_evo(tier: Dictionary) -> void:
	evo_banner.visible = true
	evo_banner_label.text = "¡EVOLUCIÓN! %s" % str(tier["name"])
	var tw := create_tween()
	tw.tween_interval(4.0)
	tw.tween_callback(func(): evo_banner.visible = false)

func _on_log(text: String, kind: String) -> void:
	log_lines.push_front(text)
	if log_lines.size() > 8:
		log_lines.resize(8)
	log_label.text = "\n".join(log_lines)

func _on_auto_hunt_pressed() -> void:
	if player:
		player.toggle_auto_hunt()

func _on_mode_pressed() -> void:
	if player:
		player.toggle_wielder_mode()

func _on_level_up_pressed() -> void:
	if player:
		player.jump_to_level(player.sword_level + 1)

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

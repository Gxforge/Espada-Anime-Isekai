extends Node

## Autoload: datos globales del juego (evoluciones, monstruos, materiales, reliquias, consumibles)

const SWORD_EVOLUTIONS := [
	{
		"id": "wood", "tier_index": 0, "min_level": 1, "next_evolution_level": 5,
		"name": "Espada de Madera Ancestral", "subtitle": "Fase I • Nivel 1 – 4",
		"material_name": "Roble Vivo Tallado y Cuerda de Cáñamo",
		"description": "Tallada a mano del corazón de un roble milenario. Aunque humilde, absorbe la esencia vital de cada monstruo derrotado.",
		"passive_name": "Semilla del Despertar",
		"passive_description": "Absorbe +15% de Esencia de Alma adicional de monstruos básicos.",
		"base_damage": 18, "attack_speed": 1.15, "range": 3.1, "crit_chance": 0.10,
		"blade_color": Color("#9c6635"), "edge_color": Color("#c48f5a"),
		"guard_color": Color("#5c3a1e"), "aura_color": Color("#86efac"),
		"slash_color": Color("#d4a373"), "special_effect": "none",
		"model_path": "res://assets/models/sword_wood_nv1.obj"
	},
	{
		"id": "copper", "tier_index": 1, "min_level": 5, "next_evolution_level": 10,
		"name": "Espada de Cobre Forjado", "subtitle": "Fase II • Nivel 5 – 9",
		"material_name": "Cobre Fundido con Pátina de Verdete",
		"description": "¡Al alcanzar el Nivel 5, la madera se mineraliza en Cobre ardiente! Libera chispas voltaicas.",
		"passive_name": "Conductividad de Cobre",
		"passive_description": "Cada 3er golpe libera chispas cobrizas que infligen +35% de daño en área.",
		"base_damage": 42, "attack_speed": 1.28, "range": 3.55, "crit_chance": 0.16,
		"blade_color": Color("#d97742"), "edge_color": Color("#f7a574"),
		"guard_color": Color("#7c3f23"), "aura_color": Color("#fb923c"),
		"slash_color": Color("#f97316"), "special_effect": "sparks",
		"model_path": "res://assets/models/sword_copper_nv5.obj"
	},
	{
		"id": "iron", "tier_index": 2, "min_level": 10, "next_evolution_level": 15,
		"name": "Mandoble de Hierro Templado", "subtitle": "Fase III • Nivel 10 – 14",
		"material_name": "Acero y Hierro Negro de Cruzado",
		"description": "Forjada en sangre de bestias al Nivel 10. Hoja ancha con guarda de caballero.",
		"passive_name": "Filo Quebrantahuesos",
		"passive_description": "Los cortes críticos provocan sangrado profundo durante 3 segundos.",
		"base_damage": 88, "attack_speed": 1.38, "range": 3.9, "crit_chance": 0.22,
		"blade_color": Color("#94a3b8"), "edge_color": Color("#e2e8f0"),
		"guard_color": Color("#334155"), "aura_color": Color("#60a5fa"),
		"slash_color": Color("#93c5fd"), "special_effect": "bleed",
		"model_path": "res://assets/models/sword_iron_nv10.obj"
	},
	{
		"id": "silver", "tier_index": 3, "min_level": 15, "next_evolution_level": 20,
		"name": "Hoja de Plata Rúnica", "subtitle": "Fase IV • Nivel 15 – 19",
		"material_name": "Plata Lunar Grabada con Runas Nórdicas",
		"description": "Al Nivel 15 el metal se purifica en Plata Lunar. Siete runas brillan en azul celeste.",
		"passive_name": "Tormenta de Valquiria",
		"passive_description": "Los ataques invocan cadenas de relámpagos que saltan hasta a 3 monstruos.",
		"base_damage": 165, "attack_speed": 1.52, "range": 4.25, "crit_chance": 0.28,
		"blade_color": Color("#cbd5e1"), "edge_color": Color("#ffffff"),
		"guard_color": Color("#1e3a8a"), "aura_color": Color("#38bdf8"),
		"slash_color": Color("#00f2fe"), "special_effect": "lightning",
		"model_path": "res://assets/models/sword_silver_nv15.obj"
	},
	{
		"id": "gold", "tier_index": 4, "min_level": 20, "next_evolution_level": 25,
		"name": "Claymore de Oro Solar Imperial", "subtitle": "Fase V • Nivel 20 – 24",
		"material_name": "Oro Sagrado de 24 Quilates y Rubí Solar",
		"description": "Despertada al Nivel 20. Colosal espada real con halo ardiente levitante.",
		"passive_name": "Fulgor del Rey Sol",
		"passive_description": "Incendia el suelo al golpear y restaura vida constantemente en combate.",
		"base_damage": 295, "attack_speed": 1.65, "range": 4.6, "crit_chance": 0.34,
		"blade_color": Color("#facc15"), "edge_color": Color("#fef08a"),
		"guard_color": Color("#b45309"), "aura_color": Color("#fbbf24"),
		"slash_color": Color("#f59e0b"), "special_effect": "solar_burn",
		"model_path": "res://assets/models/sword_gold_nv20.obj"
	},
	{
		"id": "crystal", "tier_index": 5, "min_level": 25, "next_evolution_level": 30,
		"name": "Espada de Cristal Arcano", "subtitle": "Fase VI • Nivel 25 – 29",
		"material_name": "Prisma de Amatista y Diamante Astral",
		"description": "Al Nivel 25 la materia se cristaliza en energía pura. Fragmentos flotantes orbitan la hoja.",
		"passive_name": "Resonancia de Mil Prismas",
		"passive_description": "Los fragmentos flotantes disparan proyectiles de cristal automáticos.",
		"base_damage": 490, "attack_speed": 1.80, "range": 5.0, "crit_chance": 0.42,
		"blade_color": Color("#c084fc"), "edge_color": Color("#f3e8ff"),
		"guard_color": Color("#581c87"), "aura_color": Color("#d946ef"),
		"slash_color": Color("#c026d3"), "special_effect": "arcane_shards",
		"model_path": "res://assets/models/sword_crystal_nv25.obj"
	},
	{
		"id": "obsidian", "tier_index": 6, "min_level": 30, "next_evolution_level": 35,
		"name": "Devoradora de Obsidiana Dracónica", "subtitle": "Fase VII • Nivel 30 – 34",
		"material_name": "Obsidiana Volcánica, Magma y Hueso de Dragón",
		"description": "Al Nivel 30 asimila el corazón de los dragones. Hoja negra dentada con venas de magma.",
		"passive_name": "Sed de Sangre Abisal",
		"passive_description": "Drena vida masiva con cada tajo y provoca erupciones volcánicas.",
		"base_damage": 790, "attack_speed": 1.95, "range": 5.45, "crit_chance": 0.50,
		"blade_color": Color("#1e1b2e"), "edge_color": Color("#ff4500"),
		"guard_color": Color("#450a0a"), "aura_color": Color("#ef4444"),
		"slash_color": Color("#dc2626"), "special_effect": "lifesteal_magma",
		"model_path": "res://assets/models/sword_obsidian_nv30.obj"
	},
	{
		"id": "celestial", "tier_index": 7, "min_level": 35, "next_evolution_level": null,
		"name": "Excalibur Celestial del Vacío Cósmico", "subtitle": "Fase VIII (Forma Divina Final) • Nivel 35+",
		"material_name": "Luz Estelar Condensada y Singularidad del Vacío",
		"description": "La cúspide absoluta al Nivel 35. Alas de serafín, anillos orbitales y núcleo de agujero negro.",
		"passive_name": "Apocalipsis Astral",
		"passive_description": "Cada golpe invoca ondas dimensionales y duplica todo el daño crítico.",
		"base_damage": 1350, "attack_speed": 2.25, "range": 6.1, "crit_chance": 0.65,
		"blade_color": Color("#38bdf8"), "edge_color": Color("#fef08a"),
		"guard_color": Color("#f59e0b"), "aura_color": Color("#22d3ee"),
		"slash_color": Color("#67e8f9"), "special_effect": "cosmic_nova",
		"model_path": "res://assets/models/sword_celestial_nv35.obj"
	},
]

const MONSTER_DEFINITIONS := [
	{
		"id": "slime", "name": "Slime Cristalino del Bosque", "title": "Criatura Gelatinosa Nv. 1",
		"min_wave": 1, "is_boss": false, "base_hp": 48, "base_damage": 7, "speed": 3.1,
		"attack_range": 1.9, "attack_cooldown": 1.5, "xp_reward": 22, "gold_reward": 12,
		"scale": 1.0, "primary_color": Color("#22c55e"), "accent_color": Color("#86efac"),
		"drop_material": "gel_cristalino", "drop_chance": 0.65,
		"model_path": "res://assets/models/monster_slime.obj"
	},
	{
		"id": "goblin", "name": "Trasgo Saqueador", "title": "Explorador Salvaje Nv. 3",
		"min_wave": 1, "is_boss": false, "base_hp": 85, "base_damage": 12, "speed": 4.1,
		"attack_range": 2.2, "attack_cooldown": 1.25, "xp_reward": 34, "gold_reward": 20,
		"scale": 1.05, "primary_color": Color("#65a30d"), "accent_color": Color("#a16207"),
		"drop_material": "colmillo_trasgo", "drop_chance": 0.60,
		"model_path": "res://assets/models/monster_goblin.obj"
	},
	{
		"id": "skeleton", "name": "Esqueleto Guardia Maldito", "title": "No-Muerto de la Cripta Nv. 5",
		"min_wave": 2, "is_boss": false, "base_hp": 145, "base_damage": 18, "speed": 3.6,
		"attack_range": 2.4, "attack_cooldown": 1.3, "xp_reward": 52, "gold_reward": 32,
		"scale": 1.15, "primary_color": Color("#e2e8f0"), "accent_color": Color("#38bdf8"),
		"drop_material": "hueso_maldito", "drop_chance": 0.58,
		"model_path": "res://assets/models/monster_skeleton.obj"
	},
	{
		"id": "copper_golem", "name": "Gólem de Roca y Cobre", "title": "Coloso Mineral Nv. 8",
		"min_wave": 3, "is_boss": false, "base_hp": 280, "base_damage": 28, "speed": 2.45,
		"attack_range": 2.8, "attack_cooldown": 1.8, "xp_reward": 88, "gold_reward": 55,
		"scale": 1.35, "primary_color": Color("#57534e"), "accent_color": Color("#ea580c"),
		"drop_material": "nucleo_cobre", "drop_chance": 0.55,
		"model_path": "res://assets/models/monster_copper_golem.obj"
	},
	{
		"id": "orc_berserker", "name": "Orco Berserker Sangriento", "title": "Campeón de Guerra Nv. 12",
		"min_wave": 4, "is_boss": false, "base_hp": 460, "base_damage": 40, "speed": 3.8,
		"attack_range": 2.7, "attack_cooldown": 1.2, "xp_reward": 135, "gold_reward": 85,
		"scale": 1.3, "primary_color": Color("#15803d"), "accent_color": Color("#dc2626"),
		"drop_material": "sangre_berserker", "drop_chance": 0.52,
		"model_path": "res://assets/models/monster_orc_berserker.obj"
	},
	{
		"id": "crimson_drake", "name": "Draco Escarlata Alado", "title": "Bestia Dracónica Nv. 16",
		"min_wave": 5, "is_boss": false, "base_hp": 720, "base_damage": 56, "speed": 4.3,
		"attack_range": 3.1, "attack_cooldown": 1.4, "xp_reward": 210, "gold_reward": 140,
		"scale": 1.4, "primary_color": Color("#b91c1c"), "accent_color": Color("#f59e0b"),
		"drop_material": "escama_escarlata", "drop_chance": 0.50,
		"model_path": "res://assets/models/monster_crimson_drake.obj"
	},
	{
		"id": "demon_lord", "name": "Malakor, Señor del Abismo", "title": "JEFE SUPREMO DE FORJA",
		"min_wave": 3, "is_boss": true, "base_hp": 1450, "base_damage": 75, "speed": 3.3,
		"attack_range": 3.8, "attack_cooldown": 1.6, "xp_reward": 550, "gold_reward": 400,
		"scale": 1.85, "primary_color": Color("#18181b"), "accent_color": Color("#ef4444"),
		"drop_material": "corazon_abismo", "drop_chance": 1.0,
		"model_path": "res://assets/models/monster_demon_lord.obj"
	},
]

const MATERIAL_DEFINITIONS := {
	"gel_cristalino": {
		"id": "gel_cristalino", "name": "Gel Cristalino", "rarity": "common",
		"color": Color("#4ade80"), "source": "slime",
		"desc": "Esencia gelatinosa pura del bosque."
	},
	"colmillo_trasgo": {
		"id": "colmillo_trasgo", "name": "Colmillo Salvaje", "rarity": "common",
		"color": Color("#a3e635"), "source": "goblin",
		"desc": "Colmillo afilado de trasgo saqueador."
	},
	"hueso_maldito": {
		"id": "hueso_maldito", "name": "Hueso Rúnico", "rarity": "uncommon",
		"color": Color("#38bdf8"), "source": "skeleton",
		"desc": "Fragmento óseo grabado con runas antiguas."
	},
	"nucleo_cobre": {
		"id": "nucleo_cobre", "name": "Núcleo Mineral", "rarity": "uncommon",
		"color": Color("#fb923c"), "source": "copper_golem",
		"desc": "Corazón fundido de roca y cobre vivo."
	},
	"sangre_berserker": {
		"id": "sangre_berserker", "name": "Esencia Berserker", "rarity": "rare",
		"color": Color("#f87171"), "source": "orc_berserker",
		"desc": "Furia concentrada de campeón de guerra."
	},
	"escama_escarlata": {
		"id": "escama_escarlata", "name": "Escama de Draco", "rarity": "epic",
		"color": Color("#f59e0b"), "source": "crimson_drake",
		"desc": "Escama ígnea casi indestructible."
	},
	"corazon_abismo": {
		"id": "corazon_abismo", "name": "Corazón de Malakor", "rarity": "legendary",
		"color": Color("#e879f9"), "source": "demon_lord",
		"desc": "Núcleo abisal arrebatado al Señor del Abismo."
	},
}

const RELIC_DEFINITIONS := [
	{
		"id": "grip_oak", "slot": "grip", "slot_label": "Empuñadura",
		"name": "Guardamano de Roble Vivo", "rarity": "common", "color": Color("#4ade80"),
		"desc": "+35 Vida Máx • +10% EXP",
		"stats": {"max_hp_bonus": 35, "xp_mult": 0.10},
		"recipe_gold": 40, "recipe_mats": {"gel_cristalino": 3}
	},
	{
		"id": "grip_crusader", "slot": "grip", "slot_label": "Empuñadura",
		"name": "Empuñadura de Cruzado", "rarity": "rare", "color": Color("#60a5fa"),
		"desc": "+15% Daño • +6% Prob. Crítico",
		"stats": {"dmg_mult": 0.15, "crit_chance": 0.06},
		"recipe_gold": 110, "recipe_mats": {"hueso_maldito": 2, "nucleo_cobre": 2}
	},
	{
		"id": "grip_draconic", "slot": "grip", "slot_label": "Empuñadura",
		"name": "Garras de Obsidiana", "rarity": "epic", "color": Color("#c084fc"),
		"desc": "+26% Daño • +4 Vida/golpe",
		"stats": {"dmg_mult": 0.26, "life_on_hit": 4},
		"recipe_gold": 240, "recipe_mats": {"sangre_berserker": 2, "escama_escarlata": 2}
	},
	{
		"id": "rune_wind", "slot": "rune", "slot_label": "Runa",
		"name": "Runa del Céfiro", "rarity": "common", "color": Color("#38bdf8"),
		"desc": "+14% Vel. Ataque • -10% Enfriamiento",
		"stats": {"atk_speed_mult": 0.14, "cd_reduction": 0.10},
		"recipe_gold": 45, "recipe_mats": {"colmillo_trasgo": 3}
	},
	{
		"id": "rune_storm", "slot": "rune", "slot_label": "Runa",
		"name": "Runa de Valquiria", "rarity": "rare", "color": Color("#60a5fa"),
		"desc": "+10% Prob. Crítico • +25% Daño Crít.",
		"stats": {"crit_chance": 0.10, "crit_mult": 0.25},
		"recipe_gold": 130, "recipe_mats": {"hueso_maldito": 3, "nucleo_cobre": 1}
	},
	{
		"id": "rune_void", "slot": "rune", "slot_label": "Runa",
		"name": "Runa Astral del Vacío", "rarity": "epic", "color": Color("#c084fc"),
		"desc": "+28% Daño • +12% Alcance • -15% CD",
		"stats": {"dmg_mult": 0.28, "range_mult": 0.12, "cd_reduction": 0.15},
		"recipe_gold": 320, "recipe_mats": {"escama_escarlata": 2, "corazon_abismo": 1}
	},
	{
		"id": "relic_chalice", "slot": "relic", "slot_label": "Reliquia",
		"name": "Cáliz Carmesí", "rarity": "rare", "color": Color("#f87171"),
		"desc": "+5 Vida/golpe • +55 Vida Máx",
		"stats": {"life_on_hit": 5, "max_hp_bonus": 55},
		"recipe_gold": 150, "recipe_mats": {"nucleo_cobre": 2, "sangre_berserker": 2}
	},
	{
		"id": "relic_magnet", "slot": "relic", "slot_label": "Reliquia",
		"name": "Prisma Colector", "rarity": "rare", "color": Color("#fbbf24"),
		"desc": "+25% EXP • +25% Oro",
		"stats": {"xp_mult": 0.25, "gold_mult": 0.25},
		"recipe_gold": 95, "recipe_mats": {"gel_cristalino": 2, "colmillo_trasgo": 2}
	},
	{
		"id": "relic_malakor", "slot": "relic", "slot_label": "Reliquia",
		"name": "Corona Abisal de Malakor", "rarity": "legendary", "color": Color("#f59e0b"),
		"desc": "+38% Daño • +12% Crítico • +7 Vida/golpe",
		"stats": {"dmg_mult": 0.38, "crit_chance": 0.12, "life_on_hit": 7},
		"recipe_gold": 500, "recipe_mats": {"corazon_abismo": 2, "escama_escarlata": 2}
	},
]

const CONSUMABLE_DEFINITIONS := {
	"potion_hp": {
		"id": "potion_hp", "name": "Poción de Brasa Vital",
		"desc": "Restaura al instante 45% de tu Vida Máxima.",
		"cost_gold": 35, "heal_ratio": 0.45, "color": Color("#fb7185")
	},
	"elixir_xp": {
		"id": "elixir_xp", "name": "Elixir de Esencia Pura",
		"desc": "Otorga +65% de la EXP requerida del nivel actual.",
		"cost_gold": 75, "xp_ratio": 0.65, "color": Color("#38bdf8")
	},
}

const UPGRADE_DEFINITIONS := [
	{"key": "sharpness", "name": "Afilar Hoja", "short": "Afilar", "desc": "+18% Daño", "base_cost": 25},
	{"key": "swiftness", "name": "Ligereza", "short": "Ligereza", "desc": "+8% Vel. Ataque", "base_cost": 30},
	{"key": "criticalMastery", "name": "Maestría Crítica", "short": "Crítico", "desc": "+4% Crit / +15% Mult", "base_cost": 35},
	{"key": "vampirism", "name": "Runa Vampírica", "short": "Vampiro", "desc": "+3 Vida/golpe", "base_cost": 40},
	{"key": "soulMagnet", "name": "Imán de Almas", "short": "Almas", "desc": "+15% EXP / +12% Oro", "base_cost": 30},
	{"key": "bladeSize", "name": "Hoja Colosal", "short": "Colosal", "desc": "+6% Alcance y Escala", "base_cost": 45},
]

func get_sword_for_level(level: int) -> Dictionary:
	var current: Dictionary = SWORD_EVOLUTIONS[0]
	for tier in SWORD_EVOLUTIONS:
		if level >= int(tier["min_level"]):
			current = tier
	return current

func get_xp_required(level: int) -> int:
	if level <= 4:
		return int(round(35 + (level - 1) * 20))
	if level <= 10:
		return int(round(110 + (level - 4) * 38))
	return int(round(340 + pow(level - 10, 1.35) * 65))

func get_eligible_monsters(wave: int, boss_only: bool = false) -> Array:
	var pool: Array = []
	for m in MONSTER_DEFINITIONS:
		if int(m["min_wave"]) <= wave and bool(m["is_boss"]) == boss_only:
			pool.append(m)
	if pool.is_empty():
		if boss_only:
			for m in MONSTER_DEFINITIONS:
				if bool(m["is_boss"]):
					return [m]
		return [MONSTER_DEFINITIONS[0]]
	return pool

func get_relic_by_id(relic_id: String) -> Dictionary:
	for r in RELIC_DEFINITIONS:
		if str(r["id"]) == relic_id:
			return r
	return {}

func get_material_by_id(mat_id: String) -> Dictionary:
	return MATERIAL_DEFINITIONS.get(mat_id, {})

func get_drop_material_for_monster(m_id: String) -> String:
	for k in MATERIAL_DEFINITIONS.keys():
		if str(MATERIAL_DEFINITIONS[k].get("source", "")) == m_id:
			return str(k)
	return "gel_cristalino"

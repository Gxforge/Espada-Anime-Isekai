extends Node

## Autoload: datos globales del juego (evoluciones, monstruos, estado)

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
		"model_path": "res://assets/models/monster_slime.obj"
	},
	{
		"id": "goblin", "name": "Trasgo Saqueador", "title": "Explorador Salvaje Nv. 3",
		"min_wave": 1, "is_boss": false, "base_hp": 85, "base_damage": 12, "speed": 4.1,
		"attack_range": 2.2, "attack_cooldown": 1.25, "xp_reward": 34, "gold_reward": 20,
		"scale": 1.05, "primary_color": Color("#65a30d"), "accent_color": Color("#a16207"),
		"model_path": "res://assets/models/monster_goblin.obj"
	},
	{
		"id": "skeleton", "name": "Esqueleto Guardia Maldito", "title": "No-Muerto de la Cripta Nv. 5",
		"min_wave": 2, "is_boss": false, "base_hp": 145, "base_damage": 18, "speed": 3.6,
		"attack_range": 2.4, "attack_cooldown": 1.3, "xp_reward": 52, "gold_reward": 32,
		"scale": 1.15, "primary_color": Color("#e2e8f0"), "accent_color": Color("#38bdf8"),
		"model_path": "res://assets/models/monster_skeleton.obj"
	},
	{
		"id": "copper_golem", "name": "Gólem de Roca y Cobre", "title": "Coloso Mineral Nv. 8",
		"min_wave": 3, "is_boss": false, "base_hp": 280, "base_damage": 28, "speed": 2.45,
		"attack_range": 2.8, "attack_cooldown": 1.8, "xp_reward": 88, "gold_reward": 55,
		"scale": 1.35, "primary_color": Color("#57534e"), "accent_color": Color("#ea580c"),
		"model_path": "res://assets/models/monster_copper_golem.obj"
	},
	{
		"id": "orc_berserker", "name": "Orco Berserker Sangriento", "title": "Campeón de Guerra Nv. 12",
		"min_wave": 4, "is_boss": false, "base_hp": 460, "base_damage": 40, "speed": 3.8,
		"attack_range": 2.7, "attack_cooldown": 1.2, "xp_reward": 135, "gold_reward": 85,
		"scale": 1.3, "primary_color": Color("#15803d"), "accent_color": Color("#dc2626"),
		"model_path": "res://assets/models/monster_orc_berserker.obj"
	},
	{
		"id": "crimson_drake", "name": "Draco Escarlata Alado", "title": "Bestia Dracónica Nv. 16",
		"min_wave": 5, "is_boss": false, "base_hp": 720, "base_damage": 56, "speed": 4.3,
		"attack_range": 3.1, "attack_cooldown": 1.4, "xp_reward": 210, "gold_reward": 140,
		"scale": 1.4, "primary_color": Color("#b91c1c"), "accent_color": Color("#f59e0b"),
		"model_path": "res://assets/models/monster_crimson_drake.obj"
	},
	{
		"id": "demon_lord", "name": "Malakor, Señor del Abismo", "title": "JEFE SUPREMO DE FORJA",
		"min_wave": 3, "is_boss": true, "base_hp": 1450, "base_damage": 75, "speed": 3.3,
		"attack_range": 3.8, "attack_cooldown": 1.6, "xp_reward": 550, "gold_reward": 400,
		"scale": 1.85, "primary_color": Color("#18181b"), "accent_color": Color("#ef4444"),
		"model_path": "res://assets/models/monster_demon_lord.obj"
	},
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

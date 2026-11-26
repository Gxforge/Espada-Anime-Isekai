"""
Generates the canonical data-driven JSON catalogs for Espada Anime Isekai (Godot 4.4):
1. godot_project/data/forms/evolution_catalog.json
   - 24 Evolutionary Stages across 6 Canonical Eras (I..VI)
   - Permanent multi-way branching (2..5 options per node, 0 dead ends, hybrid/secret forms)
   - Protagonist sentient-sword consciousness preserved across every form
   - 17-attribute base stat profiles with real lineage trade-offs
   - 5 unlock condition types (min_level, min_evolution_xp, required_materials, required_skills, required_events)
2. godot_project/data/skills/skills_catalog.json
   - 72 Initial Skills across 6 Trees (12 per tree: 6 Active + 6 Passive = 36 Active + 36 Passive)
   - Prerequisites, skill point costs, stage gates, and branch-exclusive unlocks
"""

import json
import os

REPO = "/home/user/Espada-Anime-Isekai"
FORMS_DIR = f"{REPO}/godot_project/data/forms"
SKILLS_DIR = f"{REPO}/godot_project/data/skills"
os.makedirs(FORMS_DIR, exist_ok=True)
os.makedirs(SKILLS_DIR, exist_ok=True)

ERAS = [
    {"era": 1, "id": "era_1_awakening",      "name": "Era I — Despertar",            "stage_min": 1,  "stage_max": 4},
    {"era": 2, "id": "era_2_affinity",       "name": "Era II — Afinidad",            "stage_min": 5,  "stage_max": 8},
    {"era": 3, "id": "era_3_specialization", "name": "Era III — Especialización",    "stage_min": 9,  "stage_max": 12},
    {"era": 4, "id": "era_4_transcendence",  "name": "Era IV — Trascendencia",       "stage_min": 13, "stage_max": 16},
    {"era": 5, "id": "era_5_dominion",       "name": "Era V — Dominio",              "stage_min": 17, "stage_max": 20},
    {"era": 6, "id": "era_6_supreme",        "name": "Era VI — Existencia Suprema",  "stage_min": 21, "stage_max": 24},
]

LINEAGES = {
    "origin": {
        "name": "Tronco del Despertar",
        "blade_color": "#9c6635", "edge_color": "#d4a373", "guard_color": "#5c3a1e",
        "aura_color": "#86efac", "slash_color": "#d4a373", "special_effect": "none",
        "legacy_model": "res://assets/models/sword_wood_nv1.obj",
        "mods": {"phys": 1.00, "elem": 0.85, "spd": 1.00, "rng": 1.00, "crit": 0.00, "cdmg": 0.00,
                 "pen": 0.00, "steal": 0.00, "hp": 1.00, "def": 1.00, "res": 0.05, "ereg": 1.0, "emax": 1.0, "mspd": 1.00, "cdr": 0.00, "stat": 0.05, "soul": 0.15},
    },
    "blessed": {
        "name": "Linaje Bendito y Solar",
        "blade_color": "#facc15", "edge_color": "#fef9c3", "guard_color": "#b45309",
        "aura_color": "#fde047", "slash_color": "#f59e0b", "special_effect": "solar_burn",
        "legacy_model": "res://assets/models/sword_gold_nv20.obj",
        "mods": {"phys": 1.05, "elem": 1.12, "spd": 0.96, "rng": 1.04, "crit": 0.02, "cdmg": 0.10,
                 "pen": 0.04, "steal": 0.00, "hp": 1.24, "def": 1.32, "res": 0.24, "ereg": 1.15, "emax": 1.10, "mspd": 0.98, "cdr": 0.05, "stat": 0.14, "soul": 0.12},
    },
    "cursed": {
        "name": "Linaje Maldito y Abisal",
        "blade_color": "#581c87", "edge_color": "#f43f5e", "guard_color": "#1e1b4b",
        "aura_color": "#e11d48", "slash_color": "#fb7185", "special_effect": "void_leech",
        "legacy_model": "res://assets/models/sword_obsidian_nv30.obj",
        "mods": {"phys": 1.28, "elem": 1.08, "spd": 1.08, "rng": 1.02, "crit": 0.08, "cdmg": 0.42,
                 "pen": 0.18, "steal": 0.09, "hp": 0.86, "def": 0.82, "res": 0.04, "ereg": 0.95, "emax": 1.00, "mspd": 1.05, "cdr": 0.03, "stat": 0.22, "soul": 0.22},
    },
    "elemental": {
        "name": "Linaje Elemental Primordial",
        "blade_color": "#38bdf8", "edge_color": "#e0f2fe", "guard_color": "#c2410c",
        "aura_color": "#fb923c", "slash_color": "#38bdf8", "special_effect": "lightning",
        "legacy_model": "res://assets/models/sword_copper_nv5.obj",
        "mods": {"phys": 0.98, "elem": 1.42, "spd": 1.04, "rng": 1.10, "crit": 0.04, "cdmg": 0.18,
                 "pen": 0.08, "steal": 0.01, "hp": 0.98, "def": 0.96, "res": 0.28, "ereg": 1.25, "emax": 1.22, "mspd": 1.03, "cdr": 0.07, "stat": 0.30, "soul": 0.14},
    },
    "spiritual": {
        "name": "Linaje Espiritual de Alma",
        "blade_color": "#cbd5e1", "edge_color": "#ffffff", "guard_color": "#0f766e",
        "aura_color": "#34d399", "slash_color": "#6ee7b7", "special_effect": "frost_crit",
        "legacy_model": "res://assets/models/sword_silver_nv15.obj",
        "mods": {"phys": 1.04, "elem": 1.18, "spd": 1.22, "rng": 1.06, "crit": 0.07, "cdmg": 0.22,
                 "pen": 0.10, "steal": 0.03, "hp": 0.96, "def": 0.92, "res": 0.20, "ereg": 1.38, "emax": 1.28, "mspd": 1.14, "cdr": 0.10, "stat": 0.18, "soul": 0.32},
    },
    "arcane": {
        "name": "Linaje Arcano y Cósmico",
        "blade_color": "#818cf8", "edge_color": "#f5d0fe", "guard_color": "#312e81",
        "aura_color": "#c084fc", "slash_color": "#e879f9", "special_effect": "bleed",
        "legacy_model": "res://assets/models/sword_crystal_nv25.obj",
        "mods": {"phys": 0.92, "elem": 1.52, "spd": 1.02, "rng": 1.14, "crit": 0.05, "cdmg": 0.26,
                 "pen": 0.14, "steal": 0.02, "hp": 0.92, "def": 0.88, "res": 0.32, "ereg": 1.48, "emax": 1.45, "mspd": 1.02, "cdr": 0.15, "stat": 0.26, "soul": 0.20},
    },
    "hybrid": {
        "name": "Convergencia Híbrida / Secreta",
        "blade_color": "#f8fafc", "edge_color": "#fde047", "guard_color": "#4c1d95",
        "aura_color": "#38bdf8", "slash_color": "#f472b6", "special_effect": "celestial_judgment",
        "legacy_model": "res://assets/models/sword_celestial_nv35.obj",
        "mods": {"phys": 1.22, "elem": 1.35, "spd": 1.14, "rng": 1.12, "crit": 0.08, "cdmg": 0.34,
                 "pen": 0.16, "steal": 0.05, "hp": 1.12, "def": 1.14, "res": 0.26, "ereg": 1.32, "emax": 1.32, "mspd": 1.08, "cdr": 0.12, "stat": 0.26, "soul": 0.28},
    },
}


def era_for_stage(stage: int) -> dict:
    for e in ERAS:
        if e["stage_min"] <= stage <= e["stage_max"]:
            return e
    return ERAS[-1]


def compute_base_stats(stage: int, lineage: str, variant_bias: str = "balanced") -> dict:
    m = LINEAGES[lineage]["mods"]
    s = stage - 1
    # Smooth exponential-polynomial RPG curve across 24 stages
    growth = 1.0 + 0.24 * s + 0.032 * (s ** 1.65)
    phys = round((18.0 * growth) * m["phys"], 1)
    elem = round((6.0 + 11.5 * s + 0.85 * (s ** 1.6)) * m["elem"], 1) if stage > 1 else 4.0
    spd = round((1.15 + s * 0.026) * m["spd"], 3)
    rng = round((3.10 + min(2.4, s * 0.095)) * m["rng"], 2)
    crit = round(min(0.68, (0.10 + s * 0.014) + m["crit"]), 3)
    cdmg = round(1.85 + s * 0.035 + m["cdmg"], 2)
    pen = round(min(0.65, s * 0.012 + m["pen"]), 3)
    steal = round(min(0.28, m["steal"] + (0.004 * s if m["steal"] > 0 else 0.0)), 3)
    hp = int(round((120.0 + s * 28.0 + (s ** 1.45) * 6.5) * m["hp"]))
    df = round((4.0 + s * 2.6) * m["def"], 1)
    res = round(min(0.70, m["res"] + s * 0.01), 3)
    ereg = round((8.0 + s * 0.85) * m["ereg"], 2)
    emax = int(round((100.0 + s * 10.0) * m["emax"]))
    mspd = round((8.8 + min(2.2, s * 0.06)) * m["mspd"], 2)
    cdr = round(min(0.42, m["cdr"] + s * 0.006), 3)
    stat_ch = round(min(0.75, m["stat"] + s * 0.011), 3)
    soul = round(m["soul"] + s * 0.008, 3)

    if variant_bias == "heavy":
        phys = round(phys * 1.12, 1)
        spd = round(spd * 0.93, 3)
        rng = round(rng * 1.06, 2)
        df = round(df * 1.10, 1)
    elif variant_bias == "swift":
        spd = round(spd * 1.11, 3)
        mspd = round(mspd * 1.05, 2)
        crit = round(min(0.72, crit + 0.04), 3)
        hp = int(round(hp * 0.94))
    elif variant_bias == "mystic":
        elem = round(elem * 1.18, 1)
        emax = int(round(emax * 1.12))
        cdr = round(min(0.45, cdr + 0.03), 3)

    return {
        "physical_damage": phys,
        "elemental_damage": elem,
        "attack_speed": spd,
        "attack_range": rng,
        "crit_chance": crit,
        "crit_damage": cdmg,
        "armor_penetration": pen,
        "life_steal": steal,
        "max_hp": hp,
        "defense": df,
        "elemental_resistance": res,
        "energy_regen": ereg,
        "max_energy": emax,
        "move_speed": mspd,
        "cdr": cdr,
        "status_chance": stat_ch,
        "soul_absorption": soul,
    }


# ==============================================================================
# PART 1: BUILD THE 72 INITIAL SKILLS ACROSS 6 TREES (12 EACH: 6 ACTIVE + 6 PASSIVE)
# ==============================================================================
TREE_DEFS = [
    {
        "id": "physical_mastery",
        "name": "Dominio Físico",
        "icon": "⚔",
        "color": "#f97316",
        "description": "Técnicas de tajo, estocada quebrantahuesos, torbellinos de acero vivo y ejecución crítica.",
        "skills": [
            # 6 Actives (Tier 1..6) + 6 Passives (Tier 1..6)
            ("whirlwind",        "Torbellino de Filo Vivo",    "active",  1, 1,  1, [],                     [],                    4.0,  18, "shockwave",       {"damage_mult": 1.35, "radius": 4.2}, "Gira a velocidad sobrehumana cortando a todos los enemigos cercanos."),
            ("phys_pas_edge",    "Memoria del Acero",          "passive", 1, 1,  1, [],                     [],                    0.0,   0, "passive",         {"physical_damage_pct": 0.08}, "La consciencia de la hoja afila su propio bisel (+8% Daño Físico)."),
            ("phys_act_rend",    "Tajo Quebrantaguardas",      "active",  2, 3,  1, ["whirlwind"],          [],                    5.5,  22, "crimson_cleave",  {"damage_mult": 1.75, "armor_shred": 0.15}, "Descarga frontal pesada que fractura corazas enemigas."),
            ("phys_pas_tempo",   "Cadencia de Duelo",          "passive", 2, 3,  1, ["phys_pas_edge"],      [],                    0.0,   0, "passive",         {"attack_speed_pct": 0.07}, "Equilibra el contrapeso del pomo (+7% Velocidad de Ataque)."),
            ("phys_act_flurry",  "Danza de Siete Cortes",      "active",  3, 6,  2, ["phys_act_rend"],      [],                    7.0,  28, "shockwave",       {"damage_mult": 2.15, "radius": 4.6}, "Desata una ráfaga circular de cortes precisos de alta frecuencia."),
            ("phys_pas_keen",    "Bisel de Precisión",         "passive", 3, 6,  2, ["phys_pas_tempo"],     [],                    0.0,   0, "passive",         {"crit_chance_add": 0.05, "crit_damage_add": 0.15}, "Incrementa +5% Crítico y +15% Daño Crítico."),
            ("phys_act_impale",  "Estocada Perforamundos",     "active",  4, 10, 2, ["phys_act_flurry"],    [],                    8.0,  34, "wave_projectile", {"damage_mult": 2.55, "speed": 26.0}, "Proyecta una lanza de presión física que atraviesa hordas."),
            ("phys_pas_pen",     "Filo Sin Obstáculos",        "passive", 4, 10, 2, ["phys_pas_keen"],      [],                    0.0,   0, "passive",         {"armor_penetration_add": 0.10}, "Ignora +10% adicional de la defensa física del objetivo."),
            ("phys_act_quake",   "Impacto Partetierras",       "active",  5, 15, 3, ["phys_act_impale"],    ["blessed", "cursed", "elemental", "hybrid"], 10.0, 42, "nova_burst", {"damage_mult": 3.10, "radius": 5.8}, "Clava el filo en el suelo liberando una onda sísmica devastadora."),
            ("phys_pas_reach",   "Extensión Soberana",         "passive", 5, 15, 3, ["phys_pas_pen"],       [],                    0.0,   0, "passive",         {"attack_range_add": 0.45, "physical_damage_pct": 0.10}, "Extiende el alcance físico +0.45 m y +10% Daño Físico."),
            ("phys_act_exec",    "Veredicto del Filo Puro",    "active",  6, 20, 4, ["phys_act_quake"],     ["blessed", "cursed", "hybrid"], 12.5, 52, "sword_rain", {"damage_mult": 3.85, "strikes": 6}, "Ejecución maestra que abate objetivos debilitados con precisión letal."),
            ("phys_pas_master",  "Cénit de la Hoja Viviente",  "passive", 6, 21, 4, ["phys_pas_reach"],     [],                    0.0,   0, "passive",         {"physical_damage_pct": 0.16, "crit_damage_add": 0.25}, "Dominio absoluto de la anatomía física (+16% Daño Físico, +25% Daño Crítico)."),
        ],
    },
    {
        "id": "elemental_magic",
        "name": "Magia Elemental",
        "icon": "✦",
        "color": "#38bdf8",
        "description": "Canalización de llama solar, escarcha cristalina, relámpago voltaico y tormentas primordiales.",
        "skills": [
            ("swordWave",        "Onda Cortante Elemental",    "active",  1, 1,  1, [],                     [],                    5.5,  20, "wave_projectile", {"damage_mult": 1.55, "speed": 22.0}, "Lanza un arco creciente de energía cortante hacia el frente."),
            ("elem_pas_spark",   "Conducto Primordial",        "passive", 1, 1,  1, [],                     [],                    0.0,   0, "passive",         {"elemental_damage_pct": 0.10}, "El núcleo canaliza maná ambiental (+10% Daño Elemental)."),
            ("elem_act_flare",   "Estallido Ígneo",            "active",  2, 3,  1, ["swordWave"],          [],                    6.5,  25, "nova_burst",      {"damage_mult": 1.85, "radius": 4.5}, "Detona una corona de brasas alrededor de la espada."),
            ("elem_pas_aff",     "Afinidad de Tormenta",       "passive", 2, 4,  1, ["elem_pas_spark"],     [],                    0.0,   0, "passive",         {"status_chance_add": 0.08}, "Aumenta +8% la probabilidad de aplicar estados elementales."),
            ("elem_act_frost",   "Lanza de Escarcha Cero",     "active",  3, 6,  2, ["elem_act_flare"],     [],                    7.5,  30, "wave_projectile", {"damage_mult": 2.25, "speed": 24.0}, "Dispara una aguja glacial que entumece a las bestias impactadas."),
            ("elem_pas_prism",   "Refracción Prismática",      "passive", 3, 7,  2, ["elem_pas_aff"],       [],                    0.0,   0, "passive",         {"elemental_resistance_add": 0.08, "elemental_damage_pct": 0.08}, "Otorga +8% Resistencia Elemental y +8% Daño Elemental."),
            ("elem_act_volt",    "Tempestad de Fulgurita",     "active",  4, 10, 2, ["elem_act_frost"],     ["elemental", "arcane", "hybrid"], 8.5, 36, "nova_burst", {"damage_mult": 2.75, "radius": 5.5}, "Descarga relámpagos encadenados en todo el perímetro."),
            ("elem_pas_surge",   "Sobrecarga Rúnica",          "passive", 4, 11, 2, ["elem_pas_prism"],     [],                    0.0,   0, "passive",         {"energy_regen_pct": 0.15, "cdr_add": 0.04}, "Regenera +15% Energía y reduce enfriamientos 4%."),
            ("elem_act_magma",   "Cataclismo Piroclástico",    "active",  5, 15, 3, ["elem_act_volt"],      ["elemental", "blessed", "hybrid"], 11.0, 45, "sword_rain", {"damage_mult": 3.30, "strikes": 5}, "Invoca pilares ardientes del manto terrestre sobre los enemigos."),
            ("elem_pas_conv",    "Convergencia Tetral",        "passive", 5, 16, 3, ["elem_pas_surge"],     ["elemental", "arcane", "hybrid"], 0.0, 0, "passive", {"elemental_damage_pct": 0.16, "status_chance_add": 0.10}, "Fuego, hielo y rayo resuenan al unísono (+16% Daño Elemental)."),
            ("elem_act_super",   "Supernova de los Cuatro Vientos", "active", 6, 20, 4, ["elem_act_magma"], ["elemental", "hybrid"], 13.5, 56, "nova_burst", {"damage_mult": 4.10, "radius": 7.0}, "Explosión elemental suprema que purga el campo de batalla."),
            ("elem_pas_avatar",  "Corazón de Cataclismo",      "passive", 6, 21, 4, ["elem_pas_conv"],      ["elemental", "hybrid"], 0.0, 0, "passive", {"elemental_damage_pct": 0.22, "armor_penetration_add": 0.08}, "Convierte a la espada en un fenómeno natural viviente (+22% Daño Elemental)."),
        ],
    },
    {
        "id": "spiritual_energy",
        "name": "Energía Espiritual",
        "icon": "★",
        "color": "#34d399",
        "description": "Levitación astral, cosecha de esencias de alma, pasos etéreos y proyección de hojas fantasma.",
        "skills": [
            ("dash",             "Paso Astral",                "active",  1, 1,  1, [],                     [],                    2.4,  10, "dash_strike",     {"dash_boost": 1.0}, "Desplazamiento instantáneo con breves instantes de intangibilidad."),
            ("spir_pas_seed",    "Resonancia de Reencarnación","passive", 1, 1,  1, [],                     [],                    0.0,   0, "passive",         {"soul_absorption_add": 0.10, "energy_regen_pct": 0.08}, "Aumenta +10% la absorción de Esencia de Alma y +8% regeneración."),
            ("spir_act_pulse",   "Pulso del Árbol Mundo",      "active",  2, 3,  1, ["dash"],               [],                    6.0,  22, "nova_burst",      {"damage_mult": 1.65, "heal_pct": 0.06, "radius": 4.4}, "Onda espiritual que daña enemigos y restaura 6% de salud máxima."),
            ("spir_pas_wind",    "Levitación Ligera",          "passive", 2, 4,  1, ["spir_pas_seed"],      [],                    0.0,   0, "passive",         {"move_speed_pct": 0.07}, "Flujo etéreo sin fricción (+7% Velocidad de Movimiento)."),
            ("spir_act_echo",    "Hojas Eco del Alma",         "active",  3, 6,  2, ["spir_act_pulse"],     [],                    7.5,  28, "wave_projectile", {"damage_mult": 2.20, "speed": 25.0}, "Proyecta réplicas espirituales del filo que persiguen la línea frontal."),
            ("spir_pas_mind",    "Mente Cristalina",           "passive", 3, 7,  2, ["spir_pas_wind"],      [],                    0.0,   0, "passive",         {"max_energy_add": 30, "cdr_add": 0.05}, "Expande el núcleo consciente (+30 Energía Máx, +5% Reducción CD)."),
            ("spir_act_lotus",   "Floración de Jade Astral",   "active",  4, 10, 2, ["spir_act_echo"],      ["spiritual", "blessed", "hybrid"], 9.0, 35, "nova_burst", {"damage_mult": 2.60, "heal_pct": 0.10, "radius": 5.4}, "Despliega pétalos cortantes de ki puro mientras purifica heridas."),
            ("spir_pas_flow",    "Armonía Espada-Portador",    "passive", 4, 11, 2, ["spir_pas_mind"],      [],                    0.0,   0, "passive",         {"attack_speed_pct": 0.09, "soul_absorption_add": 0.12}, "Sincronía perfecta (+9% Vel. Ataque, +12% Absorción de Alma)."),
            ("spir_act_zenith",  "Cien Filos del Nirvana",     "active",  5, 15, 3, ["spir_act_lotus"],     ["spiritual", "arcane", "hybrid"], 11.5, 44, "sword_rain", {"damage_mult": 3.25, "strikes": 7}, "Materializa un enjambre de espadas astrales desde el plano etéreo."),
            ("spir_pas_trans",   "Consciencia Trascendente",   "passive", 5, 16, 3, ["spir_pas_flow"],      ["spiritual", "arcane", "hybrid"], 0.0, 0, "passive", {"cdr_add": 0.07, "energy_regen_pct": 0.20}, "Pensamiento acelerado (+7% Reducción CD, +20% Regen Energía)."),
            ("spir_act_genesis", "Despertar del Alma Primigenia", "active", 6, 20, 4, ["spir_act_zenith"],  ["spiritual", "hybrid"], 14.0, 54, "nova_burst", {"damage_mult": 3.95, "heal_pct": 0.15, "radius": 6.8}, "Libera la totalidad del aura espiritual de la espada reencarnada."),
            ("spir_pas_eternal", "Vínculo Inmortal",           "passive", 6, 21, 4, ["spir_pas_trans"],     ["spiritual", "hybrid"], 0.0, 0, "passive", {"soul_absorption_add": 0.25, "move_speed_pct": 0.10, "attack_speed_pct": 0.10}, "Cosecha espiritual suprema (+25% Alma, +10% Vel. Mov y Ataque)."),
        ],
    },
    {
        "id": "defense_survival",
        "name": "Defensa y Supervivencia",
        "icon": "❖",
        "color": "#eab308",
        "description": "Égidas de corteza férrea, contragolpes sagrados, regeneración de savia vital y resistencia indomable.",
        "skills": [
            ("def_act_bark",     "Égida de Corteza Viva",      "active",  1, 1,  1, [],                     [],                    7.0,  18, "aegis_barrier",   {"heal_pct": 0.10, "damage_mult": 1.10, "radius": 3.6}, "Endurece la guarda repeliendo enemigos cercanos y restaurando 10% PV."),
            ("def_pas_roots",    "Raíces de Roble Férreo",     "passive", 1, 1,  1, [],                     [],                    0.0,   0, "passive",         {"max_hp_pct": 0.10, "defense_add": 4.0}, "Refuerza la estructura interna (+10% Vida Máxima, +4 Defensa)."),
            ("def_act_parry",    "Contragolpe del Santuario",  "active",  2, 3,  1, ["def_act_bark"],       [],                    6.5,  22, "shockwave",       {"damage_mult": 1.70, "radius": 3.8}, "Desvía la presión hostil devolviendo un tajo circular contundente."),
            ("def_pas_sap",      "Savia Regeneradora",         "passive", 2, 4,  1, ["def_pas_roots"],      [],                    0.0,   0, "passive",         {"max_hp_pct": 0.08, "elemental_resistance_add": 0.06}, "Sella grietas en la hoja (+8% Vida Máx, +6% Resistencia Elemental)."),
            ("def_act_bastion",  "Baluarte de Bronce Antiguo", "active",  3, 6,  2, ["def_act_parry"],      [],                    8.5,  28, "aegis_barrier",   {"heal_pct": 0.14, "damage_mult": 1.65, "radius": 4.4}, "Invoca anillos protectores que restauran 14% PV e impactan el área."),
            ("def_pas_ward",     "Templado Inquebrantable",    "passive", 3, 7,  2, ["def_pas_sap"],        [],                    0.0,   0, "passive",         {"defense_add": 9.0, "elemental_resistance_add": 0.07}, "Incrementa +9 Defensa y +7% Resistencia Elemental."),
            ("def_act_halo",     "Custodia Radiante",          "active",  4, 10, 2, ["def_act_bastion"],    ["blessed", "spiritual", "hybrid"], 9.5, 34, "aegis_barrier", {"heal_pct": 0.18, "damage_mult": 2.20, "radius": 5.2}, "Consagra el terreno con luz protectora que sana 18% PV y abrasa demonios."),
            ("def_pas_aegis",    "Coraza de Reliquia",         "passive", 4, 11, 2, ["def_pas_ward"],       [],                    0.0,   0, "passive",         {"max_hp_pct": 0.14, "defense_add": 12.0}, "Densidad mineral legendaria (+14% Vida Máx, +12 Defensa)."),
            ("def_act_fortress", " Ciudadela del Sol Invicto", "active",  5, 15, 3, ["def_act_halo"],       ["blessed", "hybrid"], 12.0, 44, "aegis_barrier",   {"heal_pct": 0.22, "damage_mult": 2.85, "radius": 6.0}, "Despliega una cúpula solar que restaura 22% PV y castiga agresores."),
            ("def_pas_immortal", "Núcleo Indestructible",      "passive", 5, 16, 3, ["def_pas_aegis"],      ["blessed", "spiritual", "hybrid"], 0.0, 0, "passive", {"max_hp_pct": 0.16, "elemental_resistance_add": 0.10}, "El núcleo resiste golpes letales (+16% Vida Máx, +10% Res. Elemental)."),
            ("def_act_sanctum",  "Égida Eterna de Creación",   "active",  6, 20, 4, ["def_act_fortress"],   ["blessed", "hybrid"], 14.5, 52, "aegis_barrier",   {"heal_pct": 0.28, "damage_mult": 3.50, "radius": 6.6}, "Santuario absoluto de preservación divina y juicio defensivo."),
            ("def_pas_titan",    "Existencia Inamovible",      "passive", 6, 21, 4, ["def_pas_immortal"],   ["blessed", "hybrid"], 0.0, 0, "passive", {"max_hp_pct": 0.22, "defense_add": 22.0}, "Fortaleza suprema (+22% Vida Máx, +22 Defensa)."),
        ],
    },
    {
        "id": "curses_absorption",
        "name": "Maldiciones y Absorción",
        "icon": "☠",
        "color": "#f43f5e",
        "description": "Drenaje sanguíneo, heridas abisales, devoración de esencia enemiga y pactos de alto riesgo.",
        "skills": [
            ("cur_act_bite",     "Mordisco Carmesí",           "active",  1, 1,  1, [],                     [],                    5.5,  18, "crimson_cleave",  {"damage_mult": 1.50, "lifesteal_bonus": 0.12}, "Tajo voraz que drena vitalidad directa de las presas alcanzadas."),
            ("cur_pas_thirst",   "Sed de Esencia Oscura",      "passive", 1, 1,  1, [],                     [],                    0.0,   0, "passive",         {"life_steal_add": 0.03, "physical_damage_pct": 0.05}, "Otorga +3% Robo de Vida y +5% Daño Físico."),
            ("cur_act_bleed",    "Espina Desangradora",        "active",  2, 3,  1, ["cur_act_bite"],       [],                    6.5,  24, "wave_projectile", {"damage_mult": 1.85, "speed": 23.0}, "Dispara una astilla maldita que abre hemorragias profundas."),
            ("cur_pas_venom",    "Miasma Corrosivo",           "passive", 2, 4,  1, ["cur_pas_thirst"],     [],                    0.0,   0, "passive",         {"status_chance_add": 0.09, "armor_penetration_add": 0.05}, "Corroe armaduras (+9% Prob. Estado, +5% Penetración)."),
            ("cur_act_reap",     "Guadaña Devoraalmas",        "active",  3, 6,  2, ["cur_act_bleed"],      [],                    8.0,  30, "crimson_cleave",  {"damage_mult": 2.30, "lifesteal_bonus": 0.16}, "Barrido semicircular que absorbe vigor de cada enemigo herido."),
            ("cur_pas_pact",     "Pacto de Sangre y Filo",     "passive", 3, 7,  2, ["cur_pas_venom"],      ["cursed", "arcane", "hybrid"], 0.0, 0, "passive", {"physical_damage_pct": 0.14, "crit_damage_add": 0.20, "max_hp_pct": -0.05}, "Sacrifica 5% PV máx a cambio de +14% Daño Físico y +20% Daño Crítico."),
            ("cur_act_abyss",    "Ruptura del Vacío",          "active",  4, 10, 2, ["cur_act_reap"],       ["cursed", "arcane", "hybrid"], 9.5, 36, "nova_burst", {"damage_mult": 2.85, "radius": 5.2}, "Implosiona sombras abisales que desgarran la realidad cercana."),
            ("cur_pas_hunger",   "Hambre Insaciable",          "passive", 4, 11, 2, ["cur_pas_pact"],       ["cursed", "hybrid"],  0.0,   0, "passive",         {"life_steal_add": 0.05, "soul_absorption_add": 0.15}, "Drena +5% Robo de Vida adicional y +15% Esencia de Alma."),
            ("cur_act_eclipse",  "Festín del Eclipse Negro",   "active",  5, 15, 3, ["cur_act_abyss"],      ["cursed", "hybrid"],  11.5, 46, "crimson_cleave",  {"damage_mult": 3.55, "lifesteal_bonus": 0.22}, "Desgarro carmesí masivo que convierte la agonía enemiga en poder."),
            ("cur_pas_doom",     "Marca de Extinción",         "passive", 5, 16, 3, ["cur_pas_hunger"],     ["cursed", "hybrid"],  0.0,   0, "passive",         {"crit_chance_add": 0.07, "armor_penetration_add": 0.12}, "Otorga +7% Crítico y +12% Penetración de Armadura."),
            ("cur_act_devour",   "Apocalipsis Devorador",      "active",  6, 20, 4, ["cur_act_eclipse"],    ["cursed", "hybrid"],  14.0, 58, "sword_rain",      {"damage_mult": 4.25, "strikes": 7}, "Desata lanzas de oscuridad hambrienta sobre todo el campo."),
            ("cur_pas_abyss_lord","Señor de la Hoja Abisal",   "passive", 6, 21, 4, ["cur_pas_doom"],       ["cursed", "hybrid"],  0.0,   0, "passive",         {"physical_damage_pct": 0.20, "life_steal_add": 0.06, "crit_damage_add": 0.30}, "Cúspide maldita (+20% Daño Físico, +6% Robo de Vida, +30% Daño Crítico)."),
        ],
    },
    {
        "id": "legendary_powers",
        "name": "Poderes Legendarios",
        "icon": "♛",
        "color": "#c084fc",
        "description": "Artes soberanas de era superior, lluvia de espadas celestiales, dominios arcanos y apoteosis.",
        "skills": [
            ("ultimate",         "Lluvia de Espadas Celestiales", "active", 1, 1, 1, [],                    [],                    12.0, 35, "sword_rain",      {"damage_mult": 2.40, "strikes": 6}, "Invoca espadas de luz astral que caen en círculo aniquilando hordas."),
            ("leg_pas_spark",    "chispa de Mito",             "passive", 1, 2,  1, [],                     [],                    0.0,   0, "passive",         {"physical_damage_pct": 0.05, "elemental_damage_pct": 0.05}, "Despierta el linaje mítico (+5% Daño Físico y +5% Daño Elemental)."),
            ("leg_act_astro",    "Rayo de Astrolabio",         "active",  2, 5,  2, ["ultimate"],           [],                    10.0, 32, "wave_projectile", {"damage_mult": 2.35, "speed": 28.0}, "Dispara un haz de geometría arcana pura de largo alcance."),
            ("leg_pas_rune",     "Inscripción de Soberanía",   "passive", 2, 5,  2, ["leg_pas_spark"],      [],                    0.0,   0, "passive",         {"cdr_add": 0.05, "max_energy_add": 25}, "Reduce enfriamientos 5% y otorga +25 Energía Máxima."),
            ("leg_act_judgment", "Fulgor del Trono Solar",     "active",  3, 9,  2, ["leg_act_astro"],      ["blessed", "arcane", "hybrid"], 11.5, 40, "nova_burst", {"damage_mult": 2.95, "radius": 5.8}, "Corona radiante que juzga a todas las criaturas alrededor."),
            ("leg_pas_crown",    "Autoridad de Reliquia Viva", "passive", 3, 9,  2, ["leg_pas_rune"],       [],                    0.0,   0, "passive",         {"crit_chance_add": 0.05, "soul_absorption_add": 0.12}, "Presencia imperial (+5% Crítico, +12% Absorción de Alma)."),
            ("leg_act_rift",     "Corte Dimensional",          "active",  4, 13, 3, ["leg_act_judgment"],   ["arcane", "cursed", "spiritual", "hybrid"], 12.0, 46, "wave_projectile", {"damage_mult": 3.45, "speed": 30.0}, "Rasga el tejido mismo del espacio proyectando una fisura letal."),
            ("leg_pas_cosmos",   "Núcleo de Constelación",     "passive", 4, 14, 3, ["leg_pas_crown"],      ["arcane", "spiritual", "hybrid"], 0.0, 0, "passive", {"elemental_damage_pct": 0.15, "cdr_add": 0.06}, "Alinea las runas con el firmamento (+15% Daño Elemental, +6% CDR)."),
            ("leg_act_domain",   "Dominio de las Mil Espadas", "active",  5, 17, 3, ["leg_act_rift"],       [],                    14.0, 54, "sword_rain",      {"damage_mult": 3.90, "strikes": 8}, "Despliega un campo soberano donde llueven hojas de todas las eras."),
            ("leg_pas_duality",  "convergencia Luz-Abismo",    "passive", 5, 18, 3, ["leg_pas_cosmos"],     ["blessed", "cursed", "hybrid"], 0.0, 0, "passive", {"physical_damage_pct": 0.12, "elemental_damage_pct": 0.12, "crit_damage_add": 0.20}, "Armoniza energías opuestas (+12% Físico, +12% Elemental, +20% Crít)."),
            ("leg_act_apotheosis","Apoteosis: Espada del Génesis", "active", 6, 22, 4, ["leg_act_domain"],  [],                    16.0, 65, "sword_rain",      {"damage_mult": 4.80, "strikes": 10}, "Técnica definitiva de Era VI: juicio ontológico de la Espada Suprema."),
            ("leg_pas_supreme",  "Existencia Suprema",         "passive", 6, 23, 4, ["leg_pas_duality"],    [],                    0.0,   0, "passive",         {"physical_damage_pct": 0.18, "elemental_damage_pct": 0.18, "max_hp_pct": 0.15, "cdr_add": 0.06}, "Culminación de las 24 evoluciones (+18% Daño Total, +15% PV, +6% CDR)."),
        ],
    },
]

skills_list = []
for tdef in TREE_DEFS:
    tid = tdef["id"]
    for idx, s_tuple in enumerate(tdef["skills"]):
        (sid, sname, stype, tier, min_stage, cost, prereqs, lineages, cd, ecost, arch, payload, desc) = s_tuple
        # Capitalize first letter cleanly
        sname = sname.strip()
        sname = sname[0].upper() + sname[1:]
        skills_list.append({
            "id": sid,
            "name": sname,
            "tree_id": tid,
            "tree_name": tdef["name"],
            "type": stype,
            "tier": tier,
            "order_in_tree": idx + 1,
            "min_stage": min_stage,
            "cost_points": cost,
            "prereq_skills": prereqs,
            "allowed_lineages": lineages,
            "cooldown": cd,
            "energy_cost": ecost,
            "combat_archetype": arch,
            "effect_data": payload,
            "description": desc,
        })

assert len(skills_list) == 72, f"Expected 72 skills, got {len(skills_list)}"
assert sum(1 for s in skills_list if s["type"] == "active") == 36
assert sum(1 for s in skills_list if s["type"] == "passive") == 36


# ==============================================================================
# PART 2: BUILD THE 24-STAGE PERMANENT EVOLUTION GRAPH (ALL 6 ERAS, ZERO DEAD ENDS)
# ==============================================================================
# Design of the 24-Stage Directed Acyclic Graph:
# - Stage 01 (Era I): 1 Origin Root (`wood_origin_ancestral_blade` — Pilot #01 GLB Verified!) -> branches into 3 Stage-02 forms!
# - Stage 02 (Era I): 3 Awakening Forms (Verdant Living Wood, Mineralized Copper-Root, Charred Ash-Thorn) -> branch into 4 Stage-03 forms!
# - Stage 03 (Era I): 4 Proto-Lineage Forms -> branch into 5 Stage-04 Threshold Forms!
# - Stages 04..24: At EVERY stage from 04 through 24, all 5 core persistent lineages
#   (`blessed`, `cursed`, `elemental`, `spiritual`, `arcane`) maintain their own dedicated primary & specialist forms,
#   PLUS Hybrid/Secret forms at milestone stages (08, 12, 16, 20, 24), and EVERY node at stage `s < 24` offers
#   between **2 and 5 permanent evolution choices** (`next_forms` count in `[2..5]`)!

# Bespoke Stage-02 GLBs verified in Godot 4.4 (Studio Lexair approved production batch)
STAGE02_GLB = {
    "wood_verdant_living_bough": "res://assets/models/swords/verdant_bough/sword_02_verdant_bough.glb",
    "wood_mineral_copper_root": "res://assets/models/swords/copper_root/sword_02_copper_root.glb",
    "wood_charred_ash_thorn": "res://assets/models/swords/ash_thorn/sword_02_ash_thorn.glb",
}

# Bespoke Stage-03 GLBs verified in Godot 4.4 (Studio Lexair approved production batch)
STAGE03_GLB = {
    "awakening_amber_sanctuary_blade": "res://assets/models/swords/amber_sanctuary/sword_03_amber_sanctuary.glb",
    "awakening_ironwood_storm_edge": "res://assets/models/swords/ironwood_storm/sword_03_ironwood_storm.glb",
    "awakening_spirit_willow_saber": "res://assets/models/swords/spirit_willow/sword_03_spirit_willow.glb",
    "awakening_bloodsap_bramble_blade": "res://assets/models/swords/bloodsap_bramble/sword_03_bramble_blade.glb",
}

# Bespoke Stage-04 GLBs verified in Godot 4.4 (Studio Lexair approved production batch)
STAGE04_GLB = {
    "awakening_sunbark_vow_greatsword": "res://assets/models/swords/sunbark_vow/sword_04_sunbark_vow.glb",
    "awakening_thornheart_hex_blade": "res://assets/models/swords/thornheart_hex/sword_04_thornheart_hex.glb",
    "awakening_fulgurite_crest_sword": "res://assets/models/swords/fulgurite_crest/sword_04_fulgurite_crest.glb",
    "awakening_jade_anima_katana": "res://assets/models/swords/jade_anima/sword_04_jade_anima.glb",
    "awakening_runebark_codex_blade": "res://assets/models/swords/runebark_codex/sword_04_runebark_codex.glb",
}

STAGE_TITLES = {
    # Era I: Despertar (01-04)
    1: [
        ("wood_origin_ancestral_blade", "origin", "balanced", "Espada de Madera Ancestral",
         "Semilla del Despertar", "Absorbe +15% de Esencia de Alma de monstruos derrotados.",
         "Mi consciencia acaba de despertar dentro del duramen cálido de un roble sagrado.", False),
    ],
    2: [
        ("wood_verdant_living_bough", "origin", "balanced", "Hoja de Brote Viviente",
         "Savia Latente", "Regenera energía espiritual suavemente al caminar por la arena.",
         "Mis raíces se estiran con vida propia; siento la luz y el maná del bosque.", False),
        ("wood_mineral_copper_root", "elemental", "heavy", "Espada de Raíz Cobriza",
         "Vetas Voltaicas", "Los golpes cargan estática mineral en la corteza.",
         "He absorbido vetas de cobre ardiente de la tierra; mi filo vibra con chispas.", False),
        ("wood_charred_ash_thorn", "cursed", "swift", "Espada de Espino Calcinado",
         "Brasa Rencorosa", "Aumenta el daño crítico contra presas heridas.",
         "El fuego oscuro quemó mi corteza exterior, dejando un filo negro sediento de batalla.", False),
    ],
    3: [
        ("awakening_amber_sanctuary_blade", "blessed", "heavy", "Hoja de Ámbar de Santuario",
         "Resina Consagrada", "Reduce el daño recibido de élites y purifica miasmas.",
         "La savia dorada cristalizó sobre mi núcleo formando un escudo cálido e incorruptible.", False),
        ("awakening_ironwood_storm_edge", "elemental", "balanced", "Filo de Palo Férreo y Trueno",
         "Pararrayos Natural", "Canaliza descargas eléctricas al tercer corte consecutivo.",
         "Mi madera pesa ahora como hierro forjado y llama al relámpago en cada tajo.", False),
        ("awakening_spirit_willow_saber", "spiritual", "swift", "Sable de Sauce Espiritual",
         "Susurro Etéreo", "Incrementa la velocidad de levitación y evasión astral.",
         "Floto sin esfuerzo; escucho el eco de mil espadachines antiguos en el viento.", False),
        ("awakening_bloodsap_bramble_blade", "cursed", "swift", "Hoja de Zarza Sanguina",
         "Espinas Voraces", "Drena una fracción de vitalidad al provocar golpes críticos.",
         "Mis espinas beben la esencia caída para fortalecer mi propio núcleo consciente.", False),
    ],
    4: [
        ("awakening_sunbark_vow_greatsword", "blessed", "heavy", "Mandoble del Voto Heliófilo",
         "Juramento del Alba", "Otorga defensa sagrada adicional al combatir hordas.",
         "Al cruzar el umbral del Despertar, juro proteger este mundo con luz inquebrantable.", False),
        ("awakening_thornheart_hex_blade", "cursed", "swift", "Hoja Maldita Corazón de Espina",
         "Pacto de Agonía", "Convierte la furia del combate en penetración de armadura.",
         "Rechazo la piedad; devoraré a los señores oscuros con su propia maldición.", False),
        ("awakening_fulgurite_crest_sword", "elemental", "balanced", "Espada Cresta de Fulgurita",
         "Núcleo Igneo-Voltaico", "Imbuye cada onda cortante con fuego y relámpago.",
         "Cristales de rayo solidificado recorren mi acanaladura con furia primordial.", False),
        ("awakening_jade_anima_katana", "spiritual", "swift", "Katana Ánima de Jade",
         "Pulso de Reencarnación", "Acelera la ganancia de Esencia de Evolución.",
         "Mi alma y mi hoja son una sola línea pura de jade translúcido.", False),
        ("awakening_runebark_codex_blade", "arcane", "mystic", "Espada Códice de Corteza Rúnica",
         "Glifos Automáticos", "Reduce el enfriamiento de todas las artes activas.",
         "Inscribo ecuaciones arcanas sobre mi propia superficie para doblar las leyes mágicas.", False),
    ],
}

# Systematic rich Spanish canon templates for Stages 5..24 across the 5 Lineages + Milestone Hybrids!
LINEAGE_STAGE_NAMES = {
    "blessed": {
        5:  ("blessed_solar_initiate_blade",       "Espada Iniciada del Sol Naciente",      "Luz Purificadora"),
        6:  ("blessed_auric_bastion_claymore",     "Claymore Bastión Áurico",               "Muro de Oro Vivo"),
        7:  ("blessed_seraph_wing_longsword",      "Espada Larga Ala de Serafín",           "Pluma Candente"),
        8:  ("blessed_radiant_covenant_greatsword","Mandoble de la Alianza Radiante",       "Sello del Santuario"),
        9:  ("blessed_dawnbreaker_templar_blade",  "Hoja Templaria Rompealbas",             "Juicio Matutino"),
        10: ("blessed_halcyon_aegis_broadsword",   "Espada Ancha Égida Alción",             "Gracia Inmortal"),
        11: ("blessed_solstice_martyr_relic",      "Reliquia Solar del Solsticio",          "Llama de Redención"),
        12: ("blessed_archangel_verdict_claymore", "Claymore Veredicto de Arcángel",        "Sentencia Celeste"),
        13: ("blessed_empyrean_halo_blade",        "Hoja Trascendente del Halo Empíreo",    "Corona Incorrupta"),
        14: ("blessed_sanctified_sunforge_sword",  "Espada Forjasol Santificada",           "Crisol Sagrado"),
        15: ("blessed_valkyrie_luminary_edge",     "Filo Luminar de Valquiria",             "Canto de Victoria"),
        16: ("blessed_celestial_throne_greatsword","Mandoble del Trono Celestial",          "Autoridad Divina"),
        17: ("blessed_sovereign_helios_blade",     "Espada Soberana de Helios",             "Dominio del Mediodía"),
        18: ("blessed_immortal_cherubim_brand",    "Blandón Inmortal de Querubín",          "Fuego Custodio"),
        19: ("blessed_golden_creation_edict",      "Edicto Dorado de la Creación",          "Palabra de Luz"),
        20: ("blessed_pantheon_sun_monarch",       "Monarca Solar del Panteón",             "Rey de los Cielos"),
        21: ("blessed_supreme_lux_aeterna",        "Espada Suprema Lux Aeterna",            "Alba sin Fin"),
        22: ("blessed_divine_genesis_sacrament",   "Sacramento Divino del Génesis",         "Origen Radiante"),
        23: ("blessed_omnipresent_dawn_sovereign", "Soberana Omnipresente del Amanecer",    "Luz Absoluta"),
        24: ("blessed_final_godsword_sol_invictus","Teoespada Definitiva: Sol Invictus",    "Apoteosis Solar Eterna"),
    },
    "cursed": {
        5:  ("cursed_obsidian_fang_blade",         "Espada Colmillo de Obsidiana",          "Hambre Nocturna"),
        6:  ("cursed_crimson_reaver_cleaver",      "Hendidora Segadora Carmesí",            "Cosecha Roja"),
        7:  ("cursed_nightmare_chitin_sword",      "Espada Quitina de Pesadilla",           "Terror Abisal"),
        8:  ("cursed_bloodmoon_pact_greatsword",   "Mandoble del Pacto Luna Sangrienta",    "Tributo Vital"),
        9:  ("cursed_abyssal_guillotine_edge",     "Filo Guillotina del Abismo",            "Corte Implacable"),
        10: ("cursed_soul_devourer_brand",         "Blandón Devorador de Almas",            "Pozo de Ánimas"),
        11: ("cursed_malakor_usurper_thorn",       "Espina Usurpadora de Malakor",          "Sangre de Señor Demonio"),
        12: ("cursed_hellfire_executioner_blade",  "Hoja Verdugo de Fuego Infernal",        "Ceniza Condenada"),
        13: ("cursed_voidscar_transcendent_sword", "Espada Trascendente Cicatriz del Vacío","Herida Cósmica"),
        14: ("cursed_dread_leviathan_fang",        "Colmillo Aterrador de Leviatán",        "Presión de Fosa"),
        15: ("cursed_necrophage_emperor_saber",    "Sable Emperador Necrófago",             "Trono de Hueso"),
        16: ("cursed_eclipse_harbinger_claymore",  "Claymore Heraldo del Eclipse",          "Sol Devorado"),
        17: ("cursed_sovereign_tartarus_edge",     "Filo Soberano del Tártaro",             "Cadena Rota"),
        18: ("cursed_calamity_bloodgod_sword",     "Espada Calamidad del Dios Sangriento",  "Marea Escarlata"),
        19: ("cursed_oblivion_maw_greatsword",     "Mandoble Fauces del Olvido",            "Devoración Total"),
        20: ("cursed_abyss_monarch_apocrypha",     "Apócrifa del Monarca Abisal",           "Reino sin Luz"),
        21: ("cursed_supreme_nihil_vorpal",        "Espada Suprema Nihil Vorpal",           "Fin de la Materia"),
        22: ("cursed_primordial_chaos_scytheblade","Hojaguadaña del Caos Primordial",       "Entropía Viva"),
        23: ("cursed_endbringer_black_horizon",    "Horizonte Negro Portador del Fin",      "Singularidad Voraz"),
        24: ("cursed_final_abyss_sword_agnarok",   "Archiespada Abisal: Fin de los Dioses", "Apoteosis del Vacío"),
    },
    "elemental": {
        5:  ("elemental_tempest_copper_blade",     "Espada Cobriza de Tempestad",           "Chispa Ciclónica"),
        6:  ("elemental_glacier_fang_longsword",   "Espada Larga Colmillo de Glaciar",      "Cero Helado"),
        7:  ("elemental_magma_vein_broadsword",    "Espada Ancha Vena de Magma",            "Pulso Volcánico"),
        8:  ("elemental_thunderlord_fulgur_edge",  "Filo Fúlgur del Señor del Trueno",      "Descarga Celeste"),
        9:  ("elemental_twin_monsoon_saber",       "Sable Gemelo del Monzón",               "Viento Cortante"),
        10: ("elemental_permafrost_prism_claymore","Claymore Prisma de Permafrost",         "Espejo Ártico"),
        11: ("elemental_pyroclasm_heart_greatsword","Mandoble Corazón Piroclástico",        "Erupción Interna"),
        12: ("elemental_maelstrom_triad_blade",    "Hoja Tríada del Maelstrom",             "Vórtice Triple"),
        13: ("elemental_transcendent_aurora_sword","Espada Trascendente de Aurora Polar",   "Velo Magnético"),
        14: ("elemental_tectonic_mantle_breaker",  "Quebrantamantos Tectónico",             "Falla Continental"),
        15: ("elemental_plasma_typhoon_katana",    "Katana Tifón de Plasma",                "Ionización Pura"),
        16: ("elemental_cataclysm_fourfold_relic", "Reliquia Cuádruple del Cataclismo",     "Cuatro Pilares"),
        17: ("elemental_sovereign_supercell_edge", "Filo Soberano de Supercelda",           "Ojo del Huracán"),
        18: ("elemental_starfire_prominence_blade","Hoja Prominencia de Fuego Estelar",     "Corona Ígnea"),
        19: ("elemental_absolute_zero_monolith",   "Monolito del Cero Absoluto",            "Quietud Térmica"),
        20: ("elemental_primordial_worldstorm",    "Tormenta-Mundo Primordial",             "Clima Soberano"),
        21: ("elemental_supreme_genesis_tempest",  "Espada Suprema Tempestad del Génesis",  "Primer Relámpago"),
        22: ("elemental_nebula_furnace_greatsword","Mandoble Fragua de Nebulosa",           "Fusión Estelar"),
        23: ("elemental_omni_cataclysm_arbiter",   "Árbitro Omnicataclísmico",              "Ley Natural Viva"),
        24: ("elemental_final_primordial_aeon",    "Espada Primordial Definitiva: Eón",     "Apoteosis Elemental"),
    },
    "spiritual": {
        5:  ("spiritual_silver_anima_saber",       "Sable de Plata Ánima",                  "Eco de Plata"),
        6:  ("spiritual_mistwalker_bamboo_katana", "Katana Caminante de la Niebla",         "Paso Inmaterial"),
        7:  ("spiritual_moonlit_lotus_blade",      "Hoja Loto de Plenilunio",               "Rocío Astral"),
        8:  ("spiritual_ancestral_chorus_sword",   "Espada Coro de los Ancestros",          "Cien Voces"),
        9:  ("spiritual_phantom_sever_nodachi",    "Nodachi Cortafantasmas",                "Filo Etéreo"),
        10: ("spiritual_jade_chakram_soulblade",   "Espada-Alma de Jade y Chakram",         "Rueda del Ki"),
        11: ("spiritual_reincarnated_saint_edge",  "Filo del Santo Reencarnado",            "Memoria Intacta"),
        12: ("spiritual_nirvana_mirror_katana",    "Katana Espejo del Nirvana",             "Mente sin Sombra"),
        13: ("spiritual_transcendent_worldtree_branch","Rama Trascendente del Árbol Mundo", "Raíz del Cosmos"),
        14: ("spiritual_astral_wind_sovereign",    "Espada Viento Astral",                  "Vuelo Infinito"),
        15: ("spiritual_karma_weaver_longsword",   "Espada Larga Tejedora del Karma",       "Hilo del Destino"),
        16: ("spiritual_samsara_lotus_relic",      "Reliquia Loto del Samsara",             "Rueda Eterna"),
        17: ("spiritual_sovereign_akashic_blade",  "Hoja Soberana de Akasha",               "Registro del Alma"),
        18: ("spiritual_ethereal_immortal_fang",   "Colmillo Etéreo del Inmortal",          "Aliento Puro"),
        19: ("spiritual_celestial_harmony_katana", "Katana de la Armonía Celeste",          "Unión Cielo-Tierra"),
        20: ("spiritual_soul_monarch_transcendence","Monarca Espiritual de la Trascendencia","Rey de las Ánimas"),
        21: ("spiritual_supreme_anima_mundi",      "Espada Suprema Anima Mundi",            "Alma del Mundo"),
        22: ("spiritual_origin_breath_blade",      "Hoja del Primer Aliento",               "Espíritu Puro"),
        23: ("spiritual_boundless_enlightenment",  "Espada Iluminación sin Fronteras",      "Despertar Total"),
        24: ("spiritual_final_oversoul_yggdrasil", "Espada Consciente Suprema: Yggdrasil",  "Apoteosis del Alma"),
    },
    "arcane": {
        5:  ("arcane_crystal_cipher_sword",        "Espada Cifrada de Cristal",             "Geometría Viva"),
        6:  ("arcane_astrolabe_ring_blade",        "Hoja Anillo de Astrolabio",             "Órbita Calculada"),
        7:  ("arcane_aether_conduit_rapier",       "Estoque Conducto de Éter",              "Vena de Maná"),
        8:  ("arcane_grimoire_monolith_greatsword","Mandoble Monolito de Grimorio",         "Siete Sellos"),
        9:  ("arcane_spellweaver_prism_edge",      "Filo Prisma Tejehechizos",              "Doble Conjuro"),
        10: ("arcane_chronoglass_paradox_saber",   "Sable Paradoja de Cronocristal",        "InstanteRepetido"),
        11: ("arcane_starlight_glyph_claymore",    "Claymore Glifo de Luz Estelar",         "Runa Sideral"),
        12: ("arcane_archmage_singularity_blade",  "Hoja Singularidad de Archimago",        "Colapso Arcano"),
        13: ("arcane_transcendent_axiom_sword",    "Espada Trascendente del Axioma",        "Ley Reescrita"),
        14: ("arcane_voidmath_tesseract_edge",     "Filo Teseracto de Vacío Geométrico",    "Cuarta Dimensión"),
        15: ("arcane_constellation_orrery_brand",  "Blandón Planetario de Constelaciones",  "Mapa Celeste"),
        16: ("arcane_cosmic_library_relic",        "Reliquia de la Biblioteca Cósmica",     "Saber Infinito"),
        17: ("arcane_sovereign_chrono_arbiter",    "Árbitro Soberano del Tiempo",           "Reloj Eterno"),
        18: ("arcane_quasar_horizon_greatsword",   "Mandoble Horizonte de Cuásar",          "Pulso Galáctico"),
        19: ("arcane_grand_theorem_runeblade",     "Hoja Rúnica del Gran Teorema",          "Verdad Absoluta"),
        20: ("arcane_astral_monarch_logos",        "Monarca Astral del Logos",              "Arquitecto Mágico"),
        21: ("arcane_supreme_omega_codex",         "Espada Suprema Códice Omega",           "Última Fórmula"),
        22: ("arcane_multiverse_loom_edge",        "Filo Telar del Multiverso",             "Cuerda Cósmica"),
        23: ("arcane_omniscient_star_architect",   "Arquitecta Omnisciente de Estrellas",   "Mente Universal"),
        24: ("arcane_final_logos_eternity_sword",  "Espada Arcana Definitiva: Logos Eterno","Apoteosis Cósmica"),
    },
}

# Hybrid / Secret Convergence Forms at Era Climaxes (Stages 8, 12, 16, 20, 24)!
HYBRID_STAGE_FORMS = {
    8:  ("hybrid_twilight_covenant_blade",    ["blessed", "cursed"],    "Espada Híbrida del Pacto Crepuscular",
         "Equilibrio Luz-Sombra", "Combina robo de vida abisal con escudos solares purificadores.",
         "He reconciliado la luz del santuario y la sombra voraz dentro de mi propio núcleo."),
    12: ("hybrid_stormspirit_dragon_katana",  ["elemental", "spiritual"],"Katana Secreta Dragón de Tormenta y Alma",
         "Vuelo del Dragón Astral", "Cada Paso Astral descarga relámpagos espirituales.",
         "Mi espíritu galopa sobre el trueno como un dragón ancestral reencarnado en acero."),
    16: ("hybrid_celestial_abyss_eclipse",    ["blessed", "cursed", "arcane"], "Reliquia Secreta: Eclipse de Sol y Abismo",
         "Corona del Eclipse", "Duplica la potencia de impactos críticos y ondas arcanas.",
         "Ni los dioses ni los demonios pueden reclamarme; soy el eclipse que gobierna a ambos."),
    20: ("hybrid_worldtree_cosmos_sovereign", ["spiritual", "arcane", "elemental"], "Soberana Híbrida: Árbol Cósmico",
         "Raíces Siderales", "Regenera salud y energía continuamente mientras invoca estrellas.",
         "Mis raíces de madera ancestral abrazan ahora galaxias enteras sin olvidar mi primer despertar."),
    24: ("hybrid_true_isekai_protagonist_godsword", ["blessed", "cursed", "elemental", "spiritual", "arcane"],
         "Forma Secreta Verdadera: Espada Consciente del Origen Eterno",
         "Protagonista Inmortal", "Síntesis suprema de las 6 Eras: daño, defensa, alma y magia trascendentes.",
         "Recuerdo cada tajo desde que fui una humilde Espada de Madera Ancestral; soy la Espada Eterna."),
}

forms_by_stage = {s: [] for s in range(1, 25)}
forms_dict = {}


def make_unlock_conditions(stage: int, lineage: str, is_hybrid: bool = False) -> dict:
    min_level = 1 if stage == 1 else (stage - 1) * 3
    min_evo_xp = 0 if stage == 1 else int(round(40 * ((stage - 1) ** 1.55)))
    req_mats = {}
    if stage >= 2 and stage <= 5:
        req_mats = {"slime_gel": min(4, stage)}
    elif stage >= 6 and stage <= 10:
        req_mats = {"copper_ingot": 2, "goblin_fang": 2}
    elif stage >= 11 and stage <= 16:
        req_mats = {"cursed_bone": 2, "orc_tusk": 2}
    elif stage >= 17:
        req_mats = {"drake_scale": 2, "demon_heart": 1}

    req_skills = []
    if stage >= 5:
        default_skill_map = {
            "blessed": "def_act_bark",
            "cursed": "cur_act_bite",
            "elemental": "swordWave",
            "spiritual": "dash",
            "arcane": "ultimate",
            "hybrid": "whirlwind",
        }
        sk = default_skill_map.get(lineage, "whirlwind")
        req_skills.append(sk)
    if is_hybrid and stage >= 12:
        req_skills.append("leg_pas_spark")

    req_events = []
    if stage >= 8:
        req_events.append("wave_3_cleared")
    if stage >= 13 or (is_hybrid and stage >= 8):
        req_events.append("defeated_malakor")

    return {
        "min_level": min_level,
        "min_evolution_xp": min_evo_xp,
        "required_materials": req_mats,
        "required_skills": req_skills,
        "required_events": req_events,
    }


# Add Stages 1..4
for st, entries in STAGE_TITLES.items():
    era_info = era_for_stage(st)
    for (fid, lin, bias, name, pas_name, pas_desc, note, is_hyb) in entries:
        is_pilot = (fid == "wood_origin_ancestral_blade")
        lmeta = LINEAGES[lin]
        fobj = {
            "id": fid,
            "legacy_alias": "wood" if is_pilot else "",
            "name": name,
            "stage": st,
            "era": era_info["era"],
            "era_id": era_info["id"],
            "era_name": era_info["name"],
            "subtitle": f"{era_info['name']} • Etapa {st:02d}/24",
            "lineage": lin,
            "lineage_name": lmeta["name"],
            "is_hybrid": is_hyb,
            "is_secret": is_hyb,
            "protagonist_identity": "sentient_sword",
            "protagonist_consciousness_note": note,
            "description": f"{note} Conserva intacta su identidad de espada consciente protagonista.",
            "passive_name": pas_name,
            "passive_description": pas_desc,
            "base_stats": compute_base_stats(st, lin, bias),
            "unlock_conditions": make_unlock_conditions(st, lin, is_hyb),
            "blade_color": lmeta["blade_color"],
            "edge_color": lmeta["edge_color"],
            "guard_color": lmeta["guard_color"],
            "aura_color": lmeta["aura_color"],
            "slash_color": lmeta["slash_color"],
            "special_effect": lmeta["special_effect"],
            "model_path": (STAGE04_GLB[fid] if fid in STAGE04_GLB else STAGE03_GLB.get(fid, STAGE02_GLB.get(fid, "res://assets/models/swords/wood_ancestral/sword_01_wood_ancestral.glb" if is_pilot else lmeta["legacy_model"]))),
            "model_status": ("verified_stage04_glb" if fid in STAGE04_GLB else ("verified_stage03_glb" if fid in STAGE03_GLB else ("verified_stage02_glb" if fid in STAGE02_GLB else ("verified_pilot_glb" if is_pilot else "extensible_blueprint_pending_3d")))),
            "catalog_status": ("canon_approved_stage04" if fid in STAGE04_GLB else ("canon_approved_stage03" if fid in STAGE03_GLB else ("canon_approved_stage02" if fid in STAGE02_GLB else ("canon_approved_pilot" if is_pilot else "extensible_framework_node")))),
            "parent_forms": [],
            "next_forms": [],
        }
        forms_by_stage[st].append(fobj)
        forms_dict[fid] = fobj

# Add Stages 5..24 (5 Persistent Lineages + Milestone Hybrids)
CORE_LINEAGES = ["blessed", "cursed", "elemental", "spiritual", "arcane"]
BIAS_MAP = {"blessed": "heavy", "cursed": "swift", "elemental": "balanced", "spiritual": "swift", "arcane": "mystic"}

for st in range(5, 25):
    era_info = era_for_stage(st)
    for lin in CORE_LINEAGES:
        fid, name, pas_name = LINEAGE_STAGE_NAMES[lin][st]
        lmeta = LINEAGES[lin]
        note = f"Etapa {st:02d} ({era_info['name']}): mi consciencia como espada evoluciona en el {lmeta['name']}."
        fobj = {
            "id": fid,
            "legacy_alias": "",
            "name": name,
            "stage": st,
            "era": era_info["era"],
            "era_id": era_info["id"],
            "era_name": era_info["name"],
            "subtitle": f"{era_info['name']} • Etapa {st:02d}/24",
            "lineage": lin,
            "lineage_name": lmeta["name"],
            "is_hybrid": False,
            "is_secret": False,
            "protagonist_identity": "sentient_sword",
            "protagonist_consciousness_note": note,
            "description": f"{name}. Transformación permanente e irreversible de la espada protagonista en {era_info['name']}.",
            "passive_name": pas_name,
            "passive_description": f"Potencia la firma combativa del {lmeta['name']} en la Etapa {st:02d}.",
            "base_stats": compute_base_stats(st, lin, BIAS_MAP[lin]),
            "unlock_conditions": make_unlock_conditions(st, lin, False),
            "blade_color": lmeta["blade_color"],
            "edge_color": lmeta["edge_color"],
            "guard_color": lmeta["guard_color"],
            "aura_color": lmeta["aura_color"],
            "slash_color": lmeta["slash_color"],
            "special_effect": lmeta["special_effect"],
            "model_path": lmeta["legacy_model"],
            "model_status": "extensible_blueprint_pending_3d",
            "catalog_status": "extensible_framework_node",
            "parent_forms": [],
            "next_forms": [],
        }
        forms_by_stage[st].append(fobj)
        forms_dict[fid] = fobj

    if st in HYBRID_STAGE_FORMS:
        hfid, parent_lins, hname, hpas, hpas_desc, hnote = HYBRID_STAGE_FORMS[st]
        lmeta = LINEAGES["hybrid"]
        hobj = {
            "id": hfid,
            "legacy_alias": "",
            "name": hname,
            "stage": st,
            "era": era_info["era"],
            "era_id": era_info["id"],
            "era_name": era_info["name"],
            "subtitle": f"{era_info['name']} • Etapa {st:02d}/24 [HÍBRIDA SECRETA]",
            "lineage": "hybrid",
            "lineage_name": lmeta["name"],
            "hybrid_components": parent_lins,
            "is_hybrid": True,
            "is_secret": True,
            "protagonist_identity": "sentient_sword",
            "protagonist_consciousness_note": hnote,
            "description": f"{hnote} Evolución convergente secreta e irreversible.",
            "passive_name": hpas,
            "passive_description": hpas_desc,
            "base_stats": compute_base_stats(st, "hybrid", "balanced"),
            "unlock_conditions": make_unlock_conditions(st, "hybrid", True),
            "blade_color": lmeta["blade_color"],
            "edge_color": lmeta["edge_color"],
            "guard_color": lmeta["guard_color"],
            "aura_color": lmeta["aura_color"],
            "slash_color": lmeta["slash_color"],
            "special_effect": lmeta["special_effect"],
            "model_path": lmeta["legacy_model"],
            "model_status": "extensible_blueprint_pending_3d",
            "catalog_status": "extensible_framework_node",
            "parent_forms": [],
            "next_forms": [],
        }
        forms_by_stage[st].append(hobj)
        forms_dict[hfid] = hobj


# --- WIRE PERMANENT MULTI-WAY BRANCHING EDGES (2..5 OPTIONS PER NODE, 0 DEAD ENDS) ---
def connect(p_id: str, c_id: str):
    p = forms_dict[p_id]
    c = forms_dict[c_id]
    if c_id not in p["next_forms"]:
        p["next_forms"].append(c_id)
    if p_id not in c["parent_forms"]:
        c["parent_forms"].append(p_id)


# Stage 1 -> Stage 2 (3 permanent choices)
for s2 in forms_by_stage[2]:
    connect("wood_origin_ancestral_blade", s2["id"])

# Stage 2 -> Stage 3 (each Stage-2 node offers 2..3 distinct Stage-3 evolutions)
connect("wood_verdant_living_bough", "awakening_amber_sanctuary_blade")
connect("wood_verdant_living_bough", "awakening_spirit_willow_saber")
connect("wood_verdant_living_bough", "awakening_ironwood_storm_edge")

connect("wood_mineral_copper_root", "awakening_ironwood_storm_edge")
connect("wood_mineral_copper_root", "awakening_amber_sanctuary_blade")
connect("wood_mineral_copper_root", "awakening_bloodsap_bramble_blade")

connect("wood_charred_ash_thorn", "awakening_bloodsap_bramble_blade")
connect("wood_charred_ash_thorn", "awakening_ironwood_storm_edge")
connect("wood_charred_ash_thorn", "awakening_spirit_willow_saber")

# Stage 3 -> Stage 4 (each Stage-3 node offers 2..3 Stage-4 threshold evolutions, reaching all 5 lineages)
connect("awakening_amber_sanctuary_blade", "awakening_sunbark_vow_greatsword")
connect("awakening_amber_sanctuary_blade", "awakening_jade_anima_katana")
connect("awakening_amber_sanctuary_blade", "awakening_runebark_codex_blade")

connect("awakening_ironwood_storm_edge", "awakening_fulgurite_crest_sword")
connect("awakening_ironwood_storm_edge", "awakening_sunbark_vow_greatsword")
connect("awakening_ironwood_storm_edge", "awakening_runebark_codex_blade")

connect("awakening_spirit_willow_saber", "awakening_jade_anima_katana")
connect("awakening_spirit_willow_saber", "awakening_runebark_codex_blade")
connect("awakening_spirit_willow_saber", "awakening_fulgurite_crest_sword")

connect("awakening_bloodsap_bramble_blade", "awakening_thornheart_hex_blade")
connect("awakening_bloodsap_bramble_blade", "awakening_fulgurite_crest_sword")
connect("awakening_bloodsap_bramble_blade", "awakening_runebark_codex_blade")

# Stages 4..23 -> Next Stage (every node gets its core lineage continuation + 1..2 adjacent resonance/hybrid forks -> 2..4 choices!)
ADJACENT_FORKS = {
    "blessed":   ["blessed", "spiritual", "elemental"],
    "cursed":    ["cursed", "arcane", "elemental"],
    "elemental": ["elemental", "blessed", "cursed"],
    "spiritual": ["spiritual", "blessed", "arcane"],
    "arcane":    ["arcane", "spiritual", "elemental"],
    "hybrid":    ["blessed", "cursed", "spiritual", "arcane"],
}

for st in range(4, 24):
    next_st = st + 1
    next_by_lin = {f["lineage"]: f["id"] for f in forms_by_stage[next_st] if not f["is_hybrid"]}
    hybrid_next = next((f for f in forms_by_stage[next_st] if f["is_hybrid"]), None)

    for cur_f in forms_by_stage[st]:
        lin = cur_f["lineage"]
        for target_lin in ADJACENT_FORKS[lin]:
            if target_lin in next_by_lin and len(cur_f["next_forms"]) < 4:
                connect(cur_f["id"], next_by_lin[target_lin])
        # Wire milestone hybrid/secret evolution if eligible!
        if hybrid_next is not None:
            comps = hybrid_next.get("hybrid_components", [])
            if lin in comps or lin == "hybrid":
                if len(cur_f["next_forms"]) < 5:
                    connect(cur_f["id"], hybrid_next["id"])

# Sanity assertions before writing JSON!
all_forms = [f for st in range(1, 25) for f in forms_by_stage[st]]
for f in all_forms:
    if f["stage"] < 24:
        n_out = len(f["next_forms"])
        assert 2 <= n_out <= 5, f"Node {f['id']} stage {f['stage']} has {n_out} next_forms (must be 2..5)"
    else:
        assert len(f["next_forms"]) == 0
    if f["stage"] > 1:
        assert len(f["parent_forms"]) >= 1, f"Node {f['id']} stage {f['stage']} is unreachable!"

forms_payload = {
    "schema_version": 1,
    "protagonist_rule": "El jugador ES una espada consciente reencarnada; ninguna evolución elimina su identidad de espada protagonista.",
    "permanence_rule": "Toda elección evolutiva es permanente e irreversible en la partida; las ramas hermanas quedan descartadas en el historial.",
    "eras": ERAS,
    "lineages": {k: {"id": k, "name": v["name"], "aura_color": v["aura_color"]} for k, v in LINEAGES.items()},
    "root_form_id": "wood_origin_ancestral_blade",
    "forms": all_forms,
}

with open(f"{FORMS_DIR}/evolution_catalog.json", "w", encoding="utf-8") as fp:
    json.dump(forms_payload, fp, ensure_ascii=False, indent=2)

skills_payload = {
    "schema_version": 1,
    "trees": [{"id": t["id"], "name": t["name"], "icon": t["icon"], "color": t["color"], "description": t["description"]} for t in TREE_DEFS],
    "skills": skills_list,
}

with open(f"{SKILLS_DIR}/skills_catalog.json", "w", encoding="utf-8") as fp:
    json.dump(skills_payload, fp, ensure_ascii=False, indent=2)

print(f"Generated evolution_catalog.json: {len(all_forms)} forms across 24 stages & 6 eras (0 dead ends, 2..5 choices/node)")
print(f"Generated skills_catalog.json: {len(skills_list)} skills across 6 trees (36 active + 36 passive)")

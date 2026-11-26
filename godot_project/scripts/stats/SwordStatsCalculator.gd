extends RefCounted
class_name SwordStatsCalculator

## Unified 17-Attribute Combat Stat Calculator for the Sentient Sword Protagonist.
## Combines:
##  1. Active Evolution Form Base Stats (17 attributes with lineage trade-offs)
##  2. Sword Level Scaling
##  3. Forge Upgrades (sharpness, swiftness, reach, vitality, fortune)
##  4. Equipped RPG Relics (grip, rune, relic)
##  5. Unlocked Passive Skills from the 72-Skill / 6-Tree System

static func calculate_stats(
	form_def: Dictionary,
	sword_level: int,
	upgrades: Dictionary,
	relic_bonuses: Dictionary,
	passive_mods: Dictionary
) -> Dictionary:
	var bs: Dictionary = form_def.get("base_stats", {})
	var lvl_steps: float = float(maxi(0, sword_level - 1))

	# Base form stats (with fallback defaults if legacy tier dict is passed)
	var base_phys: float = float(bs.get("physical_damage", form_def.get("base_damage", 18.0)))
	var base_elem: float = float(bs.get("elemental_damage", 4.0))
	var base_spd: float = float(bs.get("attack_speed", form_def.get("attack_speed", 1.15)))
	var base_rng: float = float(bs.get("attack_range", form_def.get("range", 3.1)))
	var base_crit: float = float(bs.get("crit_chance", form_def.get("crit_chance", 0.10)))
	var base_cdmg: float = float(bs.get("crit_damage", 1.85))
	var base_pen: float = float(bs.get("armor_penetration", 0.0))
	var base_steal: float = float(bs.get("life_steal", 0.0))
	var base_hp: float = float(bs.get("max_hp", 120.0))
	var base_def: float = float(bs.get("defense", 4.0))
	var base_res: float = float(bs.get("elemental_resistance", 0.05))
	var base_ereg: float = float(bs.get("energy_regen", 8.0))
	var base_emax: float = float(bs.get("max_energy", 100.0))
	var base_mspd: float = float(bs.get("move_speed", 8.8))
	var base_cdr: float = float(bs.get("cdr", 0.0))
	var base_stat_ch: float = float(bs.get("status_chance", 0.05))
	var base_soul: float = float(bs.get("soul_absorption", 0.15))

	var u_sharp: float = float(upgrades.get("sharpness", 0))
	var u_swift: float = float(upgrades.get("swiftness", 0))
	var u_reach: float = float(upgrades.get("reach", 0))
	var u_vit: float = float(upgrades.get("vitality", 0))
	var u_fort: float = float(upgrades.get("fortune", 0))

	var phys_pct: float = 1.0 + u_sharp * 0.14 + float(relic_bonuses.get("damage_pct", 0.0)) + float(passive_mods.get("physical_damage_pct", 0.0))
	var elem_pct: float = 1.0 + u_sharp * 0.08 + float(relic_bonuses.get("damage_pct", 0.0)) + float(passive_mods.get("elemental_damage_pct", 0.0))

	var physical_damage: float = round((base_phys + lvl_steps * 3.2) * maxf(0.25, phys_pct))
	var elemental_damage: float = round((base_elem + lvl_steps * 1.4) * maxf(0.25, elem_pct))
	var total_damage: float = round(physical_damage + elemental_damage * 0.45)

	var spd_mult: float = 1.0 + float(passive_mods.get("attack_speed_pct", 0.0))
	var attack_speed: float = (base_spd + u_swift * 0.09 + float(relic_bonuses.get("attack_speed", 0.0))) * spd_mult

	var attack_range: float = base_rng + u_reach * 0.25 + float(relic_bonuses.get("range", 0.0)) + float(passive_mods.get("attack_range_add", 0.0))

	var crit_chance: float = clampf(
		base_crit + u_fort * 0.025 + float(relic_bonuses.get("crit_chance", 0.0)) + float(passive_mods.get("crit_chance_add", 0.0)),
		0.0, 0.85
	)
	var crit_damage: float = maxf(1.25, base_cdmg + float(passive_mods.get("crit_damage_add", 0.0)))
	var armor_penetration: float = clampf(base_pen + float(passive_mods.get("armor_penetration_add", 0.0)), 0.0, 0.80)
	var life_steal: float = clampf(base_steal + float(relic_bonuses.get("lifesteal", 0.0)) + float(passive_mods.get("life_steal_add", 0.0)), 0.0, 0.45)

	var hp_pct: float = maxf(0.4, 1.0 + float(passive_mods.get("max_hp_pct", 0.0)))
	var max_hp: int = int(round((base_hp + lvl_steps * 14.0 + u_vit * 32.0 + float(relic_bonuses.get("max_hp", 0.0))) * hp_pct))
	var defense: float = maxf(0.0, base_def + lvl_steps * 0.6 + u_vit * 1.5 + float(passive_mods.get("defense_add", 0.0)))
	var elemental_resistance: float = clampf(base_res + float(passive_mods.get("elemental_resistance_add", 0.0)), 0.0, 0.80)

	var energy_regen: float = base_ereg * (1.0 + float(passive_mods.get("energy_regen_pct", 0.0)))
	var max_energy: int = int(round(base_emax + float(passive_mods.get("max_energy_add", 0.0))))
	var move_speed: float = (base_mspd + float(relic_bonuses.get("move_speed", 0.0))) * (1.0 + float(passive_mods.get("move_speed_pct", 0.0)))
	var cdr: float = clampf(base_cdr + float(relic_bonuses.get("cd_reduction", 0.0)) + float(passive_mods.get("cdr_add", 0.0)), 0.0, 0.45)
	var status_chance: float = clampf(base_stat_ch + float(passive_mods.get("status_chance_add", 0.0)), 0.0, 0.90)
	var soul_absorption: float = maxf(0.0, base_soul + float(relic_bonuses.get("xp_bonus", 0.0)) + float(passive_mods.get("soul_absorption_add", 0.0)))
	var gold_mult: float = 1.0 + u_fort * 0.16 + float(relic_bonuses.get("gold_bonus", 0.0))

	return {
		# Legacy keys preserved for 100% combat/HUD/test compatibility
		"damage": total_damage,
		"range": attack_range,
		"gold_mult": gold_mult,
		"xp_mult": 1.0 + soul_absorption,
		"lifesteal": life_steal,
		"cd_reduction": cdr,
		# Full 17-attribute schema
		"physical_damage": physical_damage,
		"elemental_damage": elemental_damage,
		"attack_speed": attack_speed,
		"attack_range": attack_range,
		"crit_chance": crit_chance,
		"crit_damage": crit_damage,
		"armor_penetration": armor_penetration,
		"life_steal": life_steal,
		"max_hp": max_hp,
		"defense": defense,
		"elemental_resistance": elemental_resistance,
		"energy_regen": energy_regen,
		"max_energy": max_energy,
		"move_speed": move_speed,
		"cdr": cdr,
		"status_chance": status_chance,
		"soul_absorption": soul_absorption,
	}

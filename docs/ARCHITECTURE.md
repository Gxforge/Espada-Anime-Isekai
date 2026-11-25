# ARCHITECTURE

## Current (baseline)

- **Engine:** Godot 4.4, Forward+, GDScript.
- **Autoload:** `GameData.gd` — sword tiers, monster definitions, XP curve, eligibility helpers.
- **Main scene:** `Main.tscn` — WorldEnvironment, lights, arena meshes, Player, Monsters container, Camera3D, HUD.
- **Player:** `Player.gd` (`CharacterBody3D`) — movement, combat, skills, progression, upgrades, visuals, signals.
- **Monster:** `Monster.gd` (`CharacterBody3D`) — chase/attack, damage, bleed/lightning partial, death rewards.
- **Projectiles/FX:** `SwordWave.gd`, `SkySword.gd`, `CustomGeometry.gd`.
- **Visual builders:** `SwordBuilder.gd`, `MonsterBuilder.gd` — procedural fallback visuals.
- **HUD:** `HUD.gd` + scene nodes in `Main.tscn`.

## Target direction (incremental)

Do not big-bang rewrite. Incrementally extract responsibilities while preserving behavior:

- `scripts/core/` — constants, IDs, signal contracts, utility.
- `scripts/data/` — static data/definitions.
- `scripts/gameplay/player/` — movement, combat, skills, progression.
- `scripts/gameplay/enemies/` — AI, spawning, boss.
- `scripts/systems/` — save, forge, audio, settings.
- `scripts/visuals/` — model loading, VFX.
- `scenes/ui/` — HUD subscenes/menus.

## Known architectural debt

- `Player.gd` mixes input, movement, combat, skills, progression, upgrades, VFX, visuals.
- `Main.gd` handles spawn/camera/HUD wiring/boss trigger.
- No save system, no test harness, no model loader abstraction.
- Procedural builders are used instead of real OBJ assets.

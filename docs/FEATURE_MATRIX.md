# FEATURE MATRIX

Status: `Implemented` / `Partial` / `Broken` / `Missing` / `Not tested`

| Area | Feature | Status | Notes |
|---|---|---|---|
| Core | Godot 4.4 project boots | Partial | Main scene exists; no automated boot test in CI. |
| Core | Feature inventory/docs | Implemented | This audit pass creates baseline docs. |
| Models | 16 OBJ assets present in repo | Implemented | `godot_project/assets/models/` + web source. |
| Models | Real OBJ runtime integration - swords | Missing | `Player.gd` uses `SwordBuilder.gd` procedural visuals. |
| Models | Real OBJ runtime integration - monsters | Missing | `Monster.gd` uses `MonsterBuilder.gd`. |
| Models | Real OBJ runtime integration - knight | Missing | Knight holder has placeholder mesh; no `hero_knight_wielder.obj` loaded. |
| Models | Model validation report | Missing | To be created. |
| Player | Movement WASD/arrows | Implemented | In `Player.gd`. |
| Player | Camera follow | Implemented | `Main.gd` lerp camera. |
| Player | Basic attack/combo | Partial | Combo exists; hit detection simple; no full animation/state machine. |
| Player | Dash | Partial | Works; collision-safe/invuln tuning needed. |
| Player | Death/respawn | Partial | HP<=0 teleports to center and restores HP; no game over/state flow. |
| Player | Wielder modes | Partial | Toggle exists; knight visual not real model. |
| Combat | Damage/crit/atk speed/range | Partial | Core stats exist; crit applied in Monster.take_damage; needs canonical pipeline/tests. |
| Combat | Cooldowns independent | Partial | Cooldowns exist; canonical ID inconsistency `wave`/`swordWave` flagged. |
| Combat | Whirlwind Q | Partial | Area tick damage and VFX present; needs balance/tests. |
| Combat | Sword Wave E | Partial | Projectile exists; cooldown key naming issue. |
| Combat | Ultimate R | Partial | Sky swords fall and explode; visuals improved; needs targeting/pattern polish. |
| Combat | Dash Shift | Partial | Implemented. |
| Sword FX | Wood +15% soul essence | Partial | xp_mult includes wood bonus in stats; needs verification against all XP sources. |
| Sword FX | Copper 3rd hit sparks +35% AoE | Missing | No 3rd-hit counter/effect. |
| Sword FX | Iron crit bleed 3s | Partial | Bleed timer exists on monster; damage application simplistic. |
| Sword FX | Silver lightning chains up to 3 | Partial | Chains to 1 extra target currently. |
| Sword FX | Gold solar burn + combat regen | Missing | No burn/regen mechanic. |
| Sword FX | Crystal auto arcane shards | Missing | No shard projectiles. |
| Sword FX | Obsidian lifesteal + magma eruptions | Partial | Lifesteal on hit exists; magma eruptions missing. |
| Sword FX | Celestial dimensional waves/cosmic nova/double crit | Partial | Crit mult bonus exists; waves/nova missing. |
| Enemies | 7 monster definitions | Implemented | In `GameData.gd`. |
| Enemies | Distinct AI behaviors | Partial | Mostly same chase/attack; speed/range/stats differ. |
| Enemies | Boss Malakor encounter | Partial | Spawns every 3rd wave; no boss UI/patterns/telegraph/defeat sequence. |
| Progression | XP formula | Implemented | Matches web reference formula. |
| Progression | Wave 8 kills | Implemented | `Player.add_kill()`. |
| Progression | Evolution thresholds | Implemented | GameData tiers. |
| Progression | No duplicate rewards | Not tested | Needs audit/tests. |
| Forge | 6 upgrades | Partial | Buy/scale exists; max level limits not enforced; UI names shortened. |
| Save/Load | Local persistence | Missing | No save system. |
| UI | HUD | Partial | Functional/styled; missing cooldown UI, boss HP, pause/inventory/game over. |
| UI | Responsive 1280-1920 | Not tested | Canvas items stretch configured; needs verification. |
| Audio | SFX/BGM/settings | Missing | No audio assets/system. |
| Performance | Quality settings/pooling | Missing | No settings/pooling system. |
| Tests | Automated tests | Missing | No test suite. |
| CI | Strict GitHub Actions | Broken/Missing | Existing workflow permissive with `|| true`. |
| Build | Windows export verified | Missing | No verified export. |
| Build | Linux export verified | Missing | No verified export. |

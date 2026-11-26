# TEST PLAN

## Automated Headless Suite (`godot_project/tests/run_tests.gd`)

Run with:
```bash
godot --headless --path godot_project -s res://tests/run_tests.gd
```

Current status: **507 passed, 0 failed**.

### 1. Static & Data Integrity Checks
- **GameData**: 8 canonical sword evolutions, 7 canonical monster definitions, 7 RPG materials, 9 relics across 3 slots, 2 consumables, 6 forge upgrades, XP curve (`get_xp_required`).
- **3D & 2D Assets**: all 16 `.obj` meshes load with valid non-zero AABBs; all 10 UI PNGs (`logo`, `title`, `menu_bg`, `loading_bg`, `portrait`, `skill_attack/q/e/r/shift`) and all 19 `.wav` audio streams load cleanly.
- **Scenes & Export Presets**: `Boot.tscn`, `LoadingScreen.tscn`, `MainMenu.tscn`, `Main.tscn`, `Monster.tscn`, and `export_presets.cfg` (`Linux` & `Windows Desktop`) verified.

### 2. Runtime Combat, Progression & Malakor Boss Tests
- **Player Combat**: melee arc hit detection, canonical `swordWave` + legacy `wave` alias, `whirlwind`, `ultimate`, `dash` i-frames (`invuln_timer > 0`), XP level-up and `evolution_changed` signal, forge upgrade purchase & damage scaling, lethal damage `player_died` signal, and `respawn_player()` full recovery.
- **RPG Inventory & Crafting**: material collection, `can_craft_relic`, `craft_relic` gold/material deduction, auto-equip & slot swapping (`grip`, `rune`, `relic`) updating live `stats`, `potion_hp` healing, and `elixir_xp` XP grant.
- **Malakor 2-Phase Boss**: Phase I initialization, deterministic transition to Phase II (`boss_phase == 2`, `boss_phase_changed` signal) at `<= 50%` HP, guaranteed `corazon_abismo` drop, and anti-duplicate `_dead` guard preventing double kill/XP/gold/loot rewards.

### 3. SaveSystem v2, Migration & Audio Persistence
- **v2 Roundtrip**: serializes and restores level, XP, gold, kills, wave, `bosses_defeated`, `wielder_mode`, `auto_hunt`, upgrades, `materials`, `inventory_items`, `equipped`, and `consumables`.
- **v1 Migration**: loads legacy v1 JSON saves cleanly into v2, preserving progression and migrating legacy `volume` to `master_volume`.
- **AudioManager & Settings**: verifies `Music` and `SFX` buses, mute state, and `save_settings` / `load_settings_only` persistence.

### 4. Multi-Resolution HUD & Modal Geometry Regression
- Resizes `HUD` across **`1280x720`**, **`1366x768`**, **`1600x900`**, and **`1920x1080`**, asserting:
  - Every primary HUD panel (`TopLeft`, `QuickPills`, `Objective`, `TopCenter`, `TopRight`, `Minimap`, `Forge`, `BottomSkills`, `Log`, `Branding`, `BossBar`) is strictly within viewport bounds.
  - Zero pairwise `Rect2.intersects()` overlaps among all primary HUD panels.
  - All modal overlays (`Settings`, `Inventory`, `Stats`, `GameOver`) fit within viewport margins and enforce mutual exclusion when toggled.

## Visual Interactive QA (Xvfb + Vulkan)
- Verified real rendered frames across `LoadingScreen`, `MainMenu`, `Main` (`1280x720`, `1366x768`, `1600x900`, `1920x1080`), Malakor Phase I & Phase II, and all 5 modal overlays under `xvfb-run` + Mesa Vulkan Forward+.

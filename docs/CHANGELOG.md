# CHANGELOG

## Unreleased (feature/godot-complete-reconstruction)

### Baseline/docs
- Created reconstruction branch from `d943b30`.
- Added baseline docs: `AUDIT.md`, `FEATURE_MATRIX.md`, `ARCHITECTURE.md`, `KNOWN_ISSUES.md`, `MODEL_INTEGRATION.md`, `TEST_PLAN.md`, `CHANGELOG.md`.
- Added root `.gitignore` (ignore `extracted/`, build/cache).

### Gameplay/code
- **Skill cooldown canonicalization**: normalized skill IDs (`whirlwind`, `swordWave`, `ultimate`, `dash`) with alias support for `wave`; fixed auto-hunt to use canonical `swordWave`.
- **Real OBJ model integration**: added `scripts/ModelLoader.gd`; Player swords, sky swords, monsters, and knight wielder now load real OBJ meshes from `assets/models/` with procedural-builder fallback.
- **Sword special effects (initial pass)**: copper 3rd-hit sparks + AoE, iron bleed hook, silver lightning chains up to 3 targets with arc VFX, gold burn patch + combat regen, crystal auto shard projectiles, obsidian magma eruption, celestial dimensional wave + cosmic nova; wood XP bonus already present in stats.
- **Forge limit**: added max upgrade level (10) guard in `buy_upgrade`.
- **Save/Load**: added `SaveSystem.gd` autoload (versioned JSON, atomic-ish temp write, validation/defaults) and periodic autosave/load in `Main.gd`.

### QA/CI
- Added lightweight headless test runner: `godot_project/tests/run_tests.gd` (60 passing checks locally).
- Rewrote GitHub Actions workflow to strict mode: no failure masking, template checks, test execution, verified Linux/Windows exports, artifacts on success.
- Added Windows Desktop export preset to `export_presets.cfg`.

### Known remaining
- Boss Malakor encounter still shallow (no full pattern/telegraph/boss UI/defeat sequence).
- No pause/inventory/game-over/audio/quality settings screens/systems.
- Full sword effect parity and balance need gameplay validation.
- CI strict export depends on GitHub runner image having Godot 4.4 templates.

### Continuation pass
- **Boss Malakor**: added boss AI state machine in `Monster.gd` (chase/telegraph slam/slam/telegraph charge/charge/recover), telegraph VFX, AoE slam damage.
- **HUD boss HP**: runtime boss HP panel/bar in `HUD.gd`.
- **Death/Game Over**: `player_died` signal, `is_dead`/`invuln_timer`, respawn flow and game-over overlay in HUD.
- **Save on exit**: `Main.gd` saves on `NOTIFICATION_WM_CLOSE_REQUEST`.
- **Tests**: expanded to 67 passing checks (player death/respawn, boss AI markers).

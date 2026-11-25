# KNOWN ISSUES

## Resolved in this pass

- Real OBJ runtime integration wired for swords, monsters, and knight (with procedural fallback).
- Skill cooldown canonicalization fixed (`swordWave` canonical, `wave` alias supported).
- Basic sword special effects implemented (copper sparks AoE, silver chain up to 3, gold burn+regen, crystal auto shards, obsidian magma eruption, celestial wave/nova; iron bleed hook present).
- Upgrade max level guard added (10).
- Basic SaveSystem added (versioned JSON, load on start, autosave).
- Headless test runner added (60 checks passing locally).
- CI rewritten to strict mode; Windows export preset added.

## Still open

1. **Boss Malakor encounter incomplete** — no dedicated boss patterns/telegraphing/boss UI/defeat sequence/reward ceremony.
2. **Sword effect parity/balance not fully validated** — effects are implemented as initial gameplay pass; need tuning and playtest against web reference.
3. **No pause menu / inventory / game-over screen** — death currently respawns player in-place.
4. **No audio system** — no SFX/BGM/settings.
5. **No quality settings / performance profiling report** — no measured FPS data on target hardware.
6. **OBJ orientation/scale polish** — models load and render, but per-model pivot/orientation/material polish may be needed for closer parity.
7. **Player.gd still large** — responsibilities should be split further.
8. **CI export depends on runner templates** — strict workflow will fail clearly if templates are missing, but GitHub environment must provide Godot 4.4 export templates.
9. **No full regression suite** — current tests cover data/resources/basic invariants; combat/scene integration tests need expansion.

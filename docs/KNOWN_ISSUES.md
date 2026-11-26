# KNOWN ISSUES

## Resolved in 2026-11-26 Pass

- **Fixed `Main.gd` parse error**: removed undeclared `_music` reference and wired `AudioManager` crossfading (`ambient` <-> `boss_theme`).
- **HUD 1:1 anime-isekai layout & multi-resolution support**: rebuilt `HUD.gd` + `MinimapRadar.gd`, clipped circular portrait cleanly inside its 84x84 ring, eliminated all `U+1Fxxx` missing-glyph tofu boxes, and verified zero overlaps across `1280x720`, `1366x768`, `1600x900`, and `1920x1080`.
- **Complete RPG Inventory, Relics & Loot**: implemented 7 monster materials, 9 equippable relics across 3 slots, crafting workshop, and 2 consumables persisted in `SaveSystem` v2 (with v1 save migration).
- **Complete Audio System**: implemented `AudioManager.gd` (`Master`/`Music`/`SFX` buses, 3 music loops, 16 SFX WAVs, persistent mixer sliders).
- **Complete Malakor 2-Phase Encounter**: implemented active melee + telegraphed `slam`, `charge`, and Phase II `meteor` barrage, Phase II HUD bar, anti-duplicate `_dead` reward guard, and guaranteed `corazon_abismo` drop.
- **Expanded Regression Suite**: expanded `godot_project/tests/run_tests.gd` to **507 deterministic runtime assertions**.

## Remaining / Environment Limitations

1. **Physical GPU FPS Not Measured in Container (`NOT TESTED`)**:
   - Interactive 3D rendering in this environment runs on CPU software rasterization (`Mesa llvmpipe`, ~2.38 FPS at `1600x900` Forward+). Frame rate on dedicated/integrated desktop GPUs has not been profiled in this container and should be validated on target Windows/Linux hardware.
2. **Windows `.exe` Native OS Execution (`NOT TESTED`) & `rcedit`**:
   - `ForjaDeAlmas3D.exe` builds cleanly as a valid 64-bit PE32+ executable on Linux/CI, with a non-blocking Godot export warning because `rcedit` (optional Windows icon/version resource tool) is not configured in the Linux container. Interactive gameplay on native Windows OS was not executed in this Linux session.
3. **Reference Web Directory Included in Default Pack**:
   - `godot_project/reference_web/` remains intact inside `godot_project/` as historical reference; excluding `reference_web/*` in `export_presets.cfg` could reduce `.pck` size further in a future release-packaging pass if desired.
4. **`Player.gd` & `HUD.gd` File Size**:
   - Both scripts are self-contained and cleanly tested, though future feature expansions could split `HUD` modals (`Inventory`, `Stats`, `Settings`) into dedicated sub-controllers.

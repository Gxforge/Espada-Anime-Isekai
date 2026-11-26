# CHANGELOG

## 2026-11-26 — Complete HUD, RPG Inventory, Audio, Malakor Phase II & 507-Check QA Suite (`feature/godot-complete-reconstruction`)

### UI, Art & Multi-Resolution HUD (`HUD.gd`, `MinimapRadar.gd`, `MainMenu.gd`, `LoadingScreen.gd`)
- Generated and integrated anime-isekai UI artwork in `godot_project/assets/ui/`: `portrait.png`, `menu_bg.png`, `loading_bg.png`, `title.png`, `logo.png`, `skill_attack.png`, `skill_q.png`, `skill_e.png`, `skill_r.png`, `skill_shift.png`.
- Rebuilt `HUD.gd` with responsive layout engine (`_layout_responsive`) guaranteeing zero panel overlaps across `1280x720`, `1366x768`, `1600x900`, and `1920x1080`.
- Added custom vector radar minimap (`MinimapRadar.gd`) with rotating sweep, Sacred Forge Altar marker, directional player chevron, enemy dots, and pulsing Malakor boss diamond.
- Implemented all 5 modal overlays (`Pause`, `RPG Inventory & Relic Workshop`, `Stats & Evolution Codex`, `Settings Mixer`, `Game Over`), 2D projected floating combat/heal/XP numbers, dynamic skill cooldown curtains, and ceremonial evolution/boss banners.
- Replaced all supplementary-plane Unicode emojis (`U+1Fxxx`) with font-safe glyphs (`✦`, `★`, `⚒`, `⚙`, `☠`, `⚠`, `❤`, `⚡`, `▶`, `✕`, `✓`) to eliminate missing-glyph tofu boxes on Linux/Windows default fonts.

### RPG Inventory, Materials, Relics & Consumables (`GameData.gd`, `Player.gd`, `SaveSystem.gd`)
- Added 7 monster drop materials (`gel_cristalino`, `colmillo_trasgo`, `hueso_maldito`, `nucleo_cobre`, `sangre_berserker`, `escama_escarlata`, `corazon_abismo`).
- Added 9 craftable/droppable Relics across 3 equipment slots (`grip`, `rune`, `relic`) dynamically modifying combat and progression stats.
- Added 2 battle consumables (`potion_hp` with `[H]` hotkey & HUD quick pill, and `elixir_xp`).
- Upgraded `SaveSystem.gd` to `SAVE_VERSION = 2` with full persistence for materials, relics, equipped slots, consumables, `auto_hunt`, `bosses_defeated`, and volume channels, plus automatic migration from v1 saves.

### Audio System (`AudioManager.gd`, `assets/audio/`)
- Added `AudioManager` autoload with dedicated `Master`, `Music`, and `SFX` buses, smooth music crossfading (`menu_theme.wav`, `ambient.wav`, `boss_theme.wav`), and an 8-player polyphonic SFX pool across 16 combat/UI/progression WAV effects.
- Connected persistent Master/Music/SFX volume sliders and Mute toggle in HUD `Ajustes`.

### Malakor Boss Encounter, Monsters & 3D Sanctuary (`Main.gd`, `ArenaDecor.gd`, `Monster.gd`)
- Fixed `Main.gd` `_music` undeclared identifier parse error and connected dynamic boss music crossfading.
- Added `ArenaDecor.gd` building a 3D Soul Forge Sanctuary (runic circles, Sacred Anvil Altar, 8 fire braziers, floating crystals, scenic pines) scalable via Quality settings (`low` / `medium` / `high`).
- Implemented distinct AI for all 7 canonical monster species (`slime`, `goblin`, `skeleton`, `copper_golem`, `orc_berserker`, `crimson_drake`, `demon_lord`) and 2-phase Malakor encounter (Phase I melee/`slam`/`charge`; Phase II `meteor` barrage, Phase II HUD bar, anti-duplicate `_dead` reward guard, guaranteed `corazon_abismo` drop).

### Testing, Exports & CI (`tests/run_tests.gd`)
- Expanded automated headless test suite to **507 passing checks** covering runtime combat, skills, evolutions, upgrades, RPG crafting/equipping/consumables, Malakor phases & anti-duplicate rewards, SaveSystem v2 + v1 migration, `AudioManager`, `ArenaDecor`, and HUD bounds/non-overlap across all 4 resolutions.
- Verified Linux (`ForjaDeAlmas3D.x86_64`) and Windows (`ForjaDeAlmas3D.exe`) release exports and Xvfb + Vulkan visual screenshots across `1280x720`, `1366x768`, `1600x900`, and `1920x1080`.

---

## Previous Passes (2026-11-24)
- Created `feature/godot-complete-reconstruction` from `d943b30` with baseline audit docs (`AUDIT.md`, `FEATURE_MATRIX.md`, `ARCHITECTURE.md`, `MODEL_INTEGRATION.md`).
- Integrated `ModelLoader.gd` for all 16 OBJ models (8 swords, 7 monsters, knight wielder) with procedural fallback.
- Normalized canonical skill IDs (`swordWave` with `wave` alias), added max upgrade level guard (`10`), initial `SaveSystem.gd` v1, strict GitHub Actions workflow (`.github/workflows/godot-ci.yml`), and Windows/Linux export presets.

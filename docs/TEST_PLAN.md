# TEST PLAN

## Scope

Baseline has no automated tests. This plan defines minimum verifiable checks to add incrementally.

## Unit/data tests

- GameData: 8 sword tiers, 7 monsters, required fields, evolution thresholds, XP formula, eligible monster pools.
- Progression: level-up, evolution, wave transition every 8 kills, no duplicate reward on single death.
- Combat: damage formula, crit multiplier, cooldown independence, skill canonical IDs.
- Upgrades: costs, max levels, insufficient gold, stat recalculation.
- Save/load: schema version, round-trip, invalid/missing file defaults, atomic write.

## Integration/runtime tests (headless)

- Main scene instantiates.
- Player scene/script loads and has expected signals/methods.
- Monster instantiation from definitions.
- All 16 OBJ resources load via `load()`.
- Sword/monster/knight visual integration produces visible nodes.

## Regression

- Original controls: WASD/arrows, click/space, Q/E/R/Shift.
- Original 8 swords / 7 monsters / 6 upgrades present.
- Wave rule: 8 kills -> next wave.

## CI

- Strict import/parse/test/export checks.
- No `|| true` masking failures.
- Artifacts only for verified builds.

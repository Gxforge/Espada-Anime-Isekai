# MODEL INTEGRATION

## Status: Partial (runtime OBJ loading wired; visual verification done in-engine)

## Inventory (16 OBJ)

| Asset | Type | Path | Runtime integration | Status |
|---|---|---|---|---|
| `hero_knight_wielder.obj` | Player | `res://assets/models/hero_knight_wielder.obj` | Loaded via `ModelLoader.build_knight_visual()` into `KnightHolder` | Implemented (needs visual polish) |
| `sword_wood_nv1.obj` | Sword | `res://assets/models/sword_wood_nv1.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_copper_nv5.obj` | Sword | `res://assets/models/sword_copper_nv5.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_iron_nv10.obj` | Sword | `res://assets/models/sword_iron_nv10.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_silver_nv15.obj` | Sword | `res://assets/models/sword_silver_nv15.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_gold_nv20.obj` | Sword | `res://assets/models/sword_gold_nv20.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_crystal_nv25.obj` | Sword | `res://assets/models/sword_crystal_nv25.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_obsidian_nv30.obj` | Sword | `res://assets/models/sword_obsidian_nv30.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `sword_celestial_nv35.obj` | Sword | `res://assets/models/sword_celestial_nv35.obj` | `ModelLoader.build_sword_visual()` | Implemented |
| `monster_slime.obj` | Monster | `res://assets/models/monster_slime.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_goblin.obj` | Monster | `res://assets/models/monster_goblin.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_skeleton.obj` | Monster | `res://assets/models/monster_skeleton.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_copper_golem.obj` | Monster | `res://assets/models/monster_copper_golem.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_orc_berserker.obj` | Monster | `res://assets/models/monster_orc_berserker.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_crimson_drake.obj` | Monster | `res://assets/models/monster_crimson_drake.obj` | `ModelLoader.build_monster_visual()` | Implemented |
| `monster_demon_lord.obj` | Monster | `res://assets/models/monster_demon_lord.obj` | `ModelLoader.build_monster_visual()` | Implemented |

## Implementation

- `scripts/ModelLoader.gd`: loads OBJ mesh via `load()`, creates `MeshInstance3D` with fallback material, normalizes to target height, centers XZ/base Y.
- `Player._refresh_sword_visual()`: uses `ModelLoader.build_sword_visual()` with fallback to `SwordBuilder`.
- `Monster._load_model()`: uses `ModelLoader.build_monster_visual()` with fallback to `MonsterBuilder`.
- `Player._ensure_knight_visual()`: loads `hero_knight_wielder.obj` into `KnightHolder`.
- Sky swords also use `ModelLoader`.

## Validation

- Headless probe confirmed all sampled OBJ files load as `ArrayMesh` with valid AABBs.
- Runtime screenshot capture confirmed real OBJ sword/monster meshes render in-game.
- Automated test `run_tests.gd` verifies 16 model paths exist and key models load with AABB size.

## Remaining

- Per-model scale/orientation fine-tuning for gameplay feel (some OBJs may need pivot/rotation tweaks).
- Material/texture fidelity review against original web look.
- Confirm knight model visibility/animation in wielder mode across all sword tiers.

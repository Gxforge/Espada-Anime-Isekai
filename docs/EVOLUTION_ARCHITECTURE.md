# Arquitectura del Sistema de Evolución Permanente, Habilidades y Estadísticas (v3)

**Proyecto:** Espada Anime Isekai / Forja de Almas 3D (Godot 4.4)
**Rama:** `feature/godot-complete-reconstruction`
**Regla de oro:** el protagonista ES una espada consciente reencarnada — su identidad se preserva en los 118 nodos del grafo; las decisiones de evolución son **permanentes e irreversibles**.

---

## 1. Diagrama de módulos

```
res://data/
  forms/evolution_catalog.json ──► EvolutionCatalog.gd (scripts/evolution/)
  skills/skills_catalog.json ───► SkillCatalog.gd ────► (scripts/skills/)
                                        │                       │
                                        ▼                       ▼
                          EvolutionValidator.gd        SkillTreeManager.gd
                          (validate_graph automático)  (puntos, gates, ranuras)
                                        │                       │
                                        ▼                       ▼
                              EvolutionManager.gd ──── Player.gd ──── SwordStatsCalculator.gd
                              (5 condiciones, commit   (try_evolve,        (scripts/stats/,
                              irreversible, historia,  perform_slot,       17 atributos:
                              eventos del mundo)       energía)            forma×nivel×forja
                                        │                                 ×reliquias×pasivas)
                                        ▼
        HUD.gd (modales [T]/[K], pills vivos, ranuras Q/E/R/Shift, barra ⚡)
                                        │
                                        ▼
        SaveSystem.gd (v3) + SaveMigration.gd (scripts/save/) ── user://savegame.json
```

Todos los catálogos son JSON planos (`include_filter="*.json"` en ambos presets de exportación incrusta los datos en el PCK). `EvolutionCatalog.register_form()` y `SkillCatalog.register_skill()` permiten registrar formas/habilidades **adicionales en runtime** (packs de expansión) sin tocar código: no existe límite artificial de formas.

## 2. Esquema del catálogo de formas (`evolution_catalog.json`)

| Campo | Descripción |
|---|---|
| `eras[]` | 6 eras (`era_1_awakening` … `era_6_supreme`), cada una cubre 4 etapas |
| `lineages{}` | 7 linajes: `origin`, `blessed`, `cursed`, `elemental`, `spiritual`, `arcane`, `hybrid` |
| `root_form_id` | `wood_origin_ancestral_blade` (Pilot #01 verificado, GLB propio) |
| `forms[]` | 118 formas. Cada nodo: `id`, `legacy_alias`, `stage` (01–24), `era`, `lineage`, `is_hybrid`, `is_secret`, `protagonist_identity` (`sentient_sword` en TODOS), `base_stats` (17 atributos), `unlock_conditions` (5 tipos), `parent_forms[]`, `next_forms[]` (2–5 por nodo, 0 en etapa 24), colores (`blade_color`, `aura_color`, `slash_color`…), `special_effect`, `model_path`, `model_status` (`verified_pilot_glb` ×1, `extensible_blueprint_pending_3d` ×117) |

Los 5 hitos híbridos (etapas 8, 12, 16, 20, 24) tienen ≥2 `parent_forms` — por ejemplo `hybrid_celestial_abyss_eclipse` (Etapa 16) exige dos eventos del mundo (`wave_3_cleared` + `defeated_malakor`), 2 habilidades dominadas y materiales abisales.

### Los 5 tipos de condición de desbloqueo (`unlock_conditions`)

| Clave | Evaluación en `EvolutionManager.evaluate_unlock_conditions()` |
|---|---|
| `min_level` | `context.sword_level >= min_level` |
| `min_evolution_xp` | Esencia Evolutiva acumulada (kills +3, nivel +25) |
| `required_materials` | Diccionario `material_id -> cantidad`; se **consumen** al cometer |
| `required_skills` | Habilidades aprendidas del árbol de 72 |
| `required_events` | `world_events` registrados en vivo (`wave_3_cleared` en `Player.add_kill`, `defeated_malakor` vía `Monster.gd` → `Player.notify_boss_defeated`) |

### Reglas de ramificación permanente (`commit_permanent_evolution`)

1. Solo se permiten hijos **directos** del formulario actual (prohibido saltar etapas o retroceder).
2. Las condiciones de las 5 categorías deben evaluarse en verde.
3. Al cometer: los materiales se descuentan, cada hermana no elegida se sella en `discarded_form_ids` **para siempre**, y la elección se añade a `evolution_history` (`stage`, `era`, `form_id`, `from_form_id`, `level_at_choice`).
4. El grafo se valida automáticamente (`EvolutionValidator.validate_graph()`): 6 eras, 24 etapas cubiertas, aristas bidireccionales coherentes, sin ciclos (etapas estrictamente crecientes), **cero puntos muertos** (todo nodo alcanza la Etapa 24), alcance total desde la raíz, identidad `sentient_sword`, 17 stats y 5 condiciones por nodo.

## 3. Esquema del catálogo de habilidades (`skills_catalog.json`)

- **6 árboles × 12 habilidades = 72** (`36 active` + `36 passive`): `physical_mastery` ⚔, `elemental_magic` ✦, `spiritual_energy` ★, `defense_survival` ❖, `curses_absorption` ☠, `legendary_powers` ♛ (iconos BMP verificados en la fuente fallback de Godot 4.4).
- Por habilidad: `type`, `tier`, `min_stage`, `cost_points`, `prereq_skills[]`, `allowed_lineages[]` (exclusividad de linaje), `cooldown`, `energy_cost`, `combat_archetype` (enrutamiento de comportamiento en `Player.perform_skill`), `effect_data` (modificadores pasivos o parámetros activos).
- Las 4 canónicas (`whirlwind`, `swordWave` con alias legacy `wave`, `ultimate`, `dash`) vienen aprendidas de inicio y equipadas por defecto en Q/E/R/Shift.

## 4. Ranuras de carga (loadout) y energía

- `Player.perform_slot("Q"|"E"|"R"|"SHIFT")` lanza la habilidad **equipada** (no hay llamadas fijas); las teclas físicas Q/E/R/Shift y los clics en el HUD pasan por ahí.
- `HUD._refresh_bottom_skill_slots()` re-vincula cortinas de cooldown (`cd_nodes[slot]["skill"]`) y etiquetas al cambiar la carga (`active_loadout_changed`).
- `Player.energy` se regenera con `stats.energy_regen` hasta `stats.max_energy`; cada activa descuenta `energy_cost`. La barra ⚡ del panel inferior se actualiza por frame (`HUD._update_energy`).
- Las pasivas desbloqueadas alimentan `SkillTreeManager.get_aggregated_passive_modifiers()` → `SwordStatsCalculator` (16 claves de modificación, respetando exclusividad de linaje).

## 5. Guardado v3 (`user://savegame.json`)

```
version: 3
sword_level / current_xp / gold / kills / wave / wave_kills / player_hp / ...
upgrades / materials / inventory_items / equipped / consumables / bosses_defeated
evolution_state: { current_form_id, evolution_xp, evolution_history[], discarded_form_ids[], world_events{} }
skill_state:     { skill_points, unlocked_skills{}, equipped_slots{} }
settings: {...}
```

- **v1 → v2 → v3** (`SaveMigration.migrate_save_dict`): un save legacy recibe un estado inicial mapeado por nivel (`migrated_from_v2: true` en el historial) — un save **v3** existente se aplica **verbatim**: la forma jamás se reconstruye desde `sword_level` (probado manipulando el JSON: nivel reescrito a 1 y la elección permanente sobrevive intacta).
- `Main.gd` sigue llamando `SaveSystem.load_game(player)` / `save_game(player)`; la API no cambió.

## 6. Controles nuevos

| Tecla | Acción |
|---|---|
| `T` | Árbol de Evolución Permanente (filtros por Era, estados ★/✓/✕/▶/⚠, botón EVOLUCIONAR) |
| `K` | Árbol de Habilidades (6 ramas, APRENDER, asignación Q/E/R/Shift) |
| `Q`/`E`/`R`/`Shift` | Lanzan la habilidad **equipada** en cada ranura |

## 7. Cómo extender (sin tocar código)

1. Añade nodos al JSON respetando las invariantes del validador (etapas crecientes, `parent_forms` inversos, 2–5 hijos, 17 stats, 5 condiciones) y ejecuta `validate_graph()` en la suite.
2. Añade habilidades con prerequisitos válidos y ejecuta `SkillCatalog.validate_catalog()`.
3. Para una forma con modelo 3D propio: marca `model_status: verified_*` y apunta `model_path` al GLB aprobado por Studio Lexair (ver `docs/3D_PRODUCTION_PLAN.md` — nada de meshes procedurales ni recolores).

## 8. Evidencia de QA

- Suite headless: **752 passed, 0 failed** (`godot_project/tests/run_tests.gd`), incluyendo validación de grafo, ramificación permanente y sellado de hermanas, 5 condiciones, gates de 72 habilidades, matemática de 17 atributos, roundtrip v3 + test de manipulación, ranuras dinámicas de carga, eventos del mundo en vivo y barra de energía.
- Capturas Xvfb + Vulkan: `art_pipeline/ui_qa/` (`evolution_panel_1280x720.png`, `skill_tree_panel_1280x720.png`, `hud_gameplay_after_evolution_1280x720.png`, `hud_energy_slots_1280x720.png`).
- Rendimiento con GPU física: **NOT TESTED** (el contenedor solo tiene rasterizador software `llvmpipe`).

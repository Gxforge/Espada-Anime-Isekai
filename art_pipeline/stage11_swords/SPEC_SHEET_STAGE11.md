# SPEC SHEET — Etapa 11 (Era III · Especialización III) — 5 espadas bespoke

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 941–989. Build: `build_stage11_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage11_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_solstice_martyr_relic` — «Reliquia Solar del Solsticio» (blessed)
- Stats: dmg 102.3 · +173.4 elem · spd 1.259 · rng 4.46 · pasiva «Llama de Redención»
- Parents: halcyon_aegis + permafrost_prism + jade_chakram
- Geometría (8 piezas): mandoble perla-oro 14-vert (2.10) · guardia disco-solar (anillo + 8 rayos) · halos de mártir flotantes ×2 (detrás, escalonados) · llamas de redención serpenteantes ×2 caras · núcleo cápsula-reliquia con gema · pomo orbe-solar
- PBR: perla-oro grabado, bronce radial, grip seda marfil; BR disco solar (rayos + anillo + halo)
- Build: 1120 v / 2128 t · scale 1.0548 · engine 8 mesh_instances ✔

## 2. `cursed_malakor_usurper_thorn` — «Espina Usurpadora de Malakor» (cursed)
- Stats: dmg 111.3 · +167.2 elem · spd 1.691 · rng 4.13 · pasiva «Sangre de Señor Demonio»
- Parents: soul_devourer + permafrost_prism
- Geometría (7 piezas): hoja púrpura-negra 12-vert (1.98) · espinas alternadas lomo/filo ×7 · guardia corona invertida (banda + 5 puntas abajo) · sarmientos de espinas en el grip ×3 · núcleo corazón-demonio · pomo bola de espinas
- PBR: púrpura abisal con costillas, moteado oscuro, grip pespuntes; BR corona usurpada invertida + anillo de espinas carmesí
- Build: 748 v / 1384 t · scale 1.0994 · engine 7 mesh_instances ✔

## 3. `elemental_pyroclasm_heart_greatsword` — «Mandoble Corazón Piroclástico» (elemental)
- Stats: dmg 85.2 · +219.9 elem · spd 1.466 · rng 4.46 · pasiva «Erupción Interna»
- Parents: halcyon_aegis + soul_devourer + permafrost_prism + chronoglass_paradox
- Geometría (7 piezas): obsidiana volcánica 12-vert (2.04) · venas de magma luminosas ×2 ×2 caras · bombas piroclásticas flotantes ×3 · guardia acantilado basáltico (marco) · núcleo corazón eruptivo con llama-picos ×3 · pomo orbe-magma
- PBR: obsidiana vítrea con grietas ígneas, escoria, grip chamuscado; BR corazón eruptivo (estallido radial + boca)
- Build: 686 v / 1304 t · scale 1.0856 · engine 7 mesh_instances ✔

## 4. `spiritual_reincarnated_saint_edge` — «Filo del Santo Reencarnado» (spiritual)
- Stats: dmg 90.4 · +182.7 elem · spd 1.909 · rng 4.29 · pasiva «Memoria Intacta»
- Parents: halcyon_aegis + jade_chakram + chronoglass_paradox
- Geometría (8 piezas): hoja plata-seda esbelta (2.15) · ecos de vidas pasadas ×3 anillos flotantes escalonados · halo santo doble tras la base · espiral de reencarnación ×2 caras · tsuba loto (anillo + 6 pétalos) · pomo gema-santo
- PBR: plata seda con halos, jade-oro grabado, grip blanco-jade; BR halo santo doble + pétalos de loto pálidos
- Build: 992 v / 1908 t · scale 1.0256 · engine 8 mesh_instances ✔

## 5. `arcane_starlight_glyph_claymore` — «Claymore Glifo de Luz Estelar» (arcane)
- Stats: dmg 80.0 · +277.8 elem · spd 1.438 · rng 4.62 · pasiva «Runa Sideral»
- Parents: soul_devourer + jade_chakram + chronoglass_paradox
- Geometría (7 piezas): mandoble indigo 14-vert (2.08) · constelación glifo (4 segmentos + 4 estrellas-punto) ×2 caras · guardia anillo estelar + 5 puntas-estrella con mini-estrellas · estrellas orbitantes ×4 · núcleo gema-estrella octaédrica · pomo orbe-estelar
- PBR: indigo nocturno facetado, violeta chispeante, grip violeta; BR constelación (puntos + líneas + estallido)
- Build: 1232 v / 2276 t · scale 1.0678 · engine 7 mesh_instances ✔

## Catálogo
- 118 formas · 51 GLB bespoke verificados (pilot + Etapas 02–11) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 5 formas stage-11 → `verified_stage11_glb` / `canon_approved_stage11`
- Tests: **752/752** · Hoja: 12×5, 58 cards (7032×3680)

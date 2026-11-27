# SPEC SHEET — Etapa 12 (Era III → IV · Afinidad V) — 6 espadas bespoke + segunda híbrida secreta

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 1041–1099. Build: `build_stage12_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage12_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_archangel_verdict_claymore` — «Claymore Veredicto de Arcángel» (blessed)
- Stats: dmg 112.4 · +192.5 elem · spd 1.282 · rng 4.57 · pasiva «Sentencia Celeste»
- Parents: solstice_martyr + pyroclasm_heart + saint_reincarnated
- Geometría (8 piezas): mandoble blanco-catedral 14-vert (2.08) · arcos catedralicios grabados ×2 caras ×3 · alas de arcángel ascendentes ×2 ×3 plumas · guardia fachada catedral (barra + arco central) · núcleo gema-veredicto rombo + anillo · pomo gema
- PBR: blanco-perla catedral con arcos, oro plumaje, grip marfil; BR sello de veredicto (halo + haz descendente)
- Build: 1136 v / 2156 t · scale 1.0634 · engine 8 mesh_instances ✔

## 2. `cursed_hellfire_executioner_blade` — «Hoja Verdugo de Fuego Infernal» (cursed)
- Stats: dmg 122.4 · +185.7 elem · spd 1.722 · rng 4.23 · pasiva «Ceniza Condenada»
- Parents: malakor_thorn + pyroclasm_heart
- Geometría (8 piezas): hoja obsidiana-púrpura (2.00) · fisuras de fuego ×2 caras ×3 · humo infernal flotante ×3 · guardia capucha + pica · cadena de condena ×5 eslabones · núcleo brasa-horno · pomo gota de ceniza
- PBR: obsidiana con fisuras lava, escoria, grip hueso; BR anillo de fuego + humo ascendente
- Build: 1038 v / 1988 t · scale 1.1064 · engine 8 mesh_instances ✔

## 3. `elemental_maelstrom_triad_blade` — «Hoja Tríada del Maelstrom» (elemental)
- Stats: dmg 93.7 · +244.1 elem · spd 1.493 · rng 4.56 · pasiva «Vórtice Triple»
- Parents: solstice_martyr + malakor_thorn + pyroclasm_heart + starlight_glyph
- Geometría (9 piezas): hoja principal curva + 2 hojas-tríada paralelas ±0.044 · anillos vórtice ×2 · guardia anillo-tormenta + 3 púas a 120° · surcos de marea ×2 caras · núcleo ojo-del-remolino · pomo orbe-tríada
- PBR: cian espuma con remolinos y bruma, bronce salino, grip jade-espuma; BR vórtice triple (espiral + brazos)
- Build: 922 v / 1784 t · scale 1.1525 · engine 9 mesh_instances ✔

## 4. `spiritual_nirvana_mirror_katana` — «Katana Espejo del Nirvana» (spiritual)
- Stats: dmg 99.5 · +202.9 elem · spd 1.945 · rng 4.39 · pasiva «Mente sin Sombra»
- Parents: solstice_martyr + saint_reincarnated + starlight_glyph
- Geometría (9 piezas): katana espejo (2.10) · ensō zen abierto flotante · líneas de espejo ×2 caras ×3 · ondas de calma ×2 · tsuba ensō con hueco · menuki espejo gemelo · pomo cuenta zen
- PBR: plata espejo pulida, bronce zen rosado, grip seda lila; BR ensō (anillo abierto) + ondas de calma
- Build: 784 v / 1500 t · scale 1.0463 · engine 9 mesh_instances ✔

## 5. `arcane_archmage_singularity_blade` — «Hoja Singularidad de Archimago» (arcane)
- Stats: dmg 88.0 · +308.3 elem · spd 1.465 · rng 4.73 · pasiva «Colapso Arcano»
- Parents: malakor_thorn + saint_reincarnated + starlight_glyph
- Geometría (9 piezas): cristal largo fino (2.12) · orbe singularidad + anillo de acreción · 5 esquirlas orbitando · anillo rúnico con 8 marcas · guardia crescente · runas diagonales ×2 caras ×4 · pomo cuenta-singularidad
- PBR: violeta espacio profundo con nebulosa, bronce estelar, grip violeta; BR singularidad (núcleo oscuro + disco de acreción)
- Build: 1018 v / 1912 t · scale 1.0548 · engine 9 mesh_instances ✔

## 6. `hybrid_stormspirit_dragon_katana` — «Katana Secreta Dragón de Tormenta y Alma» (HÍBRIDA SECRETA 🔒)
- Segunda híbrida del árbol (parents elemental + spiritual, 2 linajes); stages 12 = nodo híbrido/secreto
- Stats: dmg 116.7 · +232.1 elem · spd 1.637 · rng 4.64 · pasiva «Vuelo del Dragón Astral»
- Geometría (8 piezas): katana blanco-azul con escamas (2.10) · escamas en chevron ×2 caras ×5 · cabeza de dragón en la guarda (hocico + cuernos ×2 + bigotes) · espirales de tormenta ×3 · cola de dragón desde el pomo · núcleo ojo-de-dragón · pomo perla de tormenta
- PBR: blanco perla con escamas y tormenta azul, cuernos dorados, grip seda blanco-azul; BR dragón de tormenta (espiral + rayo + ojo)
- Build: 878 v / 1660 t · scale 1.0225 · engine 8 mesh_instances ✔

## Catálogo
- 118 formas · 57 GLB bespoke verificados (pilot + Etapas 02–12, incl. 2 híbridas secretas) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 6 formas stage-12 → `verified_stage12_glb` / `canon_approved_stage12`
- Tests: **752/752** · Hoja: 14×5, 64 cards (8200×3680)

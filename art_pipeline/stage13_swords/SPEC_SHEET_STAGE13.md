# SPEC SHEET — Etapa 13 (Era IV · Afinidad VI — Trascendente) — 5 espadas bespoke

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 1141–1189. Build: `build_stage13_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage13_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_empyrean_halo_blade` — «Hoja Trascendente del Halo Empíreo» (blessed)
- Stats: dmg 123.0 · +212.0 elem · spd 1.306 · rng 4.67 · pasiva «Corona Incorrupta»
- Parents: archangel_verdict + maelstrom_triad + nirvana_mirror + stormspirit_dragon
- Geometría (8 piezas): mandoble perla-oro 14-vert (2.08) · 3 halos imperio concéntricos flotantes · 4 motas de luz orbitantes · guardia corona incorrupta (arco + 7 púas) · filo-luz ascendente ×2 caras · núcleo corazón imperio · pomo orbe-halo
- PBR: perla-oro con arcos, bronce radial, grip seda marfil; BR halos concéntricos + corona
- Build: 1248 v / 2376 t · scale 1.0634 · engine 8 mesh_instances ✔

## 2. `cursed_voidscar_transcendent_sword` — «Espada Trascendente Cicatriz del Vacío» (cursed)
- Stats: dmg 133.9 · +204.4 elem · spd 1.753 · rng 4.32 · pasiva «Herida Cósmica»
- Parents: hellfire_executioner + maelstrom_triad + stormspirit_dragon
- Geometría (7 piezas): hoja negra 12-vert (2.02) · cicatriz cruzada en X + anillo de herida ×2 caras · motas de vacío ×3 · guardia rasgada (arco con corte central) · bordados de cicatriz en grip ×3 · núcleo herida cósmica · pomo gota de vacío
- PBR: negro-vacío con cicatriz magenta, moteado, grip pespuntes magenta; BR cicatriz cósmica (X + herida + anillo)
- Build: 770 v / 1468 t · scale 1.0970 · engine 7 mesh_instances ✔

## 3. `elemental_transcendent_aurora_sword` — «Espada Trascendente de Aurora Polar» (elemental)
- Stats: dmg 102.5 · +268.8 elem · spd 1.520 · rng 4.66 · pasiva «Velo Magnético»
- Parents: archangel_verdict + hellfire_executioner + maelstrom_triad + archmage_singularity
- Geometría (7 piezas): mandoble aurora 14-vert (2.08) · cortinas de aurora onduladas ×2 caras ×3 bandas · 2 pilares magnéticos laterales con 3 aros cada uno · guardia pilar-polo + pica · núcleo viento-solar (espiral) · pomo orbe-polar
- PBR: verde-cian cortinas con destello rosa, bronce polar, grip jade-menta; BR cortinas de aurora ×3
- Build: 1348 v / 2604 t · scale 1.0678 · engine 7 mesh_instances ✔

## 4. `spiritual_transcendent_worldtree_branch` — «Rama Trascendente del Árbol Mundo» (spiritual)
- Stats: dmg 108.8 · +223.4 elem · spd 1.980 · rng 4.49 · pasiva «Raíz del Cosmos»
- Parents: archangel_verdict + nirvana_mirror + archmage_singularity + stormspirit_dragon
- Geometría (9 piezas): tronco-madera 12-vert (2.02) · ramas laterales con mini-hojas ×2 caras ×2 niveles · hojas esmeralda flotantes ×3 · raíces curvas ×3 en la base · guardia corona de ramas + 5 ramitas · anillos de crecimiento ×3 ×2 caras · núcleo semilla-cosmos · pomo orbe-árbol
- PBR: madera-luz con vetas, esmeralda-dorado, grip corteza clara; BR árbol mundo (copa espiral + raíces)
- Build: 1452 v / 2756 t · scale 1.0722 · engine 9 mesh_instances ✔

## 5. `arcane_transcendent_axiom_sword` — «Espada Trascendente del Axioma» (arcane)
- Stats: dmg 96.2 · +339.5 elem · spd 1.491 · rng 4.83 · pasiva «Ley Reescrita»
- Parents: hellfire_executioner + nirvana_mirror + archmage_singularity + stormspirit_dragon
- Geometría (9 piezas): cristal rombo indigo (1.88) · glifos matemáticos (sumas + integrales) ×2 caras ×4 · símbolo infinito flotante · guardia tabla-axioma (doble barra + pilar) · constantes orbitantes ×3 (π, e, φ) · núcleo gema-igualdad · pomo cuenta-axioma
- PBR: cristal indigo facetado con glifos, bronce violeta, grip índigo; BR axioma reescrito (ecuaciones + igualdad + infinito)
- Build: 1110 v / 2060 t · scale 1.1685 · engine 9 mesh_instances ✔

## Catálogo
- 118 formas · 62 GLB bespoke verificados (pilot + Etapas 02–13, incl. 2 híbridas secretas) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 5 formas stage-13 → `verified_stage13_glb` / `canon_approved_stage13`
- Tests: **752/752** · Hoja: 16×5, 69 cards (9368×3680)

## Nota
1 fix menor: `math.pi` → `np.pi` en paint_axiom (el módulo painters no importa math).
Nombres de individual/ deben coincidir exactamente con CARDS (sword_13_axiom.png, no sword_13_axiom_sword.png).

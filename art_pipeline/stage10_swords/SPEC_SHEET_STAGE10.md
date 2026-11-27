# SPEC SHEET — Etapa 10 (Era III · Especialización II) — 5 espadas bespoke

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 841–889. Build: `build_stage10_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage10_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_halcyon_aegis_broadsword` — «Espada Ancha Égida Alción» (blessed)
- Stats: dmg 92.3 · +154.7 elem · spd 1.236 · rng 4.36 · pasiva «Gracia Inmortal»
- Parents: dawnbreaker_templar + twin_monsoon + phantom_nodachi
- Geometría (9 piezas): mandoble ancho dorado 14-vert (2.06, 212→112 mm) · emblema égida con plumones radiales ×2 caras · halo de calma · guardia égida semicúpula + alas escalonadas ×3 · cresta de alción · núcleo corazón-de-mareas · pomo perla
- PBR: acero oro calma con ondas serenas, bronce plumaje, grip plata-acero; BR égida (semicírculo + plumones)
- Build: 1202 v / 2284 t · scale 1.0722 · engine 9 mesh_instances ✔

## 2. `cursed_soul_devourer_brand` — «Blandón Devorador de Almas» (cursed)
- Stats: dmg 100.5 · +149.1 elem · spd 1.659 · rng 4.03 · pasiva «Pozo de Ánimas»
- Parents: abyssal_guillotine + twin_monsoon
- Geometría (8 piezas): masa monolítica 11-vert (2.00, 205 mm) · boca devoradora con dientes ×2 caras · pozo de ánimas (anillo doble) · guardia mandíbulas abiertas arriba/abajo · barbas de cadena en el lomo ×5 · núcleo brasa-horno · pomo bomba de horno
- PBR: acero negro-brasa con grietas ígneas, moteado horno, grip pespuntes rojizos; BR pozo de ánimas (anillo + espiral naranja)
- Build: 1198 v / 2280 t · scale 1.1064 · engine 8 mesh_instances ✔

## 3. `elemental_permafrost_prism_claymore` — «Claymore Prisma de Permafrost» (elemental)
- Stats: dmg 76.9 · +196.1 elem · spd 1.439 · rng 4.35 · pasiva «Espejo Ártico»
- Parents: dawnbreaker_templar + abyssal_guillotine + twin_monsoon + spellweaver_prism
- Geometría (9 piezas): rombo facetado 4-vert (1.98) · espejos árticos diagonales ×2 caras · racimos de escarcha flotantes ×3 · tres púas icicle en la punta · guardia corona de escarcha + 3 picos · núcleo congelado · pomo glaciar
- PBR: hielo facetado con destellos, plata espejo, grip azul-hielo; BR espejo ártico (retícula de rombos + destello radial)
- Build: 766 v / 1428 t · scale 1.1181 · engine 9 mesh_instances ✔

## 4. `spiritual_jade_chakram_soulblade` — «Espada-Alma de Jade y Chakram» (spiritual)
- Stats: dmg 81.6 · +162.9 elem · spd 1.874 · rng 4.19 · pasiva «Rueda del Ki»
- Parents: dawnbreaker_templar + phantom_nodachi + spellweaver_prism
- Geometría (8 piezas): hoja de jade esbelta (1.94) · chakram perpendicular (rueda 8 rayos + buje luminoso, z=0.135) · canales de ki serpenteantes ×2 caras · cuentas de ki gemelas · tsuba disco de jade · núcleo incluido en chakram · pomo cuentas de jade
- PBR: jade marmolado con vetas, jade-oro grabado, grip blanco-jade; BR rueda del ki (anillo + 8 rayos esmeralda)
- Build: 710 v / 1340 t · scale 1.1231 · engine 8 mesh_instances ✔

## 5. `arcane_chronoglass_paradox_saber` — «Sable Paradoja de Cronocristal» (arcane)
- Stats: dmg 72.2 · +247.7 elem · spd 1.412 · rng 4.51 · pasiva «InstanteRepetido»
- Parents: abyssal_guillotine + phantom_nodachi + spellweaver_prism
- Geometría (9 piezas): sable curvo de cristal temporal (1.98) · 2 ecos-paradoja flotantes paralelos · engranaje-rueda del tiempo (8 dientes) · espiral de tiempo ascendente · guardia portal-reloj · núcleo reloj de arena · pomo bomba de reloj
- PBR: cristal violeta-ámbar facetado con remolinos de arena, bronce grabado con marcas, grip violeta; BR engranaje temporal + manecillas
- Build: 826 v / 1572 t · scale 1.1178 · engine 9 mesh_instances ✔

## Catálogo
- 118 formas · 46 GLB bespoke verificados (pilot + Etapas 02–10) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 5 formas stage-10 → `verified_stage10_glb` / `canon_approved_stage10`
- Tests: **752/752** · Hoja: 11×5, 53 cards (6448×3680)

## Nota de infraestructura
Reset del sandbox al inicio del turno (3º): git revertido a `326283d` y toolchain borrada. Recuperación vía
`git reset --hard origin/...` (a `87161d4`) + reinstalación completa de toolchain (~/.local/opt + wrappers ~/bin).
Xvfb requiere proot-bind de xkbcomp (hardcodeado en /usr/bin por el paquete xorg-server).

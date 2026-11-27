# SPEC SHEET — Etapa 14 (Era IV · Afinidad VII) — 5 espadas bespoke

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 1241–1289. Build: `build_stage14_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage14_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_sanctified_sunforge_sword` — «Espada Forjasol Santificada» (blessed)
- Stats: dmg 133.8 · +231.8 elem · spd 1.328 · rng 4.78 · pasiva «Crisol Sagrado»
- Parents: blessed_empyrean_halo_blade + elemental_transcendent_aurora_sword + spiritual_transcendent_worldtree_branch
- Geometría (7 piezas): mandoble oro-forja 14-vert (2.10) · costuras de forja diagonales ×2 caras ×3 · llamas solares ascendentes ×3 · guardia yunque-forja (anillo + 2 pares de tenazas) · núcleo crisol con orbe fundido · grip forja trenzada · pomo yunque-bulbo con anillo
- PBR: oro-fundido con costillas incandescentes, bronce radial martillado, grip cobre-oro; BR crisol sagrado (boca de forja + llamas ascendentes)
- Build: 784 v / 1488 t · scale 1.0548 · engine 7 mesh_instances ✔

## 2. `cursed_dread_leviathan_fang` — «Colmillo Aterrador de Leviatán» (cursed)
- Stats: dmg 145.7 · +223.5 elem · spd 1.784 · rng 4.42 · pasiva «Presión de Fosa»
- Parents: cursed_voidscar_transcendent_sword + elemental_transcendent_aurora_sword
- Geometría (7 piezas): colmillo curvado orgánico (1.90, curva t^1.7) · ventosas ×2 filas ×6 · anillos de percebes ×2 · guardia mandíbula con 4 colmillos menores ×2 lados · núcleo ojo de fosa · grip kelp trenzado · pomo cola-aza (squash 1.45)
- PBR: púrpura-abisal con venas magenta, filas de ventosas, grip verde-musgo; BR presión de fosa (anillos concéntricos + ojo abisal)
- Build: 1010 v / 1908 t · scale 1.1553 · engine 7 mesh_instances ✔

## 3. `elemental_tectonic_mantle_breaker` — «Quebrantamantos Tectónico» (elemental)
- Stats: dmg 111.6 · +293.9 elem · spd 1.548 · rng 4.77 · pasiva «Falla Continental»
- Parents: blessed_empyrean_halo_blade + cursed_voidscar_transcendent_sword + elemental_transcendent_aurora_sword + arcane_transcendent_axiom_sword
- Geometría (7 piezas): losa-pico 14-vert (2.00) · fallas de lava zigzag ×2 caras ×2 · fragmentos continentales flotantes ×3 · guardia placas de falla (2 losas desplazadas por lado) · núcleo corazón del manto · grip piedra trenzada · pomo roca-bulbo
- PBR: roca gris con grietas incandescentes, grava fina, grip gris-cálido; BR falla continental (grieta zigzag + manto + escalones sísmicos)
- Build: 720 v / 1376 t · scale 1.1040 · engine 7 mesh_instances ✔

## 4. `spiritual_astral_wind_sovereign` — «Espada Viento Astral» (spiritual)
- Stats: dmg 118.4 · +244.2 elem · spd 2.015 · rng 4.60 · pasiva «Vuelo Infinito»
- Parents: blessed_empyrean_halo_blade + spiritual_transcendent_worldtree_branch + arcane_transcendent_axiom_sword
- Geometría (8 piezas): hoja fina curvada 14-vert (2.06, spine t^1.8) · estelas de viento ×2 caras ×2 líneas · plumas-viento grandes curvadas ×2 caras ×2 · anillos ciclónicos cónicos ×2 · guardia barra + alas barridas ×3 niveles · núcleo zéfiro (esfera + anillo orbital) · grip seda-viento · pomo orbe-brisa
- PBR: plata-cian con corrientes, bronce-aero con destello dorado, grip blanco-turquesa; BR vuelo infinito (ciclogénesis + estelas + plumas)
- Build: 1000 v / 1904 t · scale 1.0766 · engine 8 mesh_instances ✔ (v2: hoja circular v1 rechazada en QA → sección afilada 14-vert + alas grandes)

## 5. `arcane_voidmath_tesseract_edge` — «Filo Teseracto de Vacío Geométrico» (arcane)
- Stats: dmg 104.7 · +371.2 elem · spd 1.518 · rng 4.94 · pasiva «Cuarta Dimensión»
- Parents: cursed_voidscar_transcendent_sword + spiritual_transcendent_worldtree_branch + arcane_transcendent_axiom_sword
- Geometría (8 piezas): hoja exterior rombo 4-vert (1.86) · hoja interior teseracto (mitad de escala, misma altura) · struts hiper-aristas ×2 caras ×2 niveles ×2 ejes · marcos-cubo rotando ×2 (exterior + interior + 4 conectores) · guardia marco hiper-cubo (doble rectángulo) · núcleo corazón 4D (cubo en cubo) · grip geométrica · pomo hiper-cuenta
- PBR: índigo facetado con retícula magenta, violeta destello, grip índigo-oscuro; BR teseracto (marcos interior/exterior + conectores + vacío)
- Build: 672 v / 1220 t · scale 1.1791 · engine 8 mesh_instances ✔

## Catálogo
- Hoja: `sword_catalog_sheet.png` 18×5 · 74 cards (10536×3680) · 67 GLB bespoke verificados + 7 siluetas OBJ legacy provisionales
- Cableado: `STAGE14_GLB` (5 entradas) · estados `verified_stage14_glb` / `canon_approved_stage14` · regen JSON 118 forms
- Tests: 752/752 ✔ · Engine: 7/7/7/8/8 mesh_instances

## Nota
Era IV Afinidad VII sin híbrida (próxima híbrida secreta en Etapa 16). GLBs y texturas en
`godot_project/assets/models/swords/{sunforge, leviathan_fang, tectonic_breaker, astral_wind, tesseract}/`,
fuentes `.blend` y renders en `art_pipeline/stage14_swords/`.

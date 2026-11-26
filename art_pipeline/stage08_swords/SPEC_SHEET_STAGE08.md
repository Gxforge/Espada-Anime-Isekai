# SPEC SHEET — Etapa 08 (Era II · Afinidad IV) — 6 espadas bespoke + primera híbrida secreta

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 681–735. Build: `build_stage08_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage08_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_radiant_covenant_greatsword` — «Mandoble de la Alianza Radiante» (blessed)
- Stats: dmg 73.5 · +118.3 elem · spd 1.189 · rng 4.16 · skill «Sello del Santuario»
- Parents: seraph_wing + magma_vein + moonlit_lotus
- Geometría (8 piezas): gran mandoble perla 14-vert (2.08, 185→100 mm) · sello santuario doble anillo z=1.02 ×2 caras · pulse strips · guarda velo-ala 2 capas ×2 lados · core reliquia · pomo orbe
- PBR: acero perla con sheen, damasquino oro, grip seda blanco-oro; BR sigilo santuario (anillos concéntricos + cruz oro)
- Build: 1109 v / 2150 t · scale 0.9793 · engine 8 mesh_instances ✔

## 2. `cursed_bloodmoon_pact_greatsword` — «Mandoble del Pacto Luna Sangrienta» (cursed)
- Stats: dmg 80.0 · +114.1 elem · spd 1.597 · rng 3.84 · skill «Tributo Vital»
- Parents: nightmare_chitin + magma_vein
- Geometría (8 piezas): hoja 14-vert con muescas alternas (notch 0.022 i impar i≥5, 2.00) · disco luna sangrienta emboss z=0.98 · venas de pacto full-length · guarda crescente invertido + cuernos ×2 · pomo gota de sangre (squash 1.35)
- PBR: acero carmesí oscuro con venas, crestas oscuras, grip sangre; BR disco luna sangrienta con cráteres
- Build: 1048 v / 2032 t · scale 1.0136 · engine 8 mesh_instances ✔

## 3. `elemental_thunderlord_fulgur_edge` — «Filo Fulgur del Señor del Trueno» (elemental)
- Stats: dmg 61.3 · +150.0 elem · spd 1.385 · rng 4.14 · skill «Descarga Celeste»
- Parents: seraph_wing + nightmare_chitin + magma_vein + aether_conduit
- Geometría (8 piezas): hoja tormenta 12-vert (2.06, 160→70 mm) · prongs de tridente ×2 (split z1.44→2.10) · canales de tormenta · guarda corona + 3 dientes chispa · orbe fulgur
- PBR: acero tormenta con relámpagos, martillado, grip azul tormenta; BR zigzag relámpago blanco-cian
- Build: 781 v / 1502 t · scale 0.9810 · engine 8 mesh_instances ✔

## 4. `spiritual_ancestral_chorus_sword` — «Espada Coro de los Ancestros» (spiritual)
- Stats: dmg 65.0 · +124.6 elem · spd 1.804 · rng 3.99 · skill «Cien Voces»
- Parents: seraph_wing + moonlit_lotus + aether_conduit
- Geometría (9 piezas): hoja bronce-campana ripple 12-vert (2.00) · ecos de onda ×3 ×2 caras · halos de ancestros ×4 flotantes · tubos-campana ×2 con aros · guarda arco campana · pomo campana
- PBR: bronce campana con pátina verdigrís, grip seda jade; BR ondas coro teal + puntos
- Build: 1113 v / 2134 t · scale 1.0548 · engine 9 mesh_instances ✔

## 5. `arcane_grimoire_monolith_greatsword` — «Mandoble Monolito de Grimorio» (arcane)
- Stats: dmg 57.5 · +189.4 elem · spd 1.359 · rng 4.29 · skill «Siete Sellos»
- Parents: nightmare_chitin + moonlit_lotus + aether_conduit
- Geometría (8 piezas): monolito índigo 14-vert (1.96, 205 mm base) · 7 gemas-sello en línea ×2 caras (z=0.36+0.20k) · líneas oro canto-página · guarda lomo-libro + 2 broches · pomo sello
- PBR: índigo basalto-libro con líneas oro, bandas cuero, grip índigo; BR 7 sellos en puntos violeta
- Build: 1017 v / 1930 t · scale 1.0400 · engine 8 mesh_instances ✔

## 6. `hybrid_twilight_covenant_blade` — «Espada Híbrida del Pacto Crepuscular» (HÍBRIDA SECRETA 🔒)
- Primera híbrida del árbol (components blessed + cursed); stage 8/12/16/20/24 son nodos híbridos/secreto
- Stats: dmg 76.3 · +142.6 elem · spd 1.518 · rng 4.22 · skill «Equilibrio Luz-Sombra» (robo de vida abisal + escudos solares)
- Parents: seraph_wing + nightmare_chitin
- Geometría (8 piezas): hoja 12-vert dividida L/R (L perla-luz · R violeta-sombra, 2.02) · costura crepuscular luminosa central · piedras orbitales duales (oro z0.92 / violeta z1.24) · guarda asimétrica ala-luz + garra-sombra · core eclipse (anillo brillante + corazón)
- PBR: hoja dividida L perla / R violeta, damasquino crepúsculo, grip dual; BR eclipse (anillo + corona)
- Build: 799 v / 1534 t · scale 1.0256 · engine 8 mesh_instances ✔

## Catálogo
- 118 formas · 36 GLB bespoke verificados (pilot + Etapas 02–08) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 6 formas stage-8 → `verified_stage08_glb` / `canon_approved_stage08`
- Tests: **752/752** · Hoja: 9×5, 43 cards (4112→5280 px ancho)

# SPEC SHEET — Etapa 09 (Era III · Especialización) — 5 espadas bespoke

Pipeline Studio Lexair completo (PBR → Blender → GLB → renders neutros → verificación en motor Godot 4.4).
Seeds painters: 741–789. Build: `build_stage09_swords.py` (normalize h=2.60, pivot grip, Emission 2.2).
Renders: `render_stage09_swords.py` (6 vistas neutras + silueta, Cycles 48 spp). Engine: `view_engine_verified_34.png` por carpeta.

## 1. `blessed_dawnbreaker_templar_blade` — «Hoja Templaria Rompealbas» (blessed)
- Stats: dmg 82.8 · +136.3 elem · spd 1.213 · rng 4.25 · pasiva «Juicio Matutino»
- Parents: radiant_covenant + thunderlord_fulgur + ancestral_chorus + twilight_covenant
- Geometría (8 piezas): mandoble templario 14-vert (2.10) · rayos de amanecer en abanico ×2 caras · línea de templado luminosa · guardia arco-sol naciente + rayos irradiados · núcleo reliquia solar · pomo anillo-sol
- PBR: acero oro solar con rayos, bronce grabado radial, grip seda crema-roja; BR sol naciente (disco + rayos + horizonte)
- Build: 852 v / 1596 t · scale 1.0548 · engine 8 mesh_instances ✔

## 2. `cursed_abyssal_guillotine_edge` — «Filo Guillotina del Abismo» (cursed)
- Stats: dmg 90.1 · +131.4 elem · spd 1.628 · rng 3.94 · pasiva «Corte Implacable»
- Parents: bloodmoon_pact + thunderlord_fulgur + twilight_covenant
- Geometría (8 piezas): masa de verdugo 11-vert ancha (2.06, poco afilada al final) · aparturas hexagonales ×2 · venas de vacío rosas full-length · guardia boca-del-abismo crescente + cuernos ×2 · púas de tortura en el lomo ×6 · corazón de vacío · pomo gota
- PBR: acero púrpura-negro con filo rosa, moteado abisal, grip pespuntes; BR anillo de apartura + sendero de descenso
- Build: 872 v / 1656 t · scale 1.0788 · engine 8 mesh_instances ✔

## 3. `elemental_twin_monsoon_saber` — «Sable Gemelo del Monzón» (elemental)
- Stats: dmg 69.0 · +172.8 elem · spd 1.412 · rng 4.25 · pasiva «Viento Cortante»
- Parents: radiant_covenant + bloodmoon_pact + thunderlord_fulgur + grimoire_monolith
- Geometría (9 piezas): hoja principal curva (sable) + hoja gemela paralela más corta · horquilla de bifurcación · guardia crescente monzón · surcos de lluvia ×2 ×2 caras · núcleo ojo-de-tormenta · pomo orbe con aro
- PBR: acero cielo con lluvia diagonal y remolino, bronce cincelado, grip jade-lluvia; BR chubasco (arcos de vendaval + rayo cian)
- Build: 840 v / 1620 t · scale 1.1130 · engine 9 mesh_instances ✔

## 4. `spiritual_phantom_sever_nodachi` — «Nodachi Cortafantasmas» (spiritual)
- Stats: dmg 73.2 · +143.6 elem · spd 1.839 · rng 4.09 · pasiva «Filo Etéreo»
- Parents: radiant_covenant + ancestral_chorus + grimoire_monolith + twilight_covenant
- Geometría (8 piezas): nodachi esbelta 9 estaciones (2.22, curva ascendente) · hamon ondulado espectral ×2 caras · wisps de fuego fantasma ×3 · tsuba oval-sello · menuki gemelos · collar ferrule · pomo kabuto-gashira
- PBR: acero plata con wisps esmeralda, bronce teal grabado, lacado negro-verdoso, grip blanco-jade; BR fuegos fatuos ×4
- Build: 552 v / 1052 t · scale 0.9981 · engine 8 mesh_instances ✔

## 5. `arcane_spellweaver_prism_edge` — «Filo Prisma Tejehechizos» (arcane)
- Stats: dmg 64.7 · +218.3 elem · spd 1.385 · rng 4.40 · pasiva «Doble Conjuro»
- Parents: bloodmoon_pact + ancestral_chorus + grimoire_monolith + twilight_covenant
- Geometría (9 piezas): hoja cristal rombo 4-vert (1.86) · tres puntas de prisma divididas · retícula de runas diagonales ×2 caras · guardia marco de grimorio abierto · anillo orbitante de 6 fragmentos arcanos · núcleo prisma · pomo esquirla
- PBR: cristal índigo facetado con destellos fucsia, bronce chispeante, grip violeta; BR retícula de runas + triángulo prisma
- Build: 568 v / 1036 t · scale 1.1579 · engine 9 mesh_instances ✔

## Catálogo
- 118 formas · 41 GLB bespoke verificados (pilot + Etapas 02–09) · 7 siluetas OBJ legacy provisionales
- `evolution_catalog.json` regenerado: 5 formas stage-9 → `verified_stage09_glb` / `canon_approved_stage09`
- Tests: **752/752** · Hoja: 10×5, 48 cards (5864×3680)

## Nota de infraestructura
El reset del sandbox entre turnos capó el snapshot del workspace (pérdida parcial de binarios) y revertió `.git`
al commit de la galería. Recuperación: respaldo del trabajo Etapa 09 fuera del repo → `git fetch origin` +
`git reset --hard origin/feature/godot-complete-reconstruction` (HEAD `d03ae5a`) → restauración del trabajo →
re-import del caché de Godot. Sin pérdida neta. Toolchain reinstalado en `~/.local/opt` (Blender 4.3.2 + Godot 4.4
+ libxkbcommon/libunwind/xvfb vía .debs extraídos; Xvfb bajo proot por el xkbcomp hardcodeado en /usr/bin).

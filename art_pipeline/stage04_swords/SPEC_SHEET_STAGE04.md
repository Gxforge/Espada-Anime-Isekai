# SPEC SHEET — Stage 04 "Awakening Finale" Batch (5 GLBs, Studio Lexair)

Proyecto: Espada Anime Isekai · Rama `feature/godot-complete-reconstruction`
Pipeline: Blender 4.3.2 (geometría única → UVs atlas → 5 mapas PBR 1024² → `.blend`) → renders neutros Cycles → GLB → verificación Godot 4.4 (Vulkan/Xvfb) → cableado catálogo.
Estilo: anime exagerado por linaje. NO meshes procedurales runtime, NO recolores.
Cierre de la **Era I — Despertar**: las 5 ramas fundamentales (blessed/cursed/elemental/spiritual/arcane) quedan con GLB propio.

## Formas cubiertas (stage 04, nivel 9, xp 220, mats {slime_gel:4})

| # | Form ID | Nombre | Linaje / Parents | GLB | Dir |
|---|---------|--------|------------------|-----|-----|
| 1 | `awakening_sunbark_vow_greatsword` | Mandoble del Voto Heliófilo | blessed ← amber+ironwood | `sword_04_sunbark_vow.glb` | `sunbark_vow/` |
| 2 | `awakening_thornheart_hex_blade` | Hoja Maldita Corazón de Espina | cursed ← bramble | `sword_04_thornheart_hex.glb` | `thornheart_hex/` |
| 3 | `awakening_fulgurite_crest_sword` | Espada Cresta de Fulgurita | elemental ← ironwood+willow+bramble | `sword_04_fulgurite_crest.glb` | `fulgurite_crest/` |
| 4 | `awakening_jade_anima_katana` | Katana Ánima de Jade | spiritual ← amber+willow | `sword_04_jade_anima.glb` | `jade_anima/` |
| 5 | `awakening_runebark_codex_blade` | Espada Códice de Corteza Rúnica | arcane ← las 4 de stage 3 | `sword_04_runebark_codex.glb` | `runebark_codex/` |

## Resultados de build (Blender, escala normalizada h≈2.60, pivote en empuñadura)

| Espada | Piezas | Vértices | Tris | Escala |
|--------|--------|----------|------|--------|
| sunbark_vow | 7 | 893 | 1722 | 0.9683 |
| thornheart_hex | 7 | 804 | 1552 | 1.0136 |
| fulgurite_crest | 8 | 709 | 1370 | 0.9905 |
| jade_anima | 7 | 626 | 1212 | 1.0097 |
| runebark_codex | 7 | 834 | 1584 | 0.9962 |

## Identidad visual (anime exagerado)

- **Sunbark Vow (mandoble solar)**: hoja 14-vert con punta de verdugo acampanada (flare t>0.80), fullers solares ×2 emisivos, guarda disco amanecer + 6 rayos dorados, corazón voto-del-alba, pomo dial solar. Glow oro (1.0, 0.82, 0.28).
- **Thornheart Hex (hoja hex maldita)**: hoja 12-vert con muescas serradas alternas (notch 0.020/0.004), venas rúnicas púrpura ×2, corazón-lobe envuelto en anillo de espinas, guarda collar de 4 espinas índigo cruzadas, pomo brota-espinas squash 1.2. Glow rosa (0.96, 0.22, 0.32).
- **Fulgurite Crest (vid relámpago)**: hoja 12-vert vitrea con borde ondulado (wave 0.012·sin 9t), cresta-sierra de rayo en el lomo, ramas fulgurita cian ×2, quillones de vid fundido con gota, núcleo ígneo-voltaico. Glow dual naranja+cian.
- **Jade Anima (katana)**: hoja 12-vert curvada (cur = −0.075·t^1.65, ancho 62→42mm, kissaki ×0.72), hamon de jade pegado al filo, tsuba doble elipse jade (squash 0.62), farol ánima flotante, tsuka con wrap rombos, kashira jade. Glow esmeralda (0.25, 0.95, 0.62).
- **Runebark Codex (grimorio)**: hoja 14-vert con punta cuadrada de libro (width 0.092 fija desde z=1.82), columnas de glifos magenta 4×2 caras, guarda cubierta de códice (2 losas inclinadas + lomo), halo rúnico con 3 piedras orbitales, pomo sello. Glow magenta (0.95, 0.55, 1.0).

## PBR / Renders / Motor

- Atlas 5 regiones (blade TL, flair TR, grip BL, shell BM, glow BR), painters seeds 471–519 en `generate_stage04_pbr_maps.py`; 5 PNGs 1024² por dir en `godot_project/assets/models/swords/{dir}/`.
- 30 renders neutros Cycles (6 vistas × 5) en `art_pipeline/stage04_swords/{dir}/renders/`; QA visual view_04 ×5 OK.
- Verificación Godot 4.4 Vulkan/Xvfb (`/tmp/verify_stage04.gd`, `ModelLoader.build_glb_scene_instance(path, 2.6, true)`):

| Espada | mesh_instances | Captura |
|--------|----------------|---------|
| sunbark | 7 | `sunbark_vow/view_engine_verified_34.png` |
| thornheart | 7 | `thornheart_hex/view_engine_verified_34.png` |
| fulgurite | 8 | `fulgurite_crest/view_engine_verified_34.png` |
| jadeanima | 7 | `jade_anima/view_engine_verified_34.png` |
| runebark | 7 | `runebark_codex/view_engine_verified_34.png` |

mesh_instances == piezas del build en las 5 → GLB íntegro en motor.

## Cableado catálogo

`STAGE04_GLB` en `generate_evolution_and_skills_data.py` → `verified_stage04_glb` / `canon_approved_stage04` (fallback stage03 → stage02 → pilot → legacy OBJ). JSON regenerado (118 forms). Tests: **752/752**.

## Estado del catálogo 3D tras Etapa 04

13/118 formas con GLB bespoke verificado: pilot (1) + stage02 (3) + stage03 (4) + stage04 (5). Resto `extensible_blueprint_pending_3d`.
Hoja catálogo: `art_pipeline/sword_catalog_renders/sword_catalog_sheet.png` (2360×3680, grid 4×5, 20 cards).

## Artefactos fuente

- `art_pipeline/stage04_swords/generate_stage04_pbr_maps.py` / `build_stage04_swords.py` / `render_stage04_swords.py`
- `art_pipeline/stage04_swords/{dir}/` — `.blend` editable + engine shot
- Nota: painters derivan del prefijo compartido stage-03; builders reutilizan helpers (add_lofted_tube/curved_loft/grip_braid/ferrule_pair/bulb_pommel/strip_loft/make_rings).

# SPEC SHEET — Stage 06 "Affinity II" Batch (5 GLBs, Studio Lexair)

Proyecto: Espada Anime Isekai · Rama `feature/godot-complete-reconstruction`
Pipeline: Blender 4.3.2 (geometría única → UVs atlas → 5 mapas PBR 1024² → `.blend`) → renders neutros Cycles → GLB → verificación Godot 4.4 (Vulkan/Xvfb) → cableado catálogo.
Estilo: anime exagerado por linaje. NO meshes procedurales runtime, NO recolores.

## Formas cubiertas (stage 06)

| # | Form ID | Nombre | Linaje / Parents | GLB | Dir |
|---|---------|--------|------------------|-----|-----|
| 1 | `blessed_auric_bastion_claymore` | Claymore Bastión Áurico | blessed ← solarinit+tempest+silver | `sword_06_auric_bastion.glb` | `auric_bastion/` |
| 2 | `cursed_crimson_reaver_cleaver` | Hendidora Segadora Carmesí | cursed ← obsidianfang+tempest | `sword_06_crimson_reaver.glb` | `crimson_reaver/` |
| 3 | `elemental_glacier_fang_longsword` | Espada Larga Colmillo de Glaciar | elemental ← solarinit+obsidianfang+tempest+crystal | `sword_06_glacier_fang.glb` | `glacier_fang/` |
| 4 | `spiritual_mistwalker_bamboo_katana` | Katana Caminante de la Niebla | spiritual ← solarinit+silver+crystal | `sword_06_mistwalker_bamboo.glb` | `mistwalker_bamboo/` |
| 5 | `arcane_astrolabe_ring_blade` | Hoja Anillo de Astrolabio | arcane ← obsidianfang+silver+crystal | `sword_06_astrolabe_ring.glb` | `astrolabe_ring/` |

## Resultados de build (Blender, escala normalizada h≈2.60, pivote en empuñadura)

| Espada | Piezas | Vértices | Tris | Escala |
|--------|--------|----------|------|--------|
| auric_bastion | 8 | 755 | 1438 | 0.9905 |
| crimson_reaver | 8 | 892 | 1720 | 1.0039 |
| glacier_fang | 8 | 789 | 1502 | 0.9886 |
| mistwalker_bamboo | 9 | 1000 | 1928 | 1.0256 |
| astrolabe_ring | 8 | 1194 | 2312 | 0.9612 |

## Identidad visual (anime exagerado)

- **Auric Bastion (fortaleza dorada)**: claymore 14-vert de muro ancho (175→105mm) con punta roma, **5 almenas de oro vivo** en el lomo, venas-muralla emisivas, guarda barra de rampar con 3 dientes-almena, corazón bastión, pomo torreta. Glow oro (1.0, 0.84, 0.30).
- **Crimson Reaver (segadora)**: hendidera 14-vert masiva (190mm) con **punta-gancho** (flare t>0.82), oleaje ×1.05 alternante, emblema luna-segadora (anillo + creciente), aletas-thorn ×3 en el lomo, guarda hoz creciente (150mm × squash 0.42) con 2 púas, corazón cosecha, pomo hoz-sickle. Glow carmesí (1.0, 0.24, 0.20).
- **Glacier Fang (colmillo glaciar)**: espada larga 12-vert de hielo con biseles nítidos, **4 colmillos-carambano colgando del lomo**, líneas de deshielo emisivas, guarda estante-de-hielo con 2 carambanos hacia abajo por lado, estrella congelada, pomo iceberg. Glow cian-blanco (0.80, 0.96, 1.0).
- **Mistwalker Bamboo (bambú niebla)**: katana 12-vert de bambú pálido (70→44mm), **4 nudos-collar de bambú** sobre la hoja, wisps de niebla emisivos, halo-nube de niebla ×3 anillos flotando junto a la hoja, tsuba bambú tejido, farol de niebla, pomo anillo-bambú. Glow menta-niebla (0.85, 0.98, 0.92).
- **Astrolabe Ring (armilar)**: hoja 12-vert charted esbelta (105→37mm, alcance 4.08), etch cartas-estelares doradas emisivas, **esfera armilar completa**: anillo vertical 125mm + anillo inclinado 98mm + anillo horizontal 86mm con 4 estrellas orbitales, guarda disco-astrolabio con aguja-puntero, corazón polaris, pomo gimbales. Glow oro-blanco (1.0, 0.90, 0.62).

## PBR / Renders / Motor

- Atlas 5 regiones, painters seeds 571–621 en `generate_stage06_pbr_maps.py`; 5 PNGs 1024² por dir.
- 30 renders neutros Cycles (6 vistas × 5) en `art_pipeline/stage06_swords/{dir}/renders/`; QA visual view_04 ×5 OK.
- Verificación Godot 4.4 Vulkan/Xvfb (`/tmp/verify_stage06.gd`): auric **8**, reaver **8**, glacier **8**, mistwalk **9**, astrolabe **8** mesh_instances — todas iguales a las piezas del build → GLB íntegro. Capturas `view_engine_verified_34.png` en cada dir.

## Cableado catálogo

`STAGE06_GLB` + cadenas extendidas en ambas rutas del generador (bloque Era I + bucle 5–24) → `verified_stage06_glb`/`canon_approved_stage06`. JSON regenerado (118 forms). Tests: **752/752**.

## Estado del catálogo 3D tras Etapa 06

**23/118** formas con GLB bespoke verificado: pilot (1) + stage02 (3) + stage03 (4) + stage04 (5) + stage05 (5) + stage06 (5). Resto `extensible_blueprint_pending_3d`.
Hoja catálogo: `sword_catalog_sheet.png` (3528×3680, grid 6×5, 30 cards).

## Artefactos fuente

- `art_pipeline/stage06_swords/generate_stage06_pbr_maps.py` / `build_stage06_swords.py` / `render_stage06_swords.py`
- `art_pipeline/stage06_swords/{dir}/` — `.blend` editable + engine shot
- Fixes de este lote: Vector() explícito en paths de curved_loft (reaver thorns); corte de prefijo por índice (junta `#===` de stage05 pegada a comentario).

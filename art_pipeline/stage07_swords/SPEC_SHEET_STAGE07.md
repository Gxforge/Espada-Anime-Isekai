# SPEC SHEET — Stage 07 "Affinity III" Batch (5 GLBs, Studio Lexair)

Proyecto: Espada Anime Isekai · Rama `feature/godot-complete-reconstruction`
Pipeline: Blender 4.3.2 (geometría única → UVs atlas → 5 mapas PBR 1024² → `.blend`) → renders neutros Cycles → GLB → verificación Godot 4.4 (Vulkan/Xvfb) → cableado catálogo.
Estilo: anime exagerado por linaje. NO meshes procedurales runtime, NO recolores.

## Formas cubiertas (stage 07)

| # | Form ID | Nombre | Linaje / Parents | GLB | Dir |
|---|---------|--------|------------------|-----|-----|
| 1 | `blessed_seraph_wing_longsword` | Espada Larga Ala de Serafín | blessed ← bastion+glacier+mistwalker | `sword_07_seraph_wing.glb` | `seraph_wing/` |
| 2 | `cursed_nightmare_chitin_sword` | Espada Quitina de Pesadilla | cursed ← reaver+glacier | `sword_07_nightmare_chitin.glb` | `nightmare_chitin/` |
| 3 | `elemental_magma_vein_broadsword` | Espada Ancha Vena de Magma | elemental ← bastion+reaver+glacier+astrolabe | `sword_07_magma_vein.glb` | `magma_vein/` |
| 4 | `spiritual_moonlit_lotus_blade` | Hoja Loto de Plenilunio | spiritual ← bastion+mistwalker+astrolabe | `sword_07_moonlit_lotus.glb` | `moonlit_lotus/` |
| 5 | `arcane_aether_conduit_rapier` | Estoque Conducto de Éter | arcane ← reaver+mistwalker+astrolabe | `sword_07_aether_conduit.glb` | `aether_conduit/` |

## Resultados de build (Blender, escala normalizada h≈2.60, pivote en empuñadura)

| Espada | Piezas | Vértices | Tris | Escala |
|--------|--------|----------|------|--------|
| seraph_wing | 8 | 863 | 1662 | 0.9830 |
| nightmare_chitin | 8 | 730 | 1400 | 0.9848 |
| magma_vein | 7 | 731 | 1406 | 1.0196 |
| moonlit_lotus | 8 | 883 | 1694 | 1.0400 |
| aether_conduit | 8 | 758 | 1456 | 0.9420 |

## Identidad visual (anime exagerado)

- **Seraph Wing (serafín)**: espada larga radiante perla (140→58mm), plumas-radiante ×2, **3 capas de alas-pluma por lado** (170/132/94mm escalonadas), halo elíptico flotante (0.170 z), corazón serafín, pomo orbe. Glow blanco-oro (1.0, 0.94, 0.68).
- **Nightmare Chitin (quitina)**: hoja segmentada con **sierra en el vientre** (saw alterno 0.018), iridiscencia verde-veneno, conductos de veneno ×2, 3 pares de barbas-pata en el lomo, guarda mandíbulas curvadas, saco de veneno, pomo aguijón con púa extra (hasta −0.600). Glow tóxico (0.55, 1.0, 0.30).
- **Magma Vein (magma)**: espada ancha de basalto (180→90mm) con **grietas de lava ardiente ×4** (2 por cara, onda 9t), biseladas, guarda losas de basalto + púa, corazón magma, pomo bomba volcánica. Glow naranja (1.0, 0.45, 0.12).
- **Moonlit Lotus (loto)**: hoja-pétalo con ondulación ×1.10·sin11t, **3 capas de pétalos por cara**, disco luna-llena (86mm) tras la guarda + anillo interior, 3 gotas de rocío astral, semilla de loto, pomo capullo. Glow luna-rosa (0.95, 0.88, 1.0).
- **Aether Conduit (éter)**: estoque ultra-esbelto (88→30mm, alcance 4.18 la mayor del lote), canales de maná ×2 de punta a punta, **3 anillos-conducto** alrededor de la hoja, guarda vórtice con 2 brazos, canal de maná, pomo vial. Glow cian-violeta (0.45, 0.85, 1.0).

## PBR / Renders / Motor

- Atlas 5 regiones, painters seeds 623–679 en `generate_stage07_pbr_maps.py`; 5 PNGs 1024² por dir.
- 30 renders neutros Cycles (6 vistas × 5) en `art_pipeline/stage07_swords/{dir}/renders/`; QA visual view_04 ×5 OK.
- Verificación Godot 4.4 Vulkan/Xvfb (`/tmp/verify_stage07.gd`): seraph **8**, chitin **8**, magma **7**, lotus **8**, aether **8** mesh_instances — todas iguales a las piezas del build → GLB íntegro. Capturas `view_engine_verified_34.png` en cada dir.

## Cableado catálogo

`STAGE07_GLB` + cadenas extendidas en ambas rutas del generador → `verified_stage07_glb`/`canon_approved_stage07`. JSON regenerado (118 forms). Tests: **752/752**.
Nota de corrección: un paréntesis extra en el edit del bucle 5–24 rompió el generador; detectado por `ast.parse` en la misma tanda y corregido antes del commit.

## Estado del catálogo 3D tras Etapa 07

**28/118** formas con GLB bespoke verificado: pilot (1) + stage02 (3) + stage03 (4) + stage04 (5) + stage05 (5) + stage06 (5) + stage07 (5). Resto `extensible_blueprint_pending_3d`.
Hoja catálogo: `sword_catalog_sheet.png` (4112×3680, grid 7×5, 35 cards).

## Artefactos fuente

- `art_pipeline/stage07_swords/generate_stage07_pbr_maps.py` / `build_stage07_swords.py` / `render_stage07_swords.py`
- `art_pipeline/stage07_swords/{dir}/` — `.blend` editable + engine shot

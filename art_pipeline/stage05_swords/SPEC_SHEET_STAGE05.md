# SPEC SHEET — Stage 05 "Affinity" Batch (5 GLBs, Studio Lexair)

Proyecto: Espada Anime Isekai · Rama `feature/godot-complete-reconstruction`
Pipeline: Blender 4.3.2 (geometría única → UVs atlas → 5 mapas PBR 1024² → `.blend`) → renders neutros Cycles → GLB → verificación Godot 4.4 (Vulkan/Xvfb) → cableado catálogo.
Estilo: anime exagerado por linaje. NO meshes procedurales runtime, NO recolores.
Primera etapa de la **Era II — Afinidad**: las 5 líneas persistentes con formas propias de afinidad.

## Formas cubiertas (stage 05)

| # | Form ID | Nombre | Linaje / Parents | GLB | Dir |
|---|---------|--------|------------------|-----|-----|
| 1 | `blessed_solar_initiate_blade` | Espada Iniciada del Sol Naciente | blessed ← sunbark+fulgurite+jade | `sword_05_solar_initiate.glb` | `solar_initiate/` |
| 2 | `cursed_obsidian_fang_blade` | Espada Colmillo de Obsidiana | cursed ← thornheart+fulgurite | `sword_05_obsidian_fang.glb` | `obsidian_fang/` |
| 3 | `elemental_tempest_copper_blade` | Espada Cobriza de Tempestad | elemental ← sunbark+thornheart+fulgurite+runebark | `sword_05_copper_tempest.glb` | `copper_tempest/` |
| 4 | `spiritual_silver_anima_saber` | Sable de Plata Ánima | spiritual ← sunbark+jade+runebark | `sword_05_silver_anima.glb` | `silver_anima/` |
| 5 | `arcane_crystal_cipher_sword` | Espada Cifrada de Cristal | arcane ← thornheart+jade+runebark | `sword_05_crystal_cipher.glb` | `crystal_cipher/` |

## Resultados de build (Blender, escala normalizada h≈2.60, pivote en empuñadura)

| Espada | Piezas | Vértices | Tris | Escala |
|--------|--------|----------|------|--------|
| solar_initiate | 7 | 743 | 1414 | 0.9905 |
| obsidian_fang | 8 | 730 | 1400 | 1.0097 |
| copper_tempest | 8 | 826 | 1592 | 0.9886 |
| silver_anima | 8 | 753 | 1446 | 1.0136 |
| crystal_cipher | 8 | 954 | 1840 | 1.0097 |

## Identidad visual (anime exagerado)

- **Solar Initiate (estoque solar)**: hoja 14-vert elegante afinada (135→45mm), líneas-prick solares ×2, guarda corona-sol (anillo + 8 puntas rayo alternadas ±8mm), semilla solar, pomo corona. Glow oro (1.0, 0.86, 0.34).
- **Obsidian Fang (colmillo de vidrio)**: hoja 12-vert curva con panza profunda (off −0.075·t^1.7, grosor alterno ×1.12), vetas sangre ×2 pegadas al filo, 4 astillas de vidrio en el lomo, guarda mandíbula con 2 colmillos verticales (0.095→0.380 z), corazón del vacío, pomo garra squash 1.18. Glow rosa (0.98, 0.20, 0.28).
- **Copper Tempest (ciclón de cobre)**: hoja 12-vert con **twist ciclónico t×2.4 rad** + ondulación de ancho ×1.06·sin14t, surcos-ciclón emisivos siguiendo la torsión, 3 cintas de patina verdín en espiral, guarda remolino con 2 ganchos, núcleo ojo-del-ciclón, empuñadura alambre cobre (thick_every=1), pomo bobina vórtice. Glow eléctrico (0.85, 0.97, 1.0).
- **Silver Anima (sable de caballería)**: hoja 12-vert curva ancha (88→50mm, off −0.065·t^1.6), líneas-wisp menta ×2, guarda con arco de guardamano completo (0.078→−0.40 z) + disco achatado, **2 borlas de seda fantasmal** con gota emisiva, llama ánima plateada, pomo lágrima. Glow menta (0.55, 1.0, 0.82).
- **Crystal Cipher (prisma cifrado)**: hoja 12-vert prismática con biseles fuertes alternos, glifos-anillo ×2, **3 collares faceta** (z 0.72/1.12/1.52), 2 anillos orbitales inclinados ±30° + 3 piedras orbitales emisivas, núcleo prisma, pomo matriz-cubo squash 1.25. Glow magenta (0.95, 0.55, 1.0).

## PBR / Renders / Motor

- Atlas 5 regiones, painters seeds 521–569 en `generate_stage05_pbr_maps.py`; 5 PNGs 1024² por dir.
- 30 renders neutros Cycles (6 vistas × 5) en `art_pipeline/stage05_swords/{dir}/renders/`; QA visual view_04 ×5 OK.
- Verificación Godot 4.4 Vulkan/Xvfb (`/tmp/verify_stage05.gd`): solarinit **7**, obsidianfang **8**, coppertempest **8**, silveranima **8**, crystalcipher **8** mesh_instances — todas iguales a las piezas del build → GLB íntegro. Capturas `view_engine_verified_34.png` en cada dir.

## Cableado catálogo (nota técnica)

El bucle `for st in range(5, 25)` del generador hardcodeaba `pending_3d`; generalizado para consultar `STAGE05_GLB`→`STAGE04_GLB`→`STAGE03_GLB`→`STAGE02_GLB` (patrón reutilizable para etapas 06+ añadiendo un dict). Resultado: las 5 formas stage-5 con `verified_stage05_glb`/`canon_approved_stage05`. JSON regenerado (118 forms). Tests: **752/752**.

## Estado del catálogo 3D tras Etapa 05

**18/118** formas con GLB bespoke verificado: pilot (1) + stage02 (3) + stage03 (4) + stage04 (5) + stage05 (5). Resto `extensible_blueprint_pending_3d`.
Hoja catálogo: `sword_catalog_sheet.png` (2944×3680, grid 5×5, 25 cards).

## Artefactos fuente

- `art_pipeline/stage05_swords/generate_stage05_pbr_maps.py` / `build_stage05_swords.py` / `render_stage05_swords.py`
- `art_pipeline/stage05_swords/{dir}/` — `.blend` editable + engine shot

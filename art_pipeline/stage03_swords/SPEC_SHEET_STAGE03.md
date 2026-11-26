# SPEC SHEET — Stage 03 "Awakening" Batch (4 GLBs, Studio Lexair)

Proyecto: Espada Anime Isekai · Rama `feature/godot-complete-reconstruction`
Pipeline: Blender 4.3.2 (geometría única → UVs atlas → 5 mapas PBR 1024² → `.blend`) → renders neutros Cycles → GLB → verificación Godot 4.4 (Vulkan/Xvfb) → cableado catálogo.
Estilo: anime exagerado por linaje. NO meshes procedurales runtime, NO recolores.

## Formas cubiertas (stage 03, nivel 6)

| # | Form ID | Nombre | Linaje / Arquetipo | GLB | Dir |
|---|---------|--------|--------------------|-----|-----|
| 1 | `awakening_amber_sanctuary_blade` | Hoja de Ámbar de Santuario | blessed / heavy | `sword_03_amber_sanctuary.glb` | `godot_project/assets/models/swords/amber_sanctuary/` |
| 2 | `awakening_ironwood_storm_edge` | Filo de Palo Férreo y Trueno | elemental / balanced | `sword_03_ironwood_storm.glb` | `godot_project/assets/models/swords/ironwood_storm/` |
| 3 | `awakening_spirit_willow_saber` | Sable de Sauce Espiritual | spiritual / swift | `sword_03_spirit_willow.glb` | `godot_project/assets/models/swords/spirit_willow/` |
| 4 | `awakening_bloodsap_bramble_blade` | Hoja de Zarza Sanguina | cursed / swift | `sword_03_bramble_blade.glb` | `godot_project/assets/models/swords/bloodsap_bramble/` |

## Resultados de build (Blender, escala normalizada h≈2.60, pivote en empuñadura)

| Espada | Piezas | Vértices | Tris | Escala aplicada |
|--------|--------|----------|------|-----------------|
| amber_sanctuary | 8 | 939 | 1814 | 0.9756 |
| ironwood_storm | 7 | 786 | 1444 | 0.9756 |
| spirit_willow | 8 | 881 | 1706 | 0.9848 |
| bloodsap_bramble | 8 | 980 | 1896 | 0.9756 |

Nota ironwood: los 3 collares de hierro van integrados como bandas en la propia losa (no piezas separadas) — por eso 7 parts en vez de 10.

## Identidad visual por espada (anime exagerado)

- **Amber Sanctuary (claymore catedral)**: hoja 14-vert con vitrales de resina ámbar emisiva (Strength 2.2), halo-sanctuario flotante con 4 pétalos, guardas en alas doradas, pomo orbe con anillo. Glow resina (1.0, 0.78, 0.32).
- **Ironwood Storm (losa cleaver)**: losa 14-vert de palo férreo con 3 collares de acero pavonado, costuras de rayo emisivas cian (0.45, 0.80, 1.0), quillones en Z, pomo yunque hexagonal, empuñadura con vendas gruesas.
- **Spirit Willow (sable creciente)**: hoja 12-vert con lomo curvo y frondas caídas ×4, guarda nudo de sauce, costura etérea doble, farol espiritual en el core, pomo campana. Glow luna-cian (0.55, 0.92, 1.0).
- **Bloodsap Bramble (rapier retorcida)**: hoja 12-vert con twist por estación (t×1.15), 5 espinas bebedoras, guarda zarza de 2 lazos, goteos de savia ×2, corazón sangrante en el core, pomo brotaespina. Glow carmesí (1.0, 0.12, 0.10).

## PBR (atlas 5 regiones: blade TL, flair TR, grip BL, shell BM, glow BR)

Cada dir contiene 5 PNGs 1024²: `{tex}_basecolor.png`, `_roughness.png`, `_metallic.png`, `_normal.png`, `_emission.png`.
Painters con seeds 401–469 en `art_pipeline/stage03_swords/generate_stage03_pbr_maps.py`.
Material único Principled BSDF (Emission Strength 2.2) en GLB.

## Renders neutros (Cycles CPU, 48 spp, 800×1000, denoise OFF)

`art_pipeline/stage03_swords/{dir}/renders/` ×4 espadas ×6 vistas:
`view_01_front` / `view_02_side` / `view_03_back` / `view_04_three_quarters` / `view_05_detail_upper` / `view_06_silhouette`.
QA visual view_04 ×4: identidades correctas, siluetas claramente distintas, emisivos visibles.

## Verificación en motor (Godot 4.4.stable, Vulkan + Xvfb 800×1000)

Script frame-gated (`/tmp/verify_stage03.gd`, patrón Etapa 02), `ModelLoader.build_glb_scene_instance(path, 2.6, preserve_hilt_pivot=true)`:

| Espada | mesh_instances | Captura |
|--------|----------------|---------|
| amber | 8 | `amber_sanctuary/view_engine_verified_34.png` |
| ironwood | 7 | `ironwood_storm/view_engine_verified_34.png` |
| willow | 8 | `spirit_willow/view_engine_verified_34.png` |
| bramble | 8 | `bloodsap_bramble/view_engine_verified_34.png` |

mesh_instances == piezas del build en las 4 → GLB íntegro en motor.

## Cableado catálogo

`art_pipeline/generate_evolution_and_skills_data.py`: dict `STAGE03_GLB` + lógica `model_path`/`model_status` (`verified_stage03_glb`) / `catalog_status` (`canon_approved_stage03`), con fallback a STAGE02 → pilot → legacy OBJ.
Regenerado `godot_project/data/forms/evolution_catalog.json`: 118 forms; las 4 stage-3 con GLB propio; resto stage 3+ sigue `extensible_blueprint_pending_3d` (pending 3D, no inventado).
Tests: **752/752** tras regenerar.

## Artefactos fuente

- `art_pipeline/stage03_swords/generate_stage03_pbr_maps.py` — painters PBR ×4.
- `art_pipeline/stage03_swords/build_stage03_swords.py` — builders ×4 + helpers compartidos.
- `art_pipeline/stage03_swords/render_stage03_swords.py` — rig de renders (derivado de stage02).
- `art_pipeline/stage03_swords/{dir}/` — `.blend` editable + copia del engine shot.
- Parentado catálogo: amber ← verdant+copper; ironwood ← verdant+copper+ash; willow ← verdant+ash; bramble ← copper+ash (stats lvl6 xp117, mats {slime_gel:3}).

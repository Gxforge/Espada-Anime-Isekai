# Ficha Técnica — Etapa 02: Tres Ramas Bespoke (Lote Aprobado)

**Proyecto:** Espada Anime Isekai / Forja de Almas 3D — Directiva Studio Lexair
**Lote:** Etapa 02 del Árbol de Evolución Permanente (3 ramas permanentes desde la Etapa 01)
**Dirección de arte confirmada por el usuario:** anime exagerado por linaje (orgánico denso / eléctrico / brasas malditas)
**Regla cumplida:** cada espada tiene geometría única modelada a mano (nada de clones recoloreados ni meshes procedurales), UVs limpias en atlas de 5 regiones, 5 mapas PBR 1024×1024, `.blend` editable, renders neutros y verificación GLB en Godot 4.4.

---

## A. `sword_02_verdant_bough.glb` — "Hoja de Brote Viviente"

| Campo | Valor |
|---|---|
| Form ID | `wood_verdant_living_bough` (Etapa 02 · Era I · linaje `origin`) |
| Piezas (8) | `Blade_LivingBough` (12-secc. orgánica con vena central torcida), `Leaves_CanopyClusters` (6 hojas en 2 abanicos), `Guard_CurlingRoots` (2 brazos espiral), `Grip_MossWrappedWood`, `Inlay_SapVeins` (2 tiras emisivas), `Core_BloomingBud` (lente emisiva + 2 pétalos), `Pommel_RootBulb`, `Ferrule_VeridianBronze` |
| Geometría | 1.129 verts / 1.986 tris |
| Escala | 2.60 m normalizados (escala 0.9856), pivote en la empuñadura (z=0) |
| Curvatura | Hoja de sable orgánica (offset sinusoidal del lomo) |
| Emisión | Vetas de savia verde-primavera (región `glow` del atlas) |
| Maps | `verdant_bough_{basecolor,roughness,metallic,normal,emission}.png` (1024²) |
| Fuente editable | `art_pipeline/stage02_swords/verdant_bough/sword_02_verdant_bough.blend` |
| Renders | `view_01_front … view_06_silhouette` (800×1000, Cycles CPU 48 spp, key/fill/rim neutra) |
| Verificación Godot | `godot_project/assets/models/swords/verdant_bough/view_engine_verified_34.png` — `wrapper=SwordGLB mesh_instances=8` (Vulkan Forward+ en vivo) |

## B. `sword_02_copper_root.glb` — "Espada de Raíz Cobriza"

| Campo | Valor |
|---|---|
| Form ID | `wood_mineral_copper_root` (Etapa 02 · Era I · linaje `elemental`) |
| Piezas (8) | `Blade_CopperFangSheath` (12-secc. hexagonal en diente, 3 collares de placas), `Core_PetrifiedRootCore` (núcleo petrificado visible en la ranura dorsal), `Guard_ForkedStagHorns` (4 astas bifurcadas), `Grip_CopperCoilWrap` (bobina alterna), `Inlay_VoltaicSeams` (2 zigzags + costura dorsal emisivos), `Sparks_AnodicFinials` (3 púas), `Pommel_GalvanicBulb` + anillo ecuatorial emisivo, `Ferrule_GalvanicCopper` |
| Geometría | 1.048 verts / 1.944 tris |
| Escala | 2.60 m normalizados (escala 0.9811), pivote en la empuñadura (z=0) |
| Emisión | Costuras voltaicas ámbar-eléctrico sobre cobre pulido con verdete en hendiduras |
| Maps | `copper_root_{basecolor,roughness,metallic,normal,emission}.png` (1024²) |
| Fuente editable | `art_pipeline/stage02_swords/copper_root/sword_02_copper_root.blend` |
| Renders | `view_01 … view_06` (idem estándar neutro) |
| Verificación Godot | `godot_project/assets/models/swords/copper_root/view_engine_verified_34.png` — `mesh_instances=8` |

## C. `sword_02_ash_thorn.glb` — "Espada de Espino Carbonizado"

| Campo | Valor |
|---|---|
| Form ID | `wood_charred_ash_thorn` (Etapa 02 · Era I · linaje `cursed`) |
| Piezas (8) | `Blade_CharredBlackwood` (12-secc. con sierra dorsal y torsión), `Thorns_BlackBriarSpikes` (4 espinas), `Guard_CursedThornCrown` (anillo octogonal + 6 púas), `Grip_AshCharcoalWrap`, `Core_SmolderingEmberHeart` (núcleo brasas), `Inlay_EmberFissures` (3 grietas emisivas), `Pommel_EmberSeed` + anillo brasas, `Ferrule_CursedAshIron` |
| Geometría | 1.039 verts / 1.994 tris |
| Escala | 2.60 m normalizados (escala 0.9867), pivote en la empuñadura (z=0) |
| Emisión | Grietas de brasas naranja-fuego sobre carbón negro (corazón de brasa) |
| Maps | `ash_thorn_{basecolor,roughness,metallic,normal,emission}.png` (1024²) |
| Fuente editable | `art_pipeline/stage02_swords/ash_thorn/sword_02_ash_thorn.blend` |
| Renders | `view_01 … view_06` (idem estándar neutro) |
| Verificación Godot | `godot_project/assets/models/swords/ash_thorn/view_engine_verified_34.png` — `mesh_instances=8` |

---

## Pipeline reproducible

```bash
# 1. Mapas PBR (atlas 5 regiones x 5 mapas por espada)
python3 art_pipeline/stage02_swords/generate_stage02_pbr_maps.py all

# 2. Modelado + UVs + .blend + GLB (una invocación por espada)
blender --background --python art_pipeline/stage02_swords/build_stage02_swords.py -- sword=verdant
blender --background --python art_pipeline/stage02_swords/build_stage02_swords.py -- sword=copper
blender --background --python art_pipeline/stage02_swords/build_stage02_swords.py -- sword=ash

# 3. Renders neutros de revision (6 vistas por espada)
blender --background --python art_pipeline/stage02_swords/render_stage02_swords.py -- sword=all

# 4. Import + verificacion en el motor (Xvfb + Vulkan)
godot --headless --import --path godot_project
```

## Integración en el juego

`evolution_catalog.json` (regenerado desde `generate_evolution_and_skills_data.py`): las 3 formas de la Etapa 02 apuntan ahora a sus GLB bespoke con `model_status: verified_stage02_glb` y `catalog_status: canon_approved_stage02`. Al cometer la evolución permanente correspondiente, `EvolutionManager.get_legacy_tier_view()` entrega el `model_path` del GLB y `ModelLoader.build_sword_visual()` muestra el modelo nuevo en el juego automáticamente.

## Estado del catálogo tras este lote

- 3 / 118 formas con GLB bespoke verificado (Pilot #01 + 2 ramas... más la 3ª = **4 formas bespoke**).
- 114 formas pendientes (`extensible_blueprint_pending_3d`) — ninguna inventada sin aprobación.

# SPEC SHEET — REMASTER PILOT — 5 espadas realistas (2048² + geometría densificada)

Remasterizado Studio Lexair aprobado por el usuario tras Etapa 14 (cap de etapas: NO más etapas nuevas).
Directrices: **siluetas anime intactas** + **materiales PBR con micro-detalle realista** + texturas **2048²** (4× píxeles).
Script painters: `art_pipeline/remaster/paint_remaster_2048.py` (regiones idénticas ×2 px: blade TL / flair TR / grip BL / shell BM / glow BR).

## Stack de realismo (todas las espadas)
- `vnoise()` ruido de valor multi-octava (grano de superficie), `streaks()` micro-rayas finas (arañazos/hairlines de pulido)
- `edge_wear()` desgaste del filo (metal desnudo brillante en bordes de corte), `hammer_pits()` celdillas de martillado (height)
- `damascus()` capas de forja (acero negro), `ao_from_height()` oclusión pintada (grietas/hendiduras se oscurecen)
- `normal_from_height()` normal 2048 suavizada (blur 2, strength 2) — sin ruido de alta frecuencia
- Builders: estaciones de hoja **densificadas ×2** (`densify_stations`) + segmentos de anillos subidos (10→15 … 29→45)

## Las 5 del piloto
| Espada | Etapa | Geometría | Cambios de material |
|---|---|---|---|
| `wood_ancestral` | 01 | 5509v/6264t (igual) | veta abedul multi-octava + 2 nudos anulares + corteza agrietada con musgo + bronce con pátina + runas + savia ámbar |
| `glacier_fang` | 06 | 1169v/2262t (+40%) | hielo saturado v3 (fracturas internas, carámbanos, hoarfrost, plata cepillada) — 2 retintados tras QA |
| `soul_devourer` | 10 | 1604v/3092t (+36%) | damasco sutil sobre acero negro + grietas de brasa AO + cuero con pespuntes + pozo de ánimas con volutas |
| `archangel_verdict` | 12 | 1378v/2640t (+23%) | perla-blanco luminosa v2 + filigrana dorada fina (arch_f ×0.16) + plumas con barbas reales — 1 retintado tras QA |
| `sunforge` | 14 | 1121v/2162t (+45%) | oro con celdillas martilladas + costillas de forja incandescentes + arañazos + crisol con chispas |

- Builds: `build_remaster_swords.py` (4 de stage14/06/10/12) + `build_remaster_pilot_sword.py` (pilot) — `.blend` en `art_pipeline/remaster/<dir>/`
- Renders: `render_remaster_swords.py` (6 vistas ×4) + pilot 6 vistas; QA view_04 aprobado ×5 (3 iteraciones en glacier, 2 en archangel)
- Engine: verificados en Godot 4.4 vía Xvfb → `view_engine_verified_34.png` actualizado ×5 (mesh 7/8/8/8/7 ✔)
- Comparativa: `art_pipeline/remaster/REMASTER_PILOT_SHEET.png` (antes 1024 / después 2048)
- Tests: expectativa pilot PBR actualizada a 2048 (`tests/run_tests.gd`) → **752/752** ✔

## Plan de despliegue (pendiente de aprobación del usuario)
Extender el mismo stack a las **65 espadas**: painters 2048 por familia + densificación de estaciones en builders de etapas 02-14
(pilot ya denso) + re-render + re-verify en motor + actualización de cards del catálogo + nueva hoja comparativa completa.

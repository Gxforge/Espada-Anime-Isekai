# Ficha Técnica Oficial — Piloto 3D #01: Espada de Madera Ancestral

**Proyecto:** Espada Anime Isekai (Godot 4.4)  
**Estándar Visual:** Studio Lexair — Referencia y Dirección de Producción 3D  
**Estado:** `APROBADO TÉCNICAMENTE / VERIFICADO EN BLENDER 4.3 Y GODOT 4.4 (VULKAN FORWARD+)`

---

## 1. Identificación de la Forma

| Campo | Valor |
|---|---|
| **ID Canónico Permanente** | `wood_origin_ancestral_blade` (alias legacy compatible: `wood`) |
| **Nombre Oficial** | Espada de Madera Ancestral |
| **Era / Etapa** | Era I: Despertar — Etapa 01 (Origen de la Espada Consciente) |
| **Rama** | Tronco de Origen (`origin`) |
| **Identidad Protagonista** | La espada consciente recién reencarnada en el corazón de un roble milenario sagrado; conserva su núcleo de alma vivo visible dentro del Ojo del Despertar. |

---

## 2. Arquitectura Geométrica Individual (7 Sub-Piezas Reales)

Modelo 3D esculpido y construido individualmente en **Blender 4.3.2** sin generación procedural en runtime ni reutilización de malla base:

| Sub-Objeto (Nodo glTF / Godot) | Rol Estructural y Silueta | Vértices | Triángulos | Canal UV |
|---|---|---:|---:|---|
| `Blade_SacredHeartwood` | Hoja asimétrica de duramen sagrado con **Ojo del Despertar** calado en el ricasso, acanaladura central (*fuller*) rebajada, vientre de hoja tipo lanza-hoja (`+X`) y dos muescas de corteza ancestral con espolón dorsal (`-X`). | 444 | 872 | `UVMap` |
| `Core_AwakeningSeed` | Cristal bipiramidal facetado de esencia vital suspendido en el espacio negativo del Ojo del Despertar. | 42 | 80 | `UVMap` |
| `Inlay_RunicVeins` | Circuito rúnico físico tallado en relieve con nodos romboidales en ambas caras (`+Y` / `-Y`) de la acanaladura. | 234 | 312 | `UVMap` |
| `Guard_LivingRoots` | Guarda asimétrica de 4 raíces vivas entrelazadas (ala ascendente de filo `+X`, espolón secundario trenzado, garra descendente dorsal `-X` y cuerno de corteza superior) más 2 zarcillos internos que sostienen la Semilla del Alma. | 1,092 | 2,160 | `UVMap` |
| `Ferrule_SanctuaryBronze` | Tres abrazaderas octogonales martilladas en bronce de santuario: collar *habaki* inferior de guarda, corona superior del Ojo y virola inferior de pomo. | 126 | 240 | `UVMap` |
| `Grip_BraidedVine` | Empuñadura oval ergonómica con engrosamiento palmar (*palm-swell*) y 7 bandas físicas cruzadas en relieve real de cuero y liana trenzada. | 690 | 1,320 | `UVMap` |
| `Pommel_RootClaw` | Pomo de 4 garras de raíz viva que engarzan una gema facetada de savia espiritual ámbar. | 650 | 1,280 | `UVMap` |
| **TOTAL VERIFICADO** | **7 mallas diferenciadas (`MeshInstance3D` en Godot 4.4)** | **3,278** | **6,264** | **100% UV** |

---

## 3. Escala, Pivote y Orientación Estándar

- **Altura total del modelo:** `2.60 m` exactos en unidades de motor (`y = -0.58 m` extremo inferior del pomo a `y = +2.02 m` punta de la hoja en espacio glTF/Godot `+Y`).
- **Pivote `(0, 0, 0)`:** Situado exactamente en la unión entre el collar *habaki* superior de la empuñadura y la base de la guarda de raíces vivas, garantizando rotación natural tanto en modo **Espada Viviente Levitante** (`living_sword`) como en mano del **Portador Caballero** (`knight_wielder`).
- **Orientación de hoja:** Eje longitudinal `+Y` arriba (exportado desde Blender `+Z` con `export_yup=True`), filo principal hacia `+X`, lomo de corteza hacia `-X`, caras planas en `±Y`.

---

## 4. Mapas PBR (`1024 × 1024 px`, Atlas Unificado No Solapado)

Ubicación en motor: `godot_project/assets/models/swords/wood_ancestral/`

1. **`wood_ancestral_basecolor.png` (`sRGB`, `1024×1024`)**: Vetas longitudinales de roble milenario cálido, corteza oscura fisurada, cuero trenzado, bronce martillado con pátina verdete en recovecos, cristal esmeralda-cian y ámbar dorado.
2. **`wood_ancestral_roughness.png` (`Non-Color`, `1024×1024`)**: Contraste táctil real entre corteza mate (`0.84–0.92`), madera satinada tallada (`0.56–0.70`), cuero engrasado (`0.72–0.82`), bronce bruñido (`0.28–0.38`) y gemas pulidas (`0.10–0.16`).
3. **`wood_ancestral_metallic.png` (`Non-Color`, `1024×1024`)**: Dieléctrico puro (`0.0`) en maderas, raíces, cuero y cristales; metálico calibrado (`0.82–0.90`) exclusivamente en las abrazaderas de bronce de santuario.
4. **`wood_ancestral_normal.png` (`Non-Color` OpenGL Tangent-Space, `1024×1024`)**: Micro-relieve de fibras de duramen, surcos profundos de corteza, trenzado de fibras en correas y martillado artesanal del bronce.
5. **`wood_ancestral_emission.png` (`sRGB`, `1024×1024`)**: Luminiscencia contenida exclusivamente en la Semilla del Despertar, las venas rúnicas talladas y el corazón ámbar del pomo; el arma mantiene lectura completa con emisión `0.0` bajo luz neutra.

---

## 5. Archivos Entregables y Renders de Validación

- **Fuente editable Blender 4.3:** `art_pipeline/pilot_01_wood_ancestral/sword_01_wood_ancestral.blend`
- **Scripts reproducibles de pipeline:**
  - `art_pipeline/pilot_01_wood_ancestral/generate_pbr_maps.py`
  - `art_pipeline/pilot_01_wood_ancestral/build_pilot_sword_blender.py`
  - `art_pipeline/pilot_01_wood_ancestral/build_presentation_sheet.py`
- **Exportación runtime Godot 4.4 (`glTF 2.0 Binary`):** `godot_project/assets/models/swords/wood_ancestral/sword_01_wood_ancestral.glb`
- **Renders de revisión bajo luz neutra de estudio (sin bloom ni partículas):**
  1. `renders/view_01_front_neutral.png` — Vista frontal completa
  2. `renders/view_02_side_neutral.png` — Perfil lateral completo
  3. `renders/view_03_back_neutral.png` — Vista trasera completa
  4. `renders/view_04_three_quarter_neutral.png` — Vista heroica 3/4
  5. `renders/view_05a_closeup_hilt_core.png` — Primer plano de guarda de raíces, collar de bronce y Semilla del Despertar
  6. `renders/view_05b_closeup_blade_runes.png` — Primer plano de biseles de madera, muesca dorsal y runas físicas
  7. `renders/view_06_silhouette_check.png` — Prueba de silueta negra pura sobre fondo neutro claro
  8. `renders/view_07_presentation_sheet.png` — Lámina técnica consolidada Studio Lexair (`1920×1080`)
  9. `renders/view_08_godot44_engine_verified.png` — Captura verificada en tiempo real dentro de **Godot 4.4 (`Vulkan Forward+`)** mediante `ModelLoader.build_sword_visual()` (`wrapper = SwordGLB`, `mesh_instances = 7`).

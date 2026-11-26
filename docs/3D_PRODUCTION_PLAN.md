# Plan Maestro de Producción 3D de Espadas — Studio Lexair

**Proyecto:** Espada Anime Isekai (Godot 4.4)  
**Directiva de Referencia:** *Studio Lexair — Espada Anime Isekai: Referencia Visual y Directiva de Producción 3D*  
**Piloto Base Verificado:** `#01 Espada de Madera Ancestral` (`wood_origin_ancestral_blade`)

---

## 1. Principios Innegociables de Diseño y Modelado

1. **Protagonismo Absoluto de la Espada Consciente:** El jugador encarna una espada consciente reencarnada. Cada evolución representa una transformación física, espiritual y narrativa real del protagonista; jamás un simple cambio estadístico o cosmético.
2. **Prohibición Total de Generación Procedural de Mallas y Recoloreados:**
   - Queda prohibido generar espadas mediante primitivas procedurales como sustituto del arte final.
   - Queda prohibido duplicar una malla base cambiándole únicamente el color, el brillo o añadiendo accesorios menores.
   - Dos formas alternativas de una misma etapa (p. ej. rama `Bendita` vs `Maldita` vs `Elemental`) deben distinguirse al instante incluso en **silueta negra pura** (`view_06_silhouette_check.png`).
3. **Legibilidad bajo Luz Neutra sin Postprocesado:** Todo modelo debe aprobar revisión visual con iluminación de estudio de 3 puntos neutra, sin depender de *glow*, *bloom*, niebla ni partículas para ocultar carencias de geometría o textura.

---

## 2. Anatomía Obligatoria por Espada (Mínimo 5 a 9 Sub-Piezas)

Cada archivo `.blend` y `.glb` debe separar explícitamente sus componentes estructurales:

1. **`Blade_*` (Hoja principal):** Silueta propia, biseles definidos, sección transversal creíble (diamante, hexagonal, acanalada, asimétrica, segmentada o calada según la forma) y grosor real en filo y lomo.
2. **`Core_*` (Núcleo del Alma Consciente):** Gema, semilla, ojo abisal, corazón estelar o sello rúnico suspendido o engarzado que manifiesta la consciencia viva del protagonista.
3. **`Inlay_*` / `Fuller_*` (Acanaladura, grabados o venas energéticas):** Geometría física rebajada o en relieve a lo largo de la hoja.
4. **`Guard_*` (Guarda / Cruz):** Proporción, curvatura y lenguaje formal exclusivos de su linaje evolutivo.
5. **`Ferrule_*` / `Collar_*` (Virolas, *habaki* y engastes metálicos/minerales):** Transición mecánica creíble entre hoja, guarda y empuñadura.
6. **`Grip_*` (Empuñadura):** Sección oval ergonómica (nunca un cilindro liso genérico) con encordado, escamas, anillos o relieve físico.
7. **`Pommel_*` (Pomo / Contrapeso):** Cierre inferior distintivo que equilibra visualmente la silueta total.

---

## 3. Contrato Técnico Blender -> glTF 2.0 (`.glb`) -> Godot 4.4

| Parámetro | Especificación Estándar |
|---|---|
| **Herramienta Fuente** | Blender 4.3+ (`.blend` editable conservado en `art_pipeline/<form_slug>/`) |
| **Formato Runtime** | `glTF 2.0 Binary (.glb)` en `godot_project/assets/models/swords/<form_slug>/` |
| **Altura Total Normalizada** | `2.60 m` (`y = -0.58 m` pomo base a `y = +2.02 m` punta en eje `+Y` de Godot) |
| **Pivote `(0, 0, 0)`** | Centro del collar superior de empuñadura / base de la guarda |
| **Orientación** | Punta hacia `+Y` (Blender `+Z` con `export_yup=True`), filo principal `+X`, caras `±Y` |
| **Presupuesto Poligonal** | Era I–II: `4,500 – 7,500 tris` · Era III–IV: `7,500 – 12,000 tris` · Era V–VI: `10,000 – 16,000 tris` |
| **Mapas PBR Requeridos** | `BaseColor` (sRGB), `Roughness` (Non-Color), `Metallic` (Non-Color), `Normal` (Non-Color OpenGL), `Emission` (sRGB) |
| **Resolución de Texturas** | `1024 × 1024 px` estándar runtime (`2048 × 2048 px` permitido en formas trascendentes/supremas Era V–VI) |
| **Integración en Motor** | `ModelLoader.build_glb_scene_instance()` instancia `PackedScene` preservando los materiales PBR originales sin sobrescribir `material_override` |

---

## 4. Escalada Visual a través de las 6 Eras (24 Etapas)

| Era | Etapas | Lenguaje de Silueta y Materiales |Complejidad Estructural |
|---|---|---|---|
| **I. Despertar** | `01 – 04` | Maderas sagradas, cortezas vivas, raíces, bronce antiguo, minerales despiertos, cristales semilla. | Austera pero artesanal (`5–7` piezas, calado focal simple, runas incisas). |
| **II. Afinidad** | `05 – 08` | Divergencia clara de linaje: metales solares bruñidos (`Bendita`), quitina/obsidiana dentada (`Maldita`), fulgurita/escarcha/magma (`Elemental`), jade etéreo (`Espiritual`), astrolabios de platino (`Arcana`). | Guardas esculturales pronunciadas, hojas con asimetrías de facción (`6–8` piezas). |
| **III. Especialización** | `09 – 12` | Hojas compuestas, dobles filos escalonados, anillos flotantes anclados o canales de absorción abiertos. | Geometría secundaria articulada y núcleos expuestos multicapa. |
| **IV. Trascendencia** | `13 – 16` | Reliquias consagradas o profanas de escala heroica; metales imposibles, filigranas reales modeladas y fracturas contenidas. | Siluetas icónicas de alto rango con sub-elementos suspendidos. |
| **V. Dominio** | `17 – 20` | Soberanía elemental/cósmica: hojas coronadas, guardas aladas o mandibulares monumentales, núcleos múltiples sincronizados. | Alto detalle escultórico (`10k–14k tris`) legible tanto en cámara lejana como en catálogo. |
| **VI. Existencia Suprema** | `21 – 24` | Culminación ontológica de la espada consciente; proporciones divinas/abisales/estelares irrepetibles sin perder jamás la lectura inequívoca de espada protagonista. | Máxima artesanía (`12k–16k tris`), texturas de alta densidad y presencia de reliquia definitiva. |

---

## 5. Protocolo de Validación (QA Gate) por Cada Espada

Ninguna espada pasa al catálogo como `MODEL_VERIFIED` sin superar los 7 controles verificados en el Piloto #01:

1. **Revisión de Silueta Pura (`view_06_silhouette_check.png`):** Reconocible en negro sólido a `128 px` de alto sin confundirse con ninguna otra espada del catálogo.
2. **Turnaround en Luz Neutra (`view_01..04`):** Frontal, lateral, trasera y 3/4 sin *bloom* ni luces dramáticas coloreadas.
3. **Close-ups de Unión Mecánica (`view_05a`, `view_05b`):** Inspección de biseles, acanaladura, engaste del núcleo, unión hoja-guarda-empuñadura y encordado físico.
4. **Auditoría UV y PBR:** Cero estiramientos severos, veta coherente con la dirección estructural del material y separación limpia metal/dieléctrico/rugosidad.
5. **Fuente Editable Archivada:** `.blend` limpio con nombres de colección y sub-piezas semánticos.
6. **Verificación en Godot 4.4 (`view_08`):** Importación `.glb` limpia sin errores de consola y render verificado en motor.
7. **Ficha Técnica (`SPEC_SHEET.md`):** Conteo exacto de vértices, triángulos, mapas y rutas reales.

---

## 6. Estado Real del Catálogo 3D (Sin Métricas Inventadas)

| Lote | Formas Incluidas | Estado Actual |
|---|---|---|
| **Piloto Oficial #01** | `wood_origin_ancestral_blade` (*Espada de Madera Ancestral*, Etapa 01) | **COMPLETADO Y VERIFICADO EN BLENDER 4.3 + GODOT 4.4** (`6,264 tris`, 7 sub-piezas, 5 mapas PBR `1024px`, `.blend` + `.glb` + 8 renders de validación). |
| **Modelos Legacy de Transición** | 8 archivos `.obj` previos (`sword_wood_nv1.obj` .. `sword_celestial_nv35.obj`) | **CONSERVADOS INTACTOS EN DISCO** por compatibilidad regresiva y tests existentes; clasificados como *placeholders legacy sin UVs/PBR* pendientes de reemplazo individual lote a lote. |
| **Lotes Siguientes (Etapas 02–24 y Ramas)** | Ramas permanentes `Bendita`, `Maldita`, `Elemental`, `Espiritual`, `Arcana` e `Híbrida` | **ARQUITECTURA DATA-DRIVEN LISTA / MODELOS 3D INDIVIDUALES PENDIENTES DE APROBACIÓN POR LOTE** (cada entrada del catálogo declara explícitamente `model_status: "verified_pilot_glb"` vs `"legacy_placeholder_pending_3d"`). |

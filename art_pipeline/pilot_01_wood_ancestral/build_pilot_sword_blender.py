"""
Blender 4.3 Bespoke Modeling, UV Mapping, PBR Material Setup, GLB Export & Studio Turnaround Renderer
for Pilot Sword #01: s01_wood_ancestral — Espada de Madera Ancestral (Studio Lexair)

Run via:
  blender --background --python build_pilot_sword_blender.py
"""

import math
import os
import bpy
import bmesh
from mathutils import Vector, Matrix

REPO_ROOT = "/home/user/Espada-Anime-Isekai"
TEX_DIR = f"{REPO_ROOT}/godot_project/assets/models/swords/wood_ancestral"
GLB_PATH = f"{TEX_DIR}/sword_01_wood_ancestral.glb"
PIPE_DIR = f"{REPO_ROOT}/art_pipeline/pilot_01_wood_ancestral"
BLEND_PATH = f"{PIPE_DIR}/sword_01_wood_ancestral.blend"
RENDERS_DIR = f"{PIPE_DIR}/renders"
os.makedirs(RENDERS_DIR, exist_ok=True)

# 1. Reset factory scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

sword_col = bpy.data.collections.new("Sword_01_Wood_Ancestral")
scene.collection.children.link(sword_col)

sword_root = bpy.data.objects.new("Sword_01_Wood_Ancestral", None)
sword_col.objects.link(sword_root)


# --- UV ATLAS HELPERS ---
# Atlas regions in UV space (u in [0..1], v in [0..1] where v=1 is top of image):
# Wood Heartwood (top-left):     u=[0.03..0.47], v=[0.53..0.97]
# Bark (top-right):              u=[0.53..0.97], v=[0.53..0.97]
# Cord Wrap (bottom-left):       u=[0.03..0.47], v=[0.03..0.47]
# Bronze Ferrule (bottom-mid):   u=[0.52..0.73], v=[0.03..0.47]
# Emerald Crystal (bot-right 1): u=[0.77..0.97], v=[0.27..0.47]
# Amber Sap (bot-right 2):       u=[0.77..0.97], v=[0.03..0.23]
ATLAS = {
    "wood":    (0.03, 0.47, 0.53, 0.97),
    "bark":    (0.53, 0.97, 0.53, 0.97),
    "cord":    (0.03, 0.47, 0.03, 0.47),
    "bronze":  (0.52, 0.73, 0.03, 0.47),
    "emerald": (0.77, 0.97, 0.27, 0.47),
    "amber":   (0.77, 0.97, 0.03, 0.23),
}


def map_uv(u01: float, v01: float, region: str):
    u0, u1, v0, v1 = ATLAS[region]
    u = u0 + max(0.0, min(1.0, u01)) * (u1 - u0)
    v = v0 + max(0.0, min(1.0, v01)) * (v1 - v0)
    return (u, v)


# --- BUILD UNIFIED PBR MATERIAL ---
def create_pbr_material(enable_emission: bool = True) -> bpy.types.Material:
    mat = bpy.data.materials.new("M_Sword01_WoodAncestral_PBR")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (520, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (180, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    def tex_node(filename: str, non_color: bool, loc):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.location = loc
        img = bpy.data.images.load(f"{TEX_DIR}/{filename}", check_existing=True)
        img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
        n.image = img
        return n

    n_base = tex_node("wood_ancestral_basecolor.png", False, (-420, 280))
    n_metal = tex_node("wood_ancestral_metallic.png", True, (-420, 40))
    n_rough = tex_node("wood_ancestral_roughness.png", True, (-420, -180))
    n_norm_tex = tex_node("wood_ancestral_normal.png", True, (-420, -420))
    n_emis = tex_node("wood_ancestral_emission.png", False, (-420, -660))

    n_norm = nt.nodes.new("ShaderNodeNormalMap")
    n_norm.location = (-120, -420)
    n_norm.inputs["Strength"].default_value = 0.85

    nt.links.new(n_base.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(n_metal.outputs["Color"], bsdf.inputs["Metallic"])
    nt.links.new(n_rough.outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(n_norm_tex.outputs["Color"], n_norm.inputs["Color"])
    nt.links.new(n_norm.outputs["Normal"], bsdf.inputs["Normal"])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(n_emis.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.15 if enable_emission else 0.0
    elif "Emission" in bsdf.inputs:
        nt.links.new(n_emis.outputs["Color"], bsdf.inputs["Emission"])

    return mat


pbr_mat = create_pbr_material(enable_emission=True)


def finalize_mesh_obj(name: str, bm: bmesh.types.BMesh, smooth_angle_deg: float = 42.0) -> bpy.types.Object:
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = smooth_angle_deg > 0.0

    mesh.materials.append(pbr_mat)
    obj = bpy.data.objects.new(name, mesh)
    obj.parent = sword_root
    sword_col.objects.link(obj)
    return obj


# --- HELPER: LOFT RING SECTIONS WITH CLEAN UVs ---
def add_lofted_tube(bm: bmesh.types.BMesh, uv_layer, rings_pts, rings_v, region: str, cap_start=True, cap_end=True):
    """rings_pts: list of lists of Vector (all same vertex count K around loop)."""
    K = len(rings_pts[0])
    vert_rings = []
    for r_pts in rings_pts:
        vert_rings.append([bm.verts.new(p) for p in r_pts])

    for i in range(len(vert_rings) - 1):
        r0 = vert_rings[i]
        r1 = vert_rings[i + 1]
        v0 = rings_v[i]
        v1 = rings_v[i + 1]
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([r0[j], r0[jn], r1[jn], r1[j]])
            u0 = j / K
            u1 = (j + 1) / K
            f.loops[0][uv_layer].uv = map_uv(u0, v0, region)
            f.loops[1][uv_layer].uv = map_uv(u1, v0, region)
            f.loops[2][uv_layer].uv = map_uv(u1, v1, region)
            f.loops[3][uv_layer].uv = map_uv(u0, v1, region)

    if cap_start:
        c0 = sum(rings_pts[0], Vector()) / K
        vc0 = bm.verts.new(c0)
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([vert_rings[0][jn], vert_rings[0][j], vc0])
            f.loops[0][uv_layer].uv = map_uv((j + 1) / K, rings_v[0], region)
            f.loops[1][uv_layer].uv = map_uv(j / K, rings_v[0], region)
            f.loops[2][uv_layer].uv = map_uv(0.5, rings_v[0], region)

    if cap_end:
        c1 = sum(rings_pts[-1], Vector()) / K
        vc1 = bm.verts.new(c1)
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([vert_rings[-1][j], vert_rings[-1][jn], vc1])
            f.loops[0][uv_layer].uv = map_uv(j / K, rings_v[-1], region)
            f.loops[1][uv_layer].uv = map_uv((j + 1) / K, rings_v[-1], region)
            f.loops[2][uv_layer].uv = map_uv(0.5, rings_v[-1], region)


def apply_timber_planar_uvs(bm: bmesh.types.BMesh, uv_layer, x_min: float, x_max: float, z_min: float, z_max: float, region_main: str = "wood", spine_bark_cutoff: float = -0.105):
    """Projects UVs from world (X, Z) so carved bevels & notches slice naturally across continuous vertical wood grain."""
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        cx = sum(v.co.x for v in f.verts) / len(f.verts)
        reg = "bark" if cx < spine_bark_cutoff else region_main
        # Offset -Y face slightly in U so front and back faces don't look mirror-identical
        n_y = f.normal.y
        u_shift = 0.0 if n_y >= 0.0 else 0.23
        for loop in f.loops:
            co = loop.vert.co
            u01 = ((co.x - x_min) / max(0.001, (x_max - x_min))) * 0.72 + u_shift
            v01 = (co.z - z_min) / max(0.001, (z_max - z_min))
            loop[uv_layer].uv = map_uv(u01 % 1.0, v01, reg)



def frame_along_curve(pts):
    frames = []
    up_ref = Vector((0, 1, 0))
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        if abs(t.dot(up_ref)) > 0.92:
            up_ref = Vector((1, 0, 0))
        n = t.cross(up_ref).normalized()
        b = n.cross(t).normalized()
        frames.append((p, n, b, t))
    return frames


def sample_cubic_bezier(p0, p1, p2, p3, steps: int):
    out = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1.0 - t
        p = (mt**3) * p0 + 3 * (mt**2) * t * p1 + 3 * mt * (t**2) * p2 + (t**3) * p3
        out.append(p)
    return out


# ==============================================================================
# PART 1: BLADE_SACREDHEARTWOOD (Split-Eye Ricasso + Asymmetric Leaf-Swell Blade)
# ==============================================================================
bm_blade = bmesh.new()
uv_blade = bm_blade.loops.layers.uv.new("UVMap")


def blade_main_section(z: float, x_spine: float, x_edge: float, half_t: float, fuller_depth: float):
    """
    10-vertex crisp sword cross-section around perimeter (CCW looking from +Z):
    - Spine back (-X) has beveled bark flat
    - Recessed central fuller on +Y and -Y faces
    - Proud bevel ridge before razor cutting edge (+X)
    """
    w = x_edge - x_spine
    x_sp_bevel = x_spine + 0.14 * w
    x_full_l = x_spine + 0.28 * w
    x_full_r = x_spine + 0.56 * w
    x_ed_bevel = x_spine + 0.74 * w

    y_sp = half_t * 0.52
    y_ridge = half_t
    y_full = max(0.004, half_t - fuller_depth)
    y_edge = 0.0022

    return [
        Vector((x_edge,     +y_edge,  z)),  # 0: cutting edge +Y
        Vector((x_ed_bevel, +y_ridge, z)),  # 1: front bevel ridge +Y
        Vector((x_full_r,   +y_full,  z)),  # 2: fuller outer +Y
        Vector((x_full_l,   +y_full,  z)),  # 3: fuller inner +Y
        Vector((x_sp_bevel, +y_ridge * 0.92, z)),  # 4: spine ridge +Y
        Vector((x_spine,    +y_sp,    z)),  # 5: spine back +Y
        Vector((x_spine,    -y_sp,    z)),  # 6: spine back -Y
        Vector((x_sp_bevel, -y_ridge * 0.92, z)),  # 7: spine ridge -Y
        Vector((x_full_l,   -y_full,  z)),  # 8: fuller inner -Y
        Vector((x_full_r,   -y_full,  z)),  # 9: fuller outer -Y
        Vector((x_ed_bevel, -y_ridge, z)),  # 10: front bevel ridge -Y
        Vector((x_edge,     -y_edge,  z)),  # 11: cutting edge -Y
    ]


# 1A. Ricasso base block (z = 0.055 .. 0.175) tapering smoothly into the Split-Eye limbs
ricasso_stations = [
    (0.055, -0.102, +0.106, 0.036, 0.004),
    (0.115, -0.125, +0.130, 0.036, 0.006),
    (0.175, -0.132, +0.136, 0.034, 0.008),
]
add_lofted_tube(
    bm_blade, uv_blade,
    [blade_main_section(*st) for st in ricasso_stations],
    [0.02, 0.06, 0.10],
    "wood", cap_start=True, cap_end=True
)

# 1B. Two curved limbs framing the open Tear-Drop "Eye of Awakening" (z = 0.155 .. 0.545)
# Outer boundaries match ricasso (z=0.175) and upper blade (z=0.525) so there is zero horizontal step!
cut_limb_rings = []
cut_limb_v = []
for i in range(13):
    t = i / 12.0
    z = 0.155 + t * (0.545 - 0.155)
    arch = math.sin(t * math.pi)
    x_outer = 0.134 + 0.038 * arch
    x_inner = 0.024 + 0.068 * (arch ** 0.78)
    cx = 0.5 * (x_outer + x_inner)
    hw = 0.5 * (x_outer - x_inner)
    ht = 0.033 - 0.003 * arch
    cut_limb_rings.append([
        Vector((x_outer,        +0.003, z)),
        Vector((cx + hw * 0.35, +ht,    z)),
        Vector((cx - hw * 0.55, +ht * 0.82, z)),
        Vector((x_inner,        +0.008, z)),
        Vector((x_inner,        -0.008, z)),
        Vector((cx - hw * 0.55, -ht * 0.82, z)),
        Vector((cx + hw * 0.35, -ht,    z)),
        Vector((x_outer,        -0.003, z)),
    ])
    cut_limb_v.append(0.10 + t * 0.18)
add_lofted_tube(bm_blade, uv_blade, cut_limb_rings, cut_limb_v, "wood", cap_start=True, cap_end=True)

# Spine-side (-X) gnarled bark limb arching around the crystal eye
sp_limb_rings = []
sp_limb_v = []
for i in range(13):
    t = i / 12.0
    z = 0.155 + t * (0.545 - 0.155)
    arch = math.sin(t * math.pi)
    x_outer = -0.130 - 0.036 * arch
    x_inner = -0.024 - 0.064 * (arch ** 0.78)
    cx = 0.5 * (x_outer + x_inner)
    hw = 0.5 * (x_inner - x_outer)
    ht = 0.034 - 0.003 * arch
    sp_limb_rings.append([
        Vector((x_inner,        +0.008, z)),
        Vector((cx + hw * 0.45, +ht * 0.85, z)),
        Vector((cx - hw * 0.45, +ht,    z)),
        Vector((x_outer,        +0.014, z)),
        Vector((x_outer,        -0.014, z)),
        Vector((cx - hw * 0.45, -ht,    z)),
        Vector((cx + hw * 0.45, -ht * 0.85, z)),
        Vector((x_inner,        -0.008, z)),
    ])
    sp_limb_v.append(0.10 + t * 0.18)
add_lofted_tube(bm_blade, uv_blade, sp_limb_rings, sp_limb_v, "bark", cap_start=True, cap_end=True)

# 1C. Upper Sacred Heartwood Blade (z = 0.525 .. 2.02m) with asymmetric leaf-swell & 2 spine notches!
# Each tuple: (z, x_spine, x_edge, half_thickness, fuller_depth)
upper_blade_stations = [
    (0.525, -0.130, +0.136, 0.034, 0.013),
    (0.62,  -0.122, +0.138, 0.034, 0.016),
    (0.76,  -0.128, +0.144, 0.033, 0.016),
    (0.89,  -0.136, +0.150, 0.032, 0.015),
    (0.93,  -0.092, +0.153, 0.031, 0.014),  # Spine scar notch #1 (dramatic silhouette step!)
    (0.98,  -0.164, +0.157, 0.032, 0.015),  # Spine bark barb #1!
    (1.12,  -0.134, +0.165, 0.031, 0.015),
    (1.28,  -0.126, +0.174, 0.030, 0.014),
    (1.42,  -0.122, +0.182, 0.029, 0.013),  # Asymmetric Leaf-Swell maximum width!
    (1.47,  -0.084, +0.178, 0.028, 0.011),  # Spine scar notch #2!
    (1.52,  -0.132, +0.173, 0.027, 0.011),  # Upper spine spur!
    (1.66,  -0.104, +0.154, 0.024, 0.008),
    (1.80,  -0.068, +0.118, 0.020, 0.004),
    (1.91,  -0.028, +0.072, 0.014, 0.001),
    (1.98,  +0.002, +0.036, 0.008, 0.000),
    (2.02,  +0.018, +0.021, 0.002, 0.000),  # Razor asymmetric spear-leaf tip!
]
ub_rings = [blade_main_section(*st) for st in upper_blade_stations]
ub_v = [0.26 + 0.72 * ((st[0] - 0.525) / (2.02 - 0.525)) for st in upper_blade_stations]
add_lofted_tube(bm_blade, uv_blade, ub_rings, ub_v, "wood", cap_start=True, cap_end=True)

# Re-project continuous vertical timber UVs across the blade so notches slice across real vertical wood fibers!
apply_timber_planar_uvs(bm_blade, uv_blade, -0.175, +0.190, 0.05, 2.03, region_main="wood", spine_bark_cutoff=-0.108)

finalize_mesh_obj("Blade_SacredHeartwood", bm_blade, smooth_angle_deg=0.0)  # Crisp faceted bevels!


# ==============================================================================
# PART 2: CORE_AWAKENINGSEED (Faceted Emerald-Cyan Bipyramid Crystal + Root Prongs)
# ==============================================================================
bm_core = bmesh.new()
uv_core = bm_core.loops.layers.uv.new("UVMap")

crys_stations = [
    (0.225, 0.003, 0.003),
    (0.265, 0.026, 0.022),
    (0.345, 0.044, 0.036),
    (0.425, 0.026, 0.022),
    (0.470, 0.003, 0.003),
]
crys_rings = []
for zc, rx, ry in crys_stations:
    ring = []
    for k in range(8):
        ang = k * (2 * math.pi / 8.0) + (math.pi / 8.0)
        mod = 1.0 if k % 2 == 0 else 0.82
        ring.append(Vector((math.cos(ang) * rx * mod, math.sin(ang) * ry * mod, zc)))
    crys_rings.append(ring)
add_lofted_tube(bm_core, uv_core, crys_rings, [0.05, 0.28, 0.52, 0.76, 0.96], "emerald", cap_start=True, cap_end=True)
finalize_mesh_obj("Core_AwakeningSeed", bm_core, smooth_angle_deg=0.0)


# ==============================================================================
# PART 3: INLAY_RUNICVEINS (Carved Ancestral Rune Glyphs along Both Fuller Faces)
# ==============================================================================
bm_runes = bmesh.new()
uv_runes = bm_runes.loops.layers.uv.new("UVMap")


def add_rune_bar(bm, uv_l, p_a: Vector, p_b: Vector, width: float, depth_y: float, sign_y: float):
    d = p_b - p_a
    perp = Vector((-d.z, 0.0, d.x)).normalized() * (width * 0.5)
    y_base = sign_y * (depth_y - 0.002)
    y_top = sign_y * (depth_y + 0.0035)
    pts_bot = [
        Vector((p_a.x - perp.x, y_base, p_a.z - perp.z)),
        Vector((p_a.x + perp.x, y_base, p_a.z + perp.z)),
        Vector((p_b.x + perp.x, y_base, p_b.z + perp.z)),
        Vector((p_b.x - perp.x, y_base, p_b.z - perp.z)),
    ]
    pts_top = [
        Vector((p_a.x - perp.x * 0.65, y_top, p_a.z - perp.z * 0.65)),
        Vector((p_a.x + perp.x * 0.65, y_top, p_a.z + perp.z * 0.65)),
        Vector((p_b.x + perp.x * 0.65, y_top, p_b.z + perp.z * 0.65)),
        Vector((p_b.x - perp.x * 0.65, y_top, p_b.z - perp.z * 0.65)),
    ]
    add_lofted_tube(bm, uv_l, [pts_bot, pts_top], [0.2, 0.8], "emerald", cap_start=False, cap_end=True)


# Ancestral World-Tree rune motif along fuller centerline (x ~ -0.015 .. +0.025)
rune_segments = [
    (Vector((-0.008, 0, 0.60)), Vector((+0.004, 0, 0.84)), 0.012, 0.018),
    (Vector((+0.004, 0, 0.72)), Vector((+0.032, 0, 0.79)), 0.010, 0.018),
    (Vector((+0.002, 0, 0.88)), Vector((-0.024, 0, 0.99)), 0.011, 0.017),
    (Vector((-0.024, 0, 0.99)), Vector((+0.022, 0, 1.12)), 0.011, 0.017),
    (Vector((+0.022, 0, 1.12)), Vector((-0.014, 0, 1.26)), 0.010, 0.016),
    (Vector((-0.014, 0, 1.26)), Vector((+0.018, 0, 1.42)), 0.010, 0.016),
    (Vector((+0.002, 0, 1.33)), Vector((+0.034, 0, 1.40)), 0.009, 0.016),
    (Vector((+0.018, 0, 1.46)), Vector((+0.012, 0, 1.64)), 0.009, 0.016),
]
for pa, pb, rw, dy in rune_segments:
    add_rune_bar(bm_runes, uv_runes, pa, pb, rw, dy, +1.0)
    add_rune_bar(bm_runes, uv_runes, pa, pb, rw, dy, -1.0)

# Faceted diamond rune-nodes sealing all vertex junctions cleanly
rune_nodes = [
    (Vector((+0.004, 0, 0.72)), 0.011, 0.018),
    (Vector((-0.024, 0, 0.99)), 0.012, 0.017),
    (Vector((+0.022, 0, 1.12)), 0.012, 0.017),
    (Vector((-0.014, 0, 1.26)), 0.011, 0.016),
    (Vector((+0.018, 0, 1.42)), 0.012, 0.016),
]
for pn, nr, dy in rune_nodes:
    for sy in (+1.0, -1.0):
        yb = sy * (dy - 0.002)
        yt = sy * (dy + 0.0048)
        r0 = [Vector((pn.x + nr, yb, pn.z)), Vector((pn.x, yb, pn.z + nr * 1.3)), Vector((pn.x - nr, yb, pn.z)), Vector((pn.x, yb, pn.z - nr * 1.3))]
        r1 = [Vector((pn.x + nr * 0.45, yt, pn.z)), Vector((pn.x, yt, pn.z + nr * 0.6)), Vector((pn.x - nr * 0.45, yt, pn.z)), Vector((pn.x, yt, pn.z - nr * 0.6))]
        add_lofted_tube(bm_runes, uv_runes, [r0, r1], [0.25, 0.75], "emerald", cap_start=False, cap_end=True)

finalize_mesh_obj("Inlay_RunicVeins", bm_runes, smooth_angle_deg=0.0)


# ==============================================================================
# PART 4: GUARD_LIVINGROOTS (Asymmetric Intertwined Sacred Oak Roots)
# ==============================================================================
bm_guard = bmesh.new()
uv_guard = bm_guard.loops.layers.uv.new("UVMap")


def add_swept_root(bm, uv_l, ctrl_pts, r_start: float, r_end: float, twist_turns: float = 0.6, segs: int = 20):
    pts = sample_cubic_bezier(ctrl_pts[0], ctrl_pts[1], ctrl_pts[2], ctrl_pts[3], segs)
    frames = frame_along_curve(pts)
    K = 10
    rings = []
    vs = []
    for idx, (p, n, b, _t) in enumerate(frames):
        u = idx / segs
        r = r_start * (1.0 - 0.94 * (u ** 1.35)) + r_end * (u ** 1.35)
        # Subtle organic root knot swell around u=0.35, tapering crisply at u->1
        r *= 1.0 + 0.14 * math.sin(u * math.pi * 2.5) * (1.0 - u)
        ring = []
        for k in range(K):
            ang = k * (2 * math.pi / K) + u * twist_turns * 2 * math.pi
            bark_flute = 1.0 + 0.12 * math.cos(k * 3.0 + u * 5.0)
            offset = (n * math.cos(ang) + b * math.sin(ang) * 0.86) * (r * bark_flute)
            ring.append(p + offset)
        rings.append(ring)
        vs.append(0.04 + 0.92 * u)
    add_lofted_tube(bm, uv_l, rings, vs, "bark", cap_start=True, cap_end=True)


# 4A. Leading-edge (+X) Ascending Wing-Root (emerges above Bronze Habaki collar at z=0.072!)
add_swept_root(
    bm_guard, uv_guard,
    [Vector((-0.02, 0.0, 0.072)), Vector((0.18, +0.028, 0.078)), Vector((0.36, +0.015, 0.168)), Vector((0.46, -0.010, 0.285))],
    0.048, 0.0035, twist_turns=0.45, segs=22
)
# 4B. Secondary intertwined (+X) Lower Root Spur
add_swept_root(
    bm_guard, uv_guard,
    [Vector((0.02, -0.018, 0.062)), Vector((0.16, -0.032, 0.045)), Vector((0.29, +0.018, 0.082)), Vector((0.36, +0.012, 0.148))],
    0.036, 0.0030, twist_turns=-0.5, segs=18
)
# 4C. Spine-side (-X) Descending Knuckle-Hook Root (asymmetric downward sweep!)
add_swept_root(
    bm_guard, uv_guard,
    [Vector((0.02, 0.0, 0.074)), Vector((-0.17, -0.026, 0.065)), Vector((-0.34, +0.016, +0.005)), Vector((-0.41, +0.005, -0.085))],
    0.047, 0.0035, twist_turns=-0.45, segs=22
)
# 4D. Spine-side (-X) Upper Bark Horn cradling the ricasso
add_swept_root(
    bm_guard, uv_guard,
    [Vector((-0.03, +0.018, 0.078)), Vector((-0.15, +0.030, 0.102)), Vector((-0.24, -0.012, 0.148)), Vector((-0.28, -0.005, 0.205))],
    0.034, 0.0030, twist_turns=0.35, segs=16
)
# 4E. Two delicate inner tendrils cradling the Awakening Seed inside the Eye
add_swept_root(
    bm_guard, uv_guard,
    [Vector((0.032, 0.0, 0.165)), Vector((0.052, +0.016, 0.205)), Vector((0.030, +0.010, 0.245)), Vector((0.006, 0.0, 0.268))],
    0.015, 0.003, twist_turns=0.2, segs=12
)
add_swept_root(
    bm_guard, uv_guard,
    [Vector((-0.032, 0.0, 0.530)), Vector((-0.048, -0.015, 0.490)), Vector((-0.026, -0.009, 0.455)), Vector((-0.005, 0.0, 0.440))],
    0.014, 0.003, twist_turns=-0.2, segs=12
)

finalize_mesh_obj("Guard_LivingRoots", bm_guard, smooth_angle_deg=55.0)


# ==============================================================================
# PART 5: FERRULE_SANCTUARYBRONZE (Upper Habaki Collar, Eye Arch Bands & Lower Collar)
# ==============================================================================
bm_ferrule = bmesh.new()
uv_ferrule = bm_ferrule.loops.layers.uv.new("UVMap")


def add_oct_collar(bm, uv_l, z_bot: float, z_top: float, rx_base: float, ry_base: float):
    zs = [
        (z_bot,                          0.92),
        (z_bot + (z_top - z_bot) * 0.18, 1.06),
        (z_bot + (z_top - z_bot) * 0.50, 0.98),
        (z_bot + (z_top - z_bot) * 0.82, 1.08),
        (z_top,                          0.94),
    ]
    rings = []
    vs = []
    for idx, (zv, sc) in enumerate(zs):
        ring = []
        for k in range(8):
            ang = k * (2 * math.pi / 8.0) + (math.pi / 8.0)
            ring.append(Vector((math.cos(ang) * rx_base * sc, math.sin(ang) * ry_base * sc, zv)))
        rings.append(ring)
        vs.append(0.1 + 0.8 * (idx / (len(zs) - 1)))
    add_lofted_tube(bm, uv_l, rings, vs, "bronze", cap_start=True, cap_end=True)


# Upper Habaki/Fuchi collar sits cleanly below the living-root guard (z = -0.012 .. +0.052)
add_oct_collar(bm_ferrule, uv_ferrule, -0.012, 0.052, 0.078, 0.048)
# Sculpted bronze crown band clasping the reunion of the Eye limbs at z = 0.515 .. 0.550!
add_oct_collar(bm_ferrule, uv_ferrule, 0.518, 0.548, 0.138, 0.039)
# Lower Pommel Collar (z = -0.455 .. -0.402)
add_oct_collar(bm_ferrule, uv_ferrule, -0.455, -0.402, 0.076, 0.048)

finalize_mesh_obj("Ferrule_SanctuaryBronze", bm_ferrule, smooth_angle_deg=0.0)


# ==============================================================================
# PART 6: GRIP_BRAIDEDVINE (Oval Ironwood Handle + 7 Raised Criss-Cross Wraps)
# ==============================================================================
bm_grip = bmesh.new()
uv_grip = bm_grip.loops.layers.uv.new("UVMap")

# 6A. Ergonomic palm-swell oval handle core (z = -0.415 .. +0.010)
grip_rings = []
grip_vs = []
for i in range(13):
    u = i / 12.0
    z = -0.415 + u * 0.425
    swell = 1.0 + 0.15 * math.sin(u * math.pi)
    rx = 0.056 * swell
    ry = 0.036 * swell
    ring = []
    for k in range(12):
        ang = k * (2 * math.pi / 12.0)
        ring.append(Vector((math.cos(ang) * rx, math.sin(ang) * ry, z)))
    grip_rings.append(ring)
    grip_vs.append(0.05 + 0.90 * u)
add_lofted_tube(bm_grip, uv_grip, grip_rings, grip_vs, "bark", cap_start=True, cap_end=True)

# 6B. 7 physical raised X-crossed leather/vine wrap bands!
for b_idx in range(7):
    z_mid = -0.365 + b_idx * 0.056
    u_mid = (z_mid - (-0.415)) / 0.425
    swell = 1.0 + 0.15 * math.sin(u_mid * math.pi)
    rx = 0.060 * swell
    ry = 0.040 * swell
    for tilt_sign in (-1.0, +1.0):
        band_rings = []
        for s in (-1, 0, 1):
            ring = []
            r_bulge = 1.005 if s == 0 else 0.965
            for k in range(12):
                ang = k * (2 * math.pi / 12.0)
                z_off = s * 0.012 + tilt_sign * 0.016 * math.sin(ang)
                ring.append(Vector((math.cos(ang) * rx * r_bulge, math.sin(ang) * ry * r_bulge, z_mid + z_off)))
            band_rings.append(ring)
        add_lofted_tube(bm_grip, uv_grip, band_rings, [0.15, 0.50, 0.85], "cord", cap_start=True, cap_end=True)

finalize_mesh_obj("Grip_BraidedVine", bm_grip, smooth_angle_deg=48.0)


# ==============================================================================
# PART 7: POMMEL_ROOTCLAW & STONE_AMBERSAP (4 Root Talons Clasping Amber Spirit Gem)
# ==============================================================================
bm_pommel = bmesh.new()
uv_pommel = bm_pommel.loops.layers.uv.new("UVMap")

claw_angles = [0.0, math.pi * 0.5, math.pi, math.pi * 1.5]
claw_scales = [(1.12, 1.0), (0.82, 0.92), (1.08, 1.04), (0.82, 0.92)]
for ang, (rad_sc, len_sc) in zip(claw_angles, claw_scales):
    dx = math.cos(ang)
    dy = math.sin(ang) * 0.78
    add_swept_root(
        bm_pommel, uv_pommel,
        [
            Vector((dx * 0.048, dy * 0.048, -0.440)),
            Vector((dx * 0.098 * rad_sc, dy * 0.098 * rad_sc, -0.485)),
            Vector((dx * 0.092 * rad_sc, dy * 0.092 * rad_sc, -0.548 * len_sc)),
            Vector((dx * 0.026, dy * 0.026, -0.580 * len_sc)),
        ],
        0.026, 0.008, twist_turns=0.22, segs=14
    )

# Faceted Amber Sap Spirit Gem nestled inside the 4 root claws
sap_stations = [
    (-0.575, 0.004, 0.004),
    (-0.548, 0.036, 0.030),
    (-0.512, 0.046, 0.038),
    (-0.478, 0.032, 0.026),
    (-0.458, 0.005, 0.005),
]
sap_rings = []
for zs_v, rx, ry in sap_stations:
    ring = []
    for k in range(8):
        ang = k * (2 * math.pi / 8.0)
        ring.append(Vector((math.cos(ang) * rx, math.sin(ang) * ry, zs_v)))
    sap_rings.append(ring)
add_lofted_tube(bm_pommel, uv_pommel, sap_rings, [0.05, 0.30, 0.55, 0.80, 0.96], "amber", cap_start=True, cap_end=True)

finalize_mesh_obj("Pommel_RootClaw", bm_pommel, smooth_angle_deg=35.0)


# --- PRINT EXACT MESH STATS FOR SPEC SHEET ---
total_verts = 0
total_tris = 0
for child in sword_root.children:
    if child.type == "MESH":
        m = child.data
        m.calc_loop_triangles()
        v_cnt = len(m.vertices)
        t_cnt = len(m.loop_triangles)
        total_verts += v_cnt
        total_tris += t_cnt
        print(f"PART {child.name:26s}: verts={v_cnt:5d}  tris={t_cnt:5d}  uv_layers={len(m.uv_layers)}")
print(f"TOTAL PILOT SWORD STATS: verts={total_verts}, tris={total_tris}")


# --- SAVE EDITABLE .BLEND SOURCE & EXPORT .GLB FOR GODOT 4.4 ---
# Note: Blender +Z up exports automatically as glTF +Y up (blade pointing straight up +Y in Godot 4.4!)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH, compress=True)
print("Saved editable Blender source:", BLEND_PATH)

bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format="GLB",
    export_yup=True,
    export_apply=True,
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_materials="EXPORT",
)
print("Exported Godot-ready GLB:", GLB_PATH)


# ==============================================================================
# STUDIO LEXAIR VALIDATION RENDERS (NEUTRAL THREE-POINT STUDIO LIGHT, NO BLOOM!)
# ==============================================================================
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_denoising = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

# Neutral studio light grey world (zero dramatic color bias, zero glow/fog!)
world = bpy.data.worlds.new("NeutralStudioWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.16, 0.17, 0.19, 1.0)
bg_node.inputs[1].default_value = 0.85


def add_area_light(name, loc, rot_deg, energy, size, col=(1.0, 0.99, 0.97)):
    ld = bpy.data.lights.new(name, type="AREA")
    ld.energy = energy
    ld.size = size
    ld.color = col
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    return lo


key_light = add_area_light("KeyLight", (1.9, -2.4, 1.8), (58, 0, 36), 150.0, 2.2, (1.0, 0.98, 0.95))
fill_light = add_area_light("FillLight", (-2.2, -1.8, 0.9), (72, 0, -48), 75.0, 2.6, (0.94, 0.97, 1.0))
rim_light = add_area_light("RimLight", (-0.4, 2.3, 1.5), (-62, 0, 168), 95.0, 2.0, (1.0, 1.0, 1.0))

cam_data = bpy.data.cameras.new("ReviewCam")
cam_data.lens = 55.0
cam_obj = bpy.data.objects.new("ReviewCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

target_empty = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(target_empty)
track = cam_obj.constraints.new(type="TRACK_TO")
track.target = target_empty
track.track_axis = "TRACK_NEGATIVE_Z"
track.up_axis = "UP_Y"


def render_view(filename: str, cam_pos, target_pos, res_x=800, res_y=1200, lens=55.0, emission_strength=0.15):
    # Note: emission_strength=0.15 during neutral light review so crystal isn't blown out and geometry stands on its own!
    for n in pbr_mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED" and "Emission Strength" in n.inputs:
            n.inputs["Emission Strength"].default_value = emission_strength
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    cam_data.lens = lens
    cam_obj.location = Vector(cam_pos)
    target_empty.location = Vector(target_pos)
    scene.render.filepath = f"{RENDERS_DIR}/{filename}"
    bpy.ops.render.render(write_still=True)
    print("Rendered:", filename)


# 1. Frontal (Neutral Light, looking from -Y toward +Y — full pommel-to-tip framing!)
render_view("view_01_front_neutral.png", (0.0, -4.35, 0.72), (0.0, 0.0, 0.72), 760, 1200, lens=50.0, emission_strength=0.18)

# 2. Lateral / Side Profile (looking from +X toward -X)
render_view("view_02_side_neutral.png", (4.35, 0.0, 0.72), (0.0, 0.0, 0.72), 760, 1200, lens=50.0, emission_strength=0.18)

# 3. Trasera / Back View (looking from +Y toward -Y)
render_view("view_03_back_neutral.png", (0.0, 4.35, 0.72), (0.0, 0.0, 0.72), 760, 1200, lens=50.0, emission_strength=0.18)

# 4. Tres Cuartos Hero View (3/4 angle, neutral light)
render_view("view_04_three_quarter_neutral.png", (1.95, -3.75, 0.86), (0.0, 0.0, 0.72), 900, 1200, lens=50.0, emission_strength=0.35)

# 5A. Close-up Hilt, Living Root Guard, Bronze Collar & Awakening Eye
render_view("view_05a_closeup_hilt_core.png", (0.54, -1.32, 0.22), (0.01, 0.0, 0.14), 900, 900, lens=58.0, emission_strength=0.35)

# 5B. Close-up Leaf-Swell Blade Bevels, Spine Bark Notch & Recessed Runes
render_view("view_05b_closeup_blade_runes.png", (0.48, -1.18, 1.24), (0.02, 0.0, 1.20), 900, 900, lens=60.0, emission_strength=0.25)

# 6. Pure Backlit Silhouette Check (Black Sword against Bright Neutral Studio Card!)
key_light.data.energy = 0.0
fill_light.data.energy = 0.0
rim_light.data.energy = 0.0
bg_node.inputs[0].default_value = (0.92, 0.94, 0.96, 1.0)
bg_node.inputs[1].default_value = 1.0
sil_mat = bpy.data.materials.new("M_PureSilhouette")
sil_mat.use_nodes = True
sil_bsdf = sil_mat.node_tree.nodes["Principled BSDF"]
sil_bsdf.inputs["Base Color"].default_value = (0.01, 0.01, 0.015, 1.0)
sil_bsdf.inputs["Roughness"].default_value = 1.0
sil_bsdf.inputs["Specular IOR Level"].default_value = 0.0
for child in sword_root.children:
    if child.type == "MESH":
        child.data.materials[0] = sil_mat
scene.cycles.samples = 16
render_view("view_06_silhouette_check.png", (0.0, -4.35, 0.72), (0.0, 0.0, 0.72), 760, 1200, lens=50.0, emission_strength=0.0)

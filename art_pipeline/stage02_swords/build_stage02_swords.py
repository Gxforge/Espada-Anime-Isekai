# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 02: TRES espadas bespoke (estilo anime exagerado por linaje)
  A. wood_verdant_living_bough  "Hoja de Brote Viviente"    (origin/orgánico denso)
  B. wood_mineral_copper_root   "Espada de Raíz Cobriza"    (elemental/eléctrico)
  C. wood_charred_ash_thorn     "Espada de Espino Carbonizado" (cursed/brasas)

Regla: geometría única por espada (nada de clones recolocados), UVs limpias en un
atlas de 5 regiones, emisión solo en zonas autorizadas del atlas.

Uso:
  blender --background --python build_stage02_swords.py -- sword=verdant
  blender --background --python build_stage02_swords.py -- sword=copper
  blender --background --python build_stage02_swords.py -- sword=ash
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

REPO = "/home/user/Espada-Anime-Isekai"

# Atlas de 5 regiones (idéntico layout que el Pilot #01):
REGIONS = {
    "blade": (0.00, 0.50, 0.50, 1.00),  # TL
    "flair": (0.50, 0.50, 1.00, 1.00),  # TR (guard / thorns / leaves / petals)
    "grip":  (0.00, 0.00, 0.50, 0.50),  # BL
    "shell": (0.50, 0.00, 0.75, 0.50),  # BM (ferrules / fins / pommel shell / ribs)
    "glow":  (0.75, 0.00, 1.00, 0.50),  # BR (cores / inlays / emitter rings)
}

def map_uv(u, v, region):
    u0, v0, u1, v1 = REGIONS[region]
    return (u0 + (u % 1.0) * (u1 - u0), v0 + min(max(v, 0.0), 1.0) * (v1 - v0))

def new_mesh_obj(name, collection):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    # re-open editable bmesh bound to this object
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    uv2 = bm2.loops.layers.uv.get("UVMap") or bm2.loops.layers.uv.new("UVMap")
    return obj, bm2, uv2

def commit(obj, bm):
    bm.to_mesh(obj.data)
    bm.free()

def add_lofted_tube(bm, uv_layer, rings_pts, rings_v, region, cap_start=True, cap_end=True, u_tile=1.0):
    K = len(rings_pts[0])
    vert_rings = [[bm.verts.new(p) for p in rp] for rp in rings_pts]
    for i in range(len(vert_rings) - 1):
        r0, r1 = vert_rings[i], vert_rings[i + 1]
        v0, v1 = rings_v[i], rings_v[i + 1]
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([r0[j], r0[jn], r1[jn], r1[j]])
            u0, u1u = j / K * u_tile, (j + 1) / K * u_tile
            f.loops[0][uv_layer].uv = map_uv(u0, v0, region)
            f.loops[1][uv_layer].uv = map_uv(u1u, v0, region)
            f.loops[2][uv_layer].uv = map_uv(u1u, v1, region)
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

def make_rings(stations, section_fn):
    """stations: list of (z, params-dict). section_fn(z, p) -> list[Vector]."""
    rings, vs = [], []
    for st in stations:
        z, p = st
        rings.append(section_fn(z, p))
        vs.append(p.get("v", (z - stations[0][0]) / max(1e-4, stations[-1][0] - stations[0][0])))
    return rings, vs

def strip_loft(bm, uv, pts_xy_at_z, region, half_w=0.006, half_t=0.0035, v_range=(0.0, 1.0)):
    """Thin rectangular-section strip following a 3D polyline (for inlay seams)."""
    rings, vs = [], []
    n = len(pts_xy_at_z)
    for i, (x, y, z) in enumerate(pts_xy_at_z):
        rings.append([
            Vector((x, y + half_t, z)), Vector((x + half_w, y, z)),
            Vector((x, y - half_t, z)), Vector((x - half_w, y, z)),
        ])
        vs.append(v_range[0] + (v_range[1] - v_range[0]) * i / max(1, n - 1))
    add_lofted_tube(bm, uv, rings, vs, region)

def bez(p0, p1, p2, p3, t):
    mt = 1.0 - t
    return mt**3 * p0 + 3 * mt**2 * t * p1 + 3 * mt * t**2 * p2 + t**3 * p3

def frame_frames(pts):
    frames = []
    up_ref = Vector((0, 1, 0))
    for i, p in enumerate(pts):
        t = (pts[1] - pts[0]).normalized() if i == 0 else ((pts[-1] - pts[-2]).normalized() if i == len(pts) - 1 else (pts[i + 1] - pts[i - 1]).normalized())
        if abs(t.dot(up_ref)) > 0.92:
            up_ref = Vector((1, 0, 0))
        n = t.cross(up_ref).normalized()
        b = n.cross(t).normalized()
        frames.append((p, n, b, t))
    return frames

def curved_loft(bm, uv, path_pts, radius_fn, K, region, cap_start=True, cap_end=True, v_tile=None):
    frames = frame_frames(path_pts)
    rings, vs = [], []
    n = len(frames) - 1
    for i, (p, nrm, bnr, tg) in enumerate(frames):
        rad = radius_fn(i / max(1, n))
        ring = []
        for j in range(K):
            a = 2 * math.pi * j / K
            ring.append(p + nrm * math.cos(a) * rad + bnr * math.sin(a) * rad)
        rings.append(ring)
        vs.append(i / n if v_tile is None else i / n * v_tile)
    add_lofted_tube(bm, uv, rings, vs, region, cap_start=cap_start, cap_end=cap_end)

# =============================================================================
# SWORD A: wood_verdant_living_bough - "Hoja de Brote Viviente"
# =============================================================================
def build_verdant(col):
    def blade_section(z, p):
        # 12-vert organic bough: thick gnarled spine, grooved belly, keen edge
        w = p["x_edge"] - p["x_spine"]
        xs, xe = p["x_spine"], p["x_edge"]
        ys, yr = p["half_t"] * 0.55, p["half_t"]
        yf = max(0.006, p["half_t"] - p["fuller"])
        ye = 0.0022
        gn = p.get("gnarl", 0.0)
        return [
            Vector((xe,             ye,        z)),           # 0 edge
            Vector((xs + 0.78 * w,  yr,        z)),           # 1
            Vector((xs + 0.56 * w,  yf,        z + gn)),      # 2
            Vector((xs + 0.44 * w,  yf,        z - gn)),      # 3
            Vector((xs + 0.24 * w,  yr * 0.94, z)),           # 4
            Vector((xs + 0.10 * w,  ys * 1.12, z + gn * 0.6)),# 5 bark ridge
            Vector((xs,             ys * 0.62, z)),           # 6 spine back
            Vector((xs,             -ys * 0.62,z)),           # 7
            Vector((xs + 0.10 * w,  -ys * 1.12,z - gn * 0.6)),# 8
            Vector((xs + 0.24 * w,  -yr * 0.94,z)),           # 9
            Vector((xs + 0.44 * w,  -yf,       z - gn)),      # 10
            Vector((xs + 0.56 * w,  -yf,       z + gn)),      # 11
            Vector((xs + 0.78 * w,  -yr,       z)),           # 12
            Vector((xe,             -ye,       z)),           # 13
        ]

    # Curved organic lean (scimitar-ish) via spine offset
    def spine_x(z):
        return -0.055 + 0.16 * math.sin(max(0.0, z) / 2.05 * 1.15) * (z / 2.05)

    stations = []
    zs = [0.06, 0.14, 0.30, 0.55, 0.85, 1.15, 1.45, 1.72, 1.92, 2.02, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = (0.155 - 0.105 * t) * (1.0 + 0.10 * math.sin(t * 9.0))
        half_t = 0.030 * (1.0 - 0.72 * t) + 0.0025
        stations.append((z, {
            "x_spine": spine_x(z), "x_edge": spine_x(z) + width,
            "half_t": half_t, "fuller": 0.011 * (1.0 - 0.5 * t),
            "gnarl": 0.010 * math.sin(t * 16.0), "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_LivingBough", col)
    rings, vs = make_rings(stations, blade_section)
    add_lofted_tube(bm, uv, rings, vs, "blade", cap_start=True, cap_end=True)
    # 2 branch stubs from the spine (disconnected islands, same object)
    for bz, blen, brot in [(0.85, 0.34, 0.55), (1.42, 0.26, 0.80)]:
        sx = spine_x(bz)
        path = []
        for i in range(7):
            t = i / 6.0
            path.append(Vector((sx - 0.02, 0.0, bz + blen * t * math.cos(brot)) ) + Vector((-blen * t * math.sin(brot), 0, 0)))
        curved_loft(bm, uv, path, lambda t: 0.022 * (1.0 - t) + 0.004, 8, "flair")
    commit(obj, bm)

    # Leaf canopy fans (6 leaves in one object, two fans)
    obj, bm, uv = new_mesh_obj("Leaves_CanopyClusters", col)
    def leaf(origin, direction, length, width, tilt):
        frames = []
        for i in range(6):
            t = i / 5.0
            pos = origin + direction * (length * t) + Vector((0, tilt * math.sin(t * math.pi) * 0.5, 0))
            frames.append(pos)
        for i in range(5):
            p0 = frames[i]; p1 = frames[i + 1]
            w0 = width * math.sin((i / 5.0) * math.pi * 0.9)
            w1 = width * math.sin(((i + 1) / 5.0) * math.pi * 0.9)
            v0 = i / 5.0; v1 = (i + 1) / 5.0
            ring0 = [p0, p0 + Vector((0, w0 * 0.5, 0)), p0 + Vector((0, 0, w0 * 0.8)), p0 + Vector((0, -w0 * 0.5, 0))]
            ring1 = [p1, p1 + Vector((0, w1 * 0.5, 0)), p1 + Vector((0, 0, w1 * 0.8)), p1 + Vector((0, -w1 * 0.5, 0))]
            add_lofted_tube(bm, uv, [ring0, ring1], [v0, v1], "flair", cap_start=(i == 0), cap_end=(i == 4))
    for bz, cnt in [(0.72, 3), (1.30, 3)]:
        sx = spine_x(bz)
        for k in range(cnt):
            ang = -0.5 + k * 0.5
            leaf(Vector((sx - 0.03, 0.02 * (k - 1), bz)), Vector((-0.55 - 0.2 * k, 0.12 * (k - 1), 0.55 + 0.1 * abs(ang))).normalized(), 0.20, 0.045, 0.6)
    commit(obj, bm)

    # Curling root guard (two symmetric spiral arms)
    obj, bm, uv = new_mesh_obj("Guard_CurlingRoots", col)
    for side in (1.0, -1.0):
        path = []
        for i in range(10):
            t = i / 9.0
            ang = t * 2.1
            path.append(Vector((
                side * (0.075 + 0.115 * math.sin(ang)),
                side * (0.02 * math.sin(ang * 1.6)),
                0.10 - 0.19 * t + 0.05 * math.sin(ang),
            )))
        curved_loft(bm, uv, path, lambda t: 0.030 * (1.0 - 0.75 * t) + 0.006, 9, "flair")
    commit(obj, bm)

    # Moss-wrapped grip
    obj, bm, uv = new_mesh_obj("Grip_MossWrappedWood", col)
    rings, vs, zz = [], [], []
    for i in range(11):
        z = 0.055 - 0.47 * (i / 10.0)
        r = 0.030 + 0.006 * math.sin(i * 2.4) + (0.005 if i % 3 == 0 else 0.0)
        ring = [Vector((math.cos(2 * math.pi * j / 9) * r + 0.012 * math.sin(i * 1.7), math.sin(2 * math.pi * j / 9) * r, z)) for j in range(9)]
        rings.append(ring); vs.append(i / 10.0)
    add_lofted_tube(bm, uv, rings, vs, "grip")
    commit(obj, bm)

    # Sap veins (two wavy emissive strips on the blade faces)
    obj, bm, uv = new_mesh_obj("Inlay_SapVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.22 + 1.62 * t
            pts.append((spine_x(z) + 0.055 + 0.045 * math.sin(t * 7.5), sy * 0.018, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0035)
    commit(obj, bm)

    # Blooming bud core (emissive lens) + 2 petals (flair region)
    obj, bm, uv = new_mesh_obj("Core_BloomingBud", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.026, 0.030), (0.034, 0.052), (0.026, 0.070), (0.012, 0.078)]):
        z = 0.20 + h2
        ring = [Vector((0.015 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.55, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    for side in (1.0, -1.0):
        path = [Vector((0.015, side * 0.012, 0.22)), Vector((0.015, side * 0.052, 0.245)), Vector((0.015, side * 0.030, 0.272))]
        curved_loft(bm, uv, path, lambda t: 0.012 * (1.0 - t) + 0.003, 7, "flair")
    commit(obj, bm)

    # Root bulb pommel
    obj, bm, uv = new_mesh_obj("Pommel_RootBulb", col)
    rings, vs = [], []
    for i, r in enumerate([0.016, 0.036, 0.044, 0.040, 0.024, 0.006]):
        z = -0.475 - 0.10 * (i / 5.0)
        ring = [Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r * 1.15, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 5.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    # Bronze-wood ferrule collars
    obj, bm, uv = new_mesh_obj("Ferrule_VeridianBronze", col)
    for z0, z1 in [(0.02, 0.06), (-0.44, -0.475)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            r = 0.037
            ring = [Vector((math.cos(2 * math.pi * j / 12) * r, math.sin(2 * math.pi * j / 12) * r * 1.1, z)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell", cap_start=True, cap_end=True)
    commit(obj, bm)

# =============================================================================
# SWORD B: wood_mineral_copper_root - "Espada de Raíz Cobriza"
# =============================================================================
def build_copper(col):
    def fang_section(z, p):
        # 12-vert angular hex-fang: flat plated back, chevron ridge, razor tip face
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        return [
            Vector((xe,                 0.0,          z)),          # 0 razor point
            Vector((xs + 0.86 * w,      ht * 0.42,    z)),          # 1
            Vector((xs + 0.68 * w,      ht,           z)),          # 2 hex ridge top
            Vector((xs + 0.50 * w,      ht * 0.72,    z)),          # 3 valley
            Vector((xs + 0.30 * w,      ht * 0.95,    z)),          # 4 rib
            Vector((xs + 0.12 * w,      ht * 0.55,    z)),          # 5 plated back top
            Vector((xs,                 ht * 0.18,    z)),          # 6 spine back top
            Vector((xs,                 -ht * 0.18,   z)),          # 7 spine back bot
            Vector((xs + 0.12 * w,      -ht * 0.55,   z)),          # 8
            Vector((xs + 0.30 * w,      -ht * 0.95,   z)),          # 9
            Vector((xs + 0.50 * w,      -ht * 0.72,   z)),          # 10
            Vector((xs + 0.68 * w,      -ht,          z)),          # 11
            Vector((xs + 0.86 * w,      -ht * 0.42,   z)),          # 12
            Vector((xe,                 -0.0,         z)),          # 13
        ]

    stations = []
    zs = [0.06, 0.13, 0.28, 0.52, 0.80, 1.10, 1.42, 1.70, 1.92, 2.03, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.148 - 0.098 * t) * (1.0 + 0.06 * ((i % 2) * 0.5))
        stations.append((z, {
            "x_spine": -0.052, "x_edge": -0.052 + width,
            "half_t": 0.026 * (1.0 - 0.70 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_CopperFangSheath", col)
    rings, vs = make_rings(stations, fang_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    # 3 angled plating rib collars (hexagonal, slightly proud, disconnected islands)
    for z0 in (0.42, 0.95, 1.50):
        rings, vs = [], []
        for i, z in enumerate([z0, z0 + 0.07]):
            t = z / 2.08
            xs, xe = -0.052, -0.052 + (0.148 - 0.098 * t)
            ht = 0.026 * (1.0 - 0.70 * t) + 0.003 + 0.006
            rings.append(fang_section(z, {"x_spine": xs, "x_edge": xe, "half_t": ht}))
            vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell", cap_start=False, cap_end=False)
    commit(obj, bm)

    # Petrified root core visible through the spine slit
    obj, bm, uv = new_mesh_obj("Core_PetrifiedRootCore", col)
    rings, vs = [], []
    for i in range(9):
        z = 0.10 + 1.80 * (i / 8.0)
        r = 0.014 + 0.005 * math.sin(i * 1.9)
        ring = [Vector((-0.052 - r, math.sin(2 * math.pi * j / 8) * r * 0.7, z)) for j in range(8)]
        rings.append(ring); vs.append(i / 8.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Forked stag-horn guard (4 horns = 2 per side)
    obj, bm, uv = new_mesh_obj("Guard_ForkedStagHorns", col)
    for side in (1.0, -1.0):
        main = [Vector((side * 0.055, 0.0, 0.11)), Vector((side * 0.135, 0.0, 0.02)),
                Vector((side * 0.205, 0.0, -0.06)), Vector((side * 0.255, 0.0, -0.16))]
        curved_loft(bm, uv, main, lambda t: 0.030 * (1.0 - 0.7 * t) + 0.005, 9, "flair")
        fork = [Vector((side * 0.135, 0.0, 0.02)), Vector((side * 0.190, 0.0, 0.09)),
                Vector((side * 0.230, 0.0, 0.19))]
        curved_loft(bm, uv, fork, lambda t: 0.020 * (1.0 - 0.8 * t) + 0.004, 8, "flair")
    commit(obj, bm)

    # Copper coil-wrapped grip (alternating coil rings)
    obj, bm, uv = new_mesh_obj("Grip_CopperCoilWrap", col)
    rings, vs = [], []
    for i in range(13):
        z = 0.055 - 0.46 * (i / 12.0)
        r = 0.029 + (0.007 if i % 2 == 0 else 0.0)
        ring = [Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 12.0)
    add_lofted_tube(bm, uv, rings, vs, "grip")
    commit(obj, bm)

    # Voltaic seams (2 sharp zigzag emissive strips + spine seam)
    obj, bm, uv = new_mesh_obj("Inlay_VoltaicSeams", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(15):
            t = i / 14.0
            z = 0.20 + 1.70 * t
            zig = 0.014 * (1.0 if (i % 2 == 0) else -1.0)
            pts.append((-0.052 + 0.075 + 0.035 * math.sin(t * 5.0), sy * (0.016 + zig), z))
        strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.003)
    pts = []
    for i in range(11):
        t = i / 10.0
        z = 0.16 + 1.75 * t
        pts.append((-0.058, 0.0, z))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.0035)
    commit(obj, bm)

    # Anodic finials (3 copper spikes near the ricasso)
    obj, bm, uv = new_mesh_obj("Sparks_AnodicFinials", col)
    for (y0, z0, ln, dx) in [(0.035, 0.16, 0.22, 0.06), (-0.035, 0.16, 0.22, 0.06), (0.0, 0.30, 0.30, 0.10)]:
        path = [Vector((-0.052 + dx * t * t + 0.01, y0 * (1.0 - 0.6 * t), z0 + ln * t)) for t in [i / 5.0 for i in range(6)]]
        curved_loft(bm, uv, path, lambda t: 0.011 * (1.0 - t) + 0.002, 7, "shell")
    commit(obj, bm)

    # Galvanic bulb pommel + emissive equatorial ring
    obj, bm, uv = new_mesh_obj("Pommel_GalvanicBulb", col)
    rings, vs = [], []
    for i, r in enumerate([0.014, 0.033, 0.042, 0.038, 0.022, 0.005]):
        z = -0.465 - 0.105 * (i / 5.0)
        ring = [Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)]
        rings.append(ring); vs.append(i / 5.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    ring_pts = []
    for j in range(17):
        a = 2 * math.pi * j / 16
        ring_pts.append((math.cos(a) * 0.043, math.sin(a) * 0.043, -0.512))
    strip_loft(bm, uv, ring_pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # Copper ferrule collars
    obj, bm, uv = new_mesh_obj("Ferrule_GalvanicCopper", col)
    for z0, z1 in [(0.02, 0.06), (-0.435, -0.465)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            r = 0.036
            ring = [Vector((math.cos(2 * math.pi * j / 12) * r, math.sin(2 * math.pi * j / 12) * r, z)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

# =============================================================================
# SWORD C: wood_charred_ash_thorn - "Espada de Espino Carbonizado"
# =============================================================================
def build_ash(col):
    def charred_section(z, p):
        # 12-vert jagged charcoal: saw-back spine, cracked belly, keen edge
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        saw = p.get("saw", 0.0)
        return [
            Vector((xe,                 0.0,          z)),
            Vector((xs + 0.80 * w,      ht * 0.5,     z)),
            Vector((xs + 0.58 * w,      ht,           z)),
            Vector((xs + 0.40 * w,      ht * 0.62,    z)),
            Vector((xs + 0.22 * w,      ht * 0.92,    z)),
            Vector((xs + 0.08 * w + saw,ht * 0.5,     z)),
            Vector((xs + saw,           ht * 0.16,    z)),
            Vector((xs + saw,           -ht * 0.16,   z)),
            Vector((xs + 0.08 * w + saw,-ht * 0.5,    z)),
            Vector((xs + 0.22 * w,      -ht * 0.92,   z)),
            Vector((xs + 0.40 * w,      -ht * 0.62,   z)),
            Vector((xs + 0.58 * w,      -ht,          z)),
            Vector((xs + 0.80 * w,      -ht * 0.5,    z)),
            Vector((xe,                 0.0,          z)),
        ]

    stations = []
    zs = [0.06, 0.13, 0.30, 0.55, 0.82, 1.12, 1.44, 1.72, 1.92, 2.02, 2.07]
    for i, z in enumerate(zs):
        t = z / 2.07
        bend = 0.045 * math.sin(t * 1.35)
        width = (0.150 - 0.100 * t) * (1.0 + (0.05 if i % 2 else 0.0))
        stations.append((z, {
            "x_spine": -0.050 + bend, "x_edge": -0.050 + bend + width,
            "half_t": 0.027 * (1.0 - 0.70 * t) + 0.003,
            "saw": 0.012 * (1.0 if i % 2 else 0.0) * (1.0 - t),
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_CharredBlackwood", col)
    rings, vs = make_rings(stations, charred_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Black briar thorn spikes along the spine (4, one object)
    obj, bm, uv = new_mesh_obj("Thorns_BlackBriarSpikes", col)
    for bz, ln, tilt in [(0.50, 0.20, 0.9), (0.95, 0.26, 1.1), (1.40, 0.22, 1.0), (1.75, 0.15, 0.8)]:
        st = min(stations, key=lambda s: abs(s[0] - bz))
        sx = st[1]["x_spine"] - 0.004
        path = []
        for i in range(6):
            t = i / 5.0
            path.append(Vector((sx - 0.055 * t * tilt, 0.0, bz + ln * t)))
        curved_loft(bm, uv, path, lambda t: 0.017 * (1.0 - t) + 0.002, 7, "flair")
    commit(obj, bm)

    # Cursed thorn crown guard: octagonal ring band + 6 thorns
    obj, bm, uv = new_mesh_obj("Guard_CursedThornCrown", col)
    rings, vs = [], []
    for i, (r, z) in enumerate([(0.052, 0.09), (0.085, 0.055), (0.085, -0.02), (0.052, -0.055)]):
        ring = [Vector((math.cos(2 * math.pi * j / 12) * r, math.sin(2 * math.pi * j / 12) * r, z)) for j in range(12)]
        rings.append(ring); vs.append(i / 3.0)
    add_lofted_tube(bm, uv, rings, vs, "flair", cap_start=True, cap_end=True)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.26
        path = []
        for i in range(5):
            t = i / 4.0
            path.append(Vector((math.cos(a) * (0.085 + 0.055 * t), math.sin(a) * (0.085 + 0.055 * t), 0.02 - 0.075 * t)))
        curved_loft(bm, uv, path, lambda t: 0.013 * (1.0 - t) + 0.002, 6, "flair")
    commit(obj, bm)

    # Ash charcoal grip
    obj, bm, uv = new_mesh_obj("Grip_AshCharcoalWrap", col)
    rings, vs = [], []
    for i in range(11):
        z = 0.055 - 0.47 * (i / 10.0)
        r = 0.029 + 0.005 * math.sin(i * 2.1)
        ring = [Vector((math.cos(2 * math.pi * j / 9) * r, math.sin(2 * math.pi * j / 9) * r, z)) for j in range(9)]
        rings.append(ring); vs.append(i / 10.0)
    add_lofted_tube(bm, uv, rings, vs, "grip")
    commit(obj, bm)

    # Ember heart visible through the ricasso crack
    obj, bm, uv = new_mesh_obj("Core_SmolderingEmberHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.022, 0.024), (0.030, 0.044), (0.020, 0.060), (0.009, 0.066)]):
        z = 0.18 + h2
        ring = [Vector((0.020 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Ember fissures (3 jagged emissive crack strips)
    obj, bm, uv = new_mesh_obj("Inlay_EmberFissures", col)
    for sy, z0, z1, amp in ((1.0, 0.24, 1.55, 0.016), (-1.0, 0.35, 1.35, 0.014), (1.0, 1.60, 1.95, 0.010)):
        pts = []
        n = 12
        for i in range(n):
            t = i / (n - 1.0)
            z = z0 + (z1 - z0) * t
            sx = -0.050 + 0.045 * math.sin(t * 1.35)  # follow the bend
            pts.append((sx + 0.062 + 0.028 * math.sin(t * 9.0), sy * (amp if i % 2 == 0 else amp * 0.35), z))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.0028)
    commit(obj, bm)

    # Ember seed pommel
    obj, bm, uv = new_mesh_obj("Pommel_EmberSeed", col)
    rings, vs = [], []
    for i, r in enumerate([0.015, 0.034, 0.042, 0.036, 0.020, 0.004]):
        z = -0.465 - 0.10 * (i / 5.0)
        ring = [Vector((math.cos(2 * math.pi * j / 9) * r, math.sin(2 * math.pi * j / 9) * r * 1.1, z)) for j in range(9)]
        rings.append(ring); vs.append(i / 5.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    ring_pts = []
    for j in range(13):
        a = 2 * math.pi * j / 12
        ring_pts.append((math.cos(a) * 0.031, math.sin(a) * 0.034, -0.502))
    strip_loft(bm, uv, ring_pts, "glow", half_w=0.0045, half_t=0.0045)
    commit(obj, bm)

    # Cursed iron-ash ferrule collars
    obj, bm, uv = new_mesh_obj("Ferrule_CursedAshIron", col)
    for z0, z1 in [(0.02, 0.06), (-0.435, -0.465)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            r = 0.036
            ring = [Vector((math.cos(2 * math.pi * j / 12) * r, math.sin(2 * math.pi * j / 12) * r, z)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

# =============================================================================
# MATERIAL, SCENE, SAVE & EXPORT
# =============================================================================
SWORD_META = {
    "verdant": {
        "name": "sword_02_verdant_bough",
        "builder": build_verdant,
        "tex": "verdant_bough",
        "form_id": "wood_verdant_living_bough",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "verdant_bough"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage02_swords", "verdant_bough"),
    },
    "copper": {
        "name": "sword_02_copper_root",
        "builder": build_copper,
        "tex": "copper_root",
        "form_id": "wood_mineral_copper_root",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "copper_root"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage02_swords", "copper_root"),
    },
    "ash": {
        "name": "sword_02_ash_thorn",
        "builder": build_ash,
        "tex": "ash_thorn",
        "form_id": "wood_charred_ash_thorn",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "ash_thorn"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage02_swords", "ash_thorn"),
    },
}

def make_atlas_material(mat_name, tex_dir, tex_base):
    m = bpy.data.materials.new(mat_name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]

    def img_node(fname, colorspace):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(os.path.join(tex_dir, fname))
        n.image.colorspace_settings.name = colorspace
        return n

    n_base = img_node("%s_basecolor.png" % tex_base, "sRGB")
    n_rough = img_node("%s_roughness.png" % tex_base, "Non-Color")
    n_metal = img_node("%s_metallic.png" % tex_base, "Non-Color")
    n_norm = img_node("%s_normal.png" % tex_base, "Non-Color")
    n_emis = img_node("%s_emission.png" % tex_base, "sRGB")
    n_nmap = nt.nodes.new("ShaderNodeNormalMap")
    n_nmap.inputs["Strength"].default_value = 0.85

    nt.links.new(n_base.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(n_rough.outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(n_metal.outputs["Color"], bsdf.inputs["Metallic"])
    nt.links.new(n_norm.outputs["Color"], n_nmap.inputs["Color"])
    nt.links.new(n_nmap.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(n_emis.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 2.2
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m

def main():
    # parse args after "--"
    argv = sys.argv
    sword = "verdant"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_02_%s" % meta["name"].split("_")[-1], None)
    col.objects.link(sword_root)
    parts = [o for o in col.objects if o.type == "MESH"]
    for o in parts:
        o.parent = sword_root

    # world scale: normalize along Z so total = 2.60 m, pivot at grip (z=0)
    zmin, zmax = 1e9, -1e9
    for o in parts:
        for v in o.data.vertices:
            zmin = min(zmin, v.co.z); zmax = max(zmax, v.co.z)
    s = 2.60 / max(1e-4, (zmax - zmin))
    sword_root.scale = (s, s, s)
    bpy.context.view_layer.update()

    # material from atlas maps (generated by generate_stage02_pbr_maps.py)
    tex_dir = meta["out_dir"]
    mat = make_atlas_material("MAT_%s" % meta["tex"], tex_dir, meta["tex"])
    for o in parts:
        o.data.materials.append(mat)

    # smooth shading for organic parts
    for o in parts:
        for p in o.data.polygons:
            p.use_smooth = True

    os.makedirs(meta["out_dir"], exist_ok=True)
    os.makedirs(meta["art_dir"], exist_ok=True)

    # stats
    tris = sum(len(p.vertices) - 2 for o in parts for p in o.data.polygons)
    verts = sum(len(o.data.vertices) for o in parts)
    print("BUILT %s parts=%d verts=%d tris=%d scale=%.4f" % (meta["name"], len(parts), verts, tris, s))

    # save editable .blend in art pipeline
    blend_path = os.path.join(meta["art_dir"], "%s.blend" % meta["name"])
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # export GLB (+Y up conversion handled by exporter)
    glb_path = os.path.join(meta["out_dir"], "%s.glb" % meta["name"])
    bpy.ops.export_scene.gltf(filepath=glb_path, use_selection=False, export_format="GLB")
    print("GLB_SAVED", glb_path)
    print("BLEND_SAVED", blend_path)
    print("STAGE02_BUILD_DONE", sword)

main()

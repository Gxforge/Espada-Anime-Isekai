# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 03: CUATRO espadas bespoke (anime exagerado por linaje)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage03_swords.py -- sword=amber|ironwood|willow|bramble
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

REPO = "/home/user/Espada-Anime-Isekai"

REGIONS = {
    "blade": (0.00, 0.50, 0.50, 1.00),
    "flair": (0.50, 0.50, 1.00, 1.00),
    "grip":  (0.00, 0.00, 0.50, 0.50),
    "shell": (0.50, 0.00, 0.75, 0.50),
    "glow":  (0.75, 0.00, 1.00, 0.50),
}

def map_uv(u, v, region):
    u0, v0, u1, v1 = REGIONS[region]
    return (u0 + (u % 1.0) * (u1 - u0), v0 + min(max(v, 0.0), 1.0) * (v1 - v0))

def new_mesh_obj(name, collection):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    uv2 = bm2.loops.layers.uv.get("UVMap") or bm2.loops.layers.uv.new("UVMap")
    return obj, bm2, uv2

def commit(obj, bm):
    bm.to_mesh(obj.data); bm.free()

def add_lofted_tube(bm, uv, rings_pts, rings_v, region, cap_start=True, cap_end=True):
    K = len(rings_pts[0])
    vert_rings = [[bm.verts.new(p) for p in rp] for rp in rings_pts]
    for i in range(len(vert_rings) - 1):
        r0, r1 = vert_rings[i], vert_rings[i + 1]
        v0, v1 = rings_v[i], rings_v[i + 1]
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([r0[j], r0[jn], r1[jn], r1[j]])
            u0, u1u = j / K, (j + 1) / K
            f.loops[0][uv].uv = map_uv(u0, v0, region)
            f.loops[1][uv].uv = map_uv(u1u, v0, region)
            f.loops[2][uv].uv = map_uv(u1u, v1, region)
            f.loops[3][uv].uv = map_uv(u0, v1, region)
    if cap_start:
        c0 = sum(rings_pts[0], Vector()) / K
        vc0 = bm.verts.new(c0)
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([vert_rings[0][jn], vert_rings[0][j], vc0])
            f.loops[0][uv].uv = map_uv((j + 1) / K, rings_v[0], region)
            f.loops[1][uv].uv = map_uv(j / K, rings_v[0], region)
            f.loops[2][uv].uv = map_uv(0.5, rings_v[0], region)
    if cap_end:
        c1 = sum(rings_pts[-1], Vector()) / K
        vc1 = bm.verts.new(c1)
        for j in range(K):
            jn = (j + 1) % K
            f = bm.faces.new([vert_rings[-1][j], vert_rings[-1][jn], vc1])
            f.loops[0][uv].uv = map_uv(j / K, rings_v[-1], region)
            f.loops[1][uv].uv = map_uv((j + 1) / K, rings_v[-1], region)
            f.loops[2][uv].uv = map_uv(0.5, rings_v[-1], region)

def make_rings(stations, section_fn):
    rings, vs = [], []
    for st in stations:
        z, p = st
        rings.append(section_fn(z, p))
        vs.append(p.get("v", (z - stations[0][0]) / max(1e-4, stations[-1][0] - stations[0][0])))
    return rings, vs

def strip_loft(bm, uv, pts_xy_at_z, region, half_w=0.005, half_t=0.0035, v_range=(0.0, 1.0)):
    rings, vs = [], []
    n = len(pts_xy_at_z)
    for i, (x, y, z) in enumerate(pts_xy_at_z):
        rings.append([Vector((x, y + half_t, z)), Vector((x + half_w, y, z)),
                      Vector((x, y - half_t, z)), Vector((x - half_w, y, z))])
        vs.append(v_range[0] + (v_range[1] - v_range[0]) * i / max(1, n - 1))
    add_lofted_tube(bm, uv, rings, vs, region)

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

def curved_loft(bm, uv, path_pts, radius_fn, K, region, cap_start=True, cap_end=True):
    frames = frame_frames(path_pts)
    rings, vs = [], []
    n = len(frames) - 1
    for i, (p, nrm, bnr, tg) in enumerate(frames):
        rad = radius_fn(i / max(1, n))
        ring = []
        for j in range(K):
            a = 2 * math.pi * j / K
            ring.append(p + nrm * math.cos(a) * rad + bnr * math.sin(a) * rad)
        rings.append(ring); vs.append(i / n)
    add_lofted_tube(bm, uv, rings, vs, region, cap_start=cap_start, cap_end=cap_end)

def grip_braid(bm, uv, z_top, z_bot, n_st, K, base_r, wobble, region="grip", thick_every=3, thick=0.006):
    rings, vs = [], []
    for i in range(n_st):
        z = z_top + (z_bot - z_top) * (i / (n_st - 1.0))
        r = base_r + wobble * math.sin(i * 2.2) + (thick if i % thick_every == 0 else 0.0)
        ring = [Vector((math.cos(2 * math.pi * j / K) * r, math.sin(2 * math.pi * j / K) * r, z)) for j in range(K)]
        rings.append(ring); vs.append(i / (n_st - 1.0))
    add_lofted_tube(bm, uv, rings, vs, region)

def ferrule_pair(bm, uv, pairs, r, K=12, squash=1.0):
    for z0, z1 in pairs:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            ring = [Vector((math.cos(2 * math.pi * j / K) * r, math.sin(2 * math.pi * j / K) * r * squash, z)) for j in range(K)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell")

def bulb_pommel(bm, uv, z_start, radii, K, squash=1.0, drop=0.105, ring_r=None, ring_z=None):
    rings, vs = [], []
    for i, r in enumerate(radii):
        z = z_start - drop * (i / (len(radii) - 1.0))
        ring = [Vector((math.cos(2 * math.pi * j / K) * r, math.sin(2 * math.pi * j / K) * r * squash, z)) for j in range(K)]
        rings.append(ring); vs.append(i / (len(radii) - 1.0))
    add_lofted_tube(bm, uv, rings, vs, "shell")
    if ring_r:
        pts = []
        for j in range(17):
            a = 2 * math.pi * j / 16
            pts.append((math.cos(a) * ring_r, math.sin(a) * ring_r * squash, ring_z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0045)

# =============================================================================
# A. awakening_amber_sanctuary_blade - "Hoja de Ambar de Santuario" (blessed heavy)
# =============================================================================
def build_amber(col):
    def amber_section(z, p):
        # 14-vert broad claymore: wide flat faces, proud bevels, warm edge
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0028
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.62 * w,  ht * 0.72, z)),
            Vector((xs + 0.38 * w,  ht * 0.98, z)),
            Vector((xs + 0.16 * w,  ht * 0.66, z)),
            Vector((xs + 0.05 * w,  ht * 0.30, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.30,z)),
            Vector((xs + 0.16 * w,  -ht * 0.66,z)),
            Vector((xs + 0.38 * w,  -ht * 0.98,z)),
            Vector((xs + 0.62 * w,  -ht * 0.72,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.13, 0.30, 0.56, 0.84, 1.14, 1.46, 1.74, 1.94, 2.04, 2.09]
    for i, z in enumerate(zs):
        t = z / 2.09
        width = (0.170 - 0.085 * t) * (1.0 + (0.03 if i % 2 else 0.0))
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + width,
            "half_t": 0.031 * (1.0 - 0.62 * t) + 0.004,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_AmberSanctuaryClaymore", col)
    rings, vs = make_rings(stations, amber_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Amber resin windows: 2 wide glassy strips on the flat faces (glow)
    obj, bm, uv = new_mesh_obj("Inlay_AmberResinWindows", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.30 * t
            pts.append((-0.050 + 0.085 + 0.030 * math.sin(t * 6.0), sy * 0.026, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.010, half_t=0.0045)
    commit(obj, bm)

    # Sanctuary halo ring floating behind the ricasso (glow emitter)
    obj, bm, uv = new_mesh_obj("Halo_SanctuaryRing", col)
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append((math.cos(a) * 0.105, math.sin(a) * 0.105, 0.24))
    strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.006)
    for k in range(4):  # 4 small halo petals
        a = 2 * math.pi * k / 4 + 0.4
        path = [Vector((math.cos(a) * (0.105 + 0.020 * t), math.sin(a) * (0.105 + 0.020 * t), 0.24 + 0.012 * math.sin(t * 3.0))) for t in [i / 4.0 for i in range(5)]]
        curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - t) + 0.003, 7, "flair")
    commit(obj, bm)

    # Sanctuary wings guard: 2 swept gilded wings
    obj, bm, uv = new_mesh_obj("Guard_SanctuaryWings", col)
    for side in (1.0, -1.0):
        path = [Vector((side * 0.055, 0.0, 0.10)), Vector((side * 0.130, 0.0, 0.055)),
                Vector((side * 0.210, 0.0, 0.035)), Vector((side * 0.265, 0.0, 0.065)),
                Vector((side * 0.290, 0.0, 0.115))]
        curved_loft(bm, uv, path, lambda t: 0.030 * (1.0 - 0.55 * t) + 0.006, 9, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ResinWrappedHilt", col)
    grip_braid(bm, uv, 0.055, -0.47, 11, 9, 0.031, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_AmberHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.006), (0.024, 0.028), (0.031, 0.048), (0.022, 0.062), (0.010, 0.068)]):
        z = 0.17 + h2
        ring = [Vector((0.020 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AmberOrb", col)
    bulb_pommel(bm, uv, -0.470, [0.016, 0.036, 0.045, 0.041, 0.026, 0.008], 9, squash=1.0, drop=0.105, ring_r=0.046, ring_z=-0.522)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_GildedBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.06), (-0.44, -0.47)], 0.037)
    commit(obj, bm)

# =============================================================================
# B. awakening_ironwood_storm_edge - "Filo de Palo Ferreo y Trueno" (elemental)
# =============================================================================
def build_ironwood(col):
    def slab_section(z, p):
        # 14-vert heavy cleaver slab: near-rectangular, broad, clipped tip feel
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,         z)),
            Vector((xs + 0.88 * w,  ht,         z)),
            Vector((xs + 0.70 * w,  ht,         z)),
            Vector((xs + 0.50 * w,  ht * 0.86,  z)),
            Vector((xs + 0.30 * w,  ht,         z)),
            Vector((xs + 0.12 * w,  ht,         z)),
            Vector((xs,             ht * 0.55,  z)),
            Vector((xs,             -ht * 0.55, z)),
            Vector((xs + 0.12 * w,  -ht,        z)),
            Vector((xs + 0.30 * w,  -ht,        z)),
            Vector((xs + 0.50 * w,  -ht * 0.86, z)),
            Vector((xs + 0.70 * w,  -ht,        z)),
            Vector((xs + 0.88 * w,  -ht,        z)),
            Vector((xe,             -ye,        z)),
        ]

    stations = []
    zs = [0.06, 0.14, 0.32, 0.58, 0.86, 1.16, 1.48, 1.76, 1.95, 2.05, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.162 - 0.092 * t) * (1.0 + (0.04 if i % 2 else 0.0))
        stations.append((z, {
            "x_spine": -0.048, "x_edge": -0.048 + width,
            "half_t": 0.036 * (1.0 - 0.60 * t) + 0.005,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_IronwoodSlab", col)
    rings, vs = make_rings(stations, slab_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    # 3 transverse iron storm bands (wrapping collars, shell region)
    for z0 in (0.46, 1.02, 1.56):
        rings, vs = [], []
        for i, z in enumerate([z0, z0 + 0.08]):
            t = z / 2.10
            xs = -0.048; xe = xs + (0.162 - 0.092 * t)
            ht = 0.036 * (1.0 - 0.60 * t) + 0.005 + 0.008
            rings.append(slab_section(z, {"x_spine": xs, "x_edge": xe, "half_t": ht}))
            vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell", cap_start=False, cap_end=False)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_StormBoltSeams", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(15):
            t = i / 14.0
            z = 0.24 + 1.66 * t
            zig = 0.012 * (1.0 if i % 2 == 0 else -1.0)
            pts.append((-0.048 + 0.080 + 0.030 * math.sin(t * 5.5), sy * (0.033 + zig), z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0035)
    commit(obj, bm)

    # Angular bolt quillons: Z-shaped, blued iron
    obj, bm, uv = new_mesh_obj("Guard_BoltQuillons", col)
    for side in (1.0, -1.0):
        path = [Vector((side * 0.05, 0.0, 0.10)), Vector((side * 0.16, 0.0, 0.10)),
                Vector((side * 0.16, 0.0, 0.02)), Vector((side * 0.26, 0.0, 0.02)),
                Vector((side * 0.26, 0.0, -0.06)), Vector((side * 0.34, 0.0, -0.06))]
        curved_loft(bm, uv, path, lambda t: 0.024 * (1.0 - 0.35 * math.sin(t * 3.0)) + 0.006, 8, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StormWrappedLeather", col)
    grip_braid(bm, uv, 0.055, -0.46, 13, 10, 0.030, 0.004, thick_every=2)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_GroundedIronCore", col)
    pts = []
    for i in range(11):
        t = i / 10.0
        z = 0.14 + 1.82 * t
        pts.append((-0.052, 0.0, z))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_StormAnvil", col)
    # hex prism anvil pommel
    rings, vs = [], []
    for i, (r, sw) in enumerate([(0.020, 1.0), (0.040, 1.25), (0.046, 1.45), (0.046, 1.45), (0.030, 1.2), (0.008, 1.0)]):
        z = -0.465 - 0.10 * (i / 5.0)
        ring = [Vector((math.cos(2 * math.pi * j / 6) * r, math.sin(2 * math.pi * j / 6) * r * sw, z)) for j in range(6)]
        rings.append(ring); vs.append(i / 5.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    pts = []
    for j in range(13):
        a = 2 * math.pi * j / 12
        pts.append((math.cos(a) * 0.047, math.sin(a) * 0.068, -0.515))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0045)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_StormIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.06), (-0.435, -0.465)], 0.036)
    commit(obj, bm)

# =============================================================================
# C. awakening_spirit_willow_saber - "Sable de Sauce Espiritual" (spiritual swift)
# =============================================================================
def build_willow(col):
    def saber_section(z, p):
        # 12-vert slim crescent: very swift, thin, keen
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0018
        return [
            Vector((xe,             ye,         z)),
            Vector((xs + 0.80 * w,  ht,         z)),
            Vector((xs + 0.55 * w,  ht * 0.60,  z)),
            Vector((xs + 0.28 * w,  ht * 0.92,  z)),
            Vector((xs + 0.10 * w,  ht * 0.45,  z)),
            Vector((xs,             ht * 0.12,  z)),
            Vector((xs,             -ht * 0.12, z)),
            Vector((xs + 0.10 * w,  -ht * 0.45, z)),
            Vector((xs + 0.28 * w,  -ht * 0.92, z)),
            Vector((xs + 0.55 * w,  -ht * 0.60, z)),
            Vector((xs + 0.80 * w,  -ht,        z)),
            Vector((xe,             -ye,        z)),
        ]

    def spine_x(z):
        return -0.045 + 0.30 * math.sin(max(0.0, z) / 2.08 * 0.85) * (z / 2.08)

    stations = []
    zs = [0.06, 0.13, 0.30, 0.55, 0.82, 1.12, 1.44, 1.72, 1.92, 2.03, 2.09]
    for i, z in enumerate(zs):
        t = z / 2.09
        width = (0.115 - 0.075 * t) * (1.0 + 0.05 * math.sin(t * 11.0))
        stations.append((z, {
            "x_spine": spine_x(z), "x_edge": spine_x(z) + width,
            "half_t": 0.018 * (1.0 - 0.62 * t) + 0.0025,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_WillowSaber", col)
    rings, vs = make_rings(stations, saber_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # 4 long drooping willow fronds from the spine (flair)
    obj, bm, uv = new_mesh_obj("Fronds_DroopingWillow", col)
    for bz, ln, droop in [(0.62, 0.42, 0.16), (1.02, 0.50, 0.22), (1.40, 0.44, 0.26), (1.72, 0.34, 0.30)]:
        sx = spine_x(bz)
        path = []
        for i in range(9):
            t = i / 8.0
            path.append(Vector((
                sx - 0.03 - 0.10 * t - droop * t * t,
                0.018 * math.sin(t * 6.0 + bz),
                bz + ln * t - droop * t * t * 1.6,
            )))
        curved_loft(bm, uv, path, lambda t: 0.014 * (1.0 - 0.75 * t) + 0.002, 7, "flair")
    commit(obj, bm)

    # Willow knot guard: flattened twisted disc
    obj, bm, uv = new_mesh_obj("Guard_WillowKnot", col)
    rings, vs = [], []
    for i, (rx, ry, z) in enumerate([(0.034, 0.030, 0.095), (0.075, 0.062, 0.070), (0.088, 0.070, 0.030), (0.075, 0.062, -0.010), (0.034, 0.030, -0.030)]):
        ring = [Vector((math.cos(2 * math.pi * j / 12) * rx, math.sin(2 * math.pi * j / 12) * ry, z + 0.012 * math.sin(2 * math.pi * j / 12 * 2))) for j in range(12)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_GhostWillowWrap", col)
    grip_braid(bm, uv, 0.055, -0.46, 11, 9, 0.028, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_EtherealSeam", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.24 + 1.55 * t
            pts.append((spine_x(z) + 0.045 + 0.025 * math.sin(t * 7.0), sy * 0.010, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_SpiritLantern", col)
    rings, vs = [], []
    for i, (r, sw) in enumerate([(0.010, 1.0), (0.024, 1.35), (0.030, 1.55), (0.024, 1.35), (0.010, 1.0)]):
        z = 0.20 + 0.017 * i
        ring = [Vector((0.015 + math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r * sw, z)) for j in range(8)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_HangingBell", col)
    rings, vs = [], []
    for i, r in enumerate([0.014, 0.030, 0.038, 0.042, 0.044]):
        z = -0.465 - 0.085 * (i / 4.0)
        ring = [Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    pts = []
    for j in range(17):
        a = 2 * math.pi * j / 16
        pts.append((math.cos(a) * 0.045, math.sin(a) * 0.045, -0.542))
    strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_Silvermist", col)
    ferrule_pair(bm, uv, [(0.02, 0.06), (-0.435, -0.465)], 0.034)
    commit(obj, bm)

# =============================================================================
# D. awakening_bloodsap_bramble_blade - "Hoja de Zarza Sanguina" (cursed swift)
# =============================================================================
def build_bramble(col):
    def rapier_section(z, p):
        # 12-vert narrow twisted blade
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0018
        sec = [
            Vector((xe,             ye,         0.0)),
            Vector((xs + 0.82 * w,  ht,         0.0)),
            Vector((xs + 0.58 * w,  ht * 0.55,  0.0)),
            Vector((xs + 0.30 * w,  ht * 0.95,  0.0)),
            Vector((xs + 0.10 * w,  ht * 0.42,  0.0)),
            Vector((xs,             ht * 0.10,  0.0)),
            Vector((xs,             -ht * 0.10, 0.0)),
            Vector((xs + 0.10 * w,  -ht * 0.42, 0.0)),
            Vector((xs + 0.30 * w,  -ht * 0.95, 0.0)),
            Vector((xs + 0.58 * w,  -ht * 0.55, 0.0)),
            Vector((xs + 0.82 * w,  -ht,        0.0)),
            Vector((xe,             -ye,        0.0)),
        ]
        th = p.get("twist", 0.0)
        if abs(th) > 1e-5:
            cx = (xs + xe) * 0.5
            out = []
            for v in sec:
                dx = v.x - cx
                out.append(Vector((cx + dx * math.cos(th) - v.y * math.sin(th), dx * math.sin(th) + v.y * math.cos(th), 0.0)))
            sec = out
        return [Vector((v.x, v.y, z)) for v in sec]

    stations = []
    zs = [0.06, 0.13, 0.30, 0.55, 0.82, 1.12, 1.44, 1.72, 1.92, 2.03, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.125 - 0.078 * t)
        stations.append((z, {
            "x_spine": -0.046, "x_edge": -0.046 + width,
            "half_t": 0.020 * (1.0 - 0.60 * t) + 0.003,
            "twist": t * 1.15,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_BrambleRapier", col)
    rings, vs = make_rings(stations, rapier_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # 5 backward-hooked drinking thorns (flair)
    obj, bm, uv = new_mesh_obj("Thorns_DrinkingThorns", col)
    for bz, ln in [(0.48, 0.16), (0.86, 0.20), (1.24, 0.18), (1.60, 0.14), (1.90, 0.10)]:
        t0 = bz / 2.10
        sx = -0.046 + (0.125 - 0.078 * t0) * 0.25
        path = []
        for i in range(6):
            tt = i / 5.0
            path.append(Vector((
                sx + 0.06 * tt - 0.075 * tt * tt,
                0.02 * math.sin(tt * 5.0 + bz),
                bz + ln * tt - 0.10 * tt * tt,
            )))
        curved_loft(bm, uv, path, lambda t: 0.013 * (1.0 - t) + 0.002, 7, "flair")
    commit(obj, bm)

    # Bramble tangle guard: 2 interlocked loops
    obj, bm, uv = new_mesh_obj("Guard_BrambleTangle", col)
    for k, (ph, tilt) in enumerate([(0.0, 0.35), (2.1, -0.30)]):
        pts = []
        for i in range(13):
            a = 2 * math.pi * i / 12 + ph
            pts.append(Vector((math.cos(a) * 0.105, math.sin(a) * 0.030 + 0.02 * math.sin(a * 3), 0.03 + math.sin(a + ph) * 0.030)))
        curved_loft(bm, uv, pts, lambda t: 0.016 * (1.0 - 0.25 * math.sin(t * 6.0)) + 0.004, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_BloodbarkWrap", col)
    grip_braid(bm, uv, 0.055, -0.46, 12, 9, 0.028, 0.006, thick_every=2)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_BloodSapDrips", col)
    for sy, z0, z1 in ((1.0, 0.26, 1.60), (-1.0, 0.40, 1.45)):
        pts = []
        n = 12
        for i in range(n):
            t = i / (n - 1.0)
            z = z0 + (z1 - z0) * t
            pts.append((-0.046 + 0.050 + 0.020 * math.sin(t * 8.0), sy * (0.012 if i % 2 == 0 else 0.005), z))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_BleedingHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.020, 0.024), (0.027, 0.042), (0.018, 0.056), (0.008, 0.062)]):
        z = 0.17 + h2
        ring = [Vector((0.014 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_ThornBud", col)
    bulb_pommel(bm, uv, -0.465, [0.014, 0.032, 0.040, 0.035, 0.020, 0.005], 9, squash=1.15, drop=0.10, ring_r=0.041, ring_z=-0.512)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BloodIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.06), (-0.435, -0.465)], 0.034)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "amber": {
        "name": "sword_03_amber_sanctuary", "builder": build_amber, "tex": "amber_sanctuary",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "amber_sanctuary"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage03_swords", "amber_sanctuary"),
    },
    "ironwood": {
        "name": "sword_03_ironwood_storm", "builder": build_ironwood, "tex": "ironwood_storm",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "ironwood_storm"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage03_swords", "ironwood_storm"),
    },
    "willow": {
        "name": "sword_03_spirit_willow", "builder": build_willow, "tex": "spirit_willow",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "spirit_willow"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage03_swords", "spirit_willow"),
    },
    "bramble": {
        "name": "sword_03_bramble_blade", "builder": build_bramble, "tex": "bloodsap_bramble",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "bloodsap_bramble"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage03_swords", "bloodsap_bramble"),
    },
}

def make_atlas_material(mat_name, tex_dir, tex_base):
    m = bpy.data.materials.new(mat_name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]

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
    return m

def main():
    argv = sys.argv
    sword = "amber"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_03_Root", None)
    col.objects.link(sword_root)
    parts = [o for o in col.objects if o.type == "MESH"]
    for o in parts:
        o.parent = sword_root

    zmin, zmax = 1e9, -1e9
    for o in parts:
        for v in o.data.vertices:
            zmin = min(zmin, v.co.z); zmax = max(zmax, v.co.z)
    s = 2.60 / max(1e-4, (zmax - zmin))
    sword_root.scale = (s, s, s)
    bpy.context.view_layer.update()

    mat = make_atlas_material("MAT_%s" % meta["tex"], meta["out_dir"], meta["tex"])
    for o in parts:
        o.data.materials.append(mat)
    for o in parts:
        for p in o.data.polygons:
            p.use_smooth = True

    os.makedirs(meta["out_dir"], exist_ok=True)
    os.makedirs(meta["art_dir"], exist_ok=True)

    tris = sum(len(p.vertices) - 2 for o in parts for p in o.data.polygons)
    verts = sum(len(o.data.vertices) for o in parts)
    print("BUILT %s parts=%d verts=%d tris=%d scale=%.4f" % (meta["name"], len(parts), verts, tris, s))

    blend_path = os.path.join(meta["art_dir"], "%s.blend" % meta["name"])
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    glb_path = os.path.join(meta["out_dir"], "%s.glb" % meta["name"])
    bpy.ops.export_scene.gltf(filepath=glb_path, use_selection=False, export_format="GLB")
    print("GLB_SAVED", glb_path)
    print("BLEND_SAVED", blend_path)
    print("STAGE03_BUILD_DONE", sword)

main()

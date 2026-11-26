# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 07: CINCO espadas bespoke (anime exagerado por linaje)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage07_swords.py -- sword=seraph|chitin|magma|lotus|aether
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
# A. blessed_seraph_wing_longsword - "Espada Larga Ala de Serafin" (blessed)
# =============================================================================
def build_seraph(col):
    def seraph_section(z, p):
        # 14-vert radiant longsword
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0026
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.60 * w,  ht * 0.70, z)),
            Vector((xs + 0.36 * w,  ht * 0.98, z)),
            Vector((xs + 0.15 * w,  ht * 0.62, z)),
            Vector((xs + 0.05 * w,  ht * 0.26, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.26,z)),
            Vector((xs + 0.15 * w,  -ht * 0.62,z)),
            Vector((xs + 0.36 * w,  -ht * 0.98,z)),
            Vector((xs + 0.60 * w,  -ht * 0.70,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.44, 0.72, 1.00, 1.28, 1.54, 1.78, 1.98, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.140 - 0.082 * t) * (0.40 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + width,
            "half_t": 0.022 * (1.0 - 0.52 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_SeraphWingLongsword", col)
    rings, vs = make_rings(stations, seraph_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Radiant plume down each flat
    obj, bm, uv = new_mesh_obj("Plume_RadiantPlume", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.36 + 1.32 * t
            pts.append((-0.050 + 0.070 + 0.012 * math.sin(t * 7.0), sy * 0.020, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.007, half_t=0.0035)
    commit(obj, bm)

    # Seraph wings: 3 feather layers x 2 sides
    obj, bm, uv = new_mesh_obj("Feathers_SeraphWings", col)
    for side in (1.0, -1.0):
        for layer in range(3):
            zo = 0.070 - 0.020 * layer
            spread = 0.170 - 0.038 * layer
            lift = 0.060 + 0.024 * layer
            path = [Vector((side * 0.034, 0.006, zo + 0.030)),
                    Vector((side * (0.055 + 0.35 * spread), 0.012, zo + 0.030 + 0.35 * lift)),
                    Vector((side * (0.055 + 0.72 * spread), 0.014, zo + 0.030 + 0.72 * lift)),
                    Vector((side * (0.055 + spread), 0.010, zo + 0.030 + lift))]
            curved_loft(bm, uv, path, lambda t: 0.013 * (1.0 - 0.75 * t) + 0.003, 7, "flair")
    commit(obj, bm)

    # Halo ring floating above the wings
    obj, bm, uv = new_mesh_obj("Halo_SeraphRing", col)
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append((math.cos(a) * 0.072, math.sin(a) * 0.072 * 0.35, 0.170))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_SeraphHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.022, 0.023), (0.030, 0.041), (0.020, 0.055), (0.009, 0.060)]):
        z = 0.19 + h2
        ring = [Vector((0.021 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SeraphSilkHilt", col)
    grip_braid(bm, uv, 0.055, -0.45, 11, 9, 0.029, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SeraphOrb", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.031, 0.040, 0.034, 0.019, 0.006], 9, squash=1.0, drop=0.095, ring_r=0.039, ring_z=-0.496)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_SeraphGold", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.418, -0.448)], 0.034)
    commit(obj, bm)

# =============================================================================
# B. cursed_nightmare_chitin_sword - "Espada Quitina de Pesadilla" (cursed swift)
# =============================================================================
def build_chitin(col):
    def chitin_section(z, p):
        # 12-vert segmented chitin blade with sawtooth belly
        xs, xe = p["x_spine"], p["x_edge"]
        saw = p.get("saw", 0.0)
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe - saw,       ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.54 * w,  ht * 0.62, z)),
            Vector((xs + 0.28 * w,  ht * 0.98, z)),
            Vector((xs + 0.10 * w,  ht * 0.54, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.10 * w,  -ht * 0.54,z)),
            Vector((xs + 0.28 * w,  -ht * 0.98,z)),
            Vector((xs + 0.54 * w,  -ht * 0.62,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe - saw,       -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.20, 0.44, 0.68, 0.92, 1.16, 1.40, 1.62, 1.82, 1.96, 2.04]
    for i, z in enumerate(zs):
        t = z / 2.04
        stations.append((z, {
            "x_spine": -0.048, "x_edge": -0.048 + (0.128 - 0.070 * t),
            "half_t": (0.020 * (1.0 - 0.45 * t) + 0.003) * (1.10 if i % 2 == 0 else 1.0),
            "v": t, "saw": (0.018 if i % 2 == 1 and i >= 3 else 0.004),
        }))

    obj, bm, uv = new_mesh_obj("Blade_NightmareChitinSword", col)
    rings, vs = make_rings(stations, chitin_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Venom ducts along the flats
    obj, bm, uv = new_mesh_obj("Inlay_VenomDucts", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.24 * t
            pts.append((-0.048 + 0.056 + 0.010 * math.sin(t * 11.0), sy * 0.016, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Leg barbs x3 pairs off the spine
    obj, bm, uv = new_mesh_obj("Barbs_LegBarbs", col)
    for k in range(3):
        t = 0.16 + 0.22 * k
        z = 0.44 + 1.02 * t
        off = -0.075 * 0.0
        sy = 1.0 if k % 2 == 0 else -1.0
        path = [Vector((-0.048 + 0.004, sy * 0.004, z)), Vector((-0.048 - 0.016, sy * 0.024, z + 0.014)),
                Vector((-0.048 - 0.026, sy * 0.036, z + 0.040))]
        curved_loft(bm, uv, path, lambda tt: 0.007 * (1.0 - tt) + 0.002, 6, "flair")
    commit(obj, bm)

    # Mandible guard: 2 curved jaws
    obj, bm, uv = new_mesh_obj("Guard_ChitinMandibles", col)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.030, 0.004, 0.098)), Vector((sx * 0.095, 0.014, 0.075)),
                Vector((sx * 0.150, 0.008, 0.082)), Vector((sx * 0.180, -0.006, 0.108))]
        curved_loft(bm, uv, path, lambda t: 0.014 * (1.0 - 0.5 * t) + 0.004, 8, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_VenomSac", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.024, 0.025), (0.032, 0.044), (0.022, 0.058), (0.010, 0.064)]):
        z = 0.20 + h2
        ring = [Vector((0.016 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ChitinRingWrap", col)
    grip_braid(bm, uv, 0.055, -0.44, 12, 9, 0.028, 0.005, thick_every=1, thick=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_ChitinStinger", col)
    bulb_pommel(bm, uv, -0.440, [0.013, 0.030, 0.038, 0.032, 0.018, 0.005], 9, squash=1.2, drop=0.095, ring_r=0.037, ring_z=-0.486)
    path = [Vector((0.0, 0.0, -0.486)), Vector((0.0, 0.0, -0.545)), Vector((0.006, 0.0, -0.600))]
    curved_loft(bm, uv, path, lambda t: 0.007 * (1.0 - t) + 0.0015, 6, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_AbyssIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.408, -0.438)], 0.033)
    commit(obj, bm)

# =============================================================================
# C. elemental_magma_vein_broadsword - "Espada Ancha Vena de Magma" (elemental)
# =============================================================================
def build_magma(col):
    def magma_section(z, p):
        # 14-vert broad basalt blade, chunky bevels
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.86 * w,  ht,        z)),
            Vector((xs + 0.64 * w,  ht * 0.72, z)),
            Vector((xs + 0.38 * w,  ht,        z)),
            Vector((xs + 0.16 * w,  ht * 0.66, z)),
            Vector((xs + 0.05 * w,  ht * 0.28, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.28,z)),
            Vector((xs + 0.16 * w,  -ht * 0.66,z)),
            Vector((xs + 0.38 * w,  -ht,       z)),
            Vector((xs + 0.64 * w,  -ht * 0.72,z)),
            Vector((xs + 0.86 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.16, 0.38, 0.64, 0.92, 1.20, 1.46, 1.70, 1.90, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        width = (0.180 - 0.090 * t) * (0.52 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.058, "x_edge": -0.058 + width,
            "half_t": 0.028 * (1.0 - 0.48 * t) + 0.004,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_MagmaVeinBroadsword", col)
    rings, vs = make_rings(stations, magma_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Magma cracks: 2 wavy glow strips per flat
    obj, bm, uv = new_mesh_obj("Inlay_MagmaCracks", col)
    for sy in (1.0, -1.0):
        for k, zo in enumerate([0.048, 0.092]):
            pts = []
            for i in range(13):
                t = i / 12.0
                z = 0.34 + 1.22 * t
                pts.append((-0.058 + 0.070 + 0.026 * math.sin(t * 9.0 + k * 2.0), sy * (0.020 if k == 0 else 0.024), z))
            strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0038)
    commit(obj, bm)

    # Basalt slab guard: 2 rough slabs + 1 spike
    obj, bm, uv = new_mesh_obj("Guard_BasaltSlabs", col)
    for sx in (1.0, -1.0):
        rings, vs = [], []
        for i, z in enumerate([0.048, 0.094]):
            lean = 0.016 * i
            rings.append([Vector((sx * 0.028 + lean, -0.034, z)), Vector((sx * 0.130 + lean, -0.024, z)),
                          Vector((sx * 0.130 + lean, 0.024, z)), Vector((sx * 0.028 + lean, 0.034, z))])
            vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    pts = [(0.0, -0.040, z) for z in [0.048 + 0.058 * (i / 4.0) for i in range(5)]]
    strip_loft(bm, uv, pts, "flair", half_w=0.009, half_t=0.010)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_MagmaHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.025, 0.026), (0.034, 0.046), (0.023, 0.060), (0.010, 0.066)]):
        z = 0.19 + h2
        ring = [Vector((0.022 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_LavaWrappedHilt", col)
    grip_braid(bm, uv, 0.052, -0.45, 11, 9, 0.031, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_VolcanicBomb", col)
    bulb_pommel(bm, uv, -0.450, [0.016, 0.036, 0.046, 0.040, 0.023, 0.007], 9, squash=1.05, drop=0.10, ring_r=0.046, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_CoolBasalt", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.418, -0.448)], 0.037)
    commit(obj, bm)

# =============================================================================
# D. spiritual_moonlit_lotus_blade - "Hoja Loto de Plenilunio" (spiritual swift)
# =============================================================================
def build_lotus(col):
    def lotus_section(z, p):
        # 12-vert petal blade with lotus ripple
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.78 * w,  ht * 0.82, z)),
            Vector((xs + 0.52 * w,  ht,        z)),
            Vector((xs + 0.28 * w,  ht * 0.74, z)),
            Vector((xs + 0.10 * w,  ht * 0.38, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.10 * w,  -ht * 0.38,z)),
            Vector((xs + 0.28 * w,  -ht * 0.74,z)),
            Vector((xs + 0.52 * w,  -ht,       z)),
            Vector((xs + 0.78 * w,  -ht * 0.82,z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.05, 0.18, 0.42, 0.68, 0.94, 1.20, 1.44, 1.68, 1.90, 2.02]
    for i, z in enumerate(zs):
        t = z / 2.02
        ripple = 1.0 + 0.10 * math.sin(t * 11.0)
        width = (0.105 - 0.068 * t) * ripple * (0.46 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.045, "x_edge": -0.045 + width,
            "half_t": 0.017 * (1.0 - 0.42 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_MoonlitLotusBlade", col)
    rings, vs = make_rings(stations, lotus_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Lotus petals layered on the flats
    obj, bm, uv = new_mesh_obj("Petals_LotusPetals", col)
    for sy in (1.0, -1.0):
        for k, (za, zb, xo, amp) in enumerate([(0.44, 0.78, 0.050, 0.008), (0.86, 1.20, 0.058, 0.008), (1.28, 1.58, 0.050, 0.007)]):
            pts = []
            for i in range(7):
                t = i / 6.0
                z = za + (zb - za) * t
                pts.append((-0.045 + xo + amp * math.sin(t * math.pi), sy * 0.014, z))
            strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.003)
    commit(obj, bm)

    # Full moon disc behind the guard
    obj, bm, uv = new_mesh_obj("Disc_FullMoon", col)
    rings, vs = [], []
    for i, z in enumerate([0.060, 0.076]):
        ring = [Vector((math.cos(2 * math.pi * j / 18) * 0.086, math.sin(2 * math.pi * j / 18) * 0.086 * 0.78, z)) for j in range(18)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append((math.cos(a) * 0.052, math.sin(a) * 0.052 * 0.78, 0.092))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Astral dew drops x3
    obj, bm, uv = new_mesh_obj("Dew_AstralDrops", col)
    for k, (zo, xo) in enumerate([(0.78, 0.052), (1.14, 0.044), (1.48, 0.036)]):
        rings, vs = [], []
        for i, rr in enumerate([0.0035, 0.0075, 0.0090, 0.0060, 0.0015]):
            ring = [Vector((-0.045 + xo + math.cos(2 * math.pi * j / 8) * rr, 0.018 + math.sin(2 * math.pi * j / 8) * rr * 0.8, zo + rr * 0.6)) for j in range(8)]
            rings.append(ring); vs.append(i / 4.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_LotusSeed", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.020, 0.022), (0.028, 0.040), (0.019, 0.053), (0.008, 0.058)]):
        z = 0.16 + h2
        ring = [Vector((0.015 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_LotusStemWrap", col)
    grip_braid(bm, uv, 0.048, -0.40, 11, 9, 0.026, 0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_LotusBud", col)
    bulb_pommel(bm, uv, -0.400, [0.012, 0.026, 0.033, 0.027, 0.015, 0.005], 9, squash=0.95, drop=0.08, ring_r=0.032, ring_z=-0.442)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_MoonSilver", col)
    ferrule_pair(bm, uv, [(0.02, 0.048), (-0.368, -0.398)], 0.030)
    commit(obj, bm)

# =============================================================================
# E. arcane_aether_conduit_rapier - "Estoque Conducto de Eter" (arcane mystic)
# =============================================================================
def build_aether(col):
    def aether_section(z, p):
        # 12-vert ultra-slim rapier, longest reach of the batch
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0020
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.78 * w,  ht,        z)),
            Vector((xs + 0.52 * w,  ht * 0.60, z)),
            Vector((xs + 0.28 * w,  ht * 0.95, z)),
            Vector((xs + 0.10 * w,  ht * 0.50, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.10 * w,  -ht * 0.50,z)),
            Vector((xs + 0.28 * w,  -ht * 0.95,z)),
            Vector((xs + 0.52 * w,  -ht * 0.60,z)),
            Vector((xs + 0.78 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.24, 0.52, 0.82, 1.12, 1.42, 1.70, 1.96, 2.16, 2.28]
    for i, z in enumerate(zs):
        t = z / 2.28
        width = (0.088 - 0.058 * t) * (0.42 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.038, "x_edge": -0.038 + width,
            "half_t": 0.014 * (1.0 - 0.42 * t) + 0.002,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_AetherConduitRapier", col)
    rings, vs = make_rings(stations, aether_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Aether canals: 2 full-length glow tubes
    obj, bm, uv = new_mesh_obj("Inlay_AetherCanals", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(15):
            t = i / 14.0
            z = 0.16 + 1.96 * t
            pts.append((-0.038 + 0.040 + 0.006 * math.sin(t * 8.0), sy * 0.010, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0028)
    commit(obj, bm)

    # Ring conduits x3 around the blade
    obj, bm, uv = new_mesh_obj("Conduits_RingConduits", col)
    for zo, rr in [(0.62, 0.016), (1.14, 0.014), (1.66, 0.012)]:
        rings, vs = [], []
        for i, z in enumerate([zo - 0.008, zo + 0.008]):
            ring = [Vector((-0.038 + 0.036 + math.cos(2 * math.pi * j / 12) * rr, math.sin(2 * math.pi * j / 12) * rr * 1.8, z)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    # Aether swirl guard: ring + 2 vortex arms + mana channel core
    obj, bm, uv = new_mesh_obj("Guard_AetherSwirlGuard", col)
    rings, vs = [], []
    for i, z in enumerate([0.044, 0.078]):
        ring = [Vector((math.cos(2 * math.pi * j / 16) * 0.068, math.sin(2 * math.pi * j / 16) * 0.068 * 0.52, z)) for j in range(16)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.066, 0.0, 0.061)), Vector((sx * 0.098, 0.0, 0.040)),
                Vector((sx * 0.104, 0.0, 0.070)), Vector((sx * 0.080, 0.0, 0.092))]
        curved_loft(bm, uv, path, lambda t: 0.009 * (1.0 - 0.5 * t) + 0.003, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_ManaChannel", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.007, 0.005), (0.018, 0.021), (0.025, 0.038), (0.017, 0.051), (0.007, 0.056)]):
        z = 0.14 + h2
        ring = [Vector((0.013 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_EtchedWireWrap", col)
    grip_braid(bm, uv, 0.044, -0.40, 12, 9, 0.024, 0.004, thick_every=1, thick=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AetherVial", col)
    bulb_pommel(bm, uv, -0.400, [0.011, 0.025, 0.032, 0.026, 0.015, 0.005], 9, squash=1.0, drop=0.08, ring_r=0.031, ring_z=-0.442)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_AetherBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.044), (-0.368, -0.398)], 0.028)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "seraph": {
        "name": "sword_07_seraph_wing", "builder": build_seraph, "tex": "seraph_wing",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "seraph_wing"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage07_swords", "seraph_wing"),
    },
    "chitin": {
        "name": "sword_07_nightmare_chitin", "builder": build_chitin, "tex": "nightmare_chitin",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "nightmare_chitin"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage07_swords", "nightmare_chitin"),
    },
    "magma": {
        "name": "sword_07_magma_vein", "builder": build_magma, "tex": "magma_vein",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "magma_vein"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage07_swords", "magma_vein"),
    },
    "lotus": {
        "name": "sword_07_moonlit_lotus", "builder": build_lotus, "tex": "moonlit_lotus",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "moonlit_lotus"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage07_swords", "moonlit_lotus"),
    },
    "aether": {
        "name": "sword_07_aether_conduit", "builder": build_aether, "tex": "aether_conduit",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "aether_conduit"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage07_swords", "aether_conduit"),
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
    sword = "seraph"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_07_Root", None)
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
    print("STAGE07_BUILD_DONE", sword)

main()

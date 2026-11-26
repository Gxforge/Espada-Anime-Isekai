# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 05: CINCO espadas bespoke (anime exagerado por linaje)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage05_swords.py -- sword=solarinit|obsidianfang|coppertempest|silveranima|crystalcipher
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
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.0045)# =============================================================================
# A. blessed_solar_initiate_blade - "Espada Iniciada del Sol Naciente" (blessed)
# =============================================================================
def build_solarinit(col):
    def init_section(z, p):
        # 14-vert slim elegant taper (solar rapier-longsword hybrid)
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.60 * w,  ht * 0.68, z)),
            Vector((xs + 0.36 * w,  ht * 0.98, z)),
            Vector((xs + 0.15 * w,  ht * 0.62, z)),
            Vector((xs + 0.05 * w,  ht * 0.26, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.26,z)),
            Vector((xs + 0.15 * w,  -ht * 0.62,z)),
            Vector((xs + 0.36 * w,  -ht * 0.98,z)),
            Vector((xs + 0.60 * w,  -ht * 0.68,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.16, 0.40, 0.68, 0.98, 1.28, 1.56, 1.80, 1.98, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.135 - 0.090 * t) * (0.42 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.048, "x_edge": -0.048 + width,
            "half_t": 0.024 * (1.0 - 0.58 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_SolarInitiateLongsword", col)
    rings, vs = make_rings(stations, init_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_SunPrickLines", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.34 + 1.28 * t
            pts.append((-0.048 + 0.066 + 0.014 * math.sin(t * 8.0), sy * 0.020, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Sun crown guard: ring + 8 ray pickets
    obj, bm, uv = new_mesh_obj("Guard_SunCrownRing", col)
    rings, vs = [], []
    for i, z in enumerate([0.052, 0.092]):
        ring = [Vector((math.cos(2 * math.pi * j / 16) * 0.070, math.sin(2 * math.pi * j / 16) * 0.070 * 0.55, z)) for j in range(16)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for k in range(8):
        a = 2 * math.pi * k / 8.0
        path = [Vector((math.cos(a) * 0.072, math.sin(a) * 0.072 * 0.55, 0.072)),
                Vector((math.cos(a) * 0.118, math.sin(a) * 0.118 * 0.55, 0.072 + 0.008 * (1 if k % 2 == 0 else -1)))]
        curved_loft(bm, uv, path, lambda t: 0.009 * (1.0 - t) + 0.003, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_SolarSeed", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.020, 0.022), (0.027, 0.040), (0.018, 0.054), (0.008, 0.059)]):
        z = 0.18 + h2
        ring = [Vector((0.020 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SunSilkBraid", col)
    grip_braid(bm, uv, 0.055, -0.45, 11, 9, 0.029, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SunCrownBulb", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.031, 0.040, 0.034, 0.019, 0.006], 9, squash=1.0, drop=0.095, ring_r=0.039, ring_z=-0.496)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BronzeSun", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.418, -0.448)], 0.034)
    commit(obj, bm)

# =============================================================================
# B. cursed_obsidian_fang_blade - "Espada Colmillo de Obsidiana" (cursed)
# =============================================================================
def build_obsidianfang(col):
    def fang_section(z, p):
        # 12-vert glassy fang: curved, deep belly, sharp tip
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.78 * w,  ht,        z)),
            Vector((xs + 0.52 * w,  ht * 0.62, z)),
            Vector((xs + 0.28 * w,  ht * 0.96, z)),
            Vector((xs + 0.10 * w,  ht * 0.55, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.10 * w,  -ht * 0.55,z)),
            Vector((xs + 0.28 * w,  -ht * 0.96,z)),
            Vector((xs + 0.52 * w,  -ht * 0.62,z)),
            Vector((xs + 0.78 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.42, 0.66, 0.90, 1.14, 1.38, 1.60, 1.80, 1.96, 2.04]
    offs = []
    for i, z in enumerate(zs):
        t = z / 2.04
        off = -0.075 * (t ** 1.7)
        width = (0.120 - 0.080 * t)
        if i == len(zs) - 1:
            width *= 0.42
        elif i == len(zs) - 2:
            width *= 0.78
        xs = -0.046 + off
        offs.append(xs + width)
        stations.append((z, {"x_spine": xs, "x_edge": xs + width,
                             "half_t": (0.021 * (1.0 - 0.45 * t) + 0.003) * (1.12 if i % 2 else 1.0), "v": t}))

    def xe_at(z):
        for k in range(len(zs) - 1):
            if zs[k] <= z <= zs[k + 1]:
                t = (z - zs[k]) / (zs[k + 1] - zs[k])
                return offs[k] + (offs[k + 1] - offs[k]) * t
        return offs[-1]

    obj, bm, uv = new_mesh_obj("Blade_ObsidianFangSaber", col)
    rings, vs = make_rings(stations, fang_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_BloodFangVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.26 * t
            pts.append((xe_at(z) - 0.034 + 0.008 * math.sin(t * 10.0), sy * 0.016, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Glass chips jutting from the spine
    obj, bm, uv = new_mesh_obj("Chip_GlassShards", col)
    for k in range(4):
        t = 0.18 + 0.20 * k
        z = 0.42 + 1.10 * t
        xs = -0.046 - 0.075 * (t ** 1.7)
        sy = 1.0 if k % 2 == 0 else -1.0
        path = [Vector((xs + 0.004, sy * 0.004, z)), Vector((xs + 0.010, sy * 0.024, z + 0.020)),
                Vector((xs + 0.016, sy * 0.034, z + 0.048))]
        curved_loft(bm, uv, path, lambda tt: 0.008 * (1.0 - tt) + 0.002, 6, "flair")
    commit(obj, bm)

    # Fang jaw guard: 2 bars sweeping up like fangs
    obj, bm, uv = new_mesh_obj("Guard_FangJawBars", col)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.030, 0.0, 0.095)), Vector((sx * 0.055, 0.0, 0.200)),
                Vector((sx * 0.062, 0.0, 0.300)), Vector((sx * 0.046, 0.0, 0.380))]
        curved_loft(bm, uv, path, lambda tt: 0.013 * (1.0 - 0.55 * tt) + 0.004, 8, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_VoidHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.021, 0.022), (0.028, 0.040), (0.018, 0.053), (0.008, 0.058)]):
        z = 0.19 + h2
        ring = [Vector((0.015 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_VoidLeatherHilt", col)
    grip_braid(bm, uv, 0.055, -0.44, 12, 9, 0.028, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_FangTalon", col)
    bulb_pommel(bm, uv, -0.440, [0.013, 0.030, 0.038, 0.032, 0.018, 0.005], 9, squash=1.18, drop=0.095, ring_r=0.037, ring_z=-0.486)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_VoidIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.408, -0.438)], 0.033)
    commit(obj, bm)

# =============================================================================
# C. elemental_tempest_copper_blade - "Espada Cobriza de Tempestad" (elemental)
# =============================================================================
def build_coppertempest(col):
    def tempest_section(z, p):
        # 12-vert blade rotated by a cyclone twist with ripple width
        xs, xe = p["x_spine"], p["x_edge"]
        rot = p["rot"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        cx = xs + 0.35 * w
        pts = [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.55 * w,  ht * 0.62, z)),
            Vector((xs + 0.28 * w,  ht * 0.96, z)),
            Vector((xs + 0.10 * w,  ht * 0.55, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.10 * w,  -ht * 0.55,z)),
            Vector((xs + 0.28 * w,  -ht * 0.96,z)),
            Vector((xs + 0.55 * w,  -ht * 0.62,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]
        out = []
        for q in pts:
            dx, dy = q.x - cx, q.y
            out.append(Vector((cx + dx * math.cos(rot) - dy * math.sin(rot),
                               dy * math.cos(rot) + dx * math.sin(rot), z)))
        return out

    stations = []
    zs = [0.06, 0.22, 0.46, 0.72, 0.98, 1.24, 1.50, 1.74, 1.94, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        ripple = 1.0 + 0.06 * math.sin(t * 14.0)
        width = (0.130 - 0.072 * t) * ripple
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + width,
            "half_t": 0.020 * (1.0 - 0.5 * t) + 0.003,
            "rot": t * 2.4, "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_CopperTempestTwist", col)
    rings, vs = make_rings(stations, tempest_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    def rot_xy(x0, y0, z):
        t = z / 2.08
        r = t * 2.4
        cx = -0.050 + 0.35 * (0.130 - 0.072 * t)
        dx, dy = x0 - cx, y0
        return (cx + dx * math.cos(r) - dy * math.sin(r), dy * math.cos(r) + dx * math.sin(r))

    obj, bm, uv = new_mesh_obj("Inlay_CycloneGrooves", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.32 * t
            xr, yr = rot_xy(-0.050 + 0.060 + 0.010 * math.sin(t * 12.0), sy * 0.018, z)
            pts.append((xr, yr, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Patina ribs spiraling along the blade
    obj, bm, uv = new_mesh_obj("Spiral_PatinaRibs", col)
    for k in range(3):
        base_a = 2 * math.pi * k / 3.0
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.24 + 1.36 * t
            a = base_a + t * 2.4
            rr = 0.020 + 0.004 * math.sin(t * 9.0)
            xr, yr = rot_xy(-0.050 + 0.045, 0.0, z)
            pts.append((xr + math.cos(a) * 0.006, yr + math.sin(a) * rr, z))
        strip_loft(bm, uv, pts, "flair", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Storm swirl guard: ring + 2 hooks
    obj, bm, uv = new_mesh_obj("Guard_StormSwirlRing", col)
    rings, vs = [], []
    for i, z in enumerate([0.050, 0.090]):
        ring = [Vector((math.cos(2 * math.pi * j / 16) * 0.072, math.sin(2 * math.pi * j / 16) * 0.072 * 0.75, z)) for j in range(16)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.070, 0.0, 0.070)), Vector((sx * 0.105, 0.0, 0.045)),
                Vector((sx * 0.118, 0.0, 0.075)), Vector((sx * 0.098, 0.0, 0.100))]
        curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - 0.5 * t) + 0.003, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_CycloneEye", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.020, 0.022), (0.027, 0.040), (0.018, 0.053), (0.008, 0.058)]):
        z = 0.18 + h2
        ring = [Vector((0.018 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StormCopperWire", col)
    grip_braid(bm, uv, 0.055, -0.45, 12, 9, 0.028, 0.004, thick_every=1, thick=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_VortexCoil", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.031, 0.040, 0.033, 0.018, 0.005], 9, squash=1.0, drop=0.10, ring_r=0.040, ring_z=-0.498)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_VerdigrisBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.418, -0.448)], 0.034)
    commit(obj, bm)

# =============================================================================
# D. spiritual_silver_anima_saber - "Sable de Plata Anima" (spiritual)
# =============================================================================
def build_silveranima(col):
    def saber_section(z, p):
        # 12-vert curved cavalry saber, wide gentle arc
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.75 * w,  ht * 0.85, z)),
            Vector((xs + 0.50 * w,  ht,        z)),
            Vector((xs + 0.26 * w,  ht * 0.75, z)),
            Vector((xs + 0.09 * w,  ht * 0.38, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.14,z)),
            Vector((xs + 0.09 * w,  -ht * 0.44,z)),
            Vector((xs + 0.26 * w,  -ht * 0.88,z)),
            Vector((xs + 0.50 * w,  -ht,       z)),
            Vector((xs + 0.75 * w,  -ht * 0.82,z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.05, 0.20, 0.46, 0.74, 1.02, 1.30, 1.56, 1.80, 1.98, 2.08]
    offs = []
    for i, z in enumerate(zs):
        t = z / 2.08
        off = -0.065 * (t ** 1.6)
        width = (0.088 - 0.038 * t) * (0.58 if i == len(zs) - 1 else 1.0)
        xs = -0.024 + off
        offs.append(xs + width)
        stations.append((z, {"x_spine": xs, "x_edge": xs + width,
                             "half_t": 0.011 * (1.0 - 0.38 * t) + 0.002, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_SilverAnimaSaber", col)
    rings, vs = make_rings(stations, saber_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_AnimaWispLines", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.24 + 1.42 * t
            off = -0.065 * ((z / 2.08) ** 1.6)
            pts.append((-0.024 + off + 0.036 + 0.006 * math.sin(t * 11.0), sy * 0.011, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.003)
    commit(obj, bm)

    # Saber guard: knuckle bow + disc
    obj, bm, uv = new_mesh_obj("Guard_AnimaSaberBow", col)
    rings, vs = [], []
    for i, z in enumerate([0.048, 0.078]):
        ring = [Vector((math.cos(2 * math.pi * j / 16) * 0.055, math.sin(2 * math.pi * j / 16) * 0.055 * 0.42, z)) for j in range(16)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    path = [Vector((0.0, 0.034, 0.078)), Vector((0.0, 0.058, -0.06)),
            Vector((0.0, 0.046, -0.24)), Vector((0.0, 0.024, -0.40))]
    curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - 0.3 * t) + 0.004, 7, "flair")
    commit(obj, bm)

    # Ghost silk tassels dangling from the guard
    obj, bm, uv = new_mesh_obj("Tassel_GhostSilk", col)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.050, 0.0, 0.062)), Vector((sx * 0.072, 0.0, -0.02)),
                Vector((sx * 0.066, 0.0, -0.12)), Vector((sx * 0.050, 0.0, -0.20))]
        curved_loft(bm, uv, path, lambda t: 0.007 * (1.0 - t) + 0.002, 6, "flair")
        pts = []
        for j in range(9):
            a = 2 * math.pi * j / 8
            pts.append((sx * 0.050 + math.cos(a) * 0.009, math.sin(a) * 0.009, -0.20))
        strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_SilverAnimaFlame", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.007, 0.005), (0.018, 0.020), (0.025, 0.037), (0.016, 0.050), (0.007, 0.055)]):
        z = 0.16 + h2
        ring = [Vector((0.014 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SilkWireWrap", col)
    grip_braid(bm, uv, 0.048, -0.40, 11, 9, 0.026, 0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AnimaTeardrop", col)
    bulb_pommel(bm, uv, -0.400, [0.012, 0.026, 0.034, 0.028, 0.016, 0.005], 9, squash=0.92, drop=0.085, ring_r=0.033, ring_z=-0.446)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_SilverFittings", col)
    ferrule_pair(bm, uv, [(0.02, 0.048), (-0.368, -0.398)], 0.031)
    commit(obj, bm)

# =============================================================================
# E. arcane_crystal_cipher_sword - "Espada Cifrada de Cristal" (arcane)
# =============================================================================
def build_crystalcipher(col):
    def cipher_section(z, p):
        # 12-vert faceted prism: strong bevel planes, hot flashes
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.85 * w,  ht * 0.55, z)),
            Vector((xs + 0.70 * w,  ht,        z)),
            Vector((xs + 0.45 * w,  ht * 0.65, z)),
            Vector((xs + 0.20 * w,  ht,        z)),
            Vector((xs,             ht * 0.30, z)),
            Vector((xs,             -ht * 0.30,z)),
            Vector((xs + 0.20 * w,  -ht,       z)),
            Vector((xs + 0.45 * w,  -ht * 0.65,z)),
            Vector((xs + 0.70 * w,  -ht,       z)),
            Vector((xs + 0.85 * w,  -ht * 0.55,z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.42, 0.68, 0.94, 1.20, 1.46, 1.70, 1.90, 2.04]
    for i, z in enumerate(zs):
        t = z / 2.04
        width = (0.115 - 0.075 * t) * (0.50 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + width,
            "half_t": 0.024 * (1.0 - 0.40 * t) + 0.004,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_CrystalCipherSword", col)
    rings, vs = make_rings(stations, cipher_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Inlay_CipherRingGlyphs", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.32 + 1.28 * t
            pts.append((-0.050 + 0.058 + 0.010 * math.sin(t * 10.0), sy * 0.019, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Crystal facet bands: 3 collars around the blade
    obj, bm, uv = new_mesh_obj("Cipher_FacetBands", col)
    for z0, z1, rr in [(0.72, 0.78, 0.028), (1.12, 1.18, 0.024), (1.52, 1.58, 0.020)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            ring = [Vector((0.008 + math.cos(2 * math.pi * j / 12) * rr, math.sin(2 * math.pi * j / 12) * rr * 1.6, z)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Cipher orbit rings: 2 tilted rings + 3 orbit stones
    obj, bm, uv = new_mesh_obj("Guard_CipherOrbitRings", col)
    for k, (rz, tilt) in enumerate([(0.10, 0.30), (0.20, -0.26)]):
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append((math.cos(a) * 0.085, math.sin(a) * 0.085 * 0.55 + math.sin(a) * tilt * 0.0, rz + math.sin(a) * 0.030 * (1 if k == 0 else -1)))
        strip_loft(bm, uv, pts, "flair", half_w=0.0045, half_t=0.0045)
    for k in range(3):
        a = 2 * math.pi * k / 3.0 + 0.6
        path = [Vector((math.cos(a) * (0.088 + 0.016 * t), math.sin(a) * (0.088 + 0.016 * t) * 0.55, 0.15 + 0.010 * math.sin(t * 3.0))) for t in [i / 4.0 for i in range(5)]]
        curved_loft(bm, uv, path, lambda t: 0.011 * (1.0 - t) + 0.004, 7, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_PrismCipherCore", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.020, 0.022), (0.027, 0.040), (0.018, 0.053), (0.008, 0.058)]):
        z = 0.18 + h2
        ring = [Vector((0.019 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_CipherEtchedWrap", col)
    grip_braid(bm, uv, 0.055, -0.44, 11, 9, 0.028, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_CipherMatrixCube", col)
    bulb_pommel(bm, uv, -0.440, [0.013, 0.030, 0.038, 0.032, 0.018, 0.005], 9, squash=1.25, drop=0.095, ring_r=0.037, ring_z=-0.486)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_CrystalBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.408, -0.438)], 0.033)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "solarinit": {
        "name": "sword_05_solar_initiate", "builder": build_solarinit, "tex": "solar_initiate",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "solar_initiate"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage05_swords", "solar_initiate"),
    },
    "obsidianfang": {
        "name": "sword_05_obsidian_fang", "builder": build_obsidianfang, "tex": "obsidian_fang",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "obsidian_fang"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage05_swords", "obsidian_fang"),
    },
    "coppertempest": {
        "name": "sword_05_copper_tempest", "builder": build_coppertempest, "tex": "copper_tempest",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "copper_tempest"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage05_swords", "copper_tempest"),
    },
    "silveranima": {
        "name": "sword_05_silver_anima", "builder": build_silveranima, "tex": "silver_anima",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "silver_anima"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage05_swords", "silver_anima"),
    },
    "crystalcipher": {
        "name": "sword_05_crystal_cipher", "builder": build_crystalcipher, "tex": "crystal_cipher",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "crystal_cipher"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage05_swords", "crystal_cipher"),
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
    sword = "solarinit"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_05_Root", None)
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
    print("STAGE05_BUILD_DONE", sword)

main()

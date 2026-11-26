# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 06: CINCO espadas bespoke (anime exagerado por linaje)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage06_swords.py -- sword=auric|reaver|glacier|mistwalk|astrolabe
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
# A. blessed_auric_bastion_claymore - "Claymore Bastion Aurico" (blessed heavy)
# =============================================================================
def build_auric(col):
    def bastion_section(z, p):
        # 14-vert fortress claymore: wide wall faces, blunt strong tip
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0032
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.86 * w,  ht,        z)),
            Vector((xs + 0.62 * w,  ht * 0.70, z)),
            Vector((xs + 0.38 * w,  ht * 0.98, z)),
            Vector((xs + 0.16 * w,  ht * 0.64, z)),
            Vector((xs + 0.05 * w,  ht * 0.28, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.28,z)),
            Vector((xs + 0.16 * w,  -ht * 0.64,z)),
            Vector((xs + 0.38 * w,  -ht * 0.98,z)),
            Vector((xs + 0.62 * w,  -ht * 0.70,z)),
            Vector((xs + 0.86 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.15, 0.38, 0.66, 0.96, 1.26, 1.54, 1.78, 1.96, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = (0.175 - 0.070 * t) * (0.55 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.058, "x_edge": -0.058 + width,
            "half_t": 0.030 * (1.0 - 0.50 * t) + 0.004,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_AuricBastionClaymore", col)
    rings, vs = make_rings(stations, bastion_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Battlement merlons along the spine (5 gold wall blocks)
    obj, bm, uv = new_mesh_obj("Merlons_LivingGoldWall", col)
    for k in range(5):
        t = 0.16 + 0.17 * k
        z = 0.34 + 1.30 * t
        x0 = -0.058 + 0.010
        pts = [(x0, 0.0, z), (x0 - 0.026, 0.0, z + 0.010), (x0 - 0.026, 0.0, z + 0.048), (x0, 0.0, z + 0.058)]
        strip_loft(bm, uv, pts, "flair", half_w=0.0075, half_t=0.013)
    commit(obj, bm)

    # Golden wall veins (glow strips on both flats)
    obj, bm, uv = new_mesh_obj("Inlay_AuricWallVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.36 + 1.26 * t
            pts.append((-0.058 + 0.088 + 0.020 * math.sin(t * 7.0), sy * 0.025, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.008, half_t=0.004)
    commit(obj, bm)

    # Rampart bar guard with 3 merlon teeth
    obj, bm, uv = new_mesh_obj("Guard_RampartBar", col)
    rings, vs = [], []
    for i, z in enumerate([0.050, 0.098]):
        ring = [Vector((math.cos(2 * math.pi * j / 14) * 0.098, math.sin(2 * math.pi * j / 14) * 0.098 * 0.40, z)) for j in range(14)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for k, zo in enumerate([0.098, 0.098, 0.098]):
        xo = -0.062 + 0.062 * k
        pts = [(xo, 0.0, zo), (xo - 0.016, 0.0, zo + 0.006), (xo - 0.016, 0.0, zo + 0.042), (xo, 0.0, zo + 0.048)]
        strip_loft(bm, uv, pts, "flair", half_w=0.006, half_t=0.010)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_AuricBastionHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.025, 0.026), (0.033, 0.046), (0.023, 0.060), (0.010, 0.066)]):
        z = 0.19 + h2
        ring = [Vector((0.024 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_BastionWrap", col)
    grip_braid(bm, uv, 0.055, -0.46, 11, 9, 0.032, 0.005, thick_every=2, thick=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BastionTurret", col)
    bulb_pommel(bm, uv, -0.460, [0.017, 0.038, 0.048, 0.042, 0.025, 0.007], 9, squash=1.0, drop=0.105, ring_r=0.049, ring_z=-0.514)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BrassBastion", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.428, -0.458)], 0.038)
    commit(obj, bm)

# =============================================================================
# B. cursed_crimson_reaver_cleaver - "Hendidora Segadora Carmesi" (cursed swift)
# =============================================================================
def build_reaver(col):
    def reaver_section(z, p):
        # 14-vert massive cleaver with hooked tip zone
        xs, xe = p["x_spine"], p["x_edge"]
        hook = p.get("hook", 0.0)
        w = (xe + hook) - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe + hook,      ye,        z)),
            Vector((xs + 0.88 * w,  ht,        z)),
            Vector((xs + 0.72 * w,  ht * 0.88, z)),
            Vector((xs + 0.46 * w,  ht,        z)),
            Vector((xs + 0.22 * w,  ht * 0.70, z)),
            Vector((xs + 0.06 * w,  ht * 0.30, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.06 * w,  -ht * 0.30,z)),
            Vector((xs + 0.22 * w,  -ht * 0.70,z)),
            Vector((xs + 0.46 * w,  -ht,       z)),
            Vector((xs + 0.72 * w,  -ht * 0.88,z)),
            Vector((xs + 0.88 * w,  -ht,       z)),
            Vector((xe + hook,      -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.42, 0.68, 0.94, 1.20, 1.44, 1.66, 1.86, 1.98, 2.04]
    for i, z in enumerate(zs):
        t = z / 2.04
        hook = max(0.0, t - 0.82) * 0.16 if i >= 8 else 0.0
        width = (0.190 - 0.060 * t) * (1.05 if i % 2 == 0 else 1.0)
        stations.append((z, {
            "x_spine": -0.060, "x_edge": -0.060 + width,
            "half_t": 0.028 * (1.0 - 0.45 * t) + 0.004,
            "v": t, "hook": hook,
        }))

    obj, bm, uv = new_mesh_obj("Blade_CrimsonReaverCleaver", col)
    rings, vs = make_rings(stations, reaver_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Reaper moon emblem (glow ring + crescent on the flat)
    obj, bm, uv = new_mesh_obj("Emblem_ReaperMoon", col)
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append((-0.060 + 0.082 + math.cos(a) * 0.032, -0.026, 0.62 + math.sin(a) * 0.036))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    for sy in (1.0, -1.0):
        pts2 = []
        for i in range(13):
            t = i / 12.0
            z = 0.34 + 1.20 * t
            pts2.append((-0.060 + 0.108 + 0.012 * math.sin(t * 9.0), sy * 0.024, z))
        strip_loft(bm, uv, pts2, "glow", half_w=0.0065, half_t=0.004)
    commit(obj, bm)

    # Spine spikes x3 (harvest thorn fins)
    obj, bm, uv = new_mesh_obj("Fins_HarvestThorns", col)
    for k in range(3):
        t = 0.18 + 0.24 * k
        z = 0.44 + 1.06 * t
        pts = [Vector((-0.060 + 0.004, 0.0, z)), Vector((-0.060 - 0.020, 0.0, z + 0.016)), Vector((-0.060 - 0.030, 0.0, z + 0.046))]
        curved_loft(bm, uv, pts, lambda tt: 0.008 * (1.0 - tt) + 0.002, 6, "flair")
    commit(obj, bm)

    # Crescent scythe guard
    obj, bm, uv = new_mesh_obj("Guard_CrescentScythe", col)
    pts = []
    for j in range(25):
        a = math.pi * 0.15 + math.pi * 0.70 * (j / 24.0)
        pts.append((math.cos(a) * 0.150 - 0.010, math.sin(a) * 0.150 * 0.42 - 0.030, 0.072))
    strip_loft(bm, uv, pts, "flair", half_w=0.010, half_t=0.009)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.034, 0.0, 0.090)), Vector((sx * 0.052, 0.0, 0.140)), Vector((sx * 0.040, 0.0, 0.190))]
        curved_loft(bm, uv, path, lambda t: 0.009 * (1.0 - t) + 0.003, 6, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_HarvestHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.023, 0.024), (0.031, 0.043), (0.021, 0.057), (0.009, 0.062)]):
        z = 0.20 + h2
        ring = [Vector((0.020 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ReaperBloodWrap", col)
    grip_braid(bm, uv, 0.055, -0.45, 12, 9, 0.030, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SickleHook", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.032, 0.041, 0.035, 0.020, 0.006], 9, squash=1.15, drop=0.10, ring_r=0.040, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BloodIronReaver", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.418, -0.448)], 0.036)
    commit(obj, bm)

# =============================================================================
# C. elemental_glacier_fang_longsword - "Espada Larga Colmillo de Glaciar" (elemental)
# =============================================================================
def build_glacier(col):
    def glacier_section(z, p):
        # 12-vert longsword: crisp bevels, long taper
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0026
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.55 * w,  ht * 0.60, z)),
            Vector((xs + 0.30 * w,  ht * 0.96, z)),
            Vector((xs + 0.11 * w,  ht * 0.52, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.11 * w,  -ht * 0.52,z)),
            Vector((xs + 0.30 * w,  -ht * 0.96,z)),
            Vector((xs + 0.55 * w,  -ht * 0.60,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.20, 0.46, 0.74, 1.02, 1.30, 1.56, 1.80, 1.98, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.128 - 0.082 * t) * (0.40 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + width,
            "half_t": 0.021 * (1.0 - 0.50 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_GlacierFangLongsword", col)
    rings, vs = make_rings(stations, glacier_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Icicle fangs hanging from the spine (4 down-swept teeth)
    obj, bm, uv = new_mesh_obj("Fangs_IcicleTeeth", col)
    for k in range(4):
        t = 0.14 + 0.22 * k
        z = 0.42 + 1.10 * t
        sy = 1.0 if k % 2 == 0 else -1.0
        path = [Vector((-0.050 + 0.004, sy * 0.004, z)), Vector((-0.050 - 0.014, sy * 0.010, z - 0.030)),
                Vector((-0.050 - 0.020, sy * 0.014, z - 0.075))]
        curved_loft(bm, uv, path, lambda tt: 0.009 * (1.0 - tt) + 0.002, 6, "flair")
    commit(obj, bm)

    # Frost melt lines (glow strips)
    obj, bm, uv = new_mesh_obj("Inlay_FrostMeltLines", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.32 + 1.30 * t
            pts.append((-0.050 + 0.056 + 0.010 * math.sin(t * 12.0), sy * 0.018, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Ice shelf guard with icicles down
    obj, bm, uv = new_mesh_obj("Guard_IceShelfWings", col)
    for side in (1.0, -1.0):
        path = [Vector((side * 0.034, 0.0, 0.096)), Vector((side * 0.110, 0.0, 0.066)),
                Vector((side * 0.185, 0.0, 0.052)), Vector((side * 0.230, 0.0, 0.068))]
        curved_loft(bm, uv, path, lambda t: 0.017 * (1.0 - 0.5 * t) + 0.005, 8, "flair")
        for k in range(2):
            xo = side * (0.10 + 0.055 * k)
            path2 = [Vector((xo, 0.0, 0.058)), Vector((xo * 1.06, 0.0, 0.020)), Vector((xo * 1.04, 0.0, -0.030))]
            curved_loft(bm, uv, path2, lambda t: 0.006 * (1.0 - t) + 0.002, 6, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_FrozenStar", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.022, 0.023), (0.030, 0.042), (0.020, 0.056), (0.009, 0.061)]):
        z = 0.20 + h2
        ring = [Vector((0.019 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_FrostBlueHilt", col)
    grip_braid(bm, uv, 0.055, -0.45, 11, 9, 0.029, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_IcebergCrystal", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.032, 0.041, 0.035, 0.020, 0.006], 9, squash=1.1, drop=0.10, ring_r=0.040, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_FrozenSilver", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.418, -0.448)], 0.034)
    commit(obj, bm)

# =============================================================================
# D. spiritual_mistwalker_bamboo_katana - "Katana Caminante de la Niebla" (spiritual swift)
# =============================================================================
def build_mistwalk(col):
    def bamboo_section(z, p):
        # 12-vert slim bamboo katana blade
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.70 * w,  ht * 0.85, z)),
            Vector((xs + 0.45 * w,  ht,        z)),
            Vector((xs + 0.22 * w,  ht * 0.72, z)),
            Vector((xs + 0.08 * w,  ht * 0.35, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.08 * w,  -ht * 0.40,z)),
            Vector((xs + 0.24 * w,  -ht * 0.85,z)),
            Vector((xs + 0.48 * w,  -ht,       z)),
            Vector((xs + 0.72 * w,  -ht * 0.80,z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.05, 0.20, 0.46, 0.72, 1.00, 1.28, 1.54, 1.78, 1.96, 2.06]
    offs = []
    for i, z in enumerate(zs):
        t = z / 2.06
        off = -0.060 * (t ** 1.6)
        width = (0.070 - 0.026 * t) * (0.62 if i == len(zs) - 1 else 1.0)
        xs = -0.026 + off
        offs.append(xs + width)
        stations.append((z, {"x_spine": xs, "x_edge": xs + width,
                             "half_t": 0.012 * (1.0 - 0.35 * t) + 0.002, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_MistwalkerBambooKatana", col)
    rings, vs = make_rings(stations, bamboo_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Bamboo node collars x4 (slight ring bulges on the blade)
    obj, bm, uv = new_mesh_obj("Nodes_BambooJoints", col)
    for k in range(4):
        t = 0.16 + 0.19 * k
        z = 0.34 + 1.30 * t
        off = -0.060 * (t ** 1.6)
        rr = 0.0115 - 0.002 * k
        rings, vs = [], []
        for i, zc in enumerate([z - 0.006, z + 0.006]):
            ring = [Vector((-0.026 + off + 0.034 + math.cos(2 * math.pi * j / 12) * rr * 0.9,
                            math.sin(2 * math.pi * j / 12) * rr * 1.7, zc)) for j in range(12)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Mist wisp glow strip along the flats
    obj, bm, uv = new_mesh_obj("Inlay_MistWisps", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.26 + 1.44 * t
            off = -0.060 * ((z / 2.06) ** 1.6)
            pts.append((-0.026 + off + 0.040 + 0.006 * math.sin(t * 10.0), sy * 0.012, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    # Mist cloud halo floating beside the blade
    obj, bm, uv = new_mesh_obj("Halo_MistCloud", col)
    for k, (zo, rr, sq) in enumerate([(0.72, 0.052, 1.0), (1.06, 0.062, 1.0), (1.40, 0.050, 1.0)]):
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            off = -0.060 * ((zo / 2.06) ** 1.6)
            cx = -0.026 + off + 0.040
            pts.append((cx + math.cos(a) * rr * (1.0 + 0.12 * math.sin(3 * a)), math.sin(a) * rr * 0.42 + 0.040, zo + math.sin(2 * a) * 0.006))
        strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.0045)
    commit(obj, bm)

    # Woven bamboo tsuba
    obj, bm, uv = new_mesh_obj("Tsuba_BambooWeaveRings", col)
    for z0, z1, r, sq in [(0.045, 0.058, 0.072, 0.58), (0.058, 0.070, 0.064, 0.58)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            ring = [Vector((math.cos(2 * math.pi * j / 16) * r, math.sin(2 * math.pi * j / 16) * r * sq, z)) for j in range(16)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_MistLantern", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.007, 0.005), (0.019, 0.021), (0.026, 0.038), (0.017, 0.051), (0.007, 0.056)]):
        z = 0.15 + h2
        ring = [Vector((0.013 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_BambooSilkWrap", col)
    grip_braid(bm, uv, 0.045, -0.40, 12, 9, 0.025, 0.004, thick_every=2, thick=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BambooRingCap", col)
    bulb_pommel(bm, uv, -0.400, [0.012, 0.025, 0.031, 0.025, 0.013, 0.004], 9, squash=0.9, drop=0.075, ring_r=0.030, ring_z=-0.440)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BambooJadeFittings", col)
    ferrule_pair(bm, uv, [(0.050, 0.100)], 0.028, squash=0.6)
    ferrule_pair(bm, uv, [(-0.365, -0.395)], 0.028, squash=0.95)
    commit(obj, bm)

# =============================================================================
# E. arcane_astrolabe_ring_blade - "Hoja Anillo de Astrolabio" (arcane mystic)
# =============================================================================
def build_astrolabe(col):
    def astro_section(z, p):
        # 12-vert slim charted blade, long reach
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.55 * w,  ht * 0.62, z)),
            Vector((xs + 0.30 * w,  ht * 0.95, z)),
            Vector((xs + 0.11 * w,  ht * 0.52, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.11 * w,  -ht * 0.52,z)),
            Vector((xs + 0.30 * w,  -ht * 0.95,z)),
            Vector((xs + 0.55 * w,  -ht * 0.62,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.22, 0.50, 0.80, 1.10, 1.40, 1.68, 1.92, 2.10, 2.20]
    for i, z in enumerate(zs):
        t = z / 2.20
        width = (0.105 - 0.068 * t) * (0.42 if i == len(zs) - 1 else 1.0)
        stations.append((z, {
            "x_spine": -0.045, "x_edge": -0.045 + width,
            "half_t": 0.018 * (1.0 - 0.45 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_AstrolabeRingBlade", col)
    rings, vs = make_rings(stations, astro_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Star-chart etch glow strips
    obj, bm, uv = new_mesh_obj("Inlay_StarChartEtch", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.36 + 1.42 * t
            pts.append((-0.045 + 0.048 + 0.008 * math.sin(t * 9.0), sy * 0.015, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.003)
    commit(obj, bm)

    # Armillary rings: big vertical + tilted + horizontal around the lower blade
    obj, bm, uv = new_mesh_obj("Rings_ArmillarySphere", col)
    pts = []
    for j in range(29):
        a = 2 * math.pi * j / 28
        pts.append((0.010 + math.cos(a) * 0.125, math.sin(a) * 0.125, 0.34))
    strip_loft(bm, uv, pts, "flair", half_w=0.006, half_t=0.006)
    pts = []
    for j in range(29):
        a = 2 * math.pi * j / 28
        pts.append((0.010 + math.cos(a) * 0.098, math.sin(a) * 0.098 * 0.42, 0.34 + math.sin(a) * 0.070))
    strip_loft(bm, uv, pts, "flair", half_w=0.005, half_t=0.005)
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append((0.010 + math.cos(a) * 0.086, math.sin(a) * 0.086, 0.22 + math.sin(a) * 0.026))
    strip_loft(bm, uv, pts, "flair", half_w=0.0045, half_t=0.0045)
    for k in range(4):
        a = 2 * math.pi * k / 4.0 + 0.4
        path = [Vector((0.010 + math.cos(a) * (0.128 + 0.014 * t), math.sin(a) * (0.128 + 0.014 * t), 0.34 + 0.008 * math.sin(t * 3.0))) for t in [i / 4.0 for i in range(5)]]
        curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - t) + 0.004, 7, "glow")
    commit(obj, bm)

    # Astrolabe disc guard with pointer needle
    obj, bm, uv = new_mesh_obj("Guard_AstrolabeDisc", col)
    rings, vs = [], []
    for i, z in enumerate([0.046, 0.082]):
        ring = [Vector((math.cos(2 * math.pi * j / 18) * 0.082, math.sin(2 * math.pi * j / 18) * 0.082 * 0.62, z)) for j in range(18)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    path = [Vector((0.0, 0.010, 0.082)), Vector((0.070, 0.020, 0.120)), Vector((0.118, 0.028, 0.168))]
    curved_loft(bm, uv, path, lambda t: 0.006 * (1.0 - 0.4 * t) + 0.0025, 7, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_PolarisStar", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.021, 0.023), (0.029, 0.041), (0.019, 0.055), (0.008, 0.060)]):
        z = 0.16 + h2
        ring = [Vector((0.016 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_AstroChartedHilt", col)
    grip_braid(bm, uv, 0.046, -0.42, 11, 9, 0.026, 0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_GimbalRings", col)
    bulb_pommel(bm, uv, -0.420, [0.012, 0.027, 0.034, 0.028, 0.016, 0.005], 9, squash=1.0, drop=0.085, ring_r=0.034, ring_z=-0.456)
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append((math.cos(a) * 0.038, math.sin(a) * 0.026, -0.470))
    strip_loft(bm, uv, pts, "flair", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BrassAstrolabe", col)
    ferrule_pair(bm, uv, [(0.02, 0.048), (-0.388, -0.416)], 0.031)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "auric": {
        "name": "sword_06_auric_bastion", "builder": build_auric, "tex": "auric_bastion",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "auric_bastion"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage06_swords", "auric_bastion"),
    },
    "reaver": {
        "name": "sword_06_crimson_reaver", "builder": build_reaver, "tex": "crimson_reaver",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "crimson_reaver"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage06_swords", "crimson_reaver"),
    },
    "glacier": {
        "name": "sword_06_glacier_fang", "builder": build_glacier, "tex": "glacier_fang",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "glacier_fang"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage06_swords", "glacier_fang"),
    },
    "mistwalk": {
        "name": "sword_06_mistwalker_bamboo", "builder": build_mistwalk, "tex": "mistwalker_bamboo",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "mistwalker_bamboo"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage06_swords", "mistwalker_bamboo"),
    },
    "astrolabe": {
        "name": "sword_06_astrolabe_ring", "builder": build_astrolabe, "tex": "astrolabe_ring",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "astrolabe_ring"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage06_swords", "astrolabe_ring"),
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
    sword = "auric"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_06_Root", None)
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
    print("STAGE06_BUILD_DONE", sword)

main()

# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 08: SEIS espadas bespoke (5 linajes + 1 hibrida secreta)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage08_swords.py -- sword=covenant|bloodmoon|thunderlord|chorus|monolith|twilight
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
# A. blessed_radiant_covenant_greatsword - "Mandoble de la Alianza Radiante" (blessed)
# =============================================================================
def build_covenant(col):
    def cov_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.85 * w,  ht,        z)),
            Vector((xs + 0.61 * w,  ht * 0.70, z)),
            Vector((xs + 0.37 * w,  ht * 0.98, z)),
            Vector((xs + 0.15 * w,  ht * 0.62, z)),
            Vector((xs + 0.05 * w,  ht * 0.26, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.26,z)),
            Vector((xs + 0.15 * w,  -ht * 0.62,z)),
            Vector((xs + 0.37 * w,  -ht * 0.98,z)),
            Vector((xs + 0.61 * w,  -ht * 0.70,z)),
            Vector((xs + 0.85 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.44, 0.72, 1.00, 1.28, 1.54, 1.78, 1.98, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.185 - 0.085 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.060, "x_edge": -0.060 + width,
                             "half_t": 0.030 * (1.0 - 0.50 * t) + 0.004, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_RadiantCovenantGreatsword", col)
    rings, vs = make_rings(stations, cov_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Great sanctuary seal: big ring + inner ring on each flat
    obj, bm, uv = new_mesh_obj("Seal_SanctuarySeal", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(29):
            a = 2 * math.pi * j / 28
            pts.append((-0.060 + 0.088 + math.cos(a) * 0.062, sy * 0.027, 1.02 + math.sin(a) * 0.052))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            pts.append((-0.060 + 0.088 + math.cos(a) * 0.034, sy * 0.028, 1.02 + math.sin(a) * 0.029))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Radiant pulse strips toward the tip
    obj, bm, uv = new_mesh_obj("Inlay_RadiantPulse", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(11):
            t = i / 10.0
            z = 1.42 + 0.48 * t
            pts.append((-0.060 + 0.088 + 0.010 * math.sin(t * 6.0), sy * 0.024, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Veil-wing guard: 2 layered fans
    obj, bm, uv = new_mesh_obj("Guard_VeilWings", col)
    for side in (1.0, -1.0):
        for layer in range(2):
            path = [Vector((side * 0.040, 0.004, 0.080 - 0.014 * layer)),
                    Vector((side * (0.110 - 0.018 * layer), 0.008, 0.048 - 0.010 * layer)),
                    Vector((side * (0.185 - 0.030 * layer), 0.006, 0.042 - 0.008 * layer)),
                    Vector((side * (0.230 - 0.038 * layer), 0.002, 0.070 - 0.014 * layer))]
            curved_loft(bm, uv, path, lambda t: 0.016 * (1.0 - 0.55 * t) + 0.005, 8, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_RadiantReliquary", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.026, 0.027), (0.034, 0.047), (0.024, 0.061), (0.010, 0.067)]):
        z = 0.20 + h2
        ring = [Vector((0.024 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_CovenantSilkHilt", col)
    grip_braid(bm, uv, 0.055, -0.47, 11, 9, 0.032, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_ReliquaryOrb", col)
    bulb_pommel(bm, uv, -0.470, [0.016, 0.037, 0.047, 0.041, 0.024, 0.007], 9, squash=1.0, drop=0.105, ring_r=0.048, ring_z=-0.523)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_CovenantGold", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.440, -0.470)], 0.038)
    commit(obj, bm)

# =============================================================================
# B. cursed_bloodmoon_pact_greatsword - "Mandoble del Pacto Luna Sangrienta" (cursed)
# =============================================================================
def build_bloodmoon(col):
    def bm_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        notch = p.get("notch", 0.004)
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe - notch,     ye,        z)),
            Vector((xs + 0.88 * w,  ht,        z)),
            Vector((xs + 0.72 * w,  ht * 0.90, z)),
            Vector((xs + 0.48 * w,  ht,        z)),
            Vector((xs + 0.24 * w,  ht * 0.68, z)),
            Vector((xs + 0.06 * w,  ht * 0.28, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.06 * w,  -ht * 0.28,z)),
            Vector((xs + 0.24 * w,  -ht * 0.68,z)),
            Vector((xs + 0.48 * w,  -ht,       z)),
            Vector((xs + 0.72 * w,  -ht * 0.90,z)),
            Vector((xs + 0.88 * w,  -ht,       z)),
            Vector((xe - notch,     -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.18, 0.40, 0.64, 0.88, 1.12, 1.36, 1.58, 1.80, 1.94, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        stations.append((z, {
            "x_spine": -0.062, "x_edge": -0.062 + (0.200 - 0.070 * t),
            "half_t": 0.029 * (1.0 - 0.45 * t) + 0.004,
            "v": t, "notch": (0.022 if i % 2 == 1 and i >= 5 else 0.004),
        }))

    obj, bm, uv = new_mesh_obj("Blade_BloodmoonPactGreatsword", col)
    rings, vs = make_rings(stations, bm_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Blood moon disc emboss on each flat
    obj, bm, uv = new_mesh_obj("Emblem_BloodMoonDisc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append((-0.062 + 0.096 + math.cos(a) * 0.052, sy * 0.028, 0.98 + math.sin(a) * 0.044))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.006)
        pts = []
        for i in range(11):
            t = i / 10.0
            z = 0.98 + 0.044 * math.sin(t * math.pi)
            pts.append((-0.062 + 0.096 + 0.052 * math.cos(t * math.pi), sy * 0.029, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.007, half_t=0.006)
    commit(obj, bm)

    # Pact veins running to the tip
    obj, bm, uv = new_mesh_obj("Inlay_PactVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.42 * t
            pts.append((-0.062 + 0.120 + 0.016 * math.sin(t * 8.0), sy * 0.022, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.0055, half_t=0.0035)
    commit(obj, bm)

    # Inverted crescent horns guard
    obj, bm, uv = new_mesh_obj("Guard_InvertedCrescent", col)
    pts = []
    for j in range(25):
        a = math.pi * 1.15 + math.pi * 0.70 * (j / 24.0)
        pts.append((math.cos(a) * 0.170, math.sin(a) * 0.170 * 0.45 + 0.048, 0.070))
    strip_loft(bm, uv, pts, "flair", half_w=0.011, half_t=0.010)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.040, 0.0, 0.092)), Vector((sx * 0.058, 0.0, 0.150)), Vector((sx * 0.042, 0.0, 0.205))]
        curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - t) + 0.003, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_PactBleedingHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.011, 0.006), (0.027, 0.027), (0.035, 0.047), (0.024, 0.061), (0.011, 0.067)]):
        z = 0.20 + h2
        ring = []
        for j in range(10):
            a = 2 * math.pi * j / 10
            m = 1.0 + 0.18 * math.sin(2 * a + 1.1)
            ring.append(Vector((0.021 + math.cos(a) * w2 * m, math.sin(a) * h2 * 0.6 * m, z)))
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_PactBloodWrap", col)
    grip_braid(bm, uv, 0.055, -0.46, 12, 9, 0.031, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BloodDrop", col)
    bulb_pommel(bm, uv, -0.460, [0.015, 0.034, 0.043, 0.036, 0.020, 0.006], 9, squash=1.35, drop=0.105, ring_r=0.043, ring_z=-0.514)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_PactBloodIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.430, -0.460)], 0.037)
    commit(obj, bm)

# =============================================================================
# C. elemental_thunderlord_fulgur_edge - "Filo Fulgur del Senor del Trueno" (elemental)
# =============================================================================
def build_thunderlord(col):
    def tl_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0026
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.56 * w,  ht * 0.62, z)),
            Vector((xs + 0.30 * w,  ht * 0.96, z)),
            Vector((xs + 0.11 * w,  ht * 0.52, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.11 * w,  -ht * 0.52,z)),
            Vector((xs + 0.30 * w,  -ht * 0.96,z)),
            Vector((xs + 0.56 * w,  -ht * 0.62,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.22, 0.50, 0.80, 1.10, 1.38, 1.62, 1.84, 2.00, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = (0.160 - 0.090 * t) * (0.62 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.055, "x_edge": -0.055 + width,
                             "half_t": 0.024 * (1.0 - 0.48 * t) + 0.004, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_ThunderlordFulgurEdge", col)
    rings, vs = make_rings(stations, tl_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Trident side prongs: 2 swept blades splitting at the tip zone
    obj, bm, uv = new_mesh_obj("Prongs_StormTrident", col)
    for sy in (1.0, -1.0):
        path = [Vector((-0.055 + 0.052, sy * 0.010, 1.44)), Vector((-0.055 + 0.030, sy * 0.036, 1.72)),
                Vector((-0.055 + 0.016, sy * 0.048, 1.94)), Vector((-0.055 + 0.010, sy * 0.052, 2.10))]
        curved_loft(bm, uv, path, lambda t: 0.016 * (1.0 - 0.6 * t) + 0.004, 8, "flair")
    commit(obj, bm)

    # Lightning channels full length
    obj, bm, uv = new_mesh_obj("Inlay_StormChannels", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(15):
            t = i / 14.0
            z = 0.20 + 1.72 * t
            pts.append((-0.055 + 0.062 + 0.012 * math.sin(t * 12.0), sy * 0.018, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0035)
    commit(obj, bm)

    # Thunder crown guard: arc + 3 spark teeth
    obj, bm, uv = new_mesh_obj("Guard_ThunderCrown", col)
    pts = []
    for j in range(23):
        a = math.pi * 0.25 + math.pi * 0.50 * (j / 22.0)
        pts.append((math.cos(a) * 0.115, math.sin(a) * 0.115 * 0.75, 0.070))
    strip_loft(bm, uv, pts, "flair", half_w=0.009, half_t=0.009)
    for k, xo in enumerate([-0.048, 0.0, 0.048]):
        pts2 = [(xo, 0.0, 0.078), (xo - 0.010, 0.0, 0.110), (xo + 0.008, 0.0, 0.148)]
        strip_loft(bm, uv, pts2, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_FulgurOrb", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.025, 0.026), (0.033, 0.046), (0.023, 0.060), (0.010, 0.066)]):
        z = 0.19 + h2
        ring = [Vector((0.021 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StormWrappedHilt", col)
    grip_braid(bm, uv, 0.052, -0.45, 11, 9, 0.030, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BoltAnchor", col)
    bulb_pommel(bm, uv, -0.450, [0.015, 0.034, 0.043, 0.037, 0.021, 0.006], 9, squash=1.1, drop=0.10, ring_r=0.042, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_StormSteel", col)
    ferrule_pair(bm, uv, [(0.02, 0.052), (-0.418, -0.448)], 0.036)
    commit(obj, bm)

# =============================================================================
# D. spiritual_ancestral_chorus_sword - "Espada Coro de los Ancestros" (spiritual swift)
# =============================================================================
def build_chorus(col):
    def cho_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.76 * w,  ht * 0.84, z)),
            Vector((xs + 0.50 * w,  ht,        z)),
            Vector((xs + 0.26 * w,  ht * 0.74, z)),
            Vector((xs + 0.09 * w,  ht * 0.36, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.09 * w,  -ht * 0.36,z)),
            Vector((xs + 0.26 * w,  -ht * 0.74,z)),
            Vector((xs + 0.50 * w,  -ht,       z)),
            Vector((xs + 0.76 * w,  -ht * 0.84,z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.05, 0.20, 0.46, 0.72, 0.98, 1.24, 1.48, 1.70, 1.90, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        width = (0.115 - 0.062 * t) * (0.44 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.048, "x_edge": -0.048 + width,
                             "half_t": 0.019 * (1.0 - 0.42 * t) + 0.003, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_AncestralChorusSword", col)
    rings, vs = make_rings(stations, cho_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Echo ripples: 3 glow strips per flat at staggered z
    obj, bm, uv = new_mesh_obj("Rings_EchoRipples", col)
    for sy in (1.0, -1.0):
        for k, (za, zb) in enumerate([(0.52, 0.66), (0.94, 1.08), (1.36, 1.50)]):
            pts = []
            for i in range(7):
                t = i / 6.0
                z = za + (zb - za) * t
                pts.append((-0.048 + 0.052 + 0.006 * math.sin(t * math.pi), sy * 0.015, z))
            strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.003)
    commit(obj, bm)

    # 4 ancestor spirit halos floating around the blade
    obj, bm, uv = new_mesh_obj("Halos_AncestorSpirits", col)
    for k in range(4):
        t = 0.14 + 0.22 * k
        z = 0.44 + 1.06 * t
        xo = -0.048 + 0.040
        sy = 0.040 if k % 2 == 0 else -0.040
        pts = []
        for j in range(17):
            a = 2 * math.pi * j / 16
            pts.append((xo + math.cos(a) * 0.030, sy + math.sin(a) * 0.010, z + math.sin(2 * a) * 0.004))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.0035)
    commit(obj, bm)

    # Hanging chime tubes x2
    obj, bm, uv = new_mesh_obj("Chimes_AncestorChimes", col)
    for sx in (1.0, -1.0):
        path = [Vector((sx * 0.062, 0.004, 0.062)), Vector((sx * 0.072, 0.004, -0.02)),
                Vector((sx * 0.070, 0.004, -0.11))]
        curved_loft(bm, uv, path, lambda t: 0.0035 * (1.0 - t) + 0.0018, 6, "flair")
        rings, vs = [], []
        for i, z in enumerate([-0.110, -0.146]):
            ring = [Vector((sx * 0.070 + math.cos(2 * math.pi * j / 8) * 0.007, 0.004 + math.sin(2 * math.pi * j / 8) * 0.007, z)) for j in range(8)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Bell arch guard
    obj, bm, uv = new_mesh_obj("Guard_BellArch", col)
    pts = []
    for j in range(23):
        a = math.pi * 0.30 + math.pi * 0.40 * (j / 22.0)
        pts.append((math.cos(a) * 0.098, math.sin(a) * 0.098 * 0.62, 0.066))
    strip_loft(bm, uv, pts, "flair", half_w=0.009, half_t=0.0085)
    rings, vs = [], []
    for i, z in enumerate([0.040, 0.058]):
        ring = [Vector((math.cos(2 * math.pi * j / 14) * 0.070, math.sin(2 * math.pi * j / 14) * 0.070 * 0.50, z)) for j in range(14)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_AncestorFlame", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.008, 0.005), (0.021, 0.022), (0.029, 0.040), (0.019, 0.054), (0.008, 0.059)]):
        z = 0.16 + h2
        ring = [Vector((0.016 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ChorusWrappedHilt", col)
    grip_braid(bm, uv, 0.040, -0.38, 11, 9, 0.025, 0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AncestorBell", col)
    bulb_pommel(bm, uv, -0.380, [0.014, 0.030, 0.036, 0.038, 0.026, 0.008], 9, squash=1.0, drop=0.085, ring_r=0.036, ring_z=-0.418)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BellBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.042), (-0.350, -0.378)], 0.030)
    commit(obj, bm)

# =============================================================================
# E. arcane_grimoire_monolith_greatsword - "Mandoble Monolito de Grimorio" (arcane)
# =============================================================================
def build_monolith(col):
    def mono_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.88 * w,  ht,        z)),
            Vector((xs + 0.74 * w,  ht * 0.86, z)),
            Vector((xs + 0.50 * w,  ht,        z)),
            Vector((xs + 0.26 * w,  ht * 0.72, z)),
            Vector((xs + 0.06 * w,  ht * 0.28, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.06 * w,  -ht * 0.28,z)),
            Vector((xs + 0.26 * w,  -ht * 0.72,z)),
            Vector((xs + 0.50 * w,  -ht,       z)),
            Vector((xs + 0.74 * w,  -ht * 0.86,z)),
            Vector((xs + 0.88 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.16, 0.36, 0.58, 0.80, 1.02, 1.24, 1.46, 1.68, 1.88, 1.96]
    for i, z in enumerate(zs):
        t = z / 1.96
        width = 0.105 if i >= 9 else (0.205 - 0.080 * t)
        stations.append((z, {"x_spine": -0.062, "x_edge": -0.062 + width,
                             "half_t": 0.032 * (1.0 - 0.42 * t) + 0.005, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_GrimoireMonolithGreatsword", col)
    rings, vs = make_rings(stations, mono_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Seven seal gems in a vertical line on each flat
    obj, bm, uv = new_mesh_obj("Gems_SevenSeals", col)
    for sy in (1.0, -1.0):
        for k in range(7):
            z = 0.36 + 0.20 * k
            rings, vs = [], []
            for i, rr in enumerate([0.006, 0.011, 0.008]):
                ring = [Vector((-0.062 + 0.095 + math.cos(2 * math.pi * j / 8) * rr, sy * 0.031 + math.sin(2 * math.pi * j / 8) * rr * 0.7, z + rr * 0.3)) for j in range(8)]
                rings.append(ring); vs.append(i / 2.0)
            add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Page-edge gold lines x2
    obj, bm, uv = new_mesh_obj("Inlay_PageEdgeLines", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.30 + 1.42 * t
            pts.append((-0.062 + 0.170 - 0.010 * math.sin(t * 5.0), sy * 0.024, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.003)
    commit(obj, bm)

    # Book spine bar guard + 2 clasps
    obj, bm, uv = new_mesh_obj("Guard_GrimoireSpine", col)
    rings, vs = [], []
    for i, z in enumerate([0.046, 0.092]):
        ring = [Vector((math.cos(2 * math.pi * j / 14) * 0.104, math.sin(2 * math.pi * j / 14) * 0.104 * 0.38, z)) for j in range(14)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for sy in (1.0, -1.0):
        pts = [(0.070, sy * 0.030, 0.092), (0.078, sy * 0.036, 0.128), (0.062, sy * 0.034, 0.152)]
        strip_loft(bm, uv, pts, "shell", half_w=0.007, half_t=0.008)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_SevenSealStack", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.011, 0.006), (0.027, 0.027), (0.035, 0.047), (0.024, 0.061), (0.011, 0.067)]):
        z = 0.20 + h2
        ring = [Vector((0.024 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("GrimoireScriptHilt", col)
    grip_braid(bm, uv, 0.050, -0.44, 11, 9, 0.031, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_GrimoireSealStamp", col)
    bulb_pommel(bm, uv, -0.440, [0.016, 0.036, 0.046, 0.040, 0.023, 0.007], 9, squash=1.0, drop=0.10, ring_r=0.046, ring_z=-0.490)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_GrimoireBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.050), (-0.410, -0.440)], 0.037)
    commit(obj, bm)

# =============================================================================
# F. hybrid_twilight_covenant_blade - "Espada Hibrida del Pacto Crepuscular" (SECRET hybrid)
# =============================================================================
def build_twilight(col):
    def twi_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0024
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.54 * w,  ht * 0.64, z)),
            Vector((xs + 0.28 * w,  ht * 0.96, z)),
            Vector((xs + 0.10 * w,  ht * 0.52, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.10 * w,  -ht * 0.52,z)),
            Vector((xs + 0.28 * w,  -ht * 0.96,z)),
            Vector((xs + 0.54 * w,  -ht * 0.64,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.20, 0.46, 0.72, 0.98, 1.24, 1.48, 1.70, 1.90, 2.02]
    for i, z in enumerate(zs):
        t = z / 2.02
        width = (0.148 - 0.086 * t) * (0.40 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.052, "x_edge": -0.052 + width,
                             "half_t": 0.023 * (1.0 - 0.48 * t) + 0.003, "v": t}))

    obj, bm, uv = new_mesh_obj("Blade_TwilightCovenantBlade", col)
    rings, vs = make_rings(stations, twi_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Twilight seam: glow line running the split boundary
    obj, bm, uv = new_mesh_obj("Seam_TwilightSeam", col)
    pts = []
    for i in range(15):
        t = i / 14.0
        z = 0.18 + 1.70 * t
        pts.append((-0.052 + 0.006, 0.0, z))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # Dual orbit stones: gold (light) + violet (shadow)
    obj, bm, uv = new_mesh_obj("Stones_DualOrbit", col)
    for k, (zo, sy, reg) in enumerate([(0.92, 1.0, "glow"), (1.24, -1.0, "glow")]):
        rings, vs = [], []
        for i, rr in enumerate([0.004, 0.009, 0.011, 0.006]):
            ring = [Vector((-0.052 + 0.055 + math.cos(2 * math.pi * j / 8) * rr, sy * (0.046 + rr * 0.4) + math.sin(2 * math.pi * j / 8) * rr * 0.5, zo)) for j in range(8)]
            rings.append(ring); vs.append(i / 3.0)
        add_lofted_tube(bm, uv, rings, vs, reg)
        path = [Vector((-0.052 + 0.020, sy * 0.012, zo)), Vector((-0.052 + 0.044, sy * 0.036, zo)),
                Vector((-0.052 + 0.055, sy * 0.048, zo))]
        curved_loft(bm, uv, path, lambda t: 0.0035 * (1.0 - t) + 0.0015, 6, "flair")
    commit(obj, bm)

    # Asymmetric guard: light wing (left) + shadow claw (right)
    obj, bm, uv = new_mesh_obj("Guard_DuskWingClaw", col)
    path = [Vector((-0.150, 0.004, 0.096)), Vector((-0.230, 0.008, 0.070)), Vector((-0.290, 0.006, 0.098))]
    path = [Vector((-v.x, v.y, v.z)) for v in path]
    curved_loft(bm, uv, path, lambda t: 0.015 * (1.0 - 0.55 * t) + 0.005, 8, "flair")
    for k, (xo, zo) in enumerate([(-0.052, 0.0)]):
        pass
    path2 = [Vector((0.034, -0.004, 0.098)), Vector((0.088, -0.014, 0.070)),
             Vector((0.128, -0.010, 0.086)), Vector((0.148, 0.002, 0.124))]
    curved_loft(bm, uv, path2, lambda t: 0.013 * (1.0 - 0.5 * t) + 0.004, 8, "flair")
    rings, vs = [], []
    for i, z in enumerate([0.048, 0.088]):
        ring = [Vector((math.cos(2 * math.pi * j / 14) * 0.062, math.sin(2 * math.pi * j / 14) * 0.062 * 0.52, z)) for j in range(14)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Eclipse core: dark ring + bright heart
    obj, bm, uv = new_mesh_obj("Core_EclipseHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.025, 0.026), (0.033, 0.046), (0.023, 0.060), (0.010, 0.066)]):
        z = 0.18 + h2
        ring = [Vector((0.020 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append((0.020 + math.cos(a) * 0.042, math.sin(a) * 0.034, 0.26))
    strip_loft(bm, uv, pts, "flair", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_DuskPactHilt", col)
    grip_braid(bm, uv, 0.048, -0.42, 11, 9, 0.028, 0.005, thick_every=2, thick=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_EclipseOrb", col)
    bulb_pommel(bm, uv, -0.420, [0.013, 0.030, 0.039, 0.033, 0.019, 0.006], 9, squash=1.0, drop=0.095, ring_r=0.038, ring_z=-0.466)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_DuskPactBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.050), (-0.390, -0.418)], 0.033)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "covenant": {
        "name": "sword_08_radiant_covenant", "builder": build_covenant, "tex": "radiant_covenant",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "radiant_covenant"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "radiant_covenant"),
    },
    "bloodmoon": {
        "name": "sword_08_bloodmoon_pact", "builder": build_bloodmoon, "tex": "bloodmoon_pact",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "bloodmoon_pact"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "bloodmoon_pact"),
    },
    "thunderlord": {
        "name": "sword_08_thunderlord_fulgur", "builder": build_thunderlord, "tex": "thunderlord_fulgur",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "thunderlord_fulgur"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "thunderlord_fulgur"),
    },
    "chorus": {
        "name": "sword_08_ancestral_chorus", "builder": build_chorus, "tex": "ancestral_chorus",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "ancestral_chorus"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "ancestral_chorus"),
    },
    "monolith": {
        "name": "sword_08_grimoire_monolith", "builder": build_monolith, "tex": "grimoire_monolith",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "grimoire_monolith"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "grimoire_monolith"),
    },
    "twilight": {
        "name": "sword_08_twilight_covenant", "builder": build_twilight, "tex": "twilight_covenant",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "twilight_covenant"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage08_swords", "twilight_covenant"),
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
    sword = "covenant"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_08_Root", None)
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
    print("STAGE08_BUILD_DONE", sword)

main()

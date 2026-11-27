# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 10: CINCO espadas bespoke (Era III Especializacion II)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage10_swords.py -- sword=halcyon|devourer|permafrost|chakram|chronoglass
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
# A. blessed_halcyon_aegis_broadsword - "Espada Ancha Egida Alcion" (blessed)
# =============================================================================
def build_halcyon(col):
    def hal_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.86 * w,  ht,        z)),
            Vector((xs + 0.62 * w,  ht * 0.72, z)),
            Vector((xs + 0.38 * w,  ht * 0.98, z)),
            Vector((xs + 0.14 * w,  ht * 0.60, z)),
            Vector((xs + 0.04 * w,  ht * 0.24, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.24,z)),
            Vector((xs + 0.14 * w,  -ht * 0.60,z)),
            Vector((xs + 0.38 * w,  -ht * 0.98,z)),
            Vector((xs + 0.62 * w,  -ht * 0.70,z)),
            Vector((xs + 0.86 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.22, 0.50, 0.78, 1.06, 1.34, 1.60, 1.84, 2.02, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = (0.212 - 0.100 * t) * (0.42 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.070, "x_edge": -0.070 + width,
                             "half_t": 0.030 * (1.0 - 0.45 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_BroadHalcyon", col)
    rings, vs = make_rings(stations, hal_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Emblema egida con plumones radiales (x2 caras)
    obj, bm, uv = new_mesh_obj("Emboss_AegisPlume", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (0.15 + 0.70 * j / 24)
            pts.append(Vector((-0.070 + 0.072 + math.cos(a) * 0.058, sy * 0.028, 0.40 - math.sin(a) * 0.046)))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.005)
        for k in range(5):
            a = math.pi * (0.22 + 0.56 * k / 4)
            pts = [Vector((-0.070 + 0.072 + math.cos(a) * 0.030, sy * 0.027, 0.40 - math.sin(a) * 0.024)),
                   Vector((-0.070 + 0.072 + math.cos(a) * 0.052, sy * 0.027, 0.40 - math.sin(a) * 0.042))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Halo de calma
    obj, bm, uv = new_mesh_obj("Inlay_CalmHalo", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append(Vector((-0.070 + 0.060 + math.cos(a) * 0.040, sy * 0.027, 1.28 + math.sin(a) * 0.034)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Guardia egida: semicupula + alas escalonadas
    obj, bm, uv = new_mesh_obj("Guard_AegisWings", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(27):
            a = math.pi * (1.12 + 0.76 * j / 26)
            pts.append(Vector((math.cos(a) * 0.105, sy * 0.028, 0.02 - math.sin(a) * 0.062)))
        strip_loft(bm, uv, pts, "shell", half_w=0.011, half_t=0.008)
        for k in (-1, 0, 1):
            a = math.pi * 0.5 + 0.26 * k
            pts = [Vector((math.cos(a) * 0.105, sy * 0.026, 0.02 - math.sin(a) * 0.062)),
                   Vector((math.cos(a) * (0.148 + 0.012 * abs(k)), sy * 0.026, 0.02 - math.sin(a) * (0.090 + 0.014 * abs(k))))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Cresta de alcion sobre el arco
    obj, bm, uv = new_mesh_obj("Mount_KingfisherCrest", col)
    for sy in (1.0, -1.0):
        pts = [Vector((0.010, sy * 0.024, -0.005)), Vector((0.038, sy * 0.024, 0.010)), Vector((0.072, sy * 0.024, 0.006))]
        strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # nucleo corazon de mareas
    obj, bm, uv = new_mesh_obj("Core_TideHeart", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.15)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.020, math.sin(2 * math.pi * j / 10) * 0.020, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_HalcyonSilk", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_HalcyonPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_PearlOrb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 10, ring_r=0.022, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# B. cursed_soul_devourer_brand - "Blandon Devorador de Almas" (cursed)
# =============================================================================
def build_devourer(col):
    def dev_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.48 * w,  ht * 0.62, z)),
            Vector((xs + 0.18 * w,  ht * 0.90, z)),
            Vector((xs + 0.04 * w,  ht * 0.36, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.36,z)),
            Vector((xs + 0.18 * w,  -ht * 0.90,z)),
            Vector((xs + 0.48 * w,  -ht * 0.62,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.28, 0.56, 0.84, 1.12, 1.40, 1.62, 1.80, 1.94, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        base_w = 0.205 - 0.030 * t
        if i == len(zs) - 1:
            base_w *= 0.86
        stations.append((z, {"x_spine": -0.092, "x_edge": -0.092 + base_w,
                             "half_t": 0.034 * (1.0 - 0.30 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_DevourerMass", col)
    rings, vs = make_rings(stations, dev_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Boca devoradora con dientes cerca de la punta (x2 caras)
    obj, bm, uv = new_mesh_obj("Maw_DevourerTeeth", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(21):
            a = math.pi * (0.25 + 0.85 * j / 20)
            pts.append(Vector((-0.092 + 0.090 + math.cos(a) * 0.055, sy * 0.031, 1.62 - math.sin(a) * 0.036)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
        for k in range(6):
            a = math.pi * (0.30 + 0.72 * k / 5)
            pts = [Vector((-0.092 + 0.090 + math.cos(a) * 0.058, sy * 0.030, 1.62 - math.sin(a) * 0.038)),
                   Vector((-0.092 + 0.090 + math.cos(a) * 0.040, sy * 0.030, 1.62 - math.sin(a) * 0.026))]
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Pozo de animas: anillo doble negro
    obj, bm, uv = new_mesh_obj("Well_SoulPit", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(29):
            a = 2 * math.pi * j / 28
            pts.append(Vector((-0.092 + 0.088 + math.cos(a) * 0.040, sy * 0.031, 0.78 + math.sin(a) * 0.034)))
        strip_loft(bm, uv, pts, "glow", half_w=0.008, half_t=0.006)
        pts = []
        for j in range(19):
            a = 2 * math.pi * j / 18
            pts.append(Vector((-0.092 + 0.088 + math.cos(a) * 0.022, sy * 0.030, 0.78 + math.sin(a) * 0.019)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Guardia mandibulas abiertas (arriba y abajo)
    obj, bm, uv = new_mesh_obj("Guard_JawMaw", col)
    for sgn in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (0.12 + 0.82 * j / 24)
            pts.append(Vector((math.cos(a) * 0.098, 0.028, 0.02 + sgn * math.sin(a) * 0.052)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
    commit(obj, bm)

    # Barbas de cadena en el lomo
    obj, bm, uv = new_mesh_obj("Spine_ChainBarbs", col)
    for k in range(5):
        z0 = 0.42 + 0.26 * k
        xoff = -0.090 if k % 2 == 0 else -0.062
        pts = [Vector((xoff, 0.006, z0)), Vector((xoff - 0.024, 0.010, z0 + 0.038))]
        strip_loft(bm, uv, pts, "shell", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # nucleo brasa de boca de horno
    obj, bm, uv = new_mesh_obj("Core_HellmouthEmber", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.15)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.021, math.sin(2 * math.pi * j / 10) * 0.021, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_DevourerWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_FurnaceBulb", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.022, 0.014, 0.006], 10, squash=1.25, drop=0.100)
    commit(obj, bm)


# =============================================================================
# C. elemental_permafrost_prism_claymore - "Claymore Prisma de Permafrost" (elemental)
# =============================================================================
def build_permafrost(col):
    def perm_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        xm = (xs + xe) * 0.5
        ht = p["half_t"]
        return [
            Vector((xe,  0.0,  z)),
            Vector((xm,  ht,   z)),
            Vector((xs,  0.0,  z)),
            Vector((xm, -ht,   z)),
        ]

    stations = []
    zs = [0.12, 0.42, 0.72, 1.00, 1.26, 1.48, 1.66, 1.80, 1.90, 1.98]
    for i, z in enumerate(zs):
        t = z / 1.98
        width = (0.135 - 0.075 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.046, "x_edge": -0.046 + width,
                             "half_t": 0.026 * (1.0 - 0.45 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_PermafrostPrism", col)
    rings, vs = make_rings(stations, perm_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Espejos articos diagonales (x2 caras)
    obj, bm, uv = new_mesh_obj("Facet_MirrorShards", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            z0 = 0.42 + 0.34 * k
            pts = [Vector((-0.014, sy * 0.024, z0)), Vector((0.018, sy * 0.024, z0 + 0.26))]
            strip_loft(bm, uv, pts, "glow", half_w=0.012, half_t=0.003)
    commit(obj, bm)

    # Cluster de cristales de escarcha flotantes
    obj, bm, uv = new_mesh_obj("Frost_CrystalCluster", col)
    for zc, rr, zz in ((0.55, 0.014, 0.030), (0.92, 0.011, 0.052), (1.28, 0.009, 0.074)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.55, 0.003)):
            rings.append([Vector((-0.040 + math.cos(2 * math.pi * j / 8) * r, zz + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Tres puneas icicle en la punta
    obj, bm, uv = new_mesh_obj("Prongs_IcicleSplit", col)
    for xo in (-0.016, 0.0, 0.016):
        path = [Vector((xo * 0.4, 0, 1.50)), Vector((xo, 0, 1.74)), Vector((xo * 1.7, 0, 1.98))]
        curved_loft(bm, uv, path, lambda t: 0.008, 8, "flair")
    commit(obj, bm)

    # Guardia corona de escarcha
    obj, bm, uv = new_mesh_obj("Guard_FrostCrown", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (1.15 + 0.70 * j / 24)
            pts.append(Vector((math.cos(a) * 0.092, sy * 0.028, 0.02 - math.sin(a) * 0.054)))
        strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.007)
        for k in (-1, 0, 1):
            a = math.pi * 0.5 + 0.22 * k
            pts = [Vector((math.cos(a) * 0.092, sy * 0.026, 0.02 - math.sin(a) * 0.054)),
                   Vector((math.cos(a) * 0.124, sy * 0.026, 0.02 - math.sin(a) * 0.078))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # nucleo congelado
    obj, bm, uv = new_mesh_obj("Core_FrozenCore", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.14)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.019, math.sin(2 * math.pi * j / 10) * 0.019, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_FrostWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0156, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_FrostPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_GlacierOrb", col)
    bulb_pommel(bm, uv, -0.24, [0.028, 0.024, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


# =============================================================================
# D. spiritual_jade_chakram_soulblade - "Espada-Alma de Jade y Chakram" (spiritual)
# =============================================================================
def build_chakram(col):
    def jade_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.002
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.72 * w,  ht,        z)),
            Vector((xs + 0.42 * w,  ht * 0.58, z)),
            Vector((xs + 0.14 * w,  ht * 0.88, z)),
            Vector((xs,             ht * 0.14, z)),
            Vector((xs,             -ht * 0.14,z)),
            Vector((xs + 0.14 * w,  -ht * 0.88,z)),
            Vector((xs + 0.42 * w,  -ht * 0.58,z)),
            Vector((xs + 0.72 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.16, 0.46, 0.76, 1.06, 1.36, 1.62, 1.82, 1.94]
    for i, z in enumerate(zs):
        t = z / 1.94
        width = (0.056 - 0.034 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.026, "x_edge": -0.026 + width,
                             "half_t": 0.010 * (1.0 - 0.40 * t) + 0.002, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_JadeSoul", col)
    rings, vs = make_rings(stations, jade_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Chakram: rueda perpendicular con 8 rayos + buje luminoso
    obj, bm, uv = new_mesh_obj("Chakram_WheelRing", col)
    pts = []
    for j in range(37):
        a = 2 * math.pi * j / 36
        pts.append(Vector((math.cos(a) * 0.086, math.sin(a) * 0.086, 0.135)))
    strip_loft(bm, uv, pts, "flair", half_w=0.013, half_t=0.006)
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts = [Vector((math.cos(a) * 0.020, math.sin(a) * 0.020, 0.135)),
               Vector((math.cos(a) * 0.086, math.sin(a) * 0.086, 0.135))]
        strip_loft(bm, uv, pts, "flair", half_w=0.006, half_t=0.004)
    rings, vs = [], []
    for i, r in enumerate((0.020, 0.024, 0.020)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, 0.135)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Canales de ki serpenteantes (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_KiChannels", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(11):
            z = 0.34 + 1.31 * (j / 10.0)
            pts.append(Vector((-0.026 + 0.026 + 0.006 * math.sin(z * 10.0), sy * 0.010, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Cuentas de ki gemelas
    obj, bm, uv = new_mesh_obj("Beads_KiPair", col)
    for sy in (1.0, -1.0):
        pts = [Vector((0.0, sy * 0.015, 0.20)), Vector((0.0, sy * 0.015, 0.28))]
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    # Tsuba disco de jade
    obj, bm, uv = new_mesh_obj("Tsuba_JadeDisc", col)
    rings, vs = [], []
    for i, z in enumerate((0.095, 0.110)):
        rings.append([Vector((math.cos(2 * math.pi * j / 16) * 0.048, math.sin(2 * math.pi * j / 16) * 0.048, z)) for j in range(16)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Collar_JadeFerrule", col)
    ferrule_pair(bm, uv, [(0.00, 0.05)], 0.0160)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_JadeSilk", col)
    grip_braid(bm, uv, -0.05, -0.27, 10, 8, 0.0148, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_JadeBead", col)
    bulb_pommel(bm, uv, -0.27, [0.024, 0.020, 0.013, 0.005], 10, ring_r=0.018, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# E. arcane_chronoglass_paradox_saber - "Sable Paradoja de Cronocristal" (arcane)
# =============================================================================
def build_chronoglass(col):
    # Hoja sable curva de cristal temporal
    obj, bm, uv = new_mesh_obj("Blade_ChronoSaber", col)
    path = []
    for j in range(11):
        t = j / 10.0
        z = 0.16 + 1.82 * t
        x = 0.070 * (t ** 1.5)
        path.append(Vector((x, 0, z)))
    curved_loft(bm, uv, path, lambda t: 0.030 * (1.0 - 0.58 * t) + 0.004, 10, "blade")
    commit(obj, bm)

    # Ecos-paradoja: 2 fragmentos flotantes paralelos
    obj, bm, uv = new_mesh_obj("Echo_ParadoxShards", col)
    for dx, dy in ((0.052, 0.040), (-0.048, -0.042)):
        path = []
        for j in range(6):
            t = j / 5.0
            z = 0.55 + 0.95 * t
            x = 0.070 * (t ** 1.5) * 0.7 + dx
            path.append(Vector((x, dy, z)))
        curved_loft(bm, uv, path, lambda t: 0.010 * (1.0 - 0.5 * t) + 0.002, 8, "glow")
    commit(obj, bm)

    # Engranaje-rueda del tiempo
    obj, bm, uv = new_mesh_obj("Gear_ChronoRing", col)
    pts = []
    for j in range(33):
        a = 2 * math.pi * j / 32
        pts.append(Vector((math.cos(a) * 0.076, math.sin(a) * 0.076, 0.30)))
    strip_loft(bm, uv, pts, "flair", half_w=0.011, half_t=0.005)
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts = [Vector((math.cos(a) * 0.076, math.sin(a) * 0.076, 0.30)),
               Vector((math.cos(a) * 0.098, math.sin(a) * 0.098, 0.30))]
        strip_loft(bm, uv, pts, "flair", half_w=0.007, half_t=0.004)
    commit(obj, bm)

    # Espiral de tiempo ascendente
    obj, bm, uv = new_mesh_obj("Spiral_TimeCoil", col)
    pts = []
    for j in range(25):
        t = j / 24.0
        z = 0.55 + 1.10 * t
        a = 4.2 * math.pi * t
        r = 0.050 * (1.0 - 0.55 * t)
        pts.append(Vector((0.035 * t + math.cos(a) * r, math.sin(a) * r * 0.5, z)))
    strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Guardia portal de reloj
    obj, bm, uv = new_mesh_obj("Guard_ChronoGate", col)
    for sy in (1.0, -1.0):
        rect = [(-0.048, -0.028, 0.04), (0.068, -0.028, 0.04), (0.068, -0.028, -0.03),
                (-0.048, -0.028, -0.03), (-0.048, -0.028, 0.04)]
        pts = [Vector((rx, sy * 0.028, rz)) for rx, ry, rz in rect]
        strip_loft(bm, uv, pts, "shell", half_w=0.007, half_t=0.006)
    commit(obj, bm)

    # Nucleo reloj de arena
    obj, bm, uv = new_mesh_obj("Core_HourglassCore", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.017), (0.09, 0.005), (0.16, 0.017))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ChronoWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0155, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_ChronoPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_HourglassBulb", col)
    bulb_pommel(bm, uv, -0.24, [0.027, 0.023, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


SWORD_META = {
    "halcyon": {
        "name": "sword_10_halcyon_aegis", "builder": build_halcyon, "tex": "halcyon_aegis",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "halcyon_aegis"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage10_swords", "halcyon_aegis"),
    },
    "devourer": {
        "name": "sword_10_soul_devourer", "builder": build_devourer, "tex": "soul_devourer",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "soul_devourer"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage10_swords", "soul_devourer"),
    },
    "permafrost": {
        "name": "sword_10_permafrost_prism", "builder": build_permafrost, "tex": "permafrost_prism",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "permafrost_prism"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage10_swords", "permafrost_prism"),
    },
    "chakram": {
        "name": "sword_10_jade_chakram", "builder": build_chakram, "tex": "jade_chakram",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "jade_chakram"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage10_swords", "jade_chakram"),
    },
    "chronoglass": {
        "name": "sword_10_chronoglass_paradox", "builder": build_chronoglass, "tex": "chronoglass_paradox",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "chronoglass_paradox"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage10_swords", "chronoglass_paradox"),
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
    sword = "halcyon"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_10_Root", None)
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
    print("STAGE10_BUILD_DONE", sword)


main()

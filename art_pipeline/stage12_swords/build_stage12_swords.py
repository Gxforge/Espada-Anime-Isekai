# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 12: SEIS espadas bespoke (5 linajes + 2a hibrida secreta)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage12_swords.py -- sword=archangel|hellfire|maelstrom|nirvana|archmage|dragon
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
# A. blessed_archangel_verdict_claymore - "Claymore Veredicto de Arcangel" (blessed)
# =============================================================================
def build_archangel(col):
    def arc_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.85 * w,  ht,        z)),
            Vector((xs + 0.60 * w,  ht * 0.70, z)),
            Vector((xs + 0.36 * w,  ht * 0.98, z)),
            Vector((xs + 0.14 * w,  ht * 0.60, z)),
            Vector((xs + 0.04 * w,  ht * 0.24, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.24,z)),
            Vector((xs + 0.14 * w,  -ht * 0.60,z)),
            Vector((xs + 0.36 * w,  -ht * 0.98,z)),
            Vector((xs + 0.60 * w,  -ht * 0.70,z)),
            Vector((xs + 0.85 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.20, 0.48, 0.76, 1.04, 1.32, 1.58, 1.82, 2.02, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.195 - 0.092 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.066, "x_edge": -0.066 + width,
                             "half_t": 0.030 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_ArchangelVerdict", col)
    rings, vs = make_rings(stations, arc_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Arcos catedralicios grabados (x2 caras)
    obj, bm, uv = new_mesh_obj("Emboss_CathedralArches", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            z0 = 0.42 + 0.42 * k
            pts = []
            for j in range(15):
                a = math.pi * j / 14
                pts.append(Vector((-0.066 + 0.050 + math.cos(a) * 0.030, sy * 0.028, z0 + math.sin(a) * 0.032)))
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
            pts = [Vector((-0.066 + 0.020, sy * 0.028, z0)), Vector((-0.066 + 0.020, sy * 0.028, z0 + 0.032)),
                   Vector((-0.066 + 0.080, sy * 0.028, z0))]
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Alas de arcangel ascendiendo desde la guarda (x2, 3 plumas)
    obj, bm, uv = new_mesh_obj("Wings_Archangel", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            x0 = 0.030 + 0.020 * k
            z0 = 0.14 + 0.055 * k
            pts = [Vector((x0, sy * 0.024, z0)), Vector((x0 + 0.006, sy * 0.024, z0 + 0.16 - 0.02 * k))]
            strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.004)
    commit(obj, bm)

    # Guardia facade catedral: barra + arco central
    obj, bm, uv = new_mesh_obj("Guard_CathedralFacade", col)
    for sy in (1.0, -1.0):
        pts = [Vector((-0.105, sy * 0.028, 0.03)), Vector((0.098, sy * 0.028, 0.03))]
        strip_loft(bm, uv, pts, "shell", half_w=0.011, half_t=0.009)
        pts = []
        for j in range(15):
            a = math.pi * j / 14
            pts.append(Vector((-0.066 + 0.064 + math.cos(a) * 0.046, sy * 0.028, 0.03 - math.sin(a) * 0.030)))
        strip_loft(bm, uv, pts, "shell", half_w=0.007, half_t=0.006)
    commit(obj, bm)

    # nucleo gema de veredicto (rombo) + anillo
    obj, bm, uv = new_mesh_obj("Core_VerdictGem", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.04, 0.004), (0.10, 0.019), (0.16, 0.004))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append(Vector((math.cos(a) * 0.030, math.sin(a) * 0.030, 0.10)))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ArchangelSilk", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_ArchangelPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_VerdictGemBulb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 10, ring_r=0.022, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# B. cursed_hellfire_executioner_blade - "Hoja Verdugo de Fuego Infernal" (cursed)
# =============================================================================
def build_hellfire(col):
    def hel_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.50 * w,  ht * 0.64, z)),
            Vector((xs + 0.20 * w,  ht * 0.92, z)),
            Vector((xs + 0.04 * w,  ht * 0.36, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.04 * w,  -ht * 0.36,z)),
            Vector((xs + 0.20 * w,  -ht * 0.92,z)),
            Vector((xs + 0.50 * w,  -ht * 0.64,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.30, 0.60, 0.90, 1.18, 1.42, 1.62, 1.80, 1.94, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        width = (0.210 - 0.085 * t) * (0.55 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.092, "x_edge": -0.092 + width,
                             "half_t": 0.032 * (1.0 - 0.35 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_HellfireCleaver", col)
    rings, vs = make_rings(stations, hel_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Fisuras de fuego infernal (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_HellfireCracks", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            xo = -0.045 + 0.028 * k
            pts = []
            for j in range(9):
                z = 0.30 + 1.30 * (j / 8.0) + 0.05 * k
                pts.append(Vector((xo + 0.010 * math.sin(z * 11.0 + k), sy * 0.031, z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Humo infernal flotante (3 blobs)
    obj, bm, uv = new_mesh_obj("Wisps_HellSmoke", col)
    for cx, cy, zc, rr in ((-0.118, 0.008, 0.92, 0.015), (-0.128, -0.010, 1.24, 0.012), (-0.112, 0.014, 1.52, 0.010)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.55, 0.003)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Guardia capucha: arco frontal + pica
    obj, bm, uv = new_mesh_obj("Guard_HoodArc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(21):
            a = math.pi * (1.05 + 0.90 * j / 20)
            pts.append(Vector((math.cos(a) * 0.098, sy * 0.028, 0.02 - math.sin(a) * 0.058)))
        strip_loft(bm, uv, pts, "shell", half_w=0.011, half_t=0.009)
        pts = [Vector((math.cos(math.pi * 1.5) * 0.098, sy * 0.026, 0.02 - math.sin(math.pi * 1.5) * 0.058)),
               Vector((math.cos(math.pi * 1.5) * 0.135, sy * 0.026, 0.02 - math.sin(math.pi * 1.5) * 0.088))]
        strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # Cadena de condena (5 eslabones en el lomo)
    obj, bm, uv = new_mesh_obj("Chain_Damnation", col)
    for k in range(5):
        zc = 0.40 + 0.26 * k
        pts = []
        for j in range(13):
            a = 2 * math.pi * j / 12
            pts.append(Vector((-0.096 + math.cos(a) * 0.013, math.sin(a) * 0.013, zc)))
        strip_loft(bm, uv, pts, "shell", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # nucleo brasa de horno infernal
    obj, bm, uv = new_mesh_obj("Core_HellfireEmber", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.015), (0.08, 0.021), (0.14, 0.015))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_BoneWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AshDrop", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.022, 0.014, 0.006], 10, squash=1.30, drop=0.100)
    commit(obj, bm)


# =============================================================================
# C. elemental_maelstrom_triad_blade - "Hoja Triada del Maelstrom" (elemental)
# =============================================================================
def build_maelstrom(col):
    # Hoja principal curva
    obj, bm, uv = new_mesh_obj("Blade_MaelstromMain", col)
    path = []
    for j in range(11):
        t = j / 10.0
        z = 0.14 + 1.76 * t
        x = 0.068 * (t ** 1.5)
        path.append(Vector((x, 0, z)))
    curved_loft(bm, uv, path, lambda t: 0.030 * (1.0 - 0.58 * t) + 0.004, 10, "blade")
    commit(obj, bm)

    # Hoja triada A (paralela superior)
    obj, bm, uv = new_mesh_obj("Blade_MaelstromTriA", col)
    path = []
    for j in range(8):
        t = j / 7.0
        z = 0.14 + 1.12 * t
        x = 0.068 * (t ** 1.5) + 0.026
        path.append(Vector((x, 0.044, z)))
    curved_loft(bm, uv, path, lambda t: 0.017 * (1.0 - 0.50 * t) + 0.003, 9, "blade")
    commit(obj, bm)

    # Hoja triada B (paralela inferior)
    obj, bm, uv = new_mesh_obj("Blade_MaelstromTriB", col)
    path = []
    for j in range(8):
        t = j / 7.0
        z = 0.14 + 1.12 * t
        x = 0.068 * (t ** 1.5) + 0.026
        path.append(Vector((x, -0.044, z)))
    curved_loft(bm, uv, path, lambda t: 0.017 * (1.0 - 0.50 * t) + 0.003, 9, "blade")
    commit(obj, bm)

    # Anillos vortice alrededor de la base
    obj, bm, uv = new_mesh_obj("Vortex_WhirlRings", col)
    for z0, rr, turns in ((0.46, 0.052, 2.2), (0.74, 0.060, 1.8)):
        pts = []
        for j in range(29):
            t = j / 28.0
            a = turns * 2 * math.pi * t
            r = rr * (0.75 + 0.25 * t)
            pts.append(Vector((0.030 + math.cos(a) * r, math.sin(a) * r * 1.35, z0 + 0.10 * t)))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Guardia anillo tormenta + 3 puneas a 120 grados
    obj, bm, uv = new_mesh_obj("Guard_StormRingTri", col)
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append(Vector((math.cos(a) * 0.088, math.sin(a) * 0.088, 0.08)))
    strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.007)
    for k in range(3):
        a = 2 * math.pi * k / 3
        pts = [Vector((math.cos(a) * 0.088, math.sin(a) * 0.088, 0.08)),
               Vector((math.cos(a) * 0.126, math.sin(a) * 0.126, 0.08))]
        strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # Surcos de marea en la hoja principal
    obj, bm, uv = new_mesh_obj("Inlay_TideGrooves", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(9):
            t = j / 8.0
            z = 0.32 + 1.30 * t
            x = 0.068 * (t ** 1.5) * 1.0 + 0.020
            pts.append(Vector((x, sy * 0.027, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # nucleo ojo del remolino
    obj, bm, uv = new_mesh_obj("Core_MaelstromEye", col)
    rings, vs = [], []
    for i, z in enumerate((0.06, 0.16)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.018, math.sin(2 * math.pi * j / 10) * 0.018, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_MaelstromBraid", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0158, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_TriadOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.028, 0.024, 0.016, 0.007, 0.004], 10, ring_r=0.022, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# D. spiritual_nirvana_mirror_katana - "Katana Espejo del Nirvana" (spiritual)
# =============================================================================
def build_nirvana(col):
    def nir_section(z, p):
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
    zs = [0.12, 0.44, 0.76, 1.08, 1.40, 1.68, 1.90, 2.04, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.054 - 0.032 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.026, "x_edge": -0.026 + width,
                             "half_t": 0.010 * (1.0 - 0.40 * t) + 0.002, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_NirvanaMirror", col)
    rings, vs = make_rings(stations, nir_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Enso zen abierto flotando tras la hoja
    obj, bm, uv = new_mesh_obj("Zen_EnsoRing", col)
    pts = []
    for j in range(29):
        a = 0.55 + 2 * math.pi * (0.92 * j / 28)
        pts.append(Vector((-0.075 + math.cos(a) * 0.060, 0.006 + math.sin(a) * 0.060, 1.12)))
    strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # Lineas de espejo diagonales (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_MirrorStreaks", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            z0 = 0.55 + 0.42 * k
            t0 = z0 / 2.10
            pts = [Vector((-0.026 + 0.054 * t0 + 0.006, sy * 0.010, z0)),
                   Vector((-0.026 + 0.054 * (t0 + 0.14) + 0.006, sy * 0.010, z0 + 0.24))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.0025)
    commit(obj, bm)

    # Ondas de calma (2 anillos pequenos)
    obj, bm, uv = new_mesh_obj("Zen_CalmRipples", col)
    for zc, rr in ((0.72, 0.030), (0.98, 0.024)):
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            pts.append(Vector((-0.026 + 0.052 * (zc / 2.10) + math.cos(a) * rr, 0.006 + math.sin(a) * rr, zc)))
        strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # Tsuba enso: anillo con hueco
    obj, bm, uv = new_mesh_obj("Tsuba_EnsoTsuba", col)
    pts = []
    for j in range(25):
        a = 0.4 + 2 * math.pi * (0.94 * j / 24)
        pts.append(Vector((math.cos(a) * 0.050, math.sin(a) * 0.050, 0.075)))
    strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.006)
    commit(obj, bm)

    # Menuki espejo gemelo
    obj, bm, uv = new_mesh_obj("Menuki_MirrorPair", col)
    for sy in (1.0, -1.0):
        pts = [Vector((0, sy * 0.015, 0.12)), Vector((0, sy * 0.015, 0.21))]
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Collar_NirvanaFerrule", col)
    ferrule_pair(bm, uv, [(-0.02, -0.06)], 0.0162)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_NirvanaIto", col)
    grip_braid(bm, uv, -0.06, -0.28, 10, 8, 0.0150, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_ZenBead", col)
    bulb_pommel(bm, uv, -0.28, [0.024, 0.020, 0.013, 0.005], 10, ring_r=0.018, ring_z=-0.315)
    commit(obj, bm)


# =============================================================================
# E. arcane_archmage_singularity_blade - "Hoja Singularidad de Archimago" (arcane)
# =============================================================================
def build_archmage(col):
    # Hoja cristal larga y fina (2.16)
    def amg_section(z, p):
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
    zs = [0.14, 0.50, 0.86, 1.18, 1.44, 1.66, 1.84, 1.98, 2.06, 2.12]
    for i, z in enumerate(zs):
        t = z / 2.12
        width = (0.100 - 0.058 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.038, "x_edge": -0.038 + width,
                             "half_t": 0.020 * (1.0 - 0.50 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_ArchmageSingularity", col)
    rings, vs = make_rings(stations, amg_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Orbe singularidad (esfera oscura) + anillo de acrecion
    obj, bm, uv = new_mesh_obj("Singularity_Orb", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.055, 0.020), (0.090, 0.030), (0.125, 0.020))):
        rings.append([Vector((math.cos(2 * math.pi * j / 12) * r, math.sin(2 * math.pi * j / 12) * r, z)) for j in range(12)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    pts = []
    for j in range(33):
        a = 2 * math.pi * j / 32
        pts.append(Vector((math.cos(a) * 0.048, math.sin(a) * 0.048, 0.090)))
    strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # 5 esquirlas orbitando el orbe
    obj, bm, uv = new_mesh_obj("Shards_OrbitSingularity", col)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        rr = 0.062 + 0.008 * (k % 2)
        zc = 0.36 + 0.11 * k
        cx, cy = math.cos(a) * rr, math.sin(a) * rr * 0.8
        rings, vs = [], []
        for i, r in enumerate((0.010, 0.005, 0.002)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 6) * r, cy + math.sin(2 * math.pi * j / 6) * r, zc)) for j in range(6)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Anillo runico grande con marcas
    obj, bm, uv = new_mesh_obj("Ring_ArcaneRunes", col)
    pts = []
    for j in range(33):
        a = 2 * math.pi * j / 32
        pts.append(Vector((math.cos(a) * 0.080, math.sin(a) * 0.080, 0.60)))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.0035)
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts = [Vector((math.cos(a) * 0.080, math.sin(a) * 0.080, 0.60)),
               Vector((math.cos(a) * 0.098, math.sin(a) * 0.098, 0.60))]
        strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # Guardia crescente asimetrico hacia el orbe
    obj, bm, uv = new_mesh_obj("Guard_SingularityCrescent", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(23):
            a = math.pi * (1.10 + 0.80 * j / 22)
            pts.append(Vector((math.cos(a) * 0.092, sy * 0.026, 0.02 - math.sin(a) * 0.055)))
        strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.007)
    commit(obj, bm)

    # Runas diagonales en la hoja (x2 caras)
    obj, bm, uv = new_mesh_obj("Facet_SingularityRunes", col)
    for sy in (1.0, -1.0):
        for k in range(4):
            z0 = 0.90 + 0.26 * k
            pts = [Vector((-0.010, sy * 0.020, z0)), Vector((0.016, sy * 0.020, z0 + 0.20))]
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ArchmageWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0155, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_ArchmagePair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SingularityBead", col)
    bulb_pommel(bm, uv, -0.24, [0.027, 0.023, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


# =============================================================================
# F. hybrid_stormspirit_dragon_katana - "Katana Secreta Dragon de Tormenta y Alma" (HIBRIDA SECRETA)
# =============================================================================
def build_dragon(col):
    def drg_section(z, p):
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
    zs = [0.12, 0.44, 0.76, 1.08, 1.40, 1.68, 1.90, 2.04, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.058 - 0.034 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.028, "x_edge": -0.028 + width,
                             "half_t": 0.010 * (1.0 - 0.40 * t) + 0.002, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_DragonKatana", col)
    rings, vs = make_rings(stations, drg_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Escamas en chevron (x2 caras, 5 filas)
    obj, bm, uv = new_mesh_obj("Scales_DragonChevrons", col)
    for sy in (1.0, -1.0):
        for k in range(5):
            z0 = 0.50 + 0.28 * k
            t0 = z0 / 2.10
            xo = -0.028 + 0.056 * t0
            pts = [Vector((xo + 0.004, sy * 0.010, z0 - 0.035)),
                   Vector((xo + 0.018, sy * 0.010, z0)),
                   Vector((xo + 0.004, sy * 0.010, z0 + 0.035))]
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.0025)
    commit(obj, bm)

    # Cabeza de dragon en la guarda: hocico + cuernos + bigotes
    obj, bm, uv = new_mesh_obj("Head_DragonGuard", col)
    rect = [(-0.020, -0.020, 0.075), (0.054, -0.016, 0.080), (0.054, 0.016, 0.080), (-0.020, 0.020, 0.075), (-0.020, -0.020, 0.075)]
    pts = [Vector((rx, ry, rz)) for rx, ry, rz in rect]
    strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.009)
    for sy in (1.0, -1.0):
        pts = [Vector((0.030, sy * 0.014, 0.088)), Vector((0.006, sy * 0.030, 0.118)), Vector((-0.012, sy * 0.034, 0.146))]
        strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
        pts = [Vector((0.056, sy * 0.008, 0.072)), Vector((0.092, sy * 0.022, 0.056))]
        strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # Espirales de tormenta flotantes (3)
    obj, bm, uv = new_mesh_obj("Wisps_StormCoils", col)
    for z0, rr in ((0.80, 0.036), (1.18, 0.032), (1.55, 0.026)):
        pts = []
        for j in range(23):
            t = j / 22.0
            a = 2.4 * math.pi * t
            r = rr * (0.8 + 0.2 * t)
            pts.append(Vector((-0.028 + 0.056 * ((z0 + 0.14 * t) / 2.10) + math.cos(a) * r, math.sin(a) * r * 0.6, z0 + 0.14 * t)))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Cola de dragon curvada desde el pomo
    obj, bm, uv = new_mesh_obj("Tail_DragonCoil", col)
    path = []
    for j in range(9):
        t = j / 8.0
        z = -0.28 - 0.16 * t
        x = 0.030 * math.sin(t * 3.4)
        path.append(Vector((x, 0.012 * math.cos(t * 3.0), z)))
    curved_loft(bm, uv, path, lambda t: 0.008 * (1.0 - 0.6 * t) + 0.002, 8, "shell")
    commit(obj, bm)

    # nucleo ojo de dragon
    obj, bm, uv = new_mesh_obj("Core_DragonEye", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.005), (0.09, 0.018), (0.16, 0.005))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_DragonSilk", col)
    grip_braid(bm, uv, -0.055, -0.28, 10, 8, 0.0148, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_StormPearl", col)
    bulb_pommel(bm, uv, -0.28, [0.024, 0.020, 0.013, 0.005], 10, ring_r=0.018, ring_z=-0.315)
    commit(obj, bm)


SWORD_META = {
    "archangel": {
        "name": "sword_12_archangel_verdict", "builder": build_archangel, "tex": "archangel_verdict",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "archangel_verdict"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "archangel_verdict"),
    },
    "hellfire": {
        "name": "sword_12_hellfire_executioner", "builder": build_hellfire, "tex": "hellfire_executioner",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "hellfire_executioner"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "hellfire_executioner"),
    },
    "maelstrom": {
        "name": "sword_12_maelstrom_triad", "builder": build_maelstrom, "tex": "maelstrom_triad",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "maelstrom_triad"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "maelstrom_triad"),
    },
    "nirvana": {
        "name": "sword_12_nirvana_mirror", "builder": build_nirvana, "tex": "nirvana_mirror",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "nirvana_mirror"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "nirvana_mirror"),
    },
    "archmage": {
        "name": "sword_12_archmage_singularity", "builder": build_archmage, "tex": "archmage_singularity",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "archmage_singularity"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "archmage_singularity"),
    },
    "dragon": {
        "name": "sword_12_stormspirit_dragon", "builder": build_dragon, "tex": "stormspirit_dragon",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "stormspirit_dragon"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage12_swords", "stormspirit_dragon"),
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
    sword = "archangel"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_12_Root", None)
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
    print("STAGE12_BUILD_DONE", sword)


main()

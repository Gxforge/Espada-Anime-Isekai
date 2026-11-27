# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 11: CINCO espadas bespoke (Era III Especializacion III)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage11_swords.py -- sword=solstice|malakor|pyroclasm|saint|starlight
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
# A. blessed_solstice_martyr_relic - "Reliquia Solar del Solsticio" (blessed)
# =============================================================================
def build_solstice(col):
    def sol_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.85 * w,  ht,        z)),
            Vector((xs + 0.60 * w,  ht * 0.68, z)),
            Vector((xs + 0.36 * w,  ht * 0.98, z)),
            Vector((xs + 0.14 * w,  ht * 0.60, z)),
            Vector((xs + 0.04 * w,  ht * 0.24, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.24,z)),
            Vector((xs + 0.14 * w,  -ht * 0.60,z)),
            Vector((xs + 0.36 * w,  -ht * 0.98,z)),
            Vector((xs + 0.60 * w,  -ht * 0.68,z)),
            Vector((xs + 0.85 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.20, 0.48, 0.76, 1.04, 1.32, 1.58, 1.82, 2.02, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.190 - 0.090 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.064, "x_edge": -0.064 + width,
                             "half_t": 0.029 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_SolsticeRelic", col)
    rings, vs = make_rings(stations, sol_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Guardia disco solar: anillo + 8 rayos de llama
    obj, bm, uv = new_mesh_obj("Guard_SunDisc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(33):
            a = 2 * math.pi * j / 32
            pts.append(Vector((-0.064 + 0.066 + math.cos(a) * 0.085, sy * 0.028, 0.02 + math.sin(a) * 0.085)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for k in range(8):
            a = 2 * math.pi * k / 8
            pts = [Vector((-0.064 + 0.066 + math.cos(a) * 0.085, sy * 0.026, 0.02 + math.sin(a) * 0.085)),
                   Vector((-0.064 + 0.066 + math.cos(a) * 0.122, sy * 0.026, 0.02 + math.sin(a) * 0.122))]
            strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # Halo de martir flotante tras la hoja (doble anillo)
    obj, bm, uv = new_mesh_obj("Halo_MartyrRings", col)
    for zc, rr, sy in ((0.42, 0.048, 0.012), (0.58, 0.034, -0.012)):
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append(Vector((-0.064 - 0.105, sy * 0.008 + math.cos(a) * rr, zc + math.sin(a) * rr)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # Llamas de redencion serpenteantes (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_RedemptionFlames", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(11):
            z = 0.30 + 1.45 * (j / 10.0)
            pts.append(Vector((-0.012 + 0.010 * math.sin(z * 7.5), sy * 0.028, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # nucleo reliquia: capsula con gema
    obj, bm, uv = new_mesh_obj("Core_ReliquaryCapsule", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.06, 0.014), (0.11, 0.019), (0.16, 0.014))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SolsticeSilk", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_SolsticePair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SunOrb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 10, ring_r=0.023, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# B. cursed_malakor_usurper_thorn - "Espina Usurpadora de Malakor" (cursed)
# =============================================================================
def build_malakor(col):
    def mal_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.48 * w,  ht * 0.60, z)),
            Vector((xs + 0.18 * w,  ht * 0.92, z)),
            Vector((xs + 0.04 * w,  ht * 0.34, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.34,z)),
            Vector((xs + 0.18 * w,  -ht * 0.92,z)),
            Vector((xs + 0.48 * w,  -ht * 0.60,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.28, 0.56, 0.84, 1.12, 1.38, 1.60, 1.78, 1.92, 1.98]
    for i, z in enumerate(zs):
        t = z / 1.98
        width = (0.170 - 0.075 * t) * (0.36 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.075, "x_edge": -0.075 + width,
                             "half_t": 0.028 * (1.0 - 0.35 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_UsurperThorn", col)
    rings, vs = make_rings(stations, mal_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Espinas alternadas a lo largo del lomo y el filo
    obj, bm, uv = new_mesh_obj("Thorn_Barbs", col)
    for k in range(7):
        z0 = 0.35 + 0.22 * k
        if k % 2 == 0:
            pts = [Vector((-0.073, 0, z0)), Vector((-0.098, 0, z0 + 0.040))]
        else:
            t0 = z0 / 1.98
            xe0 = -0.075 + (0.170 - 0.075 * t0) * 0.95
            pts = [Vector((xe0, 0, z0)), Vector((xe0 + 0.024, 0, z0 + 0.034))]
        strip_loft(bm, uv, pts, "shell", half_w=0.0045, half_t=0.0045)
    commit(obj, bm)

    # Guardia corona invertida: banda + 5 puntas hacia abajo
    obj, bm, uv = new_mesh_obj("Guard_InvertedCrown", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            pts.append(Vector((math.cos(a) * 0.058, sy * 0.024, 0.055 + math.sin(a) * 0.026)))
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.006)
        for k in range(5):
            a = 2 * math.pi * k / 5
            pts = [Vector((math.cos(a) * 0.058, sy * 0.022, 0.055 + math.sin(a) * 0.026)),
                   Vector((math.cos(a) * 0.082, sy * 0.022, 0.055 + math.sin(a) * 0.038 - 0.055))]
            strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # Sarmientos de espinas enrollados en el grip
    obj, bm, uv = new_mesh_obj("Grip_ThornVines", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0160, 0.0014)
    for k in range(3):
        z0 = -0.06 - 0.07 * k
        pts = [Vector((0.016, 0.004, z0)), Vector((-0.014, -0.006, z0 - 0.028))]
        strip_loft(bm, uv, pts, "shell", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # nucleo corazon de senor demonio
    obj, bm, uv = new_mesh_obj("Core_DemonHeart", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.014), (0.07, 0.020), (0.12, 0.014))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_MalakorPair", col)
    ferrule_pair(bm, uv, [(-0.26, -0.29)], 0.0170)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_ThornBall", col)
    bulb_pommel(bm, uv, -0.29, [0.028, 0.024, 0.016, 0.007, 0.004], 10, squash=1.20, drop=0.095, ring_r=0.021, ring_z=-0.33)
    commit(obj, bm)


# =============================================================================
# C. elemental_pyroclasm_heart_greatsword - "Mandoble Corazon Piroclastico" (elemental)
# =============================================================================
def build_pyroclasm(col):
    def pyr_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.52 * w,  ht * 0.66, z)),
            Vector((xs + 0.22 * w,  ht * 0.94, z)),
            Vector((xs + 0.04 * w,  ht * 0.40, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.04 * w,  -ht * 0.40,z)),
            Vector((xs + 0.22 * w,  -ht * 0.94,z)),
            Vector((xs + 0.52 * w,  -ht * 0.66,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.30, 0.60, 0.90, 1.18, 1.44, 1.66, 1.84, 1.98, 2.04]
    for i, z in enumerate(zs):
        t = z / 2.04
        width = (0.185 - 0.080 * t) * (0.62 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.080, "x_edge": -0.080 + width,
                             "half_t": 0.031 * (1.0 - 0.40 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_ObsidianPyroclasm", col)
    rings, vs = make_rings(stations, pyr_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Venas de magma luminosas (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_MagmaVeins", col)
    for sy in (1.0, -1.0):
        for xo in (-0.010, 0.022):
            pts = []
            for j in range(11):
                z = 0.12 + 1.70 * (j / 10.0)
                pts.append(Vector((xo + 0.008 * math.sin(z * 8.0 + xo * 20.0), sy * 0.030, z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.004)
    commit(obj, bm)

    # Bombas piroclasticas flotantes (3 rocas)
    obj, bm, uv = new_mesh_obj("Bombs_Pyroclastic", col)
    for cx, cy, zc, rr in ((-0.115, 0.010, 0.85, 0.016), (-0.130, -0.008, 1.15, 0.013), (-0.108, 0.016, 1.42, 0.011)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.6, 0.003)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Guardia acantilado basaltico angular
    obj, bm, uv = new_mesh_obj("Guard_BasaltCliff", col)
    for sy in (1.0, -1.0):
        rect = [(-0.088, -0.030, 0.045), (0.068, -0.030, 0.045), (0.068, -0.030, -0.025),
                (-0.088, -0.030, -0.025), (-0.088, -0.030, 0.045)]
        pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect]
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
    commit(obj, bm)

    # nucleo corazon eruptivo (bomba con 3 llama-picos)
    obj, bm, uv = new_mesh_obj("Core_EruptionHeart", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.016), (0.07, 0.022), (0.12, 0.016))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    for k in range(3):
        a = 2 * math.pi * k / 3
        pts = [Vector((math.cos(a) * 0.016, math.sin(a) * 0.016, 0.115)),
               Vector((math.cos(a) * 0.006, math.sin(a) * 0.006, 0.155))]
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.0035)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_CharredWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_MagmaOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.023, 0.015, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# D. spiritual_reincarnated_saint_edge - "Filo del Santo Reencarnado" (spiritual)
# =============================================================================
def build_saint(col):
    def st_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.002
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.74 * w,  ht,        z)),
            Vector((xs + 0.44 * w,  ht * 0.62, z)),
            Vector((xs + 0.14 * w,  ht * 0.90, z)),
            Vector((xs,             ht * 0.15, z)),
            Vector((xs,             -ht * 0.15,z)),
            Vector((xs + 0.14 * w,  -ht * 0.90,z)),
            Vector((xs + 0.44 * w,  -ht * 0.62,z)),
            Vector((xs + 0.74 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.10, 0.42, 0.74, 1.06, 1.38, 1.68, 1.92, 2.08, 2.15]
    for i, z in enumerate(zs):
        t = z / 2.15
        width = (0.062 - 0.036 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.028, "x_edge": -0.028 + width,
                             "half_t": 0.011 * (1.0 - 0.40 * t) + 0.002, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_SaintSilver", col)
    rings, vs = make_rings(stations, st_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Ecos de vidas pasadas: 3 anillos flotantes escalonados
    obj, bm, uv = new_mesh_obj("Echo_PastLifeRings", col)
    for cx, cy, zc, rr in ((0.058, 0.014, 0.90, 0.026), (0.070, -0.010, 1.22, 0.021), (0.055, 0.012, 1.52, 0.017)):
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            pts.append(Vector((cx + math.cos(a) * rr, cy + math.sin(a) * rr, zc)))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Halo santo doble tras la base
    obj, bm, uv = new_mesh_obj("Halo_SaintHalo", col)
    for zc, rr in ((0.34, 0.050), (0.44, 0.036)):
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append(Vector((-0.028 - 0.098, 0.004 + math.cos(a) * rr, zc + math.sin(a) * rr)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # Espiral de reencarnacion en la base (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_RebirthSpiral", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(15):
            t = j / 14.0
            z = 0.22 + 0.50 * t
            pts.append(Vector((-0.028 + 0.028 + 0.020 * t, sy * 0.011, z - 0.014 * math.sin(t * 9.4))))
        strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Tsuba loto: anillo + 6 petalos
    obj, bm, uv = new_mesh_obj("Tsuba_LotusRing", col)
    rings, vs = [], []
    for i, z in enumerate((0.062, 0.072)):
        rings.append([Vector((math.cos(2 * math.pi * j / 16) * 0.052, math.sin(2 * math.pi * j / 16) * 0.052, z)) for j in range(16)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    for k in range(6):
        a = 2 * math.pi * k / 6
        pts = [Vector((math.cos(a) * 0.052, math.sin(a) * 0.052, 0.067)),
               Vector((math.cos(a) * 0.070, math.sin(a) * 0.070, 0.067))]
        strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Collar_SaintFerrule", col)
    ferrule_pair(bm, uv, [(-0.02, -0.06)], 0.0162)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SaintSilk", col)
    grip_braid(bm, uv, -0.06, -0.28, 10, 8, 0.0150, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SaintGem", col)
    bulb_pommel(bm, uv, -0.28, [0.024, 0.020, 0.013, 0.005], 10, ring_r=0.018, ring_z=-0.315)
    commit(obj, bm)


# =============================================================================
# E. arcane_starlight_glyph_claymore - "Claymore Glifo de Luz Estelar" (arcane)
# =============================================================================
def build_starlight(col):
    def star_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.003
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.58 * w,  ht * 0.68, z)),
            Vector((xs + 0.34 * w,  ht * 0.98, z)),
            Vector((xs + 0.13 * w,  ht * 0.60, z)),
            Vector((xs + 0.04 * w,  ht * 0.24, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.24,z)),
            Vector((xs + 0.13 * w,  -ht * 0.60,z)),
            Vector((xs + 0.34 * w,  -ht * 0.98,z)),
            Vector((xs + 0.58 * w,  -ht * 0.68,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.22, 0.50, 0.78, 1.06, 1.34, 1.60, 1.84, 2.02, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        width = (0.180 - 0.090 * t) * (0.36 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.062, "x_edge": -0.062 + width,
                             "half_t": 0.027 * (1.0 - 0.48 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_StarGlyphClaymore", col)
    rings, vs = make_rings(stations, star_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Constelacion: 4 segmentos de linea + 4 estrellas-punto (x2 caras)
    obj, bm, uv = new_mesh_obj("Glyph_Constellation", col)
    for sy in (1.0, -1.0):
        for (z1, z2, xo1, xo2) in ((0.45, 0.78, -0.020, 0.006), (0.78, 1.05, 0.006, 0.030), (1.05, 1.42, 0.030, 0.004), (1.42, 1.70, 0.004, 0.026)):
            pts = [Vector((xo1, sy * 0.026, z1)), Vector((xo2, sy * 0.026, z2))]
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
        for (zc, xo) in ((0.45, -0.020), (0.78, 0.006), (1.05, 0.030), (1.70, 0.026)):
            rings, vs = [], []
            for i, r in enumerate((0.012, 0.006, 0.002)):
                rings.append([Vector((xo + math.cos(2 * math.pi * j / 8) * r, sy * 0.026 + math.sin(2 * math.pi * j / 8) * r * 0.4, zc)) for j in range(8)])
                vs.append(i / 2.0)
            add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Guardia anillo estelar con 5 puntas-estrella
    obj, bm, uv = new_mesh_obj("Guard_StarRing", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(29):
            a = 2 * math.pi * j / 28
            pts.append(Vector((-0.062 + 0.064 + math.cos(a) * 0.078, sy * 0.028, 0.02 + math.sin(a) * 0.078)))
        strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.007)
        for k in range(5):
            a = 2 * math.pi * k / 5
            pts = [Vector((-0.062 + 0.064 + math.cos(a) * 0.078, sy * 0.026, 0.02 + math.sin(a) * 0.078)),
                   Vector((-0.062 + 0.064 + math.cos(a) * 0.112, sy * 0.026, 0.02 + math.sin(a) * 0.112))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.005)
            rings, vs = [], []
            for i, r in enumerate((0.012, 0.005)):
                rings.append([Vector((-0.062 + 0.064 + math.cos(a) * 0.116 + math.cos(2 * math.pi * j / 6) * r, sy * 0.026, 0.02 + math.sin(a) * 0.116 + math.sin(2 * math.pi * j / 6) * r)) for j in range(6)])
                vs.append(i)
            add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Estrellas orbitantes diminutas (4)
    obj, bm, uv = new_mesh_obj("Stars_OrbitSet", col)
    for cx, cy, zc, rr in ((-0.098, 0.012, 1.12, 0.010), (-0.108, -0.010, 1.36, 0.008), (-0.092, 0.016, 1.58, 0.007), (-0.104, -0.006, 1.78, 0.006)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.5, 0.002)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # nucleo gema estrella (octaedro aproximado)
    obj, bm, uv = new_mesh_obj("Core_StarGem", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.004), (0.09, 0.018), (0.16, 0.004))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StarWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0157, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_StarOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.023, 0.015, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.295)
    commit(obj, bm)


SWORD_META = {
    "solstice": {
        "name": "sword_11_solstice_relic", "builder": build_solstice, "tex": "solstice_relic",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "solstice_relic"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage11_swords", "solstice_relic"),
    },
    "malakor": {
        "name": "sword_11_malakor_thorn", "builder": build_malakor, "tex": "malakor_thorn",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "malakor_thorn"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage11_swords", "malakor_thorn"),
    },
    "pyroclasm": {
        "name": "sword_11_pyroclasm_heart", "builder": build_pyroclasm, "tex": "pyroclasm_heart",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "pyroclasm_heart"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage11_swords", "pyroclasm_heart"),
    },
    "saint": {
        "name": "sword_11_saint_reincarnated", "builder": build_saint, "tex": "saint_reincarnated",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "saint_reincarnated"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage11_swords", "saint_reincarnated"),
    },
    "starlight": {
        "name": "sword_11_starlight_glyph", "builder": build_starlight, "tex": "starlight_glyph",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "starlight_glyph"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage11_swords", "starlight_glyph"),
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
    sword = "solstice"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_11_Root", None)
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
    print("STAGE11_BUILD_DONE", sword)


main()

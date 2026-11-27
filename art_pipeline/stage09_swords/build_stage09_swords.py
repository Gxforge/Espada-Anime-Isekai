# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 09: CINCO espadas bespoke (Era III Especializacion)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage09_swords.py -- sword=dawnbreaker|guillotine|monsoon|nodachi|prism
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
# A. blessed_dawnbreaker_templar_blade - "Hoja Templaria Rompealbas" (blessed)
# =============================================================================
def build_dawnbreaker(col):
    def dawn_section(z, p):
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
    zs = [0.06, 0.20, 0.48, 0.76, 1.04, 1.32, 1.58, 1.82, 2.02, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.180 - 0.085 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.058, "x_edge": -0.058 + width,
                             "half_t": 0.028 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_TemplarDawn", col)
    rings, vs = make_rings(stations, dawn_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Rayos de amanecer en abanico cerca de la punta (x2 caras)
    obj, bm, uv = new_mesh_obj("Emboss_DawnRays", col)
    for sy in (1.0, -1.0):
        for k in range(5):
            z0 = 1.35 + 0.10 * k
            x0 = -0.030 + 0.014 * k
            pts = [Vector((x0, sy * 0.026, z0)), Vector((x0 + 0.010, sy * 0.026, z0 + 0.105))]
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Linea de templado luminosa a lo largo de la cara
    obj, bm, uv = new_mesh_obj("Inlay_TemperLine", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(9):
            z = 0.35 + 1.50 * (j / 8.0)
            pts.append(Vector((-0.012, sy * 0.027, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.0045)
    commit(obj, bm)

    # Guardia: arco de sol naciente
    obj, bm, uv = new_mesh_obj("Guard_SunArc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(29):
            a = math.pi * (1.15 + 0.70 * j / 28)
            pts.append(Vector((math.cos(a) * 0.095, sy * 0.028, 0.02 - math.sin(a) * 0.055)))
        strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.0075)
    commit(obj, bm)

    # Rayos irradiando desde el arco
    obj, bm, uv = new_mesh_obj("Mount_GuardSpokes", col)
    for sy in (1.0, -1.0):
        for k in (-2, -1, 1, 2):
            a = math.pi * 0.5 + 0.20 * k
            pts = [Vector((math.cos(a) * 0.095, sy * 0.026, 0.02 - math.sin(a) * 0.055)),
                   Vector((math.cos(a) * 0.132, sy * 0.026, 0.02 - math.sin(a) * 0.078))]
            strip_loft(bm, uv, pts, "shell", half_w=0.004, half_t=0.0035)
    commit(obj, bm)

    # nucleo reliquia solar
    obj, bm, uv = new_mesh_obj("Core_SolarReliquary", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.16)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.020, math.sin(2 * math.pi * j / 10) * 0.020, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_TemplarWrap", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0165, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SunRing", col)
    bulb_pommel(bm, uv, -0.26, [0.030, 0.026, 0.020, 0.012, 0.005], 10, ring_r=0.024, ring_z=-0.30)
    commit(obj, bm)


# =============================================================================
# B. cursed_abyssal_guillotine_edge - "Filo Guillotina del Abismo" (cursed)
# =============================================================================
def build_guillotine(col):
    def gil_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.50 * w,  ht * 0.66, z)),
            Vector((xs + 0.20 * w,  ht * 0.92, z)),
            Vector((xs + 0.05 * w,  ht * 0.40, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.05 * w,  -ht * 0.40,z)),
            Vector((xs + 0.20 * w,  -ht * 0.92,z)),
            Vector((xs + 0.50 * w,  -ht * 0.66,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.30, 0.60, 0.90, 1.20, 1.50, 1.75, 1.95, 2.02, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = (0.200 - 0.045 * t) * (0.72 if i == len(zs) - 1 else 1.0)
        x_edge = -0.090 + width + (0.018 if i == len(zs) - 1 else 0.0)
        stations.append((z, {"x_spine": -0.090, "x_edge": x_edge,
                             "half_t": 0.030 * (1.0 - 0.35 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_AbyssGuillotine", col)
    rings, vs = make_rings(stations, gil_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Aparturas hexagonales en la masa del filo (x2 caras)
    obj, bm, uv = new_mesh_obj("Holes_AbyssAperture", col)
    for sy in (1.0, -1.0):
        for zc, rr in ((0.85, 0.034), (1.25, 0.026)):
            pts = []
            for j in range(13):
                a = 2 * math.pi * j / 12
                pts.append(Vector((-0.030 + math.cos(a) * rr, sy * 0.030, zc + math.sin(a) * rr * 1.15)))
            strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Venas de vacio brillantes full-length
    obj, bm, uv = new_mesh_obj("Inlay_RoseVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(11):
            z = 0.10 + 1.80 * (j / 10.0)
            pts.append(Vector((-0.045 + 0.012 * math.sin(z * 9.0), sy * 0.029, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Guardia: boca del abismo (crescente invertido + cuernos)
    obj, bm, uv = new_mesh_obj("Guard_AbyssMaw", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (1.10 + 0.80 * j / 24)
            pts.append(Vector((math.cos(a) * 0.100, sy * 0.028, 0.02 - math.sin(a) * 0.060)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for a0 in (math.pi * 1.10, math.pi * 1.90):
            pts = [Vector((math.cos(a0) * 0.100, sy * 0.026, 0.02 - math.sin(a0) * 0.060)),
                   Vector((math.cos(a0) * 0.135, sy * 0.026, 0.02 - math.sin(a0) * 0.085))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Espinas de tortura a lo largo del lomo
    obj, bm, uv = new_mesh_obj("Spine_TortureBarbs", col)
    for k in range(6):
        z0 = 0.50 + 0.24 * k
        pts = [Vector((-0.088, 0, z0)), Vector((-0.112, 0, z0 + 0.045))]
        strip_loft(bm, uv, pts, "shell", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_VoidHeart", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.16)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.021, math.sin(2 * math.pi * j / 10) * 0.021, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_AbyssWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BloodDrop", col)
    bulb_pommel(bm, uv, -0.25, [0.026, 0.021, 0.014, 0.006], 10, squash=1.35, drop=0.100)
    commit(obj, bm)


# =============================================================================
# C. elemental_twin_monsoon_saber - "Sable Gemelo del Monzon" (elemental)
# =============================================================================
def build_monsoon(col):
    # Hoja principal curva (sable)
    obj, bm, uv = new_mesh_obj("Blade_MonsoonMain", col)
    path = []
    for j in range(11):
        t = j / 10.0
        z = 0.14 + 1.84 * t
        x = 0.075 * (t ** 1.6)
        path.append(Vector((x, 0, z)))
    curved_loft(bm, uv, path, lambda t: 0.033 * (1.0 - 0.60 * t) + 0.004, 10, "blade")
    commit(obj, bm)

    # Hoja gemela paralela mas corta
    obj, bm, uv = new_mesh_obj("Blade_MonsoonTwin", col)
    path = []
    for j in range(9):
        t = j / 8.0
        z = 0.14 + 1.18 * t
        x = 0.075 + 0.050 * (t ** 1.6)
        path.append(Vector((x, 0, z)))
    curved_loft(bm, uv, path, lambda t: 0.024 * (1.0 - 0.55 * t) + 0.003, 10, "blade")
    commit(obj, bm)

    # Horquilla que bifurca la guarda hacia la gemela
    obj, bm, uv = new_mesh_obj("Fork_TwinSplit", col)
    for x0 in (0.012, -0.012):
        path = [Vector((x0, 0, 0.16)), Vector((0.038 + (0.012 if x0 > 0 else -0.012), 0, 0.26)),
                Vector((0.072, 0, 0.36))]
        curved_loft(bm, uv, path, lambda t: 0.010, 8, "shell")
    commit(obj, bm)

    # Guardia crescente monzon
    obj, bm, uv = new_mesh_obj("Guard_MonsoonCrescent", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(23):
            a = math.pi * (1.12 + 0.76 * j / 22)
            pts.append(Vector((math.cos(a) * 0.088, sy * 0.026, 0.02 - math.sin(a) * 0.052)))
        strip_loft(bm, uv, pts, "shell", half_w=0.009, half_t=0.007)
    commit(obj, bm)

    # Surcos de lluvia sobre la hoja principal
    obj, bm, uv = new_mesh_obj("Inlay_RainGrooves", col)
    for sy in (1.0, -1.0):
        for xo in (0.030, 0.048):
            pts = []
            for j in range(9):
                t = j / 8.0
                z = 0.30 + 1.45 * t
                x = 0.075 * (t ** 1.6) + xo
                pts.append(Vector((x, sy * 0.030, z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_StormEye", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.15)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.019, math.sin(2 * math.pi * j / 10) * 0.019, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StormBraid", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0158, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_MonsoonPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0185)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_StormOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.028, 0.024, 0.017, 0.008, 0.004], 10, ring_r=0.022, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# D. spiritual_phantom_sever_nodachi - "Nodachi Cortafantasmas" (spiritual)
# =============================================================================
def build_nodachi(col):
    def noda_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.002
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.72 * w,  ht,        z)),
            Vector((xs + 0.40 * w,  ht * 0.60, z)),
            Vector((xs + 0.12 * w,  ht * 0.90, z)),
            Vector((xs,             ht * 0.15, z)),
            Vector((xs,             -ht * 0.15,z)),
            Vector((xs + 0.12 * w,  -ht * 0.90,z)),
            Vector((xs + 0.40 * w,  -ht * 0.60,z)),
            Vector((xs + 0.72 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.10, 0.40, 0.75, 1.10, 1.45, 1.75, 2.00, 2.15, 2.22]
    for i, z in enumerate(zs):
        t = z / 2.22
        width = (0.052 - 0.030 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.024 + 0.050 * t, "x_edge": -0.024 + 0.050 * t + width,
                             "half_t": 0.010 * (1.0 - 0.40 * t) + 0.002, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_PhantomNodachi", col)
    rings, vs = make_rings(stations, noda_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Hamon ondulado espectral
    obj, bm, uv = new_mesh_obj("Inlay_GhostHamon", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(13):
            z = 0.25 + 1.80 * (j / 12.0)
            t = z / 2.22
            pts.append(Vector((-0.024 + 0.050 * t + 0.020 + 0.006 * math.sin(z * 14.0), sy * 0.011, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    # Wisps flotantes de fuego fantasma
    obj, bm, uv = new_mesh_obj("Wisps_GhostFlame", col)
    for cx, cy, zc in ((0.06, 0.02, 1.55), (0.08, -0.01, 1.75), (0.05, 0.015, 1.92)):
        rings, vs = [], []
        for i, rr in enumerate((0.016, 0.012, 0.006)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * rr, cy + math.sin(2 * math.pi * j / 8) * rr, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Tsuba sello espectral
    obj, bm, uv = new_mesh_obj("Tsuba_PhantomSeal", col)
    rings, vs = [], []
    for i, z in enumerate((0.058, 0.068)):
        rings.append([Vector((math.cos(2 * math.pi * j / 16) * 0.055, math.sin(2 * math.pi * j / 16) * 0.055, z)) for j in range(16)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    # Menuki gemelos espectrales
    obj, bm, uv = new_mesh_obj("Menuki_GhostPair", col)
    for sy in (1.0, -1.0):
        pts = [Vector((0, sy * 0.016, 0.10)), Vector((0, sy * 0.016, 0.20))]
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Collar_TealFerrule", col)
    ferrule_pair(bm, uv, [(-0.02, -0.06)], 0.0170)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SilkIto", col)
    grip_braid(bm, uv, -0.06, -0.28, 10, 8, 0.0150, 0.0013)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_KabutoGashira", col)
    bulb_pommel(bm, uv, -0.28, [0.024, 0.020, 0.013, 0.005], 10, ring_r=0.018, ring_z=-0.315)
    commit(obj, bm)


# =============================================================================
# E. arcane_spellweaver_prism_edge - "Filo Prisma Tejehechizos" (arcane)
# =============================================================================
def build_prism(col):
    def prism_section(z, p):
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
    zs = [0.12, 0.45, 0.80, 1.10, 1.35, 1.55, 1.70, 1.80, 1.86]
    for i, z in enumerate(zs):
        t = z / 1.86
        width = (0.105 - 0.050 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.040, "x_edge": -0.040 + width,
                             "half_t": 0.024 * (1.0 - 0.50 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_PrismCrystal", col)
    rings, vs = make_rings(stations, prism_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Tres puntas de prisma que se dividen al final
    obj, bm, uv = new_mesh_obj("Prongs_PrismSplit", col)
    for xo in (-0.018, 0.0, 0.018):
        path = [Vector((xo * 0.4, 0, 1.42)), Vector((xo, 0, 1.64)), Vector((xo * 1.6, 0, 1.90))]
        curved_loft(bm, uv, path, lambda t: 0.009, 8, "flair")
    commit(obj, bm)

    # Retricula de runas diagonales (x2 caras)
    obj, bm, uv = new_mesh_obj("Facet_RuneLattice", col)
    for sy in (1.0, -1.0):
        for k in range(4):
            z0 = 0.35 + 0.30 * k
            pts = [Vector((-0.010, sy * 0.024, z0)), Vector((0.020, sy * 0.024, z0 + 0.22))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Guardia marco de grimorio abierto
    obj, bm, uv = new_mesh_obj("Guard_SpellbookFrame", col)
    frame = []
    rect = [(-0.055, -0.030, 0.04), (0.075, -0.030, 0.04), (0.075, -0.030, -0.03),
            (-0.055, -0.030, -0.03), (-0.055, -0.030, 0.04)]
    for sy in (1.0, -1.0):
        pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect]
        strip_loft(bm, uv, pts, "shell", half_w=0.007, half_t=0.006)
    commit(obj, bm)

    # Anillo orbitante de fragmentos arcanos
    obj, bm, uv = new_mesh_obj("Shard_OrbitRing", col)
    for k in range(6):
        a = 2 * math.pi * k / 6
        cx, cy = math.cos(a) * 0.085, math.sin(a) * 0.085
        rings, vs = [], []
        for i, rr in enumerate((0.011, 0.005)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 6) * rr, cy + math.sin(2 * math.pi * j / 6) * rr, 1.12)) for j in range(6)])
            vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_ArcanePrism", col)
    rings, vs = [], []
    for i, z in enumerate((0.02, 0.14)):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.018, math.sin(2 * math.pi * j / 10) * 0.018, z)) for j in range(10)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_PrismWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0155, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_PrismPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_PrismShard", col)
    bulb_pommel(bm, uv, -0.24, [0.027, 0.023, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


SWORD_META = {
    "dawnbreaker": {
        "name": "sword_09_dawnbreaker_templar", "builder": build_dawnbreaker, "tex": "dawnbreaker_templar",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "dawnbreaker_templar"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage09_swords", "dawnbreaker_templar"),
    },
    "guillotine": {
        "name": "sword_09_abyssal_guillotine", "builder": build_guillotine, "tex": "abyssal_guillotine",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "abyssal_guillotine"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage09_swords", "abyssal_guillotine"),
    },
    "monsoon": {
        "name": "sword_09_twin_monsoon", "builder": build_monsoon, "tex": "twin_monsoon",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "twin_monsoon"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage09_swords", "twin_monsoon"),
    },
    "nodachi": {
        "name": "sword_09_phantom_nodachi", "builder": build_nodachi, "tex": "phantom_nodachi",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "phantom_nodachi"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage09_swords", "phantom_nodachi"),
    },
    "prism": {
        "name": "sword_09_spellweaver_prism", "builder": build_prism, "tex": "spellweaver_prism",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "spellweaver_prism"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage09_swords", "spellweaver_prism"),
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
    sword = "dawnbreaker"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_09_Root", None)
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
    print("STAGE09_BUILD_DONE", sword)


main()

# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 14: CINCO espadas bespoke (Era IV Afinidad VII)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage14_swords.py -- sword=sunforge|leviathan|tectonic|astral|tesseract
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
# A. blessed_sanctified_sunforge_sword - "Espada Forjasol Santificada" (blessed)
# =============================================================================
def build_sunforge(col):
    def sun_section(z, p):
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
    zs = [0.06, 0.20, 0.48, 0.76, 1.04, 1.32, 1.58, 1.82, 2.02, 2.10]
    for i, z in enumerate(zs):
        t = z / 2.10
        width = (0.192 - 0.094 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.066, "x_edge": -0.066 + width,
                             "half_t": 0.030 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_Sunforged", col)
    rings, vs = make_rings(stations, sun_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Costuras de forja diagonales (x2 caras)
    obj, bm, uv = new_mesh_obj("Seam_ForgeLines", col)
    for sy in (1.0, -1.0):
        for k in range(3):
            z0 = 0.45 + 0.36 * k
            pts = [Vector((-0.020, sy * 0.028, z0)), Vector((0.024, sy * 0.028, z0 + 0.30))]
            strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Llamas solares ascendentes (3)
    obj, bm, uv = new_mesh_obj("Flames_RisingSolar", col)
    for cx, cy, zc, rr in ((-0.098, 0.010, 0.80, 0.014), (-0.108, -0.010, 1.12, 0.012), (-0.094, 0.014, 1.44, 0.010)):
        rings, vs = [], []
        for i, (r, zo) in enumerate(((rr, 0.0), (rr * 0.55, 0.035), (0.003, 0.06))):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc + zo)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Guardia yunque-forja: anillo + tenazas x2
    obj, bm, uv = new_mesh_obj("Guard_AnvilForge", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(29):
            a = 2 * math.pi * j / 28
            pts.append(Vector((-0.066 + 0.066 + math.cos(a) * 0.082, sy * 0.028, 0.02 + math.sin(a) * 0.082)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for sx in (-1.0, 1.0):
            pts = [Vector((-0.066 + 0.066 + sx * 0.082, sy * 0.026, 0.02)),
                   Vector((-0.066 + 0.066 + sx * 0.122, sy * 0.026, 0.055))]
            strip_loft(bm, uv, pts, "shell", half_w=0.006, half_t=0.005)
    commit(obj, bm)

    # nucleo crisol con orbe fundido
    obj, bm, uv = new_mesh_obj("Core_CrucibleOrb", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.03, 0.016), (0.09, 0.023), (0.15, 0.016))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ForgeLeather", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AnvilBulb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 10, ring_r=0.022, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# B. cursed_dread_leviathan_fang - "Colmillo Aterrador de Leviatan" (cursed)
# =============================================================================
def build_leviathan(col):
    # Colmillo curvado organico (grueso en base, punta afilada)
    obj, bm, uv = new_mesh_obj("Fang_Leviathan", col)
    path = []
    for j in range(12):
        t = j / 11.0
        z = 0.10 + 1.80 * t
        x = 0.020 + 0.105 * (t ** 1.7)
        path.append(Vector((x, 0, z)))
    curved_loft(bm, uv, path, lambda t: 0.052 * ((1.0 - t) ** 1.25) + 0.005, 10, "blade")
    commit(obj, bm)

    # Ventosas en 2 filas a lo largo del colmillo
    obj, bm, uv = new_mesh_obj("Suckers_LeviathanRows", col)
    for sy in (1.0, -1.0):
        for k in range(6):
            t = 0.12 + 0.13 * k
            z = 0.10 + 1.55 * t
            x = 0.020 + 0.105 * (t ** 1.7) - 0.020
            rings, vs = [], []
            for i, r in enumerate((0.011 * (1.0 - 0.5 * t), 0.006, 0.002)):
                rings.append([Vector((x + math.cos(2 * math.pi * j / 8) * r, sy * (0.040 - 0.020 * t) + math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
                vs.append(i / 2.0)
            add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Anillos de bernardos ermitanos (2)
    obj, bm, uv = new_mesh_obj("Barnacle_Rings", col)
    for t0, rr in ((0.30, 0.052), (0.55, 0.044)):
        z = 0.10 + 1.55 * t0
        x = 0.020 + 0.105 * (t0 ** 1.7)
        pts = []
        for j in range(21):
            a = 2 * math.pi * j / 20
            pts.append(Vector((x + math.cos(a) * rr, math.sin(a) * rr, z)))
        strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Guardia mandibula con 4 colmillos menores
    obj, bm, uv = new_mesh_obj("Guard_LeviathanJaw", col)
    for sgn in (1.0, -1.0):
        pts = []
        for j in range(21):
            a = math.pi * (0.15 + 0.80 * j / 20)
            pts.append(Vector((math.cos(a) * 0.095, 0.028, 0.02 + sgn * math.sin(a) * 0.048)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for k in range(4):
            a = math.pi * (0.25 + 0.60 * k / 3)
            pts = [Vector((math.cos(a) * 0.095, 0.026, 0.02 + sgn * math.sin(a) * 0.048)),
                   Vector((math.cos(a) * 0.124, 0.026, 0.02 + sgn * math.sin(a) * 0.036))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # nucleo ojo de fosa
    obj, bm, uv = new_mesh_obj("Core_TrenchEye", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.005), (0.09, 0.019), (0.16, 0.005))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_KelpWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0158, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_TailFin", col)
    bulb_pommel(bm, uv, -0.25, [0.028, 0.024, 0.016, 0.007, 0.004], 10, squash=1.45, drop=0.100)
    commit(obj, bm)


# =============================================================================
# C. elemental_tectonic_mantle_breaker - "Quebrantamantos Tectonico" (elemental)
# =============================================================================
def build_tectonic(col):
    def tec_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.005
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.56 * w,  ht * 0.68, z)),
            Vector((xs + 0.30 * w,  ht * 0.98, z)),
            Vector((xs + 0.10 * w,  ht * 0.58, z)),
            Vector((xs + 0.02 * w,  ht * 0.22, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.02 * w,  -ht * 0.22,z)),
            Vector((xs + 0.10 * w,  -ht * 0.58,z)),
            Vector((xs + 0.30 * w,  -ht * 0.98,z)),
            Vector((xs + 0.56 * w,  -ht * 0.68,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.30, 0.58, 0.86, 1.12, 1.36, 1.58, 1.78, 1.94, 2.00]
    for i, z in enumerate(zs):
        t = z / 2.00
        width = (0.205 - 0.100 * t) * (0.62 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.085, "x_edge": -0.085 + width,
                             "half_t": 0.034 * (1.0 - 0.42 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Slab_TectonicBreaker", col)
    rings, vs = make_rings(stations, tec_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Fallas de lava zigzag (x2 caras)
    obj, bm, uv = new_mesh_obj("Faults_LavaLines", col)
    for sy in (1.0, -1.0):
        for k, xo in enumerate((-0.030, 0.014)):
            pts = []
            for j in range(11):
                z = 0.20 + 1.55 * (j / 10.0)
                pts.append(Vector((xo + 0.012 * math.sin(z * 10.0 + k * 2.4), sy * 0.033, z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.004)
    commit(obj, bm)

    # Fragmentos continentales flotantes (3)
    obj, bm, uv = new_mesh_obj("Shards_FloatingRock", col)
    for cx, cy, zc, rr in ((-0.118, 0.010, 0.78, 0.020), (-0.132, -0.010, 1.16, 0.016), (-0.112, 0.014, 1.50, 0.013)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.62, 0.004)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Guardia placas de falla: 2 losas desplazadas
    obj, bm, uv = new_mesh_obj("Guard_FaultPlates", col)
    for sy in (1.0, -1.0):
        for sx, dz in ((-1.0, 0.010), (1.0, -0.010)):
            rect = [(sx * 0.050, -0.030, 0.050 + dz), (sx * 0.105, -0.030, 0.044 + dz),
                    (sx * 0.105, -0.030, -0.022 + dz), (sx * 0.050, -0.030, -0.028 + dz), (sx * 0.050, -0.030, 0.050 + dz)]
            pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect]
            strip_loft(bm, uv, pts, "shell", half_w=0.011, half_t=0.009)
    commit(obj, bm)

    # nucleo corazon del manto
    obj, bm, uv = new_mesh_obj("Core_MantleHeart", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.016), (0.08, 0.023), (0.14, 0.016))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_StoneWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_Boulder", col)
    bulb_pommel(bm, uv, -0.25, [0.028, 0.024, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# D. spiritual_astral_wind_sovereign - "Espada Viento Astral" (spiritual)
# =============================================================================
def build_astral(col):
    def astral_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.86 * w,  ht,        z)),
            Vector((xs + 0.62 * w,  ht * 0.62, z)),
            Vector((xs + 0.38 * w,  ht * 0.94, z)),
            Vector((xs + 0.16 * w,  ht * 0.55, z)),
            Vector((xs + 0.04 * w,  ht * 0.20, z)),
            Vector((xs,             ht * 0.09, z)),
            Vector((xs,             -ht * 0.09,z)),
            Vector((xs + 0.04 * w,  -ht * 0.20,z)),
            Vector((xs + 0.16 * w,  -ht * 0.55,z)),
            Vector((xs + 0.38 * w,  -ht * 0.94,z)),
            Vector((xs + 0.62 * w,  -ht * 0.62,z)),
            Vector((xs + 0.86 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    # Hoja fina curvada (spine desplazado con t^1.8)
    stations = []
    zs = [0.14, 0.42, 0.72, 1.00, 1.28, 1.54, 1.78, 1.96, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        xoff = 0.034 * (t ** 1.8)
        width = (0.150 - 0.094 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.060 + xoff, "x_edge": -0.060 + xoff + width,
                             "half_t": 0.026 * (1.0 - 0.52 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_WindSliver", col)
    rings, vs = make_rings(stations, astral_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    def blade_frame(z):
        t = max(0.0, min(1.0, (z - 0.14) / 2.06))
        xoff = 0.034 * (t ** 1.8)
        width = 0.150 - 0.094 * t
        ht = 0.026 * (1.0 - 0.52 * t) + 0.003
        return xoff, width, ht

    # Estelas de viento siguiendo la cara (x2 caras x2 lineas)
    obj, bm, uv = new_mesh_obj("Streams_WindTrails", col)
    for sy in (1.0, -1.0):
        for xo in (0.30, 0.62):
            pts = []
            for j in range(11):
                z = 0.30 + 1.55 * (j / 10.0)
                xoff, width, ht = blade_frame(z)
                x = -0.060 + xoff + xo * width + 0.008 * math.sin(z * 9.0 + xo * 20.0)
                pts.append(Vector((x, sy * (ht + 0.002), z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    # Plumas-viento grandes curvadas (x2 caras x2)
    obj, bm, uv = new_mesh_obj("Feathers_WindBlades", col)
    for sy in (1.0, -1.0):
        for z0 in (0.62, 1.18):
            xoff, width, ht = blade_frame(z0)
            xb = -0.060 + xoff + 0.24 * width
            pts = [Vector((xb, sy * (ht + 0.004), z0)),
                   Vector((xb + 0.052, sy * (ht + 0.052), z0 + 0.085)),
                   Vector((xb + 0.030, sy * (ht + 0.078), z0 + 0.185))]
            strip_loft(bm, uv, pts, "flair", half_w=0.009, half_t=0.004)
    commit(obj, bm)

    # Anillos ciclonicos en espiral conica (2)
    obj, bm, uv = new_mesh_obj("Rings_Cyclone", col)
    for z0, rr in ((0.46, 0.052), (1.02, 0.062)):
        pts = []
        for j in range(29):
            t = j / 28.0
            a = 1.25 * 2 * math.pi * t
            r = rr * (0.72 + 0.28 * t)
            z = z0 + 0.22 * t
            xoff, width, ht = blade_frame(z)
            xc = -0.060 + xoff + 0.5 * width
            pts.append(Vector((xc + math.cos(a) * r, math.sin(a) * r * 1.15, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    # Guardia: barra solida + pares de alas grandes barridas
    obj, bm, uv = new_mesh_obj("Guard_WingPair", col)
    for sy in (1.0, -1.0):
        pts = [Vector((-0.064, sy * 0.026, 0.045)), Vector((0.082, sy * 0.026, 0.045))]
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.007)
        for k, x0 in enumerate((0.004, 0.030, 0.056)):
            lift = 0.100 - 0.014 * k
            pts = [Vector((x0, sy * 0.028, 0.050)),
                   Vector((x0 + 0.020, sy * (0.040 + 0.010 * (2 - k)), 0.050 + lift * 0.5)),
                   Vector((x0 + 0.006, sy * (0.052 + 0.010 * (2 - k)), 0.050 + lift))]
            strip_loft(bm, uv, pts, "flair", half_w=0.0075, half_t=0.0035)
    commit(obj, bm)

    # nucleo zefiro (esfera + anillo orbitando)
    obj, bm, uv = new_mesh_obj("Core_AstralZephyr", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.006), (0.09, 0.018), (0.16, 0.006))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(17):
        a = 2 * math.pi * j / 16
        pts.append(Vector((math.cos(a) * 0.028, math.sin(a) * 0.028, 0.09)))
    strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_WindSilk", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0154, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_BreezeOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.026, 0.022, 0.015, 0.007, 0.004], 10, ring_r=0.020, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# E. arcane_voidmath_tesseract_edge - "Filo Teseracto de Vacio Geometrico" (arcane)
# =============================================================================
def build_tesseract(col):
    # Hoja exterior rombo 4-vert (2.02)
    def tes_out(z, p):
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
    zs = [0.12, 0.44, 0.74, 1.02, 1.26, 1.46, 1.62, 1.76, 1.86]
    for i, z in enumerate(zs):
        t = z / 1.86
        width = (0.118 - 0.066 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.046, "x_edge": -0.046 + width,
                             "half_t": 0.024 * (1.0 - 0.50 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_TesseractOuter", col)
    rings, vs = make_rings(stations, tes_out)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Hoja interior teseracto (mitad de tamano, misma altura)
    def tes_in(z, p):
        xm = 0.012
        ht = p["half_t"] * 0.42
        w = 0.028
        return [
            Vector((xm + w,  0.0,  z)),
            Vector((xm,  ht,   z)),
            Vector((xm - w,  0.0,  z)),
            Vector((xm, -ht,   z)),
        ]

    stations_in = []
    for i, z in enumerate(zs):
        t = z / 1.86
        stations_in.append((z, {"half_t": 0.024 * (1.0 - 0.50 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_TesseractInner", col)
    rings, vs = make_rings(stations_in, tes_in)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Struts hiper-aristas conectando exterior e interior (4, x2 caras)
    obj, bm, uv = new_mesh_obj("Struts_HyperEdges", col)
    for sy in (1.0, -1.0):
        for z0 in (0.40, 1.10):
            pts = [Vector((0.012, sy * (0.024 * (1.0 - 0.50 * (z0 / 1.86)) + 0.003) * 0.42, z0)),
                   Vector((0.012, sy * (0.024 * (1.0 - 0.50 * (z0 / 1.86)) + 0.003), z0))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0025, half_t=0.0025)
            pts = [Vector((-0.030, 0, z0)), Vector((0.012 - 0.028, 0, z0))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0025, half_t=0.0025)
    commit(obj, bm)

    # Cubos-guia rotando alrededor (2 marcos cuadrados)
    obj, bm, uv = new_mesh_obj("Rings_RotatingCubes", col)
    for zc, rr, tilt in ((0.55, 0.070, 0.0), (1.05, 0.082, 0.0)):
        rect = [(-rr, -rr * 0.55, 0.0), (rr, -rr * 0.55, 0.0), (rr, rr * 0.55, 0.0), (-rr, -rr * 0.55, 0.0)]
        pts = [Vector((math.cos(a) * rr, math.sin(a) * rr * 0.55, zc)) for a in [tilt + 2 * math.pi * j / 4 for j in range(5)]]
        strip_loft(bm, uv, pts, "flair", half_w=0.004, half_t=0.004)
        rect2 = [(math.cos(2 * math.pi * j / 4 + 0.785) * rr * 0.5, math.sin(2 * math.pi * j / 4 + 0.785) * rr * 0.5 * 0.55, zc) for j in range(5)]
        strip_loft(bm, uv, rect2, "glow", half_w=0.003, half_t=0.003)
        for j in range(4):
            a0 = tilt + 2 * math.pi * j / 4
            a1 = 2 * math.pi * j / 4 + 0.785
            pts = [Vector((math.cos(a0) * rr, math.sin(a0) * rr * 0.55, zc)),
                   Vector((math.cos(a1) * rr * 0.5, math.sin(a1) * rr * 0.5 * 0.55, zc))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0025, half_t=0.0025)
    commit(obj, bm)

    # Guardia marco hiper-cubo
    obj, bm, uv = new_mesh_obj("Guard_HyperFrame", col)
    for sy in (1.0, -1.0):
        rect = [(-0.062, -0.030, 0.055), (0.070, -0.030, 0.055), (0.070, -0.030, -0.020),
                (-0.062, -0.030, -0.020), (-0.062, -0.030, 0.055)]
        pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect]
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.007)
        rect_in = [(-0.036, -0.030, 0.038), (0.046, -0.030, 0.038), (0.046, -0.030, -0.004), (-0.036, -0.030, -0.004), (-0.036, -0.030, 0.038)]
        pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect_in]
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # nucleo corazon 4D (cubo dentro de cubo)
    obj, bm, uv = new_mesh_obj("Core_FourDHeart", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.03, 0.017), (0.09, 0.010), (0.15, 0.017))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(9):
        a = 2 * math.pi * j / 8
        pts.append(Vector((math.cos(a) * 0.008, math.sin(a) * 0.008, 0.09)))
    strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_GeomWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0155, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_HyperBead", col)
    bulb_pommel(bm, uv, -0.24, [0.027, 0.023, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


SWORD_META = {
    "sunforge": {
        "name": "sword_14_sunforge", "builder": build_sunforge, "tex": "sunforge",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "sunforge"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage14_swords", "sunforge"),
    },
    "leviathan": {
        "name": "sword_14_leviathan_fang", "builder": build_leviathan, "tex": "leviathan_fang",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "leviathan_fang"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage14_swords", "leviathan_fang"),
    },
    "tectonic": {
        "name": "sword_14_tectonic_breaker", "builder": build_tectonic, "tex": "tectonic_breaker",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "tectonic_breaker"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage14_swords", "tectonic_breaker"),
    },
    "astral": {
        "name": "sword_14_astral_wind", "builder": build_astral, "tex": "astral_wind",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "astral_wind"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage14_swords", "astral_wind"),
    },
    "tesseract": {
        "name": "sword_14_tesseract", "builder": build_tesseract, "tex": "tesseract",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "tesseract"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage14_swords", "tesseract"),
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
    sword = "sunforge"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_14_Root", None)
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
    print("STAGE14_BUILD_DONE", sword)


main()

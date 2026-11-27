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

def densify_stations(stations, factor=2):
    out = []
    for i in range(len(stations) - 1):
        (z0, p0), (z1, p1) = stations[i], stations[i + 1]
        for k in range(factor):
            t = k / float(factor)
            z = z0 + (z1 - z0) * t
            p = {}
            for key, v0 in p0.items():
                v1 = p1.get(key, v0)
                if key == "v":
                    p[key] = v0 + (v1 - v0) * t
                elif isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
                    p[key] = v0 + (v1 - v0) * t
                else:
                    p[key] = v0
            out.append((z, p))
    out.append((stations[-1][0], dict(stations[-1][1])))
    return out


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
    rings, vs = make_rings(densify_stations(stations), sun_section)
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
        for j in range(45):
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
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(15)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ForgeLeather", col)
    grip_braid(bm, uv, -0.02, -0.26, 12, 10, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AnvilBulb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 14, ring_r=0.022, ring_z=-0.305)
    commit(obj, bm)


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
    rings, vs = make_rings(densify_stations(stations), glacier_section)
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
        curved_loft(bm, uv, path, lambda tt: 0.009 * (1.0 - tt) + 0.002, 9, "flair")
    commit(obj, bm)

    # Frost melt lines (glow strips)
    obj, bm, uv = new_mesh_obj("Inlay_FrostMeltLines", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(21):
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
        curved_loft(bm, uv, path, lambda t: 0.017 * (1.0 - 0.5 * t) + 0.005, 12, "flair")
        for k in range(2):
            xo = side * (0.10 + 0.055 * k)
            path2 = [Vector((xo, 0.0, 0.058)), Vector((xo * 1.06, 0.0, 0.020)), Vector((xo * 1.04, 0.0, -0.030))]
            curved_loft(bm, uv, path2, lambda t: 0.006 * (1.0 - t) + 0.002, 9, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_FrozenStar", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.022, 0.023), (0.030, 0.042), (0.020, 0.056), (0.009, 0.061)]):
        z = 0.20 + h2
        ring = [Vector((0.019 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(15)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_FrostBlueHilt", col)
    grip_braid(bm, uv, 0.055, -0.45, 14, 11, 0.029, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_IcebergCrystal", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.032, 0.041, 0.035, 0.020, 0.006], 13, squash=1.1, drop=0.10, ring_r=0.040, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_FrozenSilver", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.418, -0.448)], 0.034)
    commit(obj, bm)


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
    rings, vs = make_rings(densify_stations(stations), dev_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Boca devoradora con dientes cerca de la punta (x2 caras)
    obj, bm, uv = new_mesh_obj("Maw_DevourerTeeth", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(33):
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
        for j in range(45):
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
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * 0.021, math.sin(2 * math.pi * j / 10) * 0.021, z)) for j in range(15)])
        vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "shell")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_DevourerWrap", col)
    grip_braid(bm, uv, -0.02, -0.25, 12, 10, 0.0160, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_FurnaceBulb", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.022, 0.014, 0.006], 14, squash=1.25, drop=0.100)
    commit(obj, bm)


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
    rings, vs = make_rings(densify_stations(stations), arc_section)
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
    for j in range(33):
        a = 2 * math.pi * j / 20
        pts.append(Vector((math.cos(a) * 0.030, math.sin(a) * 0.030, 0.10)))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_ArchangelSilk", col)
    grip_braid(bm, uv, -0.02, -0.26, 12, 10, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_ArchangelPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_VerdictGemBulb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 14, ring_r=0.022, ring_z=-0.305)
    commit(obj, bm)

SWORD_META = {
    "sunforge": {
        "name": "sword_14_sunforge", "builder": build_sunforge, "tex": "sunforge",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "sunforge"),
        "art_dir": os.path.join(REPO, "art_pipeline", "remaster", "sunforge"),
    },
    "glacier": {
        "name": "sword_06_glacier_fang", "builder": build_glacier, "tex": "glacier_fang",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "glacier_fang"),
        "art_dir": os.path.join(REPO, "art_pipeline", "remaster", "glacier_fang"),
    },
    "devourer": {
        "name": "sword_10_soul_devourer", "builder": build_devourer, "tex": "soul_devourer",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "soul_devourer"),
        "art_dir": os.path.join(REPO, "art_pipeline", "remaster", "soul_devourer"),
    },
    "archangel": {
        "name": "sword_12_archangel_verdict", "builder": build_archangel, "tex": "archangel_verdict",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "archangel_verdict"),
        "art_dir": os.path.join(REPO, "art_pipeline", "remaster", "archangel_verdict"),
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
    n_nmap.inputs["Strength"].default_value = 1.0
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

    sword_root = bpy.data.objects.new("Sword_Root_Remaster", None)
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
    print("REMASTER_BUILD_DONE", sword)


main()

# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 13: CINCO espadas bespoke (Era IV Afinidad VI Trascendente)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage13_swords.py -- sword=empyrean|voidscar|aurora|worldtree|axiom
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
# A. blessed_empyrean_halo_blade - "Hoja Trascendente del Halo Empireo" (blessed)
# =============================================================================
def build_empyrean(col):
    def emp_section(z, p):
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
        width = (0.190 - 0.090 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.064, "x_edge": -0.064 + width,
                             "half_t": 0.029 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_EmpyreanHalo", col)
    rings, vs = make_rings(stations, emp_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Halos imperio concéntricos flotantes (3, detrás de la hoja)
    obj, bm, uv = new_mesh_obj("Halo_EmpyreanRings", col)
    for zc, rr in ((0.72, 0.060), (0.94, 0.046), (1.14, 0.034)):
        pts = []
        for j in range(29):
            a = 2 * math.pi * j / 28
            pts.append(Vector((-0.064 - 0.110, 0.006 + math.cos(a) * rr, zc + math.sin(a) * rr)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.005)
    commit(obj, bm)

    # Motas de luz orbitantes (4)
    obj, bm, uv = new_mesh_obj("Orbs_EmpyreanMotes", col)
    for cx, cy, zc, rr in ((-0.092, 0.014, 0.82, 0.009), (-0.102, -0.012, 1.04, 0.007), (-0.088, 0.016, 1.26, 0.006), (-0.098, -0.008, 1.46, 0.005)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.5, 0.002)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Guardia corona incorrupta: arco + 7 púas altas
    obj, bm, uv = new_mesh_obj("Guard_IncorruptCrown", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (1.10 + 0.80 * j / 24)
            pts.append(Vector((math.cos(a) * 0.096, sy * 0.028, 0.02 - math.sin(a) * 0.058)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for k in range(7):
            a = math.pi * (1.10 + 0.80 * k / 6)
            pts = [Vector((math.cos(a) * 0.096, sy * 0.026, 0.02 - math.sin(a) * 0.058)),
                   Vector((math.cos(a) * 0.132, sy * 0.026, 0.02 - math.sin(a) * 0.090))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Filo-luz ascendente (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_EmpyreanLicht", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(9):
            t = j / 8.0
            z = 0.30 + 1.40 * t
            pts.append(Vector((-0.014 + 0.010 * math.sin(z * 6.5), sy * 0.028, z)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # núcleo corazón imperio
    obj, bm, uv = new_mesh_obj("Core_EmpyreanHeart", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.014), (0.08, 0.020), (0.14, 0.014))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_EmpyreanSilk", col)
    grip_braid(bm, uv, -0.02, -0.26, 9, 8, 0.0162, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_HaloOrb", col)
    bulb_pommel(bm, uv, -0.26, [0.029, 0.025, 0.017, 0.008, 0.004], 10, ring_r=0.023, ring_z=-0.305)
    commit(obj, bm)


# =============================================================================
# B. cursed_voidscar_transcendent_sword - "Espada Trascendente Cicatriz del Vacio" (cursed)
# =============================================================================
def build_voidscar(col):
    def voi_section(z, p):
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
    zs = [0.06, 0.30, 0.60, 0.90, 1.18, 1.42, 1.64, 1.82, 1.96, 2.02]
    for i, z in enumerate(zs):
        t = z / 2.02
        width = (0.180 - 0.080 * t) * (0.42 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.080, "x_edge": -0.080 + width,
                             "half_t": 0.030 * (1.0 - 0.40 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_Voidscar", col)
    rings, vs = make_rings(stations, voi_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Cicatriz cruzada en X (x2 caras)
    obj, bm, uv = new_mesh_obj("Scar_CosmicCross", col)
    for sy in (1.0, -1.0):
        pts = [Vector((-0.010, sy * 0.029, 0.42)), Vector((0.030, sy * 0.029, 1.30))]
        strip_loft(bm, uv, pts, "glow", half_w=0.006, half_t=0.004)
        pts = [Vector((0.030, sy * 0.029, 0.62)), Vector((-0.010, sy * 0.029, 1.42))]
        strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
        # anillo de la herida
        pts = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            pts.append(Vector((-0.010 + 0.030 + math.cos(a) * 0.030, sy * 0.030, 0.92 + math.sin(a) * 0.026)))
        strip_loft(bm, uv, pts, "glow", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Motas de vacío flotantes (3)
    obj, bm, uv = new_mesh_obj("Wisps_VoidMotes", col)
    for cx, cy, zc, rr in ((-0.108, 0.010, 0.86, 0.013), (-0.118, -0.008, 1.20, 0.011), (-0.104, 0.012, 1.52, 0.009)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.55, 0.003)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Guardia rasgada: arco con corte central
    obj, bm, uv = new_mesh_obj("Guard_TornArc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(23):
            a = math.pi * (1.05 + 0.90 * j / 22)
            if math.pi * 1.38 < a < math.pi * 1.62:
                continue
            pts.append(Vector((math.cos(a) * 0.098, sy * 0.028, 0.02 - math.sin(a) * 0.060)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
    commit(obj, bm)

    # Bordados de cicatriz en el grip (3)
    obj, bm, uv = new_mesh_obj("Grip_ScarStitches", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0160, 0.0014)
    for k in range(3):
        z0 = -0.05 - 0.06 * k
        pts = [Vector((-0.014, 0.004, z0)), Vector((0.014, -0.004, z0 - 0.022))]
        strip_loft(bm, uv, pts, "shell", half_w=0.0035, half_t=0.0035)
    commit(obj, bm)

    # núcleo herida cósmica
    obj, bm, uv = new_mesh_obj("Core_CosmicWound", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.015), (0.08, 0.021), (0.14, 0.015))):
        rings.append([Vector((math.cos(2 * math.pi * j / 10) * r, math.sin(2 * math.pi * j / 10) * r, z)) for j in range(10)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_VoidDrop", col)
    bulb_pommel(bm, uv, -0.25, [0.027, 0.022, 0.014, 0.006], 10, squash=1.30, drop=0.100)
    commit(obj, bm)


# =============================================================================
# C. elemental_transcendent_aurora_sword - "Espada Trascendente de Aurora Polar" (elemental)
# =============================================================================
def build_aurora(col):
    def aur_section(z, p):
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
        width = (0.185 - 0.092 * t) * (0.34 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.062, "x_edge": -0.062 + width,
                             "half_t": 0.028 * (1.0 - 0.50 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_AuroraPolar", col)
    rings, vs = make_rings(stations, aur_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Cortinas de aurora onduladas (x2 caras, 3 bandas)
    obj, bm, uv = new_mesh_obj("Inlay_AuroraCurtains", col)
    for sy in (1.0, -1.0):
        for k, xo in enumerate((0.000, 0.016, 0.032)):
            pts = []
            for j in range(11):
                z = 0.28 + 1.45 * (j / 10.0)
                pts.append(Vector((xo - 0.010 + 0.010 * math.sin(z * 6.0 + k * 2.0), sy * 0.027, z)))
            strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.003)
    commit(obj, bm)

    # Pilares magnéticos con aros (2 pilares a los lados)
    obj, bm, uv = new_mesh_obj("Pillars_MagneticPoles", col)
    for sx in (-1.0, 1.0):
        pts = [Vector((sx * 0.090, 0.008, 0.06)), Vector((sx * 0.104, 0.010, 0.70))]
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.008)
        for k in range(3):
            zc = 0.16 + 0.17 * k
            rr = 0.030 - 0.006 * k
            pts = []
            for j in range(17):
                a = 2 * math.pi * j / 16
                pts.append(Vector((sx * (0.090 + 0.014 * (zc / 0.70)) + math.cos(a) * rr, 0.009 + math.sin(a) * rr, zc)))
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # Guardia pilar-polo (arco + pica central)
    obj, bm, uv = new_mesh_obj("Guard_PoleArc", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(23):
            a = math.pi * (1.10 + 0.80 * j / 22)
            pts.append(Vector((math.cos(a) * 0.094, sy * 0.028, 0.02 - math.sin(a) * 0.056)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        pts = [Vector((0, sy * 0.026, -0.026)), Vector((0, sy * 0.026, -0.062))]
        strip_loft(bm, uv, pts, "shell", half_w=0.007, half_t=0.006)
    commit(obj, bm)

    # núcleo viento solar (espiral compacta)
    obj, bm, uv = new_mesh_obj("Core_SolarWind", col)
    pts = []
    for j in range(21):
        t = j / 20.0
        a = 3.0 * math.pi * t
        r = 0.018 * (0.7 + 0.3 * t)
        pts.append(Vector((math.cos(a) * r, math.sin(a) * r, 0.03 + 0.14 * t)))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_AuroraBraid", col)
    grip_braid(bm, uv, -0.02, -0.25, 9, 8, 0.0158, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_PolarOrb", col)
    bulb_pommel(bm, uv, -0.25, [0.028, 0.024, 0.016, 0.007, 0.004], 10, ring_r=0.022, ring_z=-0.295)
    commit(obj, bm)


# =============================================================================
# D. spiritual_transcendent_worldtree_branch - "Rama Trascendente del Arbol Mundo" (spiritual)
# =============================================================================
def build_worldtree(col):
    def wld_section(z, p):
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.004
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.80 * w,  ht,        z)),
            Vector((xs + 0.50 * w,  ht * 0.62, z)),
            Vector((xs + 0.18 * w,  ht * 0.90, z)),
            Vector((xs + 0.04 * w,  ht * 0.36, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.04 * w,  -ht * 0.36,z)),
            Vector((xs + 0.18 * w,  -ht * 0.90,z)),
            Vector((xs + 0.50 * w,  -ht * 0.62,z)),
            Vector((xs + 0.80 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.10, 0.40, 0.70, 1.00, 1.30, 1.56, 1.78, 1.94, 2.02]
    for i, z in enumerate(zs):
        t = z / 2.02
        width = (0.110 - 0.055 * t) * (0.44 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.052, "x_edge": -0.052 + width,
                             "half_t": 0.022 * (1.0 - 0.40 * t) + 0.004, "v": t}))
    obj, bm, uv = new_mesh_obj("Trunk_WorldtreeBlade", col)
    rings, vs = make_rings(stations, wld_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Ramas laterales con mini-hojas (x2 caras, 2 niveles)
    obj, bm, uv = new_mesh_obj("Branches_Worldtree", col)
    for sy in (1.0, -1.0):
        for k, z0 in enumerate((0.85, 1.25)):
            rr = 0.050 - 0.008 * k
            pts = [Vector((-0.052 + 0.040, sy * 0.020, z0)), Vector((-0.052 + 0.040 + 0.006, sy * (0.020 + rr), z0 + 0.10))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.005)
            rings, vs = [], []
            for i, r in enumerate((0.020, 0.013, 0.004)):
                rings.append([Vector((-0.052 + 0.046 + math.cos(2 * math.pi * j / 8) * r, sy * (0.020 + rr) + math.sin(2 * math.pi * j / 8) * r, z0 + 0.12)) for j in range(8)])
                vs.append(i / 2.0)
            add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Hojas-esmeralda flotantes (3)
    obj, bm, uv = new_mesh_obj("Leaves_EmeraldFloat", col)
    for cx, cy, zc, rr in ((-0.100, 0.012, 0.95, 0.018), (-0.112, -0.010, 1.28, 0.015), (-0.096, 0.014, 1.58, 0.012)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.5, 0.002)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # Raíces en la base (3 raíces curvas)
    obj, bm, uv = new_mesh_obj("Roots_CosmosRoots", col)
    for k in range(3):
        a = 2 * math.pi * k / 3
        path = []
        for j in range(7):
            t = j / 6.0
            path.append(Vector((math.cos(a) * (0.020 + 0.055 * t), math.sin(a) * (0.020 + 0.048 * t), -0.02 - 0.10 * t)))
        curved_loft(bm, uv, path, lambda t: 0.009 * (1.0 - 0.5 * t) + 0.002, 8, "shell")
    commit(obj, bm)

    # Guardia corona de ramas (anillo + 5 ramitas)
    obj, bm, uv = new_mesh_obj("Guard_BranchCrown", col)
    for sy in (1.0, -1.0):
        pts = []
        for j in range(25):
            a = math.pi * (1.12 + 0.76 * j / 24)
            pts.append(Vector((math.cos(a) * 0.096, sy * 0.028, 0.02 - math.sin(a) * 0.058)))
        strip_loft(bm, uv, pts, "shell", half_w=0.010, half_t=0.008)
        for k in range(5):
            a = math.pi * (1.15 + 0.70 * k / 4)
            pts = [Vector((math.cos(a) * 0.096, sy * 0.026, 0.02 - math.sin(a) * 0.058)),
                   Vector((math.cos(a) * 0.118, sy * 0.026, 0.02 - math.sin(a) * 0.050))]
            strip_loft(bm, uv, pts, "shell", half_w=0.005, half_t=0.004)
    commit(obj, bm)

    # Anillos de crecimiento en el tronco (x2 caras)
    obj, bm, uv = new_mesh_obj("Inlay_GrowthRings", col)
    for sy in (1.0, -1.0):
        for k, zc in enumerate((0.45, 0.85, 1.25)):
            pts = []
            for j in range(17):
                a = 2 * math.pi * j / 16
                pts.append(Vector((-0.052 + 0.040 + math.cos(a) * (0.026 - 0.006 * k), sy * 0.021, zc + math.sin(a) * (0.020 - 0.005 * k))))
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # núcleo semilla cosmos
    obj, bm, uv = new_mesh_obj("Core_CosmosSeed", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.005), (0.09, 0.018), (0.16, 0.005))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_WorldtreeBark", col)
    grip_braid(bm, uv, -0.12, -0.30, 9, 8, 0.0155, 0.0014)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_TreeOrb", col)
    bulb_pommel(bm, uv, -0.30, [0.026, 0.022, 0.015, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.34)
    commit(obj, bm)


# =============================================================================
# E. arcane_transcendent_axiom_sword - "Espada Trascendente del Axioma" (arcane)
# =============================================================================
def build_axiom(col):
    def axi_section(z, p):
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
    zs = [0.12, 0.44, 0.76, 1.04, 1.28, 1.48, 1.64, 1.78, 1.88]
    for i, z in enumerate(zs):
        t = z / 1.88
        width = (0.115 - 0.062 * t) * (0.30 if i == len(zs) - 1 else 1.0)
        stations.append((z, {"x_spine": -0.044, "x_edge": -0.044 + width,
                             "half_t": 0.023 * (1.0 - 0.50 * t) + 0.003, "v": t}))
    obj, bm, uv = new_mesh_obj("Blade_AxiomCrystal", col)
    rings, vs = make_rings(stations, axi_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Glifos-matemáticos grabados: sumas e integrales (x2 caras)
    obj, bm, uv = new_mesh_obj("Glyph_MathSigils", col)
    for sy in (1.0, -1.0):
        for k, zc in enumerate((0.42, 0.74, 1.06, 1.38)):
            # suma (cruz griega)
            pts = [Vector((-0.044 + 0.030, sy * 0.022, zc - 0.028)), Vector((-0.044 + 0.030, sy * 0.022, zc + 0.028))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
            pts = [Vector((-0.044 + 0.016, sy * 0.022, zc)), Vector((-0.044 + 0.044, sy * 0.022, zc))]
            strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.003)
            # integral (curva S)
            pts = []
            for j in range(11):
                t = j / 10.0
                pts.append(Vector((-0.044 + 0.058 + 0.010 * math.sin(t * 6.283), sy * 0.022, zc - 0.026 + 0.052 * t)))
            strip_loft(bm, uv, pts, "glow", half_w=0.003, half_t=0.003)
    commit(obj, bm)

    # Símbolo infinito flotante bajo la hoja
    obj, bm, uv = new_mesh_obj("Glyph_Infinity", col)
    pts = []
    for j in range(33):
        t = j / 32.0
        a = 2 * math.pi * t
        xx0 = 0.5 + 0.5 * math.cos(a)
        pts.append(Vector((-0.044 - 0.098 + math.cos(a) * 0.034 * (0.6 + 0.4 * math.sin(a)), 0.008 + math.sin(a) * math.cos(a) * 0.017, 0.30)))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Guardia tabla-axioma: barra doble con pilar central
    obj, bm, uv = new_mesh_obj("Guard_AxiomTablet", col)
    for sy in (1.0, -1.0):
        rect = [(-0.078, -0.030, 0.052), (0.062, -0.030, 0.052), (0.062, -0.030, 0.024), (-0.078, -0.030, 0.024), (-0.078, -0.030, 0.052)]
        pts = [Vector((rx, sy * 0.030, rz)) for rx, ry, rz in rect]
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.007)
        pts = [Vector((-0.008, sy * 0.028, 0.024)), Vector((-0.008, sy * 0.028, -0.010))]
        strip_loft(bm, uv, pts, "shell", half_w=0.008, half_t=0.007)
    commit(obj, bm)

    # Constantes orbitantes (3 esferas pequeñas: pi, e, phi)
    obj, bm, uv = new_mesh_obj("Orbs_Constants", col)
    for cx, cy, zc, rr in ((-0.094, 0.012, 0.78, 0.009), (-0.104, -0.010, 1.02, 0.007), (-0.092, 0.014, 1.24, 0.006)):
        rings, vs = [], []
        for i, r in enumerate((rr, rr * 0.5, 0.002)):
            rings.append([Vector((cx + math.cos(2 * math.pi * j / 8) * r, cy + math.sin(2 * math.pi * j / 8) * r, zc)) for j in range(8)])
            vs.append(i / 2.0)
        add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    # núcleo gema-axioma (igualdad: dos barras gemelas)
    obj, bm, uv = new_mesh_obj("Core_AxiomGem", col)
    rings, vs = [], []
    for i, (z, r) in enumerate(((0.02, 0.005), (0.09, 0.018), (0.16, 0.005))):
        rings.append([Vector((math.cos(2 * math.pi * j / 8) * r, math.sin(2 * math.pi * j / 8) * r, z)) for j in range(8)])
        vs.append(i / 2.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    for zo in (0.19, 0.215):
        pts = [Vector((-0.008, 0, zo)), Vector((0.008, 0, zo))]
        strip_loft(bm, uv, pts, "glow", half_w=0.008, half_t=0.004)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_AxiomWrap", col)
    grip_braid(bm, uv, -0.02, -0.24, 9, 8, 0.0155, 0.0012)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_AxiomPair", col)
    ferrule_pair(bm, uv, [(-0.02, -0.05)], 0.0180)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_AxiomBead", col)
    bulb_pommel(bm, uv, -0.24, [0.027, 0.023, 0.016, 0.007, 0.004], 10, ring_r=0.021, ring_z=-0.285)
    commit(obj, bm)


SWORD_META = {
    "empyrean": {
        "name": "sword_13_empyrean_halo", "builder": build_empyrean, "tex": "empyrean_halo",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "empyrean_halo"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage13_swords", "empyrean_halo"),
    },
    "voidscar": {
        "name": "sword_13_voidscar", "builder": build_voidscar, "tex": "voidscar",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "voidscar"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage13_swords", "voidscar"),
    },
    "aurora": {
        "name": "sword_13_aurora_polar", "builder": build_aurora, "tex": "aurora_polar",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "aurora_polar"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage13_swords", "aurora_polar"),
    },
    "worldtree": {
        "name": "sword_13_worldtree", "builder": build_worldtree, "tex": "worldtree",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "worldtree"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage13_swords", "worldtree"),
    },
    "axiom": {
        "name": "sword_13_axiom", "builder": build_axiom, "tex": "axiom_sword",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "axiom_sword"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage13_swords", "axiom_sword"),
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
    sword = "empyrean"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_13_Root", None)
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
    print("STAGE13_BUILD_DONE", sword)


main()

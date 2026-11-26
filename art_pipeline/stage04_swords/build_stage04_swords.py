# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 04: CINCO espadas bespoke (anime exagerado por linaje)
  A. awakening_amber_sanctuary_blade  "Hoja de Ambar de Santuario"   (blessed/heavy)
  B. awakening_ironwood_storm_edge    "Filo de Palo Ferreo y Trueno" (elemental/balanced)
  C. awakening_spirit_willow_saber    "Sable de Sauce Espiritual"    (spiritual/swift)
  D. awakening_bloodsap_bramble_blade "Hoja de Zarza Sanguina"       (cursed/swift)

Uso:
  blender --background --python build_stage04_swords.py -- sword=sunbark|thornheart|fulgurite|jadeanima|runebark
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
# A. awakening_sunbark_vow_greatsword - "Mandoble del Voto Heliofilo" (blessed heavy)
# =============================================================================
def build_sunbark(col):
    def vow_section(z, p):
        # 14-vert broad greatsword with flared executioner tip
        xs, xe = p["x_spine"], p["x_edge"]
        flare = p.get("flare", 0.0)
        w = (xe + flare) - xs
        ht = p["half_t"]
        ye = 0.0028
        return [
            Vector((xe + flare,     ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
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
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe + flare,     -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.14, 0.34, 0.62, 0.92, 1.22, 1.50, 1.74, 1.94, 2.06, 2.11]
    for i, z in enumerate(zs):
        t = z / 2.11
        flare = max(0.0, t - 0.80) * 0.26 if i >= 7 else 0.0
        width = (0.185 - 0.075 * t)
        stations.append((z, {
            "x_spine": -0.055, "x_edge": -0.055 + width,
            "half_t": 0.033 * (1.0 - 0.55 * t) + 0.004,
            "v": t, "flare": flare,
        }))

    obj, bm, uv = new_mesh_obj("Blade_SunbarkVowGreatsword", col)
    rings, vs = make_rings(stations, vow_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Sunburst fullers: 2 glow strips on the flats
    obj, bm, uv = new_mesh_obj("Inlay_SunburstFullers", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.34 + 1.26 * t
            pts.append((-0.055 + 0.090 + 0.024 * math.sin(t * 6.5), sy * 0.026, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.009, half_t=0.0045)
    commit(obj, bm)

    # Rising-sun guard: gilded disc + 6 rays
    obj, bm, uv = new_mesh_obj("Guard_RisingSunDisc", col)
    rings, vs = [], []
    for i, z in enumerate([0.055, 0.095]):
        ring = [Vector((math.cos(2 * math.pi * j / 16) * 0.082, math.sin(2 * math.pi * j / 16) * 0.082 * 0.92, z)) for j in range(16)]
        rings.append(ring); vs.append(i)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    for k in range(6):
        a = 2 * math.pi * k / 6.0
        path = [Vector((math.cos(a) * (0.086 + 0.115 * t), math.sin(a) * (0.086 + 0.115 * t) * 0.92, 0.075 + 0.004 * math.sin(t * 3.0))) for t in [i / 5.0 for i in range(6)]]
        curved_loft(bm, uv, path, lambda t: 0.013 * (1.0 - t) + 0.002, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_DawnOathHeart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.010, 0.006), (0.024, 0.026), (0.032, 0.046), (0.023, 0.060), (0.010, 0.066)]):
        z = 0.18 + h2
        ring = [Vector((0.022 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_SunleatherHilt", col)
    grip_braid(bm, uv, 0.055, -0.47, 11, 9, 0.032, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_SunDialBulb", col)
    bulb_pommel(bm, uv, -0.470, [0.016, 0.036, 0.046, 0.040, 0.024, 0.007], 9, squash=1.0, drop=0.105, ring_r=0.047, ring_z=-0.522)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_GildedSunBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.44, -0.47)], 0.038)
    commit(obj, bm)

# =============================================================================
# B. awakening_thornheart_hex_blade - "Hoja Maldita Corazon de Espina" (cursed)
# =============================================================================
def build_thornheart(col):
    def hex_section(z, p):
        # 12-vert hex blade with notched sawtooth edge
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        notch = p.get("notch", 0.004)
        ye = 0.0026
        return [
            Vector((xe - notch,      ye,        z)),
            Vector((xs + 0.85 * w,   ht,        z)),
            Vector((xs + 0.60 * w,   ht * 0.80, z)),
            Vector((xs + 0.32 * w,   ht,        z)),
            Vector((xs + 0.10 * w,   ht * 0.60, z)),
            Vector((xs,              ht * 0.15, z)),
            Vector((xs,              -ht * 0.15,z)),
            Vector((xs + 0.10 * w,   -ht * 0.60,z)),
            Vector((xs + 0.32 * w,   -ht,       z)),
            Vector((xs + 0.60 * w,   -ht * 0.80,z)),
            Vector((xs + 0.85 * w,   -ht,       z)),
            Vector((xe - notch,      -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.16, 0.38, 0.60, 0.82, 1.04, 1.26, 1.48, 1.70, 1.90, 2.02]
    for i, z in enumerate(zs):
        t = z / 2.02
        stations.append((z, {
            "x_spine": -0.048, "x_edge": -0.048 + (0.150 - 0.090 * t),
            "half_t": 0.026 * (1.0 - 0.55 * t) + 0.003,
            "v": t, "notch": (0.020 if i % 2 == 1 else 0.004),
        }))

    obj, bm, uv = new_mesh_obj("Blade_ThornheartHexBlade", col)
    rings, vs = make_rings(stations, hex_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Hex runic veins: 2 purple glow strips
    obj, bm, uv = new_mesh_obj("Inlay_HexRunicVeins", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(13):
            t = i / 12.0
            z = 0.35 + 1.20 * t
            pts.append((-0.048 + 0.062 + 0.018 * math.sin(t * 9.0), sy * 0.022, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.008, half_t=0.004)
    commit(obj, bm)

    # Thorn heart core: lobed glowing heart wrapped by a thorn ring
    obj, bm, uv = new_mesh_obj("Core_Thornheart", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.012, 0.007), (0.026, 0.026), (0.030, 0.044), (0.020, 0.058), (0.009, 0.064)]):
        z = 0.20 + h2
        ring = []
        for j in range(10):
            a = 2 * math.pi * j / 10
            m = 1.0 + 0.20 * math.sin(2 * a + 1.2)
            ring.append(Vector((0.016 + math.cos(a) * w2 * m, math.sin(a) * h2 * 0.6 * m, z)))
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append((0.016 + math.cos(a) * 0.055, math.sin(a) * 0.045, 0.26))
    strip_loft(bm, uv, pts, "glow", half_w=0.004, half_t=0.004)
    commit(obj, bm)

    # Indigo thorn collar guard: 4 crossed thorn arcs
    obj, bm, uv = new_mesh_obj("Guard_IndigoThornCollar", col)
    for sx in (1.0, -1.0):
        for dy in (0.020, -0.020):
            path = [Vector((sx * 0.030, dy, 0.100)), Vector((sx * 0.090, dy * 1.8, 0.072)),
                    Vector((sx * 0.150, dy * 2.2, 0.062)), Vector((sx * 0.185, dy * 1.6, 0.078))]
            curved_loft(bm, uv, path, lambda t: 0.014 * (1.0 - 0.5 * t) + 0.004, 7, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_HexWrappedHilt", col)
    grip_braid(bm, uv, 0.055, -0.45, 12, 9, 0.029, 0.005, thick_every=2, thick=0.006)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_HexThornBud", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.032, 0.040, 0.034, 0.019, 0.005], 9, squash=1.2, drop=0.095, ring_r=0.039, ring_z=-0.495)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_HexIron", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.415, -0.445)], 0.034)
    commit(obj, bm)

# =============================================================================
# C. awakening_fulgurite_crest_sword - "Espada Cresta de Fulgurita" (elemental)
# =============================================================================
def build_fulgurite(col):
    def fulg_section(z, p):
        # 12-vert glassy blade with wavy fulgurite edges
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0022
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.82 * w,  ht,        z)),
            Vector((xs + 0.55 * w,  ht * 0.62, z)),
            Vector((xs + 0.30 * w,  ht * 0.95, z)),
            Vector((xs + 0.12 * w,  ht * 0.55, z)),
            Vector((xs,             ht * 0.12, z)),
            Vector((xs,             -ht * 0.12,z)),
            Vector((xs + 0.12 * w,  -ht * 0.55,z)),
            Vector((xs + 0.30 * w,  -ht * 0.95,z)),
            Vector((xs + 0.55 * w,  -ht * 0.62,z)),
            Vector((xs + 0.82 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.15, 0.36, 0.60, 0.86, 1.12, 1.38, 1.62, 1.84, 2.00, 2.08]
    for i, z in enumerate(zs):
        t = z / 2.08
        wave = 0.012 * math.sin(t * 9.0)
        stations.append((z, {
            "x_spine": -0.050, "x_edge": -0.050 + (0.135 - 0.085 * t) + wave,
            "half_t": 0.020 * (1.0 - 0.55 * t) + 0.003,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_FulguriteCrestSword", col)
    rings, vs = make_rings(stations, fulg_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Lightning crest fin: sawtooth glass fin along the spine
    obj, bm, uv = new_mesh_obj("Crest_LightningFin", col)
    rings, vs = [], []
    for i in range(15):
        t = i / 14.0
        z = 0.30 + 1.25 * t
        h = 0.020 if i % 2 == 0 else 0.009
        x0 = -0.050 + 0.006 * math.sin(t * 7.0)
        rings.append([Vector((x0, h, z)), Vector((x0 + 0.005, 0.0, z)), Vector((x0, -0.006, z)), Vector((x0 - 0.005, 0.0, z))])
        vs.append(t)
    add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Fulgurite branches: 2 wavy cyan glow strips
    obj, bm, uv = new_mesh_obj("Inlay_FulguriteBranches", col)
    for sy in (1.0, -1.0):
        pts = []
        for i in range(15):
            t = i / 14.0
            z = 0.32 + 1.30 * t
            pts.append((-0.050 + 0.058 + 0.014 * math.sin(t * 13.0), sy * 0.019, z))
        strip_loft(bm, uv, pts, "glow", half_w=0.007, half_t=0.0035)
    commit(obj, bm)

    # Fused glass quillons with droplet bulges
    obj, bm, uv = new_mesh_obj("Guard_FusedGlassQuillons", col)
    for side in (1.0, -1.0):
        path = [Vector((side * 0.030, 0.0, 0.095)), Vector((side * 0.100, 0.0, 0.072)),
                Vector((side * 0.165, 0.0, 0.058))]
        curved_loft(bm, uv, path, lambda t: 0.016 * (1.0 - 0.5 * t) + 0.006 * math.exp(-((t - 0.85) ** 2) / 0.004), 9, "flair")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Core_IgneousVoltaicNucleus", col)
    rings, vs = [], []
    for i, (w2, h2) in enumerate([(0.009, 0.005), (0.022, 0.024), (0.029, 0.043), (0.019, 0.057), (0.008, 0.062)]):
        z = 0.20 + h2
        ring = [Vector((0.018 + math.cos(2 * math.pi * j / 10) * w2, math.sin(2 * math.pi * j / 10) * h2 * 0.6, z)) for j in range(10)]
        rings.append(ring); vs.append(i / 4.0)
    add_lofted_tube(bm, uv, rings, vs, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_VitrifiedWrap", col)
    grip_braid(bm, uv, 0.055, -0.45, 11, 9, 0.028, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_FulguriteKnob", col)
    bulb_pommel(bm, uv, -0.450, [0.013, 0.030, 0.038, 0.032, 0.018, 0.005], 9, squash=1.0, drop=0.095, ring_r=0.037, ring_z=-0.495)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_BurntCopper", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.415, -0.445)], 0.033)
    commit(obj, bm)

# =============================================================================
# D. awakening_jade_anima_katana - "Katana Anima de Jade" (spiritual swift)
# =============================================================================
def build_jadeanima(col):
    def kat_section(z, p):
        # 12-vert slim single-edge katana blade
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
    zs = [0.05, 0.18, 0.42, 0.70, 1.00, 1.30, 1.58, 1.82, 2.00, 2.10]
    xes = []
    for i, z in enumerate(zs):
        t = z / 2.10
        cur = -0.075 * (t ** 1.65)
        width = (0.062 - 0.020 * t) * (0.72 if i == len(zs) - 1 else 1.0)
        xs = -0.030 + cur
        xe = xs + width
        xes.append(xe)
        stations.append((z, {"x_spine": xs, "x_edge": xe,
                             "half_t": 0.010 * (1.0 - 0.35 * t) + 0.002, "v": t}))

    def xe_at(z):
        for k in range(len(zs) - 1):
            if zs[k] <= z <= zs[k + 1]:
                t = (z - zs[k]) / (zs[k + 1] - zs[k])
                return xes[k] + (xes[k + 1] - xes[k]) * t
        return xes[-1]

    obj, bm, uv = new_mesh_obj("Blade_JadeAnimaKatana", col)
    rings, vs = make_rings(stations, kat_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Jade hamon: wavy temper-line glow near the edge
    obj, bm, uv = new_mesh_obj("Inlay_JadeHamonLine", col)
    pts = []
    for i in range(15):
        t = i / 14.0
        z = 0.22 + 1.62 * t
        pts.append((xe_at(z) - 0.016 + 0.004 * math.sin(t * 15.0), 0.0, z))
    strip_loft(bm, uv, pts, "glow", half_w=0.0045, half_t=0.0035)
    commit(obj, bm)

    # Tsuba: two jade ellipse discs
    obj, bm, uv = new_mesh_obj("Tsuba_JadeAnimaRings", col)
    for z0, z1, r, sq in [(0.045, 0.058, 0.078, 0.62), (0.058, 0.070, 0.070, 0.62)]:
        rings, vs = [], []
        for i, z in enumerate([z0, z1]):
            ring = [Vector((math.cos(2 * math.pi * j / 16) * r, math.sin(2 * math.pi * j / 16) * r * sq, z)) for j in range(16)]
            rings.append(ring); vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    commit(obj, bm)

    # Anima lantern: small jade glow ring floating beside the tsuba
    obj, bm, uv = new_mesh_obj("Core_AnimaLantern", col)
    pts = []
    for j in range(21):
        a = 2 * math.pi * j / 20
        pts.append((0.024 + math.cos(a) * 0.022, 0.036 + math.sin(a) * 0.015, 0.058))
    strip_loft(bm, uv, pts, "glow", half_w=0.0035, half_t=0.0035)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_TsukaJadeWrap", col)
    grip_braid(bm, uv, 0.045, -0.40, 12, 9, 0.026, 0.004, thick_every=2, thick=0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_KashiraJadeCap", col)
    bulb_pommel(bm, uv, -0.400, [0.012, 0.024, 0.030, 0.024, 0.012, 0.004], 9, squash=0.9, drop=0.075, ring_r=0.030, ring_z=-0.440)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_JadeFittings", col)
    ferrule_pair(bm, uv, [(0.050, 0.100)], 0.030, squash=0.6)
    ferrule_pair(bm, uv, [(-0.365, -0.395)], 0.029, squash=0.95)
    commit(obj, bm)

# =============================================================================
# E. awakening_runebark_codex_blade - "Espada Codice de Corteza Runica" (arcane)
# =============================================================================
def build_runebark(col):
    def codex_section(z, p):
        # 14-vert broad grimoire-page blade with squared-off tip
        xs, xe = p["x_spine"], p["x_edge"]
        w = xe - xs
        ht = p["half_t"]
        ye = 0.0026
        return [
            Vector((xe,             ye,        z)),
            Vector((xs + 0.84 * w,  ht,        z)),
            Vector((xs + 0.60 * w,  ht * 0.72, z)),
            Vector((xs + 0.36 * w,  ht * 0.98, z)),
            Vector((xs + 0.15 * w,  ht * 0.64, z)),
            Vector((xs + 0.05 * w,  ht * 0.28, z)),
            Vector((xs,             ht * 0.10, z)),
            Vector((xs,             -ht * 0.10,z)),
            Vector((xs + 0.05 * w,  -ht * 0.28,z)),
            Vector((xs + 0.15 * w,  -ht * 0.64,z)),
            Vector((xs + 0.36 * w,  -ht * 0.98,z)),
            Vector((xs + 0.60 * w,  -ht * 0.72,z)),
            Vector((xs + 0.84 * w,  -ht,       z)),
            Vector((xe,             -ye,       z)),
        ]

    stations = []
    zs = [0.06, 0.14, 0.34, 0.58, 0.84, 1.10, 1.36, 1.60, 1.82, 1.98, 2.06]
    for i, z in enumerate(zs):
        t = z / 2.06
        width = 0.092 if i >= 8 else (0.160 - 0.070 * t)
        stations.append((z, {
            "x_spine": -0.052, "x_edge": -0.052 + width,
            "half_t": 0.022 * (1.0 - 0.45 * t) + 0.004,
            "v": t,
        }))

    obj, bm, uv = new_mesh_obj("Blade_RunebarkCodexBlade", col)
    rings, vs = make_rings(stations, codex_section)
    add_lofted_tube(bm, uv, rings, vs, "blade")
    commit(obj, bm)

    # Runic glyph columns: 4 glowing glyph blocks per face
    obj, bm, uv = new_mesh_obj("Inlay_RunicGlyphColumns", col)
    for sy in (1.0, -1.0):
        for k, (za, zb) in enumerate([(0.42, 0.58), (0.72, 0.88), (1.02, 1.18), (1.32, 1.48)]):
            pts = []
            for i in range(4):
                t = i / 3.0
                z = za + (zb - za) * t
                pts.append((-0.052 + 0.070 + 0.018 * math.sin(t * 9.0 + k), sy * 0.021, z))
            strip_loft(bm, uv, pts, "glow", half_w=0.007, half_t=0.004)
    commit(obj, bm)

    # Codex cover guard: 2 slanted slabs + spine bar (open grimoire)
    obj, bm, uv = new_mesh_obj("Guard_CodexCoverSlabs", col)
    for sx in (1.0, -1.0):
        rings, vs = [], []
        for i, z in enumerate([0.052, 0.108]):
            lean = 0.018 * i
            x0, x1 = sx * 0.024, sx * 0.150
            y0, y1 = -0.036, 0.036
            rings.append([Vector((x0 + lean, y0, z)), Vector((x1 + lean, y0 * 0.7, z)),
                          Vector((x1 + lean, y1 * 0.7, z)), Vector((x0 + lean, y1, z))])
            vs.append(i)
        add_lofted_tube(bm, uv, rings, vs, "flair")
    pts = [(-0.024, 0.0, z) for z in [0.052 + 0.056 * (i / 4.0) for i in range(5)]]
    strip_loft(bm, uv, pts, "flair", half_w=0.008, half_t=0.011)
    commit(obj, bm)

    # Arcane codex heart: rune halo with 3 orbiting glyph stones
    obj, bm, uv = new_mesh_obj("Core_ArcaneCodexHeart", col)
    pts = []
    for j in range(25):
        a = 2 * math.pi * j / 24
        pts.append((math.cos(a) * 0.098, math.sin(a) * 0.098, 0.235))
    strip_loft(bm, uv, pts, "glow", half_w=0.0055, half_t=0.0055)
    for k in range(3):
        a = 2 * math.pi * k / 3.0 + 0.5
        path = [Vector((math.cos(a) * (0.100 + 0.018 * t), math.sin(a) * (0.100 + 0.018 * t), 0.235 + 0.010 * math.sin(t * 3.0))) for t in [i / 4.0 for i in range(5)]]
        curved_loft(bm, uv, path, lambda t: 0.012 * (1.0 - t) + 0.004, 7, "glow")
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Grip_RuneScriptHilt", col)
    grip_braid(bm, uv, 0.055, -0.45, 11, 9, 0.029, 0.005)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Pommel_RuneSealStamp", col)
    bulb_pommel(bm, uv, -0.450, [0.014, 0.032, 0.041, 0.035, 0.020, 0.006], 9, squash=1.0, drop=0.10, ring_r=0.040, ring_z=-0.500)
    commit(obj, bm)

    obj, bm, uv = new_mesh_obj("Ferrule_ArcaneBronze", col)
    ferrule_pair(bm, uv, [(0.02, 0.055), (-0.415, -0.445)], 0.034)
    commit(obj, bm)

# =============================================================================
SWORD_META = {
    "sunbark": {
        "name": "sword_04_sunbark_vow", "builder": build_sunbark, "tex": "sunbark_vow",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "sunbark_vow"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage04_swords", "sunbark_vow"),
    },
    "thornheart": {
        "name": "sword_04_thornheart_hex", "builder": build_thornheart, "tex": "thornheart_hex",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "thornheart_hex"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage04_swords", "thornheart_hex"),
    },
    "fulgurite": {
        "name": "sword_04_fulgurite_crest", "builder": build_fulgurite, "tex": "fulgurite_crest",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "fulgurite_crest"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage04_swords", "fulgurite_crest"),
    },
    "jadeanima": {
        "name": "sword_04_jade_anima", "builder": build_jadeanima, "tex": "jade_anima",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "jade_anima"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage04_swords", "jade_anima"),
    },
    "runebark": {
        "name": "sword_04_runebark_codex", "builder": build_runebark, "tex": "runebark_codex",
        "out_dir": os.path.join(REPO, "godot_project", "assets", "models", "swords", "runebark_codex"),
        "art_dir": os.path.join(REPO, "art_pipeline", "stage04_swords", "runebark_codex"),
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
    sword = "sunbark"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                sword = a.split("=", 1)[1]
    meta = SWORD_META[sword]

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.context.scene.collection
    meta["builder"](col)

    sword_root = bpy.data.objects.new("Sword_04_Root", None)
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
    print("STAGE04_BUILD_DONE", sword)

main()

# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 03: atlas PBR 1024x1024 x 5 mapas para las 4 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage03_pbr_maps.py [amber|ironwood|willow|bramble|all]
"""
import sys
import os
import numpy as np
from PIL import Image

N = 1024
R_BLADE = (0, 512, 0, 512)
R_FLAIR = (0, 512, 512, 1024)
R_GRIP = (512, 1024, 0, 512)
R_SHELL = (512, 1024, 512, 768)
R_GLOW = (512, 1024, 768, 1024)


def fbm(h, w, freqs, seed=42):
    rng = np.random.default_rng(seed)
    yy = np.linspace(0.0, 1.0, h, endpoint=False)[:, None]
    xx = np.linspace(0.0, 1.0, w, endpoint=False)[None, :]
    acc = np.zeros((h, w), dtype=np.float32)
    amp = 0.0
    for fx, fy, a in freqs:
        p1, p2, p3 = rng.uniform(0, 2 * np.pi, 3)
        wave = (
            np.sin(2 * np.pi * (xx * fx + yy * fy * 0.25) + p1)
            + 0.6 * np.cos(2 * np.pi * (xx * fx * 0.7 - yy * fy * 0.35) + p2)
            + 0.35 * np.sin(2 * np.pi * (xx * fx * 1.4 + yy * fy * 0.8) + p3)
        ) / 1.95
        acc += a * wave
        amp += a
    return acc / max(1e-5, amp)


def new_atlas():
    return (np.zeros((N, N, 3), dtype=np.float32), np.full((N, N), 0.62, dtype=np.float32),
            np.zeros((N, N), dtype=np.float32), np.zeros((N, N), dtype=np.float32),
            np.zeros((N, N, 3), dtype=np.float32))


def place(base, rough, metal, height, emis, region, arr):
    y0, y1, x0, x1 = region
    base[y0:y1, x0:x1] = arr["base"]
    rough[y0:y1, x0:x1] = arr["rough"]
    metal[y0:y1, x0:x1] = arr["metal"]
    height[y0:y1, x0:x1] = arr["height"]
    emis[y0:y1, x0:x1] = arr["emis"]


def normal_from_height(height):
    sx = np.zeros_like(height); sy = np.zeros_like(height)
    sx[1:-1, 1:-1] = (height[1:-1, 2:] - height[1:-1, :-2]) * 2.0
    sy[1:-1, 1:-1] = (height[2:, 1:-1] - height[:-2, 1:-1]) * 2.0
    n = np.dstack([-sx, sy, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return np.clip(n * 0.5 + 0.5, 0.0, 1.0)


def paint_amber():
    """Blessed: claymore de catedral, madera dorada + resina de ambar vitrea caliente."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: pale sanctified wood with golden cathedral grain
    warp = fbm(H, W, [(3, 2, 1.0), (8, 5, 0.5)], seed=401)
    grain = np.power(0.5 + 0.5 * np.sin((xx * 17.0 + warp * 4.5) * np.pi), 1.8)
    fiber = 0.5 + 0.5 * np.sin((xx * 130.0 + yy * 4.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1)
    c_hi = np.array([0.92, 0.78, 0.48]); c_mid = np.array([0.78, 0.60, 0.30]); c_lo = np.array([0.55, 0.38, 0.16])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col * (0.94 + 0.12 * fiber[:, :, None]) + c_hi[None, None] * (0.28 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.46 - 0.12 * edge + 0.08 * grain, 0.30, 0.68),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.35 * grain + 0.15 * fiber,
        "emis": np.clip(np.stack([edge * 0.10, edge * 0.06, edge * 0.01], axis=2), 0, 0.25),
    })
    # TR flair: gilded sanctuary wings (warm gold leaf with soft damascene)
    damas = np.power(0.5 + 0.5 * np.sin((yy * 34.0 + xx * 6.0 + warp * 3.0) * np.pi), 2.0)
    gold_grit = fbm(H, W, [(14, 11, 1.0)], seed=403)
    c_g1 = np.array([0.93, 0.78, 0.38]); c_g2 = np.array([0.72, 0.52, 0.20])
    col2 = c_g2[None, None] * (0.8 + 0.4 * damas[:, :, None])
    col2 = col2 * (0.94 + 0.10 * gold_grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.12 * gold_grit - 0.10 * damas, 0.18, 0.5),
        "metal": np.full((H, W), 0.82, dtype=np.float32),
        "height": 0.35 * damas,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: resin-wrapped hilt (warm braid with amber drips)
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=405)
    c_w1 = np.array([0.50, 0.34, 0.14]); c_w2 = np.array([0.30, 0.18, 0.07])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.55 - 0.12 * weave, 0.35, 0.75),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: gilded bronze ferrules
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=407)
    col4 = c_g2[None, None] * (0.85 + 0.25 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.14 * hammer, 0.18, 0.55),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: amber resin inclusions & veins (hot golden emission, glassy)
    Hg, Wg = 512, 256
    res_warp = fbm(Hg, Wg, [(5, 9, 1.0), (13, 20, 0.5)], seed=409)
    veins = np.power(0.5 + 0.5 * np.sin((yy * 38.0 + res_warp * 5.0) * np.pi), 2.6)
    bubbles = np.clip(res_warp * 2.4 - 0.9, 0, 1)
    hot = np.clip(veins * 0.75 + bubbles * 0.55, 0, 1)
    em = np.clip(np.stack([1.0 * hot, 0.78 * hot, 0.32 * hot], axis=2), 0, 1)
    c_res = np.array([0.85, 0.60, 0.18])
    col5 = c_res[None, None] * (0.55 + 0.5 * res_warp[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.14 + 0.12 * bubbles, 0.08, 0.35),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.4 * veins + 0.5 * bubbles,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_ironwood():
    """Elemental: losa de palo ferro con bandas de hierro y motifs de tormenta."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: dark ironwood grain + iron sheen near the edge
    warp = fbm(H, W, [(4, 3, 1.0), (10, 7, 0.5)], seed=421)
    grain = np.power(0.5 + 0.5 * np.sin((xx * 15.0 + warp * 5.0) * np.pi), 2.0)
    fiber = 0.5 + 0.5 * np.sin((xx * 150.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1)
    c_w1 = np.array([0.24, 0.20, 0.15]); c_w2 = np.array([0.12, 0.10, 0.08]); c_edge = np.array([0.55, 0.58, 0.62])
    col = c_w1[None, None] * (1 - 0.55 * grain[:, :, None]) + c_w2[None, None] * (0.55 * grain[:, :, None])
    col = col * (0.92 + 0.14 * fiber[:, :, None])
    col = col + c_edge[None, None] * (0.35 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.58 - 0.25 * edge + 0.08 * grain, 0.26, 0.78),
        "metal": np.clip(0.45 * edge, 0, 0.5),
        "height": -0.4 * grain + 0.15 * fiber,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # TR flair: storm-forged iron quillons (blued steel + rain etching)
    rain = np.power(0.5 + 0.5 * np.sin((yy * 90.0 + xx * 10.0) * np.pi), 3.0)
    bluing = fbm(H, W, [(6, 5, 1.0), (17, 14, 0.5)], seed=423)
    c_i1 = np.array([0.45, 0.49, 0.56]); c_i2 = np.array([0.20, 0.23, 0.30]); c_blue = np.array([0.16, 0.22, 0.38])
    col2 = c_i2[None, None] * (0.85 + 0.35 * bluing[:, :, None])
    col2 = col2 * (1 - 0.30 * rain[:, :, None]) + c_i1[None, None] * (0.30 * rain[:, :, None])
    col2 = col2 * (1 - 0.25 * np.clip(bluing * 1.6 - 0.5, 0, 1)[:, :, None]) + c_blue[None, None] * (0.25 * np.clip(bluing * 1.6 - 0.5, 0, 1)[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.34 - 0.10 * rain + 0.10 * bluing, 0.20, 0.6),
        "metal": np.full((H, W), 0.90, dtype=np.float32),
        "height": -0.4 * rain + 0.3 * bluing,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: storm-wrapped leather (dark braid, rain streaks)
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.6))
    grit = fbm(H, W, [(19, 19, 1.0)], seed=425)
    c_l1 = np.array([0.16, 0.15, 0.14]); c_l2 = np.array([0.28, 0.27, 0.25])
    col3 = c_l1[None, None] + (c_l2 - c_l1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.9 + 0.16 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.62 - 0.10 * weave, 0.45, 0.8),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.6 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: raw iron bands
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(11, 11, 1.0), (27, 25, 0.5)], seed=427)
    col4 = c_i2[None, None] * (0.85 + 0.3 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.36 + 0.16 * hammer, 0.25, 0.62),
        "metal": np.full((Hb, Wb), 0.92, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: storm rosettes & bolt seams (electric cyan-white)
    Hg, Wg = 512, 256
    bolt = fbm(Hg, Wg, [(7, 13, 1.0), (18, 28, 0.5)], seed=429)
    crack = np.power(0.5 + 0.5 * np.sin((yy * 46.0 + bolt * 7.0) * np.pi), 3.2)
    ros = np.clip(bolt * 2.6 - 1.25, 0, 1)
    hot = np.clip(crack * 0.8 + ros * 0.5, 0, 1)
    em = np.clip(np.stack([0.45 * hot, 0.80 * hot, 1.0 * hot], axis=2), 0, 1)
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(c_i2[None, None] * (0.8 + 0.4 * bolt[:, :, None]), 0, 1),
        "rough": np.clip(0.4 - 0.25 * hot, 0.15, 0.6),
        "metal": np.full((Hg, Wg), 0.35, dtype=np.float32),
        "height": -0.5 * crack,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_willow():
    """Spiritual: sable de sauce etereo, madera palida lunar + franjas fantasma."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: moon-pale willow wood, near-white with silver fiber
    warp = fbm(H, W, [(3, 2, 1.0), (9, 6, 0.5)], seed=441)
    grain = np.power(0.5 + 0.5 * np.sin((xx * 14.0 + warp * 4.0) * np.pi), 2.2)
    fiber = 0.5 + 0.5 * np.sin((xx * 170.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1)
    c_p1 = np.array([0.88, 0.90, 0.86]); c_p2 = np.array([0.70, 0.74, 0.68]); c_p3 = np.array([0.52, 0.58, 0.52])
    col = c_p2[None, None] * (1 - 0.5 * grain[:, :, None]) + c_p3[None, None] * (0.5 * grain[:, :, None])
    col = col * (0.95 + 0.10 * fiber[:, :, None]) + c_p1[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.42 - 0.16 * edge + 0.08 * grain, 0.26, 0.62),
        "metal": np.clip(0.25 * edge, 0, 0.3),
        "height": -0.3 * grain + 0.12 * fiber,
        "emis": np.clip(np.stack([edge * 0.08, edge * 0.12, edge * 0.14], axis=2), 0, 0.3),
    })
    # TR flair: spectral willow fronds (pale green-grey with soft veins)
    frond_warp = fbm(H, W, [(5, 8, 1.0), (13, 22, 0.5)], seed=443)
    midrib = np.power(0.5 + 0.5 * np.sin((yy * 50.0 + xx * 4.0) * np.pi), 2.5)
    c_f1 = np.array([0.55, 0.66, 0.55]); c_f2 = np.array([0.34, 0.44, 0.38])
    col2 = c_f2[None, None] * (0.8 + 0.4 * frond_warp[:, :, None])
    col2 = col2 + c_f1[None, None] * (0.35 * midrib[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.52 - 0.16 * midrib, 0.35, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.3 * midrib,
        "emis": np.clip(np.stack([midrib * 0.10, midrib * 0.20, midrib * 0.18], axis=2), 0, 0.4),
    })
    # BL grip: ghost-willow wrap (pale braid, wispy)
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 24 + yy * 24) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 24 - yy * 24) * np.pi), 1.6))
    grit = fbm(H, W, [(18, 18, 1.0)], seed=445)
    col3 = c_p3[None, None] * (0.8 + 0.3 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.12 * weave, 0.4, 0.75),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.5 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: silvermist ferrules
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=447)
    c_s1 = np.array([0.72, 0.75, 0.78])
    col4 = c_s1[None, None] * (0.85 + 0.22 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.26 + 0.12 * hammer, 0.16, 0.5),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: spirit lantern core & ethereal seam (moon-cyan emission)
    Hg, Wg = 512, 256
    sp_warp = fbm(Hg, Wg, [(6, 11, 1.0), (15, 24, 0.5)], seed=449)
    wisps = np.power(0.5 + 0.5 * np.sin((yy * 36.0 + sp_warp * 6.0) * np.pi), 3.0)
    orbs = np.clip(sp_warp * 2.3 - 0.85, 0, 1)
    hot = np.clip(wisps * 0.7 + orbs * 0.6, 0, 1)
    em = np.clip(np.stack([0.55 * hot, 0.92 * hot, 1.0 * hot], axis=2), 0, 1)
    col5 = np.array([0.70, 0.78, 0.80])[None, None] * (0.7 + 0.4 * sp_warp[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.18 + 0.10 * orbs, 0.10, 0.35),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.35 * wisps + 0.4 * orbs,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_bramble():
    """Cursed: zarza sanguina, madera negra-vino con savia de sangre emisiva."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: black-wine bramble wood with deep red grain
    warp = fbm(H, W, [(4, 3, 1.0), (12, 8, 0.55)], seed=461)
    grain = np.power(0.5 + 0.5 * np.sin((xx * 19.0 + warp * 5.5) * np.pi), 2.0)
    fiber = 0.5 + 0.5 * np.sin((xx * 140.0 + yy * 4.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1)
    c_b1 = np.array([0.16, 0.05, 0.05]); c_b2 = np.array([0.07, 0.02, 0.025]); c_red = np.array([0.34, 0.04, 0.05])
    col = c_b1[None, None] * (1 - 0.55 * grain[:, :, None]) + c_b2[None, None] * (0.55 * grain[:, :, None])
    col = col * (0.92 + 0.14 * fiber[:, :, None])
    col = col + c_red[None, None] * (0.28 * grain[:, :, None] * edge[:, :, None] + 0.10 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.55 - 0.15 * edge + 0.08 * grain, 0.30, 0.72),
        "metal": np.clip(0.25 * edge, 0, 0.3),
        "height": -0.45 * grain + 0.15 * fiber,
        "emis": np.clip(np.stack([grain * edge * 0.45, grain * edge * 0.05, grain * edge * 0.04], axis=2), 0, 0.5),
    })
    # TR flair: black thorn bark with blood veins
    thorn_warp = fbm(H, W, [(6, 5, 1.0), (17, 14, 0.5)], seed=463)
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 32.0 + thorn_warp * 5.0) * np.pi), 2.0)
    blood = np.clip(thorn_warp * 1.8 - 0.55, 0, 1)
    col2 = c_b2[None, None] * (0.8 + 0.4 * ridge[:, :, None])
    col2 = col2 * (1 - blood[:, :, None]) + c_red[None, None] * blood[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.60 - 0.18 * ridge - 0.15 * blood, 0.28, 0.8),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * ridge - 0.3 * blood,
        "emis": np.clip(np.stack([blood * 0.35, blood * 0.04, blood * 0.04], axis=2), 0, 0.4),
    })
    # BL grip: bloodbark wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=465)
    col3 = c_b2[None, None] + (c_b1 - c_b2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.68 - 0.12 * weave, 0.5, 0.85),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave + 0.12 * grit,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: blood iron
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(11, 11, 1.0), (26, 24, 0.5)], seed=467)
    c_i = np.array([0.20, 0.12, 0.12])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.45 + 0.15 * hammer, 0.32, 0.72),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: bleeding heart core & sap drips (crimson emission)
    Hg, Wg = 512, 256
    drip_warp = fbm(Hg, Wg, [(6, 12, 1.0), (16, 26, 0.5)], seed=469)
    drips = np.power(0.5 + 0.5 * np.sin((yy * 42.0 + drip_warp * 5.0) * np.pi), 2.8)
    pools = np.clip(drip_warp * 2.4 - 0.95, 0, 1)
    hot = np.clip(drips * 0.65 + pools * 0.6, 0, 1)
    em = np.clip(np.stack([1.0 * hot, 0.12 * hot, 0.10 * hot], axis=2), 0, 1)
    col5 = c_red[None, None] * (0.6 + 0.5 * drip_warp[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.12 * hot, 0.16, 0.45),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.4 * drips + 0.4 * pools,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"amber": paint_amber, "ironwood": paint_ironwood, "willow": paint_willow, "bramble": paint_bramble}
OUT_DIRS = {
    "amber": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/amber_sanctuary",
    "ironwood": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/ironwood_storm",
    "willow": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/spirit_willow",
    "bramble": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/bloodsap_bramble",
}
TEX_BASE = {"amber": "amber_sanctuary", "ironwood": "ironwood_storm", "willow": "spirit_willow", "bramble": "bloodsap_bramble"}


def save_maps(which):
    base, rough, metal, height, emis = PAINTERS[which]()
    out_dir = OUT_DIRS[which]
    tb = TEX_BASE[which]
    os.makedirs(out_dir, exist_ok=True)
    Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8)).save("%s/%s_basecolor.png" % (out_dir, tb))
    Image.fromarray((np.clip(rough, 0, 1) * 255).astype(np.uint8)).save("%s/%s_roughness.png" % (out_dir, tb))
    Image.fromarray((np.clip(metal, 0, 1) * 255).astype(np.uint8)).save("%s/%s_metallic.png" % (out_dir, tb))
    Image.fromarray((normal_from_height(height) * 255).astype(np.uint8)).save("%s/%s_normal.png" % (out_dir, tb))
    Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8)).save("%s/%s_emission.png" % (out_dir, tb))
    print("PBR_SAVED", which, out_dir)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    for w in (list(PAINTERS.keys()) if arg == "all" else [arg]):
        save_maps(w)

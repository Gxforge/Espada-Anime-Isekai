# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 06: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [auric|reaver|glacier|mistwalk|astrolabe|all]
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


def paint_auric():
    """Blessed: Claymore Bastion Aurico, oro vivo fundido con almenas de laton."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: molten living gold with flow bands
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=571)
    flow = np.power(0.5 + 0.5 * np.sin((xx * 12.0 + warp * 4.0) * np.pi), 1.8)
    fiber = 0.5 + 0.5 * np.sin((xx * 120.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.99, 0.93, 0.66]); c_mid = np.array([0.92, 0.78, 0.32]); c_lo = np.array([0.62, 0.44, 0.12])
    col = c_mid[None, None] * (1 - 0.45 * flow[:, :, None]) + c_lo[None, None] * (0.45 * flow[:, :, None])
    col = col * (0.92 + 0.14 * fiber[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.08 * edge + 0.05 * flow, 0.13, 0.42),
        "metal": np.full((H, W), 0.84, dtype=np.float32),
        "height": -0.22 * flow + 0.12 * fiber,
        "emis": np.clip(np.stack([edge * (0.20 + 0.12 * flow), edge * 0.12, edge * 0.02], axis=2), 0, 0.36),
    })
    # TR flair: warm brass ramparts
    hammer = fbm(H, W, [(10, 9, 1.0), (23, 21, 0.5)], seed=573)
    c_b1 = np.array([0.76, 0.58, 0.26]); c_b2 = np.array([0.54, 0.38, 0.15])
    col2 = c_b2[None, None] * (0.85 + 0.32 * hammer[:, :, None]) + c_b1[None, None] * (0.22 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.12 * hammer, 0.18, 0.54),
        "metal": np.full((H, W), 0.84, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: gold-thread dark wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=575)
    c_w1 = np.array([0.40, 0.30, 0.14]); c_w2 = np.array([0.20, 0.15, 0.07])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 + c_hi[None, None] * (0.10 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: brass
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=577)
    col4 = c_b1[None, None] * (0.84 + 0.26 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.13 * hammer2, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.86, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: molten gold pool
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0)], seed=579)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.3, 0, 1) ** 1.4
    pool = np.power(0.5 + 0.5 * np.sin((yy * 18.0 + warp_g * 5.0) * np.pi), 2.4) * np.clip(1.0 - r * 1.6, 0, 1)
    glow_amt = np.clip(hot + 0.4 * pool, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.84 * glow_amt, 0.30 * hot], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * hot, 0.14, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_reaver():
    """Cursed: Hendidora Segadora Carmesi, acero segador oscuro + luna de cosecha."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: dark reaper steel with crimson cutting streaks
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=581)
    streak = np.power(0.5 + 0.5 * np.sin((xx * 14.0 + warp * 5.0) * np.pi), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.52, 0.22, 0.24]); c_mid = np.array([0.24, 0.10, 0.12]); c_lo = np.array([0.12, 0.05, 0.06])
    c_crim = np.array([0.90, 0.12, 0.16])
    col = c_mid[None, None] * (1 - 0.5 * streak[:, :, None]) + c_lo[None, None] * (0.5 * streak[:, :, None])
    col = col + c_hi[None, None] * (0.24 * streak[:, :, None]) + c_crim[None, None] * (0.26 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 - 0.12 * edge + 0.06 * streak, 0.18, 0.56),
        "metal": np.clip(0.55 + 0.12 * edge, 0, 0.72),
        "height": -0.28 * streak + 0.12 * edge,
        "emis": np.clip(np.stack([edge * (0.30 + 0.14 * streak), edge * 0.05, edge * 0.06], axis=2), 0, 0.5),
    })
    # TR flair: harvest burl wood
    burl = fbm(H, W, [(7, 6, 1.0), (16, 13, 0.5)], seed=583)
    c_b1 = np.array([0.28, 0.14, 0.10]); c_b2 = np.array([0.15, 0.07, 0.05])
    col2 = c_b2[None, None] * (0.85 + 0.34 * burl[:, :, None]) + c_b1[None, None] * (0.20 * burl[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.62 + 0.10 * burl, 0.46, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.4 * burl,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: blood leather
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=585)
    c_w1 = np.array([0.24, 0.10, 0.10]); c_w2 = np.array([0.12, 0.05, 0.05])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.64 - 0.12 * weave, 0.46, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: blood iron
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(12, 11, 1.0), (26, 24, 0.5)], seed=587)
    c_i = np.array([0.22, 0.12, 0.13])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.44 + 0.14 * hammer, 0.30, 0.70),
        "metal": np.full((Hb, Wb), 0.66, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: harvest moon (crimson disc with crescent shadow)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.48) * 1.1) ** 2 + (xxg - 0.5) ** 2)
    disc = np.clip(1.0 - r * 2.6, 0, 1) ** 1.2
    cres = np.clip(np.sqrt(((yy - 0.54) * 1.1) ** 2 + (xxg - 0.60) ** 2) * 2.6 - 0.4, 0, 1)
    glow_amt = np.clip(disc * (0.35 + 0.65 * cres), 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.24 * glow_amt, 0.20 * glow_amt], axis=2), 0, 1)
    col5 = c_crim[None, None] * (0.5 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.28 - 0.12 * glow_amt, 0.15, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.35 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_glacier():
    """Elemental: Espada Larga Colmillo de Glaciar, hielo glaciar palido + escarcha."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: pale glacier ice with deep crevasse streaks
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=591)
    crev = np.power(0.5 + 0.5 * np.sin((xx * 9.0 + warp * 5.5) * np.pi), 3.4)
    frost = fbm(H, W, [(16, 13, 1.0)], seed=593)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.94, 0.99, 1.0]); c_mid = np.array([0.66, 0.86, 0.95]); c_lo = np.array([0.34, 0.58, 0.76])
    col = c_mid[None, None] * (1 - 0.45 * crev[:, :, None]) + c_lo[None, None] * (0.45 * crev[:, :, None])
    col = col + c_hi[None, None] * (0.28 * edge[:, :, None] + 0.22 * frost[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.14 + 0.06 * crev, 0.08, 0.32),
        "metal": np.clip(0.04 + 0.04 * edge, 0, 0.12),
        "height": -0.24 * crev + 0.12 * frost,
        "emis": np.clip(np.stack([0.25 * crev, 0.45 * crev, 0.60 * crev], axis=2), 0, 0.6),
    })
    # TR flair: frozen steel with hoarfrost
    hammer = fbm(H, W, [(10, 9, 1.0), (22, 20, 0.5)], seed=595)
    hoar = fbm(H, W, [(15, 12, 1.0)], seed=597)
    c_s1 = np.array([0.52, 0.64, 0.72]); c_s2 = np.array([0.30, 0.42, 0.52])
    col2 = c_s2[None, None] * (0.85 + 0.30 * hammer[:, :, None]) + c_hi[None, None] * (0.16 * hoar[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.36 + 0.10 * hammer - 0.08 * hoar, 0.20, 0.58),
        "metal": np.full((H, W), 0.72, dtype=np.float32),
        "height": 0.26 * hammer + 0.18 * hoar,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: frost-blue wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=599)
    c_w1 = np.array([0.24, 0.40, 0.52]); c_w2 = np.array([0.12, 0.22, 0.30])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.36, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: frozen silver
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=601)
    c_s = np.array([0.62, 0.72, 0.78])
    col4 = c_s[None, None] * (0.86 + 0.24 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.12 * hammer2, 0.15, 0.48),
        "metal": np.full((Hb, Wb), 0.86, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: frozen star (white core, cyan corona)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    core = np.clip(1.0 - r * 3.0, 0, 1) ** 1.6
    corona = np.clip(1.0 - r * 1.6, 0, 1) * np.power(0.5 + 0.5 * np.sin(np.arctan2(yy - 0.5, xxg - 0.5) * 6.0), 3.0)
    glow_amt = np.clip(core + 0.5 * corona, 0, 1)
    em = np.clip(np.stack([0.80 * glow_amt + 0.2 * core, 0.96 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.7 + 0.4 * core[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.20 - 0.10 * core, 0.10, 0.36),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * core,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_mistwalk():
    """Spiritual: Katana Caminante de la Niebla, bambu pálido con nudos + niebla menta."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: pale bamboo with vertical fiber and horizontal node bands
    warp = fbm(H, W, [(3, 2, 1.0), (8, 5, 0.5)], seed=605)
    fiber = 0.5 + 0.5 * np.sin((xx * 95.0 + yy * 6.0) * np.pi)
    nodes = np.power(0.5 + 0.5 * np.sin(yy * 20.0 * np.pi), 5.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.85, 0.90, 0.62]); c_mid = np.array([0.62, 0.72, 0.40]); c_lo = np.array([0.40, 0.50, 0.24])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col + c_hi[None, None] * (0.22 * edge[:, :, None]) + c_lo[None, None] * (0.20 * nodes[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.46 + 0.10 * nodes - 0.06 * edge, 0.30, 0.66),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.14 * fiber + 0.45 * nodes,
        "emis": np.clip(np.stack([0.04 * edge, 0.10 * edge, 0.04 * edge], axis=2), 0, 0.12),
    })
    # TR flair: dark bamboo sheath
    sheath = fbm(H, W, [(8, 7, 1.0), (18, 15, 0.5)], seed=607)
    band = np.power(0.5 + 0.5 * np.sin((yy * 18.0 + sheath * 2.0) * np.pi), 3.0)
    c_d1 = np.array([0.22, 0.26, 0.12]); c_d2 = np.array([0.12, 0.15, 0.06])
    col2 = c_d2[None, None] * (0.85 + 0.34 * band[:, :, None]) + c_d1[None, None] * (0.22 * band[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.52 + 0.10 * band, 0.36, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.36 * band + 0.2 * sheath,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: woven bamboo silk
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 30 + yy * 30) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 30 - yy * 30) * np.pi), 1.8))
    grit = fbm(H, W, [(22, 22, 1.0)], seed=609)
    c_w1 = np.array([0.55, 0.60, 0.36]); c_w2 = np.array([0.30, 0.36, 0.18])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.14 * weave, 0.38, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: jade-green bamboo fittings
    Hb, Wb = 512, 256
    stone = fbm(Hb, Wb, [(8, 8, 1.0), (19, 17, 0.5)], seed=611)
    c_s = np.array([0.30, 0.52, 0.34])
    col4 = c_s[None, None] * (0.85 + 0.26 * stone[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.30 + 0.12 * stone, 0.18, 0.52),
        "metal": np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.25 * stone,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: drifting mist blobs (soft white-mint)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(5, 8, 1.0), (11, 15, 0.5)], seed=613)
    mist = np.clip(warp_g * 1.9 - 0.5, 0, 1) ** 1.5
    haze = 0.5 + 0.5 * np.sin((yy * 12.0 + xxg * 5.0 + warp_g * 6.0) * np.pi)
    glow_amt = np.clip(mist * (0.5 + 0.5 * haze), 0, 1)
    em = np.clip(np.stack([0.85 * glow_amt, 0.98 * glow_amt, 0.92 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.40 - 0.10 * glow_amt, 0.24, 0.54),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.15 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_astrolabe():
    """Arcane: Hoja Anillo de Astrolabio, aciero chartografado + laton dorado."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: dark charted steel with gold star-chart etch lines
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=615)
    etch = np.clip(np.abs(np.sin(xx * 20.0 + warp * 3.0) * np.sin(yy * 14.0 - warp * 2.0)) - 0.55, 0, 1) * 2.2
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.62, 0.68, 0.85]); c_mid = np.array([0.30, 0.36, 0.55]); c_lo = np.array([0.16, 0.20, 0.36])
    c_gold = np.array([0.90, 0.76, 0.40])
    col = c_mid[None, None] * (1 - 0.5 * etch[:, :, None]) + c_lo[None, None] * (0.5 * etch[:, :, None])
    col = col + c_hi[None, None] * (0.24 * edge[:, :, None]) + c_gold[None, None] * (0.30 * etch[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.30 - 0.10 * edge + 0.05 * etch, 0.18, 0.48),
        "metal": np.clip(0.62 + 0.10 * edge, 0, 0.78),
        "height": -0.12 * etch + 0.10 * edge,
        "emis": np.clip(np.stack([0.55 * etch, 0.42 * etch, 0.18 * etch], axis=2), 0, 0.55),
    })
    # TR flair: antique brass
    hammer = fbm(H, W, [(10, 9, 1.0), (23, 21, 0.5)], seed=617)
    c_b1 = np.array([0.74, 0.60, 0.30]); c_b2 = np.array([0.52, 0.40, 0.18])
    col2 = c_b2[None, None] * (0.85 + 0.32 * hammer[:, :, None]) + c_b1[None, None] * (0.22 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.32 + 0.12 * hammer, 0.20, 0.56),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: navy leather with gold stitch
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    stitch = 0.5 + 0.5 * np.sin((xx * 60.0 + yy * 6.0) * np.pi)
    grit = fbm(H, W, [(21, 21, 1.0)], seed=619)
    c_w1 = np.array([0.14, 0.16, 0.34]); c_w2 = np.array([0.08, 0.09, 0.20])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 + c_gold[None, None] * (0.10 * weave[:, :, None] * stitch[:, :, None])
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.56 - 0.12 * weave, 0.40, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave + 0.10 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: brass
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=621)
    col4 = c_b1[None, None] * (0.84 + 0.26 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.30 + 0.13 * hammer2, 0.19, 0.54),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: polaris star (gold-white with cross flare)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    core = np.clip(1.0 - r * 2.8, 0, 1) ** 1.5
    flare_h = np.exp(-(((yy - 0.5) ** 2) / 0.003)) * np.clip(1.0 - np.abs(xxg - 0.5) * 2.2, 0, 1)
    flare_v = np.exp(-(((xxg - 0.5) ** 2) / 0.006)) * np.clip(1.0 - np.abs(yy - 0.5) * 2.0, 0, 1)
    glow_amt = np.clip(core + 0.5 * flare_h + 0.5 * flare_v, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.90 * glow_amt, 0.62 * glow_amt], axis=2), 0, 1)
    col5 = c_gold[None, None] * (0.6 + 0.5 * core[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * core, 0.15, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * core,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"auric": paint_auric, "reaver": paint_reaver, "glacier": paint_glacier,
            "mistwalk": paint_mistwalk, "astrolabe": paint_astrolabe}
OUT_DIRS = {
    "auric": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/auric_bastion",
    "reaver": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/crimson_reaver",
    "glacier": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/glacier_fang",
    "mistwalk": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/mistwalker_bamboo",
    "astrolabe": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/astrolabe_ring",
}
TEX_BASE = {"auric": "auric_bastion", "reaver": "crimson_reaver", "glacier": "glacier_fang",
            "mistwalk": "mistwalker_bamboo", "astrolabe": "astrolabe_ring"}


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


def main():
    which = "all"
    if len(sys.argv) > 1 and sys.argv[-1] in PAINTERS:
        which = sys.argv[-1]
    for w in (list(PAINTERS.keys()) if which == "all" else [which]):
        save_maps(w)


main()

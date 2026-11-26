# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 08: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [covenant|bloodmoon|thunderlord|chorus|monolith|twilight|all]
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


def paint_covenant():
    """Blessed: Mandoble de la Alianza Radiante, acero perla + sello dorado gigante."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=681)
    sheen = 0.5 + 0.5 * np.sin((yy * 6.0 + warp * 2.0) * np.pi)
    fiber = 0.5 + 0.5 * np.sin((xx * 120.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.97, 0.95, 0.86]); c_mid = np.array([0.82, 0.81, 0.74]); c_lo = np.array([0.56, 0.55, 0.48])
    c_gold = np.array([0.93, 0.82, 0.44])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col * (0.92 + 0.14 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None]) + c_gold[None, None] * (0.10 * sheen[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.07 * edge + 0.04 * sheen, 0.12, 0.38),
        "metal": np.full((H, W), 0.72, dtype=np.float32),
        "height": 0.10 * sheen - 0.08 * fiber,
        "emis": np.clip(np.stack([edge * 0.20, edge * 0.16, edge * 0.08], axis=2), 0, 0.3),
    })
    damas = np.power(0.5 + 0.5 * np.sin((yy * 30.0 + xx * 7.0 + warp * 3.0) * np.pi), 2.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=683)
    col2 = c_gold[None, None] * (0.80 + 0.35 * damas[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.10 * grit - 0.08 * damas, 0.15, 0.46),
        "metal": np.full((H, W), 0.86, dtype=np.float32),
        "height": 0.35 * damas,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    grit2 = fbm(H, W, [(20, 20, 1.0)], seed=685)
    c_w1 = np.array([0.84, 0.80, 0.66]); c_w2 = np.array([0.50, 0.46, 0.34])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=687)
    col4 = c_gold[None, None] * (0.84 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.26 + 0.13 * hammer, 0.16, 0.50),
        "metal": np.full((Hb, Wb), 0.87, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: sanctuary sigil (concentric gold rings + cross)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    rings = np.power(np.abs(np.sin(r * 16.0 - 0.6)), 8.0) * np.clip(1.0 - r * 1.9, 0, 1)
    cross = np.exp(-(((yy - 0.5) ** 2) / 0.004)) * np.clip(1.0 - np.abs(xxg - 0.5) * 2.4, 0, 1) + \
            np.exp(-(((xxg - 0.5) ** 2) / 0.008)) * np.clip(1.0 - np.abs(yy - 0.5) * 2.2, 0, 1)
    glow_amt = np.clip(0.55 * rings + 0.5 * cross, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.88 * glow_amt, 0.50 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_bloodmoon():
    """Cursed: Mandoble del Pacto Luna Sangrienta, acero de pacto + luna carmesi."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=691)
    vein = np.power(0.5 + 0.5 * np.sin((xx * 8.0 + warp * 6.0) * np.pi), 5.0)
    grain = fbm(H, W, [(13, 11, 1.0)], seed=693)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.48, 0.18, 0.20]); c_mid = np.array([0.22, 0.09, 0.11]); c_lo = np.array([0.11, 0.04, 0.06])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col + c_hi[None, None] * (0.22 * grain[:, :, None] + 0.20 * edge[:, :, None])
    col = col + np.array([0.95, 0.15, 0.18])[None, None] * (0.30 * vein[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.38 + 0.08 * grain - 0.14 * edge, 0.20, 0.60),
        "metal": np.clip(0.50 + 0.12 * edge, 0, 0.68),
        "height": -0.25 * grain + 0.30 * vein,
        "emis": np.clip(np.stack([0.85 * vein, 0.14 * vein, 0.16 * vein], axis=2), 0, 0.7),
    })
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 26.0 + warp * 4.0) * np.pi), 2.2)
    col2 = c_lo[None, None] * (0.8 + 0.5 * ridge[:, :, None]) + c_hi[None, None] * (0.12 * ridge[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.56 - 0.12 * ridge, 0.36, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.42 * ridge,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=695)
    c_w1 = np.array([0.26, 0.12, 0.13]); c_w2 = np.array([0.13, 0.06, 0.07])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.62 - 0.12 * weave, 0.44, 0.80),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(12, 11, 1.0), (26, 24, 0.5)], seed=697)
    c_i = np.array([0.24, 0.13, 0.14])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.44 + 0.14 * hammer, 0.30, 0.70),
        "metal": np.full((Hb, Wb), 0.68, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: blood moon disc with crater texture
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(8, 8, 1.0)], seed=699)
    r = np.sqrt(((yy - 0.48) * 1.1) ** 2 + (xxg - 0.5) ** 2)
    disc = np.clip(1.0 - r * 2.5, 0, 1) ** 1.1
    crater = np.clip(warp_g * 1.6 - 0.45, 0, 1) * disc
    glow_amt = np.clip(disc - 0.4 * crater, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.20 * glow_amt, 0.22 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.5 + 0.5 * disc[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.28 - 0.12 * glow_amt, 0.15, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.35 * glow_amt + 0.2 * crater,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_thunderlord():
    """Elemental: Filo Fulgur del Senor del Trueno, acero tormenta + tridente electrico."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (12, 7, 0.5)], seed=701)
    bolt = np.power(0.5 + 0.5 * np.sin((xx * 11.0 + warp * 7.0) * np.pi), 6.0)
    grain = fbm(H, W, [(14, 12, 1.0)], seed=703)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.72, 0.82, 0.92]); c_mid = np.array([0.36, 0.46, 0.60]); c_lo = np.array([0.18, 0.25, 0.36])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col + c_hi[None, None] * (0.26 * edge[:, :, None]) + np.array([0.90, 0.97, 1.0])[None, None] * (0.35 * bolt[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.28 + 0.06 * grain - 0.12 * edge, 0.16, 0.48),
        "metal": np.clip(0.62 + 0.10 * edge, 0, 0.78),
        "height": -0.20 * grain + 0.30 * bolt,
        "emis": np.clip(np.stack([0.55 * bolt, 0.80 * bolt, 1.0 * bolt], axis=2), 0, 0.9),
    })
    hammer = fbm(H, W, [(10, 9, 1.0), (22, 20, 0.5)], seed=705)
    col2 = c_lo[None, None] * (0.85 + 0.32 * hammer[:, :, None]) + c_mid[None, None] * (0.22 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.40 + 0.12 * hammer, 0.26, 0.64),
        "metal": np.full((H, W), 0.76, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=707)
    c_w1 = np.array([0.16, 0.20, 0.30]); c_w2 = np.array([0.08, 0.11, 0.17])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.54 - 0.12 * weave, 0.38, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=709)
    col4 = c_mid[None, None] * (0.85 + 0.26 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.36 + 0.13 * hammer2, 0.22, 0.60),
        "metal": np.full((Hb, Wb), 0.80, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: thunder bolt sigil (zigzag white-cyan)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    zig = 0.5 + 0.28 * np.sign(np.sin(yy * 9.0 * np.pi)) * (0.4 + 0.6 * np.abs(np.sin(yy * 4.5 * np.pi)))
    d = np.abs(xxg - zig)
    boltline = np.exp(-(d ** 2) / 0.006)
    r = np.sqrt(((yy - 0.5) * 1.3) ** 2 + (xxg - 0.5) ** 2)
    glow_amt = np.clip(boltline * np.clip(1.0 - r * 1.1, 0, 1) + np.clip(1.0 - r * 3.0, 0, 1) * 0.6, 0, 1)
    em = np.clip(np.stack([0.85 * glow_amt, 0.95 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_chorus():
    """Spiritual: Espada Coro de los Ancestros, bronce campana + voces etericas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=711)
    ripple = np.power(0.5 + 0.5 * np.sin((yy * 22.0 + warp * 3.0) * np.pi), 2.6)
    patina = np.clip(fbm(H, W, [(6, 5, 1.0), (14, 11, 0.5)], seed=713) * 2.0 - 0.55, 0, 1)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_b1 = np.array([0.72, 0.55, 0.28]); c_b2 = np.array([0.48, 0.34, 0.16])
    c_verd = np.array([0.36, 0.62, 0.52])
    col = c_b2[None, None] * (1 - 0.4 * ripple[:, :, None]) + c_b1[None, None] * (0.4 * ripple[:, :, None])
    col = col * (1 - 0.5 * patina[:, :, None]) + c_verd[None, None] * (0.5 * patina[:, :, None])
    col = col + np.array([0.88, 0.80, 0.55])[None, None] * (0.18 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.40 + 0.10 * patina - 0.08 * edge, 0.24, 0.62),
        "metal": np.clip(0.68 - 0.25 * patina, 0, 0.75),
        "height": 0.28 * ripple + 0.18 * patina,
        "emis": np.clip(np.stack([0.10 * ripple, 0.35 * ripple, 0.28 * ripple], axis=2), 0, 0.38),
    })
    silk = fbm(H, W, [(9, 8, 1.0)], seed=715)
    c_s1 = np.array([0.55, 0.72, 0.66]); c_s2 = np.array([0.34, 0.50, 0.46])
    col2 = c_s2[None, None] * (0.85 + 0.30 * silk[:, :, None]) + c_s1[None, None] * (0.22 * silk[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.42 + 0.12 * silk, 0.26, 0.64),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.28 * silk,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=717)
    c_w1 = np.array([0.42, 0.52, 0.44]); c_w2 = np.array([0.24, 0.32, 0.26])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.12 * weave, 0.40, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    stone = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=719)
    col4 = c_b1[None, None] * (0.85 + 0.26 * stone[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.13 * stone, 0.20, 0.58),
        "metal": np.full((Hb, Wb), 0.72, dtype=np.float32),
        "height": 0.3 * stone,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: chorus ripples (concentric teal arcs with voice dots)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    arcs = np.power(np.abs(np.sin(r * 22.0)), 6.0) * np.clip(1.0 - r * 1.8, 0, 1)
    dots = np.clip((np.sin(xxg * 18.0) ** 6) * (np.sin(yy * 12.0) ** 6) * 3.0 - 1.4, 0, 1) * np.clip(1.0 - r * 1.4, 0, 1)
    glow_amt = np.clip(0.6 * arcs + 0.5 * dots, 0, 1)
    em = np.clip(np.stack([0.45 * glow_amt, 0.90 * glow_amt, 0.80 * glow_amt], axis=2), 0, 1)
    col5 = c_verd[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.12 * glow_amt, 0.16, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_monolith():
    """Arcane: Mandoble Monolito de Grimorio, basalto-libro indigo + 7 sellos."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=721)
    grain = fbm(H, W, [(13, 11, 1.0)], seed=723)
    goldline = np.power(0.5 + 0.5 * np.sin((yy * 14.0 + warp * 2.0) * np.pi), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.48, 0.52, 0.78]); c_mid = np.array([0.26, 0.28, 0.50]); c_lo = np.array([0.14, 0.15, 0.30])
    c_gold = np.array([0.90, 0.76, 0.42])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col + c_hi[None, None] * (0.20 * grain[:, :, None] + 0.22 * edge[:, :, None])
    col = col + c_gold[None, None] * (0.16 * goldline[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.52 + 0.08 * grain - 0.12 * edge, 0.34, 0.72),
        "metal": np.clip(0.12 * edge, 0, 0.20),
        "height": -0.24 * grain + 0.22 * goldline,
        "emis": np.clip(np.stack([0.50 * goldline, 0.35 * goldline, 0.15 * goldline], axis=2), 0, 0.5),
    })
    leather = fbm(H, W, [(8, 7, 1.0), (18, 15, 0.5)], seed=725)
    band = np.power(0.5 + 0.5 * np.sin((yy * 20.0 + leather * 2.5) * np.pi), 2.4)
    col2 = c_lo[None, None] * (0.85 + 0.35 * band[:, :, None]) + c_mid[None, None] * (0.18 * band[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.62 + 0.10 * band, 0.46, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.40 * band + 0.15 * leather,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=727)
    c_w1 = np.array([0.22, 0.20, 0.40]); c_w2 = np.array([0.12, 0.11, 0.24])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.12 * weave, 0.42, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=729)
    c_b = np.array([0.42, 0.38, 0.30])
    col4 = c_b[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.13 * hammer, 0.28, 0.64),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: seven seals (7 dots grid + faint ring)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    glow_amt = np.zeros((Hg, Wg), dtype=np.float32)
    for gy, gx in [(0.30, 0.20), (0.30, 0.40), (0.30, 0.60), (0.30, 0.80),
                   (0.68, 0.30), (0.68, 0.50), (0.68, 0.70)]:
        r = np.sqrt(((yy - gy) * 1.4) ** 2 + (xxg - gx) ** 2)
        glow_amt = np.maximum(glow_amt, np.clip(1.0 - r * 7.0, 0, 1) ** 1.2)
    em = np.clip(np.stack([0.90 * glow_amt, 0.60 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.6 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.36 - 0.14 * glow_amt, 0.20, 0.48),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.28 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_twilight():
    """Hybrid: Espada Hibrida del Pacto Crepuscular, hoja dividida luz/sombra (mitad L radiante, mitad R abisal)."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=731)
    fiber = 0.5 + 0.5 * np.sin((xx * 130.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    # split mask: soft L/R divide
    split = np.clip((xx - 0.5) * 6.0 + 0.5, 0, 1)
    c_light = np.array([0.96, 0.90, 0.70]); c_light2 = np.array([0.78, 0.74, 0.58])
    c_dark = np.array([0.16, 0.11, 0.26]); c_dark2 = np.array([0.08, 0.05, 0.14])
    c_violet = np.array([0.52, 0.32, 0.72])
    col_l = c_light2[None, None] * (1 - 0.3 * fiber[:, :, None]) + c_light[None, None] * (0.3 * fiber[:, :, None] + 0.24 * edge[:, :, None])
    col_d = c_dark2[None, None] * (1 - 0.3 * fiber[:, :, None]) + c_dark[None, None] * (0.3 * fiber[:, :, None]) + c_violet[None, None] * (0.16 * edge[:, :, None])
    col = col_l * (1 - split[:, :, None]) + col_d * split[:, :, None]
    col = col + warp[:, :, None] * 0.04
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 - 0.10 * edge + 0.16 * split, 0.16, 0.56),
        "metal": np.clip(0.66 - 0.34 * split, 0, 0.72),
        "height": 0.10 * fiber + 0.12 * edge,
        "emis": np.clip(np.stack([edge * (0.30 * (1 - split) + 0.10), edge * (0.24 * (1 - split) + 0.06), edge * (0.10 * (1 - split) + 0.22)], axis=2), 0, 0.45),
    })
    # TR flair: dusk damask (half gold half violet bands)
    damas = np.power(0.5 + 0.5 * np.sin((yy * 28.0 + xx * 7.0 + warp * 3.0) * np.pi), 2.0)
    ds = np.clip((xx - 0.5) * 6.0 + 0.5, 0, 1)
    g1 = np.array([0.85, 0.70, 0.36]); v1 = np.array([0.34, 0.22, 0.52])
    col2 = (g1[None, None] * (1 - ds[:, :, None]) + v1[None, None] * ds[:, :, None]) * (0.82 + 0.34 * damas[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.10 * damas, 0.18, 0.52),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.35 * damas,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=733)
    c_w1 = np.array([0.38, 0.30, 0.34]); c_w2 = np.array([0.20, 0.16, 0.20])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.54 - 0.12 * weave, 0.36, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=735)
    hs = np.clip((np.linspace(0, 1, 256)[None, :] - 0.5) * 6.0 + 0.5, 0, 1)
    c_s1 = np.array([0.70, 0.60, 0.38]); c_s2 = np.array([0.26, 0.20, 0.36])
    col4 = (c_s1[None, None] * (1 - hs[:, :, None]) + c_s2[None, None] * hs[:, :, None]) * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.13 * hammer, 0.20, 0.58),
        "metal": np.full((Hb, Wb), 0.72, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: eclipse (bright ring with dark centre + violet corona)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    ring = np.exp(-(((r - 0.16) ** 2) / 0.004))
    corona = np.clip(1.0 - r * 1.9, 0, 1) * 0.35
    glow_amt = np.clip(ring + corona, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.80 * glow_amt, 0.55 * glow_amt], axis=2), 0, 1)
    col5 = np.array([0.30, 0.22, 0.40])[None, None] * (0.6 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"covenant": paint_covenant, "bloodmoon": paint_bloodmoon, "thunderlord": paint_thunderlord,
            "chorus": paint_chorus, "monolith": paint_monolith, "twilight": paint_twilight}
OUT_DIRS = {
    "covenant": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/radiant_covenant",
    "bloodmoon": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/bloodmoon_pact",
    "thunderlord": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/thunderlord_fulgur",
    "chorus": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/ancestral_chorus",
    "monolith": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/grimoire_monolith",
    "twilight": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/twilight_covenant",
}
TEX_BASE = {"covenant": "radiant_covenant", "bloodmoon": "bloodmoon_pact", "thunderlord": "thunderlord_fulgur",
            "chorus": "ancestral_chorus", "monolith": "grimoire_monolith", "twilight": "twilight_covenant"}


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

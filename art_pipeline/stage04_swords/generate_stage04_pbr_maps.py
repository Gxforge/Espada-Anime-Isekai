# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 04: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [sunbark|thornheart|fulgurite|jadeanima|runebark|all]
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


def paint_sunbark():
    """Blessed: Mandoble del Voto Heliofilo, sunwood dorado + oro de amanecer."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: golden sunwood with blazing vertical grain and pale cream edge
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=471)
    grain = np.power(0.5 + 0.5 * np.sin((xx * 15.0 + warp * 5.0) * np.pi), 1.7)
    fiber = 0.5 + 0.5 * np.sin((xx * 135.0 + yy * 4.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.99, 0.91, 0.60]); c_mid = np.array([0.90, 0.66, 0.22]); c_lo = np.array([0.60, 0.38, 0.10])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col * (0.94 + 0.12 * fiber[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.42 - 0.10 * edge + 0.08 * grain, 0.28, 0.62),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.35 * grain + 0.15 * fiber,
        "emis": np.clip(np.stack([edge * (0.18 + 0.16 * grain), edge * 0.11, edge * 0.02], axis=2), 0, 0.4),
    })
    # TR flair: dawn gold leaf with soft damascene bands
    damas = np.power(0.5 + 0.5 * np.sin((yy * 30.0 + xx * 8.0 + warp * 3.5) * np.pi), 2.0)
    gold_grit = fbm(H, W, [(13, 11, 1.0)], seed=473)
    c_g1 = np.array([0.97, 0.84, 0.44]); c_g2 = np.array([0.68, 0.46, 0.15])
    col2 = c_g2[None, None] * (0.8 + 0.45 * damas[:, :, None]) * (0.94 + 0.10 * gold_grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * gold_grit - 0.08 * damas, 0.16, 0.48),
        "metal": np.full((H, W), 0.85, dtype=np.float32),
        "height": 0.35 * damas,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: sun-leather braid
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=475)
    c_w1 = np.array([0.46, 0.30, 0.12]); c_w2 = np.array([0.26, 0.15, 0.06])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.54 - 0.12 * weave, 0.34, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: gilded dawn bronze
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=477)
    col4 = c_g2[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.27 + 0.13 * hammer, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: rising-sun dawn disc (radial gold emission with rays)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.2) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.4, 0, 1) ** 1.6
    rays = np.power(0.5 + 0.5 * np.sin(np.arctan2(yy - 0.5, xxg - 0.5) * 12.0), 3.0) * np.clip(1.0 - r * 1.9, 0, 1)
    glow_amt = np.clip(hot + 0.5 * rays, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.82 * glow_amt, 0.28 * hot], axis=2), 0, 1)
    col5 = c_g1[None, None] * (0.7 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * hot, 0.15, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_thornheart():
    """Cursed: Hoja Maldita Corazon de Espina, metal hexagonal purpura + filo rosa sangrante."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: deep violet hex-plate with rose burning edge
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=481)
    hexpat = np.power(0.5 + 0.5 * np.sin((xx * 20.0 + warp * 2.5) * np.pi) * np.sin((yy * 17.0 - warp * 2.0) * np.pi), 1.6)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.52, 0.28, 0.72]); c_mid = np.array([0.30, 0.10, 0.46]); c_lo = np.array([0.15, 0.05, 0.26])
    c_rose = np.array([0.96, 0.25, 0.37])
    col = c_mid[None, None] * (1 - 0.45 * hexpat[:, :, None]) + c_lo[None, None] * (0.45 * hexpat[:, :, None])
    col = col + c_hi[None, None] * (0.18 * hexpat[:, :, None]) + c_rose[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.42 - 0.16 * edge + 0.08 * hexpat, 0.24, 0.62),
        "metal": np.clip(0.45 * edge + 0.15 * hexpat, 0, 0.55),
        "height": -0.30 * hexpat + 0.10 * edge,
        "emis": np.clip(np.stack([edge * (0.35 + 0.15 * hexpat), edge * 0.10, edge * 0.14], axis=2), 0, 0.55),
    })
    # TR flair: black-indigo thorn bark
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 34.0 + warp * 5.0) * np.pi), 2.0)
    c_b1 = np.array([0.09, 0.07, 0.20]); c_b2 = np.array([0.05, 0.03, 0.11])
    col2 = c_b2[None, None] * (0.8 + 0.5 * ridge[:, :, None]) + c_mid[None, None] * (0.10 * ridge[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.58 - 0.16 * ridge, 0.34, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * ridge,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: purple-black wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=483)
    c_w1 = np.array([0.16, 0.10, 0.26]); c_w2 = np.array([0.08, 0.05, 0.14])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.66 - 0.12 * weave, 0.48, 0.84),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave + 0.10 * grit,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: dark hex iron
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(12, 11, 1.0), (27, 24, 0.5)], seed=485)
    c_i = np.array([0.14, 0.12, 0.20])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.44 + 0.14 * hammer, 0.30, 0.70),
        "metal": np.full((Hb, Wb), 0.72, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: beating rose heart (two lobes radial)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r1 = np.sqrt((xxg - 0.38) ** 2 + ((yy - 0.42) * 1.15) ** 2)
    r2 = np.sqrt((xxg - 0.62) ** 2 + ((yy - 0.42) * 1.15) ** 2)
    hot = np.clip(1.0 - np.minimum(r1, r2) * 3.1, 0, 1) ** 1.4
    beat = 0.5 + 0.5 * np.sin(yy * 14.0)
    hot = np.clip(hot * (0.75 + 0.35 * beat), 0, 1)
    em = np.clip(np.stack([0.96 * hot, 0.22 * hot, 0.32 * hot], axis=2), 0, 1)
    col5 = c_rose[None, None] * (0.5 + 0.5 * hot[:, :, None]) * 0.5
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.12 * hot, 0.16, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.35 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_fulgurite():
    """Elemental: Espada Cresta de Fulgurita, vid de rayo cian + nucleo igneo-voltaico naranja."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: glassy lightning-fused sky-blue with pale hot edge
    warp = fbm(H, W, [(5, 3, 1.0), (13, 8, 0.5)], seed=491)
    streak = np.power(0.5 + 0.5 * np.sin((xx * 22.0 + warp * 6.0) * np.pi), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.88, 0.96, 0.99]); c_mid = np.array([0.30, 0.72, 0.95]); c_lo = np.array([0.12, 0.42, 0.68])
    col = c_mid[None, None] * (1 - 0.4 * streak[:, :, None]) + c_lo[None, None] * (0.4 * streak[:, :, None])
    col = col * (0.95 + 0.10 * warp[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None] + 0.10 * streak[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.24 - 0.08 * edge + 0.05 * streak, 0.14, 0.42),
        "metal": np.clip(0.10 + 0.15 * streak, 0, 0.3),
        "height": -0.25 * streak + 0.12 * edge,
        "emis": np.clip(np.stack([0.10 * streak, 0.35 * streak, 0.55 * streak], axis=2), 0, 0.6),
    })
    # TR flair: burnt copper-orange fused metal
    hammer = fbm(H, W, [(11, 10, 1.0), (25, 23, 0.5)], seed=493)
    c_f1 = np.array([0.72, 0.30, 0.08]); c_f2 = np.array([0.48, 0.16, 0.04])
    col2 = c_f2[None, None] * (0.85 + 0.30 * hammer[:, :, None]) + c_f1[None, None] * (0.20 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.36 + 0.14 * hammer, 0.24, 0.62),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: vitrified teal-dark wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=495)
    c_w1 = np.array([0.10, 0.22, 0.24]); c_w2 = np.array([0.05, 0.11, 0.13])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.48 - 0.12 * weave, 0.30, 0.66),
        "metal": np.clip(0.12 * weave, 0, 0.2),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: burnt copper
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=497)
    c_c = np.array([0.60, 0.30, 0.12])
    col4 = c_c[None, None] * (0.85 + 0.26 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.13 * hammer2, 0.22, 0.58),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: igneous-voltaic core (orange heat + cyan lightning branches)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 12, 1.0), (15, 25, 0.5)], seed=499)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.5, 0, 1) ** 1.5
    branch = np.power(0.5 + 0.5 * np.sin((yy * 30.0 + warp_g * 6.0) * np.pi), 6.0) * np.clip(1.0 - r * 1.6, 0, 1)
    em = np.clip(np.stack([1.0 * hot + 0.30 * branch, 0.55 * hot + 0.75 * branch, 0.20 * hot + 1.0 * branch], axis=2), 0, 1)
    col5 = c_f1[None, None] * (0.6 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * hot, 0.15, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.35 * hot + 0.25 * branch,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_jadeanima():
    """Spiritual: Katana Anima de Jade, acero palido con hamon de jade esmeralda."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: pale steel with wavy jade hamon temper line
    warp = fbm(H, W, [(4, 2, 1.0), (10, 6, 0.5)], seed=501)
    fiber = 0.5 + 0.5 * np.sin((xx * 150.0 + yy * 3.0) * np.pi)
    hamon_w = fbm(H, W, [(4, 2, 1.0)], seed=503)
    hamon = np.exp(-(((xx - 0.60 - 0.10 * hamon_w) ** 2) / 0.006))
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.92, 0.96, 0.94]); c_mid = np.array([0.70, 0.80, 0.76]); c_lo = np.array([0.45, 0.58, 0.52])
    c_jade = np.array([0.20, 0.85, 0.55])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col + c_hi[None, None] * (0.30 * edge[:, :, None]) + c_jade[None, None] * (0.30 * hamon[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.30 - 0.10 * edge - 0.06 * hamon, 0.16, 0.48),
        "metal": np.clip(0.60 + 0.15 * edge, 0, 0.8),
        "height": 0.10 * fiber + 0.20 * hamon,
        "emis": np.clip(np.stack([0.10 * hamon, 0.45 * hamon, 0.28 * hamon], axis=2), 0, 0.5),
    })
    # TR flair: teal patinated tsuba metal
    patina = fbm(H, W, [(9, 8, 1.0), (22, 19, 0.5)], seed=505)
    c_t1 = np.array([0.10, 0.45, 0.40]); c_t2 = np.array([0.05, 0.26, 0.24])
    col2 = c_t2[None, None] * (0.85 + 0.30 * patina[:, :, None]) + c_t1[None, None] * (0.22 * patina[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.32 + 0.12 * patina, 0.20, 0.56),
        "metal": np.full((H, W), 0.75, dtype=np.float32),
        "height": 0.28 * patina,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: dark teal silk diamond wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.8))
    grit = fbm(H, W, [(22, 22, 1.0)], seed=507)
    c_w1 = np.array([0.08, 0.20, 0.18]); c_w2 = np.array([0.04, 0.10, 0.09])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 + c_jade[None, None] * (0.08 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.14 * weave, 0.38, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: polished jade stone
    Hb, Wb = 512, 256
    stone = fbm(Hb, Wb, [(8, 8, 1.0), (19, 17, 0.5)], seed=509)
    c_s = np.array([0.22, 0.62, 0.48])
    col4 = c_s[None, None] * (0.85 + 0.26 * stone[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.20 + 0.10 * stone, 0.12, 0.40),
        "metal": np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.25 * stone,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: emerald anima swirl
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(7, 11, 1.0)], seed=511)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.3, 0, 1) ** 1.4
    swirl = np.power(0.5 + 0.5 * np.sin((yy * 22.0 + warp_g * 7.0) * np.pi), 2.5) * np.clip(1.0 - r * 1.7, 0, 1)
    glow_amt = np.clip(hot + 0.4 * swirl, 0, 1)
    em = np.clip(np.stack([0.25 * glow_amt, 0.95 * glow_amt, 0.62 * glow_amt], axis=2), 0, 1)
    col5 = c_s[None, None] * (0.7 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * hot, 0.14, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_runebark():
    """Arcane: Espada Codice de Corteza Runica, corteza indigo con glifos magenta vivos."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: indigo bark ridges with blocky magenta glyphs
    warp = fbm(H, W, [(4, 3, 1.0), (12, 7, 0.5)], seed=513)
    ridge = np.power(0.5 + 0.5 * np.sin((xx * 24.0 + warp * 5.0) * np.pi), 2.0)
    fiber = 0.5 + 0.5 * np.sin((xx * 120.0 + yy * 5.0) * np.pi)
    glyph = np.clip((np.sin(xx * 26.0) ** 4) * (np.sin(yy * 11.0 + 0.6) ** 4) * 3.2 - 0.85, 0, 1)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.55, 0.58, 0.88]); c_mid = np.array([0.30, 0.34, 0.62]); c_lo = np.array([0.16, 0.18, 0.38])
    c_mag = np.array([0.95, 0.55, 1.0])
    col = c_mid[None, None] * (1 - 0.5 * ridge[:, :, None]) + c_lo[None, None] * (0.5 * ridge[:, :, None])
    col = col * (0.94 + 0.10 * fiber[:, :, None]) + c_hi[None, None] * (0.20 * edge[:, :, None])
    col = col + c_mag[None, None] * (0.35 * glyph[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.48 - 0.12 * edge + 0.08 * ridge, 0.30, 0.66),
        "metal": np.clip(0.18 * edge, 0, 0.25),
        "height": -0.35 * ridge + 0.25 * glyph + 0.10 * fiber,
        "emis": np.clip(np.stack([0.85 * glyph, 0.50 * glyph, 0.95 * glyph], axis=2), 0, 0.85),
    })
    # TR flair: deep indigo leather with stitched bands
    band = np.power(0.5 + 0.5 * np.sin((yy * 26.0 + warp * 2.5) * np.pi), 3.0)
    stitch = 0.5 + 0.5 * np.sin((xx * 60.0 + yy * 6.0) * np.pi)
    c_l1 = np.array([0.15, 0.14, 0.38]); c_l2 = np.array([0.09, 0.08, 0.22])
    col2 = c_l2[None, None] * (0.85 + 0.35 * band[:, :, None]) + c_l1[None, None] * (0.18 * band[:, :, None] * stitch[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.55 - 0.12 * band, 0.38, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.40 * band + 0.15 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: indigo script wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=515)
    c_w1 = np.array([0.14, 0.13, 0.32]); c_w2 = np.array([0.07, 0.07, 0.18])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.60 - 0.12 * weave, 0.42, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: arcane dark bronze
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(11, 10, 1.0), (24, 22, 0.5)], seed=517)
    c_b = np.array([0.30, 0.26, 0.48])
    col4 = c_b[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.14 * hammer, 0.26, 0.62),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: living rune grid (magenta-violet blocks)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0)], seed=519)
    blocks = np.clip((np.sin(xxg * 24.0 + warp_g * 2.0) ** 4) * (np.sin(yy * 10.0) ** 4) * 3.4 - 0.8, 0, 1)
    pulses = 0.7 + 0.3 * np.sin(yy * 18.0 + warp_g * 4.0)
    glow_amt = np.clip(blocks * pulses, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.55 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_b[None, None] * (0.7 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.32 - 0.12 * glow_amt, 0.18, 0.46),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.30 * blocks,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"sunbark": paint_sunbark, "thornheart": paint_thornheart, "fulgurite": paint_fulgurite,
            "jadeanima": paint_jadeanima, "runebark": paint_runebark}
OUT_DIRS = {
    "sunbark": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/sunbark_vow",
    "thornheart": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/thornheart_hex",
    "fulgurite": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/fulgurite_crest",
    "jadeanima": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/jade_anima",
    "runebark": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/runebark_codex",
}
TEX_BASE = {"sunbark": "sunbark_vow", "thornheart": "thornheart_hex", "fulgurite": "fulgurite_crest",
            "jadeanima": "jade_anima", "runebark": "runebark_codex"}


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

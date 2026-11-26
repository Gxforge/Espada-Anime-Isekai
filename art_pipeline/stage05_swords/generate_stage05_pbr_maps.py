# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 05: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [solarinit|obsidianfang|coppertempest|silveranima|crystalcipher|all]
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


def paint_solarinit():
    """Blessed: Espada Iniciada del Sol Naciente, oro pulido espejo + bronce damasquinado."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: polished mirror gold with soft sheen bands
    warp = fbm(H, W, [(3, 2, 1.0), (8, 5, 0.5)], seed=521)
    sheen = 0.5 + 0.5 * np.sin((yy * 7.0 + warp * 2.0) * np.pi)
    fiber = 0.5 + 0.5 * np.sin((xx * 110.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.99, 0.95, 0.75]); c_mid = np.array([0.92, 0.78, 0.30]); c_lo = np.array([0.70, 0.52, 0.15])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.36 * edge[:, :, None] + 0.10 * sheen[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.26 - 0.08 * edge + 0.05 * sheen, 0.14, 0.44),
        "metal": np.full((H, W), 0.78, dtype=np.float32),
        "height": 0.12 * sheen - 0.10 * fiber,
        "emis": np.clip(np.stack([edge * 0.22, edge * 0.13, edge * 0.02], axis=2), 0, 0.3),
    })
    # TR flair: damascene rose-bronze
    damas = np.power(0.5 + 0.5 * np.sin((yy * 32.0 + xx * 7.0 + warp * 3.0) * np.pi), 2.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=523)
    c_g1 = np.array([0.80, 0.54, 0.24]); c_g2 = np.array([0.56, 0.34, 0.12])
    col2 = c_g2[None, None] * (0.8 + 0.45 * damas[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.28 + 0.10 * grit - 0.08 * damas, 0.16, 0.50),
        "metal": np.full((H, W), 0.86, dtype=np.float32),
        "height": 0.35 * damas,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: white-gold silk
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    grit2 = fbm(H, W, [(20, 20, 1.0)], seed=525)
    c_w1 = np.array([0.86, 0.80, 0.62]); c_w2 = np.array([0.52, 0.44, 0.28])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: bronze
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=527)
    col4 = c_g2[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.27 + 0.13 * hammer, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.86, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: radiant sun core with 8 hard rays
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.2) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.6, 0, 1) ** 1.4
    rays = np.power(np.abs(np.sin(np.arctan2(yy - 0.5, xxg - 0.5) * 4.0)), 6.0) * np.clip(1.0 - r * 1.8, 0, 1)
    glow_amt = np.clip(hot + 0.55 * rays, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.86 * glow_amt, 0.34 * hot], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * hot, 0.14, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_obsidianfang():
    """Cursed: Espada Colmillo de Obsidiana, vidrio volcanico negro + vena de sangre."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: black glass with sharp facets and rose burning edge
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=531)
    facet = np.power(np.sin(xx * 15.0 + warp * 2.0, ) ** 4, 1.2) * np.power(np.sin(yy * 9.0 - warp * 1.5) ** 4, 1.2)
    facet = np.clip(facet * 3.0 - 0.9, 0, 1)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.32, 0.24, 0.44]); c_mid = np.array([0.11, 0.08, 0.15]); c_lo = np.array([0.05, 0.03, 0.07])
    c_rose = np.array([0.95, 0.25, 0.35])
    col = c_mid[None, None] * (1 - 0.5 * facet[:, :, None]) + c_lo[None, None] * (0.5 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.30 * facet[:, :, None]) + c_rose[None, None] * (0.28 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.08 * edge + 0.05 * facet, 0.10, 0.38),
        "metal": np.clip(0.35 + 0.10 * facet, 0, 0.5),
        "height": -0.28 * facet + 0.12 * edge,
        "emis": np.clip(np.stack([edge * (0.38 + 0.12 * facet), edge * 0.09, edge * 0.12], axis=2), 0, 0.55),
    })
    # TR flair: volcanic shard bands
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 33.0 + warp * 5.0) * np.pi), 2.0)
    c_b1 = np.array([0.15, 0.11, 0.19]); c_b2 = np.array([0.08, 0.06, 0.11])
    col2 = c_b2[None, None] * (0.8 + 0.5 * ridge[:, :, None]) + c_hi[None, None] * (0.10 * ridge[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.52 - 0.14 * ridge, 0.30, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * ridge,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: black leather with rose stitch
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit2 = fbm(H, W, [(21, 21, 1.0)], seed=533)
    c_w1 = np.array([0.11, 0.09, 0.13]); c_w2 = np.array([0.05, 0.04, 0.06])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 + c_rose[None, None] * (0.06 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.14 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.64 - 0.12 * weave, 0.46, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave + 0.10 * grit2,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: void iron
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(12, 11, 1.0), (26, 24, 0.5)], seed=535)
    c_i = np.array([0.14, 0.12, 0.17])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.14 * hammer, 0.28, 0.68),
        "metal": np.full((Hb, Wb), 0.75, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: twin fang blood streaks
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 12, 1.0), (15, 25, 0.5)], seed=537)
    streak1 = np.exp(-(((xxg - 0.36 - 0.06 * warp_g) ** 2) / 0.008))
    streak2 = np.exp(-(((xxg - 0.64 - 0.06 * (1.0 - warp_g)) ** 2) / 0.008))
    hot = np.clip(streak1 + streak2, 0, 1) * np.clip(1.0 - yy * 0.4, 0.5, 1.0)
    pools = np.clip(warp_g * 2.2 - 0.95, 0, 1)
    glow_amt = np.clip(hot * 0.8 + pools * 0.5, 0, 1)
    em = np.clip(np.stack([0.98 * glow_amt, 0.20 * glow_amt, 0.28 * glow_amt], axis=2), 0, 1)
    col5 = c_rose[None, None] * (0.4 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.28 - 0.12 * glow_amt, 0.15, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.35 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_coppertempest():
    """Elemental: Espada Cobriza de Tempestad, cobre patinado verdin + remolino ciclonico."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: warm copper with verdigris patina patches and spiral streaks
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=541)
    spiral = np.power(0.5 + 0.5 * np.sin((xx * 11.0 + yy * 4.0 + warp * 4.5) * np.pi), 2.2)
    patina = np.clip(fbm(H, W, [(6, 5, 1.0), (14, 11, 0.5)], seed=543) * 2.0 - 0.55, 0, 1)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_cu1 = np.array([0.80, 0.44, 0.20]); c_cu2 = np.array([0.54, 0.26, 0.10])
    c_verd = np.array([0.28, 0.68, 0.54])
    col = c_cu2[None, None] * (1 - 0.45 * spiral[:, :, None]) + c_cu1[None, None] * (0.45 * spiral[:, :, None])
    col = col * (1 - 0.55 * patina[:, :, None]) + c_verd[None, None] * (0.55 * patina[:, :, None])
    col = col + np.array([0.90, 0.75, 0.50])[None, None] * (0.22 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 + 0.14 * patina - 0.08 * edge, 0.20, 0.62),
        "metal": np.clip(0.85 - 0.30 * patina, 0, 0.9),
        "height": -0.30 * spiral + 0.20 * patina,
        "emis": np.clip(np.stack([0.06 * spiral, 0.14 * spiral, 0.18 * spiral], axis=2), 0, 0.22),
    })
    # TR flair: heavy verdigris bronze
    hammer = fbm(H, W, [(9, 8, 1.0), (21, 19, 0.5)], seed=545)
    col2 = c_verd[None, None] * (0.75 + 0.35 * hammer[:, :, None]) + c_cu2[None, None] * (0.25 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.46 + 0.12 * hammer, 0.30, 0.70),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: storm-blue leather
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit2 = fbm(H, W, [(20, 20, 1.0)], seed=547)
    c_w1 = np.array([0.18, 0.26, 0.40]); c_w2 = np.array([0.09, 0.13, 0.22])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.56 - 0.12 * weave, 0.38, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: hammered copper
    Hb, Wb = 512, 256
    hammer2 = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=549)
    col4 = c_cu1[None, None] * (0.80 + 0.28 * hammer2[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.32 + 0.13 * hammer2, 0.20, 0.58),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: cyclonic electric spiral
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0), (14, 20, 0.5)], seed=551)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    theta = np.arctan2(yy - 0.5, xxg - 0.5)
    arms = np.power(0.5 + 0.5 * np.sin(theta * 3.0 + r * 14.0 - yy * 6.0 + warp_g * 4.0), 4.0)
    hot = np.clip(arms * np.clip(1.0 - r * 1.7, 0, 1) + np.clip(1.0 - r * 2.6, 0, 1) * 0.7, 0, 1)
    em = np.clip(np.stack([0.85 * hot, 0.97 * hot, 1.0 * hot], axis=2), 0, 1)
    col5 = c_cu1[None, None] * (0.6 + 0.4 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * hot, 0.14, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_silveranima():
    """Spiritual: Sable de Plata Anima, plata espejo + wisps fantasmales menta."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: mirror silver with mint ghost wisps
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=553)
    wisp = np.power(0.5 + 0.5 * np.sin((xx * 13.0 + yy * 3.0 + warp * 6.0) * np.pi), 3.0)
    fiber = 0.5 + 0.5 * np.sin((xx * 140.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.95, 0.97, 0.96]); c_mid = np.array([0.72, 0.78, 0.76]); c_lo = np.array([0.48, 0.55, 0.53])
    c_mint = np.array([0.55, 0.95, 0.80])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col + c_hi[None, None] * (0.32 * edge[:, :, None]) + c_mint[None, None] * (0.22 * wisp[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.16 - 0.06 * edge, 0.08, 0.30),
        "metal": np.full((H, W), 0.92, dtype=np.float32),
        "height": 0.10 * fiber + 0.15 * wisp,
        "emis": np.clip(np.stack([0.12 * wisp, 0.40 * wisp, 0.30 * wisp], axis=2), 0, 0.45),
    })
    # TR flair: pale teal-silver fittings
    patina = fbm(H, W, [(9, 8, 1.0), (22, 19, 0.5)], seed=555)
    c_t1 = np.array([0.52, 0.68, 0.62]); c_t2 = np.array([0.32, 0.46, 0.42])
    col2 = c_t2[None, None] * (0.85 + 0.30 * patina[:, :, None]) + c_t1[None, None] * (0.22 * patina[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.12 * patina, 0.18, 0.54),
        "metal": np.full((H, W), 0.82, dtype=np.float32),
        "height": 0.28 * patina,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: white silk
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.8))
    grit2 = fbm(H, W, [(22, 22, 1.0)], seed=557)
    c_w1 = np.array([0.80, 0.84, 0.82]); c_w2 = np.array([0.50, 0.56, 0.54])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.54 - 0.14 * weave, 0.36, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: silver
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=559)
    c_s = np.array([0.66, 0.71, 0.70])
    col4 = c_s[None, None] * (0.88 + 0.22 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.20 + 0.10 * hammer, 0.12, 0.40),
        "metal": np.full((Hb, Wb), 0.92, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: mint anima wisps (soft curls)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(7, 11, 1.0)], seed=561)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    core = np.clip(1.0 - r * 2.2, 0, 1) ** 1.3
    curl = np.power(0.5 + 0.5 * np.sin((yy * 20.0 + warp_g * 7.0) * np.pi), 2.2) * np.clip(1.0 - r * 1.6, 0, 1)
    glow_amt = np.clip(core + 0.45 * curl, 0, 1)
    em = np.clip(np.stack([0.55 * glow_amt, 1.0 * glow_amt, 0.82 * glow_amt], axis=2), 0, 1)
    col5 = c_s[None, None] * (0.7 + 0.4 * core[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * core, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * core,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_crystalcipher():
    """Arcane: Espada Cifrada de Cristal, prisma indigo facetado + matriz de cifrado magenta."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: faceted indigo crystal with hot facet flashes
    warp = fbm(H, W, [(4, 3, 1.0), (12, 7, 0.5)], seed=563)
    facet = np.power(np.sin(xx * 16.0 + warp * 2.5) ** 4 * np.sin(yy * 10.0) ** 4, 1.1)
    facet = np.clip(facet * 3.2 - 0.85, 0, 1)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    cipher = np.clip((np.sin(xx * 30.0 + 1.2) ** 4) * (np.sin(yy * 13.0) ** 4) * 3.4 - 0.9, 0, 1)
    c_hi = np.array([0.78, 0.84, 0.99]); c_mid = np.array([0.42, 0.48, 0.86]); c_lo = np.array([0.22, 0.25, 0.55])
    c_mag = np.array([0.95, 0.50, 1.0])
    col = c_mid[None, None] * (1 - 0.5 * facet[:, :, None]) + c_lo[None, None] * (0.5 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.28 * facet[:, :, None] + 0.25 * edge[:, :, None])
    col = col + c_mag[None, None] * (0.30 * cipher[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.14 + 0.04 * facet, 0.08, 0.28),
        "metal": np.clip(0.05 + 0.05 * facet, 0, 0.15),
        "height": -0.22 * facet + 0.25 * cipher,
        "emis": np.clip(np.stack([0.80 * cipher, 0.45 * cipher, 0.95 * cipher], axis=2), 0, 0.8),
    })
    # TR flair: dark crystal shards
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 30.0 + warp * 4.5) * np.pi), 2.0)
    c_d1 = np.array([0.24, 0.20, 0.46]); c_d2 = np.array([0.14, 0.12, 0.30])
    col2 = c_d2[None, None] * (0.8 + 0.5 * ridge[:, :, None]) + c_hi[None, None] * (0.10 * ridge[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.34 - 0.10 * ridge, 0.18, 0.52),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.42 * ridge,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: violet etched wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit2 = fbm(H, W, [(21, 21, 1.0)], seed=565)
    c_w1 = np.array([0.28, 0.22, 0.50]); c_w2 = np.array([0.15, 0.12, 0.30])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.56 - 0.12 * weave, 0.40, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: crystal bronze
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(11, 10, 1.0), (25, 23, 0.5)], seed=567)
    c_b = np.array([0.42, 0.34, 0.58])
    col4 = c_b[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.13 * hammer, 0.22, 0.58),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: cipher matrix (grid of magenta/indigo glyph blocks)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0)], seed=569)
    blocks = np.clip((np.sin(xxg * 26.0 + warp_g * 2.5) ** 4) * (np.sin(yy * 11.0) ** 4) * 3.4 - 0.8, 0, 1)
    pulse = 0.7 + 0.3 * np.sin(yy * 16.0 + warp_g * 5.0)
    glow_amt = np.clip(blocks * pulse, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.55 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_b[None, None] * (0.7 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.28 - 0.12 * glow_amt, 0.15, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.30 * blocks,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"solarinit": paint_solarinit, "obsidianfang": paint_obsidianfang, "coppertempest": paint_coppertempest,
            "silveranima": paint_silveranima, "crystalcipher": paint_crystalcipher}
OUT_DIRS = {
    "solarinit": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/solar_initiate",
    "obsidianfang": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/obsidian_fang",
    "coppertempest": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/copper_tempest",
    "silveranima": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/silver_anima",
    "crystalcipher": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/crystal_cipher",
}
TEX_BASE = {"solarinit": "solar_initiate", "obsidianfang": "obsidian_fang", "coppertempest": "copper_tempest",
            "silveranima": "silver_anima", "crystalcipher": "crystal_cipher"}


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

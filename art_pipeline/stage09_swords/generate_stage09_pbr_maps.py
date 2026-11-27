# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 09: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [dawnbreaker|guillotine|monsoon|nodachi|prism|all]
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


# =============================================================================
# Etapa 09 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


def paint_dawnbreaker():
    """Blessed: Hoja Templaria Rompealbas, acero oro solar + amanecer grabado."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=741)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    rays = 0.5 + 0.5 * np.sin((xx * 14.0 + yy * 2.0 + warp * 2.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.94, 0.66]); c_mid = np.array([0.92, 0.78, 0.36]); c_lo = np.array([0.62, 0.46, 0.18])
    col = c_mid[None, None] * (1 - 0.45 * rays[:, :, None]) + c_lo[None, None] * (0.45 * rays[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.07 * edge + 0.04 * sheen, 0.13, 0.40),
        "metal": np.full((H, W), 0.78, dtype=np.float32),
        "height": 0.10 * sheen - 0.07 * rays,
        "emis": np.clip(np.stack([edge * 0.22, edge * 0.17, edge * 0.06], axis=2), 0, 0.3),
    })
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    sunray = np.power(np.abs(np.cos(ang * 9.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=743)
    c_br = np.array([0.72, 0.48, 0.20])
    col2 = c_br[None, None] * (0.78 + 0.30 * sunray[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * sunray, 0.16, 0.48),
        "metal": np.full((H, W), 0.84, dtype=np.float32),
        "height": 0.32 * sunray,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.36, 0.16, 0.13]); c_w2 = np.array([0.72, 0.62, 0.40])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=745)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: sol naciente (disco + rayos + horizonte)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    disc = np.clip(1.0 - r * 2.7, 0, 1)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    spokes = np.power(np.abs(np.cos(angg * 6.0)), 24.0) * np.clip(r * 1.3, 0, 1) * np.clip(1.7 - r * 1.5, 0, 1)
    horizon = np.exp(-(((yyg - 0.40) ** 2) / 0.005)) * np.clip(1.0 - np.abs(xxg - 0.5) * 2.3, 0, 1)
    glow_amt = np.clip(0.62 * disc + 0.42 * spokes + 0.40 * horizon, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.86 * glow_amt, 0.42 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_guillotine():
    """Cursed: Filo Guillotina del Abismo, acero purpura negro + filo rosa."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=751)
    veins = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 7.0, 0, 1), 3.0)
    edgeband = np.clip((xx - 0.80) * 6.0, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.96, 0.25, 0.37]); c_mid = np.array([0.34, 0.11, 0.50]); c_lo = np.array([0.11, 0.05, 0.16])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.55 + 0.45 * warp[:, :, None])
    col = col + c_hi[None, None] * (0.42 * edgeband[:, :, None]) + c_hi[None, None] * (0.22 * veins[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.30 - 0.12 * edgeband + 0.06 * warp, 0.16, 0.52),
        "metal": np.full((H, W), 0.66, dtype=np.float32),
        "height": 0.08 * warp + 0.20 * veins - 0.10 * edgeband,
        "emis": np.clip(np.stack([0.55 * edgeband + 0.30 * veins, 0.10 * edgeband + 0.05 * veins, 0.16 * edgeband + 0.09 * veins], axis=2), 0, 0.7),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=753)
    col2 = c_lo[None, None] * (1.15 + 0.5 * mott[:, :, None]) + c_mid[None, None] * (0.14 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.38 + 0.14 * mott, 0.24, 0.66),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.22 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    stitch = np.clip(1.0 - np.abs(((xx * 14.0 + yy * 10.0) % 1.0) - 0.5) * 5.0, 0, 1)
    col3 = np.array([0.10, 0.05, 0.14])[None, None] * (0.9 + 0.3 * warp[:, :, None]) + \
        np.array([0.62, 0.16, 0.26])[None, None] * (0.30 * stitch[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.10 * stitch, 0.40, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=755)
    col4 = c_lo[None, None] * (1.10 + 0.45 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.36 + 0.13 * hammer, 0.22, 0.62),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: anillo de apartura + sendero de descenso creciente
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    ring = np.power(np.abs(np.sin(r * 22.0 - 1.1)), 14.0) * np.clip(1.0 - r * 1.6, 0, 1)
    arcx = 0.5 + 0.16 * np.cos(yyg * 4.4 + 2.6)
    arc = np.exp(-(((xxg - arcx) ** 2) / 0.0022)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.4, 0, 1)
    glow_amt = np.clip(0.55 * ring + 0.50 * arc, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.20 * glow_amt, 0.30 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.10 * glow_amt, 0.16, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_monsoon():
    """Elemental: Sable Gemelo del Monzon, acero cielo con lluvia y viento."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=761)
    rain = np.power(0.5 + 0.5 * np.sin((xx * 90.0 + yy * 1.5 + warp * 2.0) * np.pi), 3.0)
    swirl = np.power(np.abs(np.sin((np.sqrt(((yy - 0.35) * 3.2) ** 2 + (xx - 0.35) ** 2) * 13.0 - 0.8) * np.pi)), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.88, 0.95, 1.00]); c_mid = np.array([0.22, 0.60, 0.85]); c_lo = np.array([0.08, 0.28, 0.48])
    col = c_mid[None, None] * (1 - 0.40 * swirl[:, :, None]) + c_lo[None, None] * (0.40 * swirl[:, :, None])
    col = col * (0.92 + 0.14 * warp[:, :, None]) + c_hi[None, None] * (0.32 * edge[:, :, None]) + \
        c_hi[None, None] * (0.18 * rain[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.08 * edge + 0.05 * rain, 0.12, 0.40),
        "metal": np.full((H, W), 0.74, dtype=np.float32),
        "height": 0.09 * rain - 0.08 * swirl,
        "emis": np.clip(np.stack([0.15 * edge + 0.10 * rain, 0.42 * edge + 0.28 * rain, 0.72 * edge + 0.48 * rain], axis=2), 0, 0.8),
    })
    grit = fbm(H, W, [(13, 11, 1.0)], seed=763)
    c_br = np.array([0.76, 0.36, 0.13])
    col2 = c_br[None, None] * (0.80 + 0.28 * grit[:, :, None])
    etch = np.power(0.5 + 0.5 * np.sin((yy * 40.0) * np.pi), 2.0)
    col2 = col2 * (0.92 + 0.12 * etch[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.10 * grit, 0.20, 0.55),
        "metal": np.full((H, W), 0.82, dtype=np.float32),
        "height": 0.24 * etch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.04, 0.38, 0.38]); c_w2 = np.array([0.65, 0.85, 0.85])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=765)
    col4 = c_br[None, None] * (0.82 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.13 * hammer, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: chubasco (arcos de vendaval) + rayo zigzag cian
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    arc1 = np.exp(-(((np.sqrt(((yyg - 0.35) * 2.4) ** 2 + (xxg - 0.35) ** 2) - 0.22)) ** 2 / 0.004))
    arc2 = np.exp(-(((np.sqrt(((yyg - 0.30) * 3.0) ** 2 + (xxg - 0.62) ** 2) - 0.16)) ** 2 / 0.003))
    bolt = np.exp(-(((xxg - (0.5 + 0.10 * np.sin(yyg * 21.0 + 0.4))) ** 2) / 0.0016))
    glow_amt = np.clip(0.34 * arc1 + 0.30 * arc2 + 0.75 * bolt, 0, 1)
    em = np.clip(np.stack([0.72 * glow_amt, 0.92 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.62 + 0.38 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_nodachi():
    """Spiritual: Nodachi Cortafantasmas, acero plata con wisps espectrales."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=771)
    wisp = 0.5 + 0.5 * np.sin((yy * 6.0 + warp * 3.2) * np.pi)
    wisp = np.power(wisp, 1.6)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 1.00, 1.00]); c_mid = np.array([0.78, 0.82, 0.86]); c_lo = np.array([0.48, 0.58, 0.60])
    col = c_mid[None, None] * (1 - 0.45 * wisp[:, :, None]) + c_lo[None, None] * (0.45 * wisp[:, :, None])
    col = col + np.array([0.10, 0.24, 0.20])[None, None] * (0.25 * wisp[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.07 * edge + 0.05 * wisp, 0.11, 0.38),
        "metal": np.full((H, W), 0.70, dtype=np.float32),
        "height": 0.10 * wisp,
        "emis": np.clip(np.stack([0.10 * wisp, 0.38 * wisp, 0.30 * wisp], axis=2), 0, 0.5),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_teal = np.array([0.06, 0.46, 0.43])
    col2 = c_teal[None, None] * (0.75 + 0.35 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.10 * glint, 0.20, 0.55),
        "metal": np.full((H, W), 0.60, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.88, 0.90, 0.88]); c_w2 = np.array([0.10, 0.44, 0.42])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=773)
    col4 = np.array([0.05, 0.20, 0.19])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.10 * lacq, 0.30, 0.62),
        "metal": np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: fuegos fatuos (blobs esmeralda suaves)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    blob = np.zeros((Hg, Wg), dtype=np.float32)
    for cx, cy, s in ((0.30, 0.30, 0.05), (0.62, 0.42, 0.04), (0.45, 0.66, 0.055), (0.72, 0.74, 0.035)):
        blob = blob + np.exp(-(((xxg - cx) ** 2) / (s * 0.35) + ((yyg - cy) ** 2) / s))
    glow_amt = np.clip(blob * 0.55, 0, 1)
    em = np.clip(np.stack([0.25 * glow_amt, 0.95 * glow_amt, 0.68 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.65 + 0.35 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_prism():
    """Arcane: Filo Prisma Tejehechizos, cristal indigo con refracciones rosa."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=781)
    facet = np.floor(xx * 6.0 + yy * 1.2) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 6.0 - yy * 2.0 + warp * 1.5) * np.pi)), 30.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.96, 0.82, 1.00]); c_mid = np.array([0.45, 0.48, 0.95]); c_lo = np.array([0.18, 0.18, 0.52])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.38 * glint[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.09 * glint - 0.05 * edge + 0.03 * facet, 0.10, 0.36),
        "metal": np.full((H, W), 0.42, dtype=np.float32),
        "height": 0.10 * facet - 0.14 * glint,
        "emis": np.clip(np.stack([0.52 * glint + 0.20 * edge, 0.22 * glint + 0.12 * edge, 0.72 * glint + 0.26 * edge], axis=2), 0, 0.85),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_pk = np.array([0.90, 0.55, 0.95])
    col2 = c_mid[None, None] * (0.70 + 0.40 * sparkle[:, :, None]) + c_pk[None, None] * (0.30 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * sparkle, 0.15, 0.44),
        "metal": np.full((H, W), 0.48, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.22, 0.20, 0.46]); c_w2 = np.array([0.55, 0.40, 0.72])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=783)
    c_deep = np.array([0.16, 0.15, 0.42])
    col4 = c_deep[None, None] * (0.85 + 0.32 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.11 * grain, 0.22, 0.58),
        "metal": np.full((Hb, Wb), 0.40, dtype=np.float32),
        "height": 0.22 * grain,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: reticula de runas + triangulo prisma fucsia
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    rows = np.power(1.0 - np.abs(np.sin(yyg * 5.0 * np.pi)), 40.0)
    cols_ = np.power(1.0 - np.abs(np.sin(xxg * 5.0 * np.pi)), 40.0)
    lattice = np.clip(0.5 * rows + 0.5 * cols_, 0, 1)
    dots = np.power(np.abs(np.sin(yyg * 15.0 * np.pi) * np.sin(xxg * 15.0 * np.pi)), 30.0)
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    tri = np.power(np.abs(np.cos(angg * 1.5)), 60.0) * np.clip(1.0 - np.abs(r - 0.30) * 9.0, 0, 1)
    glow_amt = np.clip(0.32 * lattice + 0.45 * dots + 0.62 * tri, 0, 1)
    em = np.clip(np.stack([0.92 * glow_amt, 0.45 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_deep[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * glow_amt, 0.14, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"dawnbreaker": paint_dawnbreaker, "guillotine": paint_guillotine, "monsoon": paint_monsoon,
            "nodachi": paint_nodachi, "prism": paint_prism}
OUT_DIRS = {
    "dawnbreaker": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/dawnbreaker_templar",
    "guillotine": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/abyssal_guillotine",
    "monsoon": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/twin_monsoon",
    "nodachi": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/phantom_nodachi",
    "prism": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/spellweaver_prism",
}
TEX_BASE = {"dawnbreaker": "dawnbreaker_templar", "guillotine": "abyssal_guillotine", "monsoon": "twin_monsoon",
            "nodachi": "phantom_nodachi", "prism": "spellweaver_prism"}


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

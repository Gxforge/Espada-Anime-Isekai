# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 10: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [halcyon|devourer|permafrost|chakram|chronoglass|all]
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
# Etapa 10 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


# =============================================================================
# Etapa 10 painters (seeds 841-889) - Era III Especializacion II
# =============================================================================


def paint_halcyon():
    """Blessed: Espada Ancha Egida Alcion, acero oro calma + ondas serenas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=841)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    wave = 0.5 + 0.5 * np.sin((yy * 8.0 + xx * 2.5 + warp * 2.2) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.95, 0.72]); c_mid = np.array([0.90, 0.77, 0.36]); c_lo = np.array([0.52, 0.42, 0.18])
    col = c_mid[None, None] * (1 - 0.42 * wave[:, :, None]) + c_lo[None, None] * (0.42 * wave[:, :, None])
    col = col + np.array([0.10, 0.28, 0.30])[None, None] * (0.12 * wave[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.07 * edge + 0.04 * sheen, 0.13, 0.40),
        "metal": np.full((H, W), 0.78, dtype=np.float32),
        "height": 0.10 * sheen - 0.06 * wave,
        "emis": np.clip(np.stack([edge * 0.22, edge * 0.18, edge * 0.07], axis=2), 0, 0.3),
    })
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    feathers = np.power(np.abs(np.cos(ang * 11.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=843)
    c_br = np.array([0.74, 0.54, 0.24])
    col2 = c_br[None, None] * (0.78 + 0.30 * feathers[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * feathers, 0.16, 0.48),
        "metal": np.full((H, W), 0.84, dtype=np.float32),
        "height": 0.32 * feathers,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.85, 0.86, 0.88]); c_w2 = np.array([0.24, 0.30, 0.34])
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
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=845)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: egida (semicirculo + plumones dorados)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    semi = np.clip(1.4 - yyg * 2.2, 0, 1)
    disc = np.clip(1.0 - r * 2.6, 0, 1)
    plumes = np.power(np.abs(np.cos(angg * 8.0)), 20.0) * semi
    glow_amt = np.clip(0.55 * disc * semi + 0.45 * plumes, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.86 * glow_amt, 0.45 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_devourer():
    """Cursed: Blandon Devorador de Almas, acero negro-brasa + grietas fuego."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=851)
    crack = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.0, 0, 1), 2.5)
    ember = np.array([0.95, 0.35, 0.08])
    edgeband = np.clip((xx - 0.80) * 6.0, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_lo = np.array([0.05, 0.04, 0.06]); c_mid = np.array([0.16, 0.10, 0.16])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.50 + 0.45 * warp[:, :, None])
    col = col + ember[None, None] * (0.42 * crack[:, :, None]) + ember[None, None] * (0.25 * edgeband[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 - 0.12 * crack + 0.06 * warp, 0.18, 0.58),
        "metal": np.full((H, W), 0.62, dtype=np.float32),
        "height": 0.08 * warp + 0.22 * crack,
        "emis": np.clip(np.stack([0.62 * crack + 0.30 * edgeband, 0.20 * crack + 0.09 * edgeband, 0.05 * crack], axis=2), 0, 0.8),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=853)
    col2 = c_lo[None, None] * (1.30 + 0.55 * mott[:, :, None]) + np.array([0.45, 0.18, 0.10])[None, None] * (0.16 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.40 + 0.14 * mott, 0.26, 0.68),
        "metal": np.full((H, W), 0.50, dtype=np.float32),
        "height": 0.22 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    stitch = np.clip(1.0 - np.abs(((xx * 14.0 + yy * 10.0) % 1.0) - 0.5) * 5.0, 0, 1)
    col3 = np.array([0.08, 0.06, 0.07])[None, None] * (0.9 + 0.3 * warp[:, :, None]) + \
        np.array([0.58, 0.14, 0.14])[None, None] * (0.30 * stitch[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.10 * stitch, 0.40, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=855)
    col4 = c_lo[None, None] * (1.15 + 0.5 * hammer[:, :, None]) + ember[None, None] * (0.10 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.13 * hammer, 0.24, 0.64),
        "metal": np.full((Hb, Wb), 0.60, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: pozo de animas (anillo + espiral ascendente naranja)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    ring = np.power(np.abs(np.sin(r * 20.0 - 1.0)), 14.0) * np.clip(1.0 - r * 1.7, 0, 1)
    spx = 0.5 + 0.14 * np.cos(yyg * 12.0 + 1.2)
    arc = np.exp(-(((xxg - spx) ** 2) / 0.002)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.5, 0, 1)
    glow_amt = np.clip(0.50 * ring + 0.50 * arc, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.40 * glow_amt, 0.12 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.32 - 0.10 * glow_amt, 0.18, 0.46),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_permafrost():
    """Elemental: Claymore Prisma de Permafrost, hielo facetado + espejos."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=861)
    facet = np.floor(xx * 5.0 + yy * 1.5) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 5.0 - yy * 2.0 + warp * 1.5) * np.pi)), 24.0)
    crack = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 9.0, 0, 1), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.90, 0.96, 1.00]); c_mid = np.array([0.55, 0.72, 0.88]); c_lo = np.array([0.25, 0.42, 0.60])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.40 * glint[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    col = col + c_hi[None, None] * (0.20 * crack[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.16 - 0.06 * glint - 0.04 * edge + 0.03 * facet, 0.10, 0.34),
        "metal": np.full((H, W), 0.35, dtype=np.float32),
        "height": 0.10 * facet - 0.12 * glint + 0.10 * crack,
        "emis": np.clip(np.stack([0.45 * glint + 0.20 * edge, 0.62 * glint + 0.26 * edge, 0.85 * glint + 0.30 * edge], axis=2), 0, 0.9),
    })
    glint2 = np.power(0.5 + 0.5 * np.sin((xx * 20.0 - yy * 7.0) * np.pi), 5.0)
    c_sl = np.array([0.80, 0.86, 0.92])
    col2 = c_sl[None, None] * (0.80 + 0.30 * glint2[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.18 + 0.08 * glint2, 0.12, 0.40),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.28 * glint2,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.16, 0.30, 0.44]); c_w2 = np.array([0.72, 0.84, 0.92])
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
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=863)
    col4 = np.array([0.10, 0.22, 0.30])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.10 * lacq, 0.30, 0.62),
        "metal": np.full((Hb, Wb), 0.15, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: espejo artico (reticula de rombos + destello radial)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    lattice = 0.5 * np.power(1.0 - np.abs(np.sin(xxg * 6.0 * np.pi)), 30.0) + \
        0.5 * np.power(1.0 - np.abs(np.sin(yyg * 6.0 * np.pi)), 30.0)
    burst = np.power(np.abs(np.cos(angg * 3.0)), 40.0) * np.clip(1.0 - r * 2.2, 0, 1)
    glow_amt = np.clip(0.45 * lattice + 0.60 * burst, 0, 1)
    em = np.clip(np.stack([0.80 * glow_amt, 0.92 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.20 - 0.10 * glow_amt, 0.10, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_chakram():
    """Spiritual: Espada-Alma de Jade y Chakram, jade marmolado + oro."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=871)
    marble = np.power(0.5 + 0.5 * np.sin((yy * 10.0 + warp * 4.0) * np.pi), 1.2)
    vein = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 6.0, 0, 1), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.92, 0.95, 0.92]); c_mid = np.array([0.62, 0.78, 0.68]); c_lo = np.array([0.30, 0.50, 0.42])
    col = c_mid[None, None] * (1 - 0.45 * marble[:, :, None]) + c_lo[None, None] * (0.45 * marble[:, :, None])
    col = col + np.array([0.06, 0.24, 0.14])[None, None] * (0.30 * vein[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.07 * edge + 0.05 * marble, 0.12, 0.38),
        "metal": np.full((H, W), 0.45, dtype=np.float32),
        "height": 0.10 * marble + 0.12 * vein,
        "emis": np.clip(np.stack([0.10 * vein, 0.30 * vein, 0.18 * vein], axis=2), 0, 0.4),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_jade = np.array([0.28, 0.62, 0.46]); c_gold = np.array([0.85, 0.68, 0.35])
    col2 = c_jade[None, None] * (0.85 + 0.30 * glint[:, :, None]) + c_gold[None, None] * (0.15 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.22 + 0.08 * glint, 0.14, 0.42),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.86, 0.90, 0.86]); c_w2 = np.array([0.20, 0.42, 0.34])
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
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=873)
    col4 = np.array([0.10, 0.26, 0.20])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.40 + 0.10 * lacq, 0.28, 0.60),
        "metal": np.full((Hb, Wb), 0.30, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: rueda del ki (anillo + 8 rayos esmeralda)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    ring = np.power(np.abs(np.sin(r * 14.0 - 0.5)), 12.0) * np.clip(1.0 - r * 1.8, 0, 1)
    spokes = np.power(np.abs(np.cos(angg * 4.0)), 40.0) * np.clip(r * 2.2, 0, 1) * np.clip(1.8 - r * 2.0, 0, 1)
    glow_amt = np.clip(0.55 * ring + 0.50 * spokes, 0, 1)
    em = np.clip(np.stack([0.45 * glow_amt, 0.95 * glow_amt, 0.65 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.65 + 0.35 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_chronoglass():
    """Arcane: Sable Paradoja de Cronocristal, violeta-ambar + remolinos de arena."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=881)
    facet = np.floor(xx * 6.0 + yy * 1.4) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 6.0 - yy * 2.0 + warp * 1.5) * np.pi)), 26.0)
    sw = np.power(0.5 + 0.5 * np.sin((yy * 5.0 + xx * 3.0 + warp * 3.0) * np.pi), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.98, 0.88, 0.68]); c_mid = np.array([0.48, 0.44, 0.90]); c_lo = np.array([0.20, 0.18, 0.52])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + np.array([0.35, 0.22, 0.06])[None, None] * (0.30 * sw[:, :, None])
    col = col + c_hi[None, None] * (0.36 * glint[:, :, None]) + c_hi[None, None] * (0.28 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.08 * glint - 0.05 * edge + 0.03 * facet, 0.10, 0.36),
        "metal": np.full((H, W), 0.40, dtype=np.float32),
        "height": 0.10 * facet - 0.13 * glint + 0.08 * sw,
        "emis": np.clip(np.stack([0.62 * glint + 0.30 * sw + 0.18 * edge, 0.42 * glint + 0.18 * sw + 0.10 * edge, 0.80 * glint + 0.16 * sw + 0.20 * edge], axis=2), 0, 0.9),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_amb = np.array([0.85, 0.62, 0.30])
    col2 = c_amb[None, None] * (0.80 + 0.35 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * sparkle, 0.15, 0.44),
        "metal": np.full((H, W), 0.45, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.16, 0.12, 0.34]); c_w2 = np.array([0.50, 0.38, 0.66])
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
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=883)
    marks = np.power(1.0 - np.abs(np.sin(yyb * 12.0 * np.pi)), 40.0)
    c_brz = np.array([0.55, 0.42, 0.22])
    col4 = c_brz[None, None] * (0.85 + 0.30 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.26 + 0.11 * grain, 0.16, 0.50),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.22 * grain + 0.20 * marks,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: engranaje temporal + espiral de arena
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    teeth = np.power(np.abs(np.cos(angg * 8.0)), 30.0) * np.clip(1.0 - np.abs(r - 0.32) * 7.0, 0, 1)
    ring2 = np.power(np.abs(np.sin(r * 18.0 - 0.8)), 14.0) * np.clip(1.5 - r * 2.2, 0, 1)
    hands = np.exp(-np.abs(xxg - 0.5) / 0.015) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.6, 0, 1) * 0.8
    glow_amt = np.clip(0.50 * teeth + 0.45 * ring2 + 0.50 * hands, 0, 1)
    em = np.clip(np.stack([0.90 * glow_amt, 0.62 * glow_amt, 0.30 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.12, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"halcyon": paint_halcyon, "devourer": paint_devourer, "permafrost": paint_permafrost,
            "chakram": paint_chakram, "chronoglass": paint_chronoglass}
OUT_DIRS = {
    "halcyon": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/halcyon_aegis",
    "devourer": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/soul_devourer",
    "permafrost": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/permafrost_prism",
    "chakram": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/jade_chakram",
    "chronoglass": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/chronoglass_paradox",
}
TEX_BASE = {"halcyon": "halcyon_aegis", "devourer": "soul_devourer", "permafrost": "permafrost_prism",
            "chakram": "jade_chakram", "chronoglass": "chronoglass_paradox"}


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

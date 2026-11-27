# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 13: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [empyrean|voidscar|aurora|worldtree|axiom|all]
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
# Etapa 13 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


# =============================================================================
# Etapa 13 painters (seeds 841-889) - Era III Especializacion II
# =============================================================================


# =============================================================================
# Etapa 13 painters (seeds 941-989) - Era III Especializacion III
# =============================================================================


# =============================================================================
# Etapa 13 painters (seeds 1041-1099) - Era III Afinidad V (+ hibrida secreta)
# =============================================================================


# =============================================================================
# Etapa 13 painters (seeds 1141-1189) - Era IV Afinidad VI (Trascendente)
# =============================================================================


def paint_empyrean():
    """Blessed: Hoja Trascendente del Halo Empireo, perla-oro con halos."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1141)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    arch = np.power(np.abs(np.sin((yy * 5.0) * np.pi)), 5.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.97, 0.82]); c_mid = np.array([0.91, 0.84, 0.56]); c_lo = np.array([0.58, 0.50, 0.26])
    col = c_mid[None, None] * (1 - 0.40 * arch[:, :, None]) + c_lo[None, None] * (0.40 * arch[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.07 * edge + 0.04 * sheen, 0.12, 0.38),
        "metal": np.full((H, W), 0.78, dtype=np.float32),
        "height": 0.10 * sheen - 0.06 * arch,
        "emis": np.clip(np.stack([edge * 0.24, edge * 0.21, edge * 0.10], axis=2), 0, 0.3),
    })
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    rays = np.power(np.abs(np.cos(ang * 10.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1143)
    c_br = np.array([0.90, 0.78, 0.40])
    col2 = c_br[None, None] * (0.78 + 0.30 * rays[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * rays, 0.16, 0.48),
        "metal": np.full((H, W), 0.86, dtype=np.float32),
        "height": 0.32 * rays,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.97, 0.95, 0.88]); c_w2 = np.array([0.55, 0.48, 0.30])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1145)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: halos concéntricos (3 anillos + corona)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    halo = np.power(np.abs(np.sin(r * 11.0 - 0.35)), 15.0) * np.clip(1.15 - r * 1.5, 0, 1)
    corona = np.power(np.abs(np.cos(angg * 7.0)), 22.0) * np.clip(r * 2.2, 0, 1) * np.clip(1.5 - r * 1.7, 0, 1)
    core = np.clip(1.0 - r * 2.8, 0, 1) * 0.5
    glow_amt = np.clip(0.55 * halo + 0.45 * corona + 0.35 * core, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.90 * glow_amt, 0.58 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_voidscar():
    """Cursed: Espada Trascendente Cicatriz del Vacio, negro-cicatriz magenta."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1151)
    scar = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.0, 0, 1), 2.2)
    cross = np.exp(-np.abs(yy - xx + 0.18) / 0.030) + np.exp(-np.abs(yy + xx - 1.18) / 0.030)
    cross = np.clip(cross, 0, 1)
    c_lo = np.array([0.05, 0.03, 0.07]); c_mid = np.array([0.14, 0.08, 0.20])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.50 + 0.45 * warp[:, :, None])
    col = col + np.array([0.85, 0.20, 0.42])[None, None] * (0.55 * scar[:, :, None])
    col = col + np.array([0.70, 0.14, 0.34])[None, None] * (0.30 * cross[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.30 - 0.12 * scar + 0.05 * warp, 0.15, 0.52),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.08 * warp + 0.24 * scar - 0.10 * cross,
        "emis": np.clip(np.stack([0.75 * scar + 0.40 * cross, 0.20 * scar + 0.10 * cross, 0.42 * scar + 0.24 * cross], axis=2), 0, 0.85),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=1153)
    col2 = c_lo[None, None] * (1.25 + 0.5 * mott[:, :, None]) + c_mid[None, None] * (0.20 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.40 + 0.14 * mott, 0.26, 0.68),
        "metal": np.full((H, W), 0.50, dtype=np.float32),
        "height": 0.24 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    stitch = np.clip(1.0 - np.abs(((xx * 14.0 + yy * 10.0) % 1.0) - 0.5) * 5.0, 0, 1)
    col3 = np.array([0.07, 0.05, 0.10])[None, None] * (0.9 + 0.3 * warp[:, :, None]) + \
        np.array([0.62, 0.16, 0.34])[None, None] * (0.30 * stitch[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.10 * stitch, 0.40, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1155)
    col4 = c_lo[None, None] * (1.15 + 0.5 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.13 * hammer, 0.24, 0.64),
        "metal": np.full((Hb, Wb), 0.56, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: cicatriz cosmica (grieta X + herida de vacio)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    scarx = np.exp(-np.abs(yyg - xxg + 0.15) / 0.024) + np.exp(-np.abs(yyg + xxg - 1.15) / 0.024)
    scarx = np.clip(scarx, 0, 1)
    r = np.sqrt(((yyg - 0.5) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    wound = np.clip(1.0 - r * 2.4, 0, 1)
    ring = np.power(np.abs(np.sin(r * 16.0 - 0.8)), 12.0) * np.clip(1.2 - r * 1.6, 0, 1)
    glow_amt = np.clip(0.75 * scarx + 0.45 * wound + 0.35 * ring, 0, 1)
    em = np.clip(np.stack([0.92 * glow_amt, 0.22 * glow_amt, 0.44 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.10 * glow_amt, 0.16, 0.44),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_aurora():
    """Elemental: Espada Trascendente de Aurora Polar, cortinas verde-rosa-cian."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1161)
    curtain = 0.5 + 0.5 * np.sin((yy * 7.0 + xx * 5.0 + warp * 3.0) * np.pi)
    curtain = np.power(curtain, 1.6)
    aurora_r = np.power(np.clip(1.0 - np.abs(warp - 0.35) * 5.0, 0, 1), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.90, 1.00, 0.94]); c_mid = np.array([0.20, 0.72, 0.60]); c_lo = np.array([0.06, 0.30, 0.34])
    col = c_mid[None, None] * (1 - 0.42 * curtain[:, :, None]) + c_lo[None, None] * (0.42 * curtain[:, :, None])
    col = col + np.array([0.85, 0.35, 0.62])[None, None] * (0.28 * aurora_r[:, :, None])
    col = col * (0.92 + 0.14 * warp[:, :, None]) + c_hi[None, None] * (0.32 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.08 * edge + 0.05 * curtain, 0.12, 0.40),
        "metal": np.full((H, W), 0.68, dtype=np.float32),
        "height": 0.09 * curtain + 0.08 * aurora_r,
        "emis": np.clip(np.stack([0.20 * curtain + 0.42 * aurora_r, 0.68 * curtain + 0.22 * aurora_r, 0.55 * curtain + 0.38 * aurora_r], axis=2), 0, 0.8),
    })
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1163)
    c_br = np.array([0.34, 0.42, 0.52])
    col2 = c_br[None, None] * (0.80 + 0.28 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.10 * grit, 0.20, 0.55),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.22 * grit,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.10, 0.34, 0.34]); c_w2 = np.array([0.68, 0.88, 0.84])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1165)
    col4 = c_br[None, None] * (0.82 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.13 * hammer, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.84, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: cortinas de aurora onduladas
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    c1 = np.exp(-(((yyg - (0.38 + 0.08 * np.sin(xxg * 7.0))) ** 2) / 0.008))
    c2 = np.exp(-(((yyg - (0.58 + 0.07 * np.sin(xxg * 5.0 + 1.0))) ** 2) / 0.007))
    c3 = np.exp(-(((yyg - (0.72 + 0.06 * np.sin(xxg * 6.0 + 2.0))) ** 2) / 0.006))
    glow_amt = np.clip(0.62 * c1 + 0.50 * c2 + 0.45 * c3, 0, 1)
    em = np.clip(np.stack([0.30 * glow_amt, 0.95 * glow_amt, 0.72 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.62 + 0.38 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_worldtree():
    """Spiritual: Rama Trascendente del Arbol Mundo, madera-luz + hojas esmeralda."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=1171)
    grain = 0.5 + 0.5 * np.sin((yy * 16.0 + warp * 2.5) * np.pi)
    grain = np.power(grain, 1.5)
    bark = fbm(H, W, [(10, 8, 1.0), (22, 18, 0.5)], seed=1173)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.94, 0.96, 0.90]); c_mid = np.array([0.70, 0.62, 0.48]); c_lo = np.array([0.42, 0.36, 0.26])
    col = c_mid[None, None] * (1 - 0.45 * grain[:, :, None]) + c_lo[None, None] * (0.45 * grain[:, :, None])
    col = col * (0.90 + 0.16 * bark[:, :, None])
    col = col + np.array([0.10, 0.26, 0.16])[None, None] * (0.22 * warp[:, :, None])
    col = col + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.24 - 0.07 * edge + 0.05 * grain, 0.14, 0.44),
        "metal": np.full((H, W), 0.24, dtype=np.float32),
        "height": 0.12 * grain + 0.10 * bark,
        "emis": np.clip(np.stack([0.08 * warp, 0.24 * warp, 0.14 * warp], axis=2), 0, 0.3),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_leaf = np.array([0.30, 0.68, 0.44]); c_gold = np.array([0.84, 0.72, 0.42])
    col2 = c_leaf[None, None] * (0.85 + 0.30 * glint[:, :, None]) + c_gold[None, None] * (0.15 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.22 + 0.08 * glint, 0.14, 0.42),
        "metal": np.full((H, W), 0.45, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.90, 0.88, 0.80]); c_w2 = np.array([0.30, 0.44, 0.30])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=1175)
    col4 = np.array([0.14, 0.30, 0.22])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.40 + 0.10 * lacq, 0.28, 0.60),
        "metal": np.full((Hb, Wb), 0.20, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: arbol mundo (espiral de copa + raices)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    canopy = np.power(np.abs(np.sin(angg * 2.0 + r * 8.0)), 4.0) * np.clip(1.25 - r * 2.0, 0, 1)
    roots = np.power(np.abs(np.cos(angg * 3.0)), 30.0) * np.clip(r * 2.0, 0, 1) * np.clip(1.3 - r * 1.6, 0, 1) * np.clip(yyg - 0.42, 0, 1) * 2.0
    glow_amt = np.clip(0.55 * canopy + 0.45 * roots, 0, 1)
    em = np.clip(np.stack([0.55 * glow_amt, 0.95 * glow_amt, 0.62 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.65 + 0.35 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * glow_amt, 0.14, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_axiom():
    """Arcane: Espada Trascendente del Axioma, cristal-ecuacion indigo."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1181)
    facet = np.floor(xx * 6.0 + yy * 1.4) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 6.0 - yy * 2.0 + warp * 1.5) * np.pi)), 26.0)
    glyph = np.power(np.abs(np.sin(xx * 9.0 * np.pi) * np.sin(yy * 18.0 * np.pi)), 14.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.94, 0.92, 1.00]); c_mid = np.array([0.38, 0.36, 0.78]); c_lo = np.array([0.14, 0.13, 0.40])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.36 * glint[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    col = col + np.array([0.80, 0.85, 1.00])[None, None] * (0.22 * glyph[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.08 * glint - 0.05 * edge + 0.03 * facet, 0.10, 0.36),
        "metal": np.full((H, W), 0.40, dtype=np.float32),
        "height": 0.10 * facet - 0.13 * glint + 0.10 * glyph,
        "emis": np.clip(np.stack([0.50 * glint + 0.30 * glyph + 0.20 * edge, 0.55 * glint + 0.32 * glyph + 0.18 * edge, 0.85 * glint + 0.42 * glyph + 0.26 * edge], axis=2), 0, 0.9),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_ax = np.array([0.48, 0.42, 0.82])
    col2 = c_ax[None, None] * (0.78 + 0.36 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * sparkle, 0.15, 0.44),
        "metal": np.full((H, W), 0.52, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.16, 0.14, 0.36]); c_w2 = np.array([0.50, 0.44, 0.74])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=1183)
    marks = np.power(1.0 - np.abs(np.sin(yyb_ := np.linspace(0, 1, 256)[:, None] * 12.0 * np.pi)), 40.0)
    c_bz = np.array([0.52, 0.48, 0.72])
    col4 = c_bz[None, None] * (0.85 + 0.30 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.30 + 0.11 * grain, 0.18, 0.54),
        "metal": np.full((Hb, Wb), 0.60, dtype=np.float32),
        "height": 0.22 * grain,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: axiom reescrito (ecuaciones + igualdad + infinito)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    rows = np.power(1.0 - np.abs(np.sin(yyg * 4.0 * np.pi)), 60.0)
    equals = np.power(1.0 - np.abs(np.sin(yyg * 8.0 * np.pi - 0.6)), 90.0) * np.clip(1.0 - np.abs(xxg - 0.5) * 1.4, 0, 1)
    inf = np.power(np.abs(np.cos(2 * np.pi * np.clip((yyg - 0.45) * 1.0, 0, 1))), 60.0) * 0.4
    lattice = np.clip(0.5 * rows + 0.5 * np.power(1.0 - np.abs(np.sin(xxg * 5.0 * np.pi)), 60.0), 0, 1)
    glow_amt = np.clip(0.35 * lattice + 0.60 * equals + 0.30 * inf, 0, 1)
    em = np.clip(np.stack([0.85 * glow_amt, 0.88 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.12, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"empyrean": paint_empyrean, "voidscar": paint_voidscar, "aurora": paint_aurora,
            "worldtree": paint_worldtree, "axiom": paint_axiom}
OUT_DIRS = {
    "empyrean": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/empyrean_halo",
    "voidscar": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/voidscar",
    "aurora": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/aurora_polar",
    "worldtree": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/worldtree",
    "axiom": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/axiom_sword",
}
TEX_BASE = {"empyrean": "empyrean_halo", "voidscar": "voidscar", "aurora": "aurora_polar",
            "worldtree": "worldtree", "axiom": "axiom_sword"}


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

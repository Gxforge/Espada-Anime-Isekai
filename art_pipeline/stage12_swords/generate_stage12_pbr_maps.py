# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 12: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [archangel|hellfire|maelstrom|nirvana|archmage|dragon|all]
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
# Etapa 12 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


# =============================================================================
# Etapa 12 painters (seeds 841-889) - Era III Especializacion II
# =============================================================================


# =============================================================================
# Etapa 12 painters (seeds 941-989) - Era III Especializacion III
# =============================================================================


# =============================================================================
# Etapa 12 painters (seeds 1041-1099) - Era III Afinidad V (+ hibrida secreta)
# =============================================================================


def paint_archangel():
    """Blessed: Claymore Veredicto de Arcangel, blanco-perla catedral + oro."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1041)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    arch = np.power(np.abs(np.sin((yy * 5.0) * np.pi)), 6.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.99, 0.97, 0.88]); c_mid = np.array([0.87, 0.85, 0.72]); c_lo = np.array([0.55, 0.52, 0.40])
    c_gold = np.array([0.92, 0.80, 0.42])
    col = c_mid[None, None] * (1 - 0.40 * arch[:, :, None]) + c_lo[None, None] * (0.40 * arch[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    col = col + c_gold[None, None] * (0.12 * arch[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.07 * edge + 0.04 * sheen, 0.12, 0.38),
        "metal": np.full((H, W), 0.74, dtype=np.float32),
        "height": 0.10 * sheen - 0.06 * arch,
        "emis": np.clip(np.stack([edge * 0.22, edge * 0.19, edge * 0.10], axis=2), 0, 0.3),
    })
    feather = np.power(np.abs(np.sin((xx * 6.0 + yy * 3.0) * np.pi)), 2.5)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1043)
    c_br = np.array([0.90, 0.76, 0.38])
    col2 = c_br[None, None] * (0.78 + 0.30 * feather[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * feather, 0.16, 0.48),
        "metal": np.full((H, W), 0.85, dtype=np.float32),
        "height": 0.32 * feather,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.96, 0.94, 0.86]); c_w2 = np.array([0.52, 0.46, 0.28])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1045)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.89, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: sello de veredicto (halo + haz descendente)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.35) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    halo = np.power(np.abs(np.sin(r * 13.0 - 0.5)), 13.0) * np.clip(1.15 - r * 1.6, 0, 1)
    beam = np.exp(-(((xxg - 0.5) ** 2) / 0.010)) * np.clip((yyg - 0.35) * 2.2, 0, 1) * np.clip(1.5 - yyg, 0, 1)
    glow_amt = np.clip(0.55 * halo + 0.45 * beam, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.92 * glow_amt, 0.62 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_hellfire():
    """Cursed: Hoja Verdugo de Fuego Infernal, obsidiana purpura + fisuras lava."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1051)
    fissure = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 9.0, 0, 1), 2.2)
    heat = np.power(0.5 + 0.5 * np.sin((yy * 7.0 + warp * 2.2) * np.pi), 2.6)
    ember = np.array([1.00, 0.45, 0.12])
    c_lo = np.array([0.07, 0.04, 0.10]); c_mid = np.array([0.18, 0.10, 0.22])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.50 + 0.45 * warp[:, :, None])
    col = col + ember[None, None] * (0.48 * fissure[:, :, None]) + ember[None, None] * (0.15 * heat[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.07 * heat + 0.04 * warp, 0.13, 0.38),
        "metal": np.full((H, W), 0.40, dtype=np.float32),
        "height": 0.08 * warp + 0.24 * fissure - 0.06 * heat,
        "emis": np.clip(np.stack([0.80 * fissure + 0.28 * heat, 0.32 * fissure + 0.10 * heat, 0.06 * fissure], axis=2), 0, 0.9),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=1053)
    col2 = c_lo[None, None] * (1.30 + 0.5 * mott[:, :, None]) + np.array([0.42, 0.16, 0.10])[None, None] * (0.15 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.44 + 0.14 * mott, 0.30, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.26 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    bone = np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6)
    col3 = np.array([0.86, 0.80, 0.70])[None, None] * (0.85 + 0.25 * bone[:, :, None]) * (0.9 + 0.2 * warp[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.56 - 0.10 * bone, 0.38, 0.76),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * bone,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1055)
    col4 = c_lo[None, None] * (1.18 + 0.5 * hammer[:, :, None]) + ember[None, None] * (0.10 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.40 + 0.12 * hammer, 0.26, 0.64),
        "metal": np.full((Hb, Wb), 0.30, dtype=np.float32),
        "height": 0.30 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: anillo de fuego + humo ascendente
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    ring = np.power(np.abs(np.sin(r * 18.0 - 0.9)), 13.0) * np.clip(1.0 - r * 1.7, 0, 1)
    smoke = np.exp(-(((xxg - (0.5 + 0.06 * np.sin(yyg * 8.0))) ** 2) / 0.008)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.6, 0, 1) * 0.7
    glow_amt = np.clip(0.60 * ring + 0.40 * smoke, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.42 * glow_amt, 0.10 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.10 * glow_amt, 0.14, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_maelstrom():
    """Elemental: Hoja Triada del Maelstrom, cian espuma + remolinos."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1061)
    swirl = np.power(np.abs(np.sin((np.sqrt(((yy - 0.4) * 3.0) ** 2 + (xx - 0.4) ** 2) * 12.0 - 0.9) * np.pi)), 2.2)
    spray = np.power(0.5 + 0.5 * np.sin((xx * 80.0 + yy * 2.0 + warp * 2.0) * np.pi), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.90, 0.98, 1.00]); c_mid = np.array([0.20, 0.62, 0.86]); c_lo = np.array([0.06, 0.26, 0.46])
    col = c_mid[None, None] * (1 - 0.40 * swirl[:, :, None]) + c_lo[None, None] * (0.40 * swirl[:, :, None])
    col = col * (0.92 + 0.14 * warp[:, :, None]) + c_hi[None, None] * (0.32 * edge[:, :, None]) + \
        c_hi[None, None] * (0.20 * spray[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.08 * edge + 0.05 * spray, 0.12, 0.40),
        "metal": np.full((H, W), 0.72, dtype=np.float32),
        "height": 0.09 * spray - 0.08 * swirl,
        "emis": np.clip(np.stack([0.14 * edge + 0.12 * spray, 0.44 * edge + 0.30 * spray, 0.74 * edge + 0.50 * spray], axis=2), 0, 0.8),
    })
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1063)
    c_br = np.array([0.60, 0.44, 0.30])
    col2 = c_br[None, None] * (0.80 + 0.28 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.30 + 0.10 * grit, 0.20, 0.55),
        "metal": np.full((H, W), 0.82, dtype=np.float32),
        "height": 0.22 * grit,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.10, 0.40, 0.42]); c_w2 = np.array([0.72, 0.90, 0.90])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1065)
    col4 = c_br[None, None] * (0.82 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.13 * hammer, 0.17, 0.52),
        "metal": np.full((Hb, Wb), 0.85, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: vortice triple (espiral + 3 brazos)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    spiral = np.power(np.abs(np.sin(angg * 1.5 + r * 9.0 - 1.2)), 4.0) * np.clip(1.3 - r * 2.0, 0, 1)
    arms = np.power(np.abs(np.cos(angg * 1.5)), 40.0) * np.clip(r * 2.6, 0, 1) * np.clip(1.5 - r * 1.8, 0, 1)
    glow_amt = np.clip(0.55 * spiral + 0.45 * arms, 0, 1)
    em = np.clip(np.stack([0.70 * glow_amt, 0.92 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.62 + 0.38 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_nirvana():
    """Spiritual: Katana Espejo del Nirvana, plata espejo + zen rosado."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=1071)
    mirror = np.power(0.5 + 0.5 * np.sin((yy * 6.0 + warp * 2.0) * np.pi), 1.4)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.98, 0.97]); c_mid = np.array([0.82, 0.84, 0.86]); c_lo = np.array([0.52, 0.56, 0.60])
    col = c_mid[None, None] * (1 - 0.45 * mirror[:, :, None]) + c_lo[None, None] * (0.45 * mirror[:, :, None])
    col = col + np.array([0.10, 0.06, 0.05])[None, None] * (0.18 * mirror[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.36 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.14 - 0.06 * edge + 0.04 * mirror, 0.08, 0.30),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.10 * mirror,
        "emis": np.clip(np.stack([0.12 * mirror, 0.09 * mirror, 0.10 * mirror], axis=2), 0, 0.3),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_z = np.array([0.88, 0.72, 0.72]); c_gd = np.array([0.85, 0.74, 0.48])
    col2 = c_z[None, None] * (0.85 + 0.30 * glint[:, :, None]) + c_gd[None, None] * (0.16 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.22 + 0.08 * glint, 0.14, 0.42),
        "metal": np.full((H, W), 0.60, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.92, 0.90, 0.90]); c_w2 = np.array([0.34, 0.30, 0.36])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=1073)
    col4 = np.array([0.20, 0.18, 0.22])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.10 * lacq, 0.26, 0.58),
        "metal": np.full((Hb, Wb), 0.20, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: enso (anillo zen abierto) + ondas de calma
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    gapmask = np.clip((angg + 2.6) / 1.0, 0, 1)
    enso = np.power(np.abs(np.sin(r * 12.0 - 0.55)), 16.0) * np.clip(1.0 - r * 1.7, 0, 1) * (0.35 + 0.65 * gapmask)
    ripple = np.power(np.abs(np.sin(r * 22.0 - 1.8)), 12.0) * np.clip(1.0 - r * 1.4, 0, 1) * 0.4
    glow_amt = np.clip(0.65 * enso + 0.30 * ripple, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.85 * glow_amt, 0.78 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.65 + 0.35 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.18 - 0.10 * glow_amt, 0.08, 0.34),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_archmage():
    """Arcane: Hoja Singularidad de Archimago, violeta espacio profundo."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1081)
    facet = np.floor(xx * 6.0 + yy * 1.3) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 6.0 - yy * 2.0 + warp * 1.5) * np.pi)), 26.0)
    neb = np.power(0.5 + 0.5 * np.sin((yy * 6.0 + warp * 3.0) * np.pi), 2.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.92, 0.86, 1.00]); c_mid = np.array([0.34, 0.28, 0.66]); c_lo = np.array([0.10, 0.08, 0.30])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + np.array([0.30, 0.12, 0.34])[None, None] * (0.25 * neb[:, :, None])
    col = col + c_hi[None, None] * (0.36 * glint[:, :, None]) + c_hi[None, None] * (0.28 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.08 * glint - 0.05 * edge + 0.03 * facet, 0.10, 0.36),
        "metal": np.full((H, W), 0.42, dtype=np.float32),
        "height": 0.10 * facet - 0.13 * glint + 0.08 * neb,
        "emis": np.clip(np.stack([0.55 * glint + 0.30 * neb + 0.18 * edge, 0.30 * glint + 0.14 * neb + 0.10 * edge, 0.80 * glint + 0.36 * neb + 0.22 * edge], axis=2), 0, 0.9),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_st = np.array([0.55, 0.35, 0.80])
    col2 = c_st[None, None] * (0.78 + 0.36 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * sparkle, 0.15, 0.44),
        "metal": np.full((H, W), 0.50, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.12, 0.10, 0.28]); c_w2 = np.array([0.44, 0.34, 0.62])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=1083)
    col4 = np.array([0.14, 0.12, 0.30])[None, None] * (0.85 + 0.32 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.32 + 0.11 * grain, 0.20, 0.56),
        "metal": np.full((Hb, Wb), 0.42, dtype=np.float32),
        "height": 0.22 * grain,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: singularidad (nucleo oscuro + anillo de acrecion)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    hole = np.clip(1.0 - r * 3.4, 0, 1)
    disk = np.power(np.abs(np.sin(angg * 1.5 + r * 14.0)), 5.0) * np.clip(np.abs(r - 0.22) * 6.0, 0, 1) * np.clip(1.2 - r * 1.8, 0, 1)
    ring = np.power(np.abs(np.sin(r * 16.0 - 1.0)), 12.0) * np.clip(1.3 - r * 1.9, 0, 1)
    glow_amt = np.clip(0.30 * hole + 0.55 * disk + 0.40 * ring, 0, 1)
    em = np.clip(np.stack([0.85 * glow_amt, 0.55 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.11, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_dragon():
    """Hybrid: Katana Secreta Dragon de Tormenta y Alma, blanco-azul escamas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=1091)
    scales = 0.5 + 0.5 * np.sin((xx * 11.0 + np.sin(yy * 14.0) * 1.5) * np.pi)
    scales = np.power(scales, 1.6)
    storm = np.power(np.abs(np.sin((yy * 9.0 + xx * 3.0 + warp * 2.5) * np.pi)), 2.2)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 1.00, 1.00]); c_mid = np.array([0.84, 0.90, 0.96]); c_lo = np.array([0.52, 0.64, 0.78])
    c_az = np.array([0.24, 0.52, 0.86])
    col = c_mid[None, None] * (1 - 0.42 * scales[:, :, None]) + c_lo[None, None] * (0.42 * scales[:, :, None])
    col = col + c_az[None, None] * (0.20 * storm[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.07 * edge + 0.05 * scales, 0.11, 0.36),
        "metal": np.full((H, W), 0.76, dtype=np.float32),
        "height": 0.12 * scales - 0.06 * storm,
        "emis": np.clip(np.stack([0.10 * storm, 0.26 * storm, 0.52 * storm], axis=2), 0, 0.55),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_horn = np.array([0.88, 0.82, 0.62]); c_dg = np.array([0.30, 0.58, 0.92])
    col2 = c_horn[None, None] * (0.82 + 0.30 * glint[:, :, None]) + c_dg[None, None] * (0.16 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * glint, 0.15, 0.44),
        "metal": np.full((H, W), 0.68, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.90, 0.94, 0.96]); c_w2 = np.array([0.16, 0.34, 0.56])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=1093)
    col4 = np.array([0.10, 0.20, 0.30])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.10 * lacq, 0.26, 0.58),
        "metal": np.full((Hb, Wb), 0.30, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: dragon de tormenta (espiral + rayos + ojo)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    coil = np.power(np.abs(np.sin(angg * 1.5 + r * 10.0)), 4.0) * np.clip(1.25 - r * 2.0, 0, 1)
    bolt = np.exp(-(((xxg - (0.5 + 0.08 * np.sin(yyg * 16.0))) ** 2) / 0.0014)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.5, 0, 1)
    eye = np.clip(1.0 - np.abs(r - 0.10) * 9.0, 0, 1) * 0.6
    glow_amt = np.clip(0.45 * coil + 0.55 * bolt + 0.45 * eye, 0, 1)
    em = np.clip(np.stack([0.90 * glow_amt, 0.94 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.62 + 0.38 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.20 - 0.10 * glow_amt, 0.10, 0.36),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"archangel": paint_archangel, "hellfire": paint_hellfire, "maelstrom": paint_maelstrom,
            "nirvana": paint_nirvana, "archmage": paint_archmage, "dragon": paint_dragon}
OUT_DIRS = {
    "archangel": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/archangel_verdict",
    "hellfire": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/hellfire_executioner",
    "maelstrom": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/maelstrom_triad",
    "nirvana": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/nirvana_mirror",
    "archmage": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/archmage_singularity",
    "dragon": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/stormspirit_dragon",
}
TEX_BASE = {"archangel": "archangel_verdict", "hellfire": "hellfire_executioner", "maelstrom": "maelstrom_triad",
            "nirvana": "nirvana_mirror", "archmage": "archmage_singularity", "dragon": "stormspirit_dragon"}


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

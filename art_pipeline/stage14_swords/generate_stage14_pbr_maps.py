# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 14: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [sunforge|leviathan|tectonic|astral|tesseract|all]
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
# Etapa 14 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


# =============================================================================
# Etapa 14 painters (seeds 841-889) - Era III Especializacion II
# =============================================================================


# =============================================================================
# Etapa 14 painters (seeds 941-989) - Era III Especializacion III
# =============================================================================


# =============================================================================
# Etapa 14 painters (seeds 1041-1099) - Era III Afinidad V (+ hibrida secreta)
# =============================================================================


# =============================================================================
# Etapa 14 painters (seeds 1141-1189) - Era IV Afinidad VI (Trascendente)
# =============================================================================


# =============================================================================
# Etapa 14 painters (seeds 1241-1289) - Era IV Afinidad VII
# =============================================================================


def paint_sunforge():
    """Blessed: Espada Forjasol Santificada, oro fundido con grietas de forja."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1241)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    seam = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.0, 0, 1), 2.5)
    heat = np.power(0.5 + 0.5 * np.sin((yy * 6.0 + warp * 2.0) * np.pi), 2.0)
    ember = np.array([1.00, 0.52, 0.14])
    c_hi = np.array([1.00, 0.90, 0.60]); c_mid = np.array([0.88, 0.72, 0.38]); c_lo = np.array([0.50, 0.36, 0.16])
    col = c_mid[None, None] * (1 - 0.40 * heat[:, :, None]) + c_lo[None, None] * (0.40 * heat[:, :, None])
    col = col + ember[None, None] * (0.50 * seam[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.24 - 0.10 * seam + 0.04 * sheen, 0.13, 0.42),
        "metal": np.full((H, W), 0.85, dtype=np.float32),
        "height": 0.10 * sheen + 0.20 * seam,
        "emis": np.clip(np.stack([0.80 * seam, 0.38 * seam, 0.08 * seam], axis=2), 0, 0.85),
    })
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    rays = np.power(np.abs(np.cos(ang * 10.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1243)
    c_br = np.array([0.42, 0.34, 0.30])
    col2 = c_br[None, None] * (0.78 + 0.30 * rays[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * rays, 0.16, 0.48),
        "metal": np.full((H, W), 0.78, dtype=np.float32),
        "height": 0.32 * rays,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.60, 0.30, 0.16]); c_w2 = np.array([0.85, 0.66, 0.36])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1245)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.88, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: crisol de forja (boca + llamas ascendentes)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.42) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    mouth = np.power(np.abs(np.sin(r * 14.0 - 0.6)), 13.0) * np.clip(1.2 - r * 1.6, 0, 1)
    flames = np.zeros((Hg, Wg), dtype=np.float32)
    for fx in (0.36, 0.50, 0.64):
        flames = flames + np.exp(-(((xxg - fx + 0.03 * np.sin(yyg * 9.0)) ** 2) / 0.004)) * np.clip(1.0 - yyg * 1.3, 0, 1) * 0.8
    glow_amt = np.clip(0.55 * mouth + 0.50 * flames, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.56 * glow_amt, 0.12 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.25 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_leviathan():
    """Cursed: Colmillo Aterrador de Leviatan, organico abisal con ventosas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=1251)
    ridges = np.power(0.5 + 0.5 * np.sin((yy * 18.0 + warp * 2.0) * np.pi), 1.8)
    vein = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 7.0, 0, 1), 2.5)
    c_hi = np.array([0.44, 0.20, 0.52]); c_mid = np.array([0.22, 0.10, 0.30]); c_lo = np.array([0.07, 0.04, 0.12])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.55 + 0.40 * warp[:, :, None])
    col = col + c_hi[None, None] * (0.40 * vein[:, :, None])
    col = col + np.array([0.16, 0.18, 0.22])[None, None] * (0.35 * ridges[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 - 0.10 * vein + 0.05 * warp, 0.20, 0.58),
        "metal": np.full((H, W), 0.40, dtype=np.float32),
        "height": 0.10 * warp + 0.18 * ridges + 0.22 * vein,
        "emis": np.clip(np.stack([0.55 * vein, 0.14 * vein, 0.34 * vein], axis=2), 0, 0.6),
    })
    suck = np.power(np.abs(np.sin(xx * 8.0 * np.pi) * np.sin(yy * 16.0 * np.pi)), 12.0)
    col2 = c_lo[None, None] * (1.15 + 0.4 * warp[:, :, None]) + np.array([0.50, 0.24, 0.44])[None, None] * (0.35 * suck[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.42 + 0.12 * warp, 0.28, 0.68),
        "metal": np.full((H, W), 0.35, dtype=np.float32),
        "height": 0.26 * suck,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.10, 0.22, 0.20]); c_w2 = np.array([0.28, 0.44, 0.36])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.9 + 0.3 * warp[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.10 * weave, 0.40, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1255)
    col4 = c_lo[None, None] * (1.20 + 0.5 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.40 + 0.13 * hammer, 0.26, 0.66),
        "metal": np.full((Hb, Wb), 0.38, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: presion de fosa (anillos concentricos + ojo abisal)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    pressure = np.power(np.abs(np.sin(r * 20.0 - 1.0)), 12.0) * np.clip(1.0 - r * 1.6, 0, 1)
    angg = np.arctan2(yyg - 0.45, xxg - 0.5)
    eye = np.clip(1.0 - r * 5.0, 0, 1) * np.power(np.abs(np.cos(angg * 1.5)), 2.0)
    glow_amt = np.clip(0.55 * pressure + 0.60 * eye, 0, 1)
    em = np.clip(np.stack([0.70 * glow_amt, 0.20 * glow_amt, 0.45 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.34 - 0.10 * glow_amt, 0.18, 0.46),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_tectonic():
    """Elemental: Quebrantamantos Tectonico, roca continental con fallas de lava."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(4, 3, 1.0), (10, 8, 0.55)], seed=1261)
    stone = np.power(0.5 + 0.5 * np.sin((yy * 9.0 + xx * 4.0 + warp * 3.0) * np.pi), 1.6)
    fault = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.5, 0, 1), 2.2)
    c_hi = np.array([0.58, 0.55, 0.50]); c_mid = np.array([0.36, 0.33, 0.30]); c_lo = np.array([0.16, 0.14, 0.13])
    lava = np.array([1.00, 0.44, 0.10])
    col = c_mid[None, None] * (1 - 0.42 * stone[:, :, None]) + c_lo[None, None] * (0.42 * stone[:, :, None])
    col = col + np.array([0.24, 0.34, 0.16])[None, None] * (0.10 * warp[:, :, None])
    col = col + lava[None, None] * (0.55 * fault[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.46 - 0.14 * fault + 0.06 * stone, 0.30, 0.70),
        "metal": np.full((H, W), 0.05, dtype=np.float32),
        "height": 0.14 * stone + 0.24 * fault,
        "emis": np.clip(np.stack([0.85 * fault, 0.30 * fault, 0.06 * fault], axis=2), 0, 0.9),
    })
    grit = fbm(H, W, [(14, 12, 1.0), (28, 26, 0.45)], seed=1263)
    col2 = c_lo[None, None] * (1.30 + 0.55 * grit[:, :, None]) + c_hi[None, None] * (0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.52 + 0.12 * grit, 0.36, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.30 * grit,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.20, 0.17, 0.15]); c_w2 = np.array([0.44, 0.40, 0.36])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.9 + 0.3 * warp[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.62 - 0.10 * weave, 0.44, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1265)
    col4 = c_mid[None, None] * (0.85 + 0.40 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.50 + 0.12 * hammer, 0.34, 0.72),
        "metal": np.full((Hb, Wb), 0.12, dtype=np.float32),
        "height": 0.30 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: falla continental (grieta zigzag + manto incandescente)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    faultline = np.exp(-(((xxg - (0.5 + 0.09 * np.sin(yyg * 11.0))) ** 2) / 0.003)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.5, 0, 1)
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    mantle = np.clip(1.0 - r * 2.6, 0, 1) * 0.45
    steps = np.power(1.0 - np.abs(np.sin(yyg * 6.0 * np.pi)), 50.0) * 0.35
    glow_amt = np.clip(0.70 * faultline + 0.35 * mantle + 0.30 * steps, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.46 * glow_amt, 0.10 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.40 - 0.12 * glow_amt, 0.22, 0.52),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_astral():
    """Spiritual: Espada Viento Astral, plata-cian con corrientes de viento."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=1271)
    streams = 0.5 + 0.5 * np.sin((yy * 9.0 + xx * 6.0 + warp * 3.0) * np.pi)
    streams = np.power(streams, 1.8)
    feather = np.power(np.abs(np.sin((yy * 12.0 + warp * 2.0) * np.pi)), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.98, 1.00, 1.00]); c_mid = np.array([0.80, 0.88, 0.92]); c_lo = np.array([0.48, 0.62, 0.70])
    col = c_mid[None, None] * (1 - 0.42 * streams[:, :, None]) + c_lo[None, None] * (0.42 * streams[:, :, None])
    col = col + np.array([0.16, 0.48, 0.56])[None, None] * (0.24 * feather[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.36 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.16 - 0.07 * edge + 0.05 * streams, 0.10, 0.34),
        "metal": np.full((H, W), 0.72, dtype=np.float32),
        "height": 0.09 * streams - 0.06 * feather,
        "emis": np.clip(np.stack([0.10 * streams + 0.08 * feather, 0.34 * streams + 0.26 * feather, 0.52 * streams + 0.40 * feather], axis=2), 0, 0.6),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_aero = np.array([0.36, 0.68, 0.78]); c_gd = np.array([0.84, 0.82, 0.66])
    col2 = c_aero[None, None] * (0.82 + 0.30 * glint[:, :, None]) + c_gd[None, None] * (0.16 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.22 + 0.08 * glint, 0.14, 0.42),
        "metal": np.full((H, W), 0.60, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.94, 0.96, 0.96]); c_w2 = np.array([0.30, 0.52, 0.58])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=1275)
    col4 = np.array([0.16, 0.28, 0.34])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.10 * lacq, 0.26, 0.58),
        "metal": np.full((Hb, Wb), 0.30, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: vuelo infinito (espiral ciclonica + estelas)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    cyclone = np.power(np.abs(np.sin(angg * 1.5 + r * 11.0)), 4.0) * np.clip(1.25 - r * 2.0, 0, 1)
    trails = np.exp(-(((xxg - (0.5 + 0.10 * np.sin(yyg * 13.0 + 1.0))) ** 2) / 0.003)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.5, 0, 1) * 0.7
    featherG = np.power(np.abs(np.cos(angg * 3.0)), 30.0) * np.clip(r * 2.4, 0, 1) * np.clip(1.4 - r * 1.8, 0, 1) * 0.6
    glow_amt = np.clip(0.55 * cyclone + 0.45 * trails + 0.40 * featherG, 0, 1)
    em = np.clip(np.stack([0.82 * glow_amt, 0.95 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.62 + 0.38 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.18 - 0.10 * glow_amt, 0.09, 0.34),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_tesseract():
    """Arcane: Filo Teseracto de Vacio Geometrico, reticula indigo-magenta 4D."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1281)
    facet = np.floor(xx * 6.0 + yy * 1.3) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 6.0 - yy * 2.0 + warp * 1.5) * np.pi)), 26.0)
    grid = 0.5 * np.power(1.0 - np.abs(np.sin(xx * 10.0 * np.pi)), 34.0) + \
        0.5 * np.power(1.0 - np.abs(np.sin(yy * 20.0 * np.pi)), 34.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.92, 0.84, 1.00]); c_mid = np.array([0.34, 0.30, 0.70]); c_lo = np.array([0.10, 0.08, 0.30])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.36 * glint[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    col = col + np.array([0.90, 0.40, 0.80])[None, None] * (0.20 * grid[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.08 * glint - 0.05 * edge + 0.03 * facet, 0.10, 0.36),
        "metal": np.full((H, W), 0.44, dtype=np.float32),
        "height": 0.10 * facet - 0.13 * glint + 0.12 * grid,
        "emis": np.clip(np.stack([0.50 * glint + 0.40 * grid + 0.18 * edge, 0.28 * glint + 0.18 * grid + 0.10 * edge, 0.78 * glint + 0.44 * grid + 0.24 * edge], axis=2), 0, 0.9),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_vt = np.array([0.42, 0.36, 0.80])
    col2 = c_vt[None, None] * (0.78 + 0.36 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * sparkle, 0.15, 0.44),
        "metal": np.full((H, W), 0.50, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.13, 0.11, 0.30]); c_w2 = np.array([0.44, 0.36, 0.66])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=1285)
    col4 = np.array([0.12, 0.10, 0.28])[None, None] * (0.85 + 0.32 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.32 + 0.11 * grain, 0.20, 0.56),
        "metal": np.full((Hb, Wb), 0.44, dtype=np.float32),
        "height": 0.22 * grain,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: teseracto (cuadrado exterior + interior + conectores)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    outer = 0.5 * np.power(1.0 - np.abs(np.sin(xxg * 5.0 * np.pi)), 80.0) + 0.5 * np.power(1.0 - np.abs(np.sin(yyg * 5.0 * np.pi)), 80.0)
    inner = 0.5 * np.power(1.0 - np.abs(np.sin(xxg * 10.0 * np.pi - 0.31)), 90.0) + 0.5 * np.power(1.0 - np.abs(np.sin(yyg * 10.0 * np.pi - 0.31)), 90.0)
    inner = inner * np.clip(1.0 - np.abs(yyg - 0.5) * 2.0, 0, 1) * np.clip(1.0 - np.abs(xxg - 0.5) * 1.6, 0, 1)
    connectors = np.exp(-np.abs((yyg - 0.5) * 2.0) / 0.05) * np.power(1.0 - np.abs(np.sin(xxg * 10.0 * np.pi)), 60.0) * 0.5
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    voidg = np.clip(1.0 - r * 2.4, 0, 1) * 0.30
    glow_amt = np.clip(0.40 * outer + 0.55 * inner + 0.35 * connectors + 0.30 * voidg, 0, 1)
    em = np.clip(np.stack([0.80 * glow_amt, 0.40 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.11, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"sunforge": paint_sunforge, "leviathan": paint_leviathan, "tectonic": paint_tectonic,
            "astral": paint_astral, "tesseract": paint_tesseract}
OUT_DIRS = {
    "sunforge": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/sunforge",
    "leviathan": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/leviathan_fang",
    "tectonic": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/tectonic_breaker",
    "astral": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/astral_wind",
    "tesseract": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/tesseract",
}
TEX_BASE = {"sunforge": "sunforge", "leviathan": "leviathan_fang", "tectonic": "tectonic_breaker",
            "astral": "astral_wind", "tesseract": "tesseract"}


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

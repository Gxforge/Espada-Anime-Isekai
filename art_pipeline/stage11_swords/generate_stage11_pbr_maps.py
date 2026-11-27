# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 11: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [solstice|malakor|pyroclasm|saint|starlight|all]
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
# Etapa 11 painters (seeds 741-789) - Era III Especializacion
# =============================================================================


# =============================================================================
# Etapa 11 painters (seeds 841-889) - Era III Especializacion II
# =============================================================================


# =============================================================================
# Etapa 11 painters (seeds 941-989) - Era III Especializacion III
# =============================================================================


def paint_solstice():
    """Blessed: Reliquia Solar del Solsticio, perla-oro + disco solar."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=941)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    etch = np.power(0.5 + 0.5 * np.sin((xx * 10.0 + yy * 1.5) * np.pi), 3.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.96, 0.78]); c_mid = np.array([0.90, 0.80, 0.46]); c_lo = np.array([0.55, 0.45, 0.20])
    col = c_mid[None, None] * (1 - 0.40 * etch[:, :, None]) + c_lo[None, None] * (0.40 * etch[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.30 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.07 * edge + 0.04 * sheen, 0.13, 0.40),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.10 * sheen - 0.07 * etch,
        "emis": np.clip(np.stack([edge * 0.24, edge * 0.20, edge * 0.08], axis=2), 0, 0.3),
    })
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    rays = np.power(np.abs(np.cos(ang * 12.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=943)
    c_br = np.array([0.78, 0.60, 0.26])
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
    c_w1 = np.array([0.94, 0.90, 0.76]); c_w2 = np.array([0.46, 0.38, 0.20])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=945)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.24 + 0.13 * hammer, 0.15, 0.50),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: disco solar (anillo + rayos) + halo de martir
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    disc = np.clip(1.0 - r * 2.6, 0, 1)
    spokes = np.power(np.abs(np.cos(angg * 9.0)), 20.0) * np.clip(r * 2.0, 0, 1) * np.clip(1.6 - r * 1.6, 0, 1)
    ring = np.power(np.abs(np.sin(r * 12.0 - 0.4)), 12.0) * np.clip(1.2 - r * 1.5, 0, 1)
    glow_amt = np.clip(0.50 * disc + 0.40 * spokes + 0.35 * ring, 0, 1)
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


def paint_malakor():
    """Cursed: Espina Usurpadora de Malakor, purpura negro con espinas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=951)
    thorn = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 7.0, 0, 1), 3.0)
    rib = 0.5 + 0.5 * np.sin((yy * 24.0) * np.pi)
    rib = np.power(rib, 2.0)
    edgeband = np.clip((xx - 0.80) * 6.0, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.62, 0.20, 0.30]); c_mid = np.array([0.24, 0.10, 0.34]); c_lo = np.array([0.09, 0.04, 0.14])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.55 + 0.40 * warp[:, :, None])
    col = col + c_hi[None, None] * (0.30 * thorn[:, :, None]) + np.array([0.20, 0.16, 0.20])[None, None] * (0.30 * rib[:, :, None])
    col = col + c_hi[None, None] * (0.30 * edgeband[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.32 - 0.10 * edgeband + 0.06 * warp, 0.18, 0.56),
        "metal": np.full((H, W), 0.64, dtype=np.float32),
        "height": 0.08 * warp + 0.24 * thorn + 0.10 * rib,
        "emis": np.clip(np.stack([0.40 * thorn + 0.22 * edgeband, 0.10 * thorn + 0.06 * edgeband, 0.14 * thorn + 0.10 * edgeband], axis=2), 0, 0.6),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=953)
    col2 = c_lo[None, None] * (1.15 + 0.5 * mott[:, :, None]) + c_mid[None, None] * (0.18 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.40 + 0.14 * mott, 0.26, 0.68),
        "metal": np.full((H, W), 0.54, dtype=np.float32),
        "height": 0.24 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    stitch = np.clip(1.0 - np.abs(((xx * 14.0 + yy * 10.0) % 1.0) - 0.5) * 5.0, 0, 1)
    col3 = np.array([0.09, 0.05, 0.12])[None, None] * (0.9 + 0.3 * warp[:, :, None]) + \
        np.array([0.58, 0.14, 0.22])[None, None] * (0.30 * stitch[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.58 - 0.10 * stitch, 0.40, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * stitch,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=955)
    col4 = c_lo[None, None] * (1.12 + 0.48 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.38 + 0.13 * hammer, 0.24, 0.64),
        "metal": np.full((Hb, Wb), 0.60, dtype=np.float32),
        "height": 0.28 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: corona usurpada invertida + anillo de espinas carmesi
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    angg = np.arctan2(yyg - 0.45, xxg - 0.5)
    crown = np.power(np.abs(np.sin(angg * 2.5)), 26.0) * np.clip(1.0 - np.abs(r - 0.34) * 6.5, 0, 1)
    thorns = np.power(np.abs(np.sin(r * 17.0 - 0.9)), 12.0) * np.clip(1.3 - r * 1.8, 0, 1)
    glow_amt = np.clip(0.55 * crown + 0.45 * thorns, 0, 1)
    em = np.clip(np.stack([0.85 * glow_amt, 0.14 * glow_amt, 0.24 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.32 - 0.10 * glow_amt, 0.18, 0.46),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_pyroclasm():
    """Elemental: Mandoble Corazon Piroclastico, obsidiana + venas de magma."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=961)
    crack = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.5, 0, 1), 2.4)
    glowmap = np.power(0.5 + 0.5 * np.sin((yy * 9.0 + warp * 2.5) * np.pi), 2.5)
    ember = np.array([1.00, 0.42, 0.10])
    c_lo = np.array([0.045, 0.04, 0.055]); c_mid = np.array([0.13, 0.11, 0.13])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.50 + 0.45 * warp[:, :, None])
    col = col + ember[None, None] * (0.45 * crack[:, :, None]) + ember[None, None] * (0.16 * glowmap[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.06 * glowmap + 0.04 * warp, 0.12, 0.34),
        "metal": np.full((H, W), 0.30, dtype=np.float32),
        "height": 0.08 * warp + 0.24 * crack - 0.06 * glowmap,
        "emis": np.clip(np.stack([0.75 * crack + 0.26 * glowmap, 0.28 * crack + 0.09 * glowmap, 0.06 * crack], axis=2), 0, 0.85),
    })
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=963)
    col2 = c_lo[None, None] * (1.35 + 0.55 * mott[:, :, None]) + np.array([0.40, 0.16, 0.08])[None, None] * (0.14 * mott[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.44 + 0.14 * mott, 0.30, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.26 * mott,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    col3 = np.array([0.10, 0.07, 0.06])[None, None] * (0.9 + 0.3 * weave[:, :, None]) + \
        np.array([0.55, 0.18, 0.10])[None, None] * (0.25 * weave[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.60 - 0.10 * weave, 0.42, 0.80),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=965)
    col4 = c_lo[None, None] * (1.20 + 0.5 * hammer[:, :, None]) + ember[None, None] * (0.08 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.12 * hammer, 0.28, 0.66),
        "metal": np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.30 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: corazon eruptivo (estallido radial + anillo de boca)
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    angg = np.arctan2(yyg - 0.5, xxg - 0.5)
    burst = np.power(np.abs(np.cos(angg * 6.0)), 14.0) * np.clip(1.35 - r * 2.0, 0, 1)
    vent = np.clip(1.0 - r * 3.0, 0, 1)
    ring = np.power(np.abs(np.sin(r * 15.0 - 0.7)), 12.0) * np.clip(1.3 - r * 1.7, 0, 1)
    glow_amt = np.clip(0.55 * burst + 0.45 * vent + 0.35 * ring, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.44 * glow_amt, 0.10 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_saint():
    """Spiritual: Filo del Santo Reencarnado, plata seda + lotus sereno."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 4, 0.6)], seed=971)
    halo = 0.5 + 0.5 * np.sin((yy * 5.5 + warp * 2.4) * np.pi)
    halo = np.power(halo, 1.5)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.44, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([1.00, 0.99, 0.95]); c_mid = np.array([0.80, 0.83, 0.84]); c_lo = np.array([0.50, 0.58, 0.60])
    col = c_mid[None, None] * (1 - 0.45 * halo[:, :, None]) + c_lo[None, None] * (0.45 * halo[:, :, None])
    col = col + np.array([0.08, 0.20, 0.16])[None, None] * (0.22 * halo[:, :, None])
    col = col * (0.92 + 0.12 * warp[:, :, None]) + c_hi[None, None] * (0.34 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 - 0.07 * edge + 0.05 * halo, 0.11, 0.38),
        "metal": np.full((H, W), 0.72, dtype=np.float32),
        "height": 0.10 * halo,
        "emis": np.clip(np.stack([0.10 * halo, 0.30 * halo, 0.24 * halo], axis=2), 0, 0.42),
    })
    glint = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 6.0) * np.pi), 4.0)
    c_jd = np.array([0.60, 0.72, 0.66]); c_gd = np.array([0.84, 0.72, 0.42])
    col2 = c_jd[None, None] * (0.85 + 0.30 * glint[:, :, None]) + c_gd[None, None] * (0.18 * glint[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.08 * glint, 0.15, 0.44),
        "metal": np.full((H, W), 0.55, dtype=np.float32),
        "height": 0.28 * glint,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.94, 0.94, 0.92]); c_w2 = np.array([0.42, 0.56, 0.52])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    lacq = fbm(Hb, Wb, [(9, 9, 1.0), (20, 18, 0.4)], seed=973)
    col4 = np.array([0.16, 0.26, 0.24])[None, None] * (0.85 + 0.35 * lacq[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.40 + 0.10 * lacq, 0.28, 0.60),
        "metal": np.full((Hb, Wb), 0.25, dtype=np.float32),
        "height": 0.18 * lacq,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: halo santo doble + petalos de loto palido
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r1 = np.sqrt(((yyg - 0.40) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    ring1 = np.power(np.abs(np.sin(r1 * 15.0 - 0.5)), 14.0) * np.clip(1.1 - r1 * 1.5, 0, 1)
    r2 = np.sqrt(((yyg - 0.62) * 1.0) ** 2 + ((xxg - 0.5) * 0.8) ** 2)
    ring2 = np.power(np.abs(np.sin(r2 * 18.0 - 1.0)), 14.0) * np.clip(1.0 - r2 * 1.8, 0, 1)
    angg = np.arctan2(yyg - 0.62, xxg - 0.5)
    petals = np.power(np.abs(np.cos(angg * 4.0)), 30.0) * np.clip(r2 * 2.2, 0, 1) * np.clip(1.5 - r2 * 1.9, 0, 1)
    glow_amt = np.clip(0.50 * ring1 + 0.45 * ring2 + 0.40 * petals, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.90 * glow_amt, 0.62 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.65 + 0.35 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.13, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_starlight():
    """Arcane: Claymore Glifo de Luz Estelar, indigo nocturno + constelaciones."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=981)
    facet = np.floor(xx * 5.0 + yy * 1.3) % 2.0
    facet = facet + np.zeros((H, W), dtype=np.float32)
    glint = np.power(np.abs(np.sin((xx * 5.0 - yy * 2.0 + warp * 1.5) * np.pi)), 24.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.88, 0.88, 1.00]); c_mid = np.array([0.30, 0.30, 0.62]); c_lo = np.array([0.10, 0.10, 0.30])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.45 + 0.42 * facet[:, :, None])
    col = col + c_hi[None, None] * (0.36 * glint[:, :, None]) + c_hi[None, None] * (0.28 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.20 - 0.08 * glint - 0.05 * edge + 0.03 * facet, 0.11, 0.36),
        "metal": np.full((H, W), 0.44, dtype=np.float32),
        "height": 0.10 * facet - 0.13 * glint,
        "emis": np.clip(np.stack([0.45 * glint + 0.20 * edge, 0.48 * glint + 0.20 * edge, 0.82 * glint + 0.28 * edge], axis=2), 0, 0.85),
    })
    sparkle = np.power(0.5 + 0.5 * np.sin((xx * 22.0 - yy * 8.0) * np.pi), 6.0)
    c_vt = np.array([0.50, 0.36, 0.78])
    col2 = c_vt[None, None] * (0.78 + 0.36 * sparkle[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.08 * sparkle, 0.16, 0.46),
        "metal": np.full((H, W), 0.50, dtype=np.float32),
        "height": 0.30 * sparkle,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    c_w1 = np.array([0.14, 0.12, 0.32]); c_w2 = np.array([0.48, 0.40, 0.72])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    Hb, Wb = 512, 256
    grain = fbm(Hb, Wb, [(11, 11, 1.0), (22, 20, 0.4)], seed=983)
    col4 = np.array([0.12, 0.11, 0.26])[None, None] * (0.85 + 0.32 * grain[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.34 + 0.11 * grain, 0.22, 0.58),
        "metal": np.full((Hb, Wb), 0.45, dtype=np.float32),
        "height": 0.22 * grain,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: constelacion (puntos + lineas) + estallido estelar
    Hg, Wg = 512, 256
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    dots = np.zeros((Hg, Wg), dtype=np.float32)
    for cx, cy, s in ((0.30, 0.36, 0.05), (0.50, 0.52, 0.045), (0.68, 0.38, 0.05), (0.44, 0.72, 0.04)):
        dots = dots + np.exp(-(((xxg - cx) ** 2) / (s * 0.30) + ((yyg - cy) ** 2) / s))
    lines = np.zeros((Hg, Wg), dtype=np.float32)
    for (x1, y1, x2, y2) in ((0.30, 0.36, 0.50, 0.52), (0.50, 0.52, 0.68, 0.38), (0.50, 0.52, 0.44, 0.72)):
        t_ = ((xxg - x1) * (x2 - x1) + (yyg - y1) * (y2 - y1)) / max(1e-6, (x2 - x1) ** 2 + (y2 - y1) ** 2)
        t_ = np.clip(t_, 0, 1)
        dx = xxg - (x1 + t_ * (x2 - x1)); dy = yyg - (y1 + t_ * (y2 - y1))
        lines = lines + np.exp(-(dx ** 2 + dy ** 2) / 0.0008)
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    burst = np.clip(1.0 - r * 2.8, 0, 1) * 0.5
    glow_amt = np.clip(0.60 * dots + 0.40 * lines + 0.30 * burst, 0, 1)
    em = np.clip(np.stack([0.88 * glow_amt, 0.90 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * glow_amt, 0.12, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"solstice": paint_solstice, "malakor": paint_malakor, "pyroclasm": paint_pyroclasm,
            "saint": paint_saint, "starlight": paint_starlight}
OUT_DIRS = {
    "solstice": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/solstice_relic",
    "malakor": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/malakor_thorn",
    "pyroclasm": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/pyroclasm_heart",
    "saint": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/saint_reincarnated",
    "starlight": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/starlight_glyph",
}
TEX_BASE = {"solstice": "solstice_relic", "malakor": "malakor_thorn", "pyroclasm": "pyroclasm_heart",
            "saint": "saint_reincarnated", "starlight": "starlight_glyph"}


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

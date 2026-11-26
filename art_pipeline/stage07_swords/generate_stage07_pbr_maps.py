# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 07: atlas PBR 1024x1024 x 5 mapas para las 5 espadas bespoke.
Regiones identicas al Pilot: blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage04_pbr_maps.py [seraph|chitin|magma|lotus|aether|all]
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


def paint_seraph():
    """Blessed: Espada Larga Ala de Serafin, acero radiante blanco-oro + plumas."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: radiant pearl steel with golden feather etch
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=623)
    feather = np.power(0.5 + 0.5 * np.sin((xx * 16.0 + yy * 2.0 + warp * 3.5) * np.pi), 2.2)
    fiber = 0.5 + 0.5 * np.sin((xx * 130.0 + yy * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.97, 0.96, 0.90]); c_mid = np.array([0.80, 0.80, 0.74]); c_lo = np.array([0.55, 0.55, 0.50])
    c_gold = np.array([0.92, 0.80, 0.42])
    col = c_mid[None, None] * (1 - 0.4 * fiber[:, :, None]) + c_lo[None, None] * (0.4 * fiber[:, :, None])
    col = col + c_hi[None, None] * (0.30 * edge[:, :, None]) + c_gold[None, None] * (0.20 * feather[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.08 * edge + 0.05 * feather, 0.13, 0.42),
        "metal": np.full((H, W), 0.70, dtype=np.float32),
        "height": 0.16 * feather + 0.10 * fiber,
        "emis": np.clip(np.stack([edge * (0.18 + 0.10 * feather), edge * 0.14, edge * 0.06], axis=2), 0, 0.34),
    })
    # TR flair: gold feather barbs
    barbs = np.power(0.5 + 0.5 * np.sin((yy * 26.0 + xx * 10.0 + warp * 3.0) * np.pi), 2.6)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=625)
    col2 = c_gold[None, None] * (0.82 + 0.30 * barbs[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.08 * barbs, 0.16, 0.48),
        "metal": np.full((H, W), 0.85, dtype=np.float32),
        "height": 0.38 * barbs,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: white silk with gold thread
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 25 + yy * 25) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 25 - yy * 25) * np.pi), 1.6))
    grit2 = fbm(H, W, [(20, 20, 1.0)], seed=627)
    c_w1 = np.array([0.88, 0.86, 0.78]); c_w2 = np.array([0.55, 0.52, 0.45])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 + c_gold[None, None] * (0.10 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.12 * grit2[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.50 - 0.12 * weave, 0.32, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: bright gold
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=629)
    col4 = c_gold[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.26 + 0.13 * hammer, 0.16, 0.50),
        "metal": np.full((Hb, Wb), 0.87, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: seraph radiance (white-gold radial with feather rays)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.4, 0, 1) ** 1.3
    rays = np.power(np.abs(np.sin(np.arctan2(yy - 0.5, xxg - 0.5) * 5.0)), 4.0) * np.clip(1.0 - r * 1.7, 0, 1)
    glow_amt = np.clip(hot + 0.5 * rays, 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.94 * glow_amt, 0.68 * hot], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * hot, 0.12, 0.38),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_chitin():
    """Cursed: Espada Quitina de Pesadilla, quitina negra iridiscente + veneno abisal."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: glossy black-violet chitin with shifting iridescence
    warp = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=635)
    seg = np.power(0.5 + 0.5 * np.sin((yy * 13.0 + warp * 2.0) * np.pi), 2.4)
    irid = 0.5 + 0.5 * np.sin((xx * 9.0 + yy * 4.0 + warp * 5.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.36, 0.28, 0.52]); c_mid = np.array([0.14, 0.10, 0.22]); c_lo = np.array([0.06, 0.04, 0.11])
    c_iri = np.array([0.28, 0.62, 0.52])
    col = c_mid[None, None] * (1 - 0.45 * seg[:, :, None]) + c_lo[None, None] * (0.45 * seg[:, :, None])
    col = col + c_hi[None, None] * (0.26 * seg[:, :, None]) + c_iri[None, None] * (0.16 * irid[:, :, None])
    col = col + np.array([0.52, 0.88, 0.44])[None, None] * (0.16 * edge[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.18 + 0.06 * seg - 0.06 * edge, 0.10, 0.36),
        "metal": np.clip(0.22 + 0.08 * seg, 0, 0.36),
        "height": -0.20 * seg + 0.12 * edge,
        "emis": np.clip(np.stack([0.20 * edge, 0.42 * edge, 0.18 * edge], axis=2), 0, 0.45),
    })
    # TR flair: dark plated chitin shell
    plate = np.power(0.5 + 0.5 * np.sin((yy * 17.0 + warp * 3.0) * np.pi), 2.0)
    col2 = c_lo[None, None] * (0.8 + 0.5 * plate[:, :, None]) + c_hi[None, None] * (0.10 * plate[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.40 - 0.12 * plate, 0.24, 0.58),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.42 * plate,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: black carapace rings
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=637)
    c_w1 = np.array([0.16, 0.12, 0.22]); c_w2 = np.array([0.08, 0.06, 0.12])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.62 - 0.12 * weave, 0.44, 0.80),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: abyssal dark iron
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(12, 11, 1.0), (26, 24, 0.5)], seed=639)
    c_i = np.array([0.13, 0.11, 0.18])
    col4 = c_i[None, None] * (0.85 + 0.28 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.14 * hammer, 0.28, 0.68),
        "metal": np.full((Hb, Wb), 0.72, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: venom sac (toxic green with violet mist)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0)], seed=641)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.3, 0, 1) ** 1.4
    mist = np.power(0.5 + 0.5 * np.sin((yy * 18.0 + warp_g * 6.0) * np.pi), 2.2) * np.clip(1.0 - r * 1.5, 0, 1)
    glow_amt = np.clip(hot + 0.4 * mist, 0, 1)
    em = np.clip(np.stack([0.55 * glow_amt, 1.0 * glow_amt, 0.30 * hot + 0.35 * mist], axis=2), 0, 1)
    col5 = c_iri[None, None] * (0.5 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.26 - 0.12 * hot, 0.14, 0.42),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_magma():
    """Elemental: Espada Ancha Vena de Magma, basalto negro con grietas de lava."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: dark basalt plates with burning magma cracks
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=647)
    crack = np.power(0.5 + 0.5 * np.sin((xx * 7.0 + warp * 6.5) * np.pi), 7.0)
    grain = fbm(H, W, [(14, 12, 1.0)], seed=649)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.34, 0.30, 0.30]); c_mid = np.array([0.16, 0.14, 0.14]); c_lo = np.array([0.08, 0.07, 0.07])
    col = c_mid[None, None] * (1 - 0.5 * grain[:, :, None]) + c_lo[None, None] * (0.5 * grain[:, :, None])
    col = col + c_hi[None, None] * (0.20 * grain[:, :, None] + 0.18 * edge[:, :, None])
    col = col + np.array([1.0, 0.45, 0.10])[None, None] * (0.55 * crack[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.62 + 0.10 * grain - 0.30 * crack, 0.24, 0.84),
        "metal": np.clip(0.10 * edge, 0, 0.15),
        "height": -0.30 * grain + 0.35 * crack,
        "emis": np.clip(np.stack([1.0 * crack, 0.42 * crack, 0.10 * crack], axis=2), 0, 0.9),
    })
    # TR flair: scorched black rock
    rock = fbm(H, W, [(9, 8, 1.0), (20, 18, 0.5)], seed=651)
    col2 = c_lo[None, None] * (0.85 + 0.35 * rock[:, :, None]) + c_hi[None, None] * (0.15 * rock[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.68 + 0.10 * rock, 0.52, 0.86),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.35 * rock,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: scorched leather
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=653)
    c_w1 = np.array([0.22, 0.14, 0.10]); c_w2 = np.array([0.11, 0.07, 0.05])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.60 - 0.12 * weave, 0.44, 0.78),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: dark stone
    Hb, Wb = 512, 256
    stone = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=655)
    col4 = c_mid[None, None] * (0.85 + 0.28 * stone[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.58 + 0.14 * stone, 0.42, 0.80),
        "metal": np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.3 * stone,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: magma pool (orange core with crust islands)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0), (14, 19, 0.5)], seed=657)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    hot = np.clip(1.0 - r * 2.2, 0, 1) ** 1.3
    crust = np.clip(warp_g * 2.0 - 0.75, 0, 1)
    glow_amt = np.clip(hot * (1.0 - 0.55 * crust), 0, 1)
    em = np.clip(np.stack([1.0 * glow_amt, 0.45 * glow_amt, 0.12 * glow_amt], axis=2), 0, 1)
    col5 = np.array([0.35, 0.16, 0.10])[None, None] * (0.6 + 0.6 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.42 - 0.24 * glow_amt, 0.16, 0.52),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.30 * glow_amt + 0.20 * crust,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_lotus():
    """Spiritual: Hoja Loto de Plenilunio, petalo rosa-loto con luna plateada."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: pale lotus petal with fine veins and pink tips
    warp = fbm(H, W, [(3, 2, 1.0), (8, 5, 0.5)], seed=659)
    vein = np.power(0.5 + 0.5 * np.sin((xx * 22.0 + warp * 2.5) * np.pi), 3.0)
    tip = np.clip(yy - 0.72, 0, 1) / 0.28
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.98, 0.95, 0.97]); c_mid = np.array([0.90, 0.84, 0.90]); c_lo = np.array([0.76, 0.66, 0.78])
    c_pink = np.array([0.95, 0.62, 0.85])
    col = c_mid[None, None] * (1 - 0.4 * vein[:, :, None]) + c_lo[None, None] * (0.4 * vein[:, :, None])
    col = col + c_hi[None, None] * (0.26 * edge[:, :, None]) + c_pink[None, None] * (0.20 * tip[:, :, None] * vein[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 + 0.08 * vein - 0.08 * edge, 0.20, 0.52),
        "metal": np.clip(0.06 * edge, 0, 0.10),
        "height": 0.14 * vein + 0.10 * edge,
        "emis": np.clip(np.stack([0.40 * tip * vein, 0.22 * tip * vein, 0.38 * tip * vein], axis=2), 0, 0.42),
    })
    # TR flair: moon-silver metal
    moon = fbm(H, W, [(9, 8, 1.0), (21, 19, 0.5)], seed=661)
    c_m1 = np.array([0.84, 0.86, 0.92]); c_m2 = np.array([0.60, 0.63, 0.72])
    col2 = c_m2[None, None] * (0.85 + 0.30 * moon[:, :, None]) + c_m1[None, None] * (0.22 * moon[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.12 * moon, 0.14, 0.48),
        "metal": np.full((H, W), 0.85, dtype=np.float32),
        "height": 0.28 * moon,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: lotus leaf wrap (pale green)
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 27 + yy * 27) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 27 - yy * 27) * np.pi), 1.6))
    grit = fbm(H, W, [(21, 21, 1.0)], seed=663)
    c_w1 = np.array([0.52, 0.66, 0.48]); c_w2 = np.array([0.30, 0.42, 0.28])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave, 0.36, 0.70),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: pearl
    Hb, Wb = 512, 256
    pearl = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=665)
    col4 = c_m1[None, None] * (0.86 + 0.24 * pearl[:, :, None])
    col4 = col4 + c_pink[None, None] * (0.08 * pearl[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.20 + 0.10 * pearl, 0.12, 0.40),
        "metal": np.full((Hb, Wb), 0.55, dtype=np.float32),
        "height": 0.25 * pearl,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: full moon over water (silver disc + pink dew)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    r = np.sqrt(((yy - 0.45) * 1.1) ** 2 + (xxg - 0.5) ** 2)
    disc = np.clip(1.0 - r * 2.7, 0, 1) ** 1.2
    ripple = np.power(0.5 + 0.5 * np.sin((yy * 20.0 + xxg * 8.0) * np.pi), 3.0) * np.clip(1.0 - r * 1.4, 0, 1)
    glow_amt = np.clip(disc + 0.30 * ripple, 0, 1)
    em = np.clip(np.stack([0.95 * glow_amt, 0.88 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.5 * disc[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.24 - 0.10 * disc, 0.14, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * disc,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_aether():
    """Arcane: Estoque Conducto de Eter, vidrio eterico con canales de mana."""
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: translucent aether glass with bright mana veins
    warp = fbm(H, W, [(4, 3, 1.0), (12, 7, 0.5)], seed=671)
    vein = np.power(0.5 + 0.5 * np.sin((xx * 10.0 + yy * 3.0 + warp * 5.5) * np.pi), 4.0)
    glass = 0.5 + 0.5 * np.sin((xx * 34.0 + warp * 3.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.40, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_hi = np.array([0.82, 0.96, 0.99]); c_mid = np.array([0.44, 0.74, 0.86]); c_lo = np.array([0.24, 0.46, 0.62])
    c_vio = np.array([0.62, 0.48, 0.95])
    col = c_mid[None, None] * (1 - 0.4 * glass[:, :, None]) + c_lo[None, None] * (0.4 * glass[:, :, None])
    col = col + c_hi[None, None] * (0.28 * edge[:, :, None]) + c_vio[None, None] * (0.14 * glass[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.12 + 0.05 * glass, 0.07, 0.26),
        "metal": np.clip(0.04 * edge, 0, 0.08),
        "height": -0.18 * glass + 0.12 * edge,
        "emis": np.clip(np.stack([0.30 * vein, 0.70 * vein, 0.95 * vein], axis=2), 0, 0.85),
    })
    # TR flair: violet aether vapor
    vapor = fbm(H, W, [(6, 5, 1.0), (14, 12, 0.5)], seed=673)
    vband = np.power(0.5 + 0.5 * np.sin((yy * 16.0 + vapor * 5.0) * np.pi), 2.2)
    col2 = c_vio[None, None] * (0.55 + 0.45 * vband[:, :, None]) + c_lo[None, None] * (0.35 * vband[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.34 - 0.10 * vband, 0.18, 0.52),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.30 * vband + 0.15 * vapor,
        "emis": np.clip(np.stack([0.25 * vband, 0.12 * vband, 0.45 * vband], axis=2), 0, 0.45),
    })
    # BL grip: dark etched wrap
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    grit = fbm(H, W, [(20, 20, 1.0)], seed=675)
    c_w1 = np.array([0.14, 0.20, 0.30]); c_w2 = np.array([0.07, 0.11, 0.17])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * grit[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.56 - 0.12 * weave, 0.40, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: pale bronze conduits
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=677)
    c_b = np.array([0.62, 0.56, 0.40])
    col4 = c_b[None, None] * (0.85 + 0.26 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.32 + 0.13 * hammer, 0.20, 0.56),
        "metal": np.full((Hb, Wb), 0.80, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: mana swirl (cyan-violet spiral)
    Hg, Wg = 512, 256
    xxg = np.linspace(0.0, 1.0, Wg)[None, :]
    warp_g = fbm(Hg, Wg, [(6, 10, 1.0)], seed=679)
    r = np.sqrt(((yy - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    theta = np.arctan2(yy - 0.5, xxg - 0.5)
    arms = np.power(0.5 + 0.5 * np.sin(theta * 2.0 + r * 12.0 + warp_g * 5.0), 3.5)
    core = np.clip(1.0 - r * 2.6, 0, 1)
    hot = np.clip(arms * np.clip(1.0 - r * 1.6, 0, 1) + 0.6 * core, 0, 1)
    em = np.clip(np.stack([0.45 * hot + 0.35 * core, 0.85 * hot, 1.0 * hot], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.6 + 0.5 * hot[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.20 - 0.10 * hot, 0.10, 0.36),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.3 * hot,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"seraph": paint_seraph, "chitin": paint_chitin, "magma": paint_magma,
            "lotus": paint_lotus, "aether": paint_aether}
OUT_DIRS = {
    "seraph": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/seraph_wing",
    "chitin": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/nightmare_chitin",
    "magma": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/magma_vein",
    "lotus": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/moonlit_lotus",
    "aether": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/aether_conduit",
}
TEX_BASE = {"seraph": "seraph_wing", "chitin": "nightmare_chitin", "magma": "magma_vein",
            "lotus": "moonlit_lotus", "aether": "aether_conduit"}


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

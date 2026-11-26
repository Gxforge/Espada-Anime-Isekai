# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 02: generador de atlas PBR 1024x1024 x 5 mapas por espada.
Regiones (idénticas al Pilot): blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 generate_stage02_pbr_maps.py [verdant|copper|ash|all]
"""
import sys
import numpy as np
from PIL import Image

N = 1024


def fbm(h, w, freqs, seed=42):
    rng = np.random.default_rng(seed)
    yy = np.linspace(0.0, 1.0, h, endpoint=False)[:, None]
    xx = np.linspace(0.0, 1.0, w, endpoint=False)[None, :]
    acc = np.zeros((h, w), dtype=np.float32)
    amp_sum = 0.0
    for fx, fy, amp in freqs:
        p1, p2, p3 = rng.uniform(0, 2 * np.pi, 3)
        wave = (
            np.sin(2 * np.pi * (xx * fx + yy * fy * 0.25) + p1)
            + 0.6 * np.cos(2 * np.pi * (xx * fx * 0.7 - yy * fy * 0.35) + p2)
            + 0.35 * np.sin(2 * np.pi * (xx * fx * 1.4 + yy * fy * 0.8) + p3)
        ) / 1.95
        acc += amp * wave
        amp_sum += amp
    return acc / max(1e-5, amp_sum)


def place(base, rough, metal, height, emis, region, arrays):
    """arrays: dict with base(H,W,3), rough(H,W), metal(H,W), height(H,W), emis(H,W,3)"""
    y0, y1, x0, x1 = region  # pixel coords
    base[y0:y1, x0:x1] = arrays["base"]
    rough[y0:y1, x0:x1] = arrays["rough"]
    metal[y0:y1, x0:x1] = arrays["metal"]
    height[y0:y1, x0:x1] = arrays["height"]
    emis[y0:y1, x0:x1] = arrays["emis"]


# pixel regions: TL blade, TR flair, BL grip, BM shell, BR glow
R_BLADE = (0, 512, 0, 512)
R_FLAIR = (0, 512, 512, 1024)
R_GRIP = (512, 1024, 0, 512)
R_SHELL = (512, 1024, 512, 768)
R_GLOW = (512, 1024, 768, 1024)


def normalize_height_to_normal(height):
    sobel_x = np.zeros_like(height); sobel_y = np.zeros_like(height)
    sobel_x[1:-1, 1:-1] = (height[1:-1, 2:] - height[1:-1, :-2]) * 2.0
    sobel_y[1:-1, 1:-1] = (height[2:, 1:-1] - height[:-2, 1:-1]) * 2.0
    n = np.dstack([-sobel_x, sobel_y, np.ones_like(height)])
    norm = np.linalg.norm(n, axis=2, keepdims=True)
    return np.clip((n / norm) * 0.5 + 0.5, 0.0, 1.0)


def new_atlas():
    base = np.zeros((N, N, 3), dtype=np.float32)
    rough = np.full((N, N), 0.62, dtype=np.float32)
    metal = np.zeros((N, N), dtype=np.float32)
    height = np.zeros((N, N), dtype=np.float32)
    emis = np.zeros((N, N, 3), dtype=np.float32)
    return base, rough, metal, height, emis


def paint_verdant():
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512

    # TL blade: living green heartwood, rings + sap sheen toward the edge
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    warp = fbm(H, W, [(3, 2, 1.0), (8, 5, 0.5), (16, 9, 0.25)], seed=101)
    rings = np.power(0.5 + 0.5 * np.sin((xx * 22.0 + warp * 5.0) * np.pi), 2.0)
    fibers = 0.5 + 0.5 * np.sin((xx * 110.0 + yy * 5.0 + warp * 7.0) * np.pi)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1)
    moss = np.clip(fbm(H, W, [(9, 7, 1.0), (23, 17, 0.5)], seed=103) * 1.5 - 0.45, 0, 1) * 0.5
    c_dark = np.array([0.10, 0.20, 0.11]); c_mid = np.array([0.19, 0.36, 0.16]); c_light = np.array([0.30, 0.52, 0.20]); c_moss = np.array([0.24, 0.42, 0.17])
    col = c_mid[None, None] * (1 - 0.5 * rings[:, :, None]) + c_dark[None, None] * (0.5 * rings[:, :, None])
    col = col * (0.92 + 0.16 * fibers[:, :, None])
    col = col + c_light[None, None] * (0.30 * edge[:, :, None])
    col = col * (1 - moss[:, :, None]) + c_moss[None, None] * moss[:, :, None]
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.50 - 0.14 * edge + 0.10 * rings + 0.06 * moss, 0.30, 0.75),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.4 * rings + 0.15 * fibers,
        "emis": np.clip(np.stack([edge * 0.05, edge * 0.12, edge * 0.03], axis=2), 0, 0.2),
    })

    # TR flair: gnarled dark bark + vivid leaf-green canopies
    bark_warp = fbm(H, W, [(5, 4, 1.0), (13, 8, 0.6), (29, 17, 0.35)], seed=107)
    fiss = np.power(0.5 + 0.5 * np.sin((xx * 34.0 + bark_warp * 6.0) * np.pi), 3.0)
    # leaves occupy vertical thirds (fan zones) — blend leaf green by smooth blobs
    blobs = fbm(H, W, [(4, 3, 1.0), (11, 8, 0.4)], seed=111)
    leaf_mask = np.clip(blobs * 2.2 - 0.55, 0, 1)
    veins = np.power(0.5 + 0.5 * np.sin((yy * 60.0 + xx * 8.0) * np.pi), 2.0) * leaf_mask
    c_bark_hi = np.array([0.13, 0.16, 0.09]); c_bark_lo = np.array([0.05, 0.07, 0.04])
    c_leaf = np.array([0.15, 0.44, 0.12]); c_leaf_hi = np.array([0.32, 0.62, 0.18])
    bark = c_bark_hi[None, None] * (1 - fiss[:, :, None]) + c_bark_lo[None, None] * fiss[:, :, None]
    leaf = c_leaf[None, None] * (1 - veins[:, :, None]) + c_leaf_hi[None, None] * veins[:, :, None]
    col2 = bark * (1 - leaf_mask[:, :, None]) + leaf * leaf_mask[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.72 + 0.16 * fiss - 0.25 * leaf_mask, 0.42, 0.92),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.7 * fiss + 0.4 * leaf_mask - 0.2 * veins,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # BL grip: moss-wrapped wood braid
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 26 + yy * 26) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 26 - yy * 26) * np.pi), 1.6))
    fuzz = fbm(H, W, [(20, 20, 1.0), (45, 41, 0.5)], seed=113)
    c_cord = np.array([0.20, 0.30, 0.12]); c_cord_hi = np.array([0.34, 0.46, 0.18]); c_wood = np.array([0.16, 0.24, 0.10])
    col3 = c_wood[None, None] + (c_cord_hi - c_wood)[None, None] * (0.3 + 0.7 * weave[:, :, None])
    col3 = col3 * (0.92 + 0.14 * fuzz[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.66 - 0.10 * weave + 0.08 * fuzz, 0.48, 0.85),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.5 * weave + 0.15 * fuzz,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # BM shell: verdigris bronze ferrules
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(9, 9, 1.0), (21, 21, 0.5)], seed=117)
    patina = np.clip(-hammer * 1.6 - 0.2, 0, 1) * 0.5
    c_br = np.array([0.55, 0.42, 0.22]); c_pat = np.array([0.21, 0.48, 0.40])
    col4 = c_br[None, None] * (0.88 + 0.20 * hammer[:, :, None])
    col4 = col4 * (1 - patina[:, :, None]) + c_pat[None, None] * patina[:, :, None]
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.42 + 0.22 * patina, 0.30, 0.72),
        "metal": np.clip(0.75 - 0.35 * patina, 0.2, 0.8),
        "height": 0.3 * hammer - 0.4 * patina,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })

    # BR glow: sap veins & bud core (spring-green emission)
    Hg, Wg = 512, 256
    glow_warp = fbm(Hg, Wg, [(6, 10, 1.0), (14, 20, 0.5)], seed=119)
    lines = np.power(0.5 + 0.5 * np.sin((yy * 40.0 + glow_warp * 5.0) * np.pi), 3.0)
    c_glow = np.array([0.55, 1.0, 0.35])
    em = c_glow[None, None] * (0.55 + 0.45 * lines[:, :, None])
    dark = np.array([0.03, 0.08, 0.04])
    col5 = dark[None, None] + c_glow[None, None] * (0.18 * lines[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.25 - 0.1 * lines, 0.12, 0.35),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.5 * lines,
        "emis": np.clip(em, 0, 1),
    })
    return base, rough, metal, height, emis


def paint_copper():
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512

    # TL blade: burnished copper hex plating + verdigris crevices
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    hexy = fbm(H, W, [(7, 4, 1.0), (17, 11, 0.5)], seed=201)
    plate = np.power(0.5 + 0.5 * np.sin((xx * 18.0 + yy * 9.0) * np.pi), 1.8)
    brushed = 0.5 + 0.5 * np.sin((xx * 150.0 + yy * 4.0) * np.pi)
    verd = np.clip(-hexy * 1.7 - 0.15, 0, 1) * 0.75
    c_cu_hi = np.array([0.97, 0.65, 0.45]); c_cu = np.array([0.85, 0.47, 0.26]); c_cu_lo = np.array([0.45, 0.20, 0.10]); c_verd = np.array([0.23, 0.63, 0.49])
    col = c_cu[None, None] * (1 - 0.45 * plate[:, :, None]) + c_cu_lo[None, None] * (0.45 * plate[:, :, None])
    col = col * (0.94 + 0.12 * brushed[:, :, None])
    col = col + c_cu_hi[None, None] * (0.25 * (1 - plate[:, :, None]))
    col = col * (1 - verd[:, :, None]) + c_verd[None, None] * verd[:, :, None]
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.34 + 0.30 * verd + 0.06 * plate, 0.22, 0.72),
        "metal": np.clip(0.92 - 0.55 * verd, 0.25, 0.95),
        "height": 0.4 * plate - 0.7 * verd,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # TR flair: antique copper horns with verdigris tips
    horn_warp = fbm(H, W, [(6, 5, 1.0), (15, 12, 0.5), (31, 24, 0.25)], seed=203)
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 26.0 + horn_warp * 4.0) * np.pi), 2.0)
    verd2 = np.clip(horn_warp * 1.6 - 0.35, 0, 1) * 0.55
    col2 = c_cu_lo[None, None] * (0.6 + 0.5 * ridge[:, :, None])
    col2 = col2 * (1 - verd2[:, :, None]) + c_verd[None, None] * verd2[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.38 + 0.26 * verd2 + 0.08 * ridge, 0.25, 0.75),
        "metal": np.clip(0.85 - 0.5 * verd2, 0.3, 0.9),
        "height": -0.5 * ridge + 0.3 * verd2,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # BL grip: copper coil wrap (strong braid, polished)
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 30 + yy * 30) * np.pi), 1.5),
                       np.power(0.5 + 0.5 * np.sin((xx * 30 - yy * 30) * np.pi), 1.5))
    wear = fbm(H, W, [(18, 18, 1.0)], seed=207)
    col3 = c_cu_lo[None, None] + (c_cu_hi - c_cu_lo)[None, None] * weave[:, :, None]
    col3 = col3 * (0.9 + 0.15 * wear[:, :, None])
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.30 - 0.10 * weave + 0.06 * wear, 0.18, 0.55),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.65 * weave,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # BM shell: polished copper (ribs/fins/ferrules/bulb shell)
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (23, 21, 0.5)], seed=209)
    col4 = c_cu[None, None] * (0.85 + 0.25 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.28 + 0.14 * hammer, 0.18, 0.55),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })

    # BR glow: petrified root core + voltaic seams (electric amber emission)
    Hg, Wg = 512, 256
    bolt_warp = fbm(Hg, Wg, [(8, 14, 1.0), (19, 30, 0.5)], seed=211)
    crack = np.power(0.5 + 0.5 * np.sin((yy * 55.0 + bolt_warp * 7.0) * np.pi), 3.5)
    c_root = np.array([0.20, 0.13, 0.08]); c_root_lo = np.array([0.09, 0.05, 0.03])
    col5 = c_root_lo[None, None] * (0.7 + 0.6 * bolt_warp[:, :, None]) + c_root[None, None] * 0.3
    em = np.clip(np.stack([1.0 * crack, 0.72 * crack, 0.25 * crack], axis=2), 0, 1)
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.55 + 0.2 * bolt_warp - 0.25 * crack, 0.2, 0.85),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.6 * crack,
        "emis": em,
    })
    return base, rough, metal, height, emis


def paint_ash():
    base, rough, metal, height, emis = new_atlas()
    H, W = 512, 512

    # TL blade: charcoal blackwood + ash dust + fine cracks
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    char_warp = fbm(H, W, [(4, 3, 1.0), (11, 8, 0.6), (26, 19, 0.35)], seed=301)
    grain = 0.5 + 0.5 * np.sin((xx * 120.0 + yy * 5.0 + char_warp * 8.0) * np.pi)
    cracks = np.power(0.5 + 0.5 * np.sin((xx * 30.0 + yy * 12.0 + char_warp * 6.0) * np.pi), 4.0)
    ash_dust = np.clip(fbm(H, W, [(10, 8, 1.0)], seed=303) * 1.4 - 0.5, 0, 1) * 0.45
    c_char = np.array([0.10, 0.085, 0.075]); c_char_lo = np.array([0.045, 0.038, 0.034]); c_ash = np.array([0.42, 0.40, 0.37])
    col = c_char[None, None] * (0.85 + 0.3 * grain[:, :, None])
    col = col * (1 - cracks[:, :, None]) + c_char_lo[None, None] * cracks[:, :, None]
    col = col * (1 - ash_dust[:, :, None]) + c_ash[None, None] * ash_dust[:, :, None]
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.80 + 0.12 * cracks - 0.10 * ash_dust, 0.55, 0.95),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": -0.5 * cracks + 0.3 * grain - 0.2 * ash_dust,
        "emis": np.clip(np.stack([cracks * 0.55, cracks * 0.18, cracks * 0.04], axis=2), 0, 0.6),
    })

    # TR flair: black thorn bark with cursed violet sheen
    thorn_warp = fbm(H, W, [(6, 5, 1.0), (16, 13, 0.5)], seed=305)
    ridge = np.power(0.5 + 0.5 * np.sin((yy * 30.0 + thorn_warp * 5.0) * np.pi), 2.0)
    c_violet = np.array([0.16, 0.09, 0.18]); c_thorn = np.array([0.07, 0.06, 0.065])
    col2 = c_thorn[None, None] * (0.8 + 0.4 * ridge[:, :, None])
    col2 = col2 + c_violet[None, None] * (0.22 * ridge[:, :, None])
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.72 - 0.15 * ridge, 0.45, 0.85),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.45 * ridge,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })

    # BL grip: charcoal wrap with faint ember dots
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.6),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.6))
    grit = fbm(H, W, [(22, 22, 1.0), (48, 44, 0.5)], seed=307)
    col3 = c_char_lo[None, None] + (c_char - c_char_lo)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * grit[:, :, None])
    ember_dots = np.clip(grit * 2.2 - 1.15, 0, 1)
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.78 - 0.12 * weave, 0.55, 0.9),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.55 * weave + 0.15 * grit,
        "emis": np.clip(np.stack([ember_dots * 0.9, ember_dots * 0.3, ember_dots * 0.06], axis=2), 0, 0.9),
    })

    # BM shell: cursed iron-ash (dark grey metal)
    Hb, Wb = 512, 256
    hammer = fbm(Hb, Wb, [(11, 11, 1.0), (25, 23, 0.5)], seed=309)
    c_iron = np.array([0.22, 0.21, 0.23])
    col4 = c_iron[None, None] * (0.85 + 0.25 * hammer[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.52 + 0.16 * hammer, 0.4, 0.8),
        "metal": np.full((Hb, Wb), 0.55, dtype=np.float32),
        "height": 0.3 * hammer,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })

    # BR glow: smoldering ember core & fissures (fiery emission)
    Hg, Wg = 512, 256
    fire_warp = fbm(Hg, Wg, [(7, 12, 1.0), (17, 26, 0.5)], seed=311)
    fire = np.power(0.5 + 0.5 * np.sin((yy * 48.0 + fire_warp * 6.0) * np.pi), 3.0)
    hot = np.clip(fire * 1.35 - 0.08, 0, 1)
    em = np.clip(np.stack([1.0 * hot, np.power(hot, 1.6) * 0.62, np.power(hot, 3.5) * 0.12], axis=2), 0, 1)
    col5 = np.array([0.05, 0.02, 0.012])[None, None] * (1 + fire_warp[:, :, None] * 0.5)
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.6 - 0.3 * hot, 0.25, 0.8),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.55 * fire,
        "emis": em,
    })
    return base, rough, metal, height, emis


PAINTERS = {"verdant": paint_verdant, "copper": paint_copper, "ash": paint_ash}

OUT_DIRS = {
    "verdant": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/verdant_bough",
    "copper": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/copper_root",
    "ash": "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/ash_thorn",
}
TEX_BASE = {"verdant": "verdant_bough", "copper": "copper_root", "ash": "ash_thorn"}


def save_maps(which):
    base, rough, metal, height, emis = PAINTERS[which]()
    out_dir = OUT_DIRS[which]
    tb = TEX_BASE[which]
    import os
    os.makedirs(out_dir, exist_ok=True)
    Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8)).save("%s/%s_basecolor.png" % (out_dir, tb))
    Image.fromarray((np.clip(rough, 0, 1) * 255).astype(np.uint8)).save("%s/%s_roughness.png" % (out_dir, tb))
    Image.fromarray((np.clip(metal, 0, 1) * 255).astype(np.uint8)).save("%s/%s_metallic.png" % (out_dir, tb))
    Image.fromarray((normalize_height_to_normal(height) * 255).astype(np.uint8)).save("%s/%s_normal.png" % (out_dir, tb))
    Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8)).save("%s/%s_emission.png" % (out_dir, tb))
    print("PBR_SAVED", which, out_dir)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    todo = list(PAINTERS.keys()) if arg == "all" else [arg]
    for w in todo:
        save_maps(w)

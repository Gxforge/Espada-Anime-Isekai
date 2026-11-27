# -*- coding: utf-8 -*-
"""
Studio Lexair - REMASTER PILOT: atlas PBR 2048x2048 x 5 mapas (4x detalle).
Realismo: ruido de valor multi-octava, micro-rayas, desgaste de filo, damasco,
martillado, AO de grietas, normales suavizadas. Anime proportions intactas.
Regiones identicas (x2 px): blade TL, flair TR, grip BL, shell BM, glow BR.

Uso: python3 paint_remaster_2048.py [wood|glacier|devourer|archangel|sunforge|all]
"""
import sys
import os
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

REPO = "/home/user/Espada-Anime-Isekai"
N = 2048
R_BLADE = (0, 1024, 0, 1024)
R_FLAIR = (0, 1024, 1024, 2048)
R_GRIP = (1024, 2048, 0, 1024)
R_SHELL = (1024, 2048, 1024, 1536)
R_GLOW = (1024, 2048, 1536, 2048)


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


def vnoise(h, w, cells, seed=42, octaves=3):
    """Value noise multi-octava (grid aleatorio + bilinear). cells = px base."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    amp_sum = 0.0
    for o in range(octaves):
        cw = max(2, int(cells / (2 ** o)))
        gh = max(2, h // cw + 1); gw = max(2, w // cw + 1)
        g = (rng.uniform(0, 1, (gh, gw)) * 255).astype(np.uint8)
        img = Image.fromarray(g).resize((w, h), Image.BILINEAR)
        acc += (np.asarray(img, dtype=np.float32) / 255.0) * (0.5 ** o)
        amp_sum += 0.5 ** o
    return acc / max(1e-5, amp_sum)


def streaks(h, w, n, seed, angle=90.0, jitter=14.0, ln=(0.10, 0.45), wid=(1, 3), blur=1.5):
    """Micro-rayas finas (scratches/hairlines). angle 90 = a lo largo (v/length)."""
    rng = np.random.default_rng(seed)
    img = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(img)
    for _ in range(n):
        x0 = rng.uniform(0, w); y0 = rng.uniform(0, h)
        a = math.radians(angle + rng.uniform(-jitter, jitter))
        L = rng.uniform(ln[0], ln[1]) * h
        dx, dy = math.cos(a) * L, math.sin(a) * L
        wd = rng.uniform(wid[0], wid[1])
        dr.line([(x0, y0), (x0 + dx, y0 + dy)], fill=int(rng.uniform(120, 255)), width=max(1, int(wd)))
    img = img.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(img, dtype=np.float32) / 255.0


def edge_wear(h, w, band=0.055, seed=7, grit_cells=110):
    """Desgaste del filo: bandas en u~0 y u~1 (bordes de corte) rotas por ruido."""
    xx = np.linspace(0, 1, w)[None, :]
    b = np.clip(1.0 - np.minimum(xx, 1.0 - xx) / band, 0, 1)
    n = vnoise(h, w, grit_cells, seed, octaves=2)
    return np.clip(b * (0.55 + 0.75 * n), 0, 1) + np.zeros((h, w), dtype=np.float32)


def hammer_pits(h, w, cells, seed, depth=0.5, thresh=0.74):
    """Celdillas de martillado: hoyuelos suaves para height."""
    n = vnoise(h, w, cells, seed, octaves=2)
    pits = np.clip((n - thresh) / (1.0 - thresh), 0, 1)
    img = Image.fromarray((pits * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return (np.asarray(img, dtype=np.float32) / 255.0) * depth


def damascus(h, w, freq, seed, warp_amp=3.0):
    """Bandas de damasco (capas forjadas) + grano fino."""
    yy = np.linspace(0, 1, h)[:, None]; xx = np.linspace(0, 1, w)[None, :]
    warp1 = fbm(h, w, [(2, 1, 1.0)], seed=seed) * warp_amp / 4.0
    band = 0.5 + 0.5 * np.sin((xx * freq + warp1 * warp_amp) * 2 * np.pi)
    d = np.power(np.abs(band), 2.2)
    fine = vnoise(h, w, 150, seed + 1, octaves=2)
    return np.clip(d * 0.8 + fine * 0.2, 0, 1) + np.zeros((h, w), dtype=np.float32)


def smooth_arr(a, radius=2.0):
    if a.ndim == 2:
        img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
        return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0
    return np.stack([smooth_arr(a[:, :, i], radius) for i in range(3)], axis=2)


def ao_from_height(height, strength=0.30):
    """Oclusión ambiental pintada: oscurece huecos, aclara crestas."""
    h01 = smooth_arr(np.clip(height * 0.5 + 0.5, 0, 1), radius=6)
    return np.clip(1.0 - strength * (1.0 - h01), 0.55, 1.0)


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


def normal_from_height(height, strength=2.0, blur=2.0):
    hs = smooth_arr(np.clip(height * 0.5 + 0.5, 0, 1), radius=blur) * 2.0 - 1.0
    sx = np.zeros_like(hs); sy = np.zeros_like(hs)
    sx[1:-1, 1:-1] = (hs[1:-1, 2:] - hs[1:-1, :-2]) * strength
    sy[1:-1, 1:-1] = (hs[2:, 1:-1] - hs[:-2, 1:-1]) * strength
    n = np.dstack([-sx, sy, np.ones_like(hs)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return np.clip(n * 0.5 + 0.5, 0.0, 1.0)


# =============================================================================
# 1. wood_ancestral (Etapa 01) - madera ancestral remasterizada 2048
# =============================================================================
def paint_wood():
    base, rough, metal, height, emis = new_atlas()
    H, W = 1024, 1024
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: heartwood de abedul-roble, veta fina multi-octava + nudos
    warp = fbm(H, W, [(3, 2, 1.0), (7, 5, 0.5), (15, 9, 0.25)], seed=11)
    grain = np.power(0.5 + 0.5 * np.sin((yy * 26.0 + warp * 7.0) * np.pi), 2.2)
    grain_f = np.power(0.5 + 0.5 * np.sin((yy * 60.0 + warp * 16.0) * np.pi), 3.0)
    c_hi = np.array([0.78, 0.62, 0.42]); c_mid = np.array([0.58, 0.42, 0.26]); c_lo = np.array([0.36, 0.24, 0.13])
    col = c_mid[None, None] * (1 - 0.42 * grain[:, :, None]) + c_lo[None, None] * (0.42 * grain[:, :, None])
    col = col + c_hi[None, None] * (0.16 * (1.0 - grain[:, :, None]) * warp[:, :, None])
    knots = np.zeros((H, W), dtype=np.float32)
    for kx, ky, rr, kf in ((0.30, 0.34, 0.10, 26.0), (0.66, 0.72, 0.075, 30.0)):
        r = np.sqrt(((yy - ky) * 1.0) ** 2 + ((xx - kx) * 1.0) ** 2)
        ring = np.abs(np.sin((r + 0.02 * np.sin(np.arctan2(yy - ky, xx - kx) * 6.0)) * kf * np.pi))
        knots = knots + np.clip(1.0 - r / rr, 0, 1) * np.power(ring, 1.5)
    knots = np.clip(knots, 0, 1)
    col = col * (1.0 - 0.30 * knots[:, :, None]) + np.array([0.24, 0.15, 0.08])[None, None] * (0.30 * knots[:, :, None])
    wear = edge_wear(H, W, band=0.05, seed=13)
    col = col + np.array([0.80, 0.70, 0.55])[None, None] * (0.10 * wear[:, :, None])
    scratches = streaks(H, W, 90, 17, angle=90, ln=(0.06, 0.30), wid=(1, 2))
    col = col * (0.94 + 0.12 * scratches[:, :, None])
    col = col * ao_from_height(0.4 * grain + 0.6 * knots, 0.22)[:, :, None] * (1.0 + 0.06 * warp[:, :, None])
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.44 - 0.10 * wear + 0.08 * grain + 0.05 * scratches, 0.26, 0.66),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.22 * grain + 0.12 * grain_f - 0.26 * knots - 0.06 * scratches,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # TR flair: corteza nudosa agrietada
    bark_w = fbm(H, W, [(4, 3, 1.0), (11, 7, 0.5)], seed=23)
    fissure = np.power(1.0 - np.abs(np.sin((xx * 7.0 + bark_w * 4.0) * np.pi)), 26.0)
    fissure = fissure * (0.55 + 0.45 * vnoise(H, W, 60, 29, octaves=2))
    c_b1 = np.array([0.34, 0.24, 0.15]); c_b2 = np.array([0.16, 0.10, 0.06])
    col2 = c_b1[None, None] * (1 - 0.5 * bark_w[:, :, None]) + c_b2[None, None] * (0.5 * bark_w[:, :, None])
    col2 = col2 * (1.0 - 0.45 * fissure[:, :, None])
    moss = np.clip(vnoise(H, W, 26, 31, octaves=2) - 0.55, 0, 1) * 2.2
    col2 = col2 + np.array([0.20, 0.30, 0.12])[None, None] * (0.22 * moss[:, :, None])
    col2 = col2 * ao_from_height(fissure - 0.3, 0.35)[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.72 + 0.10 * bark_w - 0.08 * moss, 0.55, 0.88),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.42 * fissure + 0.14 * bark_w,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: cordón trenzado de castaño + fibra
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 30 + yy * 30) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 30 - yy * 30) * np.pi), 1.8))
    fiber = vnoise(H, W, 130, 37, octaves=2)
    c_c1 = np.array([0.52, 0.36, 0.20]); c_c2 = np.array([0.28, 0.18, 0.09])
    col3 = c_c2[None, None] + (c_c1 - c_c2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.90 + 0.18 * fiber[:, :, None])
    col3 = col3 * ao_from_height(weave, 0.28)[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.66 - 0.12 * weave + 0.06 * fiber, 0.48, 0.82),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.50 * weave + 0.08 * fiber,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: bronce santuario cepillado + pátina
    Hb, Wb = 1024, 512
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    brush = np.power(0.5 + 0.5 * np.sin((yyb * 120.0 + fbm(Hb, Wb, [(3, 2, 1.0)], seed=41) * 6.0) * np.pi), 1.6)
    patina = np.clip(vnoise(Hb, Wb, 40, 43, octaves=3) - 0.52, 0, 1) * 2.0
    c_br1 = np.array([0.70, 0.52, 0.28]); c_br2 = np.array([0.38, 0.30, 0.18])
    col4 = c_br1[None, None] * (0.82 + 0.24 * brush[:, :, None]) + c_br2[None, None] * (0.30 * brush[:, :, None])
    col4 = col4 * (1.0 - 0.40 * patina[:, :, None]) + np.array([0.30, 0.42, 0.28])[None, None] * (0.32 * patina[:, :, None])
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.30 + 0.14 * patina - 0.06 * brush, 0.18, 0.55),
        "metal": np.clip(0.92 - 0.45 * patina, 0.3, 1.0) + np.zeros((Hb, Wb), dtype=np.float32),
        "height": 0.14 * brush - 0.18 * patina,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: cristal esmeralda-cian + savia ámbar + runas
    Hg, Wg = 1024, 512
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    facet = np.floor(xxg * 8.0 + yyg * 2.0) % 2.0
    facet = facet + np.zeros((Hg, Wg), dtype=np.float32)
    inner = np.power(np.abs(np.sin((xxg * 6.0 - yyg * 3.0) * np.pi)), 12.0)
    c_cr1 = np.array([0.30, 0.85, 0.62]); c_cr2 = np.array([0.10, 0.45, 0.38])
    col5 = c_cr2[None, None] + (c_cr1 - c_cr2)[None, None] * (0.45 + 0.45 * facet[:, :, None])
    col5 = col5 + np.array([0.92, 0.78, 0.40])[None, None] * (0.20 * inner[:, :, None])
    runes = np.zeros((Hg, Wg), dtype=np.float32)
    for ry, rx, rl in ((0.30, 0.30, 0.16), (0.52, 0.62, 0.20), (0.72, 0.38, 0.12)):
        rr = np.sqrt(((yyg - ry) * 1.0) ** 2 + ((xxg - rx) * 2.0) ** 2)
        runes = runes + np.clip(1.0 - rr / rl, 0, 1)
    runes = np.clip(runes, 0, 1)
    sap = np.clip(vnoise(Hg, Wg, 30, 47, octaves=2) - 0.6, 0, 1) * 2.0
    em = np.clip(np.stack([0.20 * runes + 0.55 * sap, 0.95 * runes + 0.42 * sap, 0.60 * runes + 0.10 * sap], axis=2), 0, 1)
    col5 = col5 * (1.0 - 0.15 * runes[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.14 + 0.10 * facet, 0.07, 0.34),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": 0.10 * facet - 0.14 * runes,
        "emis": em,
    })
    return base, rough, metal, height, emis


# =============================================================================
# 2. glacier_fang (Etapa 06) - hielo glaciar remasterizado 2048
# =============================================================================
def paint_glacier():
    base, rough, metal, height, emis = new_atlas()
    H, W = 1024, 1024
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: hielo pálido + grietas profundas + fracturas internas blancas
    warp = fbm(H, W, [(4, 3, 1.0), (10, 6, 0.5)], seed=591)
    crev = np.power(0.5 + 0.5 * np.sin((xx * 9.0 + warp * 5.5) * np.pi), 3.4)
    crev_f = np.power(0.5 + 0.5 * np.sin((xx * 24.0 + warp * 12.0) * np.pi), 6.0)
    frost = np.clip(vnoise(H, W, 46, 593, octaves=3) - 0.45, 0, 1) * 1.7
    fractures = streaks(H, W, 55, 596, angle=90, jitter=20, ln=(0.10, 0.50), wid=(1, 3), blur=2.0)
    c_hi = np.array([0.93, 0.98, 1.0]); c_mid = np.array([0.50, 0.80, 0.98]); c_lo = np.array([0.16, 0.42, 0.78])
    col = c_mid[None, None] * (1 - 0.62 * crev[:, :, None]) + c_lo[None, None] * (0.62 * crev[:, :, None])
    col = col + c_hi[None, None] * (0.18 * frost[:, :, None] + 0.22 * fractures[:, :, None])
    col = col * np.array([0.90, 0.98, 1.08])[None, None]
    wear = edge_wear(H, W, band=0.045, seed=598)
    col = col * ao_from_height(-crev, 0.42)[:, :, None]
    emis_blade = np.clip(np.stack([0.22 * crev + 0.18 * fractures, 0.42 * crev + 0.26 * fractures, 0.58 * crev + 0.30 * fractures], axis=2), 0, 0.65)
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.14 + 0.06 * crev - 0.03 * frost + 0.05 * crev_f, 0.08, 0.32),
        "metal": np.clip(0.03 + 0.04 * wear, 0, 0.10) + np.zeros((H, W), dtype=np.float32),
        "height": -0.26 * crev + 0.14 * frost + 0.10 * crev_f - 0.08 * fractures,
        "emis": emis_blade,
    })
    # TR flair: acero helado martillado + escarcha hoarfrost
    hammer = fbm(H, W, [(10, 9, 1.0), (22, 20, 0.5)], seed=595)
    pits = hammer_pits(H, W, 26, 599, depth=0.5, thresh=0.76)
    hoar = np.clip(vnoise(H, W, 38, 601, octaves=3) - 0.48, 0, 1) * 1.8
    c_s1 = np.array([0.56, 0.68, 0.76]); c_s2 = np.array([0.30, 0.42, 0.52])
    col2 = c_s2[None, None] * (0.85 + 0.30 * hammer[:, :, None]) + c_hi[None, None] * (0.18 * hoar[:, :, None])
    col2 = col2 - np.array([0.06, 0.06, 0.07])[None, None] * (pits[:, :, None] * 1.4)
    col2 = col2 * ao_from_height(hammer - pits, 0.25)[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.34 + 0.10 * hammer - 0.08 * hoar + 0.06 * pits, 0.18, 0.58),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.22 * hammer + 0.18 * hoar - 0.30 * pits,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: envoltura azul-hielo con fibra helada
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 30 + yy * 30) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 30 - yy * 30) * np.pi), 1.8))
    fiber = vnoise(H, W, 120, 603, octaves=2)
    rimed = np.clip(vnoise(H, W, 50, 605, octaves=2) - 0.55, 0, 1) * 1.6
    c_w1 = np.array([0.24, 0.46, 0.62]); c_w2 = np.array([0.10, 0.20, 0.32])
    col3 = c_w2[None, None] + (c_w1 - c_w2)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.12 * fiber[:, :, None])
    col3 = col3 + c_hi[None, None] * (0.30 * rimed[:, :, None])
    col3 = col3 * ao_from_height(weave, 0.26)[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave + 0.06 * fiber - 0.10 * rimed, 0.30, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.50 * weave + 0.07 * fiber + 0.16 * rimed,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: plata helada cepillada
    Hb, Wb = 1024, 512
    yyb = np.linspace(0, 1, Hb)[:, None]; xxb = np.linspace(0, 1, Wb)[None, :]
    brush = streaks(Hb, Wb, 130, 607, angle=88, ln=(0.15, 0.5), wid=(1, 2), blur=1.2)
    hammers2 = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=609)
    c_s = np.array([0.64, 0.74, 0.80])
    col4 = c_s[None, None] * (0.84 + 0.22 * hammers2[:, :, None]) * (0.94 + 0.12 * brush[:, :, None])
    col4 = col4 * ao_from_height(hammers2, 0.24)[:, :, None]
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.22 + 0.10 * hammers2 - 0.05 * brush, 0.12, 0.46),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.24 * hammers2 + 0.05 * brush,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: estrella congelada (núcleo blanco, corona cian)
    Hg, Wg = 1024, 512
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.5) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    core = np.clip(1.0 - r * 3.0, 0, 1) ** 1.6
    corona = np.clip(1.0 - r * 1.6, 0, 1) * np.power(0.5 + 0.5 * np.sin(np.arctan2(yyg - 0.5, xxg - 0.5) * 6.0), 3.0)
    sparkle = np.power(np.clip(vnoise(Hg, Wg, 60, 611, octaves=2) - 0.62, 0, 1) * 2.6, 2.0)
    glow_amt = np.clip(core + 0.5 * corona + 0.25 * sparkle, 0, 1)
    em = np.clip(np.stack([0.80 * glow_amt + 0.2 * core, 0.96 * glow_amt, 1.0 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.7 + 0.4 * core[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.18 - 0.10 * core, 0.08, 0.36),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.30 * core,
        "emis": em,
    })
    return base, rough, metal, height, emis


# =============================================================================
# 3. soul_devourer (Etapa 10) - acero negro-brasa remasterizado 2048
# =============================================================================
def paint_devourer():
    base, rough, metal, height, emis = new_atlas()
    H, W = 1024, 1024
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: acero negro con damasco sutil + grietas de brasa + filo encendido
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=851)
    crack = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.0, 0, 1), 2.5)
    crack_f = np.power(np.clip(1.0 - np.abs(fbm(H, W, [(14, 8, 1.0)], seed=858) - 0.5) * 10.0, 0, 1), 3.0)
    ember = np.array([0.98, 0.38, 0.09])
    dam = damascus(H, W, 22, 853, warp_amp=4.0)
    wear = edge_wear(H, W, band=0.05, seed=857)
    edgeband = np.clip((xx - 0.82) * 6.5, 0, 1) + np.zeros((H, W), dtype=np.float32)
    c_lo = np.array([0.045, 0.04, 0.055]); c_mid = np.array([0.16, 0.11, 0.15])
    col = c_lo[None, None] + (c_mid - c_lo)[None, None] * (0.50 + 0.45 * warp[:, :, None])
    col = col * (0.88 + 0.24 * dam[:, :, None])
    col = col + ember[None, None] * (0.46 * crack[:, :, None] + 0.18 * crack_f[:, :, None] + 0.28 * edgeband[:, :, None])
    col = col + np.array([0.62, 0.60, 0.58])[None, None] * (0.12 * wear[:, :, None])
    col = col * ao_from_height(0.5 * dam - 0.5 * crack, 0.30)[:, :, None]
    em = np.clip(np.stack([0.66 * crack + 0.22 * crack_f + 0.34 * edgeband, 0.22 * crack + 0.06 * crack_f + 0.11 * edgeband, 0.05 * crack], axis=2), 0, 0.85)
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.30 + 0.16 * dam - 0.12 * crack + 0.05 * warp - 0.06 * wear, 0.14, 0.62),
        "metal": np.clip(0.66 + 0.14 * dam, 0.4, 0.9) + np.zeros((H, W), dtype=np.float32),
        "height": 0.10 * warp + 0.24 * crack - 0.10 * dam,
        "emis": em,
    })
    # TR flair: escoria negra moteada con brasas tenues
    mott = fbm(H, W, [(12, 12, 1.0), (26, 24, 0.5)], seed=852)
    pits = hammer_pits(H, W, 30, 859, depth=0.55, thresh=0.75)
    c_lo2 = np.array([0.05, 0.04, 0.05])
    col2 = c_lo2[None, None] * (1.30 + 0.55 * mott[:, :, None]) + np.array([0.45, 0.18, 0.10])[None, None] * (0.18 * mott[:, :, None])
    col2 = col2 - np.array([0.03, 0.03, 0.03])[None, None] * (pits[:, :, None] * 1.2)
    col2 = col2 * ao_from_height(mott - pits, 0.28)[:, :, None]
    em2 = np.clip(np.stack([0.30 * mott, 0.08 * mott, 0.02 * mott], axis=2) * (mott > 0.55)[:, :, None], 0, 0.35)
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.42 + 0.14 * mott - 0.04 * pits, 0.28, 0.70),
        "metal": np.full((H, W), 0.52, dtype=np.float32),
        "height": 0.22 * mott - 0.30 * pits,
        "emis": em2,
    })
    # BL grip: cuero negro con pespuntes rojos sangre
    stitch = np.clip(1.0 - np.abs(((xx * 16.0 + yy * 10.0) % 1.0) - 0.5) * 5.5, 0, 1)
    leather = vnoise(H, W, 95, 855, octaves=3)
    c_g1 = np.array([0.09, 0.07, 0.08])
    col3 = c_g1[None, None] * (0.9 + 0.30 * leather[:, :, None]) + np.array([0.58, 0.13, 0.13])[None, None] * (0.34 * stitch[:, :, None])
    col3 = col3 * ao_from_height(stitch + leather * 0.3, 0.24)[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.60 + 0.10 * leather - 0.10 * stitch, 0.42, 0.80),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.42 * stitch + 0.10 * leather,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: negro-brasa martillado
    Hb, Wb = 1024, 512
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=856)
    pits2 = hammer_pits(Hb, Wb, 28, 861, depth=0.45, thresh=0.76)
    col4 = c_lo[None, None] * (1.15 + 0.5 * hammer[:, :, None]) + ember[None, None] * (0.10 * hammer[:, :, None])
    col4 = col4 * ao_from_height(hammer - pits2, 0.26)[:, :, None]
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.36 + 0.13 * hammer - 0.04 * pits2, 0.22, 0.62),
        "metal": np.full((Hb, Wb), 0.62, dtype=np.float32),
        "height": 0.26 * hammer - 0.28 * pits2,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: pozo de ánimas (anillo + espiral ascendente naranja)
    Hg, Wg = 1024, 512
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + ((xxg - 0.5) * 1.0) ** 2)
    ring = np.power(np.abs(np.sin(r * 20.0 - 1.0)), 14.0) * np.clip(1.0 - r * 1.7, 0, 1)
    spx = 0.5 + 0.14 * np.cos(yyg * 12.0 + 1.2)
    arc = np.exp(-(((xxg - spx) ** 2) / 0.002)) * np.clip(1.0 - np.abs(yyg - 0.5) * 1.5, 0, 1)
    wisps = np.clip(vnoise(Hg, Wg, 55, 863, octaves=2) - 0.58, 0, 1) * 1.4
    glow_amt = np.clip(0.50 * ring + 0.50 * arc + 0.30 * wisps, 0, 1)
    em5 = np.clip(np.stack([0.98 * glow_amt, 0.42 * glow_amt, 0.12 * glow_amt], axis=2), 0, 1)
    col5 = c_lo[None, None] * (0.9 + 0.5 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.30 - 0.10 * glow_amt, 0.16, 0.46),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.22 * glow_amt,
        "emis": em5,
    })
    return base, rough, metal, height, emis


# =============================================================================
# 4. archangel_verdict (Etapa 12) - perla-oro catedral remasterizado 2048
# =============================================================================
def paint_archangel():
    base, rough, metal, height, emis = new_atlas()
    H, W = 1024, 1024
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: perla blanca con arcos catedral + hilo de oro + filo pulido
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1041)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    arch = np.power(np.abs(np.sin((yy * 5.0) * np.pi)), 6.0)
    arch_f = np.power(np.abs(np.sin((yy * 30.0 + warp * 4.0) * np.pi)), 24.0)
    edge = np.clip(np.abs(xx - 0.5) * 2.3 - 0.42, 0, 1) + np.zeros((H, W), dtype=np.float32)
    wear = edge_wear(H, W, band=0.045, seed=1047)
    c_hi = np.array([0.995, 0.99, 0.95]); c_mid = np.array([0.93, 0.925, 0.87]); c_lo = np.array([0.62, 0.60, 0.52])
    c_gold = np.array([0.93, 0.81, 0.44])
    col = c_mid[None, None] * (1 - 0.40 * arch[:, :, None]) + c_lo[None, None] * (0.40 * arch[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None]) + c_hi[None, None] * (0.32 * edge[:, :, None])
    col = col + c_gold[None, None] * (0.08 * arch[:, :, None] + 0.16 * arch_f[:, :, None])
    col = col * ao_from_height(0.4 * arch - 0.4 * arch_f, 0.22)[:, :, None]
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.12 - 0.06 * edge - 0.03 * sheen + 0.02 * arch_f - 0.04 * wear, 0.07, 0.30),
        "metal": np.clip(0.76 + 0.10 * arch_f, 0.5, 0.95) + np.zeros((H, W), dtype=np.float32),
        "height": 0.10 * sheen - 0.06 * arch + 0.05 * arch_f,
        "emis": np.clip(np.stack([edge * 0.24 + arch_f * 0.10, edge * 0.20 + arch_f * 0.08, edge * 0.11 + arch_f * 0.04], axis=2), 0, 0.4),
    })
    # TR flair: plumas doradas con barbas reales
    feather_rows = 0.5 + 0.5 * np.sin((yy * 14.0) * np.pi)
    barbs = np.power(0.5 + 0.5 * np.sin((xx * 60.0 + yy * 8.0) * np.pi), 2.0)
    barb_gaps = np.clip(vnoise(H, W, 34, 1043, octaves=2) - 0.5, 0, 1) * 1.6
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1045)
    c_br = np.array([0.92, 0.78, 0.40])
    col2 = c_br[None, None] * (0.76 + 0.30 * feather_rows[:, :, None] + 0.18 * barbs[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    col2 = col2 * (1.0 - 0.30 * barb_gaps[:, :, None]) + c_hi[None, None] * (0.14 * barb_gaps[:, :, None])
    col2 = col2 * ao_from_height(0.6 * feather_rows + 0.4 * barbs - 0.5 * barb_gaps, 0.26)[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.24 + 0.10 * grit - 0.07 * feather_rows + 0.05 * barb_gaps, 0.14, 0.48),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.30 * feather_rows + 0.14 * barbs - 0.12 * barb_gaps,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: seda marfil con hilos de oro
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.8))
    threads = vnoise(H, W, 130, 1049, octaves=2)
    c_w1 = np.array([0.96, 0.94, 0.86]); c_w2 = np.array([0.52, 0.46, 0.28])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.92 + 0.14 * threads[:, :, None])
    col3 = col3 * ao_from_height(weave, 0.28)[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.54 - 0.12 * weave + 0.06 * threads, 0.36, 0.74),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.52 * weave + 0.07 * threads,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: oro-blanco martillado fino
    Hb, Wb = 1024, 512
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1042)
    pits = hammer_pits(Hb, Wb, 30, 1051, depth=0.4, thresh=0.77)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None]) + c_gold[None, None] * (0.10 * hammer[:, :, None])
    col4 = col4 - np.array([0.04, 0.04, 0.05])[None, None] * (pits[:, :, None] * 1.2)
    col4 = col4 * ao_from_height(hammer - pits, 0.24)[:, :, None]
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.20 + 0.12 * hammer - 0.05 * pits, 0.12, 0.46),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.26 * hammer - 0.24 * pits,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: sello de veredicto (halo + haz descendente)
    Hg, Wg = 1024, 512
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.45) * 1.1) ** 2 + (xxg - 0.5) ** 2)
    halo = np.power(np.abs(np.sin(r * 14.0 - 0.8)), 10.0) * np.clip(1.0 - r * 1.7, 0, 1)
    beam = np.exp(-(((xxg - 0.5) ** 2) / 0.006)) * np.clip(1.0 - np.abs(yyg - 0.45) * 1.6, 0, 1)
    motes = np.power(np.clip(vnoise(Hg, Wg, 60, 1053, octaves=2) - 0.62, 0, 1) * 2.6, 2.0)
    glow_amt = np.clip(0.45 * halo + 0.55 * beam + 0.25 * motes, 0, 1)
    em5 = np.clip(np.stack([1.0 * glow_amt, 0.95 * glow_amt, 0.72 * glow_amt], axis=2), 0, 1)
    col5 = c_mid[None, None] * (0.7 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.18 - 0.08 * glow_amt, 0.09, 0.36),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.24 * glow_amt,
        "emis": em5,
    })
    return base, rough, metal, height, emis


# =============================================================================
# 5. sunforge (Etapa 14) - oro forjado remasterizado 2048
# =============================================================================
def paint_sunforge():
    base, rough, metal, height, emis = new_atlas()
    H, W = 1024, 1024
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(0, 1, W)[None, :]
    # TL blade: oro fundido con costillas de forja + celdillas martilladas + caldo térmico
    warp = fbm(H, W, [(3, 2, 1.0), (9, 5, 0.5)], seed=1241)
    sheen = 0.5 + 0.5 * np.sin((yy * 5.0 + warp * 1.6) * np.pi)
    seam = np.power(np.clip(1.0 - np.abs(warp - 0.5) * 8.0, 0, 1), 2.5)
    heat = np.power(0.5 + 0.5 * np.sin((yy * 6.0 + warp * 2.0) * np.pi), 2.0)
    pits = hammer_pits(H, W, 30, 1242, depth=0.55, thresh=0.75)
    wear = edge_wear(H, W, band=0.05, seed=1244)
    scratches = streaks(H, W, 70, 1246, angle=90, ln=(0.05, 0.25), wid=(1, 2))
    ember = np.array([1.00, 0.52, 0.14])
    c_hi = np.array([1.00, 0.90, 0.60]); c_mid = np.array([0.88, 0.72, 0.38]); c_lo = np.array([0.50, 0.36, 0.16])
    col = c_mid[None, None] * (1 - 0.40 * heat[:, :, None]) + c_lo[None, None] * (0.40 * heat[:, :, None])
    col = col + ember[None, None] * (0.50 * seam[:, :, None])
    col = col * (0.90 + 0.16 * sheen[:, :, None])
    col = col - np.array([0.10, 0.08, 0.05])[None, None] * (pits[:, :, None] * 1.3)
    col = col * (0.94 + 0.10 * scratches[:, :, None]) + c_hi[None, None] * (0.14 * wear[:, :, None])
    col = col * ao_from_height(0.5 * seam - 0.6 * pits, 0.30)[:, :, None]
    place(base, rough, metal, height, emis, R_BLADE, {
        "base": np.clip(col, 0, 1),
        "rough": np.clip(0.22 - 0.10 * seam - 0.06 * wear + 0.08 * pits + 0.04 * scratches, 0.11, 0.44),
        "metal": np.full((H, W), 0.88, dtype=np.float32),
        "height": 0.10 * sheen + 0.22 * seam - 0.34 * pits,
        "emis": np.clip(np.stack([0.80 * seam, 0.38 * seam, 0.08 * seam], axis=2), 0, 0.85),
    })
    # TR flair: bronce radial martillado (rayos de yunque)
    ang = np.arctan2(yy - 0.5, xx - 0.5)
    rays = np.power(np.abs(np.cos(ang * 10.0)), 3.0)
    grit = fbm(H, W, [(13, 11, 1.0)], seed=1243)
    pits2 = hammer_pits(H, W, 34, 1248, depth=0.5, thresh=0.76)
    c_br = np.array([0.42, 0.34, 0.30])
    col2 = c_br[None, None] * (0.78 + 0.30 * rays[:, :, None]) * (0.94 + 0.10 * grit[:, :, None])
    col2 = col2 - np.array([0.05, 0.05, 0.05])[None, None] * (pits2[:, :, None] * 1.2)
    col2 = col2 * ao_from_height(0.5 * rays - 0.5 * pits2, 0.26)[:, :, None]
    place(base, rough, metal, height, emis, R_FLAIR, {
        "base": np.clip(col2, 0, 1),
        "rough": np.clip(0.26 + 0.10 * grit - 0.06 * rays + 0.06 * pits2, 0.16, 0.48),
        "metal": np.full((H, W), 0.80, dtype=np.float32),
        "height": 0.30 * rays - 0.30 * pits2,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BL grip: cobro-oro trenzado con fibra de cuero
    weave = np.maximum(np.power(0.5 + 0.5 * np.sin((xx * 28 + yy * 28) * np.pi), 1.8),
                       np.power(0.5 + 0.5 * np.sin((xx * 28 - yy * 28) * np.pi), 1.8))
    fiber = vnoise(H, W, 120, 1250, octaves=2)
    c_w1 = np.array([0.60, 0.30, 0.16]); c_w2 = np.array([0.85, 0.66, 0.36])
    col3 = c_w1[None, None] + (c_w2 - c_w1)[None, None] * weave[:, :, None]
    col3 = col3 * (0.90 + 0.16 * fiber[:, :, None])
    col3 = col3 * ao_from_height(weave, 0.28)[:, :, None]
    place(base, rough, metal, height, emis, R_GRIP, {
        "base": np.clip(col3, 0, 1),
        "rough": np.clip(0.52 - 0.12 * weave + 0.06 * fiber, 0.34, 0.72),
        "metal": np.zeros((H, W), dtype=np.float32),
        "height": 0.52 * weave + 0.07 * fiber,
        "emis": np.zeros((H, W, 3), dtype=np.float32),
    })
    # BM shell: oro alto martillado (camisa del yunque)
    Hb, Wb = 1024, 512
    hammer = fbm(Hb, Wb, [(10, 10, 1.0), (24, 22, 0.5)], seed=1245)
    pits3 = hammer_pits(Hb, Wb, 30, 1252, depth=0.45, thresh=0.76)
    col4 = c_hi[None, None] * (0.80 + 0.24 * hammer[:, :, None])
    col4 = col4 - np.array([0.06, 0.05, 0.04])[None, None] * (pits3[:, :, None] * 1.2)
    col4 = col4 * ao_from_height(hammer - pits3, 0.24)[:, :, None]
    place(base, rough, metal, height, emis, R_SHELL, {
        "base": np.clip(col4, 0, 1),
        "rough": np.clip(0.22 + 0.12 * hammer - 0.05 * pits3, 0.13, 0.48),
        "metal": np.full((Hb, Wb), 0.90, dtype=np.float32),
        "height": 0.28 * hammer - 0.28 * pits3,
        "emis": np.zeros((Hb, Wb, 3), dtype=np.float32),
    })
    # BR glow: crisol sagrado (boca de forja + llamas ascendentes + chispas)
    Hg, Wg = 1024, 512
    yyg = np.linspace(0, 1, Hg)[:, None]; xxg = np.linspace(0, 1, Wg)[None, :]
    r = np.sqrt(((yyg - 0.42) * 1.15) ** 2 + (xxg - 0.5) ** 2)
    mouth = np.power(np.abs(np.sin(r * 14.0 - 0.6)), 13.0) * np.clip(1.2 - r * 1.6, 0, 1)
    flames = np.zeros((Hg, Wg), dtype=np.float32)
    for fx in (0.36, 0.50, 0.64):
        flames = flames + np.exp(-(((xxg - fx + 0.03 * np.sin(yyg * 9.0)) ** 2) / 0.004)) * np.clip(1.0 - yyg * 1.3, 0, 1) * 0.8
    sparks = np.power(np.clip(vnoise(Hg, Wg, 70, 1254, octaves=2) - 0.65, 0, 1) * 2.8, 2.0)
    glow_amt = np.clip(0.55 * mouth + 0.50 * flames + 0.25 * sparks, 0, 1)
    em5 = np.clip(np.stack([1.0 * glow_amt, 0.56 * glow_amt, 0.12 * glow_amt], axis=2), 0, 1)
    col5 = c_hi[None, None] * (0.6 + 0.4 * glow_amt[:, :, None])
    place(base, rough, metal, height, emis, R_GLOW, {
        "base": np.clip(col5, 0, 1),
        "rough": np.clip(0.22 - 0.10 * glow_amt, 0.11, 0.40),
        "metal": np.zeros((Hg, Wg), dtype=np.float32),
        "height": -0.26 * glow_amt,
        "emis": em5,
    })
    return base, rough, metal, height, emis


PAINTERS = {"wood": paint_wood, "glacier": paint_glacier, "devourer": paint_devourer,
            "archangel": paint_archangel, "sunforge": paint_sunforge}
OUT_DIRS = {
    "wood": os.path.join(REPO, "godot_project", "assets", "models", "swords", "wood_ancestral"),
    "glacier": os.path.join(REPO, "godot_project", "assets", "models", "swords", "glacier_fang"),
    "devourer": os.path.join(REPO, "godot_project", "assets", "models", "swords", "soul_devourer"),
    "archangel": os.path.join(REPO, "godot_project", "assets", "models", "swords", "archangel_verdict"),
    "sunforge": os.path.join(REPO, "godot_project", "assets", "models", "swords", "sunforge"),
}
TEX_BASE = {"wood": "wood_ancestral", "glacier": "glacier_fang", "devourer": "soul_devourer",
            "archangel": "archangel_verdict", "sunforge": "sunforge"}


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
    print("PBR_REMASTER_SAVED", which, out_dir)


def main():
    which = "all"
    if len(sys.argv) > 1 and sys.argv[-1] in PAINTERS:
        which = sys.argv[-1]
    for w in (list(PAINTERS.keys()) if which == "all" else [which]):
        save_maps(w)


main()

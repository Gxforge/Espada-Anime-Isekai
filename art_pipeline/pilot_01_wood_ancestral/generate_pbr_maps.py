#!/usr/bin/env python3
"""
Generator for 1024x1024 PBR Texture Atlas of Pilot Sword #01:
s01_wood_ancestral — Espada de Madera Ancestral (Studio Lexair Standard)

Outputs 5 maps into godot_project/assets/models/swords/wood_ancestral/:
- wood_ancestral_basecolor.png
- wood_ancestral_roughness.png
- wood_ancestral_metallic.png
- wood_ancestral_normal.png
- wood_ancestral_emission.png

UV Atlas Layout (v=0 bottom, v=1 top in glTF/Blender UV space; PIL y=0 is top = v=1):
- Top-Left     (u: 0.00..0.50, v: 0.50..1.00 -> x: 0..512,   y: 0..512):   Sacred Birch-Oak Heartwood (Blade)
- Top-Right    (u: 0.50..1.00, v: 0.50..1.00 -> x: 512..1024, y: 0..512):  Ancient Gnarled Bark (Root Guard & Pommel)
- Bottom-Left  (u: 0.00..0.50, v: 0.00..0.50 -> x: 0..512,   y: 512..1024): Braided Chestnut Cord & Ironwood Grip
- Bottom-Mid   (u: 0.50..0.75, v: 0.00..0.50 -> x: 512..768, y: 512..1024): Aged Sanctuary Bronze Ferrules
- Bottom-Right (u: 0.75..1.00, v: 0.00..0.50 -> x: 768..1024, y: 512..1024): Awakening Emerald-Cyan Crystal, Amber Sap & Runes
"""

import os
import numpy as np
from PIL import Image

OUT_DIR = "/home/user/Espada-Anime-Isekai/godot_project/assets/models/swords/wood_ancestral"
os.makedirs(OUT_DIR, exist_ok=True)

N = 1024
base = np.zeros((N, N, 3), dtype=np.float32)
rough = np.full((N, N), 0.65, dtype=np.float32)
metal = np.zeros((N, N), dtype=np.float32)
height = np.zeros((N, N), dtype=np.float32)
emis = np.zeros((N, N, 3), dtype=np.float32)


def fbm_2d(h, w, freqs, seed=42):
    rng = np.random.default_rng(seed)
    yy = np.linspace(0.0, 1.0, h, endpoint=False)[:, None]
    xx = np.linspace(0.0, 1.0, w, endpoint=False)[None, :]
    acc = np.zeros((h, w), dtype=np.float32)
    amp_sum = 0.0
    for fx, fy, amp in freqs:
        ph1 = rng.uniform(0, 2 * np.pi)
        ph2 = rng.uniform(0, 2 * np.pi)
        ph3 = rng.uniform(0, 2 * np.pi)
        wave = (
            np.sin(2 * np.pi * (xx * fx + yy * fy * 0.25) + ph1)
            + 0.6 * np.cos(2 * np.pi * (xx * fx * 0.7 - yy * fy * 0.35) + ph2)
            + 0.35 * np.sin(2 * np.pi * (xx * fx * 1.4 + yy * fy * 0.8) + ph3)
        ) / 1.95
        acc += amp * wave
        amp_sum += amp
    return acc / max(1e-5, amp_sum)


# 1. TOP-LEFT (0:512, 0:512): Sacred Birch-Oak Heartwood (Blade)
H, W = 512, 512
yy = np.linspace(0.0, 1.0, H)[:, None]
xx = np.linspace(0.0, 1.0, W)[None, :]
warp = fbm_2d(H, W, [(3, 2, 1.0), (7, 5, 0.5), (15, 9, 0.25)], seed=11)
rings = 0.5 + 0.5 * np.sin((xx * 26.0 + warp * 4.2) * np.pi)
rings_sharp = np.power(rings, 2.2)
fine_fibers = 0.5 + 0.5 * np.sin((xx * 130.0 + yy * 6.0 + warp * 8.0) * np.pi)
# Edge bevel highlight toward outer u borders (xx near 0.1 or 0.9)
edge_polish = np.clip(1.0 - np.abs(xx - 0.5) * 2.2, 0.0, 1.0)
edge_bevel_glow = np.clip(np.abs(xx - 0.5) * 2.3 - 0.35, 0.0, 1.0)

c_warm_light = np.array([0.81, 0.60, 0.36], dtype=np.float32)
c_heart_mid = np.array([0.63, 0.41, 0.21], dtype=np.float32)
c_ring_dark = np.array([0.40, 0.24, 0.11], dtype=np.float32)

wood_col = (
    c_heart_mid[None, None, :] * (1.0 - 0.45 * rings_sharp[:, :, None])
    + c_ring_dark[None, None, :] * (0.45 * rings_sharp[:, :, None])
)
wood_col = wood_col * (0.90 + 0.16 * fine_fibers[:, :, None])
wood_col = wood_col * (1.0 - 0.28 * edge_bevel_glow[:, :, None]) + c_warm_light[None, None, :] * (0.34 * edge_bevel_glow[:, :, None])

base[0:512, 0:512] = np.clip(wood_col, 0.0, 1.0)
rough[0:512, 0:512] = np.clip(0.56 - 0.18 * edge_bevel_glow + 0.10 * rings_sharp - 0.04 * fine_fibers, 0.28, 0.78)
height[0:512, 0:512] = -0.35 * rings_sharp + 0.18 * fine_fibers

# 2. TOP-RIGHT (0:512, 512:1024): Ancient Gnarled Bark (Root Guard & Pommel)
bark_warp = fbm_2d(H, W, [(5, 4, 1.0), (13, 8, 0.6), (29, 17, 0.35), (53, 31, 0.2)], seed=27)
fissures = np.power(0.5 + 0.5 * np.sin((xx * 38.0 + bark_warp * 6.5) * np.pi), 3.0)
moss_hint = np.clip(bark_warp * 1.4 - 0.35, 0.0, 1.0) * 0.35
c_bark_hi = np.array([0.42, 0.27, 0.15], dtype=np.float32)
c_bark_lo = np.array([0.17, 0.10, 0.06], dtype=np.float32)
c_moss = np.array([0.22, 0.36, 0.18], dtype=np.float32)
bark_col = c_bark_hi[None, None, :] * (1.0 - fissures[:, :, None]) + c_bark_lo[None, None, :] * fissures[:, :, None]
bark_col = bark_col * (1.0 - moss_hint[:, :, None]) + c_moss[None, None, :] * moss_hint[:, :, None]

base[0:512, 512:1024] = np.clip(bark_col, 0.0, 1.0)
rough[0:512, 512:1024] = np.clip(0.74 + 0.18 * fissures, 0.62, 0.94)
height[0:512, 512:1024] = -0.75 * fissures + 0.25 * bark_warp

# 3. BOTTOM-LEFT (512:1024, 0:512): Braided Leather/Vine Cord Wrap
weave_a = 0.5 + 0.5 * np.sin((xx * 28.0 + yy * 28.0) * np.pi)
weave_b = 0.5 + 0.5 * np.sin((xx * 28.0 - yy * 28.0) * np.pi)
braid = np.maximum(np.power(weave_a, 1.6), np.power(weave_b, 1.6))
leather_grain = fbm_2d(H, W, [(19, 19, 1.0), (43, 41, 0.5)], seed=55)
c_cord_hi = np.array([0.58, 0.36, 0.20], dtype=np.float32)
c_cord_lo = np.array([0.26, 0.14, 0.08], dtype=np.float32)
cord_col = c_cord_lo[None, None, :] + (c_cord_hi - c_cord_lo)[None, None, :] * (0.25 + 0.75 * braid[:, :, None])
cord_col *= (0.94 + 0.10 * leather_grain[:, :, None])

base[512:1024, 0:512] = np.clip(cord_col, 0.0, 1.0)
rough[512:1024, 0:512] = np.clip(0.68 - 0.12 * braid + 0.06 * leather_grain, 0.48, 0.85)
height[512:1024, 0:512] = 0.55 * braid + 0.12 * leather_grain

# 4. BOTTOM-MID (512:1024, 512:768): Aged Sanctuary Bronze Ferrules
Hb, Wb = 512, 256
hammer = fbm_2d(Hb, Wb, [(9, 9, 1.0), (21, 21, 0.5), (41, 37, 0.25)], seed=73)
patina_mask = np.clip(-hammer * 1.6 - 0.25, 0.0, 1.0) * 0.45
c_bronze = np.array([0.74, 0.55, 0.30], dtype=np.float32)
c_patina = np.array([0.24, 0.54, 0.46], dtype=np.float32)
br_col = c_bronze[None, None, :] * (0.88 + 0.20 * hammer[:, :, None])
br_col = br_col * (1.0 - patina_mask[:, :, None]) + c_patina[None, None, :] * patina_mask[:, :, None]

base[512:1024, 512:768] = np.clip(br_col, 0.0, 1.0)
metal[512:1024, 512:768] = np.clip(0.84 - 0.45 * patina_mask, 0.2, 0.92)
rough[512:1024, 512:768] = np.clip(0.32 + 0.36 * patina_mask - 0.06 * hammer, 0.22, 0.72)
height[512:1024, 512:768] = 0.22 * hammer

# 5. BOTTOM-RIGHT (512:1024, 768:1024): Awakening Emerald-Cyan Crystal (top half) & Amber Sap (bottom half)
Hc, Wc = 256, 256
crys_noise = fbm_2d(Hc, Wc, [(7, 7, 1.0), (17, 13, 0.6), (31, 29, 0.3)], seed=91)
yy_c = np.linspace(-1.0, 1.0, Hc)[:, None]
xx_c = np.linspace(-1.0, 1.0, Wc)[None, :]
rad = np.sqrt(xx_c**2 + yy_c**2)
core_glow = np.clip(1.15 - rad * 0.75 + 0.22 * crys_noise, 0.25, 1.0)

# Emerald-Turquoise Awakening Seed & Runes (rows 512..768, cols 768..1024)
c_emerald = np.array([0.16, 0.88, 0.68], dtype=np.float32)
c_cyan_hi = np.array([0.62, 0.99, 0.92], dtype=np.float32)
em_col = c_emerald[None, None, :] * (1.0 - 0.55 * core_glow[:, :, None]) + c_cyan_hi[None, None, :] * (0.55 * core_glow[:, :, None])
base[512:768, 768:1024] = np.clip(em_col, 0.0, 1.0)
rough[512:768, 768:1024] = np.clip(0.14 + 0.08 * np.abs(crys_noise), 0.08, 0.26)
metal[512:768, 768:1024] = 0.05
emis[512:768, 768:1024] = np.clip(em_col * (0.55 * core_glow[:, :, None]), 0.0, 1.0)
height[512:768, 768:1024] = 0.18 * crys_noise

# Warm Amber Spirit Sap Stone (rows 768..1024, cols 768..1024)
c_amber = np.array([0.92, 0.56, 0.14], dtype=np.float32)
c_gold_hi = np.array([1.00, 0.86, 0.42], dtype=np.float32)
am_col = c_amber[None, None, :] * (1.0 - 0.5 * core_glow[:, :, None]) + c_gold_hi[None, None, :] * (0.5 * core_glow[:, :, None])
base[768:1024, 768:1024] = np.clip(am_col, 0.0, 1.0)
rough[768:1024, 768:1024] = 0.16
emis[768:1024, 768:1024] = np.clip(am_col * (0.38 * core_glow[:, :, None]), 0.0, 1.0)
height[768:1024, 768:1024] = 0.12 * crys_noise

# Convert height field -> Tangent-Space OpenGL Normal Map (R=+X, G=+Y, B=+Z)
strength = 3.2
dzdx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * strength
dzdy = (np.roll(height, 1, axis=0) - np.roll(height, -1, axis=0)) * strength
nx = -dzdx
ny = -dzdy
nz = np.ones_like(height)
inv_len = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
norm_rgb = np.stack([(nx * inv_len) * 0.5 + 0.5, (ny * inv_len) * 0.5 + 0.5, (nz * inv_len) * 0.5 + 0.5], axis=-1)

Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8), "RGB").save(f"{OUT_DIR}/wood_ancestral_basecolor.png", optimize=True)
Image.fromarray((np.clip(rough, 0, 1) * 255).astype(np.uint8), "L").save(f"{OUT_DIR}/wood_ancestral_roughness.png", optimize=True)
Image.fromarray((np.clip(metal, 0, 1) * 255).astype(np.uint8), "L").save(f"{OUT_DIR}/wood_ancestral_metallic.png", optimize=True)
Image.fromarray((np.clip(norm_rgb, 0, 1) * 255).astype(np.uint8), "RGB").save(f"{OUT_DIR}/wood_ancestral_normal.png", optimize=True)
Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8), "RGB").save(f"{OUT_DIR}/wood_ancestral_emission.png", optimize=True)
print("Generated 5 PBR texture maps in", OUT_DIR)

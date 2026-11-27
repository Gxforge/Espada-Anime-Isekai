# -*- coding: utf-8 -*-
"""
Studio Lexair — Hoja de Catalogo 3D (3x3) de las espadas del proyecto.
Compone los renders individuales de art_pipeline/sword_catalog_renders/individual/
en una unica lamina con titulos, fases y estado de produccion por espada.

Uso: python3 build_catalog_sheet.py
Salida: art_pipeline/sword_catalog_renders/sword_catalog_sheet.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/user/Espada-Anime-Isekai/art_pipeline/sword_catalog_renders"
IND = os.path.join(BASE, "individual")
OUT = os.path.join(BASE, "sword_catalog_sheet.png")

CELL_W, CELL_H = 560, 660
COLS, ROWS = 18, 5
PAD = 24
TITLE_H = 118
FOOT_H = 74
LEGEND_H = 44

W = COLS * CELL_W + (COLS + 1) * PAD
H = TITLE_H + ROWS * CELL_H + (ROWS + 1) * PAD + LEGEND_H + FOOT_H

BG = (16, 19, 27)
CARD = (26, 31, 44)
CARD_BORDER_OK = (86, 196, 143)
CARD_BORDER_TMP = (120, 136, 173)
GOLD = (244, 208, 108)
TXT = (226, 233, 244)
SUB = (150, 165, 192)

def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + name, size)

# (fichero, titulo, fase/etiqueta, estado, border)
CARDS = [
    ("sword_wood_ancestral_pilot_glb.png", "Espada de Madera Ancestral", "Pilot #01 - Etapa 01", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_02_verdant_bough.png", "Hoja de Brote Viviente", "Etapa 02 - Rama Origin (anime organico)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_02_copper_root.png", "Espada de Raiz Cobriza", "Etapa 02 - Rama Elemental (anime electrico)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_02_ash_thorn.png", "Espada de Espino Carbonizado", "Etapa 02 - Rama Maldita (anime brasas)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_03_amber_sanctuary.png", "Hoja de Ambar de Santuario", "Etapa 03 - Rama Blessed (anime catedral)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_03_ironwood_storm.png", "Filo de Palo Ferreo y Trueno", "Etapa 03 - Rama Elemental (anime tormenta)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_03_spirit_willow.png", "Sable de Sauce Espiritual", "Etapa 03 - Rama Spiritual (anime etereo)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_03_bramble_blade.png", "Hoja de Zarza Sanguina", "Etapa 03 - Rama Cursed (anime zarza)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_04_sunbark_vow.png", "Mandoble del Voto Heliofilo", "Etapa 04 - Rama Blessed (anime sol naciente)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_04_thornheart_hex.png", "Hoja Maldita Corazon de Espina", "Etapa 04 - Rama Cursed (anime hexagonal)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_04_fulgurite_crest.png", "Espada Cresta de Fulgurita", "Etapa 04 - Rama Elemental (anime vid relampago)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_04_jade_anima.png", "Katana Anima de Jade", "Etapa 04 - Rama Spiritual (anime katana)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_04_runebark_codex.png", "Espada Codice de Corteza Runica", "Etapa 04 - Rama Arcane (anime grimorio)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_05_solar_initiate.png", "Espada Iniciada del Sol Naciente", "Etapa 05 - Rama Blessed (anime initado solar)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_05_obsidian_fang.png", "Espada Colmillo de Obsidiana", "Etapa 05 - Rama Cursed (anime colmillo vidrio)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_05_copper_tempest.png", "Espada Cobriza de Tempestad", "Etapa 05 - Rama Elemental (anime ciclon cobre)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_05_silver_anima.png", "Sable de Plata Anima", "Etapa 05 - Rama Spiritual (anime sable plata)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_05_crystal_cipher.png", "Espada Cifrada de Cristal", "Etapa 05 - Rama Arcane (anime prisma cifrado)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_06_auric_bastion.png", "Claymore Bastion Aurico", "Etapa 06 - Rama Blessed (anime fortaleza)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_06_crimson_reaver.png", "Hendidora Segadora Carmesi", "Etapa 06 - Rama Cursed (anime segador)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_06_glacier_fang.png", "Espada Larga Colmillo de Glaciar", "Etapa 06 - Rama Elemental (anime glaciar)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_06_mistwalker_bamboo.png", "Katana Caminante de la Niebla", "Etapa 06 - Rama Spiritual (anime bambu)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_06_astrolabe_ring.png", "Hoja Anillo de Astrolabio", "Etapa 06 - Rama Arcane (anime astrolabio)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_07_seraph_wing.png", "Espada Larga Ala de Serafin", "Etapa 07 - Rama Blessed (anime serafin)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_07_nightmare_chitin.png", "Espada Quitina de Pesadilla", "Etapa 07 - Rama Cursed (anime quitina)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_07_magma_vein.png", "Espada Ancha Vena de Magma", "Etapa 07 - Rama Elemental (anime magma)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_07_moonlit_lotus.png", "Hoja Loto de Plenilunio", "Etapa 07 - Rama Spiritual (anime loto)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_07_aether_conduit.png", "Estoque Conducto de Eter", "Etapa 07 - Rama Arcane (anime eter)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_radiant_covenant.png", "Mandoble de la Alianza Radiante", "Etapa 08 - Rama Blessed (anime alianza)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_bloodmoon_pact.png", "Mandoble del Pacto Luna Sangrienta", "Etapa 08 - Rama Cursed (anime luna roja)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_thunderlord_fulgur.png", "Filo Fulgur del Senor del Trueno", "Etapa 08 - Rama Elemental (anime tridente)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_ancestral_chorus.png", "Espada Coro de los Ancestros", "Etapa 08 - Rama Spiritual (anime coro)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_grimoire_monolith.png", "Mandoble Monolito de Grimorio", "Etapa 08 - Rama Arcane (anime monolito)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_08_twilight_covenant.png", "Espada Hibrida del Pacto Crepuscular", "Etapa 08 - HIBRIDA SECRETA luz/sombra", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_09_dawnbreaker_templar.png", "Hoja Templaria Rompealbas", "Etapa 09 - Era III blessed (anime amanecer)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_09_abyssal_guillotine.png", "Filo Guillotina del Abismo", "Etapa 09 - Era III cursed (anime verdugo)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_09_twin_monsoon.png", "Sable Gemelo del Monzon", "Etapa 09 - Era III elemental (anime doble hoja)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_09_phantom_nodachi.png", "Nodachi Cortafantasmas", "Etapa 09 - Era III spiritual (anime nodachi)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_09_spellweaver_prism.png", "Filo Prisma Tejehechizos", "Etapa 09 - Era III arcane (anime prisma)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_10_halcyon_aegis.png", "Espada Ancha Egida Alcion", "Etapa 10 - Era III blessed (anime egida)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_10_soul_devourer.png", "Blandon Devorador de Almas", "Etapa 10 - Era III cursed (anime boca)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_10_permafrost_prism.png", "Claymore Prisma de Permafrost", "Etapa 10 - Era III elemental (anime hielo)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_10_jade_chakram.png", "Espada-Alma de Jade y Chakram", "Etapa 10 - Era III spiritual (anime chakram)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_10_chronoglass_paradox.png", "Sable Paradoja de Cronocristal", "Etapa 10 - Era III arcane (anime tiempo)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_11_solstice_relic.png", "Reliquia Solar del Solsticio", "Etapa 11 - Era III blessed (anime disco solar)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_11_malakor_thorn.png", "Espina Usurpadora de Malakor", "Etapa 11 - Era III cursed (anime espinas)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_11_pyroclasm_heart.png", "Mandoble Corazon Piroclastico", "Etapa 11 - Era III elemental (anime magma)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_11_saint_reincarnated.png", "Filo del Santo Reencarnado", "Etapa 11 - Era III spiritual (anime santo)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_11_starlight_glyph.png", "Claymore Glifo de Luz Estelar", "Etapa 11 - Era III arcane (anime constelacion)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_archangel_verdict.png", "Claymore Veredicto de Arcangel", "Etapa 12 - Era IV blessed (anime catedral)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_hellfire_executioner.png", "Hoja Verdugo de Fuego Infernal", "Etapa 12 - Era IV cursed (anime fuego)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_maelstrom_triad.png", "Hoja Triada del Maelstrom", "Etapa 12 - Era IV elemental (anime triada)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_nirvana_mirror.png", "Katana Espejo del Nirvana", "Etapa 12 - Era IV spiritual (anime zen)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_archmage_singularity.png", "Hoja Singularidad de Archimago", "Etapa 12 - Era IV arcane (anime singularidad)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_12_stormspirit_dragon.png", "Katana Secreta Dragon de Tormenta", "Etapa 12 - HIBRIDA SECRETA dragon-tormenta", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_13_empyrean_halo.png", "Hoja Trascendente del Halo Empireo", "Etapa 13 - Era IV blessed (anime halos)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_13_voidscar.png", "Espada Cicatriz del Vacio", "Etapa 13 - Era IV cursed (anime cicatriz)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_13_aurora_polar.png", "Espada de Aurora Polar", "Etapa 13 - Era IV elemental (anime aurora)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_13_worldtree.png", "Rama del Arbol Mundo", "Etapa 13 - Era IV spiritual (anime arbol)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_13_axiom.png", "Espada del Axioma", "Etapa 13 - Era IV arcane (anime axioma)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_14_sunforge.png", "Espada Forjasol Santificada", "Etapa 14 - Era IV blessed (anime forja solar)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_14_leviathan_fang.png", "Colmillo Aterrador de Leviatan", "Etapa 14 - Era IV cursed (anime colmillo abisal)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_14_tectonic_breaker.png", "Quebrantamantos Tectonico", "Etapa 14 - Era IV elemental (anime falla de lava)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_14_astral_wind.png", "Espada Viento Astral", "Etapa 14 - Era IV spiritual (anime viento alado)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_14_tesseract.png", "Filo Teseracto de Vacio Geometrico", "Etapa 14 - Era IV arcane (anime teseracto 4D)", "BESPOKE GLB + PBR VERIFICADO", CARD_BORDER_OK),
    ("sword_copper_nv5.png", "Espada de Cobre Forjado (legacy)", "Fase legacy - Nv.5 (referencia antigua)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_iron_nv10.png", "Mandoble de Hierro Templado", "Fase legacy - Nv.10 (Equiv. Etapa 03)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_silver_nv15.png", "Hoja de Plata Runica", "Fase legacy - Nv.15 (Equiv. Etapa 05)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_gold_nv20.png", "Claymore de Oro Solar Imperial", "Fase legacy - Nv.20 (Equiv. Etapa 06)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_crystal_nv25.png", "Espada de Cristal Arcano", "Fase legacy - Nv.25 (Equiv. Etapa 07)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_obsidian_nv30.png", "Devoradora de Obsidiana Draconica", "Fase legacy - Nv.30 (Equiv. Etapa 08)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
    ("sword_celestial_nv35.png", "Excalibur Celestial del Vacio Cosmico", "Fase legacy - Nv.35 (Forma Divina)", "SILUETA OBJ PROVISIONAL", CARD_BORDER_TMP),
]

def draw_center(d, cx, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text((cx - w / 2.0, y), text, font=f, fill=fill)

def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_title = font(34, True)
    f_sub = font(16)
    f_name = font(17, True)
    f_phase = font(13)
    f_status = font(12, True)
    f_legend = font(14)
    f_foot = font(13)

    draw_center(d, W / 2, 26, "FORJA DE ALMAS 3D - Catalogo 3D de Espadas", f_title, GOLD)
    draw_center(d, W / 2, 74, "Studio Lexair - Renders neutros Cycles (key/fill/rim, sin glow ni particulas) - 74 modelos: 67 GLB bespoke verificados (Pilot + Etapas 02-14, incl. 2 hibridas secretas) + 7 siluetas OBJ legacy provisionales", f_sub, SUB)

    for i, (fname, name, phase, status, border) in enumerate(CARDS):
        col, row = i % COLS, i // COLS
        x0 = PAD + col * (CELL_W + PAD)
        y0 = TITLE_H + PAD + row * (CELL_H + PAD)

        d.rounded_rectangle([x0, y0, x0 + CELL_W, y0 + CELL_H], radius=14, fill=CARD, outline=border, width=2)

        src = Image.open(os.path.join(IND, fname)).convert("RGB")
        # imagen 800x1000 -> fit en (CELL_W-24, CELL_H-118) manteniendo aspecto
        max_w, max_h = CELL_W - 24, CELL_H - 118
        ratio = min(max_w / src.width, max_h / src.height)
        tw, th = int(src.width * ratio), int(src.height * ratio)
        thumb = src.resize((tw, th), Image.LANCZOS)
        img.paste(thumb, (x0 + (CELL_W - tw) // 2, y0 + 12))

        cx = x0 + CELL_W / 2
        draw_center(d, cx, y0 + CELL_H - 100, name, f_name, TXT)
        draw_center(d, cx, y0 + CELL_H - 72, phase, f_phase, SUB)
        draw_center(d, cx, y0 + CELL_H - 46, "[ " + status + " ]", f_status, border)

    # Leyenda
    ly = TITLE_H + ROWS * (CELL_H + PAD) + PAD // 2 + 6
    d.rounded_rectangle([PAD, ly + 4, PAD + 18, ly + 22], radius=4, outline=CARD_BORDER_OK, width=2)
    d.text((PAD + 28, ly + 5), "GLB bespoke modelado + PBR + Godot verificado", font=f_legend, fill=TXT)
    d.rounded_rectangle([PAD + 560, ly + 4, PAD + 578, ly + 22], radius=4, outline=CARD_BORDER_TMP, width=2)
    d.text((PAD + 588, ly + 5), "Silueta OBJ del proyecto original (reemplazo bespoke pendiente de aprobacion)", font=f_legend, fill=TXT)

    draw_center(d, W / 2, H - FOOT_H + 18, "Regla Studio Lexair: cada espada final tendra geometria propia unica, UVs limpias y 5 mapas PBR - nada de meshes procedurales ni recolores", f_foot, SUB)
    draw_center(d, W / 2, H - FOOT_H + 40, "Las 24 etapas / 118 formas del sistema de evolucion reutilizan estas siluetas como provisional hasta su aprobacion individual", f_foot, SUB)

    img.save(OUT)
    print("SHEET_DONE", OUT, img.size)

main()

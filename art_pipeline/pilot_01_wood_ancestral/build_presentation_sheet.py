"""
Composes the Studio Lexair 3D Technical Presentation Sheet (view_07_presentation_sheet.png)
from the neutral-light Cycles renders of Pilot Sword #01: s01_wood_ancestral.
"""

from PIL import Image, ImageDraw, ImageFont

RENDERS = "/home/user/Espada-Anime-Isekai/art_pipeline/pilot_01_wood_ancestral/renders"
OUT = f"{RENDERS}/view_07_presentation_sheet.png"

W, H = 1920, 1080
sheet = Image.new("RGB", (W, H), (22, 24, 29))
draw = ImageDraw.Draw(sheet)

try:
    f_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 27)
    f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    f_spec = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    f_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
except Exception:
    f_title = f_sub = f_spec = f_lbl = ImageFont.load_default()

# Header bar
draw.rectangle([0, 0, W, 86], fill=(15, 17, 22))
draw.line([0, 86, W, 86], fill=(198, 158, 78), width=2)
draw.text((32, 16), "STUDIO LEXAIR — PILOTO 3D OFICIAL #01: ESPADA DE MADERA ANCESTRAL", fill=(238, 226, 198), font=f_title)
draw.text((32, 54), "ID: wood_origin_ancestral_blade (Etapa 01 - Era I: Despertar)  |  Blender 4.3 -> glTF 2.0 (.glb)  |  5x 1024px PBR Maps  |  Luz Neutra Sin Postproceso", fill=(156, 172, 188), font=f_sub)


def place_card(img_name: str, x: int, y: int, w: int, h: int, label: str, cover_fill: bool = True):
    draw.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], outline=(68, 76, 88), width=2)
    im = Image.open(f"{RENDERS}/{img_name}").convert("RGB")
    avail_h = h - 28
    im_ratio = im.width / im.height
    box_ratio = w / avail_h
    if cover_fill:
        # Scale to fill height cleanly, center-cropping excess horizontal margin so the sword fills the tall panel!
        nh = avail_h
        nw = int(nh * im_ratio)
        im_r = im.resize((nw, nh), Image.Resampling.LANCZOS)
        if nw >= w:
            left = (nw - w) // 2
            im_c = im_r.crop((left, 0, left + w, nh))
            sheet.paste(im_c, (x, y))
        else:
            bg = Image.new("RGB", (w, avail_h), im.getpixel((4, 4)))
            bg.paste(im_r, ((w - nw) // 2, 0))
            sheet.paste(bg, (x, y))
    else:
        if im_ratio > box_ratio:
            nw, nh = w, int(w / im_ratio)
        else:
            nh, nw = avail_h, int(avail_h * im_ratio)
        im_r = im.resize((nw, nh), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (w, avail_h), im.getpixel((4, 4)))
        bg.paste(im_r, ((w - nw) // 2, (avail_h - nh) // 2))
        sheet.paste(bg, (x, y))

    draw.rectangle([x, y + h - 28, x + w, y + h], fill=(15, 17, 22))
    draw.text((x + 10, y + h - 22), label, fill=(224, 212, 182), font=f_lbl)


y0 = 108
ch = 940
place_card("view_01_front_neutral.png",         28,   y0, 250, ch, "1. FRONTAL (LUZ NEUTRA)", cover_fill=True)
place_card("view_02_side_neutral.png",          294,  y0, 200, ch, "2. PERFIL LATERAL", cover_fill=True)
place_card("view_03_back_neutral.png",          510,  y0, 250, ch, "3. TRASERA", cover_fill=True)
place_card("view_04_three_quarter_neutral.png", 776,  y0, 310, ch, "4. TRES CUARTOS (3/4)", cover_fill=True)
place_card("view_06_silhouette_check.png",     1102,  y0, 245, ch, "5. SILUETA PURA", cover_fill=True)

# Right column: 2 close-ups + technical spec summary box
place_card("view_05a_closeup_hilt_core.png",   1366, y0,       526, 360, "6A. DETALLE GUARDA RAIZ, BRONCE Y SEMILLA", cover_fill=False)
place_card("view_05b_closeup_blade_runes.png", 1366, y0 + 376, 526, 340, "6B. DETALLE BISELES MADERA Y RUNAS TALLADAS", cover_fill=False)

# Spec card bottom-right
sx, sy, sw, sh = 1366, y0 + 732, 526, 208
draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(17, 20, 26), outline=(198, 158, 78), width=1)
specs = [
    "FICHA TECNICA VERIFICADA (PILOTO #01)",
    "- Sub-piezas reales: 7 (Hoja, Nucleo, Runas, Guarda, Virola, Grip, Pomo)",
    "- Geometria: 6,264 tris / 3,278 verts (Biseles reales + UVs limpias)",
    "- Escala mundo: 2.60 m alto total (-0.58 m pomo a +2.02 m punta +Y)",
    "- Mapas PBR (1024px): BaseColor, Roughness, Metallic, Normal, Emission",
    "- Fuentes: sword_01_wood_ancestral.blend + .glb importado en Godot 4.4",
]
for idx, line in enumerate(specs):
    col = (238, 212, 142) if idx == 0 else (196, 206, 218)
    fn = f_lbl if idx == 0 else f_spec
    draw.text((sx + 14, sy + 13 + idx * 31), line, fill=col, font=fn)

sheet.save(OUT, optimize=True)
print("Updated Studio Lexair Presentation Sheet:", OUT)

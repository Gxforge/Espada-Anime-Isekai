# -*- coding: utf-8 -*-
"""
Studio Lexair - Etapa 02: renders de revision neutros (Cycles CPU).
5 vistas iluminadas (frontal/lateral/trasera/3-4/detalle) + 1 silueta por espada.
Camara con look-at explicito por base (determinista) + auto-fit por vertices.

Uso: blender --background --python render_stage02_swords.py -- sword=amber|ironwood|willow|bramble|all
"""
import bpy
import math
import os
import sys
from mathutils import Vector, Matrix

REPO = "/home/user/Espada-Anime-Isekai"
OUT_ROOT = os.path.join(REPO, "art_pipeline", "stage03_swords")

SWORDS = {
    "amber": {
        "glb": os.path.join(REPO, "godot_project", "assets", "models", "swords", "amber_sanctuary", "sword_03_amber_sanctuary.glb"),
        "renders": os.path.join(OUT_ROOT, "amber_sanctuary", "renders"),
    },
    "ironwood": {
        "glb": os.path.join(REPO, "godot_project", "assets", "models", "swords", "ironwood_storm", "sword_03_ironwood_storm.glb"),
        "renders": os.path.join(OUT_ROOT, "ironwood_storm", "renders"),
    },
    "willow": {
        "glb": os.path.join(REPO, "godot_project", "assets", "models", "swords", "spirit_willow", "sword_03_spirit_willow.glb"),
        "renders": os.path.join(OUT_ROOT, "spirit_willow", "renders"),
    },
    "bramble": {
        "glb": os.path.join(REPO, "godot_project", "assets", "models", "swords", "bloodsap_bramble", "sword_03_bramble_blade.glb"),
        "renders": os.path.join(OUT_ROOT, "bloodsap_bramble", "renders"),
    },
}

VIEWS = [
    ("view_01_front", 0.0, 8.0, None, 50.0, 0.0),
    ("view_02_side", 90.0, 8.0, None, 50.0, 0.0),
    ("view_03_back", 180.0, 8.0, None, 50.0, 0.0),
    ("view_04_three_quarters", 38.0, 12.0, None, 50.0, 0.0),
    ("view_05_detail_upper", 30.0, 18.0, 0.62, 85.0, 1.55),
    ("view_06_silhouette", 38.0, 12.0, None, 50.0, 0.0),
]


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def vertex_bbox(objs):
    mins = Vector((1e9,) * 3); maxs = Vector((-1e9,) * 3)
    for o in objs:
        mw = o.matrix_world
        for v in o.data.vertices:
            wc = mw @ v.co
            mins = Vector(map(min, mins, wc)); maxs = Vector(map(max, maxs, wc))
    return mins, maxs


def add_area_light(name, loc, rot_deg, energy, size):
    ld = bpy.data.lights.new(name, type="AREA")
    ld.energy = energy; ld.size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.rotation_euler = [math.radians(a) for a in rot_deg]
    bpy.context.collection.objects.link(lo)


def setup_world(bg_strength_col):
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (bg_strength_col[0], bg_strength_col[1], bg_strength_col[2], 1.0)
    bg.inputs[1].default_value = bg_strength_col[3]


def setup_scene(res_x, res_y):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = False
    for vl in sc.view_layers:
        vl.cycles.use_denoising = False
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.image_settings.file_format = "PNG"


def render_views(sword_key, glb_path, renders_dir):
    os.makedirs(renders_dir, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=glb_path)
    mesh_objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    print("IMPORTED %s: %d meshes" % (sword_key, len(mesh_objs)))
    bpy.context.view_layer.update()

    mins, maxs = vertex_bbox(mesh_objs)
    ext = maxs - mins
    axes = {0: ext.x, 1: ext.y, 2: ext.z}
    long_axis = max(axes, key=axes.get)
    s = 2.6 / max(1e-4, axes[long_axis])

    root = bpy.data.objects.new("RenderRoot", None)
    bpy.context.collection.objects.link(root)
    allsel = set(bpy.context.selected_objects)
    tops = [o for o in allsel if o.parent is None or o.parent not in allsel]
    if long_axis == 2:
        root.rotation_euler = (math.radians(-90), 0, 0)
    elif long_axis == 0:
        root.rotation_euler = (0, 0, math.radians(-90))
    for o in tops:
        o.parent = root
    root.scale = (s, s, s)
    bpy.context.view_layer.update()

    fmins, fmaxs = vertex_bbox(mesh_objs)
    cx = (fmins.x + fmaxs.x) * 0.5; cz = (fmins.z + fmaxs.z) * 0.5
    root.location = Vector((-cx, -fmins.y, -cz))
    bpy.context.view_layer.update()
    fmins, fmaxs = vertex_bbox(mesh_objs)
    center = (fmins + fmaxs) * 0.5
    half_h = (fmaxs.y - fmins.y) * 0.5

    for (vname, az_deg, el_deg, zoom_scale, lens, target_lift) in VIEWS:
        for o in list(bpy.data.objects):
            if o.type == "LIGHT" or o.type == "CAMERA":
                bpy.data.objects.remove(o, do_unlink=True)

        silhouette = "silhouette" in vname
        if silhouette:
            setup_world((0.92, 0.94, 0.96, 1.0))
            key_e = fill_e = rim_e = 0.0
        else:
            setup_world((0.16, 0.17, 0.19, 0.85))
            key_e, fill_e, rim_e = 165.0, 85.0, 105.0

        az, el = math.radians(az_deg), math.radians(el_deg)
        tgt = center + Vector((0.0, target_lift, 0.0))
        half = half_h * (zoom_scale if zoom_scale else 1.0)
        lens_v = lens if zoom_scale else lens
        tan_half = 18.0 / lens_v
        dist = (half + 0.24) / tan_half
        cd = bpy.data.cameras.new("Cam")
        cd.lens = lens_v
        cd.sensor_fit = "VERTICAL"
        cd.sensor_height = 36.0
        cd.clip_start = 0.02; cd.clip_end = 100.0
        co = bpy.data.objects.new("Cam", cd)
        horiz = math.cos(el) * dist
        co.location = tgt + Vector((math.sin(az) * horiz, math.sin(el) * dist, math.cos(az) * horiz))
        bpy.context.collection.objects.link(co)
        fwd = (tgt - co.location).normalized()
        up_w = Vector((0.0, 1.0, 0.0))
        right = fwd.cross(up_w).normalized()
        true_up = right.cross(fwd).normalized()
        cam_mat = Matrix(((right.x, true_up.x, -fwd.x), (right.y, true_up.y, -fwd.y), (right.z, true_up.z, -fwd.z)))
        co.rotation_euler = cam_mat.to_euler()
        bpy.context.scene.camera = co

        add_area_light("Key", (2.3, -2.6, 2.0), (58, 0, 36), key_e, 2.4)
        add_area_light("Fill", (-2.6, -2.0, 1.0), (72, 0, -48), fill_e, 2.8)
        add_area_light("Rim", (-0.5, 2.5, 1.7), (-62, 0, 168), rim_e, 2.2)

        setup_scene(800, 1000)
        bpy.context.scene.render.filepath = os.path.join(renders_dir, "%s.png" % vname)
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sword_key, vname)
    print("SWORD_VIEWS_DONE", sword_key)


def main():
    argv = sys.argv
    which = "all"
    if "--" in argv:
        for a in argv[argv.index("--") + 1:]:
            if a.startswith("sword="):
                which = a.split("=", 1)[1]
    keys = list(SWORDS.keys()) if which == "all" else [which]
    for k in keys:
        m = SWORDS[k]
        render_views(k, m["glb"], m["renders"])
    print("STAGE03_RENDER_DONE")


main()

# -*- coding: utf-8 -*-
"""
Studio Lexair — Galeria de Catalogo 3D de Espadas (v2, auto-fit de camara)
Renders neutros (Cycles CPU, 48 samples, 3-point neutral light rig) para las
8 espadas existentes en el proyecto:

  1. Pilot #01 Espada de Madera Ancestral  -> GLB bespoke VERIFICADO (PBR real)
  2..8. Fases legacy Nv.5..Nv.35           -> siluetas OBJ provisionales

Correcciones v2:
  - Solo se re-parenta el TOP-LEVEL de la jerarquia importada (no se rompen
    las transformadas anidadas del glTF).
  - Encuadre auto-fit: distancia calculada desde el bbox final real con FOV
    vertical determinista (sensor VERTICAL 36mm, lens 50mm).
Uso:
  blender --background --python render_sword_catalog.py
"""
import bpy
import math
import os
from mathutils import Vector, Matrix

REPO = "/home/user/Espada-Anime-Isekai"
MODELS = os.path.join(REPO, "godot_project", "assets", "models")
OUT = os.path.join(REPO, "art_pipeline", "sword_catalog_renders", "individual")
os.makedirs(OUT, exist_ok=True)

SWORDS = [
    ("wood_ancestral_pilot_glb", os.path.join(MODELS, "swords", "wood_ancestral", "sword_01_wood_ancestral.glb"), "#9c6635", 0.05, 0.55),
    ("copper_nv5", os.path.join(MODELS, "sword_copper_nv5.obj"), "#d97742", 0.75, 0.38),
    ("iron_nv10", os.path.join(MODELS, "sword_iron_nv10.obj"), "#94a3b8", 0.72, 0.36),
    ("silver_nv15", os.path.join(MODELS, "sword_silver_nv15.obj"), "#cbd5e1", 0.78, 0.30),
    ("gold_nv20", os.path.join(MODELS, "sword_gold_nv20.obj"), "#facc15", 0.85, 0.28),
    ("crystal_nv25", os.path.join(MODELS, "sword_crystal_nv25.obj"), "#c084fc", 0.35, 0.22),
    ("obsidian_nv30", os.path.join(MODELS, "sword_obsidian_nv30.obj"), "#3a2b4d", 0.42, 0.34),
    ("celestial_nv35", os.path.join(MODELS, "sword_celestial_nv35.obj"), "#38bdf8", 0.60, 0.26),
]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.lights, bpy.data.cameras):
        for x in list(block):
            if x.users == 0:
                block.remove(x)

def setup_world():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is None:
        bg = world.node_tree.nodes.new("ShaderNodeBackground")
        world.node_tree.links.new(bg.outputs[0], world.node_tree.nodes["World Output"].inputs[0])
    bg.inputs[0].default_value = (0.16, 0.17, 0.19, 1.0)
    bg.inputs[1].default_value = 0.85

def add_area_light(name, loc, rot_deg, energy, size, col=(1.0, 0.99, 0.97)):
    ld = bpy.data.lights.new(name, type="AREA")
    ld.energy = energy
    ld.size = size
    ld.color = col
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.rotation_euler = [math.radians(a) for a in rot_deg]
    bpy.context.collection.objects.link(lo)
    return lo

def world_bbox(objs):
    # Vertex-based bbox: bound_box can be stale right after import/parenting,
    # this is fully deterministic for both OBJ and glTF hierarchies.
    mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        mw = o.matrix_world
        for v in o.data.vertices:
            wc = mw @ v.co
            mins = Vector(map(min, mins, wc)); maxs = Vector(map(max, maxs, wc))
    return mins, maxs

def make_material(name, hexcol, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    rgb = hex_to_rgb(hexcol)
    bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

def assign_flat(objs, mat):
    for o in objs:
        if o.material_slots:
            for slot in o.material_slots:
                slot.material = mat
        else:
            o.data.materials.append(mat)

def normalize_and_frame(sword_id, path, hexcol, metallic, roughness):
    mesh_objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if path.endswith(".obj"):
        assign_flat(mesh_objs, make_material("flat_%s" % sword_id, hexcol, metallic, roughness))

    mins, maxs = world_bbox(mesh_objs)
    ext = maxs - mins
    # Detect the blade's LONG axis (Blender is Z-up: glTF/OBJ Y-up imports lie along +Z)
    axes = {0: ext.x, 1: ext.y, 2: ext.z}
    long_axis = max(axes, key=axes.get)
    length = max(axes[long_axis], 1e-4)
    s = 2.6 / length

    root = bpy.data.objects.new("CatalogRoot", None)
    bpy.context.collection.objects.link(root)
    if long_axis == 2:      # +Z (Blender Z-up import, tip at +Z) -> stand on +Y with tip UP
        root.rotation_euler = (math.radians(-90), 0, 0)
    elif long_axis == 0:    # +X -> rotate to +Y
        root.rotation_euler = (0, 0, math.radians(-90))
    else:                   # already +Y
        root.rotation_euler = (0, 0, 0)
    all_objs = set(bpy.context.selected_objects)
    parents = [o for o in all_objs if o.parent is None or o.parent not in all_objs]
    for o in parents:
        o.parent = root
    root.scale = (s, s, s)
    bpy.context.view_layer.update()

    fmins, fmaxs = world_bbox(mesh_objs)
    center_xz = ((fmins.x + fmaxs.x) * 0.5, (fmins.z + fmaxs.z) * 0.5)
    root.location = Vector((-center_xz[0], -fmins.y, -center_xz[1]))
    bpy.context.view_layer.update()

    # bbox final real tras la normalizacion
    fmins, fmaxs = world_bbox(mesh_objs)
    center = (fmins + fmaxs) * 0.5
    half_h = (fmaxs.y - fmins.y) * 0.5

    # Camara 3/4: azimut 38 deg, elevacion ~12 deg, auto-fit con FOV vertical determinista
    az = math.radians(38)
    el = math.radians(12)
    lens = 50.0
    cd = bpy.data.cameras.new("ReviewCam")
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 36.0
    tan_half = 18.0 / lens
    dist = (half_h + 0.22) / tan_half
    print("  FIT %s: axis=%d ext=(%.3f, %.3f, %.3f) scale=%.4f half_h=%.3f dist=%.3f center=(%.2f, %.2f, %.2f)" % (sword_id, long_axis, ext.x, ext.y, ext.z, s, half_h, dist, center.x, center.y, center.z))
    cd.clip_start = 0.05
    cd.clip_end = 100.0
    co = bpy.data.objects.new("ReviewCam", cd)
    horiz = math.cos(el) * dist
    co.location = center + Vector((math.sin(az) * horiz, math.sin(el) * dist, math.cos(az) * horiz))
    bpy.context.collection.objects.link(co)
    # Look-at EXPLICITO determinista (construido por basis): to_track_quat elige
    # una rama rodada para direcciones diagonales y deja la espada en diagonal.
    fwd = (center - co.location).normalized()
    up_w = Vector((0.0, 1.0, 0.0))
    right = fwd.cross(up_w).normalized()
    true_up = right.cross(fwd).normalized()
    cam_matrix = Matrix((
        (right.x, true_up.x, -fwd.x),
        (right.y, true_up.y, -fwd.y),
        (right.z, true_up.z, -fwd.z),
    ))
    co.rotation_euler = cam_matrix.to_euler()

    add_area_light("KeyLight", (2.3, -2.6, 2.0), (58, 0, 36), 165.0, 2.4)
    add_area_light("FillLight", (-2.6, -2.0, 1.0), (72, 0, -48), 85.0, 2.8)
    add_area_light("RimLight", (-0.5, 2.5, 1.7), (-62, 0, 168), 105.0, 2.2)

    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = False
    # Debian builds lack OpenImageDenoise: force-disable at every view layer too
    for vl in sc.view_layers:
        vl.cycles.use_denoising = False
    sc.render.resolution_x = 800
    sc.render.resolution_y = 1000
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(OUT, "sword_%s.png" % sword_id)
    bpy.context.scene.camera = co
    bpy.ops.render.render(write_still=True)

def main():
    setup_world()
    for sword_id, path, hexcol, metallic, roughness in SWORDS:
        clear_scene()
        if path.endswith(".glb"):
            bpy.ops.import_scene.gltf(filepath=path)
        else:
            bpy.ops.wm.obj_import(filepath=path)
        print("RENDER:", sword_id, "selected:", len(bpy.context.selected_objects))
        normalize_and_frame(sword_id, path, hexcol, metallic, roughness)
    print("GALLERY_INDIVIDUAL_DONE")

main()

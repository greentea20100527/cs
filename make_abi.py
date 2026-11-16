import math
import os

import bpy
from mathutils import Vector


def material(name, color, roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    return mat


def uv_sphere(name, location, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    return obj


def cylinder(name, location, radius, depth, mat, vertices=48, bevel=0.06):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def curve_object(name, points, bevel_depth, mat, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 4
    curve.resolution_u = 16
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def point_camera(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat(
        "-Z", "Y"
    ).to_euler()


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)

skin = material("Warm porcelain skin", (0.91, 0.68, 0.53))
hair = material("Deep forest hair", (0.035, 0.16, 0.105), 0.32)
hair_light = material("Jade hair accents", (0.12, 0.38, 0.22), 0.34)
white = material("Ivory coat", (0.88, 0.91, 0.83), 0.78)
green = material("Evergreen fabric", (0.06, 0.23, 0.15), 0.72)
gold = material("Antique gold", (0.72, 0.48, 0.16), 0.3, 0.55)
eye_white = material("Eye ivory", (0.96, 0.94, 0.87), 0.3)
iris = material("Jade eyes", (0.05, 0.34, 0.22), 0.24)
black = material("Pupils", (0.018, 0.028, 0.023), 0.2)
shoe_mat = material("Dark leather", (0.09, 0.12, 0.1), 0.4)
stage_mat = material("Warm studio floor", (0.22, 0.27, 0.23), 0.85)

# Shoes, legs, and a narrow belt establish the full-body silhouette.
for side in (-1, 1):
    uv_sphere("Polished boot", (side * 0.29, -0.07, 0.29), (0.26, 0.42, 0.2), shoe_mat)
    uv_sphere("Ivory boot cuff", (side * 0.29, -0.04, 0.54), (0.2, 0.22, 0.16), white)
    uv_sphere("Tapered trouser leg", (side * 0.27, 0.01, 1.35), (0.23, 0.28, 0.88), green)
    uv_sphere("Trouser seam", (side * 0.27, -0.268, 1.3), (0.018, 0.018, 0.68), gold, 16, 12)

uv_sphere("Long ivory coat", (0, 0.02, 3.55), (0.77, 0.42, 1.45), white)
uv_sphere("Evergreen waistcoat", (0, -0.33, 3.92), (0.43, 0.12, 0.98), green)
cylinder("Waist belt", (0, -0.02, 2.95), 0.56, 0.12, gold)
uv_sphere("Belt clasp", (0, -0.58, 2.96), (0.12, 0.06, 0.11), gold)

# Coat lapels, buttons, and leaf-shaped insignia.
for side in (-1, 1):
    curve_object(
        "Tailored lapel",
        [
            (side * 0.12, -0.45, 4.95),
            (side * 0.33, -0.51, 4.54),
            (side * 0.19, -0.46, 4.15),
            (side * 0.32, -0.42, 3.55),
        ],
        0.045,
        gold,
    )
    for z in (4.0, 3.72, 3.44):
        uv_sphere("Gold coat button", (side * 0.13, -0.45, z), (0.055, 0.035, 0.055), gold, 20, 12)
    uv_sphere("Shoulder mantle", (side * 0.73, 0, 4.8), (0.36, 0.46, 0.23), green)

# Arms are built from overlapping smooth forms, with cuffs and relaxed hands.
for side in (-1, 1):
    upper = uv_sphere("Ivory sleeve", (side * 0.88, 0.0, 4.18), (0.27, 0.31, 0.72), white)
    upper.rotation_euler[1] = side * math.radians(-12)
    forearm = uv_sphere("Sleeve forearm", (side * 1.03, -0.03, 3.48), (0.22, 0.25, 0.55), white)
    forearm.rotation_euler[1] = side * math.radians(-8)
    uv_sphere("Green cuff", (side * 1.09, -0.03, 3.04), (0.24, 0.27, 0.12), green)
    uv_sphere("Hand", (side * 1.11, -0.05, 2.83), (0.15, 0.16, 0.22), skin)
    uv_sphere("Cuff clasp", (side * 1.09, -0.28, 3.05), (0.07, 0.035, 0.07), gold, 20, 12)

# Neck and stylized face.
uv_sphere("Neck", (0, -0.01, 5.42), (0.28, 0.27, 0.38), skin)
uv_sphere("Face", (0, -0.015, 6.25), (0.67, 0.57, 0.91), skin, 48, 32)
for side in (-1, 1):
    uv_sphere("Ear", (side * 0.65, -0.02, 6.22), (0.15, 0.13, 0.22), skin)
    uv_sphere("Ear detail", (side * 0.69, -0.14, 6.22), (0.055, 0.025, 0.1), gold, 20, 12)
    uv_sphere("Eye white", (side * 0.255, -0.535, 6.32), (0.16, 0.075, 0.21), eye_white)
    uv_sphere("Jade iris", (side * 0.245, -0.602, 6.31), (0.085, 0.038, 0.13), iris)
    uv_sphere("Pupil", (side * 0.24, -0.635, 6.30), (0.043, 0.024, 0.085), black)
    uv_sphere("Eye glint", (side * 0.265, -0.656, 6.36), (0.024, 0.016, 0.033), eye_white, 16, 10)
    curve_object(
        "Expressive eyebrow",
        [(side * 0.12, -0.59, 6.59), (side * 0.27, -0.61, 6.64), (side * 0.40, -0.57, 6.59)],
        0.035,
        hair,
    )

curve_object("Small nose", [(0, -0.58, 6.25), (0.025, -0.65, 6.16)], 0.025, skin)
curve_object(
    "Gentle smile",
    [(-0.09, -0.585, 6.03), (0, -0.615, 6.01), (0.09, -0.585, 6.03)],
    0.018,
    shoe_mat,
)

# Swept-back hair cap, side locks, and curved fringe.
uv_sphere("Hair cap", (0, 0.035, 6.92), (0.72, 0.62, 0.55), hair, 48, 28)
for side in (-1, 1):
    lock = uv_sphere("Long side lock", (side * 0.57, -0.01, 6.05), (0.19, 0.23, 0.83), hair)
    lock.rotation_euler[1] = side * math.radians(-8)
    curve_object(
        "Hair highlight",
        [(side * 0.63, -0.22, 6.68), (side * 0.68, -0.245, 6.18), (side * 0.59, -0.22, 5.63)],
        0.025,
        hair_light,
    )
for side, offset in ((-1, -0.07), (1, 0.07), (-1, 0.23), (1, -0.23)):
    curve_object(
        "Sculpted fringe",
        [
            (offset, -0.39, 7.18),
            (offset + side * 0.18, -0.52, 6.89),
            (offset + side * 0.12, -0.55, 6.56),
        ],
        0.13 if abs(offset) < 0.1 else 0.105,
        hair,
    )

# A small botanical ornament makes the character recognizable from a distance.
uv_sphere("Leaf brooch center", (0.52, -0.51, 4.74), (0.11, 0.055, 0.11), gold, 24, 16)
curve_object(
    "Leaf brooch stem",
    [(0.52, -0.57, 4.72), (0.57, -0.59, 4.87), (0.67, -0.53, 5.02)],
    0.025,
    green,
)
leaf_a = uv_sphere("Brooch leaf", (0.43, -0.54, 4.91), (0.17, 0.055, 0.085), hair_light)
leaf_a.rotation_euler[1] = math.radians(-35)
leaf_b = uv_sphere("Brooch leaf", (0.67, -0.53, 5.02), (0.16, 0.055, 0.08), hair_light)
leaf_b.rotation_euler[1] = math.radians(35)

# Simple presentation pedestal and studio.
cylinder("Character pedestal", (0, 0, -0.1), 0.86, 0.22, green)
cylinder("Pedestal gold rim", (0, 0, -0.22), 0.88, 0.055, gold)
cylinder("Pedestal foot", (0, 0, -0.31), 0.74, 0.12, shoe_mat)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.38))
floor = bpy.context.object
floor.name = "Studio floor"
floor.data.materials.append(stage_mat)

world = bpy.context.scene.world
world.color = (0.16, 0.16, 0.16)
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.18, 0.23, 0.2, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 900
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
def area_light(name, location, energy, size, color, target):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.data.color = color
    point_camera(light, target)


area_light("Large softbox", (4, -8, 10), 1050, 6, (1.0, 0.84, 0.68), (0, 0, 4))
area_light("Cool fill", (-6, -4, 6), 800, 5, (0.65, 0.82, 1.0), (0, 0, 4))
area_light("Jade rim light", (2, 4, 8), 1250, 4, (0.65, 1.0, 0.76), (0, 0, 4))

bpy.ops.object.camera_add(location=(8.5, -17, 8.2))
camera = bpy.context.object
camera.name = "Portrait camera"
camera.data.type = "ORTHO"
camera.data.ortho_scale = 8.8
point_camera(camera, (0, 0, 3.65))
scene.camera = camera

# Leave the character selected and save a ready-to-render Blender project.
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.context.scene.objects:
    if obj.name in {"Face", "Hair cap", "Long ivory coat"}:
        obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects.get("Face")
scene.render.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "A-Bi_2778.png")
output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "A-Bi_2778.blend")
bpy.ops.wm.save_as_mainfile(filepath=output)
bpy.ops.render.render(write_still=True)
print("Saved Blender model:", output)

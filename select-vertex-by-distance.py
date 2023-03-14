import bpy
import math

# useful to work with meshes that were edge split
# (ripped from game engines)
# basically works like 'select linked'
# but selects vertices that are not actually linked
# and only linked visually (are on the same coordinates)

THRESHOLD = 0.0001

obj = bpy.context.active_object
mesh = obj.data

def get_selected_verts():
    return [v for v in mesh.vertices if v.select]

def distance(t1, t2):
    x1, y1, z1 = t1
    x2, y2, z2 = t2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    return distance

prev_selected_amount = len(get_selected_verts())

while True:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for v in get_selected_verts():
        for va in mesh.vertices:
            if va.select:
                continue
            if distance(v.co, va.co) > THRESHOLD:
                continue
            va.select = True

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_linked()

    bpy.context.view_layer.update()

    if prev_selected_amount == len(get_selected_verts()):
        break
    prev_selected_amount = len(get_selected_verts())

bpy.ops.object.mode_set(mode = 'EDIT')
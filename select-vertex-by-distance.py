import bpy

# useful to work with meshes that were edge split
# (ripped from game engines)
# basically works like 'select linked'
# but selects vertices that are not actually linked
# and only linked visually (are on the same coordinates)

import time

start = time.time()

THRESHOLD = 0.0001

obj = bpy.context.active_object
mesh = obj.data

def get_selected_verts():
    return [v for v in mesh.vertices if v.select]

def distance(v1, v2):
    return (v2 - v1).length

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

end = time.time()
print(format(end - start, '.3f') + 's')
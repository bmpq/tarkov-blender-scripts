# useful to work with meshes that were edge split
# (ripped from game engines)
# basically works like 'select linked'
# but selects vertices that are not actually linked
# and only linked visually (are on the same coordinates)

import bpy
import bmesh
from mathutils import kdtree

THRESHOLD = 0.0001

obj = bpy.context.active_object
me = obj.data
bm = bmesh.from_edit_mesh(me)

size = len(bm.verts)
kd = kdtree.KDTree(size)
for i, vtx in enumerate(bm.verts):
    kd.insert(vtx.co, i)
kd.balance()

changed = True
# Loop until no more matching vertices are found
while changed:
    changed = False

    for v in bm.verts:
        if not v.select:
            continue

        for e in v.link_edges:
            if not e.select:
                e.select = True
                changed = True

        for (co, index, dist) in kd.find_range(v.co, THRESHOLD):
            if not bm.verts[index].select:
                bm.verts[index].select = True
                changed = True

bm.select_flush(True)
bmesh.update_edit_mesh(me)
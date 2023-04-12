import bpy
import bmesh
from math import pi, atan2
import math

if bpy.context.active_object.mode != 'EDIT':
    raise Exception('not in edit mode')

me = bpy.context.object.data
bm = bmesh.from_edit_mesh(me)

angle_min = math.radians(85)
angle_max = math.radians(95)

for f in bm.faces:
    f.select = False  # Deselect all faces first

def get_connected_faces(face_a):
    for edge in face_a.edges:
        for face_b in edge.link_faces:
            if face_b.select:
                continue
            angle = face_a.normal.angle(face_b.normal)
            if angle < angle_max and angle > angle_min:
                face_b.select = True
                get_connected_faces(face_b)


for f in bm.faces:
    f.select = True
    get_connected_faces(f)
    bmesh.update_edit_mesh(me)

    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
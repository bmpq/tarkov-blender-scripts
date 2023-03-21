from mathutils.bvhtree import BVHTree
import bpy
import bmesh

print(f'working in {bpy.context.collection.name} collection')
col_mesh = bpy.context.collection
if 'overlaps' in col_mesh.name:
    raise Exception("overlap collection selected")

col_empties = None
for col in bpy.data.collections:
    if col.name == (col_mesh.name + '_overlaps'):
        col_empties = col
if col_empties is None:
    col_empties = bpy.data.collections.new(col_mesh.name + '_overlaps')
    col_mesh.children.link(col_empties)
else:
    for ob in col_empties.objects:
        col_empties.objects.unlink(ob)

bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=4)

for ob in col_mesh.objects:
    #is_rigid_body = ob.rigid_body is not None
    #if is_rigid_body:
    #    bpy.context.view_layer.objects.active = ob
    #    bpy.ops.rigidbody.object_remove()
    bpy.context.view_layer.objects.active = ob
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.mass = 10.0


trees = []
for obj in col_mesh.objects:
    mat = obj.matrix_world
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=10)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    tree = BVHTree.FromBMesh(bm)
    trees.append((tree, (obj, bm)))

for i in range(len(trees)):
    for j in range(i + 1, len(trees)):
        tree1, (obj1, bm1) = trees[i]
        tree2, (obj2, bm2) = trees[j]
        overlap_pairs = tree1.overlap(tree2)
        if overlap_pairs:
            face1 = bm1.faces[overlap_pairs[0][0]]
            face2 = bm2.faces[overlap_pairs[0][1]]
            loc = (face1.verts[0].co + face2.verts[0].co) / 2
            min_dist = (face1.verts[0].co - face2.verts[0].co).length

            for p1, p2 in overlap_pairs:
                face1 = bm1.faces[p1]
                face2 = bm2.faces[p2]

                for v1 in face1.verts:
                    for v2 in face2.verts:
                        if (v1.co - v2.co).length < min_dist:
                            min_dist = (v1.co - v2.co).length
                            loc = (v1.co + v2.co) / 2

            empty_name = f'{obj1.name}_{obj2.name}'
            empty = bpy.data.objects.new(empty_name, None)
            empty.empty_display_size = 0.2

            empty.location = loc
            col_empties.objects.link(empty)
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            bpy.context.view_layer.objects.active = empty
            empty.select_set(True)
            bpy.ops.rigidbody.constraint_add(type='HINGE')
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            bpy.context.object.rigid_body_constraint.use_breaking = True
            bpy.context.object.rigid_body_constraint.breaking_threshold = 30

            bpy.context.object.rigid_body_constraint.object1 = obj1
            bpy.context.object.rigid_body_constraint.object2 = obj2

            empty.select_set(False)

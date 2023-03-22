import math
import bmesh
import bpy
from mathutils.bvhtree import BVHTree
from bpy.types import Panel, Operator, PropertyGroup

bl_info = {
    "name": "Rigid body structure tool",
    "author": "bmpq",
    "version": (0, 1),
    "location": "View3D > Sidebar > Tools",
    "blender": (3, 0, 0),
    "category": "3D View"
}


class MainPanel(Panel):
    bl_idname = "OBJECT_PT_rbtool_panel"
    bl_label = "Rigd body tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        rbprops = context.scene.rbtool_rbprops
        overlapprops = context.scene.rbtool_overlapprops

        col_selected = context.collection

        if 'overlaps' in col_selected.name:
            layout.label(text='Overlap collection selected')
            return

        mesh_amount = 0
        for ob in context.collection.objects:
            if ob.type == 'MESH':
                mesh_amount += 1

        layout.label(text=f'{mesh_amount} mesh objects in [{col_selected.name}]')

        layout.prop(overlapprops, "input_overlap_margin")
        layout.prop(overlapprops, "input_subd")

        if overlapprops.progress > 0.0 and overlapprops.progress < 1.0:
            layout.label(text=f"Progress: {overlapprops.progress*100:.2f}%")
        else:
            layout.operator("rbtool.button_generate")

        layout.separator()

        layout.prop(rbprops, property="input_rbshape", text="Collision shape")
        layout.operator("rbtool.button_setrb")


class OverlapProps(PropertyGroup):
    input_overlap_margin: bpy.props.FloatProperty(
        name="Overlap margin",
        default=0.0
    )
    input_subd: bpy.props.IntProperty(
        name="Subdivision level",
        min=0,
        max=100,
        default=4
    )
    progress: bpy.props.FloatProperty(
        name="Progress",
        min=0.0,
        max=1.0,
        default=0.0
    )


class RBProps(PropertyGroup):
    rb_shapes = bpy.types.RigidBodyObject.bl_rna.properties["collision_shape"].enum_items
    input_rbshape: bpy.props.EnumProperty(
        items=[(item.identifier, item.name, item.description) for item in rb_shapes]
    )


class SetRigidbodies(Operator):
    bl_idname = "rbtool.button_setrb"
    bl_label = "Set rigid bodies"

    def execute(self, context):
        props = context.scene.rbtool_rbprops

        for ob in context.collection.objects:
            if ob.type != 'MESH':
                continue

            if ob.rigid_body is None:
                bpy.context.view_layer.objects.active = ob
                bpy.ops.rigidbody.object_add()

            ob.rigid_body.mass = 10.0
            ob.rigid_body.collision_shape = props.input_rbshape

        return {'FINISHED'}


def get_bvh(collection, solidify_thickness, subd):
    trees = []
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)

        if not math.isclose(solidify_thickness, 0):
            bmesh.ops.solidify(bm, geom=bm.faces, thickness=solidify_thickness)

        if subd > 0:
            bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subd)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        tree = BVHTree.FromBMesh(bm)
        trees.append((tree, (obj, bm)))

    return trees


def reset_collection(parent_collection):
    col_empties = None
    for col in bpy.data.collections:
        if col.name == (parent_collection.name + '_overlaps'):
            col_empties = col
    if col_empties is None:
        col_empties = bpy.data.collections.new(
            parent_collection.name + '_overlaps')
        parent_collection.children.link(col_empties)
    else:
        for ob in col_empties.objects:
            col_empties.objects.unlink(ob)

    return col_empties


class StructureGenerator(Operator):
    bl_idname = "rbtool.button_generate"
    bl_label = "Generate structure"

    def execute(self, context):
        props = context.scene.rbtool_overlapprops
        collection = context.collection

        context.scene.frame_current = 0
        props.progress = 0.01

        trees = get_bvh(collection, props.input_overlap_margin, props.input_subd)
        col_empties = reset_collection(collection)

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

                    bpy.context.view_layer.objects.active = empty
                    bpy.ops.rigidbody.constraint_add(type='FIXED')

                    bpy.context.object.rigid_body_constraint.disable_collisions = True
                    bpy.context.object.rigid_body_constraint.use_breaking = True
                    bpy.context.object.rigid_body_constraint.breaking_threshold = 50

                    bpy.context.object.rigid_body_constraint.object1 = obj1
                    bpy.context.object.rigid_body_constraint.object2 = obj2

            props.progress = (i + 1) / (len(trees))
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        return {'FINISHED'}


# A list of classes to register and unregister
classes = [
    OverlapProps,
    RBProps,
    SetRigidbodies,
    StructureGenerator,
    MainPanel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rbtool_rbprops = bpy.props.PointerProperty(type=RBProps)
    bpy.types.Scene.rbtool_overlapprops = bpy.props.PointerProperty(type=OverlapProps)


def unregister():
   for cls in reversed(classes):
       bpy.utils.unregister_class(cls)

   del bpy.types.Scene.rbtool_rbprops
   del bpy.types.Scene.rbtool_overlapprops


if __name__ == "__main__":
   register()

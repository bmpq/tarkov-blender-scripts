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
    bl_label = "Rigid body tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        rbprops = context.scene.rbtool_rbprops
        overlapprops = context.scene.rbtool_overlapprops
        constprops = context.scene.rbtool_constprops

        col_selected = context.collection
        col_overlaps = col_selected.children.get(col_selected.name + '_overlaps')
        generated = col_overlaps is not None and len(col_overlaps.objects) > 0

        if col_selected == context.scene.collection:
            layout.label(text='Scene collection selected')
            return

        if 'overlaps' in col_selected.name:
            layout.label(text='Overlap collection selected')
            return

        if 'compound' in col_selected.name:
            layout.label(text='Compound collection selected')
            return

        if generated:
            layout.label(text=f'{len(col_overlaps.objects)} generated constraints')
        layout.prop(constprops, "input_type", text="Constraint type")
        layout.prop(constprops, "input_enable_collisions", text="Enable local collisions")
        layout.prop(constprops, "input_break_threshold", text="Break threshold")
        layout.prop(constprops, "input_show_in_front", text="Show in front")
        if generated:
            layout.operator("rbtool.button_modify_const", icon='RIGID_BODY_CONSTRAINT')

        layout.separator(factor=2)

        mesh_amount = 0

        for ob in context.collection.objects:
            if ob.type == 'MESH':
                mesh_amount += 1

        layout.label(text=f'{mesh_amount} mesh objects in [{col_selected.name}]')

        layout.prop(overlapprops, "input_solidify")
        if overlapprops.input_solidify:
            layout.prop(overlapprops, "input_overlap_margin")
        layout.prop(overlapprops, "input_subd")

        if overlapprops.progress > 0.0 and overlapprops.progress < 1.0:
            layout.label(text=f"Progress: {overlapprops.progress*100:.2f}%")
        else:
            layout.operator("rbtool.button_generate", icon='MOD_MESHDEFORM')

        if len(context.selected_objects) == 0:
            return

        layout.separator(factor=2)

        selected_solidified = False
        mesh_amount = 0
        rb_amount = 0
        rb_shapes = bpy.types.RigidBodyObject.bl_rna.properties["collision_shape"].enum_items
        sh_amount = dict.fromkeys(rb_shapes, 0)
        for ob in context.selected_objects:
            if '_solidified' in ob.name:
                selected_solidified = True
            if ob.type == 'MESH':
                mesh_amount += 1
                rb = ob.rigid_body
                if rb is None:
                    continue
                rb_amount += 1
                for sh in rb_shapes:
                    if sh.identifier == ob.rigid_body.collision_shape:
                        sh_amount[sh] += 1
                        break

        layout.label(text=f'{mesh_amount} mesh selected ({rb_amount} RB)')


        b = layout.box()
        for sh in sh_amount:
            if sh_amount[sh] == 0:
                continue
            r = b.row()
            r.scale_y = 0.7
            c1 = r.column()
            c1.alignment = 'LEFT'
            c1.label(text=f'{sh.name}')

            c2 = r.column()
            c2.alignment = 'RIGHT'
            c2.label(text=f'{sh_amount[sh]}')

        layout.prop(rbprops, property="input_rbshape", text="Collision shape")
        if rbprops.input_rbshape == 'COMPOUND':
            layout.prop(rbprops, "input_compound_scale")
            layout.prop(rbprops, "input_compound_voxel_size")
            layout.prop(rbprops, "input_compound_dm_ratio")

        if rbprops.progress > 0.0 and rbprops.progress < 1.0:
            layout.label(text=f"Progress: {rbprops.progress*100:.2f}%")
        elif selected_solidified:
            layout.label(text=f"Selected a solidified mesh")
        else:
            layout.operator("rbtool.button_setrb", icon='RIGID_BODY')
            layout.operator("rbtool.button_remrb", icon='REMOVE')


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
    input_solidify: bpy.props.BoolProperty(
        name="Overlap margin"
    )
    progress: bpy.props.FloatProperty(
        name="Progress",
        min=0.0,
        max=1.0,
        default=0.0
    )

import sys

class RBProps(PropertyGroup):
    rb_shapes = bpy.types.RigidBodyObject.bl_rna.properties["collision_shape"].enum_items
    input_rbshape: bpy.props.EnumProperty(
        items=[(item.identifier, item.name, item.description) for item in rb_shapes]
    )
    input_compound_scale: bpy.props.FloatVectorProperty(
        name='Scale', subtype='XYZ',
        default=(1.0, 1.0, 1.0),
        min= 0.0,
        max = 2.0
    )
    input_compound_voxel_size: bpy.props.FloatProperty(
        name='Voxel size',
        min=0.01,
        default=0.04
    )
    input_compound_dm_ratio: bpy.props.FloatProperty(
        name='Decimate ratio',
        min=0.0,
        max=1.0,
        default=0.15
    )
    progress: bpy.props.FloatProperty(
        name='Progress',
        default=0
    )


class ConstraintProps(PropertyGroup):
    const_types = bpy.types.RigidBodyConstraint.bl_rna.properties["type"].enum_items
    input_type: bpy.props.EnumProperty(
        items=[(item.identifier, item.name, item.description) for item in const_types]
    )
    input_enable_collisions: bpy.props.BoolProperty(
        name="Enable collisions",
        default=False
    )
    input_break_threshold: bpy.props.FloatProperty(
        name="Break threshold",
        min=0.0,
        max=1000.0,
        default=40
    )
    input_show_in_front: bpy.props.BoolProperty(
        name="Show in front",
        default=True
    )


def distance(point1, point2):
    return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2 + (point2.z - point1.z)**2)

class SetRigidbodies(Operator):
    bl_idname = "rbtool.button_setrb"
    bl_label = "Add/Update rigid bodies"

    def execute(self, context):
        context.scene.frame_current = 0

        props = context.scene.rbtool_rbprops
        cmpnd = props.input_rbshape == 'COMPOUND'

        bpy.ops.outliner.orphans_purge(do_local_ids=True)

        if cmpnd:
            biggest_mesh = 0
            mesh_data = {}
            for ob in context.selected_objects:
                if ob.type != 'MESH':
                    continue

                bm = bmesh.new()
                bm.from_mesh(ob.data)

                if len(bm.verts) == 0:
                    context.collection.objects.unlink(ob)
                    continue

                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

                max_vert_dist = 0
                for i in range(len(bm.verts)):
                    for j in range(i+1, len(bm.verts)):
                        dist = distance(bm.verts[i].co, bm.verts[j].co)
                        if dist > max_vert_dist:
                            max_vert_dist = dist

                mesh_data[ob] = bm, max_vert_dist

                if biggest_mesh < max_vert_dist:
                    biggest_mesh = max_vert_dist

        trees = []

        index = 0
        init_active_ob = bpy.context.view_layer.objects.active
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            bpy.context.view_layer.objects.active = ob
            for ch in ob.children_recursive:
                bpy.data.objects.remove(ch, do_unlink=True)

            if ob.rigid_body is None:
                bpy.ops.rigidbody.object_add()

            ob.rigid_body.mass = 10
            ob.rigid_body.use_deactivation = True
            ob.rigid_body.collision_shape = props.input_rbshape

            if cmpnd:
                bm, max_dist = mesh_data[ob]
                target_map = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=0.01)["targetmap"]
                bmesh.ops.weld_verts(bm, targetmap=target_map)
                bmesh.ops.holes_fill(bm, edges=bm.edges, sides=4)

                bmesh.ops.scale(
                    bm,
                    vec=props.input_compound_scale,
                    verts=bm.verts
                )

                new_me = bpy.data.meshes.new(ob.name + "_solidified")
                bm.to_mesh(new_me)

                bmesh.ops.transform(bm, matrix=ob.matrix_world, verts=bm.verts)
                trees.append((ob, BVHTree.FromBMesh(bm)))
                bm.free()

                new_ob = bpy.data.objects.new(ob.name + "_solidified", new_me)
                context.collection.objects.link(new_ob)
                new_ob.parent = ob
                bpy.context.view_layer.objects.active = new_ob

                modifier = new_ob.modifiers.new(name="Remesh", type="REMESH")
                modifier.mode = "VOXEL"
                modifier.voxel_size = props.input_compound_voxel_size
                bpy.ops.object.modifier_apply(modifier=modifier.name)

                modifier = new_ob.modifiers.new(name="Decimate", type="DECIMATE")
                modifier.decimate_type = "COLLAPSE"
                modifier.use_collapse_triangulate = True
                modifier.ratio = props.input_compound_dm_ratio
                bpy.ops.object.modifier_apply(modifier=modifier.name)

                bpy.ops.rigidbody.object_add()
                new_ob.rigid_body.collision_shape = 'MESH'
                new_ob.rigid_body.collision_margin = 0

                #new_ob.display_type = 'WIRE'
                new_ob.show_in_front = True
                new_ob.hide_select = True

                index += 1
                props.progress = index / len(context.selected_objects)
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        bpy.context.view_layer.objects.active = init_active_ob

        if cmpnd:
            for i in range(len(trees)):
                for j in range(i + 1, len(trees)):
                    obj1, tree1 = trees[i]
                    obj2, tree2 = trees[j]
                    overlap_pairs = tree1.overlap(tree2)
                    if overlap_pairs:
                        print(f'--------WARNING: {obj1.name} collides with {obj2.name}')


        return {'FINISHED'}


class RemoveRigidbodies(Operator):
    bl_idname = "rbtool.button_remrb"
    bl_label = "Remove rigid bodies"

    def execute(self, context):
        props = context.scene.rbtool_rbprops

        for ob in context.collection.objects:
            if ob.type != 'MESH':
                continue

            if ob.rigid_body is not None:
                bpy.context.view_layer.objects.active = ob
                bpy.ops.rigidbody.object_remove()
                print(f'removed rb in {ob.name}')

                for ch in ob.children_recursive:
                    bpy.data.objects.remove(ch, do_unlink=True)

                ## check the rigidbodyworld collection
                ## might not be deleting fully

        return {'FINISHED'}


class ModifyConstraints(Operator):
    bl_idname = "rbtool.button_modify_const"
    bl_label = "Update constraints"

    def execute(self, context):
        props = context.scene.rbtool_constprops
        collection = context.collection.children.get(context.collection.name  + '_overlaps')

        for ob in collection.objects:
            bpy.context.view_layer.objects.active = ob

            bpy.context.object.rigid_body_constraint.type = props.input_type
            bpy.context.object.rigid_body_constraint.disable_collisions = not props.input_enable_collisions
            bpy.context.object.rigid_body_constraint.use_breaking = True
            bpy.context.object.rigid_body_constraint.breaking_threshold = props.input_break_threshold
            bpy.context.object.show_in_front = props.input_show_in_front

        return {'FINISHED'}


def get_bvh(collection, solidify, solidify_thickness, subd):
    trees = []
    for obj in collection.objects:
        if obj.type != 'MESH':
            continue
        if 'solidif' in obj.name:
            continue

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        if len(bm.verts) == 0:
            print('todo remove empty mesh objects')

        bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)

        if solidify:
            bmesh.ops.solidify(bm, geom=bm.faces, thickness=solidify_thickness)

        if subd > 0:
            bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=subd)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        tree = BVHTree.FromBMesh(bm)
        trees.append((tree, (obj, bm)))

    return trees


def reset_collection(parent_collection, name):
    col_reset = None
    for col in bpy.data.collections:
        if col.name == name:
            col_reset = col
        if 'RigidBodyWorld' in col.name:
            colrbw = col
        if 'RigidBodyConstraints' in col.name:
            colrbc = col
    if col_reset is None:
        col_reset = bpy.data.collections.new(name)
        parent_collection.children.link(col_reset)
    else:
        for ob in col_reset.objects:
            if colrbw.objects.get(ob.name) is not None:
                colrbw.objects.unlink(ob)
            if colrbc.objects.get(ob.name) is not None:
                colrbc.objects.unlink(ob)
            col_reset.objects.unlink(ob)

    bpy.ops.outliner.orphans_purge(do_local_ids=True)

    return col_reset


class StructureGenerator(Operator):
    bl_idname = "rbtool.button_generate"
    bl_label = "Generate structure"

    def execute(self, context):
        props = context.scene.rbtool_overlapprops
        props_const = context.scene.rbtool_constprops
        collection = context.collection

        bpy.context.scene.frame_current = 0
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        trees = get_bvh(collection, props.input_solidify, props.input_overlap_margin, props.input_subd)
        col_empties = reset_collection(collection, collection.name + '_overlaps')

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

                    empty_name = f'{obj1.name}_{obj2.name}_overlap'
                    empty = bpy.data.objects.new(empty_name, None)
                    empty.empty_display_size = 0.2

                    empty.location = loc
                    col_empties.objects.link(empty)

                    bpy.context.view_layer.objects.active = empty
                    bpy.ops.rigidbody.constraint_add(type=props_const.input_type)

                    bpy.context.object.rigid_body_constraint.disable_collisions = not props_const.input_enable_collisions
                    bpy.context.object.rigid_body_constraint.use_breaking = True
                    bpy.context.object.rigid_body_constraint.breaking_threshold = props_const.input_break_threshold
                    bpy.context.object.show_in_front = props_const.input_show_in_front

                    bpy.context.object.rigid_body_constraint.object1 = obj1
                    bpy.context.object.rigid_body_constraint.object2 = obj2

            props.progress = (i + 1) / (len(trees))
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            print(f"Progress: {props.progress*100:.2f}%")

        return {'FINISHED'}


# A list of classes to register and unregister
classes = [
    OverlapProps,
    RBProps,
    ConstraintProps,
    StructureGenerator,
    SetRigidbodies,
    RemoveRigidbodies,
    ModifyConstraints,
    MainPanel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rbtool_rbprops = bpy.props.PointerProperty(type=RBProps)
    bpy.types.Scene.rbtool_overlapprops = bpy.props.PointerProperty(type=OverlapProps)
    bpy.types.Scene.rbtool_constprops = bpy.props.PointerProperty(type=ConstraintProps)


def unregister():
   for cls in reversed(classes):
       bpy.utils.unregister_class(cls)

   del bpy.types.Scene.rbtool_rbprops
   del bpy.types.Scene.rbtool_overlapprops
   del bpy.types.Scene.rbtool_constprops


if __name__ == "__main__":
   register()

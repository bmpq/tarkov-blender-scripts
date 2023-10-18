import bpy
import bmesh
import math


bl_info = {
    "name": "Wireframe Generator",
    "author": "bmpq",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Tools",
    "description": "Generate separate objects from edges",
    "category": "Object"
}


class WireframeGenProps(bpy.types.PropertyGroup):
    thickness: bpy.props.FloatProperty(
        name="Thickness",
        min=0,
        soft_min=0.001,
        soft_max=1,
        default=0.1,
        precision=3,
        step=1
    )
    prune: bpy.props.FloatProperty(
        name="Prune",
        soft_min=0,
        default=0.1,
        precision=3,
        step=1
    )


def move_coords(coord1, coord2, dist_delta):
    if dist_delta == 0:
        return coord1, coord2

    x1, y1, z1 = coord1
    x2, y2, z2 = coord2

    orig_dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    ux = (x2 - x1) / orig_dist
    uy = (y2 - y1) / orig_dist
    uz = (z2 - z1) / orig_dist

    new_dist = orig_dist + dist_delta

    if new_dist < 0:
        print('Warning: pruning resulted in negative distance')

    new_x1 = x1 + (ux * dist_delta / 2)
    new_y1 = y1 + (uy * dist_delta / 2)
    new_z1 = z1 + (uz * dist_delta / 2)
    new_x2 = x2 - (ux * dist_delta / 2)
    new_y2 = y2 - (uy * dist_delta / 2)
    new_z2 = z2 - (uz * dist_delta / 2)

    return (new_x1, new_y1, new_z1), (new_x2, new_y2, new_z2)


def get_collection(parent_col, name):
    col = parent_col.children.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        parent_col.children.link(col)
    else:
        for obj in col.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.outliner.orphans_purge(do_local_ids=True)

    return col


class WireframeGenPanel(bpy.types.Panel):
    bl_label = "Wireframe Gen"
    bl_idname = "VIEW3D_PT_wireframegen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.wireframegen_props

        edge_count = 0

        for ob in context.selected_objects:
            if 'STRA_EDGE' in ob.name:
                layout.label(text='Generated edge selected')
                return
            if ob.type == 'MESH':
                bm = bmesh.new()
                bm.from_mesh(ob.data)
                bm.edges.ensure_lookup_table()
                for edge in bm.edges:
                    edge_count += 1

        layout.label(text=f'Selected edges: {edge_count}')

        if edge_count == 0:
            return

        layout.prop(props, "prune")
        layout.prop(props, "thickness")

        txt_gen = f'Generate {edge_count} edge objects'

        if len(context.selected_objects) == 1:
            ob = context.selected_objects[0]
            for col in bpy.data.collections:
                if (ob.name + '_WIREFRAME') in col.name:
                    txt_gen = f'Regenerate {edge_count} edge objects'
                    break

        r = layout.row()
        r.scale_y = 2
        r.operator("wireframegen.generate", icon="MOD_WIREFRAME", text=txt_gen)


class WireframeGenGenerate(bpy.types.Operator):
    bl_idname = "wireframegen.generate"
    bl_label = "Generate Wireframe"
    bl_options = {"UNDO_GROUPED"}

    def execute(self, context):
        props = context.scene.wireframegen_props
        objs = context.selected_objects

        for ob in objs:
            ob.select_set(False)
            if ob.type != 'MESH':
                continue

            new_col = get_collection(context.scene.collection, f'{ob.name}_WIREFRAME')

            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bm.edges.ensure_lookup_table()

            for edge in bm.edges:
                new_mesh = bpy.data.meshes.new(f'{ob.name}_EDGE_MESH')
                new_bm = bmesh.new()
                coord1 = edge.verts[0].co
                coord2 = edge.verts[1].co

                if props.prune > 0:
                    coord1, coord2 = move_coords(coord1, coord2, props.prune)

                v1 = new_bm.verts.new(coord1)
                v2 = new_bm.verts.new(coord2)
                new_bm.edges.new([v1, v2])
                new_bm.transform(ob.matrix_world)
                new_bm.to_mesh(new_mesh)
                new_bm.free()
                new_obj = bpy.data.objects.new(f'{ob.name}_EDGE', new_mesh)
                new_col.objects.link(new_obj)

                bpy.context.view_layer.objects.active = new_obj

                modifier = new_obj.modifiers.new(name="Skin", type="SKIN")
                new_mesh.update()
                new_mesh.skin_vertices[0].data[0].radius = (props.thickness, props.thickness)
                new_mesh.skin_vertices[0].data[1].radius = (props.thickness, props.thickness)
                bpy.ops.object.modifier_apply(modifier=modifier.name)

                new_obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
                new_obj.select_set(False)

                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        for ob in objs:
            ob.select_set(True)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(WireframeGenProps)
    bpy.utils.register_class(WireframeGenPanel)
    bpy.utils.register_class(WireframeGenGenerate)
    bpy.types.Scene.wireframegen_props = bpy.props.PointerProperty(type=WireframeGenProps)

def unregister():
    bpy.utils.unregister_class(WireframeGenProps)
    bpy.utils.unregister_class(WireframeGenPanel)
    bpy.utils.unregister_class(WireframeGenGenerate)
    del bpy.types.Scene.wireframegen_props

if __name__ == "__main__":
    register()

from mathutils import kdtree
import bmesh
import bpy

bl_info = {
    "name": "Vertex Selection by Proximity",
    "author": "bmpq",
    "version": (1, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Tools",
    "description": "Selects vertices based on proximity and connected edges",
    "category": "Mesh",
}

class VertexSelectionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_vertex_selection"
    bl_label = "Vertex Selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout

        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            layout.label(text="No mesh selected")
            return

        me = obj.data
        if obj.mode != 'EDIT':
            layout.label(text="Not in Edit mode")
            return

        bm = bmesh.from_edit_mesh(me)
        selected_verts = [v for v in bm.verts if v.select]

        if len(selected_verts) == 0:
            layout.label(text="No vertices selected")
            return

        layout.prop(context.scene, "threshold")
        layout.operator("mesh.vertex_select_proximity")


class MESH_OT_vertex_select(bpy.types.Operator):
    bl_idname = "mesh.vertex_select_proximity"
    bl_label = "Select Vertices By Proximity"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = bpy.context.selected_objects
        for obj in objs:
            if obj.mode != 'EDIT':
                continue

            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            size = len(bm.verts)
            kd = kdtree.KDTree(size)
            for i, vtx in enumerate(bm.verts):
                kd.insert(vtx.co, i)
            kd.balance()

            threshold = context.scene.threshold
            changed = True
            while changed:
                changed = False

                for v in bm.verts:
                    if not v.select:
                        continue

                    # select connected vertices
                    for e in v.link_edges:
                        if not e.select:
                            e.select = True
                            changed = True

                    # select vertices by proximity
                    for (co, index, dist) in kd.find_range(v.co, threshold):
                        if not bm.verts[index].select:
                            bm.verts[index].select = True
                            changed = True

            bm.select_flush(True)
            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(VertexSelectionPanel)
    bpy.utils.register_class(MESH_OT_vertex_select)
    bpy.types.Scene.threshold = bpy.props.FloatProperty(
        name="Threshold",
        default=0.0001,
        description="Vertex selection threshold",
        min=0.0,
        precision=6,
        step=0.001
    )

def unregister():
    bpy.utils.unregister_class(VertexSelectionPanel)
    bpy.utils.unregister_class(MESH_OT_vertex_select)

    del bpy.types.Scene.threshold


if __name__ == "__main__":
    register()

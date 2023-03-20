import bpy
import bmesh
from mathutils import kdtree


bl_info = {
    "name": "Select Visually Linked Vertices within Threshold",
    "description": "Selects vertices within a threshold distance of the currently selected vertices. Basically selects vaisually connected vertices that are not actually connected",
    "author": "bmpq",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Tools > Select Visually Linked Vertices within Threshold",
    "category": "Mesh",
}

class SelectLinkedVerticesWithinThreshold(bpy.types.Operator):
    bl_idname = "mesh.select_visually_linked_within_threshold"
    bl_label = "Select Visually Linked Vertices within Threshold"
    bl_description = "Selects all linked vertices within a threshold distance of the currently selected vertices"

    threshold: bpy.props.FloatProperty(
        name="Threshold Distance",
        default=0.0001,
        min=0.0,
        precision=5,
        step=0.001,
        description="Maximum distance between vertices to be selected"
    )

    def execute(self, context):
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

                for (co, index, dist) in kd.find_range(v.co, self.threshold):
                    if not bm.verts[index].select:
                        bm.verts[index].select = True
                        changed = True

        bm.select_flush(True)
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SelectLinkedVerticesWithinThresholdPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select_linked_vertices_within_threshold"
    bl_label = "Select visually Linked Vertices within Threshold"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(
            text="Select visually linked vertices within a threshold distance of currently selected vertices:")
        layout.prop(context.scene, "threshold")
        layout.operator("mesh.select_visually_linked_within_threshold",
                        text="Select Visually Linked Vertices")


classes = [
    SelectLinkedVerticesWithinThreshold,
    SelectLinkedVerticesWithinThresholdPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.threshold = bpy.props.FloatProperty(
        name="Threshold Distance",
        default=0.0001,
        min=0.0,
        precision=5,
        step=0.001,
        description="Maximum distance between vertices to be selected"
    )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.threshold


if __name__ == "__main__":
    register()

import math
import bpy
bl_info = {
    "name": "Select Linked Vertices within Threshold",
    "description": "Selects all linked vertices within a threshold distance of the currently selected vertices",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Select Linked Vertices within Threshold",
    "category": "Mesh",
}


class SelectLinkedVerticesWithinThreshold(bpy.types.Operator):
    bl_idname = "mesh.select_linked_within_threshold"
    bl_label = "Select Linked Vertices within Threshold"
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
        mesh = obj.data

        def get_selected_verts():
            return [v for v in mesh.vertices if v.select]

        def distance(t1, t2):
            return (t2 - t1).length

        prev_selected_amount = len(get_selected_verts())
        while True:
            bpy.ops.object.mode_set(mode='OBJECT')
            for v in get_selected_verts():
                for va in mesh.vertices:
                    if va.select:
                        continue
                    if distance(v.co, va.co) > self.threshold:
                        continue
                    va.select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()

            if prev_selected_amount == len(get_selected_verts()):
                break

            prev_selected_amount = len(get_selected_verts())

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


class SelectLinkedVerticesWithinThresholdPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select_linked_vertices_within_threshold"
    bl_label = "Select Linked Vertices within Threshold"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Select"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(
            text="Select linked vertices within a threshold distance of currently selected vertices:")
        layout.prop(context.scene, "threshold")
        layout.operator("mesh.select_linked_within_threshold",
                        text="Select Linked Vertices")


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

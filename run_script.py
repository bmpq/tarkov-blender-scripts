import bpy
import os

bl_info = {
    "name": "Run python script",
    "author": "bmpq",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Tools",
    "description": "Runs script given a path",
    "category": "Development",
}

class RunScriptPanel(bpy.types.Panel):
    bl_label = "Run Script"
    bl_idname = "OBJECT_PT_runscript"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "script_path")
        layout.operator("object.run_script")


class RunScriptOperator(bpy.types.Operator):
    bl_idname = "object.run_script"
    bl_label = "Run Script"

    def execute(self, context):
        scene = context.scene
        script_path = scene.script_path
        if os.path.isfile(script_path) and script_path.endswith(".py"):
            exec(open(script_path).read())
            self.report(
                {'INFO'}, f"Script {os.path.basename(script_path)} executed successfully")
        else:
            self.report({'ERROR'}, f"Invalid script path: {script_path}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(RunScriptPanel)
    bpy.utils.register_class(RunScriptOperator)
    bpy.types.Scene.script_path = bpy.props.StringProperty(
        name="",
        description="The path of the python script to run",
        default="",
        subtype='FILE_PATH'
    )


def unregister():
    bpy.utils.unregister_class(RunScriptPanel)
    bpy.utils.unregister_class(RunScriptOperator)
    del bpy.types.Scene.script_path


if __name__ == "__main__":
    register()

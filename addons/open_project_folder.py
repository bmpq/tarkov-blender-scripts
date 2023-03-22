import bpy
import os

bl_info = {
    "name": "My Addon",
    "author": "John Doe",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Tools",
    "description": "Opens the local folder of the currently opened project in the File Explorer.",
    "category": "Development",
}

class MyAddonPanel(bpy.types.Panel):
    bl_label = "My Addon"
    bl_idname = "VIEW3D_PT_my_addon"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("myaddon.open_folder", text="Open Project Folder")

class MyAddonOpenFolder(bpy.types.Operator):
    bl_idname = "myaddon.open_folder"
    bl_label = "Open Project Folder"

    def execute(self, context):
        filepath = bpy.data.filepath
        if filepath:
            folderpath = os.path.dirname(filepath)
            os.startfile(folderpath)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MyAddonPanel)
    bpy.utils.register_class(MyAddonOpenFolder)

def unregister():
    bpy.utils.unregister_class(MyAddonPanel)
    bpy.utils.unregister_class(MyAddonOpenFolder)

if __name__ == "__main__":
    register()

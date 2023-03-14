import bpy

for obj in bpy.context.scene.objects:
    if obj.type == 'EMPTY':
        obj.empty_display_size = 0.1
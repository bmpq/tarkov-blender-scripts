import bpy

all_objects = bpy.context.scene.objects

for obj in all_objects:
    if obj.type == 'EMPTY' and not obj.children:
        print('Removing ' + obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
import bpy

mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

for obj in mesh_objs:
    for mat_slot in obj.material_slots:
        mat_name = mat_slot.material.name

        if len(mat_name) < 4:
            continue

        # check if mat_name ends with .### (where ### is a number)
        if mat_name[-4] == '.' and mat_name[-3:].isdigit():
            mat_name = mat_name[:-4]
            if mat_name in bpy.data.materials:
                mat_slot.material = bpy.data.materials[mat_name]
                print('Linked ' + mat_name + ' to ' + obj.name)
import bpy

# get a list of all objects in the scene
objects = bpy.context.scene.objects

print('Objects in the scene: ' + str(len(objects)))

# iterate through all objects in the scene
for obj in objects:
    # every slot in the object
    for slot in obj.material_slots:
        if slot.material:
            print('Unlinking ' + slot.material.name)
        slot.material = None
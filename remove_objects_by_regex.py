import re
import bpy

regex_list = [".*LOD1.*", ".*LOD2.*", ".*LOD3.*", ".*LOD4.*", ".*SHADOW.*", ".*BALLISTIC.*", ".*BALISTIC.*", ".*COLLIDER.*", ".*COLIDER.*", ".*TRIGGER.*", ".*TRIGER.*"]

# recursively remove all children of an object
def remove_children(obj):
    for child in obj.children:
        remove_children(child)
        removed_children_count += 1
        bpy.data.objects.remove(child, do_unlink=True)

print('Checking ' + str(len(bpy.context.scene.objects)) + ' objects')
removed_count = 0
removed_children_count = 0

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    for regex in regex_list:
        pattern = re.compile(regex, re.IGNORECASE)
        if pattern.match(obj.name):
            print('Removing ' + obj.name)
            removed_count += 1
            
            remove_children(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
            break
        
print('Removed ' + str(removed_count) + ' objects' + ' with ' + str(removed_children_count) + ' children')
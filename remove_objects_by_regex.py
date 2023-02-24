import re
import bpy

regex_list = [".*LOD1.*", ".*LOD2.*", ".*LOD3.*", ".*LOD4.*", ".*SHADOW.*", ".*BALLISTIC.*", ".*BALISTIC.*", ".*COLLIDER.*", ".*COLIDER.*", ".*TRIGGER.*", ".*TRIGER.*"]

removed_count = 0
removed_child_count = 0;

# recursively remove all children of an object
def remove_children(obj):
    child_count = 0;
    for child in obj.children:
        child_count += 1
        child_count += remove_children(child)
        bpy.data.objects.remove(child, do_unlink=True)
    return child_count

print('Checking ' + str(len(bpy.context.scene.objects)) + ' objects')

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    for regex in regex_list:
        pattern = re.compile(regex, re.IGNORECASE)
        if pattern.match(obj.name):
            removed_count += 1
            removed_child_delta = remove_children(obj)
            removed_child_count += removed_child_delta
            print('Removed ' + obj.name + ' with ' + str(removed_child_delta) + ' children')
            bpy.data.objects.remove(obj, do_unlink=True)
            break
        
print('Removed ' + str(removed_count) + ' objects with ' + str(removed_child_count) + ' children')
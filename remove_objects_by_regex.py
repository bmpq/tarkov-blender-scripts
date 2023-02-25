import re
import bpy

regex_list_lod = [".*LOD1.*", ".*LOD2.*", ".*LOD3.*", ".*LOD4.*", ".*lod\..*", ".*lod_2\..*", ".*_lod$"]
regex_list = [".*SHADOW.*", ".*BALLISTIC.*", ".*BALISTIC.*", ".*COLLIDER.*", ".*COLIDER.*", ".*COLISION.*",".*COLLISION.*", ".*TRIGGER.*", ".*TRIGER.*", ".*TRG.*", "^Pull\w*", "^Push\w*", "^KeyGrip\w*", ".*sg_pivot.*", ".*sg_targets.*", ".*test_hand.*"]

removed_count = 0
removed_child_count = 0

skip_if_no_siblings = True

# recursively remove all children of an object
def remove_children(obj):
    child_count = 0
    for child in obj.children:
        child_count += 1
        child_count += remove_children(child)
        bpy.data.objects.remove(child, do_unlink=True)
    return child_count

def remove(obj):
    global removed_count
    global removed_child_count

    removed_count += 1
    removed_child_delta = remove_children(obj)
    removed_child_count += removed_child_delta
    print('Removed ' + obj.name + ' with ' + str(removed_child_delta) + ' children')
    bpy.data.objects.remove(obj, do_unlink=True)

print('Checking ' + str(len(bpy.context.scene.objects)) + ' objects')

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    removed = False
    for regex in regex_list:
        pattern = re.compile(regex, re.IGNORECASE)
        if pattern.match(obj.name):
            remove(obj)
            removed = True
            break

    if removed or not obj.parent:
        continue

    for regex in regex_list_lod:
        pattern = re.compile(regex, re.IGNORECASE)
        if pattern.match(obj.name):
            if skip_if_no_siblings and len(obj.parent.children) == 1:
                print('Skipping ' + obj.name + ' (lod object with no siblings)')
                break
            remove(obj)
            break
        
print('Removed ' + str(removed_count) + ' objects with ' + str(removed_child_count) + ' children')
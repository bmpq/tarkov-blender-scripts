import re
import bpy
import time

## I made this to cleanup scenes exported from Escape from Tarkov
## not optimized, slow af

print_progress = True

# the goal is to delete all the meshes that are not LOD0, this list is separate because of reasons below
regex_list_lod = [".*lod(_)?[1-4].*", ".*_lod($|\.)"]
regex_list_decals = [".*de(c|k)al.*", ".*dekal.*", ".*dec_.*"]
regex_list = [
    # a lot of meshes on the scene have their own dedicated simplified meshes for shadow projection
    ".*SHADOW.*", ".*Sten(s|c)il.*",
    # physics and bullet penetration colliders
    ".*BAL(L)?ISTIC.*", ".*COL(L)?IDER.*", ".*COL(L)?ISION.*", ".*LowPen.*", ".*HighPen.*",
    # gameplay related triggers
    ".*TRIG(G)?ER.*", "^TRG.*",
    # almost every door in the game has a placeholder hand rig stuck to its handle for some reason, they are not even used in the game
    "^Pull\w*", "^Push\w*", ".*KeyGrip.*", ".*sg_pivot.*", ".*sg_targets.*", ".*test_hand.*", ".*HumanLPalm.*", ".*HumanRPalm.*",
    # level border or player restricted area meshes
    ".*BLOCKER.*", "^Cube.*",
    # culling
    ".*culling.*",
    # yeah i dont know, big box meshes
     "^stones_.*"]

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

avg_time = []

def remove(obj):
    global removed_count
    global removed_child_count

    time_s = time.time()

    removed_count += 1
    removed_child_delta = remove_children(obj)
    removed_child_count += removed_child_delta

    name_rem = obj.name
    bpy.data.objects.remove(obj, do_unlink=True)

    if print_progress:
        time_e = time.time()
        t = time_e - time_s
        if removed_child_delta == 0:
            avg_time.append(t)
        print(f'({removed_count + removed_child_count}) Removed {name_rem} with {removed_child_delta} children')

    if (removed_count) % 500 == 0:
        if print_progress:
            a = 0
            for ta in avg_time:
                a += ta
            a /= len(avg_time)
            avg_time.clear()
            avg_str = '%.4f' % a
            print(f'Average time to delete: {avg_str}s per object')

        # cleaning up the data-blocks from deleted objects to speed up the whole thing
        bpy.ops.outliner.orphans_purge(do_local_ids=True)
        bpy.context.view_layer.update()

print('Checking ' + str(len(bpy.context.scene.objects)) + ' objects')

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    for regex in regex_list:
        pattern = re.compile(regex, re.IGNORECASE | re.DOTALL)
        if obj and pattern.match(obj.name):
            remove(obj)
            break

for obj in bpy.context.scene.objects:
    if obj.parent is None:
        continue

    for regex in regex_list_lod:
        pattern = re.compile(regex, re.IGNORECASE)
        if pattern.match(obj.name):
            lod0found = False
            for sibling in obj.parent.children:
                if sibling == obj:
                    continue
                if sibling.name.split('.')[0].lower().endswith('_lod0'):
                    if sibling.type != 'MESH':
                        continue
                    lod0found = True
                    break

            if lod0found:
                remove(obj)
            break

print('Total removed: ' + str(removed_count) + ' objects with ' + str(removed_child_count) + ' children')
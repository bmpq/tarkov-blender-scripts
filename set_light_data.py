import bpy
import math

col = bpy.context.scene.collection.children.get('gen_lights')
if col is None:
    col = bpy.data.collections.new(name='gen_lights')
    bpy.context.scene.collection.children.link(col)
else:
    for obj in col.objects:
        col.objects.unlink(obj)
        bpy.data.objects.remove(obj)

bpy.ops.outliner.orphans_purge(do_local_ids=True)

light_data_feron = bpy.data.lights.new(name="light_feron", type="SPOT")
light_data_feron.spot_size = math.radians(85.8)
light_data_feron.shadow_soft_size = 0.35
light_data_feron.energy = 4000
light_data_feron.color = (0.6934, 0.9025, 1)

light_data_glowstick = bpy.data.lights.new(name="light_glowstick", type="POINT")
light_data_glowstick.shadow_soft_size = 0.35
light_data_glowstick.energy = 500
light_data_glowstick.color = (0.9906, 0.5285, 0.5093)

for mt in bpy.context.scene.objects:
    if mt.type != 'EMPTY':
        continue
    if 'point_light' in mt.name.lower():
        if 'gi' in mt.name.lower():
            continue
        if 'feron' in mt.parent.name.lower():
            y = mt.location[1]
            z = mt.location[2]
            if y < -0 and y > -0.33 and z > 1.95 and z < 2:
                light_obj = bpy.data.objects.new(name='feron', object_data=light_data_feron)
                col.objects.link(light_obj)
                light_obj.rotation_euler = (math.radians(180), 0,0)
                light_obj.parent = mt
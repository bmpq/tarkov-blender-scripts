import bpy

for m in bpy.data.materials:
    if m.use_nodes == False:
        continue

    tree = m.node_tree
    for n1 in tree.nodes:
        if n1.type != "TEX_IMAGE":
            continue

        texture_name = n1.image.name
        if len(texture_name) < 4:
            continue

        if texture_name[-4] == '.' and texture_name[-3:].isdigit():
            texture_name = texture_name[:-4]
            if texture_name in bpy.data.images:
                n1.image = bpy.data.images[texture_name]
                print('replaced texture: ' + texture_name)
                continue
## this script is used to convert materials in an imported unity scene
## the scene is expected to be exported as an fbx with FBX Exporter (unity package) ripped with AssetRipper

import bpy

def get_connected_link(nodes, inputSocket):
    for n in nodes:
        for socket in n.outputs:
            for l in socket.links:
                if l.to_socket == inputSocket:
                    return l
    return None


mat_num = 0

for m in bpy.data.materials:
    if m.use_nodes == False:
        continue

    ## disable backface rendering
    m.show_transparent_back = False

    tree = m.node_tree
    bsdf = None
    for n in tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            bsdf = n
            break
    if bsdf == None:
        continue

    socketBaseColor = bsdf.inputs[0]
    socketMetal = bsdf.inputs[6]
    socketSpec = bsdf.inputs[7]
    socketEmissionStrength = bsdf.inputs[20]
    socketAlpha = bsdf.inputs[21]
    socketNormal = bsdf.inputs[22]
    socketRough = bsdf.inputs[9]
    socketTransmission = bsdf.inputs[17]

    ## telling blender that the alpha channel in diffuse texture is not alpha channel
    link = get_connected_link(tree.nodes, socketBaseColor)
    if link:
        node_tex = link.from_node
        node_tex.image.alpha_mode = 'CHANNEL_PACKED'

        bc = socketBaseColor.default_value
        if bc[0] != 1 or bc[1] != 1 or bc[2] != 1 or bc[3] != 1:
            print("mat %d base color: %f %f %f %f" % (mat_num, bc[0], bc[1], bc[2], bc[3]))
            ## mix node_tex by base color default value
            n = tree.nodes.new('ShaderNodeMixRGB')
            n.location = node_tex.location
            n.blend_type = 'MULTIPLY'
            n.inputs[0].default_value = 1
            tree.links.new(node_tex.outputs[0], n.inputs[1])
            n.inputs[2].default_value = socketBaseColor.default_value
            tree.links.new(n.outputs[0], socketBaseColor)
            node_tex.location.x -= 300

    ## metallic to 0.00
    socketMetal.default_value = 0
    r = socketRough.default_value

    ## flag to skip specular conversion if the material has transparency
    ## because there is no dedicated specular texture file
    ## and it is stored in the diffuse texture's alpha channel
    ## except when the material is supposed to have transparency
    ## in that case the alpha channel is actually for alpha
    ## and the specular texture just doesn't exist I guess
    alpha_keywords = ['decal', 'dekal', 'puddle', 'graffiti', 'grafiti', 'paintcrack', 'wall_crack', 'spiral_bruno', 'chain']
    has_alpha_channel = any(keyword in m.name.lower() for keyword in alpha_keywords)
    if has_alpha_channel == False and link != None:
        has_alpha_channel = any(keyword in node_tex.image.name.lower() for keyword in alpha_keywords)

    socketEmissionStrength.default_value = 0
    m.blend_method = 'CLIP'
    m.shadow_method = 'CLIP'

    socketSpec.default_value = 0.5

    ## replugging diffuse's alpha to specular, by default blender plugs it in BSDF alpha
    if has_alpha_channel == False:
        linkAlpha = get_connected_link(tree.nodes, socketAlpha)
        if linkAlpha != None:
            tex_d = linkAlpha.from_node
            tree.links.new(tex_d.outputs[1], socketSpec)
            tree.links.remove(linkAlpha)

    ## puddles are just mirrors
    is_puddle = 'puddle' in m.name.lower()
    if is_puddle:
        ## remove diffuse texture link
        linkDiffuse = get_connected_link(tree.nodes, socketBaseColor)
        if linkDiffuse != None:
            tree.links.remove(linkDiffuse)

        socketBaseColor.default_value = 1,1,1,1
        socketTransmission.default_value = 1.0

    mat_num += 1


print(f'Successfully converted {mat_num} materials')
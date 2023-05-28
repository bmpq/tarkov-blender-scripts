## this script is used to convert materials in an imported unity scene
## the scene is expected to be exported as an fbx with AssetStudioGUI

import bpy

## unity normal maps are packed in a specific way, this creates a node setup that unpacks them
def create_nodegroup_normal_converter():
    tree = bpy.data.node_groups.new('Unpack.Unity.Normal', 'ShaderNodeTree')

    inputs = tree.nodes.new('NodeGroupInput')
    inputs.location = (-300, -300)
    tree.inputs.new('NodeSocketColor', 'Color').default_value = (0.5, 0.5, 1, 1)
    tree.inputs.new('NodeSocketFloat', 'Alpha').default_value = 1

    xy = inputs.location
    offset = 40

    n0 = tree.nodes.new('ShaderNodeSeparateRGB')
    n0.location = xy
    n0.location.x += offset + inputs.width
    tree.links.new(inputs.outputs[0], n0.inputs[0])

    n1 = tree.nodes.new('ShaderNodeCombineRGB')
    n1.location = n0.location
    n1.location.x += offset + n0.width
    n1.inputs[2].default_value = 1
    tree.links.new(n0.outputs[1], n1.inputs[0])
    tree.links.new(inputs.outputs[1], n1.inputs[1])

    n2 = tree.nodes.new('ShaderNodeSeparateXYZ')
    n2.location = n1.location
    n2.location.x += offset + n1.width
    tree.links.new(n1.outputs[0], n2.inputs[0])

    n3 = tree.nodes.new('ShaderNodeMapRange')
    n3.location = n2.location
    n3.location.x += offset + n2.width
    n3.location.y -= offset + n2.height
    n3.data_type = 'FLOAT'
    n3.inputs[1].default_value = 0
    n3.inputs[2].default_value = 1
    n3.inputs[3].default_value = -1
    n3.inputs[4].default_value = 1
    tree.links.new(n2.outputs[0], n3.inputs[0])

    n4 = tree.nodes.new('ShaderNodeMath')
    n4.location = n3.location
    n4.location.x += offset + n3.width
    n4.operation = 'MULTIPLY'
    tree.links.new(n3.outputs[0], n4.inputs[0])
    tree.links.new(n3.outputs[0], n4.inputs[1])

    n5 = tree.nodes.new('ShaderNodeMath')
    n5.location = n4.location
    n5.location.x += offset + n4.width
    n5.operation = 'SUBTRACT'
    n5.inputs[0].default_value = 1
    tree.links.new(n4.outputs[0], n5.inputs[1])

    n6 = tree.nodes.new('ShaderNodeMapRange')
    n6.location = n4.location
    n6.location.y -= offset + n4.height
    n6.data_type = 'FLOAT'
    n6.inputs[1].default_value = 0
    n6.inputs[2].default_value = 1
    n6.inputs[3].default_value = -1
    n6.inputs[4].default_value = 1
    tree.links.new(n2.outputs[1], n6.inputs[0])

    n7 = tree.nodes.new('ShaderNodeMath')
    n7.location = n5.location
    n7.location.y -= offset + n5.height
    n7.operation = 'MULTIPLY'
    tree.links.new(n6.outputs[0], n7.inputs[0])
    tree.links.new(n6.outputs[0], n7.inputs[1])

    n8 = tree.nodes.new('ShaderNodeMath')
    n8.location = n5.location
    n8.location.x += offset + n5.width
    n8.location.y -= offset
    n8.operation = 'SUBTRACT'
    tree.links.new(n5.outputs[0], n8.inputs[0])
    tree.links.new(n7.outputs[0], n8.inputs[1])

    n9 = tree.nodes.new('ShaderNodeMath')
    n9.location = n8.location
    n9.location.x += offset + n8.width
    n9.operation = 'POWER'
    n9.inputs[1].default_value = 0.5
    tree.links.new(n8.outputs[0], n9.inputs[0])

    n10 = tree.nodes.new('ShaderNodeMapRange')
    n10.location = n9.location
    n10.location.x += offset + n9.width
    n10.data_type = 'FLOAT'
    n10.inputs[1].default_value = -1
    n10.inputs[2].default_value = 1
    n10.inputs[3].default_value = 0
    n10.inputs[4].default_value = 1
    tree.links.new(n9.outputs[0], n10.inputs[0])

    n11 = tree.nodes.new('ShaderNodeInvert')
    n11.location = n10.location
    n11.location.x += offset + n10.width
    n11.inputs[0].default_value = 1
    tree.links.new(n2.outputs[1], n11.inputs[1])

    n12 = tree.nodes.new('ShaderNodeCombineXYZ')
    n12.location = n11.location
    n12.location.x += offset + n11.width
    n12.location.y = n2.location.y
    tree.links.new(n2.outputs[0], n12.inputs[0])
    tree.links.new(n11.outputs[0], n12.inputs[1])
    tree.links.new(n10.outputs[0], n12.inputs[2])

    outputs = tree.nodes.new('NodeGroupOutput')
    outputs.location = n12.location
    outputs.location.x += offset + n12.width
    outputs.location.y = n12.location.y
    tree.outputs.new('NodeSocketVector', 'Color')
    tree.links.new(n12.outputs[0], outputs.inputs[0])

    return tree


ng_converter = None
for ng in bpy.data.node_groups:
    if ng.name == "Unpack.Unity.Normal":
        ng_converter = ng
        break
if ng_converter == None:
    ng_converter = create_nodegroup_normal_converter()


def get_connected_link(nodes, inputSocket):
    for n in nodes:
        for socket in n.outputs:
            for l in socket.links:
                if l.to_socket == inputSocket:
                    return l
    return None


def convert_normalmap(tree, nodeImageTexture, socketInputNormalMap):
    ng = tree.nodes.new('ShaderNodeGroup')
    ng.node_tree = ng_converter
    ng.location.x = nodeImageTexture.location.x + 300
    ng.location.y = nodeImageTexture.location.y
    tree.links.new(nodeImageTexture.outputs[0], ng.inputs[0])
    tree.links.new(nodeImageTexture.outputs[1], ng.inputs[1])

    tree.links.new(ng.outputs[0], socketInputNormalMap)


def check_normalmap_valid(tree, socketNormal):
    link_normal = get_connected_link(tree.nodes, socketNormal)
    if link_normal == None:
        return None

    socket_color = link_normal.from_node.inputs[1]
    if socket_color == None:
        return None

    link_image_normal = get_connected_link(tree.nodes, socket_color)
    if link_image_normal == None:
        return None

    if link_image_normal.from_node.type != 'TEX_IMAGE':
        return None

    return link_image_normal


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

    ## in blender it's roughness, in unity it's glossiness, so have to invert
    ## and for some reason the value is between 0.9 and 1.0
    ## but in some materials the roughness value is normalized between 0.0-1.0
    ## i dont know whats going on, not sure i got this right
    if r > 0.9:
        r = r - 0.9
        r = r * 10
        r = 1 - r
        socketRough.default_value = r

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
    m.blend_method = 'HASHED'
    m.shadow_method = 'HASHED'

    socketSpec.default_value = 0

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

        ## set color to black
        socketBaseColor.default_value = 0,0,0,1

    ## convert normal map
    link_image_normal = check_normalmap_valid(tree, socketNormal)
    if link_image_normal != None:
        convert_normalmap(tree, link_image_normal.from_node, link_image_normal.to_socket)

    mat_num += 1


print(f'Successfully converted {mat_num} materials')
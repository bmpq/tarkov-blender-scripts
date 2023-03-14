import bpy

def get_connected_link(nodes, inputSocket):
    for n in nodes:
        for socket in n.outputs:
            for l in socket.links:
                if l.to_socket == inputSocket:
                    return l
    return None

countfound = 0
for m in bpy.data.materials:
    if m.use_nodes == False:
        continue;
        
    tree = m.node_tree;
    for n1 in tree.nodes:
        if n1.type != "BSDF_PRINCIPLED":
            continue
        
        string = m.name
        separator = '_'
        string = separator.join(string.split(separator)[:-1])
        
        name_variants = ["GLOSS", "gloss", "G", "g", "glos", "GLOS"]
        for to_append in name_variants:
            name_appended = string + separator + to_append
            path = '//' + name_appended + '.png'
            
            tex = None
            try:
                tex = bpy.data.images.load(path)
                print('found texture: ' + name_appended)
                countfound += 1
            except:
                continue
            
            if tex == None:
                continue
            
            tex.colorspace_settings.name = 'Non-Color'
                
            node_tex = tree.nodes.new('ShaderNodeTexImage')
            node_tex.location = n1.location
            node_tex.location.x -= 600
            node_tex.image = tex
            
            node_invert = tree.nodes.new('ShaderNodeInvert')
            node_invert.location = n1.location
            node_invert.location.x -= 300
                
            tree.links.new(node_tex.outputs[0], node_invert.inputs[1])
            tree.links.new(node_invert.outputs[0], n1.inputs[9])
            
            break
        
print(str(countfound) + ' gloss textures found')
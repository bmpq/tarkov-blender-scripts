import bpy

# Threshold value for the vertex coordinate comparison
threshold = 0.0001

# Get all mesh objects in the scene
mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

# Create a dictionary to store objects with matching mesh data
mesh_dict = {}

# Iterate through all mesh objects and group them by mesh data
for obj in mesh_objs:
    mesh_data = obj.data
    verts = [v.co for v in mesh_data.vertices]
    verts_key = tuple([(round(v.x, 4), round(v.y, 4), round(v.z, 4)) for v in verts])
    poly_key = tuple([(f.vertices[0], f.vertices[1], f.vertices[2]) for f in mesh_data.polygons])
    mesh_key = (len(verts), verts_key, poly_key)
    if mesh_key not in mesh_dict:
        mesh_dict[mesh_key] = []
    mesh_dict[mesh_key].append(obj)

# Link object data for objects with matching mesh data
for key, objs in mesh_dict.items():
    if len(objs) > 1:
        for i in range(len(objs) - 1):
            objs[i+1].data = objs[0].data
            print('Linked ' + objs[0].name + ' with ' + objs[i+1].name)
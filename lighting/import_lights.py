import json
import bpy
import math
from mathutils import Quaternion, Euler
from pathlib import Path
import os

POWER_MULTIPLIER = 10

def get_filepath_repo(keyword):
    repo_path = Path(os.path.realpath(bpy.path.abspath(bpy.data.texts['import_lights.py'].filepath))).parent.absolute()
    return str(repo_path) + '/' + keyword

def rot_orient(q):
    bq = Quaternion(q)
    rx = Quaternion([math.sqrt(0.5), -math.sqrt(0.5), 0, 0])
    bq = rx @ bq
    euler = bq.to_euler()
    euler.x *= -1
    euler.y *= -1
    bq = euler.to_quaternion()
    bq.rotate(Euler([0, 0, math.radians(180)]))
    return bq

def pos_orient(list):
    x = list[0]
    y = list[1]
    z = list[2]
    list[0] = -x
    list[1] = -z
    list[2] = y
    return list

def at_zero(loc):
    x_zero = math.isclose(loc[0], 0.0, abs_tol=1e-7)
    z_zero = math.isclose(loc[2], 0.0, abs_tol=1e-7)
    return x_zero and z_zero

with open(get_filepath_repo('lights_factory.json'), 'r') as f:
    light_data = json.load(f)

for light in light_data:
    # blank lights
    if light['intensity'] == 0:
        continue
    
    # pooled lights???
    if at_zero(light['position']):
        continue
    
    light_type = light['type'].upper()
    if light_type == 'DIRECTIONAL':
        light_type = 'SUN'
    light_data_block = bpy.data.lights.new(name=light['name'], type=light_type)
    light_data_block.color = light['color'][:3]
    light_data_block.energy = light['intensity'] * POWER_MULTIPLIER

    if light_type == 'SPOT':
        light_data_block.spot_size = math.radians(light['spotAngle'])
        light_data_block.spot_blend = 1 - (light['innerSpotAngle'] / light['spotAngle'])
        
        # most spotlights are inside the walls
        light_data_block.cycles.cast_shadow = False
        light_data_block.use_shadow = False
        light_data_block.shadow_soft_size = 0.15
        

    light_object = bpy.data.objects.new(light['name'], light_data_block)
    bpy.context.collection.objects.link(light_object)

    light_object.location = pos_orient(light['position'])

    xyzw = light['rotation']
    wxyz = [xyzw[3], xyzw[0], xyzw[1], xyzw[2]]

    light_object.rotation_mode = 'QUATERNION'
    light_object.rotation_quaternion = rot_orient(wxyz)

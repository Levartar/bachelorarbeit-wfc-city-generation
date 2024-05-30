import random
import bpy
import bmesh
from mathutils import Vector
import math

th = bpy.data.texts["generate_tiles_helpers.py"].as_module()

def try_w(mesh_object,group_name,index):
    try:
        return mesh_object.vertex_groups[group_name].weight(index)
    except RuntimeError:
        return 0
        pass

def w_add(mesh_object,group_name,vert_index,add_amount):
    mesh_object.vertex_groups[group_name].add(
        [vert_index], add_amount + try_w(mesh_object,group_name,vert_index), 
        'REPLACE')

### propagate River chooses one adjecant new vert that gets + .5 
### River chance the other adjecant get + .2 chance to all other types
def propagate_river(mesh_object, vert, unset_verts,riv_chance = 0.5):
    riv_vert = random.choice([vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts])
    if riv_vert:
        i = riv_vert.index
        w_add(mesh_object,"river",i,riv_chance)

    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    # add .2 to all types
    for g in mesh_object.vertex_groups:
        for v in v2s:
            w_add(mesh_object,g.name,v.index,0.2)

def propagate_highway(mesh_object, vert, unset_verts,highway_chance = 0.5):
    high_vert = random.choice([vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts])
    i = high_vert.index
    w_add(mesh_object,"highway",i,highway_chance)

    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    # add .2 to all types
    for g in mesh_object.vertex_groups:
        for v in v2s:
            w_add(mesh_object,g.name,v.index,0.2)

def propagate_road(mesh_object, vert, unset_verts,road_chance = 0.7):
    road_vert = random.choice([vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts])
    i = road_vert.index
    w_add(mesh_object,"road",i,road_chance)

    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    # add .2 to houses types
    for v in v2s:
        w_add(mesh_object,"house",v.index,0.2)

    # remove 0.2 from other roads
    for v in v2s:
        w_add(mesh_object,"road",v.index,-0.2)

def propagate_house(mesh_object, vert, unset_verts,house_chance = 0.5):
     # add .5 to house types adjecant
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"house",v.index,house_chance)

    # remove .2 to industrial types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for g in mesh_object.vertex_groups:
        for v in v2s:
            w_add(mesh_object,"industrial",v.index,-0.2)

def propagate_industrial(mesh_object, vert, unset_verts,industrial_chance = 0.5):
    # add .5 to industrial types adjecant
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"industrial",v.index,industrial_chance)

    # remove .2 to houses types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for g in mesh_object.vertex_groups:
        for v in v2s:
            w_add(mesh_object,"house",v.index,-0.2)

def propagate_park(mesh_object, vert, unset_verts,park_chance = 0.2):
    # add .2 to parks types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for g in mesh_object.vertex_groups:
        for v in v2s:
            w_add(mesh_object,"park",v.index,park_chance)
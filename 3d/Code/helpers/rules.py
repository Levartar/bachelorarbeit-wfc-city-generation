import random
import bpy
import bmesh
from mathutils import Vector
import math

th = bpy.data.texts["generate_tiles_helpers.py"].as_module()

#Global vars highest weight picked
riv_chance = 0.5
highway_chance = 0.5
road_chance = 0.5
house_chance = 0.5
industrial_chance = 0.5
park_chance = 0.5
randomness = 0.1

#global vars weight based random
#riv_chance = 1
#highway_chance = 1
#road_chance = 1
#house_chance = 0
#industrial_chance = 0
#park_chance = 0
#randomness = 0

def try_w(mesh_object,group_name,index):
    try:
        return mesh_object.vertex_groups[group_name].weight(index)
    except RuntimeError:
        return 0
        pass

def w_add(mesh_object,group_name,vert_index,add_amount):
    mesh_object.vertex_groups[group_name].add(
        [vert_index], (add_amount + try_w(mesh_object,group_name,vert_index) + random.uniform(-randomness,randomness)), 
        'REPLACE')
        
def get_rand_neigh(vert,unset_verts):
    try:
        return random.choice([vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts])
    except IndexError:
        print("--------------could not find any neighbours---------------")
        return None
        pass

### propagate River chooses one adjecant new vert that gets + .5 
### River chance the other adjecant get + .2 chance to all other types
def propagate_river(mesh_object, vert, unset_verts):
    #remove half riv chance from neighbours
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"river",v.index,riv_chance*0.1)
        w_add(mesh_object,"park",v.index,park_chance)
        
    riv_vert = get_rand_neigh(vert,unset_verts)
    if riv_vert:
        i = riv_vert.index
        w_add(mesh_object,"river",i,riv_chance)
    
#    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]   
#    for g in mesh_object.vertex_groups:
#        for v in v2s:
#            w_add(mesh_object,g.name,v.index,0.05)

def propagate_highway(mesh_object, vert, unset_verts):
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"highway",v.index,-highway_chance*0.1)
        
    high_vert = get_rand_neigh(vert,unset_verts)
    if high_vert:
        i = high_vert.index
        w_add(mesh_object,"highway",i,highway_chance)
        
    road_vert = get_rand_neigh(vert,unset_verts)
    if road_vert:
        i = road_vert.index
        w_add(mesh_object,"road",i,road_chance)

#    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
#    for g in mesh_object.vertex_groups:
#        for v in v2s:
#            w_add(mesh_object,g.name,v.index,0.2)

def propagate_road(mesh_object, vert, unset_verts):
    road_vert = get_rand_neigh(vert,unset_verts)
    if road_vert:
        i = road_vert.index
        w_add(mesh_object,"road",i,road_chance*0.8)
        
    house_vert = get_rand_neigh(vert,unset_verts)
    if house_vert:
        i = house_vert.index
        w_add(mesh_object,"house",i,house_chance-road_chance*0.5)
    
    ind_vert = get_rand_neigh(vert,unset_verts)    
    if ind_vert:
        i = ind_vert.index
        w_add(mesh_object,"industrial",i,industrial_chance*0.7)
        
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    # add .2 to houses types
    for v in v2s:
        w_add(mesh_object,"house",v.index,house_chance*0.5)
        w_add(mesh_object,"highway",v.index,highway_chance*0.2)
        w_add(mesh_object,"road",v.index,road_chance*0.1)

def propagate_house(mesh_object, vert, unset_verts):
     # add .5 to house types adjecant
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"house",v.index,house_chance*0.5)
        w_add(mesh_object,"park",v.index,park_chance)    

    # remove .2 to industrial types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for v in v2s:
        w_add(mesh_object,"industrial",v.index,-industrial_chance)

def propagate_industrial(mesh_object, vert, unset_verts):
    # add industrial to types adjecant
    nvs = [vert for vert in th.get_neigbour_verts(vert) if vert in unset_verts]
    for v in nvs:
        w_add(mesh_object,"industrial",v.index,industrial_chance)
    # remove industrial from further types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for v in v2s:
        w_add(mesh_object,"industrial",v.index,-industrial_chance*0.5)
        w_add(mesh_object,"house",v.index,-house_chance*0.5)
        
    

def propagate_park(mesh_object, vert, unset_verts):
    # add .2 to parks types
    v2s = [vert for vert in th.get_neigbour2_verts(vert) if vert in unset_verts]
    for v in v2s:
        w_add(mesh_object,"park",v.index,park_chance*0.3)
        w_add(mesh_object,"river",v.index,riv_chance*0.1)
        w_add(mesh_object,"road",v.index,road_chance*0.1)
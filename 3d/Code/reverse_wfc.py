import random
import bpy
import bmesh
import time

th = bpy.data.texts["generate_tiles_helpers.py"].as_module()
rules = bpy.data.texts["rules.py"].as_module()
eval = bpy.data.texts["wfc_eval.py"].as_module()

pick_highest = True

def init_vertex_groups(mesh_object:bpy.context.active_object, bmesh):
    #delete_objects_in_collections()
    th.delete_all_vertex_groups(mesh_object)
    print("call init")
    group_names = ["river", # Terrain
                   "highway","road", # Roads
                    # Trains
                   "house", # Residential Buildings
                   "industrial", # Industrial
                   "park" # Infrastructure 
                    ]
    for group_name in group_names:
        mesh_object.vertex_groups.new(name=group_name)
    for vert in bmesh.verts:
        for group_name in group_names:
            rules.w_add(mesh_object,group_name,vert.index,0.5)

def find_most_certain_vert(mesh_object,verts):
    vertex_groups = mesh_object.vertex_groups

    certain_vert = mesh_object.data.vertices[0]
    w_certain = 0
    certain_type = []
    certain_weight = []
    for group in vertex_groups:
        for vert in verts:
            i = vert.index
            try:
                w = mesh_object.vertex_groups[group.name].weight(i)
                #if we get past this line, then the vertex is present in the group
                #try to find the vertex with the highest weight 
                if w > w_certain:
                    w_certain = w
                    certain_vert = vert 
            except RuntimeError:
            # vertex is not in the group
                pass
    #If same certainty then choose randomly
    for group in vertex_groups:
        try:
            w = mesh_object.vertex_groups[group.name].weight(certain_vert.index)

            if pick_highest:
                #this code picks only the highest weight as type
                if w == w_certain:
                    certain_type.append(group.name) 
            else: 
                #this code picks randomly based on weights 
                certain_type.append(group.name)
                certain_weight.append(w)
        except RuntimeError:
            pass
    # return the vert with the highest certainty
    try:
        if pick_highest:
            return certain_vert, random.choice(certain_type), w_certain  
        else:
            return certain_vert, random.choices(certain_type, weights=certain_weight, k=1)[0], w_certain
    except IndexError:
        return certain_vert, "park", w_certain
    
def create_cube_at_certain(vert, color, vg_name = "undefined",cube_size=0.04):
    
    #does mat already exist?
    mat = None
    if vg_name in [m.name for m in bpy.data.materials]:
        mat  = bpy.data.materials.get(vg_name)
    else:
        mat =  th.create_simple_mat(color,vg_name)
            
    #create cube
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=vert.co)
    cube_obj = bpy.context.active_object
    # set cube material
    bpy.context.object.data.materials.append(mat)
    print("placed cube ",vg_name," at ",vert.co)

def  propagate_certainties(mesh_object, vert, 
                           group_name, unset_verts):

    match group_name:
        case "river":
            rules.propagate_river(mesh_object, vert, unset_verts)
            return (0.0,0.0,1.0) # blue
        case "highway":
            rules.propagate_highway(mesh_object, vert, unset_verts)            
            return (0.0,0.0,0.0) # black
        case "road":
            rules.propagate_road(mesh_object, vert, unset_verts)
            return (0.3,0.3,0.3) # grey
        case "house":
            rules.propagate_house(mesh_object, vert, unset_verts)
            return (0.9,0.1,0.0) # red
        case "industrial":
            rules.propagate_industrial(mesh_object, vert, unset_verts)
            return (0.7,0.7,0.0) # yellow
        case "park":
            rules.propagate_park(mesh_object, vert, unset_verts)
            return (0.0,0.9,0.1) # green
        case _:
            return
        
def wfc_rest(unset_verts,mesh_object):
    
    while len(unset_verts)>0:
        unset_verts.ensure_lookup_table()
        vert, type_name, certainty = find_most_certain_vert(mesh_object,
                                                 unset_verts)
        print("vert",vert)                                         
        print("type",type_name)                                         
        color = propagate_certainties(mesh_object, 
                                      vert,type_name,
                                      unset_verts)
        #remove vert from unset verts
        print("vert.index: ",vert.index)
        print("certainty: ",certainty)
        create_cube_at_certain(vert, 
                               color, type_name)
        unset_verts.remove(vert)
        # draw windows visualizes the creation process but takes a lot of time
        # sleep is necessary to let the viewport render 
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
def astar_fill(highw_indices,bm,unset_verts,mesh_object,type_name):
    
    for h_index in highw_indices:
        vert = bm.verts[h_index]
        rules.w_add(mesh_object,type_name,h_index,1)
#        color = propagate_certainties(mesh_object, 
#                                      vert,type_name,
#                                      unset_verts)
#        #remove vert from unset verts
#        create_cube_at_certain(vert, 
#                               color, type_name)
                               
        # draw windows visualizes the creation process but takes a lot of time
        # sleep is necessary to let the viewport render 
#        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)


def reverse_wfc(mesh_object:bpy.context.active_object,size,highways,rivers):
    #Init seach for already set vertices and update certainties for that

    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)

    init_vertex_groups(mesh_object, bm)
    
    #entropy evaluation
    initial_weights = eval.get_vertex_group_weights(mesh_object)
    initial_entropy = {vg: eval.calculate_entropy(weights) for vg, weights in initial_weights.items()}


    unset_verts = bm.verts
    unset_verts.ensure_lookup_table()
    # set random starting points
    except_verts = []
    highways_indices_list = []
    rivers_indices_list = []
    outer_verts = th.get_outer_verts(bm)
   
    for i in range(rivers):
        river_start_v = th.get_random_vert_not_in(outer_verts, except_verts)
        except_verts.append(river_start_v)

        river_end_v = th.get_random_vert_not_in(outer_verts, except_verts)
        except_verts.append(river_end_v)
        
        rivers_indices_list += th.get_shortest_path(bm, river_start_v.index, river_end_v.index)
#    
    for i in range(highways):
        highw_start_v = th.get_random_vert_not_in(outer_verts, except_verts)
        except_verts.append(highw_start_v)
        
        highw_end_v = th.find_closest_vertex_to_center(bm, 0.1)
        except_verts.append(highw_end_v)
        
        highways_indices_list += th.get_shortest_path(bm, highw_start_v.index, highw_end_v.index)
    
    # WFCs go Here
    astar_fill(highways_indices_list,bm,unset_verts,mesh_object,"highway")
    astar_fill(rivers_indices_list,bm,unset_verts,mesh_object,"river")
    
    wfc_rest(unset_verts,mesh_object)
    
    
    #entropy evaluation
    eval.evaluate_quality(mesh_object, initial_entropy)

    bm.free
    print("reverse wfc done")


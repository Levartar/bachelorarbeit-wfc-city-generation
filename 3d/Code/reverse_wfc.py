import random
import bpy
import bmesh
import time

th = bpy.data.texts["generate_tiles_helpers.py"].as_module()
rules = bpy.data.texts["rules.py"].as_module()

def init_vertex_groups(mesh_object:bpy.context.active_object):
    print("call init")
    #delete_objects_in_collections()
    th.delete_all_vertex_groups(mesh_object)
    group_names = ["river", # Terrain
                   "highway","road","bridge", # Roads
                    # Trains
                   "house", # Residential Buildings
                   "industrial", # Industrial
                   "park" # Infrastructure 
                    ]
    for group_name in group_names:
        mesh_object.vertex_groups.new(name=group_name)

def find_most_certain_vert(mesh_object,verts):
    vertex_groups = mesh_object.vertex_groups

    certain_vert = mesh_object.data.vertices[0]
    w_certain = 0
    certain_type = []
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
            if w == w_certain:
                certain_type.append(group.name)   
        except RuntimeError:
            pass
    # return the vert with the highest certainty
    return certain_vert, random.choice(certain_type), w_certain

def create_cube_at_certain(vert, color, vg_name = "undefined",cube_size=0.04):
    
    #does mat already exist?
    mat = None
    if vg_name in [m.name for m in bpy.data.materials]:
        mat  = bpy.data.materials.get(vg_name)
    else:
        mat =  th.create_simple_mat(color,vg_name)

    #create collection
    collection = bpy.data.collections.new("cubes")
    bpy.context.scene.collection.children.link(collection)
            
    #create cube
    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=vert.co)
    #add cube to collection
    cube_obj = bpy.context.active_object
    collection.objects.link(cube_obj)
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


def reverse_wfc(mesh_object:bpy.context.active_object):
    #Init seach for already set vertices and update certainties for that

    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)

    init_vertex_groups(mesh_object)

    unset_verts = bm.verts
    unset_verts.ensure_lookup_table()
    # set random starting points
    outer_verts = th.get_outer_verts(bm)
    river_start_v = outer_verts[random.randint(0,len(outer_verts))]
    rules.propagate_river(mesh_object, river_start_v, unset_verts)
    create_cube_at_certain(unset_verts[river_start_v.index], 
                               (0.0,0.0,1.0), "river")
    unset_verts.remove(river_start_v)

    while len(unset_verts)>0:
        unset_verts.ensure_lookup_table()
        vert, type_name, certainty = find_most_certain_vert(mesh_object,
                                                 unset_verts)
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
        time.sleep(0.11)

    bm.free
    print("reverse wfc done")


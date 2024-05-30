
import random
import bpy
import bmesh

helpers = bpy.data.texts["generate_tiles_helpers.py"].as_module()

def init_vertex_groups(mesh_object:bpy.context.active_object):
    print("call init")
    #delete_objects_in_collections()
    helpers.delete_all_vertex_groups(mesh_object)
    group_names = ["river","lake", # Terrain
                   "highway","road","tram","bus stop","bridge", # Roads
                   "train track","bridge", # Trains
                   "house","apartment building","suburbian home","allotment", # Residential Buildings
                   "industrial", # Industrial
                   "supermarket", "hospital", "school", "swimming pool", "park", "stadion", "cemetery" # Infrastructure 
                    ]
    for group_name in group_names:
        mesh_object.vertex_groups.new(name=group_name)

def generate_river(mesh_object:bpy.context.active_object):
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)

    outer_verts = helpers.get_outer_verts(bm)
    river_start_v = outer_verts[random.randint(0,len(outer_verts))]
    river_verts = [river_start_v] 
    
    print(outer_verts)

    prev = river_start_v
    for start_edge in river_start_v.link_edges:
        for vert in start_edge.verts:
            if vert not in outer_verts:
                river_verts.append(start_edge.other_vert(river_start_v))
                break

    # iterate over mesh and select verts
    while river_verts[len(river_verts)-1] not in outer_verts:
        river_verts.append(helpers.get_lowest_angle_vertex(river_verts[len(river_verts)-1],prev))
        prev = river_verts[len(river_verts)-2]

    # Add verts to vertex group
    #river_vertex_group = mesh_object.vertex_groups.get("river")
    print(river_verts)
    for river_vert in river_verts:
        mesh_object.vertex_groups["river"].add([river_vert.index], 1.0, 'REPLACE')
    
    # Create cubes with blue color    
    helpers.create_cube_at_vertex("river",mesh_object,mat_color=(0.0, 0.0, 1.0))

    bm.free()

def generate_terrain(mesh_object:bpy.context.active_object):
    generate_river(mesh_object)
    return

###-----------------------------------------------### 
###---------------ROADNET_START-------------------###
###-----------------------------------------------### 

def throughway(mesh_object:bpy.context.active_object, outgoing_streets):
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)

    # get a starting point near to the center with a bit of noise
    starting_point_v = helpers.find_closest_vertex_to_center(bm,0.1)
    highway_verts = [starting_point_v]
    outer_verts = helpers.get_outer_verts(bm)
    for i in range(outgoing_streets):
        start_help = starting_point_v.link_edges[random.randint(0,len(starting_point_v.link_edges))-1].other_vert(starting_point_v)
        prev = start_help
        temp_highway_verts = [prev,starting_point_v]
        #get random starting direction
        while temp_highway_verts[len(temp_highway_verts)-1] not in outer_verts:
            next_candidate = helpers.get_lowest_angle_vertex(temp_highway_verts[len(temp_highway_verts)-1],prev)
            current = temp_highway_verts[len(temp_highway_verts)-1]
            # branch highway if random noise 
            if next_candidate in highway_verts and random.uniform(0,1)>0.5:
                print("want to branch")
                for f in current.link_faces:
                    for v in f.verts:
                        if v == next_candidate:
                            for e in f.edges:
                                if current in e.verts and next_candidate not in e.verts:
                                    next_candidate = e.other_vert(current)
                                    break
            # add to temp highway
            temp_highway_verts.append(next_candidate)
            prev = temp_highway_verts[len(temp_highway_verts)-2]
        
        for vert in temp_highway_verts:
            if vert not in highway_verts and vert != start_help:
                highway_verts.append(vert)

    # Add verts to vertex group
    for highway_vert in highway_verts:
        mesh_object.vertex_groups["highway"].add([highway_vert.index], 1.0, 'REPLACE')
    
    # Create cubes with black color    
    helpers.create_cube_at_vertex("highway",mesh_object,mat_color=(0.0, 0.0, 0.0))

    bm.free()
    
def cirlceway(mesh_object:bpy.context.active_object):
    return

def generate_highways(mesh_object:bpy.context.active_object, size):
    size_factor = round(size/10)
    highway_amount = random.randint(size_factor,2*size_factor)
    print("highway_amount",highway_amount)
    throughway(mesh_object,outgoing_streets=highway_amount)    

def generate_roads(mesh_object:bpy.context.active_object):
    print("gen roads")
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)
    #bm.ensure_lookup_table()

    highway_verts_idx = helpers.get_vertices_in_vertex_group(mesh_object,"highway")
    road_verts = []
    
    
    # create a road in every place which is in a specific range of road/highway neighbours
    road_length = 7
    road_clumpyness = 3 # amount of road neighbours that forbidd new road
    needed_neighbours = 2 # the smaller the more random roads get created.
    for i in range(road_length):
        for vert in bm.verts:
            r_nb = 0
            h_nb = 0
            for nv in helpers.get_neigbour2_verts(vert):
                if nv.index in highway_verts_idx:
                    h_nb +=1
                if nv in road_verts:
                    h_nb +=1
            print(r_nb + h_nb)
            if r_nb + h_nb <= road_clumpyness and r_nb + h_nb > needed_neighbours:
                road_verts.append(vert)

#    for v_idx in highway_verts_idx:
#        bm.verts.ensure_lookup_table()
#        vert = bm.verts[v_idx]
#        for edge in vert.link_edges:
#            if not vertex_belongs_to_vertex_group(edge.other_vert(vert),mesh_object):
#                # further from middle roads should not be created
#                if (vert.co-find_closest_vertex_to_center(bm).co).length < get_mesh_dimensions(bm)[0]/4:
#                    print("found_road_vert")
#                    if vert not in road_verts:
#                        road_verts.append(vert)
     
    print(road_verts)    
    
    road_verts_copy = road_verts.copy()          
    
#    for rv in road_verts_copy:
#        t_start = rv
#        print("t_start",t_start) 
#        for i in range(random.randint(1,10)):
#            new_road = random.choice(t_start.link_faces[0].verts)
#            if not vertex_belongs_to_vertex_group(new_road,mesh_object):
#                road_verts.append(new_road)
#            t_start = new_road

    # delete roads that are created too close
#    road_verts_copy = list(road_verts)
#    for rv in road_verts_copy:
#        road_neigbours=0
#        for re in rv.link_edges:
#            if vertex_belongs_to_vertex_group(re.other_vert(rv),mesh_object):
#                road_neigbours += 1
#        if road_neigbours > 3 :
#            road_verts.remove(rv) 
    
    # add verts to vertex group
    for road_vert in road_verts:
        mesh_object.vertex_groups["road"].add([road_vert.index], 1.0, 'REPLACE')

    #create cubes with grey color
    helpers.create_cube_at_vertex("road",mesh_object,mat_color=(0.3, 0.3, 0.3))

    bm.free()

def generate_roadnet(mesh_object:bpy.context.active_object, size:float):
    generate_highways(mesh_object, size)
    generate_roads(mesh_object)

###-----------------------------------------------### 
###---------------ROADNET_END---------------------###
###-----------------------------------------------### 

def generate_industrial_district(mesh_object:bpy.context.active_object, size:float):
    print("gen Industrial")
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    road_verts_idx = helpers.get_vertices_in_vertex_group(mesh_object,"road")
    start_vert = helpers.get_neigbour_verts(bm.verts[random.choice(road_verts_idx)])[0]
    industry_verts = [start_vert]
    for i in range(size):
        for vert in helpers.get_neigbour_verts(start_vert):
            if not helpers.vertex_belongs_to_vertex_group(vert,mesh_object):
                industry_verts.append(vert)
                break
        start_vert = random.choice(helpers.get_neigbour_verts(start_vert))
        
    # add verts to vertex group
    for industry_vert in industry_verts:
        mesh_object.vertex_groups["industrial"].add([industry_vert.index], 1.0, 'REPLACE')

    #create cubes with grey color
    helpers.create_cube_at_vertex("industrial",mesh_object,mat_color=(1.0, 1.0, 0.0))

    bm.free()
        
    
    
def generate_houses(mesh_object:bpy.context.active_object):
    print("gen residential housing")
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    road_verts_idx = helpers.get_vertices_in_vertex_group(mesh_object,"road")
    house_verts = []
    for vert_idx in road_verts_idx:
        vert = bm.verts[vert_idx]
        for n in helpers.get_neigbour_verts(vert):
            if not helpers.vertex_belongs_to_vertex_group(n,mesh_object):
                house_verts.append(n)

            
    # add verts to vertex group
    for house_vert in house_verts:
        mesh_object.vertex_groups["house"].add([house_vert.index], 1.0, 'REPLACE')

    #create cubes with grey color
    helpers.create_cube_at_vertex("house",mesh_object,mat_color=(1.0, 0.1, 0.1))

    bm.free()
    
    
def generate_parks(mesh_object:bpy.context.active_object):
    print("gen residential housing")
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    park_verts = []
    for vert in bm.verts:
        if not helpers.vertex_belongs_to_vertex_group(vert,mesh_object):
                park_verts.append(vert)

            
    # add verts to vertex group
    for park_vert in park_verts:
        mesh_object.vertex_groups["park"].add([park_vert.index], 1.0, 'REPLACE')

    #create cubes with grey color
    helpers.create_cube_at_vertex("park",mesh_object,mat_color=(0.0, 1.0, 0.1))

    bm.free()

import random
import bpy
import bmesh
from mathutils import Vector
import math

def get_mesh_dimensions(mesh_object:bpy.types.Mesh):
    mesh = mesh_object

    # Get the bounding box dimensions of the mesh
    bounding_box = [v.co for v in mesh.verts]
    min_x = min(bounding_box, key=lambda x: x[0])[0]
    max_x = max(bounding_box, key=lambda x: x[0])[0]
    min_y = min(bounding_box, key=lambda x: x[1])[1]
    max_y = max(bounding_box, key=lambda x: x[1])[1]
    min_z = min(bounding_box, key=lambda x: x[2])[2]
    max_z = max(bounding_box, key=lambda x: x[2])[2]

    # Calculate dimensions (size) of the mesh
    width = max_x - min_x
    height = max_y - min_y
    depth = max_z - min_z

    return width, height, depth

def create_simple_mat(mat_color, material_name="SimpleMaterial", alpha=1.0):
    mat = bpy.data.materials.new(name=material_name)
    mat.diffuse_color = mat_color + (alpha,)
    return mat

def get_outer_verts(bmesh):
    outer_verts = []
    for edge in bmesh.edges:
        if edge.is_boundary:
            for vert in edge.verts:
                outer_verts.append(vert)
    return outer_verts

def get_lowest_angle_vertex(current_vertex, prev_vertex):
    # Initialize variables for tracking the lowest angle and the corresponding vertex
        lowest_angle = math.pi  # Initialize to pi (180 degrees)
        lowest_angle_vertex = None

        # Loop through the edges of the current vertex
        for edge in current_vertex.link_edges:
            # Get the other vertex connected to the current vertex via the edge
            connected_vertex = edge.other_vert(current_vertex)

            # Check if the connected vertex is not the previous vertex
            if connected_vertex != prev_vertex:
                # Calculate the angle between the edge and the vector from the current vertex to the connected vertex
                edge_vector = (current_vertex.co - connected_vertex.co).normalized()
                prev_vector = (prev_vertex.co - current_vertex.co).normalized()
                angle = edge_vector.angle(prev_vector)

                # Update the lowest angle and corresponding vertex if the current angle is lower
                if angle < lowest_angle:
                    lowest_angle = angle
                    lowest_angle_vertex = connected_vertex

        return lowest_angle_vertex

def find_closest_vertex_to_center(mesh:bmesh, noise = 0):

    # Calculate the mesh center
    verts = [v.co for v in mesh.verts]
    mesh_center = sum(verts, Vector()) / len(verts)

    # Initialize variables to store the closest vertex and its distance
    closest_vertex = None
    min_distance = float('inf')

    # Iterate through all vertices
    for vertex in mesh.verts:
        # Calculate the distance between the vertex and the mesh center
        distance = (vertex.co - mesh_center).length

        # Update the closest vertex and its distance if needed
        # add noise to get more random verts
        rand_noise = random.uniform(0, noise*0.5*get_mesh_dimensions(mesh)[0])
        if distance < min_distance + rand_noise:
            min_distance = distance
            closest_vertex = vertex

    return closest_vertex

def get_vertices_in_vertex_group(mesh_object, vertex_group_name):
    # index is an integer representing the index of the vertex group in a
    vg_idx = mesh_object.vertex_groups.get(vertex_group_name).index
    o = mesh_object
    vs = [ v for v in o.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
    return vs

def vertex_belongs_to_vertex_group(vertex:bmesh.types.BMVert, mesh_object:bpy.context.active_object):
    # Get the vertex groups of the mesh object
    vertex_groups = mesh_object.vertex_groups

    obj=mesh_object
    data=obj.data
    verts=data.vertices

    # Iterate over each vertex group
    for group in vertex_groups:
        # Check if the vertex belongs to the current vertex group
        for vert in verts:
            i=vert.index
            try:
                obj.vertex_groups[group.name].weight(i)
                #if we get past this line, then the vertex is present in the group
                return True         
            except RuntimeError:
            # vertex is not in the group
                pass
    return False

def delete_objects_in_collections():
    # Get all collections in the scene
    collections = bpy.context.scene.collection.children

    # Iterate over each collection
    for collection in collections:
        # Check if the collection name starts with "cubes"
        if collection.name.startswith("cubes"):
            # Iterate over each object in the collection
            for obj in collection.objects:
                # Delete the object
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)
    
def delete_all_vertex_groups(mesh_object:bpy.context.active_object):
    print("call delete vertex groups")
    # Delete all vertex groups
    for group in mesh_object.vertex_groups:
        mesh_object.vertex_groups.remove(group)

def create_cube_at_vertex(vertex_group_name,mesh_object,mat_color,cube_size=0.04):
    # Get the active object (assuming it's a mesh)
    if mesh_object and mesh_object.type == 'MESH':
        # Get the mesh data
        mesh = mesh_object.data
        
        # Get the vertex group named vertex_group_name
        vertex_group = mesh_object.vertex_groups.get(vertex_group_name)
        
        if vertex_group:
            # Get the indices of vertices in the group
            vertex_indices = [v.index for v in mesh.vertices if vertex_group.index in [vg.group for vg in v.groups]]
            
            mat = create_simple_mat(mat_color,vertex_group_name)

            #create collection
            collection = bpy.data.collections.new("cubes")
            bpy.context.scene.collection.children.link(collection)
            
            # Create a cube for each vertex in the group
            for vertex_index in vertex_indices:
                # Get the vertex coordinates
                vertex_coords = mesh.vertices[vertex_index].co
                
                # Create a cube object at the vertex coordinates
                bpy.ops.mesh.primitive_cube_add(size=cube_size, location=vertex_coords)
                #add cube to collection
                cube_obj = bpy.context.active_object
                collection.objects.link(cube_obj)
                # set cube material
                bpy.context.object.data.materials.append(mat)

        else:
            print("Vertex group '{}' not found.".format(vertex_group_name))
    else:
        print("The active object is not a mesh.") 

def get_neigbour_verts(vert):
    neighbour = []
    for edges in vert.link_edges:
        neighbour.append(edges.other_vert(vert))
    return neighbour

def get_neigbour2_verts(vert):
    neighbour = []
    for edges in vert.link_edges:
        v2 = edges.other_vert(vert)
        for e2 in v2.link_edges:
            candidate = e2.other_vert(v2)
            if candidate not in neighbour:
                neighbour.append(e2.other_vert(v2))
        neighbour.append(v2)
    return neighbour       
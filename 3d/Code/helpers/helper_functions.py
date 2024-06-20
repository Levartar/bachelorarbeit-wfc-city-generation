import random
import bpy
import bmesh
import math
from mathutils import Vector
import math

def distance_vec(point1: Vector, point2: Vector) -> float: 
    """Calculate distance between two points.""" 
    return (point2 - point1).length

def rot_vec(vector: Vector, axis_vector: Vector, angle_rad: float) -> Vector:
    return (vector*math.cos(angle_rad)+(axis_vector.cross(vector))*math.sin(angle_rad)+axis_vector*(axis_vector*vector)*(1-math.cos(angle_rad)))

def nearest_neighbour(vector: Vector, neighbours: bmesh.types.BMVertSeq) -> bmesh.types.BMVert:
    neighbours.ensure_lookup_table()
    nearest = min(neighbours, key=lambda v: (v.co - vector.co).length)
    return nearest

def furthest_neighbour(vector: Vector, neighbours: bmesh.types.BMVertSeq) -> bmesh.types.BMVert:
    neighbours.ensure_lookup_table()
    furthest = max(neighbours, key=lambda v: (v.co - vector.co).length)
    return furthest

def triangulated_to_quad(mesh_object):
    """
    Convert a triangulated mesh to a quad mesh by randomly dissolving edges.

    Parameters:
    - mesh_object: Blender mesh object
    """

    # Get the mesh data
    mesh = mesh_object.data

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Ensure all faces are triangles
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    # Switch to edge select mode
    bpy.context.tool_settings.mesh_select_mode = (False, True, False)
    
    bpy.ops.mesh.select_all(action='DESELECT')

    # Select a random subset of edges to dissolve
    bm = bmesh.from_edit_mesh(mesh_object.data)
    # shuffle List to reduce repeating patterns
    shuffledEdges = list(bm.edges)
    random.shuffle(shuffledEdges)
    
    for e in shuffledEdges:
        edge_available = True
        for f in e.link_faces:
            for inner_face_edge in f.edges:
                if inner_face_edge.select == True:
                    edge_available = False
        if edge_available:
            e.select = True
            
   # Dissolve selected edges
    bpy.ops.mesh.dissolve_edges()
    
    # Subdivide Mesh to remove leftover tris
    bpy.ops.object.modifier_add(type="SUBSURF")

    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply Modifier
    for modifier in mesh_object.modifiers:
        if modifier.type == 'SUBSURF':
            bpy.ops.object.modifier_apply(
                modifier=modifier.name
            )

def smooth_quads(mesh_object, iterations=1, strength=0.1):
    mesh = mesh_object.data
    bm = bmesh.new() # copy mesh for iterating
    bm.from_mesh(mesh)

    # Calculate average edge length for the entire mesh
    total_length = sum(edge.calc_length() for edge in bm.edges)
    average_edge_length = total_length / len(bm.edges) if len(bm.edges) > 0 else 1.0

    for i in range(iterations):
        print("debug begin:")
        for f in bm.faces:
            f_middle_co = f.calc_center_bounds()
            print("Face Middle Coords", f_middle_co)
            # f_sidelength_target = (f.calc_perimeter()/4) # Solllänge des quads 
            
            #create target square on top of face center
            face_dia_tangent = f.calc_tangent_edge_diagonal()
            print("diag_tangent",face_dia_tangent)
            target_square = bmesh.new() 
            for r in [2*math.pi,math.pi/2,math.pi,(3*math.pi)/2]: # Radianten für die rotation um jeweils 90°
                half_diag_length = math.sqrt(2*(average_edge_length/2)**2)
                new_vert = f_middle_co+rot_vec(face_dia_tangent,f.normal,r)*half_diag_length
                target_square.verts.new(new_vert)
                print("target_verts",new_vert,"rot",r)
                
            # match closest square vertices with quad vertices
            # get 2 furthest vertices
            for v in f.verts:
                return
            for v in f.verts: 
                print("------")
                print("vertex",v.co)
                nearest = nearest_neighbour(v,target_square.verts)
                v.co += (nearest.co - v.co)*strength
                target_square.verts.remove(nearest)
                #bm.faces[i].verts[n].co += lambda_factor*(new_point_target-v.co) # Write changes onto used face coordinates
            target_square.free()

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()
    
def create_subd_plane(size = 5):
    # Create a new mesh object (plane)
    bpy.ops.mesh.primitive_plane_add(size=size/10)

    # Subdivide the plane without deforming it
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=size-2)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Select the plane
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.active_object.select_set(True)
    
    bpy.context.active_object.display_type = 'WIRE'
    
    # Force Blender to update the viewport
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
import bpy
import bmesh
import random
    
helpers = bpy.data.texts["helper_functions.py"].as_module()
tiles = bpy.data.texts["generate_tiles_helpers.py"].as_module()
r_wfc = bpy.data.texts["reverse_wfc.py"].as_module()


size = 20
helpers.create_subd_plane(size)

# Get the selected object (assuming it's a mesh)
obj = bpy.context.active_object
if obj.type != 'MESH':
    raise ValueError("Selected object is not a mesh")

helpers.triangulated_to_quad(obj)
#helpers.smooth_quads(obj)
#tiles.init_vertex_groups(obj)
#tiles.generate_river(obj)
#tiles.generate_roadnet(obj, size)
#tiles.generate_industrial_district(obj, size)
#tiles.generate_houses(obj)
#tiles.generate_parks(obj)
r_wfc.reverse_wfc(obj)

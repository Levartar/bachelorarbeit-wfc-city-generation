import bpy
import os, sys

filename = os.path.join(os.path.dirname(bpy.data.filepath), ".\\Code\\Organic_grids.py")
exec(compile(open(filename).read(), filename, 'exec'))
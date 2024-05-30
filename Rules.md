Tile-class-generation
Inputs to work with: 
- what class have adjecant verts

### Terrain:
Gewässer:

Fluss:
	- start on edge
	- walk least sharp edge
	- end on edge

Highway
	- start near middle
	- walk least sharp edge
	- avoid other highways
	- end on edge

Road
	- start next to highway
	- have no more than 3 roads next to it
	- connect to other road if next to it

Industry
	- start next to random road
	- generate next to starting point
	- avoid other tiles
	- 
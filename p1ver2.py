import math
import networkx as nx
import matplotlib.pyplot as plt


##Class Definitions##
#The follwing is a class of a station, will be used as nodes
class Station(object):
    """Makes a Station"""
    def __init__(self, num, reloading_buildings, ship_in):
        self.num = num
        self.reloading_buildings = reloading_buildings
        self.ship_in = ship_in
    def displayinfo(self):
    	print('Station {0} has {1} reloading buildings and {2} incoming \
    		shipments'.format(self.num,self.reloading_buildings,self.ship_in))
    def fill(self,shipment_array):
    	"""takes a list of shipments, adds them to ship_in"""
    	for itr, item in enumerate(shipment_array):
    		for i in range(0,len(item.paths)):
    			if self.num in item.paths[i]:
    				self.ship_in += item.path_vols[i]
    	

#railroad class, used as edge
class Track(object):
	"""Conains info about a track"""
	def __init__(self, is_built, load):
		self.is_built = is_built
		self.load = load

class Shipment(object):
	"""Contains a shipment and its path"""
	def __init__(self, origin, destination, total_volume, paths, path_vols):
		self.origin = origin
		self.destination = destination
		self.total_volume = total_volume
		self.paths = paths
		self.path_vols = path_vols


##Data
stations_data = [[50,	0,		1,	0],
				 [250,	0,		1,	0],
				 [100,	50,		2,	0],
				 [0,	100,	3,	0],
				 [200,	100,	2,	0],
				 [100,	200,	2,	0],
				 [200,	200,	3,	0]]

track_data = [	[1,3,1],
				[1,4,1],
				[2,5,1],
				[3,5,1],
				[4,6,1],
				[5,7,1],
				[6,7,1]]

#paths
path = [[4,6,7],[4,1,3,5,7]]
vol = [8,3]
A = Shipment(4,7,11,path,vol)

path = [[3,5,2]]
vol = [3]
B = Shipment(3,2,3,path,vol)




###ititialize the network####
Net = nx.MultiDiGraph()
#add all the stations
for i in range(0,len(stations_data)):
	Net.add_node(i + 1, obj = Station(i + 1, stations_data[i][2],stations_data[i][3]))

#add the existing tracks 
for i in range(0,len(track_data)):
	for j in range(0,track_data[i][2]):
		Net.add_edge(track_data[i][0],track_data[i][1], Track(1,0))
###########################

###Add potential tracks###########

for i,x in enumerate(stations_data):
	for j,y in enumerate(stations_data):
		dist = math.hypot(x[0] - y[0], x[1] - y[1])
		if (dist<=220)&(dist != 0):
			Net.add_edge(i+1,j+1, Track(0,0))

test = nx.get_node_attributes(Net,'obj')
print(test[1].ship_in)
test[1].fill([A,B])
print(test[1].ship_in)

nx.draw(Net)
plt.savefig("path.png")
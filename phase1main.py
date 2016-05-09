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
	def __init__(self, origin, destination, is_built, load, stations_data):
		self.is_built = is_built
		self.load = load
		self.origin = origin
		self.destination = destination
		self.sd = stations_data
	def fill(self, shipment_array):
		for itr, item in enumerate(shipment_array):
			for i in range(0,len(item.paths)):
				for x in item.paths[i]:
					for y in item.paths[i]:
						if (x == self.origin) and (y == self.destination):
							self.load += item.path_vols[i]

	
	

class Shipment(object):
	"""Contains a shipment and its path"""
	def __init__(self, origin, destination, total_volume, paths, path_vols):
		self.origin = origin
		self.destination = destination
		self.total_volume = total_volume
		self.paths = paths
		self.path_vols = path_vols
	def cost(self,cost_reloading_building, cost_per_mile_track, cost_per_mile_line):
		for i in range(0,len(self.paths)):
			for j in range(0,len(i)):
				pass
			
##Function Definitions				
def UpdateTrackCost(Net, rscost):
	"takes a network and reloading_buildings cost and returns a \
	network with cost parameters instead of objects on the edges"
	for i in Net.nodes():
		for j in Net.nodes():
			x = Net.get_edge_data(i,j)
			if type(x) is dict:
				print(x['obj'].is_built)

##Data
rscost = 1000000

stations_data = [[50,	0,		1,	0],
				 [250,	0,		1,	0],
				 [100,	50,		2,	0],
				 [0,	100,	3,	0],
				 [200,	100,	2,	0],
				 [100,	200,	2,	0],
				 [200,	200,	3,	0]]

track_data = [	[1,3,1],
				[4,1,1],
				[5,2,1],
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

# path = [[4,1,3,5,2],[4,6,7,5,2]]
# vol = [5,2] 
# C = Shipment(4,2,7,path,vol)



###ititialize the network####
Net = nx.MultiDiGraph()
#add all the stations
for i in range(0,len(stations_data)):
	Net.add_node(i + 1, \
		obj = Station(i + 1, stations_data[i][2],stations_data[i][3]))

#add the existing tracks 
for i in range(0,len(track_data)):
	for j in range(0,track_data[i][2]):
		Net.add_edge(track_data[i][0],track_data[i][1], \
			obj = Track(track_data[i][0],track_data[i][1],1,0,stations_data))
###########################

###Add potential tracks###########

for i,x in enumerate(stations_data):
	for j,y in enumerate(stations_data):
		dist = math.hypot(x[0] - y[0], x[1] - y[1])
		if (dist<=220)&(dist != 0)&(~Net.has_edge(i+1,j+1)):
			Net.add_edge(i+1,j+1, obj = Track(i+1,j+1,0,0,stations_data))
			

################################


#################################33
###Need to figure out how to put shipment data in?	

for x in Net.nodes():
	nx.get_node_attributes(Net,'obj')[1].fill([A,B])
	print(nx.get_node_attributes(Net,'obj')[1].ship_in) #for debuging


for x in Net.edges():
	Net.get_edge_data(x[0],x[1])[0]['obj'].fill([A,B])
	print(Net.get_edge_data(x[0],x[1])[0]['obj'].load) #for debuging
###########################3






#create a psuedonetwork for shortest path purposes
pNet = nx.MultiDiGraph()
cost_dictionary = {}
#iterate through the real network, calculate costs, build the psuedonetwork
for i in Net.nodes():
	for j in Net.nodes():
		x = Net.get_edge_data(i,j)
		if type(x) is dict:
			#iterate through each edge in dictionary of edges along that path
			for key in x:
				#cost tracks cost of traversing this edge
				cost = 0
				#if no edges along the path are built
				if all(x[key]['obj'].is_built == 0 for key in x):
					#calculate distance
					dist = math.hypot(stations_data[i-1][0] - stations_data[j-1][0], \
						stations_data[i-1][1] - stations_data[j-1][1])
					#multiply distance by 7000 and add to cost
					cost += (7000 + 5000)*dist
				
				#if line built but at capacity, need to build another so add that cost
				if (x[key]['obj'].load + 1) > 10:
					#calculate distance
					dist = math.hypot(stations_data[i-1][0] - stations_data[j-1][0], \
						stations_data[i-1][1] - stations_data[j-1][1])
					#multiply distance by 5000 and add to cost
					cost += 5000*dist

				#if not enough reloading stations at destination, add that cost
				if 5*nx.get_node_attributes(Net,'obj')[j].reloading_buildings < \
					(nx.get_node_attributes(Net,'obj')[j].ship_in + 1):
					#rscost is reloading station cost
					cost += rscost
				if pNet.has_edge(i,j):
					pass
				pNet.add_edge(i, j, weight=cost)
				cost_dictionary['{0}--->{1}'.format(i,j)] = cost


nx.draw(pNet)







def CheapestPath(pNet, origin, destination, depth):
	"Iterates through every simple path calculating cost and finds the cheapest"
	cost_path_dict = {}
	for path in nx.all_simple_paths(pNet, source=origin, target=destination, cutoff = depth):
		cost = 0
		for i in range(0,len(path) - 1):
			cost += cost_dictionary['{0}--->{1}'.format(path[i],path[i +1])]
		cost_path_dict[cost] = path

	print('Cheapest Path from {0} to {1} is {2} at ${3}'.format(origin,destination,\
		cost_path_dict[min(list(cost_path_dict.keys()))], \
		min(list(cost_path_dict.keys()))))



####this is the what runs:
CheapestPath(pNet, 4,2,7)



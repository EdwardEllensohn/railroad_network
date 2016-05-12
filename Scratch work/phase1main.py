#IEMS 313 Project Phase 1
#
#Eddie, Jack, Vicky 



#Writen for Python 3.5.1 :: Anaconda 4.0.0 (64-bit)

#Should work with any python 3 distribution with networkx library 
import math
import networkx as nx





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
	def update(self, path):
		if path in self.paths:
			for itr, i in enumerate(self.paths):
				if i == path:
					x = itr 
			self.path_vols[x] += 1
		else:
			self.paths.append(path)
			self.path_vols.append(1)
	def displayinfo(self):
		print('Shipment from {0} to {1} with total volume {2}:'.format(\
			self.origin, self.destination, self.total_volume))
		for itr, item in enumerate(self.paths):
			print('  Path {0}: {1} with volume {2}'.format(itr+1, \
				item, self.path_vols[itr]))
			

###Function Definitions


def initNetwork(shipment_list):
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
	### Add current shipments#################
	for x in Net.nodes():
		nx.get_node_attributes(Net,'obj')[x].fill(shipment_list)
		#print(nx.get_node_attributes(Net,'obj')[x].ship_in) #for debuging


	for x in Net.edges():
		Net.get_edge_data(x[0],x[1])[0]['obj'].fill(shipment_list)
		#print(Net.get_edge_data(x[0],x[1])[0]['obj'].load) #for debuging
	###########################3
	return Net







def costUpdate(Net):
	global rscost
	global stations_data
	global track_data
	#create a psuedonetwork for shortest path purposes
	pNet = nx.MultiDiGraph()
	cost_dictionary = {}
	#iterate through the real network, calculate costs, build the psuedonetwork
	for i in Net.nodes():
		for j in Net.nodes():
			x = Net.get_edge_data(i,j)
			if type(x) is dict:
				#cost tracks cost of traversing this edge
				cost = 0
				#if no edges along the path are built
				y = Net.get_edge_data(j,i)
				if (type(y) is dict and all(y[key]['obj'].is_built == 0 for key in y) ) and (all(x[key]['obj'].is_built == 0 for key in x)):
					#calculate distance
					dist = math.hypot(stations_data[i-1][0] - stations_data[j-1][0], \
						stations_data[i-1][1] - stations_data[j-1][1])
					#multiply distance by 7000+5000 and add to cost
					cost += (7000 + 5000)*dist
				
				#if line built but at capacity, need to build another so add that cost
				elif all((x[key]['obj'].load + 1) > 10 for key in x) or  (all(x[key]['obj'].is_built == 0 for key in x)):
					#calculate distance
					dist = math.hypot(stations_data[i-1][0] - stations_data[j-1][0], \
						stations_data[i-1][1] - stations_data[j-1][1])
					#multiply distance by 5000 and add to cost
					cost += 5000*dist
				if 5*(nx.get_node_attributes(Net,'obj')[j].reloading_buildings) < \
					(nx.get_node_attributes(Net,'obj')[j].ship_in + 1):
					#rscost is reloading station cost
					cost += rscost
				pNet.add_edge(i, j, weight=cost)
				cost_dictionary['{0}--->{1}'.format(i,j)] = cost
	return [pNet,cost_dictionary]






def CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth):
	global rscost
	global stations_data
	global track_data
	"Iterates through every simple path calculating cost and finds the cheapest"
	cost_path_dict = {}
	build_flag_dict = {}
	for path in nx.all_simple_paths(pNet, source=origin, target=destination, cutoff = depth):
		cost = 0
		build_flag = 0
		#check if we need to add cost of reloading buildings for start nodes
		if (5*(nx.get_node_attributes(Net,'obj')[path[0]].reloading_buildings)) < (nx.get_node_attributes(Net,'obj')[path[0]].ship_in + 1):
			#rscost is cost of adding reloading station
			cost += rscost
			build_flag = 1
		for i in range(0,len(path) - 1):
			cost += cost_dictionary['{0}--->{1}'.format(path[i],path[i +1])]
		cost_path_dict[cost] = path
		build_flag_dict[cost] = build_flag
	##find cheapest path and its cost
	ccost = min(list(cost_path_dict.keys()))
	cpath = cost_path_dict[ccost]
	print('For next additional unit, Cheapest Path from {0} to {1} is {2} at ${3}'.format(origin,destination,\
		cpath, ccost))
	#check if we needed to build a reloading station at start node
	if build_flag_dict[ccost] == 1:
		stations_data[cpath[0]-1][2] += 1
		print('  -build reloading building at station {0}'\
			.format(cpath[0]))
	##find recomendations based on that path
	for i in range(0,len(cpath) - 1):
		x = Net.get_edge_data(cpath[i],cpath[i+1])
		if type(x) is dict:
			#if no edges along the path are built
			y = Net.get_edge_data(cpath[i+1], cpath[i])
			if (type(y) is dict and all(y[key]['obj'].is_built == 0 for key in y) ) and all(x[key]['obj'].is_built == 0 for key in x):
				print('  -build path and track from {0} to {1}'\
					.format(cpath[i],cpath[i+1]))
				track_data.append([cpath[i],cpath[i+1],1])
			
			#if line built but at capacity, need to build another so add that cost
			elif all((x[key]['obj'].load + 1) > 10 for key in x) or all(x[key]['obj'].is_built == 0 for key in x):
				print('  -build track from {0} to {1}'\
					.format(cpath[i],cpath[i+1]))
				track_data.append([cpath[i],cpath[i+1],1])
			#iterate through each edge in dictionary of edges along that path
			#print(x) #print edge objects for debuging
			#track reloading buildings added
			rl_added = 0
			for key in x:
				#if not enough reloading stations at destination, add that cost
				if 5*(nx.get_node_attributes(Net,'obj')[cpath[i+1]].reloading_buildings+rl_added) < \
					(nx.get_node_attributes(Net,'obj')[cpath[i+1]].ship_in + 1):
					print('  -build reloading building at station {0}'\
						.format(cpath[i+1]))
					stations_data[cpath[i+1]-1][2] += 1
					rl_added += 1

	return 	[origin, destination, cpath, ccost]


def addShipment(shipment_list, depth):
	global rscost
	global stations_data
	global track_data
	origin = int(input('Enter starting Station:'))
	destination = int(input('Enter ending Station:'))
	size = int(input('Enter Shipment size:'))
	new_shipment = Shipment(origin, destination, size, [], [])
	total_cost = 0
	Net = initNetwork(shipment_list)
	[a,b] = costUpdate(Net)
	pNet = a
	cost_dictionary = b
	[origin, destination, cpath, ccost] = CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth)
	new_shipment.update(cpath)
	total_cost += ccost
	for i in range(1,size):
		shipment_list.append(new_shipment)
		Net = initNetwork(shipment_list)
		shipment_list.pop()
		[a,b] = costUpdate(Net)
		pNet = a
		cost_dictionary = b
		[origin, destination, cpath, ccost] = CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth)
		new_shipment.update(cpath)
		total_cost += ccost
	print('total cost of addition: ${0}'.format(total_cost))
	shipment_list.append(new_shipment)
	return shipment_list



#################Data################################
## You can change these data for different situations, set for 
#       initial condition in phase 1 


#Reloading building cost
rscost = 1000000

#station data from assignment(xcoordinate, ycoordinate, num reloading buildings, initial incoming load (set to zero))
stations_data = [[50,	0,		1,	0],
				 [250,	0,		1,	0],
				 [100,	50,		2,	0],
				 [0,	100,	3,	0],
				 [200,	100,	2,	0],
				 [100,	200,	2,	0],
				 [200,	200,	3,	0]]

#Track data from assignment (origin, destination, number of tracks on that path)
track_data = [	[1,3,1],
				[4,1,1],
				[5,2,1],
				[3,5,1],
				[4,6,1],
				[5,7,1],
				[6,7,1]]

#Shipments to be added to network defined with shipment object
path = [[4,6,7],[4,1,3,5,7]]
vol = [8,3]
A = Shipment(4,7,11,path,vol)

path = [[3,5,2]]
vol = [3] 
B = Shipment(3,2,3,path,vol)


############################################################################


###RUN THE HEURISTIC:


shipment_list = [A,B]
sd = int(input('Max Path Length: '))
while 1:
	#addShipment adds a shipment to the network derived from the above data
	#--first argument is a list of the  current shipments on the network
	#--second argument controls how long of a path the heuristic looks for 
	#        (Warning: second argument has an outsized effect on run time
	#                  and higher search depths do not necissarily yield 
	#                  better solutions
	
	shipment_list = addShipment(shipment_list,sd)

	#print the shipments on the network for easy viewing 
	print('\nList of all shipments on Network:')
	for i in shipment_list:
		i.displayinfo()
	#ask the user if they want to add another shipment or not
	x = input('Add another shipment? (type "yes" to continue):')
	print(x)
	if x == 'yes':
		print('\nNext iteration:')
	else:
		print('\nHave a nice day :)')
		break




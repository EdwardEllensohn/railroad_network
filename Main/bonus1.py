#IEMS 313 Project Phase 1
#
#Eddie, Jack, Vicky 



#Writen for Python 3.5.1 :: Anaconda 4.0.0 (64-bit)

#Should work with any python 3 distribution with networkx library 
import math
import networkx as nx





#####Class Definitions#####

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
    def fill(self,shipment_list):
    	"""takes a list of shipments, adds them to ship_in"""
    	for item in shipment_list:
    		for i in range(0,len(item.paths)):
    			if self.num in item.paths[i]:
    				self.ship_in += item.path_vols[i]
    	

#railroad track class, used as edge data
class Track(object):
	"""Conains info about a track"""
	def __init__(self, origin, destination, is_built, load, stations_data):
		self.is_built = is_built
		self.load = load
		self.origin = origin
		self.destination = destination
		self.sd = stations_data
	def fill(self, shipment_list, Net):
		"Experimental fill method"
		for shipment in shipment_list:
			for itr, path in enumerate(shipment.paths):
				for i in range(0,len(path)-1):
					if (path[i] == self.origin) and (path[i+1] == self.destination):
						self.load += shipment.path_vols[itr]
						self.is_built = 1
						if Net.has_edge(self.destination, self.origin):
							for post in Net.edges(path[i+1],path[i],keys = True):
								if type(post) == dict and post[3]['obj'].is_built == 0:
									#Net.remove_edge(post[0],post[1],key=post[2])
									print('hi')
									break
		return Net

#Shipment class that stores shipment data as given in assignment
class Shipment(object):
	"""Contains a shipment and its path"""
	def __init__(self, origin, destination, total_volume, paths, path_vols):
		self.origin = origin
		self.destination = destination
		self.total_volume = total_volume
		self.paths = paths
		self.path_vols = path_vols
	def update(self, path):
		"updates the data with an additional path"
		if path in self.paths:
			for itr, i in enumerate(self.paths):
				if i == path:
					x = itr 
			self.path_vols[x] += 1
		else:
			self.paths.append(path)
			self.path_vols.append(1)
	def displayinfo(self):
		"displays all relavent information about the shipment"
		print('Shipment from {0} to {1} with total volume {2}:'.format(\
			self.origin, self.destination, self.total_volume))
		for itr, item in enumerate(self.paths):
			print('  Path {0}: {1} with volume {2}'.format(itr+1, \
				item, self.path_vols[itr]))
			

#########Function Definitions############


def initNetwork(shipment_list):
	"funcion initializes a network given a list of shipment objects"
	###ititialize the network####
	Net = nx.MultiDiGraph()
	#add all the stations
	for itr, item in enumerate(stations_data):
		Net.add_node(itr + 1, obj = Station(itr + 1, item[2], item[3]))

	#add the existing tracks 
	for itr, item in enumerate(track_data):
		for j in range(0,item[2]):
			Net.add_edge(item[0],item[1], obj = Track(item[0],item[1],0,0,stations_data))
			Net.add_edge(item[1],item[0], obj = Track(item[1],item[0],0,0,stations_data))


	###########################

	###Add potential tracks###########


	for i,x in enumerate(stations_data):
		for j,y in enumerate(stations_data):
			dist = math.hypot(x[0] - y[0], x[1] - y[1])
			#only add tracks under 220 between unique edges
			if (dist<=220)&(dist != 0)&(~Net.has_edge(i+1,j+1)):
				#add an unbuilt edge that may be filled later
				Net.add_edge(i+1,j+1, obj = Track(i+1,j+1,0,0,stations_data))

	#################################33
	### Use a list of shipment objects to define object data values in network#################

	#update the node objects
	for x in Net.nodes():
		nx.get_node_attributes(Net,'obj')[x].fill(shipment_list)
		#print(nx.get_node_attributes(Net,'obj')[x].ship_in) #for debuging

	#update teh edge objects
	for (a,b,obj) in Net.edges(data = 'obj'):
		#some debuging code:
		#Net = obj.fill(shipment_list, Net)
		#print(Net.get_edge_data(x[0],x[1])[0]['obj'].load) #for debuging
		#print(obj)

		#loop through the shipments
		for shipment in shipment_list:
			#loop through the paths in the shipments
			for itr, path in enumerate(shipment.paths):
				#loop through all the tracks in the path
				for i in range(0,len(path)-1):
					y = Net.get_edge_data(a,b)
					if (path[i] == a) and (path[i+1] == b) and all(y[key]['obj'].is_built == 0 for key in y):
						#update the data if track is built
						obj.load += shipment.path_vols[itr]
						obj.is_built = 1
						#This part doesn't do anything, could be expanded in the future
						if Net.has_edge(b, a):
							x = Net.get_edge_data(b,a)
							for key in x:
								#print(key)
								if x[key]['obj'].is_built == 0:
									#print(Net.edge(b,a,key=key))
									#Net.remove_edge(b,a,key=key)
									#print('hi')
									break
	###########################3
	return Net







#This function takes the network and creates a "pseudonetwork", which is able to weight the edges as if only
#one unit of shipment is coming through.  This is also in a multidigraph networkx dict-of-dict-of-dict-of-dict
#structure.  Function also returns a dictionary with all the edge costs
def costUpdate(Net):
	"costUpdate takes a network and returns a pseudonetwork and a cost dictionary"
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
				elif all((x[key]['obj'].load + 1) > 10 for key in x)  or all(x[key]['obj'].is_built == 0 for key in x):
					#calculate distance
					dist = math.hypot(stations_data[i-1][0] - stations_data[j-1][0], \
						stations_data[i-1][1] - stations_data[j-1][1])
					#multiply distance by 5000 and add to cost
					cost += 5000*dist
				if 5*(nx.get_node_attributes(Net,'obj')[j].reloading_buildings) < \
					(nx.get_node_attributes(Net,'obj')[j].ship_in + 1):
					#rscost is reloading station cost
					cost += rscost
				#add an edge to the pNet
				pNet.add_edge(i, j, weight=cost)
				#add an entry to the cost dict
				cost_dictionary['{0}--->{1}'.format(i,j)] = cost
	return [pNet,cost_dictionary]






def CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth):
	"finds the cheapest path through the pseudonetwork"
	global rscost
	global stations_data
	global track_data
	cost_path_dict = {}
	build_flag_dict = {}
	#iterate through all simple paths (no node repeats)
	#this fills a dict with keys of cost and their coorisponding paths
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
			#Uncomment this for debugging purposes
			# for key in y:
			# 	print('{0} is {1};;{2}<--'.format(key,y[key]['obj'].is_built,cpath[i]))
			# 	pass
			# for key in x:
			# 	print('{0} is {1};;{2}-->'.format(key,x[key]['obj'].is_built,cpath[i]))
			# 	pass

			#check if any tracks along a path are build
			if (all(y[key]['obj'].is_built == 0 for key in y) ) and all(x[key]['obj'].is_built == 0 for key in x):
				#if none we need to build a path
				print('  -build path and track from {0} to {1}'\
					.format(cpath[i],cpath[i+1]))
				track_data.append([cpath[i],cpath[i+1],1])
			
			#if lines are built but at capacity, need to build another
			elif all((x[key]['obj'].load + 1) > 10 for key in x)  or all(x[key]['obj'].is_built == 0 for key in x):
				#add that next line
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
	"add a shipment to an existing network"
	global rscost
	global stations_data
	global track_data

	#request user input on the characteristics of the new shipment
	origin = int(input('Enter starting Station:'))
	destination = int(input('Enter ending Station:'))
	size = int(input('Enter Shipment size:'))
	new_shipment = Shipment(origin, destination, size, [], [])

	total_cost = 0
	#initialize a network of stations and tracks with given shipment list
	Net = initNetwork(shipment_list)
	#create the pseudonetowrk and cost dict
	[a,b] = costUpdate(Net)
	pNet = a
	cost_dictionary = b
	#use that data to construct cheepest path of first shipment unit
	[origin, destination, cpath, ccost] = CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth)
	#update our new shipment with this path
	new_shipment.update(cpath)
	#increment cost
	total_cost += ccost
	#repeate procedure for remaining shipment units
	for i in range(1,size):
		#add the new shipment we are working on to the shipment list
		shipment_list.append(new_shipment)
		#pass all that to initialize a network
		Net = initNetwork(shipment_list)
		#remove the shipment we're working on from the list of complete shipments
		shipment_list.pop()
		#create cost dict and pseudonetwork
		[a,b] = costUpdate(Net)
		pNet = a
		cost_dictionary = b
		#find cheapest path
		[origin, destination, cpath, ccost] = CheapestPath(Net, pNet, cost_dictionary, origin, destination, depth)
		#update our working shipment object and cost
		new_shipment.update(cpath)
		total_cost += ccost
	print('total cost of addition: ${0}'.format(total_cost))
	#add the completed new shipment to our agragate list of shipments
	shipment_list.append(new_shipment)
	return shipment_list














##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################


#################Data################################
## You can change these data for different situations, set for 
# set for bonus at time of writing


#Reloading building cost (usually set to $1,000,000 or $500,000)
rscost = 1000000

#station data from assignment, station number is based on 0-index +1
#inner lists of form (xcoordinate, ycoordinate, num reloading buildings, initial incoming load (set to zero))
stations_data = [[0,	0,		4,	0],
				 [50,	50,		5,	0],
				 [250,	50,		4,	0],
				 [400,	50,		4,	0],
				 [0,	100,	6,	0],
				 [250,	100,	4,	0],
				 [150,	150,	2,	0],
				 [300,	150,	4,	0],
				 [50,	200,	4,	0],
				 [350,	200,	6,	0],
				 [150,	250,	3,	0],
				 [100,	300,	3,	0],
				 [400,	300,	7,	0],
				 [250,	350,	4,	0]]

#Track data from the assignment, order and direction do not matter (that took a while to implement in initNetwork)
#inner lists of form (origin, destination, number of tracks on that path)
track_data = [	[1,2,2],
				[1,5,1],
				[2,3,2],
				[2,5,2],
				[2,7,1],
				[3,4,3],
				[4,10,2],
				[5,9,3],
				[6,7,1],
				[6,8,2],
				[8,10,2],
				[9,12,2],
				[10,13,3],
				[11,12,2],
				[11,14,2],
				[13,14,3]]

#Shipments to be added to network defined with shipment object
#see shipment object definition for full explanation
path = [[1,5,9,12,11,14,13],[1,2,7,6,8,10,13],[1,2,3,4,10,13]]
vol = [9,5,3]
A = Shipment(1,13,17,path,vol)

path = [[5,2,7,6,8,10],[5,9,12,11,14,13,10]]
vol = [5,3 ]
B = Shipment(5,10,8,path,vol)

path = [[9,5,2,3,4]]
vol = [8] 
C = Shipment(9,4,8,path,vol)

path = [[14,13,10,4,3]]
vol = [7] 
D = Shipment(14,13,7,path,vol)

path = [[13,10,8,6]]
vol = [6] 
E = Shipment(13,6,6,path,vol)


############################################################################
############################################################################
############################################################################
############################################################################
############################################################################


###RUN THE HEURISTIC:

#define our shipment list, must be consistant with given data!!!!!!
shipment_list = [A,B,C,D,E]
#ask for user to input search depth, see report for systematic way of entering this
sd = int(input('Max Path Length: '))

#main loop where everything excecutes
while 1:
	#addShipment adds a shipment to the network derived from the above data
	#--first argument is a list of the  current shipments on the network
	#--second argument controls how long of a path the heuristic looks for 
	#        (Warning: second argument has an outsized effect on run time
	#                  and higher search depths do not necissarily yield 
	#                  better solutions)
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




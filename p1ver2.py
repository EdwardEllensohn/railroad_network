import math
import networkx as nx
import matplotlib.pyplot as plt

#The follwing is a class of a station, will be used as nodes
class Station(object):
    """Makes a Station"""
    def __init__(self, num, reloading_buildings, ship_in):
        self.num = num
        self.reloading_buildings = reloading_buildings
        self.ship_in = ship_in
    def displayinfo(self):
    	print('Station {0} has {1} reloading buildings and {2} incoming shipments'.format(self.num,self.reloading_buildings,self.ship_in))



stations_data = [[50,	0,		1,	0],
				 [250,	0,		1,	0],
				 [100,	50,		2,	0],
				 [0,	100,	3,	0],
				 [200,	100,	2,	0],
				 [100,	200,	2,	0],
				 [200,	200,	3,	0]]

xcorr 	= [50,		250,	100,	0,		200,	100,	200]
ycorr 	= [0,		0,		50,		100,	100,	200,	200]
rel_sta = [1,		1,		2,		3,		2,		2,		3]
shipins = [0,		0,		0,		0,		0,		0,		0]

track_data = [	[1,3,1],
				[1,4,1],
				[2,5,1],
				[3,5,1],
				[4,6,1],
				[5,7,1],
				[6,7,1]]


#some loops to determine which stations can be 
#connected under 220 miles
edges = []
for i in range(0,len(xcorr)):
	for j in range(0,len(ycorr)):
 		dist = math.hypot(xcorr[i] - xcorr[j], ycorr[i] - ycorr[j])
 		if (dist<=220)&(dist != 0):
 			#add a potential track 
 			edges.append((i+1,j+1))


###ititialize the network
Net = nx.DiGraph()
nodes = {}
#add all the stations
for i in range(0,len(stations_data)):
	nodes[i + 1] = Station(i + 1, stations_data[i][2],stations_data[i][3])
	Net.add_node(i + 1)

#add the existing tracks 
#for i in range(0, len(track_data)):
Net.add_weighted_edges_from(track_data)

nx.draw(Net)
plt.savefig("path.png")
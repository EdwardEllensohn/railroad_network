#phase 1

#functions

#returns a list of possible paths

# def pairs(lst):
# 	paths = []
# 	for i in lst:
# 		for j in lst:
# 			if i != j:
# 				paths.append((i,j))
# 	return paths




# #list of nodes
# nodes = list(range(1,7))
# print(nodes)


import math
from altgraph import ObjectGraph as og
from altgraph import Graph, GraphAlgo, Dot

stations = [[1,2,3]]
xcorr = [50,250,100,0,200,100,200]
ycorr = [0,0,50,100,100,200,200]
edges = []
for i in range(0,len(xcorr)):
	for j in range(0,len(ycorr)):
 		dist = math.hypot(xcorr[i] - xcorr[j], ycorr[i] - ycorr[j])
 		if (dist<=220)&(dist != 0):
 			edges.append((i+1,j+1))
 			


network = Graph.Graph()
for x,y in edges:
	network.add_edge(x,y)
print(network)	


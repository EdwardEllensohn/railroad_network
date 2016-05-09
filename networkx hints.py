####Some different networkx things 
#this file doesn't actually run, just for notes


#itterate through objects in edges in multidigraph
for i in Net.nodes():
	for j in Net.nodes():
		x = Net.get_edge_data(i,j)
		if type(x) is dict:
			for key in x:
				print(x[key]['obj'].is_built) #prints is_built attribute of object assosiated with the edge

for i in pNet.nodes():
	for j in pNet.nodes():
		x = pNet.get_edge_data(i,j)
		if type(x) is dict:
			for key in x:
				print(x[key]['weight'])


#Code to test fill method 
#it works!!!
test = nx.get_node_attributes(Net,'obj')
print(test[1].ship_in)  #print node object attribute
test[1].fill([A,B])      #sends shipments A and B through the net, updates node 1
print(test[1].ship_in) #print node object attribute



#Loops through and prints number of reloading buildings in each node
dct = nx.get_node_attributes(Net,'obj')
for key in dct:
	print(dct[key].reloading_buildings) 




######THIS IS REALLY DUMB --- DO NOT USE!!!!!!!!!!#############
###########################################################
###########################################
###################################
#############(LIKE ACTUALLY DON'T)
def lcppNet(pNet, start, end):
	path_dict = {}

	##First Level
	for i in pNet.neighbors(start):
		itr_path = []
		itr_cost = 0

		x = pNet.get_edge_data(start,i)
		#append this path step
		itr_path.append((start,i))
		#add the cost of going this way
		itr_cost += x[0]['weight']
		#if we found the end, add it to the dictionary of potentials
		if i == end:
			path_dict[itr_cost] = itr_path
			print('Cost: {0} \n ____for path: {1}'.format(itr_cost,itr_path))
		else:

			###Second Level
			for j in pNet.neighbors(i):
				level2_path = itr_path
				level2_cost = itr_cost
				#Don't Back Track
				if (j != start):
					x = pNet.get_edge_data(i,j)
					#append this path step
					level2_path.append((i,j))
					#add the cost of going this way
					level2_cost += x[0]['weight']
					#if we found the end, add it to the dictionary of potentials
					if j == end:
						path_dict[level2_cost] = level2_cost
						print('Cost: {0} \n ____for path: {1}'.format(level2_cost,level2_path))
					else:

						##Third Level
						for k in pNet.neighbors(j):
							level3_path = level2_path
							level3_cost = level2_cost
							#Don't Back Track
							if (k != start) & (k != i):
								x = pNet.get_edge_data(j,k)
								#append this path step
								itr_path.append((j,k))
								#add the cost of going this way
								itr_cost += x[0]['weight']
								#if we found the end, add it to the dictionary of potentials
								if k == end:
									path_dict[itr_cost] = itr_path
								##at bottom level do this
								else:
									print('\n idk \n')
						






		
	#print(path_dict[min(list(path_dict.keys()))])
	#print(min(list(path_dict.keys())))
	#print(path_dict)

#lcppNet(pNet,4,2)
	

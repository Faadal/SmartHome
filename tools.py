# @author : DINDIN Meryll

# Imports

import numpy as np

# Aims at removing value occurencies

def remove_doublon(raw):

	new = []

	for val in raw :
		if val not in new : new.append(val)

	return new

# Define the sensors corresponding to a given room

def match_room(room):

	# Has to evolve with the new configuration
	if room == 'N227' :
		return ['3', '6', '7', '8']
	elif room == 'E203' :
		return ['1', '2', '4']
	else :
		return []

# Define the time slicing depending of the considered sensor

def time_slot(sensor):

	if sensor[:1] in ['T', 'H', 'L'] :
		return [float(int(10*(0.0+k*0.1)))/10.0 for k in range(240)]
	else :
		return [float(int(10*(0.0+k*0.01)))/10.0 for k in range(2400)]

# Preprocessing to feed the filling holes algorithm

def time_process(sensor, stl, values):

	tab = np.zeros(len(time_slot(sensor)))

	for ind, ele in enumerate(stl) :
		if int(10*ele) >= 0 and int(10*ele) < len(time_slot(sensor)) :
			tab[int(10*ele)] = values[ind]

	return list(tab)

# Aims at filling holes in time series through linear regression

def remplissage(values) :

	# Determine le premier indice non nul de la liste    
	def first(liste) :
		i = 0
		l = liste
		if l[0] != 0 : return(i)
		else : 
			while (l[0] == 0 and len(l) > 1) :
				i += 1
				l = l[1:]
			return(i)

	# Determine le dernier indice non nul de la liste    
	def last(liste) :
		j = 0
		l = liste
		if l[-1] != 0 : return(j)
		else :
			while (l[-1] == 0 and len(l)>1) :
				j += 1
				l = l[:-1]
			return(j)

	i, j = first(values), last(values)

	if i >= 1 :
		for k in range(i) : 
			values[k] = values[i]

	if j >= 1 :
		for k in range(j) :
			values[len(values)-1-k] = values[len(values)-1-j]

	# Apply linear regression to complete the missing data
	for k in range(len(values)) :
		if values[k] == 0 :
			u = first(values[k:])
			a = ((values[k+u]-values[k-1])/float((k+u-k+1)))
			c = 0.5*(float(values[k+u]+values[k-1])-float(values[k+u]-values[k-1])*float(k+u+k-1)/float(k+u-k+1))
			values[k] = float(int(10*(a*k+c))/10.0)

	return(values)
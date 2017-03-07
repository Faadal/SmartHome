# @author : DINDIN Meryll

# Imports

# Aims at removing value occurencies

def remove_doublon(raw):

	new = []

	for val in raw :
		if val not in new : new.append(val)

	return new

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
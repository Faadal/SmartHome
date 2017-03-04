# @author : DINDIN Meryll

# Imports

import datetime
import numpy as np

from dateutil import parser

from error import *

# Job aiming at parsing all the gathered date in order to create samples

class Sampler:

	def __init__(self, date):
		self.dte = date

	def get_sample(self, sensor):

		err = Error()
		msg = Messenger()

		out, tem, sca = [], [], []

		# Read and timescale the gathered data
		try :
			pwd = open('../Data/Data_{}_{}.txt'.format(sensor[:1], sensor[1:]), 'r')
			raw = pwd.readline().split(';')
			pwd.close()

			# Reconstruct the types
			for ele in raw :
				new = ele.split(',')
				# Extract the value out of the format given by Eedomus
				if len(new) < 2 : pass
				else :
					val = float(new[0][1:])
					# Extract the datetime out of the same format
					dte = parser.parse(new[1][2:-1])
					out.append([val, dte])

			# Extract and time rescale the data for the right date
			for ele in out :
				if ele[1].date() == self.dte :
					res = float(ele[1].hour) + float(ele[1].minute)/60.0
					tem.append([ele[0], res])

			def remove_doublon(raw):
				new = []
				for val in raw :
					if val not in new : new.append(val)
				return new

			tem = remove_doublon(tem)
			msg.log('Data correctly extracted for sensor {}'.format(sensor))
		except :
			err.log('Could not read data for sensor {}'.format(sensor))

		# Save the amount of acquisitions realized by the considered sensor
		try :
			pwd = open('../Acquisition/Acq_{}_{}.txt'.format(sensor[:1], sensor[1:]), 'a')
			pwd.write('Le {} :\n'.format(self.dte.strftime('%d/%m/%Y')))
			pwd.write('{} acquisitions\n'.format(len(tem)))
			pwd.close()
			msg.log('Acquisitions have been saved for sensor {}'.format(sensor))
		except :
			err.log('Impossible to update the acquisition process')

		def time_slot(sensor):

			if sensor[:1] in ['T', 'H', 'L'] :
				return [float(int(10*(0.0+k*0.1)))/10.0 for k in range(241)]
			else :
				return [float(int(10*(0.0+k*0.01)))/10.0 for k in range(2401)]

		tab = np.zeros(len(time_slot(sensor)))

		# End of processing for the gathered time serie
		try :
			tsl = [ele[1] for ele in tem]
			val = [ele[0] for ele in tem]
			for ind, ele in enumerate(tsl) :
				if int(10*ele) >= 0 and int(10*ele) < len(time_slot(sensor)) :
					tab[int(10*ele)] = val[ind]
		except :
			err.log('Failure for algorithmic extraction and sorting for sensor {}'.format(sensor))

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

		try :
			ful = remplissage(list(tab))
			pwd = open('../Sample/Sam_{}_{}_{}.txt'.format(self.dte.strftime('%d-%m-%Y'), sensor[:1], sensor[1:]), 'w')
			pwd.write(str(time_slot(sensor))+'\n')
			pwd.write(str(ful)+'\n')
			pwd.close()
			msg.log('Sample created for sensor {}'.format(sensor))
		except :
			err.log('Could not create the sample for sensor {}'.format(sensor))

if __name__ == '__main__':
	sam = Sampler(datetime.date.today())
	sam.get_sample('TE')
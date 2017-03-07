# @author : DINDIN Meryll

# Imports

import datetime
import numpy as np

from dateutil import parser

from tools import *
from error import *

# Job aiming at parsing all the gathered date in order to create samples

class Sampler:

	def __init__(self, date=datetime.date.today()):
		self.dte = date
		self.err = Error()
		self.msg = Messenger()

	def get_sample(self, sensor):

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

			tem = remove_doublon(tem)
			self.msg.log('Data correctly extracted for sensor {}'.format(sensor))
		except :
			self.err.log('Could not read data for sensor {}'.format(sensor))

		if len(tem) == 0 :
			self.err.log('No data for sensor {}'.format(sensor))

		else :
			# Save the amount of acquisitions realized by the considered sensor
			try :
				pwd = open('../Acquisition/Acq_{}_{}.txt'.format(sensor[:1], sensor[1:]), 'a')
				pwd.write('Le {} :\n'.format(self.dte.strftime('%d/%m/%Y')))
				pwd.write('{} acquisitions\n'.format(len(tem)))
				pwd.close()
				self.msg.log('Acquisitions have been saved for sensor {}'.format(sensor))
			except :
				self.err.log('Impossible to update the acquisition process')

			tab = np.zeros(len(time_slot(sensor)))

			# End of processing for the gathered time serie
			try :
				tsl = [ele[1] for ele in tem]
				val = [ele[0] for ele in tem]
				for ind, ele in enumerate(tsl) :
					if int(10*ele) >= 0 and int(10*ele) < len(time_slot(sensor)) :
						tab[int(10*ele)] = val[ind]
			except :
				self.err.log('Failure for algorithmic extraction and sorting for sensor {}'.format(sensor))

			try :
				ful = remplissage(list(tab))
				pwd = open('../Sample/Sam_{}_{}_{}.txt'.format(self.dte.strftime('%d-%m-%Y'), sensor[:1], sensor[1:]), 'w')
				pwd.write(str(time_slot(sensor))+'\n')
				pwd.write(str(ful)+'\n')
				pwd.close()
				self.msg.log('Sample created for sensor {}'.format(sensor))
			except :
				self.err.log('Could not create the sample for sensor {}'.format(sensor))

	def get_samples(self):

		for gdr in ['T', 'H', 'L', 'M']:
			for typ in [str(k) for k in range(1, 13)] + ['C', 'E'] :
				self.get_sample(gdr + typ)
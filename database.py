# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd

from dateutil.rrule import rrule, DAILY

from api import *

# Job aiming at reading known inputs to extract sought data

class Parser:

	def __init__(self, date, sensor):
		self.dte = date
		self.err = Error()

	def parse_measures_sensor(self, sensor):

		pwd = '../Sample/Sam_{}_{}_{}.txt'.format(self.dte.date().strftime('%d-%m-%Y'), sensor[:1], sensor[1:])

		try :
			raw = open(pwd, 'r')
			stl = [float(e) for e in data.readline()[1:-2].split(',')]
			val = [float(e) for e in data.readline()[1:-2].split(',')]
			raw.close()

			return stl, val
		except :
			self.err.log('The file {} does not exist'.format(pwd))

			return [], []

	def parse_measure(self, genre, room):

		def match_room(room):

			sen = []
			# Has to evolve with the new configuration
			if room == 'N227' :
				sen = ['3', '6', '7', '8']

			return sen
			
		stl, mea = [], []

		for sen in match_room(room):
			stl, val = parse_measures_sensor(genre + sen)
			if stl, val == [], []
				pass
			else :
				stl = stl
				mea.append(val)

		# Define the average measures to constitute the database
		if len(mea) == 0 :
			self.err.log('No data gathered for room {}'.format(room))
		else :
			val = np.zeros(len(mea[0]))
			for ele in mea :
				for ind in range(len(ele)) :
					val[ind] += ele[ind]/float(len(mea))

		return stl, val

	def parse_weather(self):

		try : 
			raw = pd.read_pickle('../Weather/WEA')
			stl = raw[self.dte:self.dte].index
			val = raw[self.dte:self.dte].values

			return stl, val
		except :
			self.err.log('Could not parse the weather database')

	def parse_qai(self):

		try :
			raw = pd.read_pickle('../AirQuality/QAI_LCSQA')
			stl = raw[self.dte:self.dte].index
			val = raw[self.dte:self.dte].values

			return stl, val
		except :
			self.err.log('Could not parse the air quality database')

	def parse_hyperplanning(self):

		try :


# Job aiming at creating and updating the desired databases

class Database:

	def __init__(self, room):
		self.ort = room

	def build(self):

	def update(self):

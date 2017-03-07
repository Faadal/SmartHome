# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd
import datetime

from dateutil import parser
from dateutil.rrule import rrule, DAILY

from api import *
from tools import *

# Job aiming at reading known inputs to extract sought data

class Parser:

	def __init__(self, date):
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

	def parse_measures(self, genre, room):
			
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
			new = []
		else :
			new = np.zeros(len(mea[0]))
			for ele in mea :
				for ind in range(len(ele)) :
					new[ind] += ele[ind]/float(len(mea))

		return stl, new

	def parse_weather(self):

		try : 
			raw = pd.read_pickle('../Weather/WEA')
			stl = raw[self.dte:self.dte].index
			val = raw[self.dte:self.dte].values

			return stl, val
		except :
			self.err.log('Could not parse the weather database')

			return [], []

	def parse_qai(self):

		try :
			raw = pd.read_pickle('../AirQuality/QAI_LCSQA')
			stl = raw[self.dte:self.dte].index
			val = raw[self.dte:self.dte].values

			return stl, val
		except :
			self.err.log('Could not parse the air quality database')

			return [], []

	def parse_hyperplanning(self, tem, room):

		pwd = '../Presences/{}.txt', 'r'.format(room)

		def read(raw) :

			dbs = {}

			for line in raw.readlines() :
				item = line.split(',') 

				if item[0] not in dbs.keys() :
					dbs[item[0]] = []

				tdic = {}
				tdic['Begin'] = item[1]
				tdic['End'] = item[2]
				tdic['Type'] = item[3]

				if len(item) == 5 :
					tdic['Students'] = item[4]

				dbs[item[0]].append(tdic)
		
			return(dbs)

		try :
			raw = open(pwd, 'r')
			dbs = read(raw)
			raw.close()

			if self.dte.strftime('%d/%m/%Y') not in dbs.keys() :
				return tem, np.zeros(len(tem))
			else :
				hyp = []
				for tme in dbs[self.dte.strftime('%d/%m/%Y')] :
					l1 = [float(e) for e in tme['Begin'].split(':')]            
					t1 = l1[0] + l1[1]/60.0
					l2 = [float(e) for e in tme['End'].split(':')]            
					t2 = l2[0] + l2[1]/60.0 
					hyp += range(t1, t2, 0.1)

				val = []
				for ele in tem :
					if ele in hyp : val.append(True)
					else : val.append(False)

				return tem, val

		except :
			self.err.log('Could not parse the hyperplanning for room {}'.format(room))

			return [], []

# Job aiming at creating and updating the desired databases

class Database:

	def __init__(self, room):
		
		# Define database structure
		self.ort = room

		self.lab_cla = ['minute', 'hour', 'day', 'weekDay', 'weekNumber', 'month', 'year']
		self.lab_mea = ['T', 'H', 'L', 'Tcap', 'Hcap', 'Lcap', 'Text']
		self.lab_hyp = ['busy']
		self.lab_wea = ['summary', 'aTwea', 'cover', 'dewPoint', 'Hwea', 'ozone', 'rainFall', 'rainProb', 'Pwea', 'Twea', 'windExposure', 'windSpeed']
		self.lab_qai = ['IndMoyen', 'NO2', 'PM10', 'SO2', 'O3']

		self.lab = self.lab_cla + self.lab_hyp + self.lab_mea + self.lab_wea + self.lab_qai
		
		# Classical user-friendly objects
		self.err = Error()
		self.msg = Messenger()

	def available_dates(self, srt, end):

		val = []
		for fil in os.listdir('../Sample') :
			dte = parser.parse(fil[4:14])
			if dte in rrule(DAILY, dtstart=srt, until=end) :
				val.append(dte)

		return remove_doublon(val)

	def build_from_scratch(self):

		srt = datetime.date(2015,1,1)
		end = datetime.date.today() - datetime.timedelta(days=1)

		if os.path.exists('../Databases/DB_{}'.format(self.ort)) :
			self.err.log('Will not build the entire database from scratch')
		else :
			self.msg.log('Initialize database creation for room {}'.format(self.ort))
			
			ava = self.availables_dates(srt, end)

			idx, raw = [], []

			for dte in ava :
				par = Parser(dte)
				tim, new = time_slot('T'), []

				# Deals with non homogeneous samples
				stl, m_T = par.parse_measures('T', self.ort)
				if stl != len(tim) :
					m_T = remplissage(time_process('T', stl, m_T))
				
				stl, m_H = par.parse_measures('H', self.ort)
				if stl != len(tim) :
					m_H = remplissage(time_process('H', stl, m_H))
				
				stl, m_L = par.parse_measures('L', self.ort)
				if stl != len(tim) :
					m_L = remplissage(time_process('T', stl, m_L))

				stl, hyp = par.parse_hyperplanning(stl, self.ort)
				stl, wea = par.parse_weather()
				stl, qai = par.parse_qai()


	def update(self):
# @author : DINDIN Meryll

# Imports

import os
import copy
import datetime
import numpy as np
import pandas as pd
import datetime
import tqdm

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

		pwd = '../Sample/Sam_{}-{}_{}.txt'.format(self.dte.strftime('%d-%m-%Y'), sensor[:1], sensor[1:])

		try :
			raw = open(pwd, 'r')
			stl = [float(e) for e in raw.readline()[1:-2].split(',')]
			val = [float(e) for e in raw.readline()[1:-2].split(',')]
			raw.close()

			return stl, val
		except :
			self.err.log('The file {} does not exist'.format(pwd))

			return [], []

	def parse_measures(self, genre, room):
			
		stl, mea = [], []

		for sen in match_room(room):
			stl, val = self.parse_measures_sensor(genre + sen)
			if len(stl) == 0 and len(val) == 0 :
				pass
			else :
				stl = stl
				mea.append(val)

		# Define the average measures to constitute the database
		if len(mea) == 0 :
			self.err.log('No data gathered for room {} for the feature {}'.format(room, genre))
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
			srt = datetime.datetime(self.dte.year, self.dte.month, self.dte.day, 0, 0)
			end = srt + datetime.timedelta(hours=23, minutes=59)
			stl = raw[srt:end].index
			val = raw[srt:end].values

			return stl, val
		except :
			self.err.log('Could not parse the weather database')

			return [], []

	def parse_qai(self):

		raw = pd.read_pickle('../AirQuality/QAI_LCSQA')

		try :
			val = list(raw[self.dte:self.dte].values)[0]

			return self.dte, list(val)

		except :
			self.err.log('Could not parse the LCSQA database')

			return [], []

	def parse_hyperplanning(self, tem, room):

		pwd = '../Presences/{}.txt'.format(room)

		def read(raw) :

			dbs = {}

			for line in raw.readlines() :
				item = line.split(',') 

				if len(item) <= 3 :
					pass
				elif item[0] not in dbs.keys() :
					dbs[item[0]] = []
				else :
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
			
			if self.dte.strftime('%d/%m/%Y') not in list(dbs.keys()) :
				val = np.zeros(len(tem))
				val[:] = False
				return tem, val

			else :
				hyp = []
				for tme in dbs[self.dte.strftime('%d/%m/%Y')] :
					l1 = [float(e) for e in tme['Begin'].split(':')]            
					t1 = l1[0] + l1[1]/60.0
					l2 = [float(e) for e in tme['End'].split(':')]            
					t2 = l2[0] + l2[1]/60.0 
					hyp += [t1 + k*0.1 for k in range(int(10*(t2-t1)))]

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

		self.lab = self.lab_cla + self.lab_mea + self.lab_hyp + self.lab_wea + self.lab_qai
		
		# Classical user-friendly objects
		self.err = Error()
		self.msg = Messenger()

	def available_dates(self, srt, end):

		val = []
		for fil in os.listdir('../Sample') :

			try :
				sen = fil.split('-')[3].split('.')[0].split('_')[1]
			except :
				pass

			if sen in match_room(self.ort) :
				val.append(parser.parse(fil[4:14], dayfirst=True).date())

		return remove_doublon(val)

	def add_date_to_database(self, dte):

		pwd = '../Databases/DB_{}'.format(self.ort)

		idx, raw = [], []

		par = Parser(dte)
		
		tim, new, idx = time_slot('T'), [], []

		# Deals with non homogeneous samples
		stl, m_T = par.parse_measures('T', self.ort)
		if len(stl) != len(tim) :
			m_T = remplissage(time_process('T', stl, m_T))
		elif len(m_T) == 0 :
			m_T = np.empty(len(time_slot('T'))) * np.NaN

		stl, m_H = par.parse_measures('H', self.ort)
		if len(stl) != len(tim) :
			m_H = remplissage(time_process('H', stl, m_H))
		elif len(m_H) == 0 :
			m_H = np.empty(len(time_slot('T'))) * np.NaN
		
		stl, m_L = par.parse_measures('L', self.ort)
		if len(stl) != len(tim) :
			m_L = remplissage(time_process('T', stl, m_L))
		elif len(m_L) == 0 :
			m_L = np.empty(len(time_slot('T'))) * np.NaN

		stl, T_C = par.parse_measures_sensor('TC')
		if len(stl) != len(tim) :
			T_C = remplissage(time_process('T', stl, T_C))
		elif len(T_C) == 0 :
			T_C = np.empty(len(time_slot('T'))) * np.NaN

		stl, H_C = par.parse_measures_sensor('HC')
		if len(stl) != len(tim) :
			H_C = remplissage(time_process('T', stl, H_C))
		elif len(H_C) == 0 :
			H_C = np.empty(len(time_slot('T'))) * np.NaN

		stl, L_C = par.parse_measures_sensor('LC')
		if len(stl) != len(tim) :
			L_C = remplissage(time_process('T', stl, L_C))
		elif len(L_C) == 0 :
			L_C = np.empty(len(time_slot('T'))) * np.NaN

		stl, T_E = par.parse_measures_sensor('TE')
		if len(stl) != len(tim) :
			T_E = remplissage(time_process('T', stl, T_E))
		elif len(T_E) == 0 :
			T_E = np.empty(len(time_slot('T'))) * np.NaN

		stl, hyp = par.parse_hyperplanning(tim, self.ort)
		if len(hyp) == 0 :
			hyp = np.empty(len(time_slot('T'))) * np.NaN

		stl, tem = par.parse_weather()
		wea = []
		stl = [float(ele.hour) + float(ele.minute)/60.0 for ele in stl]
		for ind, lab in enumerate(self.lab_wea) :
			val = []
			for ele in tem :
				if lab == 'summary' :
					val.append(str(ele[ind]))
				else :
					val.append(float(ele[ind]))
			wea.append(val)
		if len(stl) != len(tim) :
			tem = []
			if len(wea[0]) < 24 :
				que = wea[0] + [np.NaN for k in range(24 - len(wea[0]))]
				tem.append(que)
			else :
				tem = [wea[0]]
			for ele in wea[1:] :
				try :
					tem.append(remplissage(time_process('T', stl, ele)))
				except :
					que = np.empty(len(time_slot('T'))) * np.NaN
					tem.append(que)
			wea = copy.copy(tem)
		elif len(wea) == 0 : wea = np.empty((len(tim), 12)) * np.NaN

		stl, qai = par.parse_qai()
		if len(qai) == 0 : qai = list(np.empty(len(pd.read_pickle('../AirQuality/QAI_LCSQA').columns)) * np.NaN)

		for ind, ele in enumerate(tim) :
			raw = []
			# Add the corresponding index
			idx.append(datetime.datetime(dte.year, dte.month, dte.day, int(ele), int((ele-int(ele))*60)))
			# Minute
			raw.append(int((ele-int(ele))*60))
			# Hour
			raw.append(int(ele))
			# Day
			raw.append(dte.day)
			# Weekday
			raw.append(dte.weekday())
			# Week number
			raw.append(dte.isocalendar()[1])
			# Month
			raw.append(dte.month)
			# Year
			raw.append(dte.year)
			# Temperature measure
			raw.append(m_T[ind])
			# Humidity measure
			raw.append(m_H[ind])
			# Luminosity measure
			raw.append(m_L[ind])
			# Hall temperature
			raw.append(T_C[ind])
			# Hall humidity
			raw.append(H_C[ind])
			# Hall luminosity
			raw.append(L_C[ind])
			# External temperature
			raw.append(T_E[ind])
			# Busy
			raw.append(hyp[ind])
			# Weather
			for i, ele in enumerate(wea) :
				# Solved the conflict with the string type
				if i == 0 :
					raw.append(ele[int(ind/10.0)])
				else :
					raw.append(ele[ind])
			# Air quality
			raw = raw + qai

			new.append(np.asarray(raw))

		if not os.path.exists(pwd) :
			pd.DataFrame(data=np.asarray(new), index=np.asarray(idx), columns=np.asarray(self.lab)).to_pickle(pwd)
			self.msg.log('Database successfully build for room {}'.format(self.ort))
		else :
			dtf = pd.read_pickle(pwd)
			new = pd.DataFrame(data=np.asarray(new), index=np.asarray(idx), columns=np.asarray(self.lab))
			dtf = pd.concat([dtf, new])
			dtf.to_pickle(pwd)
			self.msg.log('Database successfully updated for room {} on date {}'.format(self.ort, dte.strftime('%d-%m-%Y')))

	def update(self):

		dte = datetime.date.today() - datetime.timedelta(days=1)

		dbs = self.add_date_to_database(dte)

if __name__ == '__main__':
	dte = datetime.datetime(2017, 4, 1)
	a, b = Parser(dte).parse_weather()
	print(a)
	print(b)
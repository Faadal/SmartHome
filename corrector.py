# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd
import tqdm
import time

from dateutil import parser
from dateutil.rrule import rrule, DAILY

from api import *
from tools import *
from error import *
from database import *

# Job aiming at collecting data for all missing days

class Corrector:

	def __init__(self, room):
		self.err = Error()
		self.msg = Messenger()
		# First measurement on March the third
		self.str = datetime.date(2016, 3, 1)
		# Last day of correction
		self.end = datetime.date.today() - datetime.timedelta(days=1)
		# Defining the room
		self.ort = room

	def get_missing(self, db):

		mis = []

		if not os.path.exists(db) :
			for dte in rrule(DAILY, dtstart=self.str, until=self.end) :
				mis.append(dte.date())

			return mis

		else :
			raw = pd.read_pickle(db)

			for dte in rrule(DAILY, dtstart=self.str, until=self.end) :
				tem = dte.date()
				# Depending on the database, the indexes are date or datetime types - avoid conflicts and error types
				try :
					# Corresponds to the weather database
					idx = remove_doublon([ele.date() for ele in raw.index])
				except :
					# Corresponds to the airquality database
					idx = remove_doublon([ele for ele in raw.index])

				# Preprocessing to clear the database with same indexes
				if tem in idx and len(raw.loc[tem]) != len(raw.columns) :
					bit = np.zeros(len(raw.columns))
					bit[:] = np.NaN
					for ele in raw.loc[tem].values :
						if not np.isnan(ele[1]) :
							bit = ele
					raw = raw.drop(tem)
					new = pd.DataFrame(data=np.asarray([bit]), index=np.asarray([tem]), columns=np.asarray(raw.columns))
					raw = pd.concat([raw, new])
				
				raw.to_pickle(db)

				# Remove conflict with double indexing
				if tem in idx and np.isnan(float(raw[tem:tem].values[0][1])) :
					mis.append(tem)
				elif tem not in idx :
					mis.append(tem)

			return mis

	def correct_qai(self):

		mis = self.get_missing('../AirQuality/QAI_LCSQA')
		self.msg.log('Air quality lacks {} days of collection'.format(len(mis)))

		for dte in tqdm.tqdm(mis) :
			qai = RequestQAI(dte)
			qai.get_data()
			self.msg.log('Air quality database successfully updated for the {}'.format(dte.strftime('%Y-%m-%d')))
			time.sleep(1)

	def correct_wea(self):

		mis = self.get_missing('../Weather/WEA')
		self.msg.log('Weather lacks {} days of collection'.format(len(mis)))

		for dte in tqdm.tqdm(mis) :
			wea = RequestWeather(dte)
			wea.get_data()
			time.sleep(1)

		self.msg.log('Weather database successfully updated')

	def correct_database(self):

		dbs = Database(self.ort)

		pwd = '../Databases/DB_{}'.format(dbs.ort)

		ava = dbs.available_dates(self.str, self.end)

		if not os.path.exists(pwd) :
			for dte in tqdm.tqdm(ava) :
				dbs.add_date_to_database(dte)
		else :
			dtf = pd.read_pickle(pwd)

			# Take care of the duplicates
			dtf = dtf.reset_index().drop_duplicates(subset='index', keep='last').set_index('index').sort_index()

			for dte in tqdm.tqdm(ava) :
				if dte not in dtf.index :
					dbs.add_date_to_database(dte)

	def correct_samples(self):

		# Get the available dates
		ava = {}
		for ele in os.listdir('../Sample') :
			try :
				dte = parser.parse(ele[4:14], dayfirst=True).date()
				typ = ele.split('-')[3].split('.')[0].split('_')[0]
				sen = ele.split('-')[3].split('.')[0].split('_')[1]
				if typ not in list(ava.keys()) : 
					ava[typ] = {}
					ava[typ][sen] = [dte]
				elif sen not in list(ava[typ].keys()) :
					ava[typ][sen] = [dte]
				else :
					if dte not in ava[typ][sen] :
						ava[typ][sen].append(dte)
			except :
				pass

		print('|-> The list of available correction has been examined')

		# Create the list of the databases we want to correct
		lis = []
		for typ in ['T', 'H', 'L'] :
			for sen in [str(i) for i in range(1, 12)] :
				lis.append(typ + sen)

		for sen in tqdm.tqdm(lis) :

			pwd = '../Sensors/Sensor_{}_{}'.format(sen[0], sen[1:])

			if not os.path.exists(pwd) :

				if sen[0] not in list(ava.keys()) : pass

				elif sen[1:] not in list(ava[sen[0]].keys()) : pass

				else :
					dta, idx = [], []

					for dte in ava[sen[0]][sen[1:]] :
						raw = open('../Sample/Sam_{}-{}_{}.txt'.format(dte.strftime('%d-%m-%Y'), sen[0], sen[1:]), 'r')
						tim, stl = raw.readline()[1:-2].replace(' ', '').split(','), []
						for ele in tim[:-1] :
							tem = datetime.datetime(year=dte.year, month=dte.month, day=dte.day, hour=int(float(ele)), minute=int((float(ele)-int(float(ele)))*60))
							stl.append(tem)
						val = raw.readline()[1:-2].replace(' ', '').split(',')
						val = [float(e) for e in val][:-1]
						raw.close()

						for v in val : dta.append(v)
						for s in stl : idx.append(s)

					pd.DataFrame(data=np.asarray(dta), index=np.asarray(idx), columns=np.asarray(['Value'])).to_pickle(pwd)

					self.msg.log('Database for sensor {} has been successfully created'.format(sen))
			
			else :

				dtb = pd.read_pickle(pwd)
				# Delete duplicates and sort the dataframe
				dtb = dtb.reset_index().drop_duplicates(subset='index', keep='last').set_index('index').sort_index()

				if sen[0] not in list(ava.keys()) : pass

				elif sen[1:] not in list(ava[sen[0]].keys()) : pass
				
				else :

					# Get the missing dates
					dts, mis = remove_doublon([ele.date() for ele in dtb.index]), []
					for dte in ava[sen[0]][sen[1:]] :
						if dte not in dts : mis.append(dte)

					self.msg.log('{} days of data were missing in the database'.format(len(mis)))

					for dte in mis :

						raw = open('../Sample/Sam_{}-{}_{}.txt'.format(dte.strftime('%d-%m-%Y'), sen[0], sen[1:]), 'r')
						tim, stl = raw.readline()[1:-2].replace(' ', '').split(','), []
						for ele in tim[:-1] :
							tem = datetime.datetime(year=dte.year, month=dte.month, day=dte.day, hour=int(float(ele)), minute=int((float(ele)-int(float(ele)))*60))
							stl.append(tem)
						val = raw.readline()[1:-2].replace(' ', '').split(',')
						val = [float(e) for e in val][:-1]
						raw.close()

						new = pd.DataFrame(data=np.asarray(val), index=np.asarray(stl), columns=np.asarray(['Value']))
						dtb = pd.concat([dtb, new]).sort_index()
						dtb.to_pickle(pwd)

					self.msg.log('Database for sensor {} has been corrected'.format(sen))

if __name__ == '__main__':
	print(list(os.listdir('../Weather')))
	#Corrector('').correct_wea()
	Corrector('').correct_qai()
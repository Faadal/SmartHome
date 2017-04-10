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
			for dte in tqdm.tqdm(ava) :
				if dte not in dtf.index :
					dbs.add_date_to_database(dte)

	def correct_samples(self):

		for ele in tqdm.tqdm(os.listdir('../Sample')) :

			try :
				dte = parser.parse(ele[4:14])
				typ = ele.split('-')[3][:4].split('_')[0]
				sen = ele.split('-')[3][:4].split('_')[1]

				pwd = '../Data/Sensor_{}_{}'.format(typ, sen)

				raw = open('../Sample/' + ele, 'r')
				tim, stl = raw.readline()[1:-2].replace(' ', '').split(','), []
				for ele in tim[:-1] :
					tem = datetime.datetime(year=dte.year, month=dte.month, day=dte.day, hour=int(float(ele)), minute=int((float(ele)-int(float(ele)))*60))
					stl.append(tem)
				val = raw.readline()[1:-2].replace(' ', '').split(',')
				val = [float(e) for e in val][:-1]
				raw.close()

				if not os.path.exists(pwd) :
					pd.DataFrame(data=np.asarray(val), index=np.asarray(stl), columns=np.asarray(['Value'])).to_pickle(pwd)
				else :
					dtf = pd.read_pickle(pwd)
					if not dte.date() in [ele.date() for ele in dtf.index] :
						new = pd.DataFrame(data=np.asarray(val), index=np.asarray(stl), columns=np.asarray(['Value']))
						dtf = pd.concat([dtf, new])
						dtf.to_pickle(pwd)

			except :
				pass
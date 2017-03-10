# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd
import tqdm
import time

from dateutil.rrule import rrule, DAILY

from api import *
from error import *
from database import *

# Job aiming at collecting data for all missing days

class Corrector:

	def __init__(self):
		self.err = Error()
		self.msg = Messenger()
		# First measurement on March the third
		self.str = datetime.date(2016, 3, 1)
		# Last day of correction
		self.end = datetime.date.today() - datetime.timedelta(days=1)

	def get_missing(self, db):

		def remove_doublon(raw):
			new = []
			for val in raw :
				if val not in new : new.append(val)
			return new

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
			time.sleep(1)

		self.msg.log('Air quality database successfully updated for the {}'.format(dte.strftime('%Y-%m-%d')))

	def correct_wea(self):

		mis = self.get_missing('../Weather/WEA')
		self.msg.log('Weather lacks {} days of collection'.format(len(mis)))

		for dte in tqdm.tqdm(mis) :
			wea = RequestWeather(dte)
			wea.get_data()
			time.sleep(1)

		self.msg.log('Weather database successfully updated')

	def correct_database(self, room):

		self.correct_wea()
		self.correct_qai()

		dbs = Database(room)

		srt = datetime.datetime(2016, 3, 1).date()
		end = datetime.date.today() - datetime.timedelta(days=1)

		pwd = '../Databases/DB_{}'.format(dbs.ort)

		if not os.path.exists(pwd) :
			for dte in tqdm.tqdm(rrule(DAILY, dtstart=srt, until=end)) :
				dbs.add_date_to_database(dte)
		else :
			ava = dbs.available_dates(srt, end)
			dtf = read_pickle(pwd)
			for dte in tqdm.tqdm(ava) :
				if dte not in dtf.index :
					dbs.add_date_to_database(dte)
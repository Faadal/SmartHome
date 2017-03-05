# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd

from dateutil.rrule import rrule, DAILY

from api import *
from error import *

# Job aiming at collecting data for all missing days

class Corrector:

	def __init__(self):
		self.err = Error()
		self.msg = Messenger()
		# First measurement on March the third
		self.str = datetime.date(2016, 3, 1)
		# Last day of correction
		self.end = datetime.date.today()

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

			return missing

		else :
			raw = pd.read_pickle(db) :
			for dte in rrule(DAILY, dtstart=self.str, until=self.end) :
				tem = dte.date()
				idx = remove_doublon([ele.date() for ele in raw.index])
				if tem in idx and np.isnan(raw[tem:tem].values[0][0]) :
					mis.append(tem)
				elif tem not in idx :
					mis.append(tem)

			return missing

	def correct_qai(self):

		mis = self.get_missing('../AirQuality/QAI_LCSQA')
		self.msg.log('Air quality lacks {} days of collection'.format(len(mis)))

		for dte in mis :
			qai = RequestQAI(dte)
			qai.get_data()

		self.msg.log('Air quality database successfully updated')

	def correct_wea(self):

		mis = self.get_missing('../Weather/WEA')
		self.msg.log('Weather lacks {} days of collection'.format(len(mis)))

		for dte in mis :
			wea = RequestWeather(dte)
			wea.get_data()

		self.msg.log('Weather database successfully updated')
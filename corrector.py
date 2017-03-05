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
		# First measurement on March the third
		self.str = datetime.date(2016, 3, 1)
		# Last day of correction
		self.end = datetime.date.today()

	def get_missing_qai(self):

		mis = []

		if not os.path.exists('../AirQuality/QAI_LCSQA') :
			for dte in rrule(DAILY, dtstart=self.str, until=self.end) :
				mis.append(dte.date())

			return missing

		else :
			raw = pd.read_pickle('../AirQuality/QAI_LCSQA') :
			for dte in rrule(DAILY, dtstart=self.str, until=self.end) :
				tem = dte.date()
				if tem in raw.index() and np.isnan(raw[tem:tem].values[0][0]) :
					mis.append(tem)
				elif tem not in raw.index() :
					mis.append(tem)

			return missing

	def correct_qai(self):

		err = Error()
		msg = Messenger()

		mis = self.get_missing_qai()
		msg.log('Air quality lacks {} days of collection'.format(len(mis)))

		for dte in mis :
			qai = RequestQAI(dte)
			qai.get_data()

		msg.log('Air quality database successfully updated')

	def get_missing_wea(self):


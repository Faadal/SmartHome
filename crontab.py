# @author : DINDIN Meryll

# Imports

import datetime

from api import *
from database import *
from corrector import *
from processing import *

# New implementation of the crontab

class Launcher:

	def __init__(self, time):
		
		self.tim = time

	def run(self) :

		if (int(self.tim.hour), int(self.tim.minute)) == (8, 0) :
			RequestEedomus().get_data()
		elif (int(self.tim.hour), int(self.tim.minute)) == (20, 0) :
			RequestEedomus().get_data()
		elif (int(self.tim.hour), int(self.tim.minute)) == (23, 0) :
			RequestWeather().get_data()
		elif (int(self.tim.hour), int(self.tim.minute)) == (23, 10) :
			RequestQAI().get_data()
		elif (int(self.tim.hour), int(self.tim.minute)) == (5, 0) :
			Corrector('N227').correct_wea()
		elif (int(self.tim.hour), int(self.tim.minute)) == (5, 30) :
			Corrector('N227').correct_qai()
		elif (int(self.tim.hour), int(self.tim.minute)) == (9, 0) :
			Sampler().get_samples()
		elif (int(self.tim.hour), int(self.tim.minute)) == (9, 30) :
			Database('N227').update()
		elif (int(self.tim.hour), int(self.tim.minute)) == (9, 40) :
			Database('E203').update()
		elif (int(self.tim.hour), int(self.tim.minute)) == (9, 50) :
			Corrector('N227').correct_database()
		elif (int(self.tim.hour), int(self.tim.minute)) == (9, 0) :
			Corrector('E203').correct_database()

if __name__ == '__main__' :
	
	dte = datetime.datetime.now()
	
	Launcher(dte).run()
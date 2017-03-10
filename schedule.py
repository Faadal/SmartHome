# @author : DINDIN Meryll

# Imports

import schedule
import time

from api import *
from database import *
from corrector import *
from processing import *

# Get rid of the usual crontab

schedule.every().day.at('08:00').do(RequestEedomus().get_data())

schedule.every().day.at('20:00').do(RequestEedomus().get_data())

schedule.every().day.at('23:15').do(RequestQAI().get_data())

schedule.every().day.at('23:30').do(RequestWeather().get_data())

schedule.every().day.at('00:15').do(Sampler().get_samples())

schedule.every().day.at('00:30').do(Database('N227').update())

# Schedule to update database once a day

# Schedule to clear what remains unnecessary once a week

# Schedule for backup once a week (email ?)

# Launch

while True :
	schedule.run_pending()
	time.sleep(1)
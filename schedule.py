# @author : DINDIN Meryll

# Imports

import schedule
import datetime
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

schedule.every().day.at('23:45').do(Sampler().get_samples())

# Schedule to correct databases once a week

# Schedule to update database once a day

# Schedule to clear what remains unnecessary once a week

# Schedule for backup once a week (email ?)

# Launch

while True :
	schedule.run_pending()
	time.sleep(1)
# @author : DINDIN Meryll

# Imports

import schedule
import time

from api import *
from tools import *
from database import *
from corrector import *
from processing import *

# Get rid of the usual crontab

# Work on current day
schedule.every().day.at('08:00').do(RequestEedomus().get_data)
# Work on current day
schedule.every().day.at('20:00').do(RequestEedomus().get_data)
# Work on current day
schedule.every().day.at('23:20').do(RequestWeather().get_data)
# Work on current day
schedule.every().day.at('23:30').do(RequestQAI().get_data)
# Check missing dates and correct it
schedule.every().day.at('05:00').do(Corrector('N227').correct_wea)
# Check missing dates and correct it
schedule.every().day.at('05:30').do(Corrector('N227').correct_qai)
# Work on previous day
schedule.every().day.at('09:00').do(Sampler().get_samples)
# Work on previous day
schedule.every().day.at('09:30').do(Database('N227').update)
# Check missing dates and correct it
schedule.every().day.at('12:00').do(Corrector('N227').correct_database)

# Launch

while True :
	schedule.run_pending()
	time.sleep(1)

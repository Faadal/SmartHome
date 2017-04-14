# @author : DINDIN Meryll

# Imports

import time
import schedule

from api import *
from tools import *
from database import *
from corrector import *
from processing import *

# Get rid of the usual crontab

# Work on current day
schedule.every().day.at('08:00').do(RequestEedomus().get_data)
# Work on previous day
schedule.every().day.at('09:00').do(Sampler().get_samples)
# Work on previous day
#schedule.every().day.at('09:30').do(Database('N227').update)
# Work on previous day
#schedule.every().day.at('09:40').do(Database('E203').update)
# Work on current day
schedule.every().day.at('20:00').do(RequestEedomus().get_data)
# Work on current day
schedule.every().day.at('20:10').do(RequestFoobot().get_data)
# Work on current day
schedule.every().day.at('23:20').do(RequestWeather().get_data)
# Work on current day
schedule.every().day.at('23:30').do(RequestQAI().get_data)

# Send global status of the sensors
schedule.every().friday.at('07:00').do(RequestEedomus().send_status_sensors)

# Check missing dates and correct it
#schedule.every().monday.at('05:00').do(Corrector('').correct_wea)
# Check missing dates and correct it
#schedule.every().monday.at('05:30').do(Corrector('').correct_qai)
# Check missing dates and correct it
#schedule.every().monday.at('12:00').do(Corrector('N227').correct_database)
# Check missing dates and correct it
#schedule.every().monday.at('12:10').do(Corrector('E203').correct_database)

# Launch

while True :
	schedule.run_pending()
	time.sleep(10)
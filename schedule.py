# @author : DINDIN Meryll

# Imports

import schedule
import datetime
import time

from api import *
from processing import *

# Get rid of the usual crontab

api_eed = RequestEedomus()
schedule.every().day.at('08:00').do(api_eed.get_data())
schedule.every().day.at('20:00').do(api_eed.get_data())

api_qai = RequestQAI()
schedule.every().day.at('23:00').do(api_qai.get_data())

api_wea = RequestWeather()
schedule.every().day.at('23:15').do(api_wea.get_data())

sampler = Sample()
schedule.every().day.at('23:30').do(sampler.get_samples())
# Launch

while True :
	schedule.run_pending()
	time.sleep(1)
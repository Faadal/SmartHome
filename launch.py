# @author : DINDIN Meryll

# Imports

from api import *
from database import *
from corrector import *
from processing import *

# Launch

if __name__ == '__main__':
    RequestEedomus().get_data()
    RequestFoobot().get_data()
    RequestWeather().get_data()
    RequestQAI().get_data()
    Corrector('').correct_qai()
    Corrector('').correct_wea()
    Corrector('').correct_samples()
    Sampler().get_samples()
    Database('N227').update()
    Database('E203').update()
    Corrector('N227').correct_database()
    Corrector('E203').correct_database()
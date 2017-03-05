# @author : DINDIN Meryll

# Imports

import os
import datetime
import numpy as np
import pandas as pd

from dateutil.rrule import rrule, DAILY

from api import *

# Job aiming at reading known inputs to extract sought data

class Parser:

	def __init__(self, datetime):
		self.dte = datetime

	def parse_measures(self):

	def parse_weather(self):

	def parse_qai(self):

	def parse_hyperplanning(self):

# Job aiming at creating and updating the desired databases

class Database:

	def __init__(self, room):
		self.ort = room

	def build(self):

	def update(self):

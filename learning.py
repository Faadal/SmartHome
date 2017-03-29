# @author : DINDIN Meryll

# Imports

import matplotlib.pyplot as plt 
import pandas as pd 
import seaborn as sb 

# Core class

class Process:

	def __init__(self, name) :

		self.pwd = '../Databases/DB_{}'.format(name)
		self.raw = pd.read_pickle(self.pwd)
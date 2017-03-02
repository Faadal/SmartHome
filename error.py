# @author : DINDIN Meryll

# Imports

import datetime

# Define class handling errors as new log purpose

class Error:

	def __init__(self):
		self.path = './logs.txt'
		self.time = datetime.datetime.now()

	def log(self, message):
		file = open(self.path, 'a')
		file.write('[{}] : {}'.format(str(self.time), message+'\n'))
		file.close()

class Messager:

	def __init__(self):
		self.path = './messages.txt'
		self.time = datetime.datetime.now()

	def log(self, message):
		file = open(self.path, 'a')
		file.write('[{}] : {}'.format(str(self.time), message+'\n'))
		file.close()
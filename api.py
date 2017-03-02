# @author : DINDIN Meryll

# Imports

import requests
import json
import time
import tqdm

from error import *

# Define class request for data gathering
# usr -> api id
# pwd -> api key
# aut -> request for authentification
# req -> request for periphericals
# per -> dictionnary of periphericals

class RequestEedomus:

	def __init__(self):

		# Web Request
		self.usr = 'ZeRV4W'
		self.pwd = '44xNeKX0OsZt0yYR'
		self.aut = requests.get('https://api.eedomus.com/get?api_user={}&api_secret={}&action=auth.test'.format(self.usr, self.pwd))
		
		try :
			# Assert if the connection is effective
			res = json.loads(self.aut.content)
			if res['success'] == 1 :
				pass
			else :
				err = Error()
				err.log('Authentification on Eedomus server failed')
		except :
			err = Error()
			err.log('Could not load data from Eedomus server')

		self.req = requests.get('https://api.eedomus.com/get?api_user={}&api_secret={}&action=periph.list'.format(self.usr, self.pwd))

		try :
			# Check the request
			self.req = json.loads(self.req.text)['body']
		except :
			err = Error()
			err.log('Eedomus request has no body')

	# Create the list of every sensor connected to the Eedomus interface

	def get_peripheriques(self):

		per = {}

		for i in tqdm.tqdm(range(len(self.req))):
			new = self.req[i]['name'].encode('ascii', 'ignore')
			per[new] = int(self.req[i]['periph_id'])

		self.per = per



if __name__ == '__main__':
	req = RequestEedomus()
	req.get_peripheriques()
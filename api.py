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

	# Get the values corresponding to the peripherical

	def get_values(self, periph):

		def req_per(periph):

			per = str(self.per[periph])
			req = requests.get('https://api.eedomus.com/get?action=periph.history&periph_id={}&api_user={}&api_secret={}'.format(per, self.usr, self.pwd))

			return req

		raw = {}
		val = []
		try :
			raw = json.loads(req_per(periph).content)['body']['history']
		except :
			err = Error()
			err.log('Could not load intel for periph {}'.format(periph))

		if periph[0] == 'M' :
			for i in range(len(raw)) :
				new = raw[i][0].encode('utf-8')

				if new == 'Aucun mouvement': new = 0
				elif new == 'Mouvement': new = 1
				else : new = 0.5

				val.append([float(new), raw[i][1].encode('utf-8')])

		else :
			for i in range(len(raw)) :
				val.append([float(raw[i][0].encode('utf-8')), raw[i][1].encode('utf-8')])

		return val

	def get_data(self):

		# Make sure all the devices will be extracted from the Eedomus server
		self.get_peripheriques()

		msg = Messager()

		for gdr in ['T', 'H', 'L', 'M'] :
			for num in tqdm.tqdm([str(e) for e in range(1,12)] + ['C']) :

				pwd = '../Data/Data_{}_{}.txt'.format(gdr, num)
				raw = open(pwd, 'a')

				if num == 'C' :
					if gdr == 'T' : val = self.get_values('Temperature Couloir Salle')
					elif gdr == 'H' : val = self.get_values('Humidite Couloir Salle')
					elif gdr == 'L' : val = self.get_values('Luminosite Couloir Salle')
					elif gdr == 'M' : val = self.get_values('Mouvement Couloir Salle')
				else :
					if int(num) < 10 : num = '0' + num
					if gdr == 'T' : val = self.get_values('Temperature {} Salle'.format(num))
					elif gdr == 'H' : val = self.get_values('Humidite {} Salle'.format(num))
					elif gdr == 'L' : val = self.get_values('Luminosite {} Salle'.format(num))
					elif gdr == 'M' : val = self.get_values('Mouvement {} Salle'.format(num))

				for v in val : raw.write(str(v) + ';')
				msg.log('Acquisition completed for {}_{}'.format(gdr, num))

				raw.close()
				# Avoid too many requests for the server
				time.sleep(1)

		raw = open('../Data/Data_T_E.txt', 'a')
		val = self.get_values('Temprature [ambiante]')
		for v in val : raw.write(str(v) + ';')
		msg.log('Acquisition completed for T_E')
		raw.close()

if __name__ == '__main__':
	req = RequestEedomus()
	req.get_data()

	
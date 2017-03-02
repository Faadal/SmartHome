# @author : DINDIN Meryll

# Imports

import requests
import json
import time
import tqdm
import numpy as np
import pandas as pd
import os

from datetime import date
from lxml import html
from xml.etree import ElementTree
from collections import defaultdict

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

		msg = Messenger()

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

class RequestQAI:

	def __init__(self):
		self.url1 = 'http://www.lcsqa.org/indices-qualite-air/liste'
		self.url2 = 'http://www.airparif.asso.fr/indices/resultats-jour-citeair#jour/'

	def extract(self, url, req):

		# Scrapping du site de LCSQA
		if url == self.url1 :

			dic = {}
			raw = []
			pwd = req['html']['body']['div']['div'][3]['div'][1]['div']['div'][1]['div'][2]['table']['tbody']['tr']

			for i in range(len(pwd)) :
				val = pwd[i]['td']
				loc = val[2]['#text']
				dic[loc] = {}

				try :
					dic[loc]['Ind'] = float(val[3]['#text'])
				except :
					dic[loc]['Ind'] = np.NaN
				try :
					dic[loc]['O3'] = float(val[4]['#text'])
				except :
					dic[loc]['O3'] = np.NaN
				try :
					dic[loc]['NO2'] = float(val[5]['#text'])
				except :
					dic[loc]['NO2'] = np.NaN
				try :
					dic[loc]['PM10'] = float(val[6]['#text'])
				except :
					dic[loc]['PM10'] = np.NaN
				try :
					dic[loc]['SO2'] = float(val[7]['#text'])
				except :
					dic[loc]['SO2'] = np.NaN

				# Indice global, Dioxyde d'azote, Particules fines, Dioxyde de soufre, Ozo
				for fea in ['Ind', 'NO2', 'PM10', 'SO2', 'O3'] :
					raw.append(dic['PARIS'][fea])

			return raw

		# Scrapping de AirParif
		elif url == self.url2 :

			pwd = req['html']['body']['div']['div']['div'][2]['div'][0]['div'][0]['div'][4]['table']['tr']
			raw = []

			# Etat de la liste :
			# loc = 2 correspond a Paris
			# loc = 6 correspond au departement Hauts-de-Seine
			for loc in [2, 6] : 

				if loc == 2 :
					new = ['Paris']
				else : 
					new = ['Haut-de-Seine']

				# Indice moyen, Dioxyde d'azote, Ozone, Particules Fines
				for ind in [1, 3, 4, 5] :
					try :
						new.append(float(pwd[loc]['td'][ind]['#text'])/10.0)
					except :
						new.append(np.NaN)

				raw.append(np.asarray(new))

			return raw

	def get_data(self):

		err = Error()
		msg = Messenger()

		def etreeToDict(t):

			d = {t.tag: {} if t.attrib else None}
			children = list(t)

			if children:
				dd = defaultdict(list)
				for dc in map(etreeToDict, children):
					for k, v in dc.iteritems():
						dd[k].append(v)
				d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}

			if t.attrib:
				d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())

			if t.text:
				text = t.text.strip()
				if children or t.attrib:
					if text:
						d[t.tag]['#text'] = text
					else:
						d[t.tag] = text

			return d

		for ind, url in enumerate([self.url1, self.url2]) :

			ext = requests.get(url).content
			
			try :
				req = html.fromstring(ext)
				dic = etreeToDict(req)
				raw = self.extract(url, dic)
				msg.log('{}'.format(url))
			except :
				if ind == 0 : 
					raw = np.asarray([np.empty(5)])
					raw[:] = np.NaN
					err.log('Could not extract intel from LCSQA')
				elif ind == 1 :
					raw = np.empty((2,5))
					raw[:] = np.NaN
					err.log('Could not extract intel from PARIF')

			if ind == 0 : 
				pwd = '../AirQuality/QAI_LCSQA'
				lab = ['IndMoyen', 'NO2', 'PM10', 'SO2', 'O3']
				idx = [date.today()] 
			elif ind == 1 : 
				pwd = '../AirQuality/QAI_PARIF'
				lab = ['Location', 'IndMoyen', 'NO2', 'O3', 'PM10']
				idx = [date.today(), date.today()]

			if not os.path.exists(pwd) :
				pd.DataFrame(data=raw, index=idx, columns=lab).to_pickle(pwd)
			else :
				dtf = pd.read_pickle(pwd)
				new = pd.DataFrame(data=raw, index=idx, columns=lab)
				dtf = pd.concat([dtf, new])
				dtf.to_pickle(pwd)

			msg.log('Database {} successfully updated'.format(ind))

if __name__ == '__main__':
	req = RequestQAI()
	req.get_data()
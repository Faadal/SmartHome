# @author : DINDIN Meryll

# Imports

import requests
import json
import time
import tqdm
import numpy as np
import pandas as pd
import os

from pyfoobot import Foobot
from datetime import date
from lxml import html
from collections import defaultdict

from error import *

# Define class request for data gathering

class RequestEedomus:

	def __init__(self):

		# Web Request
		self.usr = 'ZeRV4W'
		self.pwd = '44xNeKX0OsZt0yYR'
		self.aut = requests.get('https://api.eedomus.com/get?api_user={}&api_secret={}&action=auth.test'.format(self.usr, self.pwd))
		self.sen = Logs()
		self.err = Error()
		self.msg = Messenger()

		res = self.aut.json()

		try :
			# Assert if the connection is effective
			if res['success'] == 1 :
				self.msg.log('Authentification on Eedomus server succeeded')
			else :
				self.err.log('Authentification on Eedomus server failed')
			self.acc = True
		except :
			self.err.log('Could not load data from Eedomus server')
			self.acc = False

		self.req = requests.get('https://api.eedomus.com/get?api_user={}&api_secret={}&action=periph.list'.format(self.usr, self.pwd))

		try :
			# Check the request
			self.req = self.req.json()['body']
		except :
			self.err.log('Eedomus request has no body')

	# Create the list of every sensor connected to the Eedomus interface

	def get_peripheriques(self):

		per = {}

		for i in tqdm.tqdm(range(len(self.req))):
			new = self.req[i]['name'].encode('ascii', 'ignore')
			# Solves the problem with bytes type keys
			new = new.decode('utf-8')
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
			raw = req_per(periph).json()['body']['history']
		except :
			self.err.log('Could not load intel for periph {}'.format(periph))

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

		if not self.acc :
			self.err.log('Aborted the request')

		else :

			# Make sure all the devices will be extracted from the Eedomus server
			self.get_peripheriques()

			for gdr in ['T', 'H', 'L', 'M'] :
				for num in tqdm.tqdm([str(e) for e in range(1,13)] + ['C']) :

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

					if len(val) == 0 :
						self.sen.log('Sensor {}_{} does not respond'.format(gdr, num))
					else :
						for v in val : raw.write(str(v) + ';')
						self.sen.log('Acquisition completed for {}_{}'.format(gdr, num))

					raw.close()
					# Avoid too many requests for the server
					time.sleep(1)

			raw = open('../Data/Data_T_E.txt', 'a')
			val = self.get_values('Temprature [ambiante]')
			for v in val : raw.write(str(v) + ';')
			self.msg.log('Acquisition completed for T_E')
			raw.close()

import datetime

# Class implementing the Foobot API

class RequestFoobot:

	def __init__(self):

		self.key = 'eyJhbGciOiJIUzI1NiJ9.eyJncmFudGVlIjoibWVyeWxsLmRpbmRpbkBzdHVkZW50L	mVjcC5mciIsImlhdCI6MTQ5MDcxNDIzMiwidmFsaWRpdHkiOi0xLCJqdGkiOiJjNjUxOT		M0Yi03OGQyLTQ4ZmQtYjE1ZS1lZGZiMWEwNmZjMmEiLCJwZXJtaXNzaW9ucyI6WyJ1c2VyOnJlYWQiLCJkZXZpY2U6cmVhZCJdLCJxdW90YSI6MjAwLCJyYXRlTGltaXQiOjV9.49NuyVZQk4Z6ZpBAm2p_7g_oZfktUO-3IL9h7V0aPwc'
		self.usr = 'meryll.dindin@student.ecp.fr'
		self.pwd = 'bo_yo!2015'
		self.sen = Logs()
		self.err = Error()
		self.msg = Messenger()

		try :
			self.api = Foobot(self.key, self.usr, self.pwd)
			self.dev = self.api.devices()
			self.msg.log('Connection to Foobots successful')
		except :
			self.err.log('Failed connection to Foobots')
		
	def get_data(self):

		for ind, foo in enumerate(tqdm.tqdm(self.dev)) :

			self.sen.log('Foobot {} does respond to request'.format(ind))

			# Get the data from the last 25 hours
			raw = foo.data_period(24*60*60, 0)

			tim, val = [], []
			lab = ['PM10', 'T', 'H', 'CO2', 'VOC', 'PolIndex']

			try :
				for ele in raw['datapoints'] :
					
					tim.append(datetime.datetime.fromtimestamp(int(ele[0])))
					val.append(np.asarray([float(e) for e in ele[1:]]))

				self.msg.log('Successfully extracted the weather intel for {}'.format(self.dte))
			
			except :
				self.err.log('Could not gather intel for Foobot {} on {}'.format(ind, datetime.date().today().srtftime('%d-%m-%Y')))

			pwd = '../Data/Foobot_{}'.format(ind)

			if not os.path.exists(pwd) :
				pd.DataFrame(data=np.asarray(val), index=np.asarray(tim), columns=lab).to_pickle(pwd)
			else :
				dtf = pd.read_pickle(pwd)
				new = pd.DataFrame(data=np.asarray(val), index=np.asarray(tim), columns=lab)
				dtf = pd.concat([dtf, new])

				

				dtf.to_pickle(pwd)

			self.msg.log('{} successfully updated'.format(pwd))


# Job aiming at gathering intel about air quality out of two websites	

class RequestQAI:

	def __init__(self, date=datetime.date.today()):

		self.err = Error()
		self.msg = Messenger()

		self.date = date

		if self.date == datetime.date.today() :
			self.url1 = 'http://www.lcsqa.org/indices-qualite-air/liste'
		else:
			self.url1 = 'http://www.lcsqa.org/indices-qualite-air/liste?date_indice={}'.format(date.strftime('%Y-%m-%d'))	
	
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

		def etreeToDict(t):

			d = {t.tag: {} if t.attrib else None}
			children = list(t)

			if children:
				dd = defaultdict(list)
				for dc in map(etreeToDict, children):
					for k, v in dc.items():
						dd[k].append(v)
				d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}

			if t.attrib:
				d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())

			if t.text:
				text = t.text.strip()
				if children or t.attrib:
					if text:
						d[t.tag]['#text'] = text
				else:
					d[t.tag] = text

			return d

		if self.date == datetime.date.today() :
			ite = [self.url1, self.url2]
		else :
			ite = [self.url1]

		for ind, url in enumerate(ite) :

			try :
				req = html.fromstring(requests.get(url).content)
				dic = etreeToDict(req)
				raw = self.extract(url, dic)
				if ind == 0 : self.msg.log('LCSQA website has been scrapped for day {}'.format(self.date.strftime('%Y-%m-%d')))
				elif ind == 1 : self.msg.log('AIRPARIF website has been scrapped for day {}'.format(self.date.strftime('%Y-%m-%d')))
			except :
				if ind == 0 : 
					raw = np.empty(5)
					raw[:] = np.NaN
					self.err.log('Could not extract intel from LCSQA for the {}'.format(self.date.strftime('%Y-%m-%d')))
				elif ind == 1 :
					raw = np.empty((2, 5))
					raw[:] = np.NaN
					self.err.log('Could not extract intel from PARIF for the {}'.format(self.date.strftime('%Y-%m-%d')))

			if ind == 0 : 
				pwd = '../AirQuality/QAI_LCSQA'
				lab = ['IndMoyen', 'NO2', 'PM10', 'SO2', 'O3']
				idx = np.asarray([self.date])
				raw = np.asarray([raw])
			elif ind == 1 : 
				pwd = '../AirQuality/QAI_PARIF'
				lab = ['Location', 'IndMoyen', 'NO2', 'O3', 'PM10']
				idx = np.asarray([self.date, self.date])
				raw = np.asarray(raw)

			if not os.path.exists(pwd) :
				pd.DataFrame(data=raw, index=idx, columns=lab).to_pickle(pwd)
			else :
				dtf = pd.read_pickle(pwd)
				new = pd.DataFrame(data=raw, index=idx, columns=lab)
				dtf = pd.concat([dtf, new])
				dtf.to_pickle(pwd)

			self.msg.log('{} successfully updated'.format(pwd))

# Job aiming at gathering intel about weather

class RequestWeather:

	def __init__(self, date=datetime.date.today()):
		self.err = Error()
		self.msg = Messenger()
		self.usr = '702b72db6a4d6dfb74390fa36065a5c5'
		self.dte = date
		# Paris geographical position
		self.lat = '48.8534'
		self.lon = '2.3488'
		self.day = str(self.dte) + 'T00:00:00'
		self.url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self.usr, self.lat, self.lon, self.day)

	def get_data(self):

		lab = ['summary', 'aTwea', 'cover', 'dewPoint', 'Hwea', 'ozone', 'rainFall', 'rainProb', 'Pwea', 'Twea', 'windExposure', 'windSpeed']
		new, idx = [], []

		try :
			req = requests.get(self.url).json()
			raw = req['hourly']['data']
			
			for ind in raw :
				tem = []
				idx.append(datetime.datetime.fromtimestamp(ind['time']))
				try :
					tem.append(ind['summary'])
				except :
					tem.append('Unknown')
				for fea in ['apparentTemperature', 'cloudCover', 'dewPoint', 'humidity', 'ozone', 'precipIntensity', 'precipProbability', 'pressure', 'temperature', 'windBearing', 'windSpeed'] :
					try :
						tem.append(float(ind[fea]))
					except :
						tem.append(np.NaN)
				new.append(np.asarray(tem))

			self.msg.log('Successfully extracted the weather intel for {}'.format(self.dte))
		except :
			new = np.zeros((24, 12))
			new[:] = np.NaN
			self.err.log('Could not gather the weather intel for {}'.format(self.dte))

		pwd = '../Weather/WEA'

		if not os.path.exists(pwd) :
			pd.DataFrame(data=np.asarray(new), index=np.asarray(idx), columns=lab).to_pickle(pwd)
		else :
			dtf = pd.read_pickle(pwd)
			new = pd.DataFrame(data=np.asarray(new), index=np.asarray(idx), columns=lab)
			dtf = pd.concat([dtf, new])
			dtf.to_pickle(pwd)

		self.msg.log('{} successfully updated'.format(pwd))
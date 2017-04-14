# Author :  DINDIN Meryll
# Date :    April 04, 2017

import requests
import time

from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO

# Core class to save snapshots
	
def Snap:

	def __init__(self) :
		self.IPa = '138.195.146.167'
		self.prt = '8085'
		self.url = 'http://{}:{}/snapshot.cgi'.format(self.IPa, self.prt)

	def save(self) :
		time.sleep(1)	
		req = requests.get(self.url, auth=HTTPBasicAuth('admin', 'admin'))
		img = Image.open(BytesIO(req.content))
		img.save('./img5.png')
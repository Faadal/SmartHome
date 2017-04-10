# Author :  DINDIN Meryll
# Date :    April 04, 2017

import requests
import time

from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO

if __name__ == '__main__':
	
	time.sleep(1)
	url = 'http://138.195.146.167:8085/snapshot.cgi'
	req = requests.get(url, auth=HTTPBasicAuth('admin', 'admin'))
	img = Image.open(BytesIO(req.content))
	img.save('./img5.png')
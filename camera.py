# Author :  DINDIN Meryll
# Date :    April 04, 2017

# Imports
from imports import *

# Core class to save snapshots
def Snap:

    # Initialisation
    def __init__(self) :
        self.IPa = 'xxx'
        self.prt = 'xxx'
        self.url = 'x{}:{}x'.format(self.IPa, self.prt)

    # Save the screen as an usable image
    def save(self) :
        time.sleep(1)   
        req = requests.get(self.url, auth=HTTPBasicAuth('xxx', 'xxx'))
        img = Image.open(BytesIO(req.content))
        img.save('./img5.png')
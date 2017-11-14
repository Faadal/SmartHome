# @author : DINDIN Meryll

import requests, json, time, tqdm, os, smtplib, datetime, copy, schedule
import numpy as np
import pandas as pd

from pyfoobot import Foobot
from datetime import date
from lxml import html
from collections import defaultdict
from dateutil import parser
from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO
from dateutil.rrule import rrule, DAILY
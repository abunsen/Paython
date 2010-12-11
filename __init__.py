#here so paython is recognized as a module
import os, sys
path = os.path.split(os.path.abspath(__file__))[0].split('/')
path.pop()
sys.path.append('/'.join(path))

import gateways
from lib import *
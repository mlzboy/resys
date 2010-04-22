import ictclas
from ictclas import *

def ict_init():
	import os
	path = os.path.join(os.getcwd(), __file__)
	path = os.path.abspath(path[:path.rfind("/")])
	return ictclas.ict_init(path)

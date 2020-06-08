from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import debugtools as DBG

class  BrowserSession:

	__init__():
		#browser = webdriver.Chrome('/usr/bin/chromedriver')
		self.browser = webdriver.Chrome()

	
class Contest:
	
	__init__(id):
		self.id = id
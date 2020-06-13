from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
import time
import getpass
import debugtools as DBG
from compiler_manager import Compiler


MainPageUrl = 'https://codeforces.com'
PageName = 'Codeforces'
UserHandle = None
Browser = None
CurrentContestUrl = None
CurrentSubmitUrl = None
CurrentSubmitWindow = None
CurrentContestWindow = None


# A decorator for returning to the current tab
def stay_in_tab(func):
	def wrapper(*args, **kwargs):
		currentWindow = Browser.current_window_handle
		ret = func(*args, **kwargs)
		Browser.switch_to.window(currentWindow)
		return ret
	return wrapper


def initBrowser():
	global Browser
	Browser = webdriver.Chrome()
	Browser.get(MainPageUrl)


# AUTHORISATION AT CODEFORCCES.COM

def getCredentials():
	handleField = None
	passwdField = None

	handleFields = Browser.find_elements_by_id('handleOrEmail')
	passwdFields = Browser.find_elements_by_id('password')

	for field in handleFields:
		if field.tag_name == "input":
			handleField = field
			
	for field in passwdFields:
			if field.tag_name == "input":
				passwdField = field
	

	if handleField is None:
		DBG.callErr(msg="Handle field not found", do_quit=True)
	
	if passwdField is None:
		DBG.callErr(msg="Password field not found", do_quit=True)

	#Prompt user for handle and password
	global UserHandle
	UserHandle = input("{} username: ".format(PageName)).rstrip()
	passwd = getpass.getpass("{} password: ".format(PageName))

	handleField.clear()
	handleField.send_keys(UserHandle)

	passwdField.clear()
	passwdField.send_keys(passwd)

	del passwd

	passwdField.send_keys(Keys.ENTER)

	#Check if login succedded (if there is still Enter option in the header)
	time.sleep(1)

	header = Browser.find_element_by_id('header')

	try:
		header.find_element_by_link_text('Enter')
	except NoSuchElementException as exception:
		#login succeeded
		return True

	return False


def login(fromMainPage = False):
	header = Browser.find_element_by_id('header')
	enter = header.find_element_by_link_text('Enter')
	enter.click()
		
	loggedIn = getCredentials()
	while not loggedIn:
		loggedIn = getCredentials()


# ENTERING THE CONTEST

def setContestUrls(constestId, contestType = "contest"):
	global CurrentContestUrl, CurrentSubmitUrl
	CurrentContestUrl = "{}/{}/{}".format(MainPageUrl, contestType, constestId)
	CurrentSubmitUrl = "{}/submit".format(CurrentContestUrl)

def gotoContestPage(contestId = -1, contestType = "contest"):
	global CurrentContestWindow

	if contestId>=0:
		setContestUrls(contestId, contestType)
	
	Browser.get(CurrentContestUrl)
	CurrentContestWindow = Browser.current_window_handle


# SUBMITTING SOLUTIONS

#opens the submission page in the background
#@stay_in_tab
def openSubmitPage():
	global CurrentSubmitWindow

	Browser.execute_script("window.open('{}');".format(CurrentSubmitUrl))
	Browser.switch_to.window(Browser.window_handles[-1])
	CurrentSubmitWindow = Browser.current_window_handle
	
#set the most suitable language
def setSubmittedLang(form, lang):
	options = form.find_elements_by_tag_name('option')

	bestCompiler  = None
	bestOption = None

	for option in options:
		text = option.get_attribute('innerHTML')
		compiler = Compiler()
		compiler.recognize(text)

		if compiler.compatible(lang):
			if bestCompiler is None:
				bestCompiler = compiler
				bestOption = option
			elif lang.version is None and bestCompiler.priority < compiler.priority:
				bestCompiler = compiler
				bestOption = option
			elif lang.version==compiler.lang.version:
				bestCompiler = compiler
				bestOption = option
		
	if bestOption is None:
		DBG.printerr("Didn't find a matching language")
		return False

	bestOption.click()
	
	return True

# finds the submitted
def setSubmittedId(form, problemId):
	options = form.find_elements_by_tag_name('option')

	for option in options:
		value = option.get_attribute('value')
		if value==problemId.lower() or value==problemId.upper():
			option.click()
			return True

	DBG.printerr("Didn't find this problem in the contest")
	return False

#@stay_in_tab
def submitSolution(problemId, sourceFile, lang):

	Browser.switch_to.window(CurrentSubmitWindow)

	fields = Browser.find_elements_by_tag_name('select')

	for field in fields:
		name = field.get_attribute('name')
		
		if name=="programTypeId":
			setSubmittedLang(field, lang)
		if name=="submittedProblemIndex":
			setSubmittedId(field, problemId)
	
	editor = Browser.find_element_by_id('editor')
	sourceInput = editor.find_element_by_tag_name('textarea')

	for line in sourceFile:
		sourceInput.send_keys(line)
	
	
	submitButton = Browser.find_element_by_xpath('//input[@class="submit" and @type="submit"]')

	# Wait for the submit button to be enabled
	maxtimeout = 100
	while submitButton.get_attribute('disabled')=="disabled":
		time.sleep(0.1)
		maxtimeout -=1 
		if maxtimeout < 0:
			#Took too long
			return False

	submitButton.click()
	

	# Failed to submit
	return True


# OPENING STATEMENTS

def openProblemPage(problemId, background, getSamples):
	if background:
		currentWindow = Browser.current_window_handle

	problemUrl = "{}/problem/{}".format(CurrentContestUrl, problemId)
	Browser.execute_script("window.open('{}');".format(problemUrl))
	Browser.switch_to.window(Browser.window_handles[-1])

	if getSamples:
		sampleSection = Browser.find_element_by_xpath('//div[@class="sample-tests"]')
		inputs = sampleSection.find_elements_by_xpath('//div[@class="input"]')
		outputs = sampleSection.find_elements_by_xpath('//div[@class="output"]')

		sampleInputs = []
		sampleOutputs = []

		for sampleIn in inputs:
			field = sampleIn.find_element_by_tag_name('pre')
			sampleInputs.append(field.text)
		
		for sampleOut in outputs:
			field = sampleOut.find_element_by_tag_name('pre')
			sampleOutputs.append(field.text)


	if getSamples:
		return [sampleInputs, sampleOutputs]

	if background:
		Browser.switch_to.window(currentWindow)

def giveBrowser():
	return Browser


def testingRoutine():
	initBrowser()
	#login()
	gotoContestPage(1349)

	#openSubmitPage()
	#submitSolution("A", solution, "c")



if __name__ == "__main__":
	initBrowser()

	login()
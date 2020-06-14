import sys
import requests
import debugtools as DBG
import cf_page as cf

# Contest_helper has the following functionalities:
# * Finding a contest that is about to start
# * Opening statements in browser
# *	Downloading sample tests (by automating browser)
# * Submitting solutions (by automating browser)
# * Reporing vertict of a submission

class  BrowserSession:

	def __init__(self):
		#browser = webdriver.Chrome('/usr/bin/chromedriver')
		self.browser = webdriver.Chrome()

class CF_API:
	APIurl = "https://codeforces.com/api/"
	
	@staticmethod
	def apiRequest(query):
		
		response = requests.get(CF_API.APIurl + query)

		JSON = response.json()
		status =  JSON['status']

		if status == "FAILED":
			if JSON['comment']=="Call limit exceeded":
				DBG.callErr(do_quit = false, msg = "Call limit to API exceeded")
				return None
			else:
				BDG.callErr(do_quit = false, msg = "Unknown API error")
				return None
		
		result = JSON['result']

		return result

	@staticmethod
	def getSubmissions(constestId, handle = None):
		query = "contest.status?contestId={}".format(contestId)
		if not handle is None:
			query = query + "&handle={}".format(handle)
		
		return CF_API.apiRequest(query)
	
	@staticmethod
	def getProblems(contestId):
		query = "contest.standings?contestId={}&".format(contestId)

		contestStandings = CF_API.apiRequest(query)

		if contestStandings is None:
			return None
		
		return contestStandings['problems']
	
	@staticmethod
	def getContests(gym = False):
		if gym:
			query = "contest.list?gym=true"
		else:
			query = "contest.list?gym=false"
		
		return CF_API.apiRequest(query)

			
	
# class for storing information about a submission
# fields data in the same format as in Codeforces API
class Submission:
	def __init__(self, JSON):
		self.id = JSON['id']
		self.relativeTime = JSON['relativeTimeSeconds']
		self.verdict = JSON['verdict']
		self.passedTestCount = JSON['passedTestCount']
		self.timeConsumed = JSON['timeConsumedMillis']
		self.memoryConsumed = JSOM['memoryConsumedBytes']


class Problem:
	def __init__(self, JSON):
		self.problemId = JSON['index']
		self.name = JSON['name']
		self.submissions = dict()
		self.lastSubmission = None
	
class Contest:

	# choose the contest to participate
	# possibly prompts user for choosing the contest
	@staticmethod
	def chooseContest(beforeStart = 60*60):
		contestList = CF_API.getContests()
		chooseFrom = []
		for contest in contestList:
			phase = contest['phase']
			if phase=="CODING":
				chooseFrom.append(contest)
			if phase=="BEFORE":
				if not "relativeTimeSeconds" in contest:
					continue
				
				relativeTime = contest['relativeTimeSeconds']

				if -relativeTime <= beforeStart:
					chooseFrom.append(contest)
		
		if len(chooseFrom)==0:
			print("No contests found", flush = True)
			return None
		
		if len(chooseFrom)==1:
			name = chooseFrom[0]['name']
			contestId = chooseFrom[0]['id']
			print("Assuming: ", name, flush = True)
			return contestId
		
		print("Please choose one of the following contests by typing the correspoding number and ENTER:", flush = True)
		
		cnt = 0
		for contest in chooseFrom:
			name = contest['name']
			print("{}.: {}".format(cnt, name), flush = True)
			cnt +=1
		
		userChoice = input("Number of the contest (0, 1,2, etc.): ")
		
		try:
			contestNo = int(userChoice)
		except ValueError:
			print("Error: This is not a valid choice.")
			return None
		
		if contestNo < 0 or contestNo >= len(chooseFrom):
			print("Error: This is not a valid choice.")
			return None
		
		contest = chooseFrom[contestNo]
		contestId = contest['id']
		return contestId

	def __init__(self, id):
		self.id = id
		self.problems = dict()

	def getProblemList(self):
		problemJSONs = CF_API.getProblems(self.id)

		if problemJSONs is None:
			DBG.callErr(do_quit = false, msg = "Failed to get problem list")
			return
		
		self.problems = []
		for JSON in problemJSONs:
			problem = Problem(JSON)
			self.problems[problem.problemId] = problem
		return
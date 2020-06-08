#module for managing programming language and compiler versions
import debugtools as DBG

class Lang:
	#set of supported languages:
	Langs = {'C', 'C++', 'Python2', 'Python3', 'Java', 'PyPy2', 'PyPy3'}
	#default values
	Aliases = {'G++':'C++', 'Python':'Python3', 'PyPy':'PyPy3', 'c++': 'C++','c':'C', 
				'python2':'Python2', 'python3':'Python3', 'python':'Python3'}

	def __init__(self, name = None, version = None):
		self.name = name
		self.version = version

	#recognize and language and its version from its name (for example C++17, Python2)
	#Python will be translated to Python3
	def recognizeLang(self, name):
		pref = name.rstrip('0123456789!., ')

		if pref in Lang.Langs:
			self.name = pref
		elif pref in Lang.Aliases:
			self.name = Lang.Aliases[pref]
		
		if (not self.name is None) and len(pref) < len(name):
			tail = name[len(pref):]
			tail.rstrip('! ')
			if len(tail)>0:
				self.version = tail


	#recognize the language and its version from the compiler name
	def recognizeComp(self, name):
		words = name.split()
		self.version = None
		self.name = None
		
		for word in words:
			short = word.rstrip('0123456789.!, ')

			if self.version is None and len(word) > 0 and len(short)==0:
				self.version=word

			if self.name is None:
				if short in Lang.Langs:
					self.name = short
				elif short in Lang.Aliases:
					self.name = Lang.Aliases[short]

				if (not self.name is None) and len(short) < len(word):
					tail = word[len(short):]
					tail.rstrip('! ')
					if len(tail) > 0:
						self.version = tail



class Compiler:
	def __init__(self, lang = None, info = None):
		self.lang = Lang()
		#priority of using this compiler (the greater means more frequent use)
		self.priority = 0 

	def write(self):
		DBG.debug(self.lang.name, self.lang.version, self.priority)

	def recognize(self, name):
		
		#recognize the language
		self.lang.recognizeComp(name)

		#always prefer the newest version
		if not self.lang.version is None:
			for i in range(len(self.lang.version)):
				c = self.lang.version[i]
				if ord(c) >= ord('0') and ord(c)<=ord('9'):
					self.priority = self.priority*10
					self.priority += ord(c)-ord('0')
				else:
					 self.priority = self.priority * 100

		for word in name.split():
			if word=="Microsoft":
				self.priority-=100000
		
	def compatible(self, lang):
		return self.lang.name==lang.name

#encoding: UTF-8

class BasicSearch():
	def __init__(self, searchString, dicUsed, mode):
		self.searchString = searchString
		self.dicUsed = dicUsed
		self.mode = mode
		self.result = []
		self.output = None
		self.searchForString()
		
		
	def outputGenerator(self):
		while True:
			for elem in self.result:
				yield elem
		
	def searchForString(self):
		for xTIG in self.dicUsed.values():
			if self.mode == 'Tags':
				if self.searchString == xTIG.getTag().tag:
					self.result.append(xTIG)
					
			else: #mode == 'Values'
				if self.searchString == xTIG.getTag().text:
					self.result.append(xTIG)
					
		self.result = sorted(self.result)
		self.output = self.outputGenerator()
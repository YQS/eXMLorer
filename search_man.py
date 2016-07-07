#encoding: UTF-8
import re

class BasicSearch(object):
	def __init__(self, searchString, dicUsed, mode):
		self.searchString = searchString
		self.dicUsed = dicUsed
		self.result = []
		self.output = None
		
		if mode == 'Tags':
			self.attrName = 'tag'
		else:	#mode == 'Values' or 'Valores'
			self.attrName = 'text'
			
		if '*' in self.searchString:
			#self.complexSearch(self.searchString)
			self.reSearch(self.searchString)
		else:
			self.simpleSearch(self.searchString)		
		
	def outputGenerator(self):
		while True:
			if len(self.result) > 0:
				for elem in self.result:
					yield elem
			else:
				yield ''
		
	def simpleSearch(self, searchString):
		searchLen = len(searchString)
		
		for xTIG in self.dicUsed.values():
			if searchString == getattr(xTIG.getTag(), self.attrName)[:searchLen]:
				self.result.append(xTIG)
					
		self.result = sorted(self.result)
		self.output = self.outputGenerator()
		
	
	def reSearch(self, searchString):
		pattern = searchString.replace('*', '(.)*').replace('?', '(.)')
		
		for xTIG in self.dicUsed.values():
			if re.search(pattern, getattr(xTIG.getTag(), self.attrName)):
					self.result.append(xTIG)
				
		self.result = sorted(self.result)
		self.output = self.outputGenerator()
#encoding: UTF-8
import re
import globals as GL

class BasicSearch(object):
	def __init__(self, searchString, dicUsed, mode, startingPoint):
		self.searchString = searchString
		self.dicUsed = dicUsed
		self.startingPoint = startingPoint
		self.result = []
		self.output = None
		
		self.numberTags()
		
		if mode == 'Tags':
			self.attrName = 'tag'
		else:	#mode == 'Values' or 'Valores'
			self.attrName = 'text'
			
		if '*' in self.searchString:
			self.reSearch(self.searchString)
		else:
			self.simpleSearch(self.searchString)		
		
	def outputGenerator(self):
		fromStart = False
	
		while True:
			if len(self.result) > 0:
				for elem in self.result:
					if fromStart:
						yield elem
					else:
						if elem.tag_order < self.startingPoint:
							continue
						else:
							fromStart = True
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
		
	def numberTags(self):
		def numberChilds(xTIG, n):
			for xChild in xTIG:
				xChild.tag_order = n
				n+=1
				n = numberChilds(xChild, n)
			return n
		
		n = 1
		rootTIG = GL.dicTagsInTree[GL.XMLTree.getroot().tag]
		rootTIG.tag_order = n
		n+=1
		numberChilds(rootTIG, n)
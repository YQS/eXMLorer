#encoding: UTF-8

import re
from operator import attrgetter

from config import Globals as GL


class BasicSearch(object):
	def __init__(self, searchString, dicUsed, mode, startingPoint):
		self.searchString = searchString
		self.dicUsed = dicUsed
		self.startingPoint = startingPoint
		self.result = []
		self.output = None
		self.flags = 0
		
		self.numberTags()
		
		#defino si es case sensitive (y para otros flags del regex, si se llegan a usar)
		if not GL.case_sensitive_search:
			self.flags = re.IGNORECASE
		
		if mode == "XPath":
			self.xPathSearch(self.searchString)
		else:
			#defino campo de busqueda
			if mode == 'Tags':
				self.attrName = 'tag'
			else:	#mode == 'Values' or 'Valores'
				self.attrName = 'text'
				
			#defino modo de busqueda
			if '*' in self.searchString:
				self.reSearch(self.searchString)
			else:
				self.simpleSearch(self.searchString)		
		
		
	def outputGenerator(self):
		self.result = sorted(self.result, key=attrgetter('tag_order'))
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
		searchString += '(.)*'
		
		for xTIG in self.dicUsed.values():
			rawText = getattr(xTIG.xmltag, self.attrName)
			if rawText == None:
				rawText = ''
			if re.search(searchString, rawText, self.flags):
				self.result.append(xTIG)

		self.output = self.outputGenerator()
		
	
	def reSearch(self, searchString):
		pattern = searchString.replace('*', '(.)*').replace('?', '(.)')
		
		for xTIG in self.dicUsed.values():
			if re.search(pattern, getattr(xTIG.xmltag, self.attrName), self.flags):
				self.result.append(xTIG)

		self.output = self.outputGenerator()
		
		
	def xPathSearch(self, searchString):
		root = GL.xml_tree.getroot()
		foundTags = root.findall(searchString)
		
		for xTIG in self.dicUsed.values():
			if xTIG.xmltag in foundTags:
				self.result.append(xTIG)

		self.output = self.outputGenerator()
		
		
	def numberTags(self):
		def numberChilds(xTIG, n):
			for xChild in xTIG:
				xChild.tag_order = n
				n+=1
				n = numberChilds(xChild, n)
			return n
		
		n = 1
		rootTIG = GL.editag_dictionary[GL.xml_tree.getroot().tag]
		rootTIG.tag_order = n
		n+=1
		numberChilds(rootTIG, n)
		
	
def xPathSearch(path, tag=None):
	if tag <> None:
		return tag.findall(path)
	else:
		return GL.xml_tree.getroot().findall(path)
'''
class XPathSearch(object):
	def __init__(self, root, path):
		self.root = root
		self.path = path
		#self.returnList = returnList
'''
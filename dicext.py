# encoding: UTF-8
import globals as GL
import os.path

class DictionaryFile(object):
	def __init__(self, filename):
		self.dic = {}
		self.filename = filename
		self.getDic()
		
	def getDic(self):
		if not os.path.exists(self.filename):
			with open(self.filename, 'w') as txt:
				txt.write('')
	
		with open(self.filename, 'r') as txt:
			sDic = txt.read()
			if sDic <> '':
				dicNames = eval(sDic)
			else:
				dicNames = {}
		self.dic = dicNames
		
	def save(self):
		with open(self.filename, 'w') as txt:
			txtDic = repr(self.dic).replace(',' , ',\n\r')
			txt.write(txtDic)
	
	def updateDic(self, parentTag, childTag):
		self.dic[parentTag] = childTag
	
	def deleteFromDic(self, key):
		del self.dic[key]

#encoding: UTF-8
#simple SQL formatter

import re

def simplePrettify(rawText):
	def cutLine(text, word, times=1):
		return text.replace(word, '\n' * times + word)
		
	rawText = rawText.upper()
	rawText = rawText.replace(', ', ', \n')
	rawText = cutLine(rawText, 'FROM', times=2)
	rawText = cutLine(rawText, 'LEFT JOIN')
	rawText = cutLine(rawText, 'LEFT OUTER JOIN')
	rawText = cutLine(rawText, 'WHERE', times=2)
	rawText = cutLine(rawText, 'ORDER BY', times=2)
	rawText = cutLine(rawText, 'GROUP BY', times=2)
	rawText = cutLine(rawText, 'LIMIT', times=2)
	
	return rawText
	
	
def simpleLinefy(rawText):
	return re.sub('[\s]+', ' ', rawText.strip())
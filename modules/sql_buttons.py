#MODULE: SQL Buttons

#importing eXMLorer directory to PYTHONPATH
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import re

from config import globals as GL
from app import module_interface as INT
#import sql_formatter




context = 'TOPLEVEL'

def run(parent=None, field=None, useButtons=True):
	if GL.useSQLButtons and useButtons:
		INT.createButton(parent, 'toplevel_sql_linefy', lambda: bSQLButtons(field, simpleLinefy), align='grid', alignParams={'row':0, 'column':0})
		INT.createButton(parent, 'toplevel_sql_prettyprint', lambda: bSQLButtons(field, simplePrettify), align='grid', alignParams={'row':0, 'column':1})



def bSQLButtons(field, SQLfunction):
	#asumo que si uso estas funciones, el firstField es el campo que me interesa
	text = field.get('1.0', 'end')
	text = SQLfunction(text)
	field.delete('1.0', 'end')
	field.insert('1.0', text)

#formatting functions (ex-sql_formatter)
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

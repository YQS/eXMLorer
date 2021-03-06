# encoding: UTF-8

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import globals as GL
import re
import StringIO

class ParserWithComments(ET.XMLParser):
	#robado del mismisimo autor del módulo ElementTree
	#http://effbot.org/zone/element-pi.htm
	def __init__(self, useEncoding):
		if useEncoding:
			ET.XMLParser.__init__(self, encoding='utf-8')
		else:
			ET.XMLParser.__init__(self)
		#asumes ElementTree 1.2.X
		self._parser.CommentHandler = self.handle_comment
		
	def handle_comment(self, data):
		self._target.start(ET.Comment, {})
		self._target.data(data)
		self._target.end(ET.Comment)

def getXML(filename, useEncoding=False):
	#parseo el xml y instancio el root, para analizarlo todo
	try:
		parser = ParserWithComments(useEncoding)
		GL.XMLTree = ET.parse(filename, parser)
	except:
		return None
		
	root = GL.XMLTree.getroot()
	GL.XMLEncoding = getEncoding(filename)
	#GL.XMLParentMap = {c:p for p in GL.XMLTree.iter() for c in p}

	print root.tag
	print root.attrib
	#print 'encoding %s' % GL.XMLEncoding
	print

	#funcion para imprimir el tag y todos sus child
	def showChilds(xBase, xLevel):
		xText = "	" * xLevel
		for xChild in xBase:
			print xText + xChild.tag
			showChilds(xChild, xLevel + 1)

	print root.tag
	#showChilds(root, 1)
	
	return root
	
def parseStringXML(stringXML):
	#return ET.fromstring(stringXML)
	#se genera un objeto en memoria con StringIO para poder usar el ET.parse y que sin importar el origen, se parsee igual
	print stringXML
	fileObj = StringIO.StringIO(stringXML)
	root = getXML(fileObj, useEncoding=True)
	fileObj.close()
	return root
	
def parseStringXML_old(stringXML):
	#creado porque el la funcion pasteFromClipboard() parsea un string pero no devuelve root
	#TODO: agregar la excepción en parseStringXML() y getXML()
	return ET.fromstring(stringXML)

def getEncoding(filename):
	def regex_search(xPattern, xString):
		try:
			xReturn = re.search(xPattern, xString).group(0)
		except:
			xReturn = ''
		finally:
			return xReturn
	
	xEncoding = ''
	
	#reviso si filename es un objeto en memoria
	if isinstance(filename, StringIO.StringIO):
		first_line = filename.getvalue()
	else:
		#es un path
		xmlfile = open(filename, 'r')
		first_line = xmlfile.readline()
	
	if first_line[0:2] == '<?':
		xEncoding = regex_search('encoding="(\S)*"', first_line)
		xEncoding = xEncoding.replace('encoding=', '')
		xEncoding = xEncoding.replace('"', '')
		
		if xEncoding == '':
			xEncoding = regex_search('encoding=\'(\S)*\'', first_line)
			xEncoding = xEncoding.replace('encoding=', '')
			xEncoding = xEncoding.replace('\'', '')
			
	if not isinstance(filename, StringIO.StringIO):
		xmlfile.close()
			
	return xEncoding


def saveXML(XMLTree, filename):#, prettyPrint, eliminateSpaceInSelfClosingTag=True):
	print 'saving in %s' % filename
	#XMLTree.write(filename, encoding=GL.XMLEncoding, xml_declaration=True)

	stringXML = getStringXML(XMLTree.getroot())
	
	with open(filename, 'w') as xmlfile:
		xmlfile.write(stringXML)
		
def getStringXML(elem, method=''):
	if GL.defaultPrettyPrint:
		prettify(elem, linefy=GL.linefyAtSave)
		
	if method == '':
		method = 'xml'
		
	#se agrega el encoding, si existe
	if GL.XMLEncoding <> '':
		stringXML = ET.tostring(elem, GL.XMLEncoding, method=method)
	else:
		stringXML = ET.tostring(elem, method=method)
	
	#reemplazo los <tag /> por <tag/>
	if GL.eliminateSpaceInSelfClosingTag:
		stringXML = stringXML.replace(' />', '/>')
		
	return stringXML

		
def prettify(elem, level=0, defaultIndentation='	', linefy=False):
	"""default indentation is Tab"""
	i = "\n" + level*defaultIndentation
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + defaultIndentation
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			prettify(elem, level+1, linefy=linefy)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i
			if elem.text:
				if linefy:
					#copiado de simpleLinefy del modulo sql_buttons.py
					elem.text = re.sub('[\s]+', ' ', elem.text.strip())
				else:
					elem.text = elem.text.rstrip()

	
def newElement(xParent, xTag, xText, xAttrib, xOrder):
	#xNewElement = ET.SubElement(xParent, xTag, xAttrib)
	xNewElement = ET.Element(xTag, xAttrib)
	xParent.insert(xOrder, xNewElement)
	xNewElement.text = xText
	return xNewElement
	
def newComment(xParent, xText, xOrder):
	xComment = ET.Comment(xText)
	xParent.insert(xOrder, xComment)
	return xComment
	
def insertElement(xParent, xElement, xOrder):
	xParent.insert(xOrder, xElement)
	
def moveTag(xParent, xTag, xPosition):
	xParent.remove(xTag)
	xParent.insert(xPosition, xTag)
	
def fileHasChanged(rootTag, filename):
	try:
		root2 = ET.parse(filename)
	except:
		print "could't parse filename"
		return None
	
	return ET.tostring(rootTag).strip() <> ET.tostring(root2.getroot()).strip()

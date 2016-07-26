# encoding: UTF-8

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import globals as GL
import re

class ParserWithComments(ET.XMLTreeBuilder):
	#robado del mismisimo autor del módulo ElementTree
	#http://effbot.org/zone/element-pi.htm
	def __init__(self):
		ET.XMLTreeBuilder.__init__(self)
		#asumes ElementTree 1.2.X
		self._parser.CommentHandler = self.handle_comment
		
	def handle_comment(self, data):
		self._target.start(ET.Comment, {})
		self._target.data(data)
		self._target.end(ET.Comment)

def getXML(filename):
	#parseo el xml y instancio el root, para analizarlo todo
	try:
		parser = ParserWithComments()
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

def getEncoding(filename):
	def regex_search(xPattern, xString):
		try:
			xReturn = re.search(xPattern, xString).group(0)
		except:
			xReturn = ''
		finally:
			return xReturn
	
	xEncoding = ''
	with open(filename, 'r') as xmlfile:
		first_line = xmlfile.readline()
		if first_line[0:2] == '<?':
			xEncoding = regex_search('encoding="(\S)*"', first_line)
			xEncoding = xEncoding.replace('encoding=', '')
			xEncoding = xEncoding.replace('"', '')
			
			if xEncoding == '':
				xEncoding = regex_search('encoding=\'(\S)*\'', first_line)
				xEncoding = xEncoding.replace('encoding=', '')
				xEncoding = xEncoding.replace('\'', '')
				
			
			
	return xEncoding			

		
def saveXML(XMLTree, filename):#, prettyPrint, eliminateSpaceInSelfClosingTag=True):
	print 'saving in %s' % filename
	#XMLTree.write(filename, encoding=GL.XMLEncoding, xml_declaration=True)
	
	encoding = GL.XMLEncoding

	if GL.defaultPrettyPrint:
		prettify(XMLTree.getroot())
	
	#agrego el encoding en cabecera
	#(solo reemplazo porque el toprettyxml de minidom ya le agrega la declaracion de xml)
	if encoding <> '':
		prettyXML = ET.tostring(XMLTree.getroot(), encoding).replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="%s" ?>' % encoding)
	else:
		prettyXML = ET.tostring(XMLTree.getroot())
	
	#reemplazo los <tag /> por <tag/>
	if GL.eliminateSpaceInSelfClosingTag:
		prettyXML = prettyXML.replace(' />', '/>')
	
	with open(filename, 'w') as xmlfile:
		xmlfile.write(prettyXML)
		
def getStringXML(elem):
	if GL.defaultPrettyPrint:
		prettify(elem)
		
	if GL.XMLEncoding <> '':
		stringXML = ET.tostring(elem, GL.XMLEncoding)
	else:
		stringXML = ET.tostring(elem)
	
	if GL.eliminateSpaceInSelfClosingTag:
		stringXML = stringXML.replace(' />', '/>')
		
	return stringXML

		
def prettify(elem, level=0, defaultIndentation='	'):
	"""default indentation is Tab"""
	i = "\n" + level*defaultIndentation
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + defaultIndentation
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			prettify(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

	
def newElement(xParent, xTag, xText, xAttrib, xOrder):
	#xNewElement = ET.SubElement(xParent, xTag, xAttrib)
	xNewElement = ET.Element(xTag, xAttrib)
	xParent.insert(xOrder, xNewElement)
	xNewElement.text = xText
	return xNewElement
	
def moveTag(xParent, xTag, xPosition):
	xParent.remove(xTag)
	xParent.insert(xPosition, xTag)
	
def fileHasChanged(rootTag, filename):
	try:
		root2 = ET.parse(filename)
	except:
		return None
	
	return ET.tostring(rootTag) <> ET.tostring(root2.getroot())

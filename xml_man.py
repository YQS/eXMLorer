# encoding: UTF-8

import xml.etree.ElementTree as ET
import globals as GL
import re

def getXML(filename):
	#parseo el xml y instancio el root, para analizarlo todo
	try:
		GL.XMLTree = ET.parse(filename)
	except:
		return None
		
	root = GL.XMLTree.getroot()
	GL.XML_encoding = getEncoding(filename)
	GL.XMLParentMap = {c:p for p in GL.XMLTree.iter() for c in p}

	print root.tag
	print root.attrib
	#print 'encoding %s' % GL.XML_encoding
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

		
def saveXML(XMLTree, filename):
	print 'saving in %s' % filename
	XMLTree.write(filename, encoding=GL.XML_encoding, xml_declaration=True)
	
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

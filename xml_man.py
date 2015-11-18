# encoding: UTF-8

import xml.etree.ElementTree as ET
import globals as GL

def getXML(filename):
	#parseo el xml y instancio el root, para analizarlo todo
	GL.XMLTree = ET.parse(filename)
	#tree = ET.parse('stylers.xml')
	root = GL.XMLTree.getroot()
	GL.XMLParentMap = {c:p for p in GL.XMLTree.iter() for c in p}

	print root.tag
	print root.attrib
	print

	#funcion para imprimir el tag y todos sus child
	def showChilds(xBase, xLevel):
		xText = "	" * xLevel
		for xChild in xBase:
			print xText + xChild.tag
			showChilds(xChild, xLevel + 1)

	print root.tag
	showChilds(root, 1)
	
	return root
	
def newElement(xParent, xTag, xText, xAttrib, xOrder):
	#xNewElement = ET.SubElement(xParent, xTag, xAttrib)
	xNewElement = ET.Element(xTag, xAttrib)
	xParent.insert(xOrder, xNewElement)
	xNewElement.text = xText
	return xNewElement
	

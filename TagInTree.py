# encoding: UTF-8

class TagInTree(object):
	def __init__(self, parent_id, id, xmltag, treeview, order='end'):
		print 'new TagInTree'
		#inicializo las variables del objeto
		self.id = id
		self.parent_tag = None	#######
		self.xmltag = None
		self.tagname = ''
		self.subname = ''
		self.treenode = None
		self.parent_treeview = None
		self.parent_id = parent_id
		##########
		self.setTag(xmltag)
		self.setNode(parent_id, id, treeview, order)
		self.setColumn('name', self.id)
		self.setColumn('data', self.getTag().text)
		self.setColumn('size', self.subname)

	# SETS
	def setTag(self, xmltag):
		self.xmltag = xmltag
		self.tagname = '<' + self.xmltag.tag + '>'
		self.subname = getSubnameOfTag(self.xmltag)
		#self.haschild = self.hasChild()
		
	def setNode(self, parent_id, id, treeview, order):
		#Asume que self.xmltag ya está asignado (por ahí conviene hacer una verificación)
		self.treenode = treeview.insert(parent_id, order, id, text= self.tagname + ' ' + getSubnameOfTag(self.xmltag) )
		self.parent_treeview = treeview
		
	def setColumn(self, column, value):
		self.parent_treeview.set( self.id, column, value )
	
	def hasChild(self):
		xHasChild = False
		for xChild in self.xmltag:
			xHasChild = True
			break
			
		return xHasChild

	# GETS
	def getTag(self):
		return self.xmltag
	
	def getNode(self):
		return self.treenode
		
	def getTreeView(self):
		return self.parent_treeview		
	


def getSubnameOfTag(xTag):
	xName = ''
	for xChild in xTag:
		if (xChild.tag.find('Name', 0) >= 0):
			xName = xChild.text
			break
			
	#if xName == '':
	#	xName = xTag.tag
		
	return xName

def generateTagInTree(parent_id, id, xmltag, treeview):			#Deprecated
	newTagInTree = TagInTree(id)
	newTagInTree.setTag(xmltag)
	newTagInTree.setNode(parent_id, id, treeview)
	
	newTagInTree.setColumn('name', newTagInTree.id)
	newTagInTree.setColumn('data', newTagInTree.getTag().text)
	newTagInTree.setColumn('size', newTagInTree.subname)
	
	return newTagInTree
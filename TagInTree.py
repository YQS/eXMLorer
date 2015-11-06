class TagInTree(object):
	def __init__(self, id):
		print 'new TagInTree'
		self.id = id
		self.xmltag = None
		self.treenode = None
		self.parent_treeview = None
		self.tagname = ''
		self.subname = ''
		
	def getTag(self):
		return self.xmltag
	
	def setTag(self, xmltag):
		self.xmltag = xmltag
		self.tagname = '<' + xmltag.tag + '>'
		self.subname = getSubnameOfTag(xmltag)
	
	def getNode(self):
		return self.treenode
		
	def setNode(self, parent_id, id, treeview):
		self.treenode = treeview.insert(parent_id, 'end', id, text='<' + self.xmltag.tag + '> ' + getSubnameOfTag(self.xmltag) )
		self.parent_treeview = treeview
		
	def getTreeView(self):
		return self.parent_treeview
		
	def setDataColumn(self, value):
		self.parent_treeview.set( self.id, 'data', value )


def getSubnameOfTag(xTag):
	xName = ''
	for xChild in xTag:
		if (xChild.tag.find('Name', 0) >= 0):
			xName = xChild.text
			break
			
	#if xName == '':
	#	xName = xTag.tag
		
	return xName

def generateTagInTree(parent_id, id, xmltag, treeview):
	newTagInTree = TagInTree(id)
	newTagInTree.setTag(xmltag)
	newTagInTree.setNode(parent_id, id, treeview)
	
	treeview.set(id, 'name', id)
	treeview.set(id, 'data', newTagInTree.getTag().text)
	treeview.set(id, 'size', newTagInTree.subname)

	return newTagInTree

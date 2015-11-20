# encoding: UTF-8
import globals as GL

class TagInTree(object):
	def __init__(self, parent_id, id, xmltag, parent_tag, treeview, order='end'):
		print 'new TagInTree'
		#inicializo las variables del objeto
		self.id = id
		self.parent_tag = parent_tag
		self.xmltag = None
		self.tagname = ''
		self.subname = ''
		self.treenode = None
		self.parent_treeview = None
		self.parent_id = parent_id
		##########
		self.setTag(xmltag)
		self.setNode(parent_id, id, treeview, order)
		self.setColumn('data', self.getTag().text)
		#self.setColumn('name', self.id)
		#self.setColumn('size', self.subname)
		
	def __del__(self):
		print 'TagInTree %s destroyed' % self.id

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
		print value
		if value <> None:
			value = value.encode(encoding='UTF-8')
			self.parent_treeview.set( self.id, column, value[:GL.dataColumnTextLimit] )
			#self.parent_treeview.set( self.id, column, value )
	
	def hasChild(self):
		xHasChild = False
		for xChild in self.xmltag:
			xHasChild = True
			break
			
		return xHasChild
		
	def updateSubname(self, newSubname):
		self.subname = newSubname
		self.parent_treeview.item(self.id, text= self.tagname + ' ' + self.subname)

	# GETS
	def getTag(self):
		return self.xmltag
	
	def getNode(self):
		return self.treenode
		
	def getTreeView(self):
		return self.parent_treeview
		
	def getParent(self):
		try:
			xParent = GL.dicTagsInTree[ self.parent_treeview.parent(self.id)]
		except:
			xParent = None
			
		return xParent
	


def getSubnameOfTag(xTag):
	xName = ''
	xPossibleChildForName = None
	xStringToFind = GL.dicTagSubnames.dic.get(xTag.tag, '*******')	#I hope that I don't find a tag like this!
	for xChild in xTag:
		if (xChild.tag.find(xStringToFind, 0) >= 0):
			try:
				xName = str(xChild.text)
			except UnicodeEncodeError:
				xName = xChild.text.encode('utf-8')
			break
		elif (xChild.tag.find('Name', 0) >= 0):
			xPossibleChildForName = xChild

	if xName == '':
		if xPossibleChildForName <> None:
			xName = str(xPossibleChildForName.text)
			GL.dicTagSubnames.dic[xTag.tag] = xPossibleChildForName.tag
			GL.dicTagSubnames.save()
		
	return xName

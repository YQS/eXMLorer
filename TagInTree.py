# encoding: UTF-8
import globals as GL
from operator import methodcaller


class TagInTree(object):
	def __init__(self, parent_id, id, xmltag, parent_tag, treeview, order='end', is_comment=False):
		#print 'new TagInTree'
		#inicializo las variables del objeto
		self.id = id
		self.parent_tag = parent_tag
		self.xmltag = None
		self.tagname = ''
		self.subname = ''
		self.treenode = None
		self.parent_treeview = None
		self.parent_id = parent_id
		self.tag_order = 0
		self.is_comment = is_comment
		##########
		self.setTag(xmltag)
		self.setNode(parent_id, id, treeview, order)
		self.setColumn('data', self.getTag().text)
		self.setColumn('subname', self.subname)
		#self.setColumn('size', self.subname)
		
	def __del__(self):
		pass
		#print 'TagInTree %s destroyed' % self.id
		
	def __repr__(self):
		return self.id
	
	def __iter__(self):
		childList = []
		for xTIG in GL.dicTagsInTree.values():
			if xTIG.parent_id == self.id:
				childList.append(xTIG)
		childList = sorted(childList, key=methodcaller('getXMLPosition'))

		for childTIG in childList:
			#print childTIG
			yield childTIG
	

	# SETS
	def setTag(self, xmltag):
		self.xmltag = xmltag
		if self.is_comment:
			self.tagname = '<!-- comment -->'
			self.subname = ''
		else:
			self.tagname = self.getTagName()
			self.subname = getSubnameOfTag(self.xmltag)
		#self.haschild = self.hasChild()
		
	def getTagName(self):
		return '<' + self.xmltag.tag + '>'
		
	def setNode(self, parent_id, id, treeview, order):
		#Asume que self.xmltag ya está asignado (por ahí conviene hacer una verificación)
		#self.treenode = treeview.insert(parent_id, order, id, text= self.tagname + ' ' + getSubnameOfTag(self.xmltag) )
		self.treenode = treeview.insert(parent_id, order, id, text= self.tagname)
		self.parent_treeview = treeview
		
		if self.is_comment:
			self.parent_treeview.tag_bind('comment', '<TreeviewOpen>', self.treenode)
			self.parent_treeview.tag_configure('comment', background='green')
		
	def setColumn(self, column, value):
		#print value
		if value <> None:
			uvalue = value[:GL.dataColumnTextLimit].replace('\n', '')
			#uvalue = value.encode(encoding='UTF-8')
			#uvalue = value.decode(encoding=GL.XMLEncoding)
			#self.parent_treeview.set( self.id, column, uvalue[:GL.dataColumnTextLimit] )
			self.parent_treeview.set( self.id, column, uvalue )
	
	
	def hasChild(self):
		xHasChild = False
		for xChild in self.xmltag:
			xHasChild = True
			break
			
		return xHasChild
		
	def updateTag(self, newTag, newValue):
		self.xmltag.tag = newTag
		self.xmltag.text = newValue
		self.tagname = self.getTagName()
		self.subname = getSubnameOfTag(self.xmltag)
		
		self.parent_treeview.item(self.id, text=self.tagname)
		self.setColumn('data', self.getTag().text)
		self.setColumn('subname', self.subname)
		
	def updateSubname(self, newSubname):
		self.subname = newSubname
		#self.parent_treeview.item(self.id, text= self.tagname + ' ' + self.subname)

		
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
	
	def getTreeViewIndex(self):
		return self.parent_treeview.index(self.id)
		
	def getXMLPosition(self):
		try:
			return self.parent_tag.getchildren().index(self.getTag())
		except:
			return '<Root>'
			
	def getNumberOfSiblings(self):
		return len(self.parent_tag.getchildren())
		
	def getNumberOfChildren(self):
		return len(self.xmltag.getchildren())
	
	def getPath(self):
		xParent = self.getParent()
		if self.is_comment:
			xTag = 'comment'
		else:
			xTag = self.xmltag.tag
			
		if xParent == None:
			return xTag
		else:
			return xParent.getPath() + '/' + xTag
			
	


def getSubnameOfTag(xTag):
	xName = ''
	xPossibleChildForName = None
	#print xTag, xTag.tag, xTag.text
	xStringToFind = GL.dicTagSubnames.dic.get(xTag.tag, '*******')	#I hope that I don't find a tag like this!
	for xChild in xTag:
		if type(xChild.tag).__name__ == 'str':
			#if xChild.tag is a XML tag and not a Comment
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

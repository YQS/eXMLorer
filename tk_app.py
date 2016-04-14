# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
import globals as GL
import app_language as LANG
import TagInTree as TIG
import xml_man
import tk_treeview


# CLASSES

class FrameExt(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.dic = {}
		
	def addWidget(self, sWidget, sKey):
		sCodeLine = '%s(self)' % sWidget
		print sCodeLine
		self.dic[sKey] = eval(sCodeLine)
		return self.dic[sKey]
		
	def clean(self):
		for widget in self.winfo_children():
			widget.destroy()

class FramePack(object):
	def __init__(self, master):
		self.menu = FrameExt(master)
		self.center = FrameExt(master)
		self.footer = FrameExt(master)
		
		self.treeview = FrameExt(self.center)
		self.buttons = FrameExt(self.center)

class MainApp(Tk):
	def __init__(self, iconfile='test.gif', lExcludeMenu = []):
		Tk.__init__(self)
		self.title('eXMLorer')
		try:
			self.iconImage = PhotoImage(file= iconfile)
			self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
		except TclError:
			print 'No se encontro el archivo de icono %s' % iconfile
		
		#elementos del main
		self.excludeList = lExcludeMenu
		
		self.menubar = None
		fillMenu(self)
		
		self.frames = FramePack(self)
		
		self.frames.menu.pack(side=TOP, fill=X)
		fillButtonBarFrame(self.frames.menu, lExcludeMenu)
		
		self.frames.center.pack(side=TOP, fill=BOTH, expand=1)
		self.frames.treeview.pack(side=LEFT, fill=BOTH)
		self.frames.buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
		
		self.frames.footer.pack(side=BOTTOM, fill=X)
		fillFooterFrame(self.frames.footer)
		
		self.bind('<F5>', lambda event: refreshApp(self))

		
# METHODS

def fillMenu(mainApp):
	menubar = Menu(mainApp)
	mainApp.config(menu=menubar)
	mainApp.menubar = menubar
	
	if not 'menu_file' in mainApp.excludeList:
		menu_file = Menu(menubar, tearoff=0)
		menubar.add_cascade(label=GL.names['menu_file'], menu=menu_file)
		
		menu_file.add_command(label= GL.names['menu_file_open'])
		menu_file.add_command(label= GL.names['menu_file_save'])
		menu_file.add_command(label= GL.names['menu_file_saveas'])
		menu_file.add_command(label= GL.names['menu_file_exit'])
	
	if not 'menu_config' in mainApp.excludeList:
		#seteo menu Configuración
		menu_config = Menu(menubar, tearoff=0)
		menubar.add_cascade(label= GL.names['menu_config'], menu=menu_config)
		
		menu_config_language = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_language']+ ' ', menu=menu_config_language)
		#menu_config.add_command(label= GL.names['menu_config_language'], command=None)
		
		#seteo lenguajes
		menu_config_language.add_command(label=GL.names['menu_config_language_spa'], command= lambda: mChangeLang(mainApp, 'SPA'))
		menu_config_language.add_command(label=GL.names['menu_config_language_eng'], command= lambda: mChangeLang(mainApp, 'ENG'))
		
		
		
		
		
def fillButtonBarFrame(xFrame, lExcludeMenu):
	mainApp = xFrame.master

	if not 'label_filename' in lExcludeMenu:
		label_filename = xFrame.addWidget('Label', 'label_filename')
		label_filename.configure(padding=(10,0,0,0))
		label_filename.grid(column=3, row=0)
	
	getButton(xFrame, 'button_open', lExcludeMenu, 0, 0, command = lambda: openXML(mainApp.frames.treeview, mainApp.frames.buttons, xFrame.dic['label_filename'] ))
	getButton(xFrame, 'button_save', lExcludeMenu, 0, 1, command = lambda: saveXML(mainApp, 'SAVE'))
	getButton(xFrame, 'button_saveAs', lExcludeMenu, 0, 2, command = lambda: saveXML(mainApp, 'SAVEAS'))
	getButton(xFrame, 'button_copyTag', lExcludeMenu, 1, 0, command = lambda: copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
	getButton(xFrame, 'button_deleteTag', lExcludeMenu, 1, 1, command = lambda: deleteTagInTree( GL.appTreeView.focus() ))		
	
	## debug buttons
	getButton(xFrame, 'button_glTreeView', lExcludeMenu, 1, 1, command = lambda: checkTreeView())
	getButton(xFrame, 'button_analyze', lExcludeMenu, 0, 1, command = lambda: bCheckEntries(mainApp.frames.buttons))
	getButton(xFrame, 'button_dicSubnames', lExcludeMenu, 1, 3, command = lambda: bPrintDicSubnames())
	getButton(xFrame, 'button_getDicSubnames', lExcludeMenu, 1, 3, command = lambda: GL.getDicSubnames())
	getButton(xFrame, 'button_printEncoding', lExcludeMenu, 1, 2, command = lambda: xml_man.getEncoding(GL.filename))
	
def fillFooterFrame(xFrame, lExcludeMenu=[]):
	getButton(xFrame, 'button_moveUp', lExcludeMenu, 0, 1, command = lambda: tk_treeview.moveNode(
																						 GL.appTreeView.focus(),
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getParent().id,
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getTreeViewIndex() - 1,
																						 GL.dicTagsInTree))
																						 
	getButton(xFrame, 'button_moveDown', lExcludeMenu, 0, 2, command = lambda: tk_treeview.moveNode(
																						 GL.appTreeView.focus(),
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getParent().id,
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getTreeViewIndex() + 1,
																						 GL.dicTagsInTree))
																						 
	getButton(xFrame, 'button_moveBeginnnig', lExcludeMenu, 0, 3, command = lambda: tk_treeview.moveNode(
																						 GL.appTreeView.focus(),
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getParent().id,
																						 0,
																						 GL.dicTagsInTree))
																						 
	getButton(xFrame, 'button_moveEnd', lExcludeMenu, 0, 4, command = lambda: tk_treeview.moveNode(
																						 GL.appTreeView.focus(),
																						 GL.dicTagsInTree[GL.appTreeView.focus()].getParent().id,
																						 'end',
																						 GL.dicTagsInTree))

def getButton(xMaster, name, lExcludeMenu, xRow, xColumn, command=''):
	if not name in lExcludeMenu:
		xButton = xMaster.addWidget('Button', name)
		xButton.configure(text= GL.names[name], width= GL.buttonWidth, command=command)
		xButton.grid(column=xColumn, row=xRow)

def getFilename():
	filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')])
	print filename
	return filename

def getIDForTreeView(xTag, dicTagsInTree):
	i = 0
	while dicTagsInTree.has_key(xTag + str(i)):
		i += 1
	dicTagsInTree[xTag + str(i)] = 0
	return xTag + str(i)	
	
def addXMLToTree(xBase, xBaseID, dicTagsInTree, appTreeView):
	for xChild in xBase:
		xID = getIDForTreeView(xChild.tag, dicTagsInTree)
		dicTagsInTree[xID] = TIG.TagInTree(xBaseID, xID, xChild, xBase, appTreeView)
		addXMLToTree(xChild, xID, dicTagsInTree, appTreeView)
		
		
# BUTTON METHODS

def openXML(band_treeview, band_buttons, label_filename):
	xFilename = getFilename()
	
	if xFilename <> '':
		band_treeview.clean()
		band_buttons.clean()
		GL.filename = xFilename
		label_filename.config(text= GL.filename)
		
		root = xml_man.getXML(GL.filename)
		#root = xml_man.getXML('stylers.xml')
		
		if root == None:
			tkMessageBox.showerror('eXMLorer', 'El archivo %s no es un archivo XML valido' % GL.filename)
			label_filename.config(text= '')
		else:	
			GL.dicTagsInTree = {}
			GL.appTreeView = tk_treeview.getTreeView(band_treeview, band_buttons, GL.dicTagsInTree)
			
			GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
			addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)

def saveXML(mainApp, modo):
	if modo == 'SAVEAS':
		save_filename = tkFileDialog.asksaveasfilename( filetypes=[('Archivos XML', '.xml'), ('Todos los archivos', '.*')], 
														initialfile = GL.filename,
														parent = mainApp)
	else:
		save_filename = GL.filename
	
	if save_filename:
		#print 'saving in ' + save_filename
		#GL.XMLTree.write(save_filename)
		print save_filename[-4:]
		if save_filename[-4:] <> '.xml':
			save_filename += '.xml'
		xml_man.saveXML(GL.XMLTree, save_filename)
		GL.filename = save_filename
		mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
		

		
def copyTagInTree(oldTagInTree, xLevel, newparent = None):
	if oldTagInTree <> None:
		if newparent == None:
			xBaseID = oldTagInTree.parent_id
			xParentTag = oldTagInTree.parent_tag
		else:
			xBaseID = newparent.id
			xParentTag = newparent.getTag()
		
		xOrder = oldTagInTree.getTreeViewIndex() + 1
		
		xNewTag = xml_man.newElement( xParentTag,
									  oldTagInTree.getTag().tag,
									  oldTagInTree.getTag().text,
									  oldTagInTree.getTag().attrib,
									  xOrder)
		
		xID = getIDForTreeView( xNewTag.tag, GL.dicTagsInTree)
		
		newTagInTree = TIG.TagInTree(xBaseID, xID, xNewTag, xParentTag, GL.appTreeView, order = xOrder)
		GL.dicTagsInTree[xID] = newTagInTree
		
		def getTagInTreeFromTag(xTag, dicTagsInTree):
			xReturn = None
			for xTuple in dicTagsInTree.items():
				#xTuple = (key, value)
				if xTuple[1].getTag() == xTag:
					xReturn = xTuple[1]
					break
			return xReturn
			
		for xChildTag in oldTagInTree.getTag():
			xChildTagInTree = getTagInTreeFromTag(xChildTag, GL.dicTagsInTree)
			copyTagInTree( xChildTagInTree, xLevel + 1, newparent = newTagInTree)
			
	else:
		print 'oldTagInTree is None'
		
		
def deleteTagInTree(xID):
	xTagInTree = GL.dicTagsInTree[xID]
	xTagInTree.parent_tag.remove( xTagInTree.getTag() )
	GL.appTreeView.delete( xTagInTree.id )
	del GL.dicTagsInTree[xID]
	del xTagInTree
	print 'Deleted %s' % xID
	

def refreshApp(mainApp):
	#mainApp = event.widget
	
	#reload buttons
	for i in range(0,50):	#habría que ver si se puede hacer esto más eficiente
		try:
			mainApp.menubar.delete(i)
		except:
			break
	fillMenu(mainApp)
	
	mainApp.frames.menu.clean()
	fillButtonBarFrame(mainApp.frames.menu, mainApp.excludeList)
	
	mainApp.frames.footer.clean()
	fillFooterFrame(mainApp.frames.footer)
	
	mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
	
	#reload treeview
	#band_treeview.clean()
	#band_buttons.clean()
	mainApp.frames.treeview.clean()
	mainApp.frames.buttons.clean()
	
	GL.dicTagsInTree = {}
	GL.appTreeView = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons, GL.dicTagsInTree)
	
	root = GL.XMLTree.getroot()
	
	GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
	addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
	mainApp.update()
	
	GL.appTreeView.see(GL.lastTreeViewFocus)
	GL.appTreeView.focus(GL.lastTreeViewFocus)
	GL.appTreeView.selection_set(GL.lastTreeViewFocus)
	
		
def checkTreeView():
	if GL.appTreeView == None:
		print 'TreeView does not exist'
	else:
		print 'TreeView is A-OK!'

		
def bCheckEntries(band_buttons):
	for widget in band_buttons.winfo_children():
		if isinstance(widget, Entry):
			print widget.get()

def bPrintDicSubnames():
	print GL.dicTagSubnames
	
def bPrintEncoding():
	print GL.XML_encoding
	
	
# MENU METHODS

def mChangeLang(mainApp, newLang):
	print 'changing language'
	if newLang == 'ENG':
		dicLang = LANG.english
	elif newLang == 'SPA':
		dicLang = LANG.spanish
	else:
		return
	
	if dicLang['lang'] <> GL.names['lang']:
		GL.names = dicLang
		refreshApp(mainApp)
		
			
#####################

if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

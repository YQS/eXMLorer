# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import globals as GL
import TagInTree as TIG
import xml_man


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

class BandPack(object):
	def __init__(self):
		self.menu = None
		self.treeview = None
		self.buttons = None

class MainApp(Tk):
	def __init__(self, iconfile='test.gif', lExcludeMenu = []): #añadir opciones de generar botonos y bandas a eleccion
		Tk.__init__(self)
		self.title('eXMLorer')
		self.iconImage = PhotoImage(file= iconfile)
		self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
		
		#elementos del main
		self.frames = BandPack()
		
		self.frames.menu = FrameExt(self)
		self.frames.menu.pack(side=TOP, fill=X)
		fillMenuFrame(self.frames.menu, lExcludeMenu)
		
		self.frames.treeview = FrameExt(self)
		self.frames.treeview.pack(side=LEFT, fill=BOTH)
		
		self.frames.buttons = FrameExt(self)
		self.frames.buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
		
		self.bind('<F5>', lambda event: refreshTreeView(event, self.frames.treeview, self.frames.buttons))

		
# METHODS
		
def fillMenuFrame(xFrame, lExcludeMenu):
	mainApp = xFrame.master

	if not 'label_filename' in lExcludeMenu:
		label_filename = xFrame.addWidget('Label', 'label_filename')
		label_filename.configure(padding=(10,0,0,0))
		label_filename.grid(column=3, row=0)
	
	if not 'button_open' in lExcludeMenu:
		button_open = xFrame.addWidget('Button', 'button_open')
		button_open.configure(text = 'Abrir', 
							 #image = ico_open,
							 width= GL.buttonWidth, 
							 command = lambda: openXML(mainApp.frames.treeview, mainApp.frames.buttons, xFrame.dic['label_filename'] ))
		button_open.grid(column=0, row=0)
		
	if not 'button_save' in lExcludeMenu:
		button_save = xFrame.addWidget('Button', 'button_save')
		button_save.configure(text= 'Guardar', width= GL.buttonWidth, command= lambda: saveXML(mainApp, 'SAVE'))
		button_save.grid(column=1, row=0)
	
	if not 'button_saveAs' in lExcludeMenu:
		button_saveAs = xFrame.addWidget('Button', 'button_saveAs')
		button_saveAs.configure(text= 'Guardar como...', width= GL.buttonWidth, command= lambda: saveXML(mainApp, 'SAVEAS'))
		button_saveAs.grid(column=2, row=0)
	
	if not 'button_copyTag' in lExcludeMenu:
		button_copyTag = xFrame.addWidget('Button', 'button_copyTag')
		button_copyTag.configure(text='Copiar tag', 
								width= GL.buttonWidth, 
								command= lambda: copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
		button_copyTag.grid(column=0, row=1)
		
	if not 'button_deleteTag' in lExcludeMenu:
		button_deleteTag = xFrame.addWidget('Button', 'button_deleteTag')
		button_deleteTag.configure(text='Borrar tag',
								   width= GL.buttonWidth, 
								   command= lambda: deleteTagInTree( GL.appTreeView.focus() ))
		button_deleteTag.grid(column=1, row=1)
		
		
	## debug buttons
	if not 'button_glTreeView' in lExcludeMenu:
		button_glTreeView = xFrame.addWidget('Button', 'button_glTreeView')
		button_glTreeView.configure(text='Check TreeView',
									width= GL.buttonWidth,
									command= lambda: checkTreeView())
		button_glTreeView.grid(column=1, row=1)
	
	if not 'button_analyze' in lExcludeMenu:
		button_analyze = xFrame.addWidget('Button', 'button_analyze')
		button_analyze.configure(text= 'Print band_buttons', width= GL.buttonWidth, command= lambda: bCheckEntries(mainApp.frames.buttons))
		button_analyze.grid(column=0, row=1)
		
	if not 'button_dicSubnames' in lExcludeMenu:
		button_dicSubnames = xFrame.addWidget('Button', 'button_dicSubnames')
		button_dicSubnames.configure(text= 'Print dicSubnames', width= GL.buttonWidth, command= lambda: bPrintDicSubnames() )
		button_dicSubnames.grid(column=2, row=1)
		
	if not 'button_getDicSubnames' in lExcludeMenu:
		button_getDicSubnames = xFrame.addWidget('Button', 'button_dicSubnames')
		button_getDicSubnames.configure(text= 'getDicSubnames', width= GL.buttonWidth, command= lambda: GL.getDicSubnames() )
		button_getDicSubnames.grid(column=3, row=1)
		
def cleanFrame(frame):
	for widget in frame.winfo_children():
		widget.destroy()

def getFilename():
	filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')])
	print filename
	return filename
	
def getTreeView(mainApp, band_buttons, dicTagsInTree):
	appTreeView = Treeview(mainApp, columns=('data','name', 'size')) #, height=20
	appTreeView.pack(side="left",fill=BOTH)
	
	scroll_treeview = Scrollbar(mainApp,command=appTreeView.yview)
	appTreeView.configure(yscrollcommand=scroll_treeview.set)
	scroll_treeview.pack(side="right",fill="y")
	
	appTreeView.column('data', width=500, anchor='w')
	appTreeView.column('name', width=200, anchor='e')
	appTreeView.column('size', width=200, anchor='e')
	appTreeView.heading('data', text='Data')
	appTreeView.heading('name', text='Nombre')
	appTreeView.heading('size', text='Tamanio')
	
	#indico que solo muestre la columna 'data'
	appTreeView.configure(displaycolumns=('data'))
	
	
	def fillBandButtons(event, band_buttons, dicTagsInTree):
		cleanFrame(band_buttons)
		appTreeView = event.widget
		
		def updateTreeNode(value, oTagInTree):
			#print entry.get()
			print value
			oTagInTree.getTag().text = value
			oTagInTree.setColumn( 'data', value)
			return True
			
		def copyTextBoxToClipboard(text, appTreeView):
			pass
			
		def selectAllText(event):
			xTextbox = event.widget
			print 'selectAllText'
			xTextbox.tag_add(SEL, "1.0", END)
			xTextbox.mark_set(INSERT, "1.0")
			xTextbox.see(INSERT)
			return 'break'		#porque si no, el tkinter lee el siguiente evento
			
			
		
		#######
		def getEntry(value, band_buttons, xRow, oTagInTree):
			xBoolOptions = ('True', 'False')
			xButtonWidth = 50
			if value in xBoolOptions:
				'''
				print 'OptionMenu'
				xStringVar = StringVar()
				xStringVar.set(value)
				OptionMenu(band_buttons, xStringVar, 'True', 'False').grid(column=1, row=xRow)
				'''
				print 'Combobox'
				xCombobox = Combobox(band_buttons, values=xBoolOptions, width=(xButtonWidth - 3), validate='focus')
				xCombobox.configure(validatecommand = lambda xCombobox=xCombobox, oTagInTree=oTagInTree: updateTreeNode(xCombobox.get(), oTagInTree) )
				xCombobox.grid(column=1, row=xRow)
				xCombobox.set(value)
			elif value == '':
				print 'disEntry'
				xEntry = Entry(band_buttons, validate='focus')
				xEntry.configure(validatecommand = lambda xEntry=xEntry, oTagInTree=oTagInTree: updateTreeNode(xEntry.get(), oTagInTree))
				xEntry.grid(column=1, row=xRow, sticky= 'w')
				if oTagInTree.hasChild():
					xEntry.insert(0, '<...>')
					xEntry.config(width=xButtonWidth)
				else:
					xEntry.insert(0,'<\>')
					xEntry.config(width=xButtonWidth - 15)
					
					
				xEntry.configure(state=DISABLED)
				#xEntry.insert(0, value)
			else:
				if len(value) < (xButtonWidth + GL.marginToExtendToText):
					print 'Entry'
					xEntry = Entry(band_buttons, width=xButtonWidth, validate='focus')
					xEntry.configure(validatecommand = lambda xEntry=xEntry, oTagInTree=oTagInTree: updateTreeNode(xEntry.get(), oTagInTree))
					xEntry.bind('<Return>', lambda event, xEntry=xEntry, oTagInTree=oTagInTree:updateTreeNode(xEntry.get(), oTagInTree))
					xEntry.grid(column=1, row=xRow)
					xEntry.insert(0, value)
				else:
					def tbMade(widget,text):
						widget.focus_set()
						print text
				
					print 'Textbox'
					xHeight = 10 #len(value) % xButtonWidth
					xTextbox = Text(band_buttons, width=xButtonWidth-7, height=xHeight)
					xTextbox.bind('<KeyRelease>', lambda event: updateTreeNode(event.widget.get('1.0', 'end'), oTagInTree ))
					xTextbox.bind('<Control-Key-a>', lambda event: selectAllText(event) )
					xTextbox.bind('<Control-Key-A>', lambda event: selectAllText(event) )
					xTextbox.grid(column=1, row=xRow)
					xTextbox.insert('1.0', value)
					
					
		
		def getLabel(name, band_buttons, xRow):
			Label(band_buttons, text=name).grid(column=0, row=xRow, sticky='wn')
			
		def getButtonRow(id, band_buttons, xRow):
			getLabel(dicTagsInTree[id].tagname, band_buttons, xRow)
			try:
				value = dicTagsInTree[id].getTag().text.strip()
			except:
				value = ''
			getEntry(value, band_buttons, xRow, dicTagsInTree[id])
		#######
		
		xIDFocus = appTreeView.focus()
		print 'focus in ' + xIDFocus 
		print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
		
		xRow = 0
		xStringVar = StringVar()
		xGotItems = False
		
		for xIDChild in appTreeView.get_children(xIDFocus):
			xGotItems = True
			getButtonRow(xIDChild, band_buttons, xRow)
			xRow += 1
		
		if not xGotItems:
			getButtonRow(xIDFocus, band_buttons, xRow)
			
		
	#appTreeView.bind('<1>', lambda event, band_buttons = band_buttons, appTreeView = appTreeView, xFocus=appTreeView.focus(): getLabel(event, band_buttons, appTreeView, xFocus))
	appTreeView.bind('<<TreeviewSelect>>', lambda event, 
												  band_buttons = band_buttons,
												  dicTagsInTree = dicTagsInTree:
												  fillBandButtons(event, band_buttons, dicTagsInTree))
	
	return appTreeView
	
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
	cleanFrame(band_treeview)
	cleanFrame(band_buttons)
	
	GL.filename = getFilename()
	root = xml_man.getXML(GL.filename)
	#root = xml_man.getXML('stylers.xml')
	
	label_filename.config(text= GL.filename)
	
	GL.dicTagsInTree = {}
	GL.appTreeView = getTreeView(band_treeview, band_buttons, GL.dicTagsInTree)
	
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
		print 'saving in ' + save_filename
		GL.XMLTree.write(save_filename)
		GL.filename = save_filename

		
def copyTagInTree(oldTagInTree, xLevel, newparent = None):
	if oldTagInTree <> None:
		if newparent == None:
			xBaseID = oldTagInTree.parent_id
			xParentTag = oldTagInTree.parent_tag
		else:
			xBaseID = newparent.id
			xParentTag = newparent.getTag()
		
		xOrder = oldTagInTree.parent_tag.getchildren().index( oldTagInTree.getTag() )
		xOrder += 1
		
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
	
def refreshTreeView(event, band_treeview, band_buttons):
	mainApp = event.widget
	cleanFrame(band_treeview)
	cleanFrame(band_buttons)
	
	GL.dicTagsInTree = {}
	GL.appTreeView = getTreeView(band_treeview, band_buttons, GL.dicTagsInTree)
	
	root = GL.XMLTree.getroot()
	
	GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
	addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
	mainApp.update()	
	
		
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
			
#####################

if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
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
	def __init__(self, iconfile='test.gif', lExcludeMenu = []):
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
	
	getButton(xFrame, 'button_open', 'Abrir', lExcludeMenu, 0, 0, command = lambda: openXML(mainApp.frames.treeview, mainApp.frames.buttons, xFrame.dic['label_filename'] ))
	getButton(xFrame, 'button_save', 'Guardar', lExcludeMenu, 0, 1, command = lambda: saveXML(mainApp, 'SAVE'))
	getButton(xFrame, 'button_saveAs', 'Guardar como...', lExcludeMenu, 0, 2, command = lambda: saveXML(mainApp, 'SAVEAS'))
	getButton(xFrame, 'button_copyTag', 'Copiar tag', lExcludeMenu, 1, 0, command = lambda: copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
	getButton(xFrame, 'button_deleteTag', 'Borrar tag', lExcludeMenu, 1, 1, command = lambda: deleteTagInTree( GL.appTreeView.focus() ))		
		
	## debug buttons
	getButton(xFrame, 'button_glTreeView', 'Check TreeView', lExcludeMenu, 1, 1, command = lambda: checkTreeView())
	getButton(xFrame, 'button_analyze', 'Print band_buttons', lExcludeMenu, 0, 1, command = lambda: bCheckEntries(mainApp.frames.buttons))
	getButton(xFrame, 'button_dicSubnames', 'Print dicSubnames', lExcludeMenu, 1, 3, command = lambda: bPrintDicSubnames())

	getButton(xFrame, 'button_getDicSubnames', 'Consigue Subnames', lExcludeMenu, 1, 3, command = lambda: GL.getDicSubnames())
		
def getButton(xMaster, name, caption, lExcludeMenu, xRow, xColumn, command=''):
	if not name in lExcludeMenu:
		xButton = xMaster.addWidget('Button', name)
		xButton.configure(text= caption, width= GL.buttonWidth, command=command)
		xButton.grid(column=xColumn, row=xRow)
		
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
		print 'EventType %s' % event.type
		appTreeView = GL.appTreeView
		
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
		
		def getTextEntry(band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value):
			xEntry = Entry(band_buttons, width=xButtonWidth, validate='focus')
			xEntry.configure(validatecommand = lambda xEntry=xEntry, oTagInTree=oTagInTree: updateTreeNode(xEntry.get(), oTagInTree))
			xEntry.bind('<Return>', lambda event, xEntry=xEntry, oTagInTree=oTagInTree:updateTreeNode(xEntry.get(), oTagInTree))
			xEntry.grid(column=1, row=xRow)
			xEntry.insert(0, value)
			
		def activateTextEntry(xEntry, xButton, band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value):
			xEntry.destroy()
			xButton.destroy()
			getTextEntry(band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value)
			
		
		#######
		def getEntry(value, band_buttons, xRow, oTagInTree):
			xBoolOptions = ('True', 'False')
			#xButtonWidth = 50
			xButtonWidth = GL.labelButtonWidth
			xExtraButtonWidth = GL.labelExtraButtonWidth
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
					xEntry.config(width=xButtonWidth - xExtraButtonWidth)
					xButton = Button(band_buttons, text='Abrir', width= xExtraButtonWidth)
					xButton.grid(column=1, row=xRow, sticky='e')
					xButton.config(command= lambda xEntry=xEntry,
												   xButton=xButton,
												   xColumn=xEntry.grid_info()['column']:
												   activateTextEntry(xEntry, xButton, band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value))
					#print xButton.grid_info()['column']
					
				xEntry.configure(state=DISABLED)
				#xEntry.insert(0, value)
			else:
				if len(value) < (xButtonWidth + GL.marginToExtendToText):
					print 'Entry'
					getTextEntry(band_buttons, xButtonWidth, 1, xRow, oTagInTree, value)
				else:
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
		GL.lastTreeViewFocus = xIDFocus
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
			
		
	appTreeView.bind('<<TreeviewSelect>>', lambda event: fillBandButtons(event, band_buttons, dicTagsInTree))
	
	def setAsParentSubname(parentTIG, childTIG):
		GL.dicTagSubnames.updateDic( parentTIG.getTag().tag, childTIG.getTag().tag )
		parentTIG.updateSubname( childTIG.getTag().text)
		GL.dicTagSubnames.save()
		
	def cleanSubname(oTIG):
		GL.dicTagSubnames.updateDic( oTIG.getTag().tag, '')
		oTIG.updateSubname('')
		GL.dicTagSubnames.deleteFromDic(oTIG.getTag().tag)
		GL.dicTagSubnames.save()
	
	def contextMenu(event, band_buttons, dicTagsInTree):
		print 'context menu'
		xFocusIDContextMenu = GL.appTreeView.identify_row(event.y)
		print 'identify row shows %s' % xFocusIDContextMenu
		GL.appTreeView.focus(xFocusIDContextMenu)
		
		# getting variables for commands
		focusTIG = dicTagsInTree[xFocusIDContextMenu]
		
		parentTIG = focusTIG.getParent()
		subnameCmdState = ACTIVE
		if parentTIG == None:
			subnameCmdState = DISABLED
		
		cleanCmdState = DISABLED
		if focusTIG.hasChild():
			cleanCmdState = ACTIVE
		
		#menu
		menu = Menu(GL.appTreeView, tearoff=0)
		menu.add_command(label='Seleccionar como Subnombre del Parent', 
						 state= subnameCmdState, 
						 command= lambda
								  parentTIG = parentTIG, 
								  focusTIG = focusTIG: 
								  setAsParentSubname(parentTIG, focusTIG)
						)
		menu.add_command(label='Limpiar definición de Subnombre', 
						 state= cleanCmdState, 
						 command= lambda 
								  focusTIG = focusTIG: 
								  cleanSubname(focusTIG) 
						)
						
		print 'identify row shows %s' % appTreeView.identify_row(event.y)
		menu.post(event.x_root, event.y_root)		
		
	appTreeView.bind('<Button-3>', lambda event: 
										  contextMenu(event, band_buttons, dicTagsInTree))
	
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
	label_filename.config(text= GL.filename)
	
	root = xml_man.getXML(GL.filename)
	#root = xml_man.getXML('stylers.xml')
	
	if root == None:
		tkMessageBox.showerror('eXMLorer', 'El archivo %s no es un archivo XML valido' % GL.filename)
	else:	
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
			
#####################

if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

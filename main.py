# encoding: UTF-8

import xml.etree.ElementTree as ET
from Tkinter import *
from ttk import *
import tkFileDialog
import globals as GL
import TagInTree as TIG
import tk_app

################
def getFilename():
	filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')])
	print filename
	return filename

def cleanFrame(frame):
	for widget in frame.winfo_children():
		widget.destroy()

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
				xEntry = Entry(band_buttons, width=xButtonWidth)
				xEntry.grid(column=1, row=xRow)
				if oTagInTree.hasChild():
					xEntry.insert(0, '<...>')
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
	

def deleteTagInTree(xID):
	xTagInTree = GL.dicTagsInTree[xID]
	xTagInTree.parent_tag.remove( xTagInTree.getTag() )
	GL.appTreeView.delete( xTagInTree.id )
	del GL.dicTagsInTree[xID]
	del xTagInTree
	print 'Deleted %s' % xID
	
	
	
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
		
		#xNewTag = ET.SubElement(xParentTag, oldTagInTree.getTag().tag, oldTagInTree.getTag().attrib)
		xNewTag = ET.Element( oldTagInTree.getTag().tag, oldTagInTree.getTag().attrib)
		xParentTag.insert( xOrder, xNewTag)
		xNewTag.text = oldTagInTree.getTag().text
		
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
	

def openXML(band_treeview, band_buttons, label_filename):
	cleanFrame(band_treeview)
	cleanFrame(band_buttons)
	
	GL.filename = getFilename()
	root = getXML(GL.filename)
	#root = getXML('stylers.xml')
	
	label_filename.config(text= GL.filename)
	
	GL.dicTagsInTree = {}
	GL.appTreeView = getTreeView(band_treeview, band_buttons, GL.dicTagsInTree)
	
	GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
	addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
	
def bCheckEntries(band_buttons):
	for widget in band_buttons.winfo_children():
		if isinstance(widget, Entry):
			print widget.get()
	
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
	
	
def main(mode = 'main'):
	if mode == 'main':
		mainApp = Tk()
		mainApp.title('eXMLorer')
		#img = PhotoImage(file='test.gif')
		#mainApp.tk.call('wm', 'iconphoto', mainApp._w, img)
		ico_mainApp = PhotoImage(file='test.gif')
		mainApp.tk.call('wm', 'iconphoto', mainApp._w, ico_mainApp)
		
		mainApp.update()		#hace que el getFilename no deje abierta una ventana
		
		band_menu = Frame(mainApp)
		band_menu.pack(side=TOP, fill=X)
		
		band_treeview = Frame(mainApp)
		band_treeview.pack(side=LEFT, fill=BOTH)
		
		band_buttons = Frame(mainApp)
		band_buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
		
		label_filename = Label(band_menu, padding=(10,0,0,0))
		label_filename.grid(column=3, row=0)
		
		openXML(band_treeview, band_buttons, label_filename)
		
		#ico_open = PhotoImage(file='OPEN2.gif').subsample(2,2)
		button_open = Button(band_menu, 
							 text = 'Abrir', 
							 #image = ico_open,
							 width=GL.buttonWidth, 
							 command = lambda band_treeview=band_treeview, 
											  band_buttons=band_buttons,
											  label_filename=label_filename: 
											  openXML(band_treeview, band_buttons, label_filename))
		button_open.grid(column=0, row=0)
		
		button_save = Button(band_menu, text= 'Guardar', width= GL.buttonWidth, command= lambda mainApp=mainApp: saveXML(mainApp, 'SAVE'))
		button_save.grid(column=1, row=0)
		
		button_saveAs = Button(band_menu, text= 'Guardar como...', width= GL.buttonWidth, command= lambda mainApp=mainApp: saveXML(mainApp, 'SAVEAS'))
		button_saveAs.grid(column=2, row=0)
		
		button_copyTag = Button(band_menu, 
								text='Copiar tag', 
								width= GL.buttonWidth, 
								command= lambda: copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
		button_copyTag.grid(column=0, row=1)
		
		#button_analyze = Button(band_menu, text= 'Print band_buttons', width= GL.buttonWidth, command= lambda band_buttons = band_buttons: bCheckEntries(band_buttons))
		#button_analyze.grid(column=0, row=1)
		
		mainApp.bind('<F5>', lambda event, band_treeview=band_treeview, band_buttons=band_buttons: refreshTreeView(event, band_treeview, band_buttons))
		
	else:
	
		mainApp = tk_app.MainApp(dicExcludeMenu = ['button_analyze', 'button_glTreeView'])
		openXML(mainApp.frames.treeview, mainApp.frames.buttons, mainApp.frames.menu.dic['label_filename'])
		
		
	mainApp.focus_set()
	mainApp.mainloop()
		
		
	try:
		mainApp.destroy()
	except:
		pass

if __name__ == '__main__':
	main('test')

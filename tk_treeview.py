# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox
import globals as GL
import xml_man

def getTreeView(mainApp, band_buttons, dicTagsInTree):
	appTreeView = Treeview(mainApp, columns=('data','name', 'size'))
	appTreeView.pack(side="left",fill=BOTH)
	
	setScrollbar(mainApp, appTreeView)
	#scroll_treeview = Scrollbar(mainApp,command=appTreeView.yview)
	#appTreeView.configure(yscrollcommand=scroll_treeview.set)
	#scroll_treeview.pack(side="right",fill="y")
	
	appTreeView.column('data', width=500, anchor='w')
	appTreeView.column('name', width=200, anchor='e')
	appTreeView.column('size', width=200, anchor='e')
	appTreeView.heading('data', text= GL.names['column-data'])
	appTreeView.heading('name', text= GL.names['column-name'])
	appTreeView.heading('size', text= GL.names['column-size'])
	
	#indico que solo muestre la columna 'data'
	appTreeView.configure(displaycolumns=('data'))
			
	#events
	#appTreeView.bind('<Double-Button-2>', lambda event: editTag(event.widget.master.master.master, dicTagsInTree[GL.appTreeView.identify_row(event.y)])) #la ruta larga es para llegar bien al mainApp
	appTreeView.bind('<<TreeviewSelect>>', lambda event: fillBandButtons(event.widget, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Button-3>', lambda event: contextMenu(event, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Shift-Up>', lambda event: moveNodeBind(event, dicTagsInTree))
	appTreeView.bind('<Shift-Down>', lambda event: moveNodeBind(event, dicTagsInTree))
	
	return appTreeView
	
	
def setScrollbar(parent, widget):
	xScroll = Scrollbar(parent, orient=VERTICAL, command= widget.yview)
	widget.configure(yscrollcommand= xScroll.set)
	xScroll.pack(side='right',fill='y')
	
	
	
def fillBandButtons(appTreeView, band_buttons, dicTagsInTree):
	band_buttons.clean()
	
	#canvas para manejar una scrollbar
	#NO FUNCIONA
	canvas = Canvas(band_buttons, borderwidth=0, highlightthickness=0)
	canvas.pack(side=LEFT, fill=BOTH, expand=True)
	
	#subframe=Frame(canvas)
	#setScrollbar(band_buttons, canvas)
	
	#canvas.create_window((0,0),window=subframe,anchor='nw')
	#subframe.bind("<Configure>",lambda : canvas.configure(scrollregion=canvas.bbox("all")))
	
	
	#print 'EventType %s' % event.type
	#appTreeView = GL.appTreeView
	#appTreeView = event.widget
	
	xIDFocus = appTreeView.focus()
	GL.lastTreeViewFocus = xIDFocus
	print 'focus in ' + xIDFocus 
	print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
	
	xRow = 0
	xStringVar = StringVar()
	xGotItems = False
	
	for xIDChild in appTreeView.get_children(xIDFocus):
		xGotItems = True
		#getButtonRow(dicTagsInTree[xIDChild], band_buttons, xRow)
		getButtonRow(dicTagsInTree[xIDChild], canvas, xRow)
		xRow += 1
	
	if not xGotItems:
		#getButtonRow(dicTagsInTree[xIDFocus], band_buttons, xRow)
		getButtonRow(dicTagsInTree[xIDFocus], canvas, xRow)

		
def getButtonRow(oTagInTree, band_buttons, xRow):
	getLabel(oTagInTree.tagname, band_buttons, xRow)
	try:
		value = oTagInTree.getTag().text.strip()
	except:
		value = ''
	getEntry(value, band_buttons, xRow, oTagInTree)
	
def getLabel(name, band_buttons, xRow):
	Label(band_buttons, text=name).grid(column=0, row=xRow, sticky='wn')
	
def getEntry(value, band_buttons, xRow, oTagInTree):
	xBoolOptions = ('True', 'False')
	xButtonWidth = GL.labelButtonWidth
	xExtraButtonWidth = GL.labelExtraButtonWidth
	xMarginToExtendToText = GL.marginToExtendToText
	
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
		xCombobox.grid(column=1, row=xRow, sticky='wn')
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
			xButton = Button(band_buttons, text=GL.names['button_open'], width= xExtraButtonWidth)
			xButton.grid(column=1, row=xRow, sticky='e')
			xButton.config(command= lambda xEntry=xEntry,
										   xButton=xButton,
										   xColumn=xEntry.grid_info()['column']:
										   activateTextEntry(xEntry, xButton, band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value))
			
		xEntry.configure(state=DISABLED)
	else:
		if len(value) < (xButtonWidth + xMarginToExtendToText):
			print 'Entry'
			getTextEntry(band_buttons, xButtonWidth, 1, xRow, oTagInTree, value)
		else:
			print 'Entry to Text'
			xEntry = getTextEntry(band_buttons, xButtonWidth-xExtraButtonWidth, 1, xRow, oTagInTree, value)
			xButton = Button(band_buttons, text='...', width= xExtraButtonWidth)
			xButton.grid(column=1, row=xRow, sticky='e')
			xButton.config(command= lambda: openTextWindow(band_buttons.master.master.master, oTagInTree, xEntry))

			
def getTextEntry(band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value):
	xEntry = Entry(band_buttons, width=xButtonWidth, validate='focus')
	xEntry.configure(validatecommand = lambda xEntry=xEntry, oTagInTree=oTagInTree: updateTreeNode(xEntry.get(), oTagInTree))
	xEntry.bind('<Return>', lambda event, xEntry=xEntry, oTagInTree=oTagInTree:updateTreeNode(xEntry.get(), oTagInTree))
	xEntry.bind('<Control-Key-a>', lambda event: selectAllText(event) )
	xEntry.bind('<Control-Key-A>', lambda event: selectAllText(event) )
	xEntry.grid(column=1, row=xRow, sticky='wn')
	xEntry.insert(0, value)
	return xEntry
	
def activateTextEntry(xEntry, xButton, band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value):
	xEntry.destroy()
	xButton.destroy()
	getTextEntry(band_buttons, xButtonWidth, xColumn, xRow, oTagInTree, value)
	
def selectAllText(event):
	xTextbox = event.widget
	print 'selectAllText'
	xTextbox.tag_add(SEL, "1.0", END)
	xTextbox.mark_set(INSERT, "1.0")
	xTextbox.see(INSERT)
	return 'break'		#porque si no, el tkinter lee el siguiente evento
	
def openTextWindow(mainApp, oTagInTree, entry):
	container = {}
	label = GL.names['message_value']
	title = GL.names['message_editing'] + ' ' + oTagInTree.tagname
	xWindow = mainApp.getToplevel2(title, container)
	xWindow.textFieldConstructor(label, entry.get())
	xWindow.show()
	
	if len(container) > 0:
		print 'updating ' + oTagInTree.tagname
		updateTreeNode(container[label], oTagInTree)
		#actualizo tambien el entry asociado
		entry.delete(0, END)
		entry.insert(0, container[label])
		
	
def updateTreeNode(value, oTagInTree):
		#print entry.get()
		print value
		oTagInTree.getTag().text = value
		oTagInTree.setColumn( 'data', value)
		return True
		

def moveNodeBind(event, dicTagsInTree):
		if event.keycode == 38:		#Up
			xDirection = -1
		elif event.keycode == 40:	#Down
			xDirection = 1
			
		appTreeView = event.widget
		xIDFocus = appTreeView.focus()
		xIDParent = dicTagsInTree[xIDFocus].getParent().id
		xPosition = dicTagsInTree[xIDFocus].getTreeViewIndex() + xDirection
		moveNode( xIDFocus, xIDParent, xPosition, dicTagsInTree)
		#appTreeView.move( xIDFocus, xIDParent, xPosition)
		#xml_man.moveTag( dicTagsInTree[xIDParent].getTag(), dicTagsInTree[xIDFocus].getTag(), xPosition)
		
		return 'break'
		
def moveNode(xIDFocus, xIDParent, xPosition, dicTagsInTree):
	GL.appTreeView.move( xIDFocus, xIDParent, xPosition)
	
	if xPosition == 'end':
		xPosition = dicTagsInTree[xIDFocus].getNumberOfSiblings()
	
	xml_man.moveTag( dicTagsInTree[xIDParent].getTag(), dicTagsInTree[xIDFocus].getTag(), xPosition)

def contextMenu(event, band_buttons, dicTagsInTree):
	print 'context menu'
	
	#la ruta es evento.TreeView.BandaTreeView.BandaCenter.mainApp
	mainApp = event.widget.master.master.master
	
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
	
	menu.add_command(label=GL.names['submenu_edittag'], state=ACTIVE, command= lambda:editTag(mainApp, focusTIG))
	menu.add_separator()
	
	menu.add_command(label= GL.names['submenu_selectParentSubname'], 
					 state= subnameCmdState, 
					 command= lambda
							  parentTIG = parentTIG, 
							  focusTIG = focusTIG: 
							  setAsParentSubname(parentTIG, focusTIG)
					)
	menu.add_command(label= GL.names['submenu_cleanParentSubname'], 
					 state= cleanCmdState, 
					 command= lambda 
							  focusTIG = focusTIG: 
							  cleanSubname(focusTIG) 
					)
	
					
	print 'identify row shows %s' % GL.appTreeView.identify_row(event.y)
	menu.post(event.x_root, event.y_root)
	
def setAsParentSubname(parentTIG, childTIG):
	GL.dicTagSubnames.updateDic( parentTIG.getTag().tag, childTIG.getTag().tag )
	parentTIG.updateSubname( childTIG.getTag().text)
	
def cleanSubname(oTIG):
	GL.dicTagSubnames.updateDic( oTIG.getTag().tag, '')
	oTIG.updateSubname('')
	GL.dicTagSubnames.deleteFromDic(oTIG.getTag().tag)

def editTag(mainApp, oTIG):
	container = {'Tag': oTIG.getTag().tag, 'Value':oTIG.getTag().text}
	xWindow = mainApp.getToplevel2(GL.names['message_edittag'], container)
	xWindow.formConstructor('Tag', 0)
	xWindow.formConstructor('Value', 1)
	xWindow.show()
	
	if len(container) > 0:
		oTIG.updateTag(container['Tag'], container['Value'])
		updateTreeNode(container['Value'], oTIG)
		oTIG.parent_treeview.item(oTIG.id, text=oTIG.getTagName())
		
		fillBandButtons(GL.appTreeView, mainApp.frames.buttons, GL.dicTagsInTree)

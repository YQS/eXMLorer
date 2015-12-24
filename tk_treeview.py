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
	appTreeView.heading('data', text='Data')
	appTreeView.heading('name', text='Nombre')
	appTreeView.heading('size', text='Tamanio')
	
	#indico que solo muestre la columna 'data'
	appTreeView.configure(displaycolumns=('data'))
			
	#events
	appTreeView.bind('<<TreeviewSelect>>', lambda event: fillBandButtons(event, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Button-3>', lambda event: contextMenu(event, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Shift-Up>', lambda event: moveNodeBind(event, dicTagsInTree))
	appTreeView.bind('<Shift-Down>', lambda event: moveNodeBind(event, dicTagsInTree))
	
	return appTreeView
	
	
def setScrollbar(parent, widget):
	xScroll = Scrollbar(parent, command= widget.yview)
	widget.configure(yscrollcommand= xScroll.set)
	xScroll.pack(side='right',fill='y')
	
def fillBandButtons(event, band_buttons, dicTagsInTree):
	band_buttons.clean()
	print 'EventType %s' % event.type
	#appTreeView = GL.appTreeView
	appTreeView = event.widget
	
	xIDFocus = appTreeView.focus()
	GL.lastTreeViewFocus = xIDFocus
	print 'focus in ' + xIDFocus 
	print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
	
	xRow = 0
	xStringVar = StringVar()
	xGotItems = False
	
	for xIDChild in appTreeView.get_children(xIDFocus):
		xGotItems = True
		getButtonRow(dicTagsInTree[xIDChild], band_buttons, xRow)
		xRow += 1
	
	if not xGotItems:
		getButtonRow(dicTagsInTree[xIDFocus], band_buttons, xRow)

		
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
			
		xEntry.configure(state=DISABLED)
	else:
		if len(value) < (xButtonWidth + xMarginToExtendToText):
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
	
def selectAllText(event):
	xTextbox = event.widget
	print 'selectAllText'
	xTextbox.tag_add(SEL, "1.0", END)
	xTextbox.mark_set(INSERT, "1.0")
	xTextbox.see(INSERT)
	return 'break'		#porque si no, el tkinter lee el siguiente evento
	

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
					
	print 'identify row shows %s' % GL.appTreeView.identify_row(event.y)
	menu.post(event.x_root, event.y_root)
	
def setAsParentSubname(parentTIG, childTIG):
	GL.dicTagSubnames.updateDic( parentTIG.getTag().tag, childTIG.getTag().tag )
	parentTIG.updateSubname( childTIG.getTag().text)
	GL.dicTagSubnames.save()
	
def cleanSubname(oTIG):
	GL.dicTagSubnames.updateDic( oTIG.getTag().tag, '')
	oTIG.updateSubname('')
	GL.dicTagSubnames.deleteFromDic(oTIG.getTag().tag)
	GL.dicTagSubnames.save()

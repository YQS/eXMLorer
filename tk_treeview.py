# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox
import globals as GL
import xml_man
import tk_app
import SSF
import module_interface as MOD

def getTreeView(treeview_frame, band_buttons, dicTagsInTree):
	appTreeView = Treeview(treeview_frame, columns=('data','subname',))
	appTreeView.pack(side="left",fill=BOTH)
	
	setScrollbar(treeview_frame, appTreeView)
	
	mainApp = treeview_frame.master.master
	
	appTreeView.column('subname', width=120, anchor='w', stretch=True)
	appTreeView.column('data', width=480, anchor='w', stretch=True)
	appTreeView.heading('subname', text= GL.names['column-subname'])
	appTreeView.heading('data', text= GL.names['column-data'])
	
	#indico las columnas a mostrar
	appTreeView.configure(displaycolumns=('subname', 'data'))
			
	#events
	#appTreeView.bind('<Double-Button-2>', lambda event: editTag(event.widget.master.master.master, dicTagsInTree[GL.appTreeView.identify_row(event.y)])) #la ruta larga es para llegar bien al mainApp
	appTreeView.bind('<<TreeviewSelect>>', lambda event: fillBandButtons(event.widget, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Button-3>', lambda event: contextMenu(event, band_buttons, dicTagsInTree))	
	appTreeView.bind('<Shift-Up>', lambda event: moveNodeBind(event, dicTagsInTree))
	appTreeView.bind('<Shift-Down>', lambda event: moveNodeBind(event, dicTagsInTree))
	appTreeView.bind('<Control-Key-c>', lambda event: copyToClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None)))
	appTreeView.bind('<Control-Key-C>', lambda event: copyToClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None)))
	appTreeView.bind('<Control-Key-v>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None)))
	appTreeView.bind('<Control-Key-V>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None)))
	appTreeView.bind('<Control-Alt-Key-v>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None, mode='CHILD')))
	appTreeView.bind('<Control-Alt-Key-V>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(appTreeView.focus(), None, mode='CHILD')))
	
	appTreeView.bind('<Control-Key-n>', lambda event: tk_app.createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-N>', lambda event: tk_app.createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-i>', lambda event: tk_app.createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'CHILD'))
	appTreeView.bind('<Control-Key-I>', lambda event: tk_app.createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'CHILD'))
	appTreeView.bind('<Delete>', lambda event: tk_app.deleteSelectionTagInTree(GL.appTreeView.selection()))
	
	
	return appTreeView
	
	
def setScrollbar(parent, widget):
	xScroll = Scrollbar(parent, orient=VERTICAL, command= widget.yview)
	widget.configure(yscrollcommand= xScroll.set)
	xScroll.pack(side=RIGHT,fill=Y)
	
	
	
def fillBandButtons(appTreeView, band_buttons, dicTagsInTree):
	band_buttons.clean()
	
	#scrollingFrame es un frame con un canvas dentro con un frame dentro, con scrollbars configuradas
	scrollFrame = SSF.scrollingFrame(band_buttons)
	scrollFrame.pack(side=BOTTOM, fill=BOTH, expand=True)
	
	xIDFocus = appTreeView.focus()
	GL.lastTreeViewFocus = xIDFocus
	print 'focus in ' + xIDFocus + ' - order ' + str(GL.dicTagsInTree[xIDFocus].tag_order)
	print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
	
	xRow = 0
	
	#showpath
	#getLabel(dicTagsInTree[xIDFocus].getPath(), scrollFrame.frame, xRow)
	Label(scrollFrame.frame, text=dicTagsInTree[xIDFocus].getPath(), font= '-weight bold', width=GL.labelButtonWidth+GL.labelExtraButtonWidth, justify=LEFT).grid(column=0, row=xRow, stick='nw', pady=5, columnspan=2)
	#Label(band_buttons, text=dicTagsInTree[xIDFocus].getPath(), font= '-weight bold').pack(side=TOP, expand=False)
	xRow += 1
	
	getButtonRow(dicTagsInTree[xIDFocus], scrollFrame.frame, xRow)
	xRow += 1
	Separator(scrollFrame.frame, orient=HORIZONTAL).grid(row=xRow, column=0, pady=4, columnspan=2, sticky='we')
	xRow += 1
	
	for xIDChild in appTreeView.get_children(xIDFocus):
		xGotItems = True
		getButtonRow(dicTagsInTree[xIDChild], scrollFrame.frame, xRow)
		xRow += 1

		
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
	
	if value.title() in xBoolOptions:
		# title devuelve el string capitalizado (o sea, la primera con mayúscula)
		value = value.title()
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
			xEntry = getTextEntry(band_buttons, xButtonWidth-xExtraButtonWidth, 1, xRow, oTagInTree, value[:xButtonWidth])
			xEntry.configure(state=DISABLED)
			xButton = Button(band_buttons, text='...', width= xExtraButtonWidth)
			xButton.grid(column=1, row=xRow, sticky='e')
			xButton.config(command= lambda: openTextWindow(band_buttons.master.master.master.master.master, oTagInTree, xEntry))

			
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
	#xWindow.textFieldConstructor(label, entry.get())
	xWindow.textFieldConstructor(label, oTagInTree.getTag().text)
	xWindow.show()
	
	if len(container) > 0:
		print 'updating ' + oTagInTree.tagname
		updateTreeNode(container[label], oTagInTree)
		#actualizo tambien el entry asociado
		entry.delete(0, END)
		#entry.insert(0, container[label])
		entry.insert(0, container[label][:GL.labelButtonWidth])
		
	
def updateTreeNode(value, oTagInTree):
		#print entry.get()
		print value
		oTagInTree.getTag().text = value
		oTagInTree.setColumn('data', value)
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
	menu.add_command(label=GL.names['submenu_copytag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG))
	menu.add_command(label=GL.names['submenu_cuttag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG, mode='CUT'))
	menu.add_command(label=GL.names['submenu_pastetag'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG))
	menu.add_command(label=GL.names['submenu_pastetagaschild'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG, mode='CHILD'))
	menu.add_separator()
	
	#fold/unfold
	menu.add_command(label=GL.names['submenu_fold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, False))
	menu.add_command(label=GL.names['submenu_unfold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, True))
	menu.add_separator()
	
	#menu.add_command(label='test_path', state=ACTIVE, command= lambda:showPath(focusTIG))
	
	#comment commands
	if focusTIG.is_comment:
		menu.add_command(label=GL.names['submenu_uncomment'], state=ACTIVE, command= lambda: unCommentTag(mainApp, focusTIG))
	else:
		menu.add_command(label=GL.names['submenu_comment'], state=ACTIVE, command= lambda: commentTag(mainApp, focusTIG))
		
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
					
	#run modules
	params = {'parent':menu, 'parentTIG':focusTIG, 'mainApp':mainApp}
	MOD.runModules('TREEVIEW_MENU', params)
	
					
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
		
def copyToClipboard(mainApp, oTIG, mode='COPY'):
	if oTIG <> None:
		stringXML = xml_man.getStringXML(oTIG.getTag())
		mainApp.clipboard_clear()
		mainApp.clipboard_append(stringXML[ stringXML.find('\n')+1:])
		if mode == 'CUT':
			tk_app.deleteTagInTree(oTIG.id)
		
def pasteFromClipboard(mainApp, baseTIG, mode='SIBLING', stringXML=''):
	if baseTIG <> None:
		if stringXML == '':
			stringXML = mainApp.selection_get(selection='CLIPBOARD')
			#stringXML = stringXML.replace('\n', '')
		try:
			print stringXML
		except UnicodeEncodeError:
			print 'using unicode'
			stringXML = unicode(stringXML, "utf-8")
			print stringXML
		pasteRoot = xml_man.parseStringXML_old(stringXML)
		print 'pasteRoot', pasteRoot
		
		rootTIG = tk_app.createNewTagInTree(mainApp, baseTIG, mode, oTag=pasteRoot)
		#comentado porque duplicaba los childs al pegar
		#createChildTIGs(mainApp, rootTIG, level=0)
		#reemplazado por un refresh, que actualiza el arbol
		tk_app.refreshTreeview(mainApp)
		
		tk_app.selectAndFocus(rootTIG.id)


def createChildTIGs(mainApp, parentTIG, level):
	qChildren = parentTIG.getNumberOfChildren()
	for xChild in parentTIG.getTag():
		print 'paste has child level', level, 'Q', qChildren
		xChildTIG = tk_app.createNewTagInTree(mainApp, parentTIG, 'CHILD', oTag=xChild)
		createChildTIGs(mainApp, xChildTIG, level=level+1)
		qChildren -= 1
		if qChildren <= 0:
			break

		
def commentTag(mainApp, oTIG):
	if oTIG <> None:
		#stringXML = xml_man.getStringXML(oTIG.getTag())
		newComment = tk_app.createNewTagInTree(mainApp, oTIG, 'SIBLING', is_comment=True)
		tk_app.deleteTagInTree(oTIG.id)
		
def unCommentTag(mainApp, commentTIG):
	stringXML = commentTIG.getTag().text
	newTIG = None
	response = 'no'
	try:
		newTag = xml_man.parseStringXML_old(stringXML)
		newTIG = tk_app.createNewTagInTree(mainApp, commentTIG, 'SIBLING', oTag = newTag)
	except:
		response = tkMessageBox.showwarning("eXMLorer", GL.names['message_uncomment_newtag'], type=tkMessageBox.YESNO)
		if response == 'yes':
			newTIG = tk_app.createNewTagInTree(mainApp, commentTIG, 'SIBLING', text=commentTIG.getTag().text)
	
	if newTIG <> None:
		createChildTIGs(mainApp, newTIG, level=0)
		tk_app.deleteTagInTree(commentTIG.id)
		tk_app.selectAndFocus(newTIG.id)
		
def unfoldingAll(idFocus, isOpen):
	#for xIDChild in appTreeView.get_children(xIDFocus):
	GL.appTreeView.item(idFocus, open=isOpen)
	for idChild in GL.appTreeView.get_children(idFocus):
		unfoldingAll(idChild, isOpen)
		
def showPath(oTIG):
	print oTIG.getPath()
# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox

from config import Globals as GL
from xml_parser import XmlParser
import module_interface as MOD
import SSF
import App

def getTreeView(treeview_frame, band_buttons, dicTagsInTree):
	appTreeView = Treeview(treeview_frame, columns=('data','subname',))
	appTreeView.pack(side="left",fill=BOTH)
	
	setScrollbar(treeview_frame, appTreeView)
	
	mainApp = treeview_frame.master.master
	
	appTreeView.column('subname', width=120, anchor='w', stretch=True)
	appTreeView.column('data', width=480, anchor='w', stretch=True)
	appTreeView.heading('subname', text= GL.lang['column-subname'])
	appTreeView.heading('data', text= GL.lang['column-data'])
	
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
	
	appTreeView.bind('<Control-Key-n>', lambda event: App.createNewTagInTree(mainApp, GL.tags_in_tree_dictionary.setdefault(GL.app_treeview.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-N>', lambda event: App.createNewTagInTree(mainApp, GL.tags_in_tree_dictionary.setdefault(GL.app_treeview.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-i>', lambda event: App.createNewTagInTree(mainApp, GL.tags_in_tree_dictionary.setdefault(GL.app_treeview.focus(), None), 'CHILD'))
	appTreeView.bind('<Control-Key-I>', lambda event: App.createNewTagInTree(mainApp, GL.tags_in_tree_dictionary.setdefault(GL.app_treeview.focus(), None), 'CHILD'))
	appTreeView.bind('<Delete>', lambda event: App.deleteSelectionTagInTree(GL.app_treeview.selection()))
	
	
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
	GL.last_treeview_focus = xIDFocus
	print 'focus in ' + xIDFocus + ' - order ' + str(GL.tags_in_tree_dictionary[xIDFocus].tag_order)
	print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
	
	xRow = 0
	
	#showpath
	#getLabel(dicTagsInTree[xIDFocus].getPath(), scrollFrame.frame, xRow)
	Label(scrollFrame.frame, text=dicTagsInTree[xIDFocus].getPath(), font= '-weight bold', width=GL.label_button_width + GL.label_extra_button_width, justify=LEFT).grid(column=0, row=xRow, stick='nw', pady=5, columnspan=2)
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
	xButtonWidth = GL.label_button_width
	xExtraButtonWidth = GL.label_extra_button_width
	xMarginToExtendToText = GL.margin_to_extend_for_text
	
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
			xButton = Button(band_buttons, text=GL.lang['button_open'], width= xExtraButtonWidth)
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
	label = GL.lang['message_value']
	title = GL.lang['message_editing'] + ' ' + oTagInTree.tagname
	xWindow = mainApp.get_aux_window(title, container)
	#xWindow.text_field_constructor(label, entry.get())
	xWindow.text_field_constructor(label, oTagInTree.getTag().text)
	xWindow.show()
	
	if len(container) > 0:
		print 'updating ' + oTagInTree.tagname
		updateTreeNode(container[label], oTagInTree)
		#actualizo tambien el entry asociado
		entry.delete(0, END)
		#entry.insert(0, container[label])
		entry.insert(0, container[label][:GL.label_button_width])
		
	
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
		#xml_man.move_tag( dicTagsInTree[xIDParent].getTag(), dicTagsInTree[xIDFocus].getTag(), xPosition)
		
		return 'break'
		
def moveNode(xIDFocus, xIDParent, xPosition, dicTagsInTree):
	GL.app_treeview.move(xIDFocus, xIDParent, xPosition)
	
	if xPosition == 'end':
		xPosition = dicTagsInTree[xIDFocus].getNumberOfSiblings()
	
	XmlParser.move_tag(dicTagsInTree[xIDParent].getTag(), dicTagsInTree[xIDFocus].getTag(), xPosition)

def contextMenu(event, band_buttons, dicTagsInTree):
	print 'context menu'
	
	#la ruta es evento.TreeView.BandaTreeView.BandaCenter.mainApp
	mainApp = event.widget.master.master.master
	
	xFocusIDContextMenu = GL.app_treeview.identify_row(event.y)
	print 'identify row shows %s' % xFocusIDContextMenu
	GL.app_treeview.focus(xFocusIDContextMenu)
	
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
	menu = Menu(GL.app_treeview, tearoff=0)
	
	menu.add_command(label=GL.lang['submenu_edittag'], state=ACTIVE, command= lambda:editTag(mainApp, focusTIG))
	menu.add_command(label=GL.lang['submenu_copytag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG))
	menu.add_command(label=GL.lang['submenu_cuttag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG, mode='CUT'))
	menu.add_command(label=GL.lang['submenu_pastetag'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG))
	menu.add_command(label=GL.lang['submenu_pastetagaschild'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG, mode='CHILD'))
	menu.add_separator()
	
	#fold/unfold
	menu.add_command(label=GL.lang['submenu_fold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, False))
	menu.add_command(label=GL.lang['submenu_unfold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, True))
	menu.add_separator()
	
	#menu.add_command(label='test_path', state=ACTIVE, command= lambda:showPath(focusTIG))
	
	#comment commands
	if focusTIG.is_comment:
		menu.add_command(label=GL.lang['submenu_uncomment'], state=ACTIVE, command= lambda: unCommentTag(mainApp, focusTIG))
	else:
		menu.add_command(label=GL.lang['submenu_comment'], state=ACTIVE, command= lambda: commentTag(mainApp, focusTIG))
		
	menu.add_separator()
	menu.add_command(label= GL.lang['submenu_selectParentSubname'],
                     state= subnameCmdState,
                     command= lambda
							  parentTIG = parentTIG, 
							  focusTIG = focusTIG: 
							  setAsParentSubname(parentTIG, focusTIG)
                     )
	menu.add_command(label= GL.lang['submenu_cleanParentSubname'],
                     state= cleanCmdState,
                     command= lambda
							  focusTIG = focusTIG: 
							  cleanSubname(focusTIG)
                     )
					
	#run modules
	params = {'parent':menu, 'parentTIG':focusTIG, 'mainApp':mainApp}
	MOD.runModules('TREEVIEW_MENU', params)
	
					
	print 'identify row shows %s' % GL.app_treeview.identify_row(event.y)
	menu.post(event.x_root, event.y_root)
	
def setAsParentSubname(parentTIG, childTIG):
	GL.tag_subnames.updateDic(parentTIG.getTag().tag, childTIG.getTag().tag)
	parentTIG.updateSubname( childTIG.getTag().text)
	
def cleanSubname(oTIG):
	GL.tag_subnames.updateDic(oTIG.getTag().tag, '')
	oTIG.updateSubname('')
	GL.tag_subnames.deleteFromDic(oTIG.getTag().tag)

def editTag(mainApp, oTIG):
	container = {'Tag': oTIG.getTag().tag, 'Value':oTIG.getTag().text}
	xWindow = mainApp.get_aux_window(GL.lang['message_edittag'], container)
	xWindow.form_constructor('Tag', 0)
	xWindow.form_constructor('Value', 1)
	xWindow.show()
	
	if len(container) > 0:
		oTIG.updateTag(container['Tag'], container['Value'])
		updateTreeNode(container['Value'], oTIG)
		oTIG.parent_treeview.item(oTIG.id, text=oTIG.getTagName())
		
		fillBandButtons(GL.app_treeview, mainApp.frames.buttons, GL.tags_in_tree_dictionary)
		
def copyToClipboard(mainApp, oTIG, mode='COPY'):
	if oTIG <> None:
		stringXML = XmlParser.get_string_from_xml_node(oTIG.getTag())
		mainApp.clipboard_clear()
		mainApp.clipboard_append(stringXML[ stringXML.find('\n')+1:])
		if mode == 'CUT':
			App.deleteTagInTree(oTIG.id)
		
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
		pasteRoot = XmlParser.get_xml_from_string(stringXML)
		print 'pasteRoot', pasteRoot
		
		rootTIG = App.createNewTagInTree(mainApp, baseTIG, mode, oTag=pasteRoot)
		#comentado porque duplicaba los childs al pegar
		#createChildTIGs(mainApp, rootTIG, level=0)
		#reemplazado por un refresh, que actualiza el arbol
		App.refreshTreeview(mainApp)
		
		App.selectAndFocus(rootTIG.id)


def createChildTIGs(mainApp, parentTIG, level):
	qChildren = parentTIG.getNumberOfChildren()
	for xChild in parentTIG.getTag():
		print 'paste has child level', level, 'Q', qChildren
		xChildTIG = App.createNewTagInTree(mainApp, parentTIG, 'CHILD', oTag=xChild)
		createChildTIGs(mainApp, xChildTIG, level=level+1)
		qChildren -= 1
		if qChildren <= 0:
			break

		
def commentTag(mainApp, oTIG):
	if oTIG <> None:
		#stringXML = xml_man.get_string_from_xml_node(oTIG.getTag())
		newComment = App.createNewTagInTree(mainApp, oTIG, 'SIBLING', is_comment=True)
		App.deleteTagInTree(oTIG.id)
		
def unCommentTag(mainApp, commentTIG):
	stringXML = commentTIG.getTag().text
	newTIG = None
	response = 'no'
	try:
		newTag = XmlParser.get_xml_from_string(stringXML)
		newTIG = App.createNewTagInTree(mainApp, commentTIG, 'SIBLING', oTag = newTag)
	except:
		response = tkMessageBox.showwarning("eXMLorer", GL.lang['message_uncomment_newtag'], type=tkMessageBox.YESNO)
		if response == 'yes':
			newTIG = App.createNewTagInTree(mainApp, commentTIG, 'SIBLING', text=commentTIG.getTag().text)
	
	if newTIG <> None:
		createChildTIGs(mainApp, newTIG, level=0)
		App.deleteTagInTree(commentTIG.id)
		App.selectAndFocus(newTIG.id)
		
def unfoldingAll(idFocus, isOpen):
	#for xIDChild in appTreeView.get_children(xIDFocus):
	GL.app_treeview.item(idFocus, open=isOpen)
	for idChild in GL.app_treeview.get_children(idFocus):
		unfoldingAll(idChild, isOpen)
		
def showPath(oTIG):
	print oTIG.getPath()
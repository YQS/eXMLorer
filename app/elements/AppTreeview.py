# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox

from config import Globals
from xml_parser import XmlParser
import app.module_interface as MOD
import app.SSF
import app.App

class AppTreeview(Treeview):
	def __init__(self, app):
		parent = app.frames.treeview
		Treeview.__init__(self, parent, columns=('data', 'subname',))

		self.pack(side='left', fill=BOTH)
		self.set_scrollbar()
		self.set_columns()
		self.bind_events()


	def set_scrollbar(self):
		scrollbar = Scrollbar(self.parent, orient=VERTICAL, command= self.yview)
		self.configure(yscrollcommand= scrollbar.set)
		scrollbar.pack(side=RIGHT, fill=Y)

	def set_columns(self):
		self.column('subname', width=120, anchor='w', stretch=True)
		self.column('data',    width=480, anchor='w', stretch=True)
		self.heading('subname', text=Globals.lang['column-subname'])
		self.heading('data',    text=Globals.lang['column-data'])

		self.configure(displaycolumns=('subname', 'data'))

	def bind_events(self):
		self.bind('<<TreeviewSelect>>', lambda event: self.fill_buttons_frame(band_buttons, dicTagsInTree))
		self.bind('<Button-3>', lambda event: contextMenu(event, band_buttons, dicTagsInTree))
		self.bind('<Shift-Up>', lambda event: moveNodeBind(event, dicTagsInTree))
		self.bind('<Shift-Down>', lambda event: moveNodeBind(event, dicTagsInTree))
		self.bind('<Control-Key-c>', lambda event: copyToClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None)))
		self.bind('<Control-Key-C>', lambda event: copyToClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None)))
		self.bind('<Control-Key-v>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None)))
		self.bind('<Control-Key-V>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None)))
		self.bind('<Control-Alt-Key-v>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None, mode='CHILD')))
		self.bind('<Control-Alt-Key-V>', lambda event: pasteFromClipboard(mainApp, dicTagsInTree.setdefault(self.focus(), None, mode='CHILD')))

		self.bind('<Control-Key-n>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'SIBLING'))
		self.bind('<Control-Key-N>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'SIBLING'))
		self.bind('<Control-Key-i>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'CHILD'))
		self.bind('<Control-Key-I>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'CHILD'))
		self.bind('<Delete>', lambda event: app.App.deleteSelectionTagInTree(Globals.app_treeview.selection()))

	def fill_buttons_frame(self):
		buttons_frame = Globals.app.frames.buttons
		buttons_frame.clean()

		id_focus = self.focus()
		Globals.last_treeview_focus = id_focus
		focused_editag = Globals.editag_dictionary[id_focus]

		# scrollingFrame es un frame con un canvas dentro con un frame dentro, con scrollbars configuradas
		scrolling_frame = app.SSF.scrollingFrame(buttons_frame)
		scrolling_frame.pack(side=BOTTOM, fill=BOTH, expand=True)

		Label(scrolling_frame.frame,
			  text=focused_editag.get_xml_path(),
			  font='-weight bold',
			  width=Globals.label_button_width + Globals.label_extra_button_width,
			  justify=LEFT)\
			.grid(column=0, row=0, stick='nw', pady=5, columnspan=2)

		focused_editag.get_as_button_row(scrolling_frame.frame, 1)
		scrolling_frame.create_separator()

		row = 3
		for child_editag in focused_editag:
			child_editag.get_as_button_row(scrolling_frame.frame, row)
			row += 1


def getTreeView(treeview_frame, band_buttons, dicTagsInTree):
	appTreeView = Treeview(treeview_frame, columns=('data','subname',))
	appTreeView.pack(side="left",fill=BOTH)

	setScrollbar(treeview_frame, appTreeView)

	mainApp = treeview_frame.master.master

	appTreeView.column('subname', width=120, anchor='w', stretch=True)
	appTreeView.column('data', width=480, anchor='w', stretch=True)
	appTreeView.heading('subname', text= Globals.lang['column-subname'])
	appTreeView.heading('data', text= Globals.lang['column-data'])

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

	appTreeView.bind('<Control-Key-n>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-N>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'SIBLING'))
	appTreeView.bind('<Control-Key-i>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'CHILD'))
	appTreeView.bind('<Control-Key-I>', lambda event: app.App.createNewTagInTree(mainApp, Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None), 'CHILD'))
	appTreeView.bind('<Delete>', lambda event: app.App.deleteSelectionTagInTree(Globals.app_treeview.selection()))


	return appTreeView


def setScrollbar(parent, widget):
	xScroll = Scrollbar(parent, orient=VERTICAL, command= widget.yview)
	widget.configure(yscrollcommand= xScroll.set)
	xScroll.pack(side=RIGHT,fill=Y)


def moveNodeBind(event, dicTagsInTree):
		if event.keycode == 38:		#Up
			xDirection = -1
		elif event.keycode == 40:	#Down
			xDirection = 1

		appTreeView = event.widget
		xIDFocus = appTreeView.focus()
		xIDParent = dicTagsInTree[xIDFocus].get_parent().id
		xPosition = dicTagsInTree[xIDFocus].get_treeview_index() + xDirection
		moveNode( xIDFocus, xIDParent, xPosition, dicTagsInTree)
		#appTreeView.move( xIDFocus, xIDParent, xPosition)
		#xml_man.move_tag( dicTagsInTree[xIDParent].xmltag(), dicTagsInTree[xIDFocus].xmltag(), xPosition)

		return 'break'

def moveNode(xIDFocus, xIDParent, xPosition, dicTagsInTree):
	Globals.app_treeview.move(xIDFocus, xIDParent, xPosition)

	if xPosition == 'end':
		xPosition = dicTagsInTree[xIDFocus].get_number_of_siblings()

	XmlParser.move_tag(dicTagsInTree[xIDParent].xmltag(), dicTagsInTree[xIDFocus].xmltag(), xPosition)

def contextMenu(event, band_buttons, dicTagsInTree):
	print 'context menu'

	#la ruta es evento.TreeView.BandaTreeView.BandaCenter.mainApp
	mainApp = event.widget.master.master.master

	xFocusIDContextMenu = Globals.app_treeview.identify_row(event.y)
	print 'identify row shows %s' % xFocusIDContextMenu
	Globals.app_treeview.focus(xFocusIDContextMenu)

	# getting variables for commands
	focusTIG = dicTagsInTree[xFocusIDContextMenu]

	parentTIG = focusTIG.get_parent()
	subnameCmdState = ACTIVE
	if parentTIG == None:
		subnameCmdState = DISABLED

	cleanCmdState = DISABLED
	if focusTIG.has_child():
		cleanCmdState = ACTIVE

	#menu
	menu = Menu(Globals.app_treeview, tearoff=0)

	menu.add_command(label=Globals.lang['submenu_edittag'], state=ACTIVE, command= lambda:editTag(mainApp, focusTIG))
	menu.add_command(label=Globals.lang['submenu_copytag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG))
	menu.add_command(label=Globals.lang['submenu_cuttag'], state=ACTIVE, command= lambda:copyToClipboard(mainApp, focusTIG, mode='CUT'))
	menu.add_command(label=Globals.lang['submenu_pastetag'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG))
	menu.add_command(label=Globals.lang['submenu_pastetagaschild'], state=ACTIVE, command= lambda:pasteFromClipboard(mainApp, focusTIG, mode='CHILD'))
	menu.add_separator()

	#fold/unfold
	menu.add_command(label=Globals.lang['submenu_fold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, False))
	menu.add_command(label=Globals.lang['submenu_unfold'], state=ACTIVE, command= lambda:unfoldingAll(xFocusIDContextMenu, True))
	menu.add_separator()

	#menu.add_command(label='test_path', state=ACTIVE, command= lambda:showPath(focusTIG))

	#comment commands
	if focusTIG.is_comment:
		menu.add_command(label=Globals.lang['submenu_uncomment'], state=ACTIVE, command= lambda: unCommentTag(mainApp, focusTIG))
	else:
		menu.add_command(label=Globals.lang['submenu_comment'], state=ACTIVE, command= lambda: commentTag(mainApp, focusTIG))

	menu.add_separator()
	menu.add_command(label= Globals.lang['submenu_selectParentSubname'],
					 state= subnameCmdState,
					 command= lambda
							  parentTIG = parentTIG,
							  focusTIG = focusTIG:
							  setAsParentSubname(parentTIG, focusTIG)
					 )
	menu.add_command(label= Globals.lang['submenu_cleanParentSubname'],
					 state= cleanCmdState,
					 command= lambda
							  focusTIG = focusTIG:
							  cleanSubname(focusTIG)
					 )

	#run modules
	params = {'parent':menu, 'parentTIG':focusTIG, 'mainApp':mainApp}
	MOD.runModules('TREEVIEW_MENU', params)


	print 'identify row shows %s' % Globals.app_treeview.identify_row(event.y)
	menu.post(event.x_root, event.y_root)

def setAsParentSubname(parentTIG, childTIG):
	Globals.subnames.update(parentTIG.xmltag().tag, childTIG.xmltag().tag)
	parentTIG.update_subname(childTIG.xmltag().text)

def cleanSubname(oTIG):
	Globals.subnames.update(oTIG.xmltag().tag, '')
	oTIG.update_subname('')
	Globals.subnames.delete(oTIG.xmltag().tag)

def editTag(mainApp, oTIG):
	container = {'Tag': oTIG.xmltag().tag, 'Value':oTIG.xmltag().text}
	xWindow = mainApp.get_aux_window(Globals.lang['message_edittag'], container)
	xWindow.form_constructor('Tag', 0)
	xWindow.form_constructor('Value', 1)
	xWindow.show()

	if len(container) > 0:
		oTIG.update_tag(container['Tag'], container['Value'])
		updateTreeNode(container['Value'], oTIG)
		oTIG.parent_treeview.item(oTIG.id, text=oTIG.get_tag_name())

		fillBandButtons(Globals.app_treeview, mainApp.frames.buttons, Globals.editag_dictionary)

def copyToClipboard(mainApp, oTIG, mode='COPY'):
	if oTIG <> None:
		stringXML = XmlParser.get_string_from_xml_node(oTIG.xmltag())
		mainApp.clipboard_clear()
		mainApp.clipboard_append(stringXML[ stringXML.find('\n')+1:])
		if mode == 'CUT':
			app.App.deleteTagInTree(oTIG.id)

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

		rootTIG = app.App.createNewTagInTree(mainApp, baseTIG, mode, oTag=pasteRoot)
		#comentado porque duplicaba los childs al pegar
		#createChildTIGs(mainApp, rootTIG, level=0)
		#reemplazado por un refresh, que actualiza el arbol
		app.App.refreshTreeview(mainApp)

		app.App.selectAndFocus(rootTIG.id)


def createChildTIGs(mainApp, parentTIG, level):
	qChildren = parentTIG.get_number_of_children()
	for xChild in parentTIG.xmltag():
		print 'paste has child level', level, 'Q', qChildren
		xChildTIG = app.App.createNewTagInTree(mainApp, parentTIG, 'CHILD', oTag=xChild)
		createChildTIGs(mainApp, xChildTIG, level=level+1)
		qChildren -= 1
		if qChildren <= 0:
			break


def commentTag(mainApp, oTIG):
	if oTIG <> None:
		#stringXML = xml_man.get_string_from_xml_node(oTIG.xmltag())
		newComment = app.App.createNewTagInTree(mainApp, oTIG, 'SIBLING', is_comment=True)
		app.App.deleteTagInTree(oTIG.id)

def unCommentTag(mainApp, commentTIG):
	stringXML = commentTIG.xmltag().text
	newTIG = None
	response = 'no'
	try:
		newTag = XmlParser.get_xml_from_string(stringXML)
		newTIG = app.App.createNewTagInTree(mainApp, commentTIG, 'SIBLING', oTag = newTag)
	except:
		response = tkMessageBox.showwarning("eXMLorer", Globals.lang['message_uncomment_newtag'], type=tkMessageBox.YESNO)
		if response == 'yes':
			newTIG = app.App.createNewTagInTree(mainApp, commentTIG, 'SIBLING', text=commentTIG.xmltag().text)

	if newTIG <> None:
		createChildTIGs(mainApp, newTIG, level=0)
		app.App.deleteTagInTree(commentTIG.id)
		app.App.selectAndFocus(newTIG.id)

def unfoldingAll(idFocus, isOpen):
	#for xIDChild in appTreeView.get_children(xIDFocus):
	Globals.app_treeview.item(idFocus, open=isOpen)
	for idChild in Globals.app_treeview.get_children(idFocus):
		unfoldingAll(idChild, isOpen)

def showPath(oTIG):
	print oTIG.get_xml_path()
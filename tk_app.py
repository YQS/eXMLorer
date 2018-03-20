# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
from ScrolledText import ScrolledText as ScrollText
import xml.etree.ElementTree as ET
import os.path

import globals as GL
import app_language as LANG
import TagInTree as TIG
import xml_man
import tk_treeview
from search_man import BasicSearch
import module_interface as MOD
from TempData import TempData


# CLASSES

class FrameExt(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.dic = {}

	def addWidget(self, sWidget, sKey, sParameters='', sObject=None):
		if sObject == None:
			sCodeLine = '%s(self)' % sWidget
			if sParameters <> '':
				sCodeLine = sCodeLine.replace(')', ', %s)' % sParameters)
			print sCodeLine
			self.dic[sKey] = eval(sCodeLine)
		else:
			self.dic[sKey] = sObject

		return self.dic[sKey]

	def clean(self):
		for widget in self.winfo_children():
			widget.destroy()

class ToplevelFromMain(Toplevel):
	def __init__(self, master, title, container, useSQLButtons=True):
		Toplevel.__init__(self)
		#self.overrideredirect(1)
		self.transient(master)
		self.title(title)

		self.parent  = master
		self.result  = container
		self.entries = {}
		self.upper   = Frame(self)
		self.body    = Frame(self)
		self.buttons = Frame(self)
		self.firstField = None

		self.useSQLButtons = useSQLButtons

		self.upper.pack(side=TOP, fill=X)
		self.body.pack(side=TOP, fill=BOTH, expand=True)
		self.buttons.pack(side=BOTTOM, fill=X)
		self.createButtons()

		self.geometry('+%d+%d' % (master.winfo_rootx()+50, master.winfo_rooty()+50))
		self.protocol('WM_DELETE_WINDOW', lambda: self.cancel())

		self.bind('<Alt-a>', lambda event: self.apply())
		self.bind('<Alt-A>', lambda event: self.apply())

	def createButtons(self):
		Button(self.buttons, text=GL.names['button_ok'], width=GL.buttonWidth, command=lambda: self.apply()).grid(row=0, column=0)
		Button(self.buttons, text=GL.names['button_cancel'], width=GL.buttonWidth, command=lambda: self.cancel()).grid(row=0, column=1)

	def formConstructor(self, labelText, xRow):
		Label(self.body, text=labelText).grid(row=xRow, column=0, sticky='e')
		xEntry = Entry(self.body, width=30)
		xEntry.grid(row=xRow, column=1, sticky='w')
		stringToInsert = self.result.setdefault(labelText, '')
		if stringToInsert == None:
			stringToInsert = ''
		#xEntry.insert(0, self.result.setdefault(labelText, u''))
		xEntry.insert(0, stringToInsert)
		self.entries[labelText] = xEntry
		if self.firstField == None:
			self.firstField = xEntry

	def textFieldConstructor(self, labelText, value):
		def selectAllText(event):
			xField = event.widget
			xField.tag_add(SEL, '1.0', 'end')
			xField.mark_set(INSERT, "1.0")
			xField.see(INSERT)
			return 'break'

		#Label(self.body, text=labelText).grid(row=0, column=0, sticky='nw')
		Label(self.body, text=labelText).pack(side=TOP)

		#xTextbox = Text(self.body) ## ver que width y height poner
		xTextbox = ScrollText(self.body)
		#xTextbox.bind('<KeyRelease>', lambda event: apply())
		xTextbox.bind('<Control-Key-a>', lambda event: selectAllText(event) )
		xTextbox.bind('<Control-Key-A>', lambda event: selectAllText(event) )
		#xTextbox.grid(row=1, column=0, sticky='nw')
		xTextbox.pack(side=BOTTOM, fill=BOTH, expand=True)
		xTextbox.insert('1.0', value)
		self.entries[labelText] = xTextbox
		if self.firstField == None:
			self.firstField = xTextbox

		#SQL buttons from module
		params = {'parent':self.upper, 'field':self.firstField, 'useButtons':self.useSQLButtons}
		MOD.runModules('TOPLEVEL', params)

	def bSQLButtons(self, SQLfunction):
		#asumo que si uso estas funciones, el firstField es el campo que me interesa
		text = self.firstField.get('1.0', 'end')
		text = SQLfunction(text)
		self.firstField.delete('1.0', 'end')
		self.firstField.insert('1.0', text)

	def show(self):
		self.wait_visibility()
		self.grab_set()
		self.focus_set()
		if self.firstField <> None:
			self.firstField.focus_set()
		self.wait_window()
		#self.grab_release()

	def apply(self):
		for key in self.entries:
			if isinstance(self.entries[key], Text):
				self.result[key] = self.entries[key].get('1.0', 'end')
			else:
				self.result[key] = self.entries[key].get()
		#print self.result
		self.close()

	def cancel(self):
		self.entries.clear()
		self.close()

	def close(self):
		self.grab_release()
		self.parent.focus_set()
		self.destroy()


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

		#elementos del main
		self.excludeList = lExcludeMenu
		self.rootTIG = None
		self.menubar = None
		self.currentSearch = None
		self.temp = TempData(GL.tempDataFile)
		#BooleanVars para los menues
		self.bool_menu_config_lang_eng = BooleanVar()
		self.bool_menu_config_lang_spa = BooleanVar()
		self.bool_menu_config_prettyprint = BooleanVar()
		self.bool_menu_config_noSpaceInSelfClosingTag = BooleanVar()
		self.bool_menu_config_linefyAtSave = BooleanVar()
		self.bool_menu_config_caseSensitive = BooleanVar()
		self.bool_menu_config_others_SQLButtons = BooleanVar()
		self.bool_menu_config_others_showFileFullPath = BooleanVar()
		self.bool_menu_config_showComments = BooleanVar()
		self.string_optionmenu_search = StringVar()

		#chequeo estado inicial de BooleanVars de menues
		if GL.names['lang'] == 'Español':
			self.bool_menu_config_lang_spa.set(True)
		else:
			self.bool_menu_config_lang_eng.set(True)

		if GL.defaultPrettyPrint:
			self.bool_menu_config_prettyprint.set(True)
		if GL.eliminateSpaceInSelfClosingTag:
			self.bool_menu_config_noSpaceInSelfClosingTag.set(True)
		if GL.linefyAtSave:
			self.bool_menu_config_linefyAtSave.set(True)
		if GL.caseSensitiveSearch:
			self.bool_menu_config_caseSensitive.set(True)
		if GL.useSQLButtons:
			self.bool_menu_config_others_SQLButtons.set(True)
		if GL.showFileFullPath:
			self.bool_menu_config_others_showFileFullPath.set(True)
		if GL.showComments:
			self.bool_menu_config_showComments.set(True)

		#icono
		try:
			self.iconImage = PhotoImage(file= iconfile)
			self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
		except TclError:
			print 'No se encontro el archivo de icono %s' % iconfile

		#captura de cierre del programa
		self.protocol('WM_DELETE_WINDOW', lambda:quitApp(self))

		#frames
		self.frames = FramePack(self)
		self.frames.menu.pack(side=TOP, fill=X)

		self.frames.center.pack(side=TOP, fill=BOTH, expand=True)
		self.frames.treeview.pack(side=LEFT, fill=BOTH)
		self.frames.buttons.pack(side=LEFT, fill=BOTH, expand=True, ipadx=0, pady=20)
		#setScrollbar(self, self.frames.buttons)
		self.frames.footer.pack(side=BOTTOM, fill=X)

		fillMenu(self)				#menu real
		fillButtonBarFrame(self)	#botones debajo del menu
		fillFooterFrame(self)

		#refreshApp(self)

		#binds
		self.bind('<F5>', lambda event: refreshTreeview(self))

	#metodos del MainApp
	def getToplevel2(self, title, container, useSQLButtons=True):
		return ToplevelFromMain(self, title, container, useSQLButtons)


##################
def setScrollbar(parent, widget):
	xScroll = Scrollbar(parent, command= widget.yview)
	widget.configure(yscrollcommand= xScroll.set)
	xScroll.pack(side='right',fill='y')
##################

# METHODS
def refreshApp(mainApp):
	#mainApp = event.widget

	#clean bars
	for i in range(0,50):	#habría que ver si se puede hacer esto más eficiente
		try:
			mainApp.menubar.delete(i)
		except:
			break
	mainApp.frames.menu.clean()
	mainApp.frames.footer.clean()
	mainApp.frames.treeview.clean()
	mainApp.frames.buttons.clean()

	#fill bars
	fillMenu(mainApp)
	fillButtonBarFrame(mainApp)
	fillFooterFrame(mainApp)

	#mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
	setFilenameLabel(mainApp.frames.menu.dic['label_filename'])

	refreshTreeview(mainApp)

def refreshTreeview(mainApp):
	#clean treeview frame
	mainApp.frames.treeview.clean()

	#set globals
	GL.dicTagsInTree = {}
	GL.appTreeView = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons, GL.dicTagsInTree)

	#load xml dic and TIGs
	root = GL.XMLTree.getroot()

	GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
	addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
	mainApp.update()

	selectAndFocus(GL.lastTreeViewFocus)

def selectAndFocus(xIDFocus):
	if xIDFocus <> '':
		GL.appTreeView.see(xIDFocus)
		GL.appTreeView.focus(xIDFocus)
		GL.appTreeView.selection_set(xIDFocus)


def fillMenu(mainApp):
	menubar = Menu(mainApp)
	mainApp.config(menu=menubar)
	mainApp.menubar = menubar

	if not 'menu_file' in mainApp.excludeList:
		menu_file = Menu(menubar, tearoff=0)
		menubar.add_cascade(label=GL.names['menu_file'], menu=menu_file)

		menu_file.add_command(label= GL.names['menu_file_open'],   command= lambda: openXML(mainApp))
		menu_file.add_command(label= GL.names['menu_file_save'],   command= lambda: saveXML(mainApp, 'SAVE'))
		menu_file.add_command(label= GL.names['menu_file_saveas'], command= lambda: saveXML(mainApp, 'SAVEAS'))
		menu_file.add_command(label= GL.names['menu_file_exit'],   command= lambda: quitApp(mainApp))

	if not 'menu_config' in mainApp.excludeList:
		#seteo menu Configuración
		menu_config = Menu(menubar, tearoff=0)
		menubar.add_cascade(label= GL.names['menu_config'], menu=menu_config)

		menu_config_language = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_language']+ ' ', menu=menu_config_language)
		#menu_config.add_command(label= GL.names['menu_config_language'], command=None)

		#seteo lenguajes
		#menu_config_language.add_command(label=GL.names['menu_config_language_spa'], command= lambda: mChangeLang(mainApp, 'SPA'))
		#menu_config_language.add_command(label=GL.names['menu_config_language_eng'], command= lambda: mChangeLang(mainApp, 'ENG'))
		menu_config_language.add_checkbutton(label=GL.names['menu_config_language_spa'],
											 variable=mainApp.bool_menu_config_lang_spa,
											 command= lambda: mChangeLang(mainApp, 'SPA'))
		menu_config_language.add_checkbutton(label=GL.names['menu_config_language_eng'],
											 variable= mainApp.bool_menu_config_lang_eng,
											 command= lambda: mChangeLang(mainApp, 'ENG'))

		#menu_config.add_separator()

		#menu de visualizacion
		menu_config_visualization = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_visualization'], menu=menu_config_visualization)
		menu_config_visualization.add_checkbutton(label=GL.names['menu_config_visualization_showcomments'],
												  variable= mainApp.bool_menu_config_showComments,
												  command= lambda: mSwitchGlobal('GL.showComments', 'show_comments', refreshTree=True))

		#seteo config de print modes
		menu_config_printmode = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_printmode'], menu=menu_config_printmode)
		menu_config_printmode.add_checkbutton(label=GL.names['menu_config_printmode_prettyprint'],
											  variable= mainApp.bool_menu_config_prettyprint,
											  command= lambda: mSwitchGlobal('GL.defaultPrettyPrint', 'pretty_print'))
		menu_config_printmode.add_checkbutton(label=GL.names['menu_config_printmode_nospaceclosedtag'],
											  variable= mainApp.bool_menu_config_noSpaceInSelfClosingTag,
											  command= lambda: mSwitchGlobal('GL.eliminateSpaceInSelfClosingTag', 'no_spaces_in_closed_tag'))
		menu_config_printmode.add_checkbutton(label=GL.names['menu_config_printmode_linefyatsave'],
											  variable= mainApp.bool_menu_config_linefyAtSave,
											  command= lambda: mSwitchGlobal('GL.linefyAtSave', 'no_spaces_in_closed_tag'))

		#menu de búsqueda
		menu_config_search = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_search'], menu=menu_config_search)
		menu_config_search.add_checkbutton(label=GL.names['menu_config_search_caseSensitive'],
										   variable=mainApp.bool_menu_config_caseSensitive,
										   command= lambda: mSwitchGlobal('GL.caseSensitiveSearch', 'case_sensitive'))

		#menu otros
		menu_config_others = Menu(menubar, tearoff=0)
		menu_config.add_cascade(label=GL.names['menu_config_others'], menu=menu_config_others)
		menu_config_others.add_checkbutton(label=GL.names['menu_config_others_SQLButtons'],
										   variable=mainApp.bool_menu_config_others_SQLButtons,
										   command= lambda: mSwitchGlobal('GL.useSQLButtons', 'use_SQL_buttons'))
		menu_config_others.add_checkbutton(label=GL.names['menu_config_others_ShowFileFullPath'],
										   variable=mainApp.bool_menu_config_others_showFileFullPath,
										   command= lambda: mChangeFilenameLabel(mainApp.frames.menu.dic['label_filename']))


def fillButtonBarFrame(mainApp):
	#mainApp = xFrame.master
	xFrame = mainApp.frames.menu
	lExcludeMenu = mainApp.excludeList

	if not 'label_filename' in lExcludeMenu:
		label_filename = xFrame.addWidget('Label', 'label_filename')
		label_filename.configure(padding=(10,0,0,0))
		label_filename.grid(row=0, column=4, columnspan=2)

	getButton(xFrame, 'button_newFromText', lExcludeMenu, 0, 0, command = lambda: openXMLFromText(mainApp))
	getButton(xFrame, 'button_open', lExcludeMenu, 0, 1, command = lambda: openXML(mainApp))
	getButton(xFrame, 'button_save', lExcludeMenu, 0, 2, command = lambda: saveXML(mainApp, 'SAVE'))
	getButton(xFrame, 'button_saveAs', lExcludeMenu, 0, 3, command = lambda: saveXML(mainApp, 'SAVEAS'))
	getButton(xFrame, 'button_newTag', lExcludeMenu, 1, 0, command= lambda: createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'SIBLING'))
	getButton(xFrame, 'button_newChildTag', lExcludeMenu, 1, 1, command= lambda: createNewTagInTree(mainApp, GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 'CHILD'))
	getButton(xFrame, 'button_copyTag', lExcludeMenu, 1, 2, command = lambda: copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
	getButton(xFrame, 'button_deleteTag', lExcludeMenu, 1, 3, command = lambda: deleteSelectionTagInTree( GL.appTreeView.selection() ))

	## debug buttons
	getButton(xFrame, 'button_glTreeView', lExcludeMenu, 1, 1, command = lambda: checkTreeView())
	getButton(xFrame, 'button_analyze', lExcludeMenu, 0, 1, command = lambda: bCheckEntries(mainApp.frames.buttons))
	getButton(xFrame, 'button_dicSubnames', lExcludeMenu, 1, 3, command = lambda: bShowGuts(GL.dicTagSubnames))
	getButton(xFrame, 'button_getDicSubnames', lExcludeMenu, 1, 3, command = lambda: GL.getDicSubnames())
	#getButton(xFrame, 'button_printEncoding', lExcludeMenu, 1, 2, command = lambda: xml_man.getEncoding(GL.filename))
	getButton(xFrame, 'button_printEncoding', lExcludeMenu, 1, 2, command = lambda: bShowGuts(GL.XMLEncoding))
	getButton(xFrame, 'button_printPrettyPrint', lExcludeMenu, 2, 1, command = lambda: bShowGuts(GL.defaultPrettyPrint))
	getButton(xFrame, 'button_showCurrentSearch', lExcludeMenu, 2, 2, command = lambda: bShowGuts(mainApp.currentSearch))
	getButton(xFrame, 'button_showDicTagsInTree', lExcludeMenu, 2, 1, command = lambda: bShowGuts(GL.dicTagsInTree))
	getButton(xFrame, 'button_showXMLParentMap', lExcludeMenu, 2, 2, command = lambda: bShowGuts(GL.XMLParentMap))
	getButton(xFrame, 'button_showCaseSensitive', lExcludeMenu, 2, 2, command = lambda: bShowGuts(GL.caseSensitiveSearch))
	getButton(xFrame, 'button_captureStringXML', lExcludeMenu, 2, 2, command = lambda: printStringXML(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None)))
	getButton(xFrame, 'button_showSearchResult', lExcludeMenu, 2, 2, command = lambda: bShowGuts(mainApp.currentSearch.result))
	getButton(xFrame, 'button_showSearchStartingPoint', lExcludeMenu, 2, 3, command = lambda: bShowGuts(mainApp.currentSearch.startingPoint))
	getButton(xFrame, 'button_lastFolder', lExcludeMenu, 2, 2, command = lambda: bShowGuts(mainApp.temp.getValue('lastVisitedFolder')))
	getButton(xFrame, 'button_foldTest', lExcludeMenu, 2, 2, command = lambda: bFoldNode(GL.appTreeView.focus()))
	#getButton(xFrame, 'button_newFromText', lExcludeMenu, 2, 2, command = lambda: openXMLFromText(mainApp))
	getButton(xFrame, 'button_showChildQty', lExcludeMenu, 2, 1, command = lambda: bShowGuts(GL.dicTagsInTree[GL.appTreeView.focus()].getNumberOfChildren()))

	#campos para busqueda
	frame_search = xFrame.addWidget('LabelFrame', 'frame_search')
	frame_search.configure(text=GL.names['frame_search'])
	frame_search.grid(row=1, column=4, sticky='wn')

	searchOptions = (GL.names['option_tags'], GL.names['option_values'], GL.names['option_xpath'])
	optionmenu_search = OptionMenu(frame_search, mainApp.string_optionmenu_search, searchOptions[0], *searchOptions)
	optionmenu_search.configure(width= GL.buttonWidth)
	optionmenu_search.grid(row=0, column=0, sticky='wn')

	entry_search = Entry(frame_search)
	entry_search.configure(width= GL.labelButtonWidth) #, validate='focus', validatecommand= lambda: printEntrySearch(entry_search))
	entry_search.grid(row=0, column=1, sticky='wn')
	entry_search.bind('<Return>', lambda event: basicSearch(mainApp, entry_search.get(), GL.appTreeView.focus() ))


def basicSearch(mainApp, searchString, xIDFocus):
	if searchString <> '':
		if (mainApp.currentSearch == None) or (mainApp.currentSearch.searchString <> searchString):
			try:
				xStartingPoint = GL.dicTagsInTree[xIDFocus].tag_order
			except:
				xStartingPoint = 0
			mainApp.currentSearch = BasicSearch(searchString, GL.dicTagsInTree, mainApp.string_optionmenu_search.get(), xStartingPoint)

		nextFocus = mainApp.currentSearch.output.next()
		if nextFocus == '':
			tkMessageBox.showinfo("eXMLorer", GL.names['message_nofinds'])
		else:
			selectAndFocus(nextFocus)


def fillFooterFrame(mainApp):
	xFrame = mainApp.frames.footer
	lExcludeMenu = mainApp.excludeList

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
	if not 'label_encoding' in lExcludeMenu:
		label_encoding = xFrame.addWidget('Label', 'label_encoding')
		label_encoding.configure(padding=(10,0,0,0))
		label_encoding.grid(row=0, column=5, sticky='e')
		#label_encoding.config(text='test')

def getButton(xMaster, name, lExcludeMenu, xRow, xColumn, command=''):
	if not name in lExcludeMenu:
		xButton = xMaster.addWidget('Button', name)
		xButton.configure(text= GL.names[name], width= GL.buttonWidth, command=command)
		xButton.grid(column=xColumn, row=xRow)

def getFilename(oTemp):
	#filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')], initialdir=GL.lastFolderVisited)
	#print filename
	#GL.lastFolderVisited = filename[:filename.rfind('\\')]

	filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')], initialdir=oTemp.getValue('lastVisitedFolder'))
	print "FILENAME"
	print filename
	print type(filename)
	if not isinstance(filename, tuple):
		oTemp.setValue('lastVisitedFolder', filename[:filename.rfind('\\')])
		return filename
	else:
		return ''

def getIDForTreeView(xTag, dicTagsInTree):
	i = 0
	while dicTagsInTree.has_key(xTag + str(i)):
		i += 1
	dicTagsInTree[xTag + str(i)] = 0
	return xTag + str(i)

def addXMLToTree(xBase, xBaseID, dicTagsInTree, appTreeView):
	for xChild in xBase:
		if xChild.tag is ET.Comment:
			print "IS COMMENT"
			if GL.showComments:
				xID = getIDForTreeView('comment', dicTagsInTree)
				dicTagsInTree[xID] = TIG.TagInTree(xBaseID, xID, xChild, xBase, appTreeView, is_comment=True)

		if type(xChild.tag).__name__ == 'str':
			xID = getIDForTreeView(xChild.tag, dicTagsInTree)
			dicTagsInTree[xID] = TIG.TagInTree(xBaseID, xID, xChild, xBase, appTreeView)
			addXMLToTree(xChild, xID, dicTagsInTree, appTreeView)

def askSaveChanges(mainApp):
	#print xml_man.fileHasChanged(mainApp.rootTIG.getTag(), GL.filename)
	#tkMessageBox.showerror('eXMLorer', 'Está saliendo del eXMLorer. Que tenga un buen día :)')
	if mainApp.rootTIG == None:
		response = 'no'
	elif not os.path.isfile(GL.filename):
		response = tkMessageBox.showwarning("eXMLorer", GL.names['message_filenotfound'] % GL.filename, type=tkMessageBox.YESNOCANCEL)
	elif xml_man.fileHasChanged(mainApp.rootTIG.getTag(), GL.filename):
		response = tkMessageBox.showwarning("eXMLorer", GL.names['message_exitsave'] % GL.filename, type=tkMessageBox.YESNOCANCEL)
	else:
		response = 'no'

	####################
	if response == 'yes':
		saveXML(mainApp, 'SAVE')
		return True
	elif response == 'cancel':
		return False
	elif response == 'no':
		return True


def quitApp(mainApp):
	if askSaveChanges(mainApp):
		mainApp.destroy()


# BUTTON METHODS

def openXML(mainApp, filename=''):
	if askSaveChanges(mainApp):
		label_filename = mainApp.frames.menu.dic['label_filename']
		label_encoding = mainApp.frames.footer.dic['label_encoding']
		if filename=='':
			filename = getFilename(mainApp.temp)

		if filename <> '':
			mainApp.frames.treeview.clean()
			mainApp.frames.buttons.clean()
			GL.filename = filename
			#label_filename.config(text= GL.filename)
			setFilenameLabel(label_filename)

			root = xml_man.getXML(GL.filename)
			#root = xml_man.getXML('stylers.xml')

			if root == None:
				tkMessageBox.showerror('eXMLorer', GL.names['message_nonvalidxml'] % GL.filename)
				label_filename.config(text= '')
			else:
				GL.dicTagsInTree = {}
				GL.appTreeView = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons, GL.dicTagsInTree)

				GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
				mainApp.rootTIG = GL.dicTagsInTree[root.tag]
				addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
				
				label_encoding.config(text = GL.XMLEncoding)


def openXMLFromText(mainApp, stringXML=''):
	def getStringXMLFromUser(mainApp):
		container = {}
		label = GL.names['message_newxmlstring']
		title = GL.names['message_newxml']
		xWindow = mainApp.getToplevel2(title, container, useSQLButtons=False)
		xWindow.textFieldConstructor(label, '')
		xWindow.show()

		if len(container) > 0:
			return container[label]
		else:
			return ''


	label_filename = mainApp.frames.menu.dic['label_filename']
	label_encoding = mainApp.frames.footer.dic['label_encoding']

	if askSaveChanges(mainApp):
		mainApp.frames.treeview.clean()
		mainApp.frames.buttons.clean()

		#stringXML = '<main><cosa>a</cosa></main>'
		stringXML = getStringXMLFromUser(mainApp)

		if stringXML <> '':
			try:
				encodedStringXML = stringXML.encode('utf-8')
				root = xml_man.parseStringXML(encodedStringXML)
				#print 'root', root
			except Exception as e:
				root = None
				print e
				
			if root == None:
				tkMessageBox.showerror('eXMLorer', GL.names['message_nonvalidxmlstring'])
				label_filename.config(text= '')
			else:
				GL.dicTagsInTree = {}
				GL.appTreeView = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons, GL.dicTagsInTree)

				GL.dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, None, GL.appTreeView)
				mainApp.rootTIG = GL.dicTagsInTree[root.tag]
				addXMLToTree(root, root.tag, GL.dicTagsInTree, GL.appTreeView)
				
				label_encoding.config(text = GL.XMLEncoding)


def saveXML(mainApp, modo):
	try:
		if modo == 'SAVEAS':
			save_filename = tkFileDialog.asksaveasfilename( filetypes=[(GL.names['saveas_filetype_xml'], '.xml'), (GL.names['saveas_filetype_all'], '.*')],
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
			#mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
			setFilenameLabel(mainApp.frames.menu.dic['label_filename'])
	except Exception, e:
		tkMessageBox.showerror('eXMLorer', GL.names['message_savingerror'] % e)


def createNewTagInTree(mainApp, baseTIG, mode, oTag=None, is_comment=False, text=''):
	if baseTIG <> None:
		if baseTIG.parent_id <> '':
			#consigo datos para nuevo tag
			xTag = ''
			if is_comment:
				xTag = 'comment'
				stringXML = xml_man.getStringXML(baseTIG.getTag())
				xText = stringXML[ stringXML.find('\n')+1:]
			elif text <> '':
				xTag = getTagFromUser(mainApp)
				xText = text
			elif oTag == None:
				xTag, xText = getTagFromUser(mainApp, getValue=True)

			if (xTag <> '') or (oTag <> None):
				xAttrib = {}
				#consigo datos para crear el TagInTree
				if mode == 'SIBLING':
					xBaseID = baseTIG.parent_id
					xParentTag = baseTIG.parent_tag
					xOrder = baseTIG.getTreeViewIndex() + 1
				elif mode == 'CHILD':
					xBaseID = baseTIG.id
					xParentTag = baseTIG.getTag()
					#xOrder = baseTIG.getNumberOfSiblings() + 1
					xOrder = baseTIG.getNumberOfChildren() + 1
					print 'parenttag in newTIG', xParentTag, xParentTag.tag, xOrder

				#creo o inserto el tag en el XML
				if is_comment:
					xNewTag = xml_man.newComment(xParentTag, xText, xOrder)
				elif oTag == None:
					xNewTag = xml_man.newElement(xParentTag, xTag, xText, xAttrib, xOrder)
				else:
					#if mode == 'SIBLING':
					xml_man.insertElement(xParentTag, oTag, xOrder)
					xNewTag = oTag

				#creo el newTagInTree
				if is_comment:
					xID = getIDForTreeView( 'comment', GL.dicTagsInTree)
					newTagInTree = TIG.TagInTree(xBaseID, xID, xNewTag, xParentTag, GL.appTreeView, order = xOrder, is_comment=True)
				else:
					xID = getIDForTreeView( xNewTag.tag, GL.dicTagsInTree)
					newTagInTree = TIG.TagInTree(xBaseID, xID, xNewTag, xParentTag, GL.appTreeView, order = xOrder)

				GL.dicTagsInTree[xID] = newTagInTree
				selectAndFocus(xID)
				print 'newTagInTree'
				return newTagInTree

def getTagFromUser(mainApp, getValue=False):
	container = {}
	xWindow = mainApp.getToplevel2(GL.names['message_newtag'], container)
	xWindow.formConstructor('Tag', 0)
	if getValue:
		xWindow.formConstructor('Value', 1)
	xWindow.show()

	if len(container) > 0:
		if getValue:
			return container['Tag'], container['Value']
		else:
			return container['Tag']
	else:
		if getValue:
			return '', ''
		else:
			return ''


def copyTagInTree(oldTagInTree, xLevel, newparent = None):
	if oldTagInTree <> None:
		if newparent == None:
			xParentID = oldTagInTree.parent_id
			xParentTag = oldTagInTree.parent_tag
		else:
			xParentID = newparent.id
			xParentTag = newparent.getTag()

		xOrder = oldTagInTree.getTreeViewIndex() + 1

		xNewTag = xml_man.newElement( xParentTag,
									  oldTagInTree.getTag().tag,
									  oldTagInTree.getTag().text,
									  oldTagInTree.getTag().attrib,
									  xOrder)

		xID = getIDForTreeView( xNewTag.tag, GL.dicTagsInTree)

		newTagInTree = TIG.TagInTree(xParentID, xID, xNewTag, xParentTag, GL.appTreeView, order = xOrder)
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

		selectAndFocus(xID)

	else:
		print 'oldTagInTree is None'

def deleteSelectionTagInTree(selection):
	for xID in selection:
		deleteTagInTree(xID)

def deleteTagInTree(xID):
	if xID <> '':
		xTagInTree = GL.dicTagsInTree[xID]
		xTagInTree.parent_tag.remove( xTagInTree.getTag() )
		if GL.appTreeView.exists(xTagInTree.id):
			GL.appTreeView.delete( xTagInTree.id )
		del GL.dicTagsInTree[xID]
		del xTagInTree
		print 'Deleted %s' % xID


def checkTreeView():
	if GL.appTreeView == None:
		print 'TreeView does not exist'
	else:
		print 'TreeView is A-OK!'


def bCheckEntries(band_buttons):
	for widget in band_buttons.winfo_children():
		if isinstance(widget, Entry):
			print widget.get()

def printStringXML(oTIG):
	if oTIG <> None:
		stringXML = xml_man.getStringXML(oTIG.getTag())
		print stringXML[ stringXML.find('\n')+1:]
	else:
		print 'None selected'

def setFilenameLabel(label_filename):
	print "setFilenameLabel"
	if GL.showFileFullPath:
		label_filename.config(text=GL.filename)
	else:
		label_filename.config(text=GL.filename[GL.filename.rfind('\\')+1:])

def bFoldNode(idNode):
	GL.appTreeView.item(idNode, open=False)

def bShowGuts(thing):
	print thing


# MENU METHODS

def mChangeLang(mainApp, newLang):
	print 'changing language'
	if newLang == 'ENG':
		dicLang = LANG.english
		mainApp.bool_menu_config_lang_eng.set(True)
		mainApp.bool_menu_config_lang_spa.set(False)

	elif newLang == 'SPA':
		dicLang = LANG.spanish
		mainApp.bool_menu_config_lang_eng.set(False)
		mainApp.bool_menu_config_lang_spa.set(True)

	else:
		return

	if dicLang['lang'] <> GL.names['lang']:
		GL.names = dicLang
		GL.updateConfigFile('Configuration', 'language', dicLang['lang'])
		refreshApp(mainApp)

def mChangeFilenameLabel(label_filename):
	mSwitchGlobal('GL.showFileFullPath', 'showFileFullPath')
	setFilenameLabel(label_filename)

def mSwitchGlobal(varName, varConfigName, refreshTree=False):
	if eval(varName) == True:
		exec('%s = False' % varName)
		GL.updateConfigFile('Configuration', varConfigName, 'False')
	else:
		exec('%s = True' % varName)
		GL.updateConfigFile('Configuration', varConfigName, 'True')

	if refreshTree:
		refreshTreeview(GL.appTreeView.master.master.master)
		#la manera mas sencilla de traer el mainApp sin cambiar todo
		#esto es porque el objeto es mainApp.center(frame).treeview(frame).treeview(mi appTreeView)

#####################

if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

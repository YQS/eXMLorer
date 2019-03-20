# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
import xml.etree.ElementTree as ElementTree
import os.path

from config import Globals, Language, Utils
import TagInTree
from xml_parser import XmlParser
import tk_treeview
from FrameExtension import FrameExtension
from search_man import BasicSearch
from TempData import TempData
from AuxWindow import AuxWindow
from AppMenu import AppMenu


# CLASSES

class FramePack(object):
    def __init__(self, master):
        self.menu = FrameExtension(master)
        self.center = FrameExtension(master)
        self.footer = FrameExtension(master)

        self.treeview = FrameExtension(self.center)
        self.buttons = FrameExtension(self.center)


class App(Tk):
    def __init__(self, icon_path='test.gif', exclude_buttons=None):
        Tk.__init__(self)
        if exclude_buttons is None:
            exclude_buttons = []
        self.title('eXMLorer')

        # elementos del main
        self.exclude_buttons = exclude_buttons
        self.root = None
        self.menubar = None
        self.current_search = None
        self.icon_path = icon_path
        self.iconImage = None
        self.temp = TempData(Globals.temp_data_file)
        self.string_optionmenu_search = StringVar()

        self.bool_menu_config_lang_eng = BooleanVar()
        self.bool_menu_config_lang_spa = BooleanVar()
        self.bool_menu_config_prettyprint = BooleanVar()
        self.bool_menu_config_noSpaceInSelfClosingTag = BooleanVar()
        self.bool_menu_config_linefyAtSave = BooleanVar()
        self.bool_menu_config_caseSensitive = BooleanVar()
        self.bool_menu_config_others_SQLButtons = BooleanVar()
        self.bool_menu_config_others_showFileFullPath = BooleanVar()
        self.bool_menu_config_showComments = BooleanVar()

        self.init_menu_bools()

        self.load_icon()

        # captura de cierre del programa
        self.protocol('WM_DELETE_WINDOW', lambda: quitApp(self))

        # frames
        self.frames = FramePack(self)
        self.load_frames()

        # binds
        self.bind('<F5>', lambda event: refreshTreeview(self))

    # metodos del MainApp
    def get_aux_window(self, title, container, use_sql_buttons=True):
        return AuxWindow(self, title, container, use_sql_buttons)

    def init_menu_bools(self):
        if Globals.lang['lang'] == 'Español':
            self.bool_menu_config_lang_spa.set(True)
        else:
            self.bool_menu_config_lang_eng.set(True)

        if Globals.pretty_print:
            self.bool_menu_config_prettyprint.set(True)
        if Globals.no_spaces_in_closed_tag:
            self.bool_menu_config_noSpaceInSelfClosingTag.set(True)
        if Globals.linefy_at_save:
            self.bool_menu_config_linefyAtSave.set(True)
        if Globals.case_sensitive_search:
            self.bool_menu_config_caseSensitive.set(True)
        if Globals.use_sql_buttons:
            self.bool_menu_config_others_SQLButtons.set(True)
        if Globals.show_file_full_path:
            self.bool_menu_config_others_showFileFullPath.set(True)
        if Globals.show_comments:
            self.bool_menu_config_showComments.set(True)

    def load_icon(self):
        try:
            self.iconImage = PhotoImage(file=self.icon_path)
            self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
        except TclError:
            print 'No se encontro el archivo de icono %s' % self.icon_path

    def load_frames(self):
        self.frames.menu.pack(side=TOP, fill=X)
        self.frames.center.pack(side=TOP, fill=BOTH, expand=True)
        self.frames.treeview.pack(side=LEFT, fill=BOTH)
        self.frames.buttons.pack(side=LEFT, fill=BOTH, expand=True, ipadx=0, pady=20)
        self.frames.footer.pack(side=BOTTOM, fill=X)

        self.menubar = AppMenu(self)
        fillButtonBarFrame(self)  # botones debajo del menu
        fillFooterFrame(self)

    @staticmethod
    def set_scrollbar(parent, widget):
        scrollbar = Scrollbar(parent, command=widget.yview)
        widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def refresh(self):
        for i in range(0, 50):  # TODO: habría que ver si se puede hacer esto más eficiente
            try:
                self.menubar.delete(i)
            except:
                break
        self.frames.menu.clean()
        self.frames.footer.clean()
        self.frames.treeview.clean()
        self.frames.buttons.clean()

        # fill bars
        self.menubar = AppMenu(self)
        fillButtonBarFrame(self)
        fillFooterFrame(self)

        # mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
        setFilenameLabel(self.frames.menu.dic['label_filename'])

        refreshTreeview(self)


# METHODS



def fillButtonBarFrame(mainApp):
    # mainApp = xFrame.master
    xFrame = mainApp.frames.menu
    lExcludeMenu = mainApp.exclude_buttons

    if not 'label_filename' in lExcludeMenu:
        label_filename = xFrame.add_widget('Label', 'label_filename')
        label_filename.configure(padding=(10, 0, 0, 0))
        label_filename.grid(row=0, column=4, columnspan=2)

    getButton(xFrame, 'button_newFromText', lExcludeMenu, 0, 0, command=lambda: openXMLFromText(mainApp))
    getButton(xFrame, 'button_open', lExcludeMenu, 0, 1, command=lambda: openXML(mainApp))
    getButton(xFrame, 'button_save', lExcludeMenu, 0, 2, command=lambda: saveXML(mainApp, 'SAVE'))
    getButton(xFrame, 'button_saveAs', lExcludeMenu, 0, 3, command=lambda: saveXML(mainApp, 'SAVEAS'))
    getButton(xFrame, 'button_newTag', lExcludeMenu, 1, 0, command=lambda: createNewTagInTree(mainApp,
                                                                                              Globals.tags_in_tree_dictionary.setdefault(
                                                                                                  Globals.app_treeview.focus(),
                                                                                                  None), 'SIBLING'))
    getButton(xFrame, 'button_newChildTag', lExcludeMenu, 1, 1, command=lambda: createNewTagInTree(mainApp,
                                                                                                   Globals.tags_in_tree_dictionary.setdefault(
                                                                                                       Globals.app_treeview.focus(),
                                                                                                       None), 'CHILD'))
    getButton(xFrame, 'button_copyTag', lExcludeMenu, 1, 2,
              command=lambda: copyTagInTree(
                  Globals.tags_in_tree_dictionary.setdefault(Globals.app_treeview.focus(), None), 0))
    getButton(xFrame, 'button_deleteTag', lExcludeMenu, 1, 3,
              command=lambda: deleteSelectionTagInTree(Globals.app_treeview.selection()))

    ## debug buttons
    getButton(xFrame, 'button_glTreeView', lExcludeMenu, 1, 1, command=lambda: checkTreeView())
    getButton(xFrame, 'button_analyze', lExcludeMenu, 0, 1, command=lambda: bCheckEntries(mainApp.frames.buttons))
    getButton(xFrame, 'button_dicSubnames', lExcludeMenu, 1, 3, command=lambda: bShowGuts(Globals.tag_subnames))
    getButton(xFrame, 'button_getDicSubnames', lExcludeMenu, 1, 3, command=lambda: Globals.getDicSubnames())
    # getButton(xFrame, 'button_printEncoding', lExcludeMenu, 1, 2, command = lambda: xml_man.get_encoding(GL.filename))
    getButton(xFrame, 'button_printEncoding', lExcludeMenu, 1, 2, command=lambda: bShowGuts(Globals.xml_encoding))
    getButton(xFrame, 'button_printPrettyPrint', lExcludeMenu, 2, 1, command=lambda: bShowGuts(Globals.pretty_print))
    getButton(xFrame, 'button_showCurrentSearch', lExcludeMenu, 2, 2, command=lambda: bShowGuts(mainApp.currentSearch))
    getButton(xFrame, 'button_showDicTagsInTree', lExcludeMenu, 2, 1,
              command=lambda: bShowGuts(Globals.tags_in_tree_dictionary))
    getButton(xFrame, 'button_showXMLParentMap', lExcludeMenu, 2, 2, command=lambda: bShowGuts(Globals.XMLParentMap))
    getButton(xFrame, 'button_showCaseSensitive', lExcludeMenu, 2, 2,
              command=lambda: bShowGuts(Globals.case_sensitive_search))
    getButton(xFrame, 'button_captureStringXML', lExcludeMenu, 2, 2,
              command=lambda: printStringXML(
                  Globals.tags_in_tree_dictionary.setdefault(Globals.app_treeview.focus(), None)))
    getButton(xFrame, 'button_showSearchResult', lExcludeMenu, 2, 2,
              command=lambda: bShowGuts(mainApp.currentSearch.result))
    getButton(xFrame, 'button_showSearchStartingPoint', lExcludeMenu, 2, 3,
              command=lambda: bShowGuts(mainApp.currentSearch.startingPoint))
    getButton(xFrame, 'button_lastFolder', lExcludeMenu, 2, 2,
              command=lambda: bShowGuts(mainApp.temp.getValue('lastVisitedFolder')))
    getButton(xFrame, 'button_foldTest', lExcludeMenu, 2, 2, command=lambda: bFoldNode(Globals.app_treeview.focus()))
    # getButton(xFrame, 'button_newFromText', lExcludeMenu, 2, 2, command = lambda: openXMLFromText(mainApp))
    getButton(xFrame, 'button_showChildQty', lExcludeMenu, 2, 1,
              command=lambda: bShowGuts(
                  Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getNumberOfChildren()))

    # campos para busqueda
    frame_search = xFrame.add_widget('LabelFrame', 'frame_search')
    frame_search.configure(text=Globals.lang['frame_search'])
    frame_search.grid(row=1, column=4, sticky='wn')

    searchOptions = (Globals.lang['option_tags'], Globals.lang['option_values'], Globals.lang['option_xpath'])
    optionmenu_search = OptionMenu(frame_search, mainApp.string_optionmenu_search, searchOptions[0], *searchOptions)
    optionmenu_search.configure(width=Globals.button_width)
    optionmenu_search.grid(row=0, column=0, sticky='wn')

    entry_search = Entry(frame_search)
    entry_search.configure(
        width=Globals.label_button_width)  # , validate='focus', validatecommand= lambda: printEntrySearch(entry_search))
    entry_search.grid(row=0, column=1, sticky='wn')
    entry_search.bind('<Return>', lambda event: basicSearch(mainApp, entry_search.get(), Globals.app_treeview.focus()))


def basicSearch(mainApp, searchString, xIDFocus):
    if searchString <> '':
        if (mainApp.currentSearch == None) or (mainApp.currentSearch.searchString <> searchString):
            try:
                xStartingPoint = Globals.tags_in_tree_dictionary[xIDFocus].tag_order
            except:
                xStartingPoint = 0
            mainApp.currentSearch = BasicSearch(searchString, Globals.tags_in_tree_dictionary,
                                                mainApp.string_optionmenu_search.get(), xStartingPoint)

        nextFocus = mainApp.currentSearch.output.next()
        if nextFocus == '':
            tkMessageBox.showinfo("eXMLorer", Globals.lang['message_nofinds'])
        else:
            selectAndFocus(nextFocus)


def fillFooterFrame(mainApp):
    xFrame = mainApp.frames.footer
    lExcludeMenu = mainApp.exclude_buttons

    getButton(xFrame, 'button_moveUp', lExcludeMenu, 0, 1, command=lambda: tk_treeview.moveNode(
        Globals.app_treeview.focus(),
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getParent().id,
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getTreeViewIndex() - 1,
        Globals.tags_in_tree_dictionary))

    getButton(xFrame, 'button_moveDown', lExcludeMenu, 0, 2, command=lambda: tk_treeview.moveNode(
        Globals.app_treeview.focus(),
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getParent().id,
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getTreeViewIndex() + 1,
        Globals.tags_in_tree_dictionary))

    getButton(xFrame, 'button_moveBeginnnig', lExcludeMenu, 0, 3, command=lambda: tk_treeview.moveNode(
        Globals.app_treeview.focus(),
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getParent().id,
        0,
        Globals.tags_in_tree_dictionary))

    getButton(xFrame, 'button_moveEnd', lExcludeMenu, 0, 4, command=lambda: tk_treeview.moveNode(
        Globals.app_treeview.focus(),
        Globals.tags_in_tree_dictionary[Globals.app_treeview.focus()].getParent().id,
        'end',
        Globals.tags_in_tree_dictionary))
    if not 'label_encoding' in lExcludeMenu:
        label_encoding = xFrame.add_widget('Label', 'label_encoding')
        label_encoding.configure(padding=(10, 0, 0, 0))
        label_encoding.grid(row=0, column=5, sticky='e')
    # label_encoding.config(text='test')


def getButton(xMaster, name, lExcludeMenu, xRow, xColumn, command=''):
    if not name in lExcludeMenu:
        xButton = xMaster.add_widget('Button', name)
        xButton.configure(text=Globals.lang[name], width=Globals.button_width, command=command)
        xButton.grid(column=xColumn, row=xRow)


def getFilename(oTemp):
    # filename = tkFileDialog.askopenfilename(defaultextension='.xml', filetypes = [('XML files', '.xml'), ('all files', '.*')], initialdir=GL.lastFolderVisited)
    # print filename
    # GL.lastFolderVisited = filename[:filename.rfind('\\')]

    filename = tkFileDialog.askopenfilename(defaultextension='.xml',
                                            filetypes=[('XML files', '.xml'), ('all files', '.*')],
                                            initialdir=oTemp.getValue('lastVisitedFolder'))
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
        if xChild.tag is ElementTree.Comment:
            print "IS COMMENT"
            if Globals.show_comments:
                xID = getIDForTreeView('comment', dicTagsInTree)
                dicTagsInTree[xID] = TagInTree.TagInTree(xBaseID, xID, xChild, xBase, appTreeView, is_comment=True)

        if type(xChild.tag).__name__ == 'str':
            xID = getIDForTreeView(xChild.tag, dicTagsInTree)
            dicTagsInTree[xID] = TagInTree.TagInTree(xBaseID, xID, xChild, xBase, appTreeView)
            addXMLToTree(xChild, xID, dicTagsInTree, appTreeView)


def askSaveChanges(mainApp):
    # print xml_man.file_has_changed(mainApp.rootTIG.getTag(), GL.filename)
    # tkMessageBox.showerror('eXMLorer', 'Está saliendo del eXMLorer. Que tenga un buen día :)')
    saveType = 'SAVE'
    if mainApp.root == None:
        response = 'no'
    elif Globals.config_filename == '':
        response = tkMessageBox.showwarning("eXMLorer", Globals.lang['message_filenotdefined'],
                                            type=tkMessageBox.YESNOCANCEL)
        if response == 'yes':
            saveType = 'SAVEAS'
    elif not os.path.isfile(Globals.config_filename):
        response = tkMessageBox.showwarning("eXMLorer", Globals.lang['message_filenotfound'] % Globals.config_filename,
                                            type=tkMessageBox.YESNOCANCEL)
    elif XmlParser.file_has_changed(mainApp.root.getTag(), Globals.config_filename):
        response = tkMessageBox.showwarning("eXMLorer", Globals.lang['message_exitsave'] % Globals.config_filename,
                                            type=tkMessageBox.YESNOCANCEL)
    else:
        response = 'no'

    ####################
    if response == 'yes':
        saveXML(mainApp, saveType)
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
        if filename == '':
            filename = getFilename(mainApp.temp)

        if filename <> '':
            mainApp.frames.treeview.clean()
            mainApp.frames.buttons.clean()
            Globals.config_filename = filename
            # label_filename.config(text= GL.filename)
            setFilenameLabel(label_filename)

            root = XmlParser.get_xml_root(Globals.config_filename)
            # root = xml_man.get_xml_root('stylers.xml')

            if root == None:
                tkMessageBox.showerror('eXMLorer', Globals.lang['message_nonvalidxml'] % Globals.config_filename)
                label_filename.config(text='')
            else:
                Globals.tags_in_tree_dictionary = {}
                Globals.app_treeview = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons,
                                                               Globals.tags_in_tree_dictionary)

                Globals.tags_in_tree_dictionary[root.tag] = TagInTree.TagInTree('', root.tag, root, None,
                                                                                Globals.app_treeview)
                mainApp.root = Globals.tags_in_tree_dictionary[root.tag]
                addXMLToTree(root, root.tag, Globals.tags_in_tree_dictionary, Globals.app_treeview)

                label_encoding.config(text=Globals.xml_encoding)


def openXMLFromText(mainApp, stringXML=''):
    def getStringXMLFromUser(mainApp):
        container = {}
        label = Globals.lang['message_newxmlstring']
        title = Globals.lang['message_newxml']
        xWindow = mainApp.get_aux_window(title, container, use_sql_buttons=False)
        xWindow.text_field_constructor(label, '')
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

        # stringXML = '<main><cosa>a</cosa></main>'
        stringXML = getStringXMLFromUser(mainApp)

        if stringXML <> '':
            try:
                encodedStringXML = stringXML.encode('utf-8')
                root = XmlParser.get_xml_root_from_string(encodedStringXML)
            # print 'root', root
            except Exception as e:
                root = None
                print e

            if root == None:
                tkMessageBox.showerror('eXMLorer', Globals.lang['message_nonvalidxmlstring'])
                label_filename.config(text='')
            else:
                Globals.tags_in_tree_dictionary = {}
                Globals.app_treeview = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons,
                                                               Globals.tags_in_tree_dictionary)

                Globals.tags_in_tree_dictionary[root.tag] = TagInTree.TagInTree('', root.tag, root, None,
                                                                                Globals.app_treeview)
                mainApp.root = Globals.tags_in_tree_dictionary[root.tag]
                addXMLToTree(root, root.tag, Globals.tags_in_tree_dictionary, Globals.app_treeview)

                label_encoding.config(text=Globals.xml_encoding)


def saveXML(mainApp, modo):
    try:
        if modo == 'SAVEAS':
            save_filename = tkFileDialog.asksaveasfilename(
                filetypes=[(Globals.lang['saveas_filetype_xml'], '.xml'), (Globals.lang['saveas_filetype_all'], '.*')],
                initialfile=Globals.config_filename,
                parent=mainApp)
        else:
            save_filename = Globals.config_filename

        if save_filename:
            # print 'saving in ' + save_filename
            # GL.XMLTree.write(save_filename)
            print save_filename[-4:]
            if save_filename[-4:] <> '.xml':
                save_filename += '.xml'
            XmlParser.save_xml(Globals.xml_tree, save_filename)
            Globals.config_filename = save_filename
            # mainApp.frames.menu.dic['label_filename'].config(text= GL.filename)
            setFilenameLabel(mainApp.frames.menu.dic['label_filename'])
    except Exception, e:
        tkMessageBox.showerror('eXMLorer', Globals.lang['message_savingerror'] % e)


def createNewTagInTree(mainApp, baseTIG, mode, oTag=None, is_comment=False, text=''):
    if baseTIG <> None:
        if baseTIG.parent_id <> '':
            # consigo datos para nuevo tag
            xTag = ''
            if is_comment:
                xTag = 'comment'
                stringXML = XmlParser.get_string_from_xml_node(baseTIG.getTag())
                xText = stringXML[stringXML.find('\n') + 1:]
            elif text <> '':
                xTag = getTagFromUser(mainApp)
                xText = text
            elif oTag == None:
                xTag, xText = getTagFromUser(mainApp, getValue=True)

            if (xTag <> '') or (oTag <> None):
                xAttrib = {}
                # consigo datos para crear el TagInTree
                if mode == 'SIBLING':
                    xBaseID = baseTIG.parent_id
                    xParentTag = baseTIG.parent_tag
                    xOrder = baseTIG.getTreeViewIndex() + 1
                elif mode == 'CHILD':
                    xBaseID = baseTIG.id
                    xParentTag = baseTIG.getTag()
                    # xOrder = baseTIG.getNumberOfSiblings() + 1
                    xOrder = baseTIG.getNumberOfChildren() + 1
                    print 'parenttag in newTIG', xParentTag, xParentTag.tag, xOrder

                # creo o inserto el tag en el XML
                if is_comment:
                    xNewTag = XmlParser.new_comment(xParentTag, xText, xOrder)
                elif oTag == None:
                    xNewTag = XmlParser.new_element(xParentTag, xTag, xText, xAttrib, xOrder)
                else:
                    # if mode == 'SIBLING':
                    XmlParser.insert_element(xParentTag, oTag, xOrder)
                    xNewTag = oTag

                # creo el newTagInTree
                if is_comment:
                    xID = getIDForTreeView('comment', Globals.tags_in_tree_dictionary)
                    newTagInTree = TagInTree.TagInTree(xBaseID, xID, xNewTag, xParentTag, Globals.app_treeview,
                                                       order=xOrder,
                                                       is_comment=True)
                else:
                    xID = getIDForTreeView(xNewTag.tag, Globals.tags_in_tree_dictionary)
                    newTagInTree = TagInTree.TagInTree(xBaseID, xID, xNewTag, xParentTag, Globals.app_treeview,
                                                       order=xOrder)

                Globals.tags_in_tree_dictionary[xID] = newTagInTree
                selectAndFocus(xID)
                print 'newTagInTree'
                return newTagInTree


def getTagFromUser(mainApp, getValue=False):
    container = {}
    xWindow = mainApp.get_aux_window(Globals.lang['message_newtag'], container)
    xWindow.form_constructor('Tag', 0)
    if getValue:
        xWindow.form_constructor('Value', 1)
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


def copyTagInTree(oldTagInTree, xLevel, newparent=None):
    if oldTagInTree <> None:
        if newparent == None:
            xParentID = oldTagInTree.parent_id
            xParentTag = oldTagInTree.parent_tag
        else:
            xParentID = newparent.id
            xParentTag = newparent.getTag()

        xOrder = oldTagInTree.getTreeViewIndex() + 1

        xNewTag = XmlParser.new_element(xParentTag,
                                        oldTagInTree.getTag().tag,
                                        oldTagInTree.getTag().text,
                                        oldTagInTree.getTag().attrib,
                                        xOrder)

        xID = getIDForTreeView(xNewTag.tag, Globals.tags_in_tree_dictionary)

        newTagInTree = TagInTree.TagInTree(xParentID, xID, xNewTag, xParentTag, Globals.app_treeview, order=xOrder)
        Globals.tags_in_tree_dictionary[xID] = newTagInTree

        def getTagInTreeFromTag(xTag, dicTagsInTree):
            xReturn = None
            for xTuple in dicTagsInTree.items():
                # xTuple = (key, value)
                if xTuple[1].getTag() == xTag:
                    xReturn = xTuple[1]
                    break
            return xReturn

        for xChildTag in oldTagInTree.getTag():
            xChildTagInTree = getTagInTreeFromTag(xChildTag, Globals.tags_in_tree_dictionary)
            copyTagInTree(xChildTagInTree, xLevel + 1, newparent=newTagInTree)

        selectAndFocus(xID)

    else:
        print 'oldTagInTree is None'


def deleteSelectionTagInTree(selection):
    for xID in selection:
        deleteTagInTree(xID)


def deleteTagInTree(xID):
    if xID <> '':
        xTagInTree = Globals.tags_in_tree_dictionary[xID]
        xTagInTree.parent_tag.remove(xTagInTree.getTag())
        if Globals.app_treeview.exists(xTagInTree.id):
            Globals.app_treeview.delete(xTagInTree.id)
        del Globals.tags_in_tree_dictionary[xID]
        del xTagInTree
        print 'Deleted %s' % xID


def checkTreeView():
    if Globals.app_treeview == None:
        print 'TreeView does not exist'
    else:
        print 'TreeView is A-OK!'


def bCheckEntries(band_buttons):
    for widget in band_buttons.winfo_children():
        if isinstance(widget, Entry):
            print widget.get()


def printStringXML(oTIG):
    if oTIG <> None:
        stringXML = XmlParser.get_string_from_xml_node(oTIG.getTag())
        print stringXML[stringXML.find('\n') + 1:]
    else:
        print 'None selected'


def setFilenameLabel(label_filename):
    print "setFilenameLabel"
    if Globals.show_file_full_path:
        label_filename.config(text=Globals.config_filename)
    else:
        label_filename.config(text=Globals.config_filename[Globals.config_filename.rfind('\\') + 1:])


def bFoldNode(idNode):
    Globals.app_treeview.item(idNode, open=False)


def bShowGuts(thing):
    print thing


# MENU METHODS


def mChangeFilenameLabel(label_filename):
    Utils.menu_switch_global('GL.showFileFullPath', 'showFileFullPath')
    setFilenameLabel(label_filename)


def refreshTreeview(mainApp):
    # clean treeview frame
    mainApp.frames.treeview.clean()

    # set globals
    Globals.tags_in_tree_dictionary = {}
    Globals.app_treeview = tk_treeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons,
                                                   Globals.tags_in_tree_dictionary)

    # load xml dic and TIGs
    root = Globals.xml_tree.getroot()

    Globals.tags_in_tree_dictionary[root.tag] = TagInTree.TagInTree('', root.tag, root, None, Globals.app_treeview)
    addXMLToTree(root, root.tag, Globals.tags_in_tree_dictionary, Globals.app_treeview)
    mainApp.update()

    selectAndFocus(Globals.last_treeview_focus)


def selectAndFocus(xIDFocus):
    if xIDFocus <> '':
        Globals.app_treeview.see(xIDFocus)
        Globals.app_treeview.focus(xIDFocus)
        Globals.app_treeview.selection_set(xIDFocus)


#####################

if __name__ == '__main__':
    self = App('test.gif')
    self.mainloop()
    try:
        self.destroy()
    except:
        print 'error trying to close mainApp'

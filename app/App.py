# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
import xml.etree.ElementTree as ElementTree
import os.path

from config import Globals
from EdiTag import EdiTag
from xml_parser import XmlParser
from FrameExtension import FrameExtension
from TempData import TempData
from AuxWindow import AuxWindow
from app.elements.AppMenu import AppMenu
from app.elements.AppButtonBar import ButtonBar
from app.elements.AppFooter import Footer
from app.elements import AppMessageBox, AppTreeview


# CLASSES

class FramePack(object):
    def __init__(self, master):
        self.button_bar = ButtonBar(master)
        self.center = FrameExtension(master)
        self.footer = Footer(master)

        self.treeview = FrameExtension(self.center)
        self.buttons = FrameExtension(self.center)


class App(Tk):
    def __init__(self, icon_path='test.gif', exclude_buttons=None):
        Tk.__init__(self)
        if exclude_buttons is None:
            exclude_buttons = []
        self.title(Globals.app_name)

        # elementos del main
        self.exclude_buttons = exclude_buttons
        self.root = None
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

        self.menubar = AppMenu(self)
        self.frames = FramePack(self)

        # procesos iniciales
        self.load_icon()
        self.init_menu_bools()
        self.refresh()

        # captura de cierre del programa
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_app())

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

    @staticmethod
    def set_scrollbar(parent, widget):
        scrollbar = Scrollbar(parent, command=widget.yview)
        widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def refresh(self):
        self.clean_app_elements()
        self.fill_app_elements()
        self.pack_app_elements()
        self.frames.button_bar.set_filename_label()

    def clean_app_elements(self):
        for i in range(0, 100):  # TODO: habría que ver si se puede hacer esto más eficiente
            self.menubar.delete(i)
        self.frames.button_bar.clean()
        self.frames.footer.clean()
        self.clean_xml_app_elements()

    def clean_xml_app_elements(self):
        self.frames.treeview.clean()
        self.frames.buttons.clean()

    def fill_app_elements(self):
        self.menubar.fill()
        self.frames.button_bar.fill()
        self.frames.footer.fill()

    def pack_app_elements(self):
        self.frames.button_bar.pack(side=TOP, fill=X)
        self.frames.center.pack(side=TOP, fill=BOTH, expand=True)
        self.frames.treeview.pack(side=LEFT, fill=BOTH)
        self.frames.buttons.pack(side=LEFT, fill=BOTH, expand=True, ipadx=0, pady=20)
        self.frames.footer.pack(side=BOTTOM, fill=X)

    # MAIN METHODS

    def quit_app(self):
        if self.check_for_changes():
            self.destroy()

    def check_for_changes(self):
        default_save_type = 'SAVE'

        if self.root is None:
            response, save_type = 'no', default_save_type
        else:
            response, save_type = self.ask_user_if_changes_must_be_saved(default_save_type)

        if response == 'yes':
            self.save_xml(save_type)
            return True
        elif response == 'cancel':
            return False
        elif response == 'no':
            return True

    def ask_user_if_changes_must_be_saved(self, save_type):
        if Globals.config_filename == '':
            response = AppMessageBox.warning(Globals.lang['message_filenotdefined'])

            if response == 'yes':
                save_type = 'SAVEAS'

        elif not os.path.isfile(Globals.config_filename):
            response = AppMessageBox.warning(Globals.lang['message_filenotfound'] % Globals.config_filename)

        elif XmlParser.file_has_changed(self.root.xmltag(), Globals.config_filename):
            response = AppMessageBox.warning(Globals.lang['message_exitsave'] % Globals.config_filename)

        else:
            response = 'no'

        return response, save_type

    # BUTTON METHODS

    def open_xml(self, file_path=''):
        if self.check_for_changes():
            if file_path == '':
                file_path = self.get_path_from_user()

            if file_path != '':
                self.open_xml_from_path(file_path)

    def open_xml_from_path(self, file_path):
        self.clean_xml_app_elements()
        xmlroot = XmlParser.get_xml_root(file_path)

        if xmlroot is None:
            tkMessageBox.showerror('eXMLorer', Globals.lang['message_nonvalidxml'] % file_path)
            file_path = ''
        else:
            self.load_xmlroot_in_app(xmlroot)

        self.update_filename_label(file_path)

    def update_filename_label(self, file_path):
        self.app.frames.button_bar.update_filename_label(file_path)

    def load_xmlroot_in_app(self, xmlroot):
        Globals.editag_dictionary = {}
        Globals.app_treeview = AppTreeview.getTreeView(self.frames.treeview,
                                                       self.frames.buttons,
                                                       Globals.editag_dictionary)

        self.root = Globals.editag_dictionary[xmlroot.tag] = EdiTag(xmlroot,
                                                                    None,
                                                                    treeview=Globals.app_treeview)

        addXMLToTree(xmlroot, Globals.editag_dictionary, Globals.app_treeview)

        self.frames.footer.update_label_encoding()

    def get_path_from_user(self):
        file_path = tkFileDialog.askopenfilename(defaultextension='.xml',
                                                 filetypes=[('XML files', '.xml'), ('all files', '.*')],
                                                 initialdir=self.temp.getValue('lastVisitedFolder'))
        if not isinstance(file_path, tuple):
            # TODO: CAMBIAR EL RFIND PARA ACEPTAR CUALQUIER TIPO DE OS
            self.temp.setValue('lastVisitedFolder', file_path[:file_path.rfind('\\')])
            return file_path
        else:
            return ''

    def open_xml_from_text(self):
        if self.check_for_changes():
            self.clean_xml_app_elements()
            xml_string = self.get_xml_string_from_user()

            if xml_string != '':
                try:
                    xmlroot = XmlParser.get_xml_root_from_string(xml_string.encode('utf-8'))
                except Exception as e:
                    xmlroot = None
                    print e

                self.load_xmlroot_in_app(xmlroot)

    def get_xml_string_from_user(self):
        container = {}
        label = Globals.lang['message_newxmlstring']
        title = Globals.lang['message_newxml']
        xml_string_window = self.get_aux_window(title, container, use_sql_buttons=False)
        xml_string_window.text_field_constructor(label)
        xml_string_window.show()

        if len(container) > 0:
            return container[label]
        else:
            return ''

    def save_xml(self, save_type):
        try:
            save_filename = self.get_save_filename(save_type)
            if save_filename:
                save_filename = self.validate_extension(save_filename)
                XmlParser.save_xml(Globals.xml_tree, save_filename)
                self.update_filename_label(save_filename)
        except Exception, e:
            AppMessageBox.error(Globals.lang['message_savingerror'] % e)

    def get_tag_from_user(self, get_value=False):
        # TODO revisar
        container = {}
        tag_window = self.get_aux_window(Globals.lang['message_newtag'], container)
        tag_window.form_constructor('Tag', 0)
        if get_value:
            tag_window.form_constructor('Value', 1)
        tag_window.show()

        if len(container) > 0:
            if get_value:
                return container['Tag'], container['Value']
            else:
                return container['Tag']
        else:
            if get_value:
                return '', ''
            else:
                return ''

    @staticmethod
    def get_save_filename(save_type):
        if save_type == 'SAVEAS':
            return AppMessageBox.file_dialog()
        else:
            return Globals.config_filename

    @staticmethod
    def validate_extension(save_filename):
        if save_filename[-4:] != '.xml':
            save_filename += '.xml'
        return save_filename


# BUTTON METHODS
def addXMLToTree(base_editag, editag_dictionary, treeview):
    for child in base_editag:
        if child.tag is ElementTree.Comment:
            if Globals.show_comments:
                id_for_treeview = getIDForTreeView('comment', editag_dictionary)
                editag_dictionary[id_for_treeview] = EdiTag(child, base_editag, is_comment=True)

        if type(child.tag).__name__ == 'str':
            id_for_treeview = getIDForTreeView(child.tag, editag_dictionary)
            editag_dictionary[id_for_treeview] = EdiTag(child, base_editag)
            addXMLToTree(child, editag_dictionary, treeview)


def createNewTagInTree(mainApp, baseTIG, mode, oTag=None, is_comment=False, text=''):
    if baseTIG <> None:
        if baseTIG.parent_id <> '':
            # consigo datos para nuevo tag
            xTag = ''
            if is_comment:
                xTag = 'comment'
                stringXML = XmlParser.get_string_from_xml_node(baseTIG.xmltag())
                xText = stringXML[stringXML.find('\n') + 1:]
            elif text <> '':
                xTag = mainApp.get_tag_from_user()
                xText = text
            elif oTag == None:
                xTag, xText = mainApp.get_tag_from_user(get_value=True)

            if (xTag <> '') or (oTag <> None):
                xAttrib = {}
                # consigo datos para crear el TagInTree
                if mode == 'SIBLING':
                    xBaseID = baseTIG.parent_id
                    xParentTag = baseTIG.parent_tag
                    xOrder = baseTIG.get_treeview_index() + 1
                elif mode == 'CHILD':
                    xBaseID = baseTIG.id
                    xParentTag = baseTIG.xmltag()
                    # xOrder = baseTIG.get_number_of_siblings() + 1
                    xOrder = baseTIG.get_number_of_children() + 1
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
                    xID = getIDForTreeView('comment', Globals.editag_dictionary)
                    newTagInTree = EdiTag.TagInTree(xBaseID, xID, xNewTag, xParentTag, Globals.app_treeview,
                                                    order=xOrder,
                                                    is_comment=True)
                else:
                    xID = getIDForTreeView(xNewTag.tag, Globals.editag_dictionary)
                    newTagInTree = EdiTag.TagInTree(xBaseID, xID, xNewTag, xParentTag, Globals.app_treeview,
                                                    order=xOrder)

                Globals.editag_dictionary[xID] = newTagInTree
                selectAndFocus(xID)
                print 'newTagInTree'
                return newTagInTree


def copyTagInTree(oldTagInTree, xLevel, newparent=None):
    if oldTagInTree <> None:
        if newparent == None:
            xParentID = oldTagInTree.parent_id
            xParentTag = oldTagInTree.parent_tag
        else:
            xParentID = newparent.id
            xParentTag = newparent.xmltag()

        xOrder = oldTagInTree.get_treeview_index() + 1

        xNewTag = XmlParser.new_element(xParentTag,
                                        oldTagInTree.xmltag().tag,
                                        oldTagInTree.xmltag().text,
                                        oldTagInTree.xmltag().attrib,
                                        xOrder)

        xID = getIDForTreeView(xNewTag.tag, Globals.editag_dictionary)

        newTagInTree = EdiTag.TagInTree(xParentID, xID, xNewTag, xParentTag, Globals.app_treeview, order=xOrder)
        Globals.editag_dictionary[xID] = newTagInTree

        def getTagInTreeFromTag(xTag, dicTagsInTree):
            xReturn = None
            for xTuple in dicTagsInTree.items():
                # xTuple = (key, value)
                if xTuple[1].xmltag() == xTag:
                    xReturn = xTuple[1]
                    break
            return xReturn

        for xChildTag in oldTagInTree.xmltag():
            xChildTagInTree = getTagInTreeFromTag(xChildTag, Globals.editag_dictionary)
            copyTagInTree(xChildTagInTree, xLevel + 1, newparent=newTagInTree)

        selectAndFocus(xID)

    else:
        print 'oldTagInTree is None'


def getIDForTreeView(xTag, dicTagsInTree):
    i = 0
    while dicTagsInTree.has_key(xTag + str(i)):
        i += 1
    dicTagsInTree[xTag + str(i)] = 0
    return xTag + str(i)


def deleteSelectionTagInTree(selection):
    for xID in selection:
        deleteTagInTree(xID)


def deleteTagInTree(xID):
    if xID <> '':
        xTagInTree = Globals.editag_dictionary[xID]
        xTagInTree.parent_tag.remove(xTagInTree.xmltag())
        if Globals.app_treeview.exists(xTagInTree.id):
            Globals.app_treeview.delete(xTagInTree.id)
        del Globals.editag_dictionary[xID]
        del xTagInTree
        print 'Deleted %s' % xID


def bCheckEntries(band_buttons):
    for widget in band_buttons.winfo_children():
        if isinstance(widget, Entry):
            print widget.get()


def printStringXML(oTIG):
    if oTIG <> None:
        stringXML = XmlParser.get_string_from_xml_node(oTIG.xmltag())
        print stringXML[stringXML.find('\n') + 1:]
    else:
        print 'None selected'


# MENU METHODS


def refreshTreeview(mainApp):
    # clean treeview frame
    mainApp.frames.treeview.clean()

    # set globals
    Globals.editag_dictionary = {}
    Globals.app_treeview = AppTreeview.getTreeView(mainApp.frames.treeview, mainApp.frames.buttons,
                                                   Globals.editag_dictionary)

    # load xml dic and TIGs
    root = Globals.xml_tree.getroot()

    Globals.editag_dictionary[root.tag] = EdiTag.TagInTree('', root.tag, root, None, Globals.app_treeview)
    addXMLToTree(root, Globals.editag_dictionary, Globals.app_treeview)
    mainApp.update()

    selectAndFocus(Globals.last_treeview_focus)


def selectAndFocus(xIDFocus):
    if xIDFocus <> '':
        Globals.app_treeview.see(xIDFocus)
        Globals.app_treeview.focus(xIDFocus)
        Globals.app_treeview.selection_set(xIDFocus)

# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkFileDialog
import tkMessageBox
import xml.etree.ElementTree as ElementTree
import os.path

from config import Globals
from EdiTag import EdiTag
from config.Utils import SaveType
from xml_parser import XmlParser
from FrameExtension import FrameExtension
from TempData import TempData
from AuxWindow import AuxWindow
from app.elements.AppMenu import AppMenu
from app.elements.AppButtonBar import ButtonBar
from app.elements.AppFooter import Footer
from app.elements import AppMessageBox
from app.elements.AppTreeview import AppTreeview


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
        self.bind('<F5>', lambda: Globals.app_treeview.refresh(self))

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
        default_save_type = SaveType.SAVE

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
                save_type = SaveType.SAVE_AS

        elif not os.path.isfile(Globals.config_filename):
            response = AppMessageBox.warning(Globals.lang['message_filenotfound'] % Globals.config_filename)

        elif XmlParser.file_has_changed(self.root.xmltag, Globals.config_filename):
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
        Globals.app.update()

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
        self.frames.button_bar.update_filename_label(file_path)

    def load_xmlroot_in_app(self, xmlroot):
        Globals.editag_dictionary = {}
        Globals.app_treeview = AppTreeview(self)

        self.root = Globals.editag_dictionary[xmlroot.tag] = EdiTag(xmlroot,
                                                                    None,
                                                                    treeview=Globals.app_treeview,
                                                                    is_root=True)

        self.add_xml_to_tree(self.root)

        self.frames.footer.update_label_encoding()

    def get_path_from_user(self):
        file_path = tkFileDialog.askopenfilename(defaultextension='.xml',
                                                 filetypes=[('XML files', '.xml'), ('all files', '.*')],
                                                 initialdir=self.temp.get_value('lastVisitedFolder'))
        if not isinstance(file_path, tuple):
            # TODO: CAMBIAR EL RFIND PARA ACEPTAR CUALQUIER TIPO DE OS
            self.temp.set_value('lastVisitedFolder', file_path[:file_path.rfind('\\')])
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

    def add_xml_to_tree(self, base_editag):
        for child in base_editag.xmltag:
            if child is ElementTree.Comment:
                EdiTag(child, base_editag, is_comment=True)
            elif type(child).__name__ == 'Element':
                child_editag = EdiTag(child, base_editag)
                self.add_xml_to_tree(child_editag)

    @staticmethod
    def get_save_filename(save_type):
        if save_type == SaveType.SAVE_AS:
            return AppMessageBox.file_dialog()
        else:
            return Globals.config_filename

    @staticmethod
    def validate_extension(save_filename):
        if save_filename[-4:] != '.xml':
            save_filename += '.xml'
        return save_filename

    def refresh_treeview(self):
        self.clean_xml_app_elements()

        del Globals.editag_dictionary
        Globals.editag_dictionary = {}
        Globals.app_treeview = AppTreeview(self)

        root = Globals.xml_tree.getroot()

        self.add_xml_to_tree(root)
        self.update()

        Globals.app_treeview.select_and_focus(Globals.last_treeview_focus)

    def get_clipboard_string(self):
        xml_string = self.selection_get(selection='CLIPBOARD')
        try:
            print xml_string
        except UnicodeEncodeError:
            print 'using unicode'
            xml_string = unicode(xml_string, "utf-8")
            print xml_string
        finally:
            return xml_string

# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox

from app import search_man
from app.FrameExtension import FrameExtension
from config import Globals, Utils
from app.EdiTag import EdiTag
from config.Utils import TagRelation, SaveType


class ButtonBar(FrameExtension):
    def __init__(self, app):
        FrameExtension.__init__(self, app)
        self.app = app
        self.entry_search = None
        self.fill_buttons()
        self.fill_search()

    def fill(self):
        self.fill_buttons()
        self.fill_search()

    def fill_buttons(self):
        print "appButtonBar - fill_buttons"
        if 'label_filename' not in self.app.exclude_buttons:
            label_filename = self.add_widget('Label', 'label_filename')
            label_filename.configure(padding=(10, 0, 0, 0))
            label_filename.grid(row=0, column=4, columnspan=2)

        Utils.create_button(self, 'button_newFromText', 0, 0, command=lambda: self.app.open_xml_from_text())
        Utils.create_button(self, 'button_open', 0, 1, command=lambda: self.app.open_xml())
        Utils.create_button(self, 'button_save', 0, 2, command=lambda: self.app.save_xml(SaveType.SAVE))
        Utils.create_button(self, 'button_saveAs', 0, 3, command=lambda: self.app.save_xml(SaveType.SAVE_AS))
        Utils.create_button(self, 'button_newTag', 1, 0,
                            command=lambda: EdiTag.build(
                                Globals.editag_dictionary.setdefault(
                                    Globals.app_treeview.focus(), None), TagRelation.SIBLING))
        Utils.create_button(self, 'button_newChildTag', 1, 1,
                            command=lambda: EdiTag.build(
                                Globals.editag_dictionary.setdefault(
                                    Globals.app_treeview.focus(), None), TagRelation.CHILD))
        Utils.create_button(self, 'button_copyTag', 1, 2,
                            command=lambda: EdiTag.copy(
                                Globals.editag_dictionary.setdefault(Globals.app_treeview.focus(), None)))
        Utils.create_button(self, 'button_deleteTag', 1, 3,
                            command=lambda: self.app.deleteSelectionTagInTree(Globals.app_treeview.selection()))

        # debug buttons
        Utils.create_button(self, 'button_showChildQty', 2, 1,
                            command=lambda: self.show_guts(
                                Globals.editag_dictionary[Globals.app_treeview.focus()].get_number_of_children()))

    def fill_search(self):
        frame_search = self.add_widget('LabelFrame', 'frame_search')
        frame_search.configure(text=Globals.lang['frame_search'])
        frame_search.grid(row=1, column=4, sticky='wn')

        search_options = (Globals.lang['option_tags'], Globals.lang['option_values'], Globals.lang['option_xpath'])
        optionmenu_search = OptionMenu(frame_search, self.app.string_optionmenu_search, search_options[0],
                                       *search_options)
        optionmenu_search.configure(width=Globals.button_width)
        optionmenu_search.grid(row=0, column=0, sticky='wn')

        entry_search = Entry(frame_search)
        self.entry_search = entry_search
        entry_search.configure(width=Globals.label_button_width)
        entry_search.grid(row=0, column=1, sticky='wn')
        entry_search.bind('<Return>', lambda: self.basic_search())

    def basic_search(self):
        search_string = self.entry_search
        id_focused_tag = Globals.app_treeview.focus()

        if search_string != '':
            if (self.app.currentSearch is None) or (self.app.currentSearch.search_string != search_string):
                try:
                    starting_point = Globals.editag_dictionary[id_focused_tag].tag_order
                except IndexError:
                    starting_point = 0
                self.app.currentSearch = search_man.BasicSearch(search_string, Globals.editag_dictionary,
                                                                self.app.string_optionmenu_search.get(), starting_point)

            new_focus = self.app.currentSearch.output.next()
            if new_focus == '':
                tkMessageBox.showinfo(Globals.app_name, Globals.lang['message_nofinds'])
            else:
                self.app.selectAndFocus(new_focus)

    @staticmethod
    def show_guts(thing):
        print thing

    def update_filename_label(self, new_path):
        Globals.file_path = new_path
        self.set_filename_label()

    def set_filename_label(self):
        if Globals.file_path != '':
            if Globals.show_file_full_path:
                self.dic['label_filename'].config(text=Globals.file_path)
            else:
                self.dic['label_filename'].config(text=Globals.file_path[Globals.file_path.rfind('\\') + 1:])

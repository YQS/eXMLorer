# Encoding: UTF-8

from app.FrameExtension import FrameExtension
from config import Globals, Utils
from app.elements import AppTreeview


class Footer(FrameExtension):
    def __init__(self, app):
        FrameExtension.__init__(self, app)
        self.app = app

    def fill(self):
        Utils.create_button(self, 'button_moveUp', 0, 1, command=lambda: Globals.app_treeview.move_node(
            Globals.app_treeview.focus(),
            Globals.editag_dictionary[Globals.app_treeview.focus()].get_treeview_index() - 1))

        Utils.create_button(self, 'button_moveDown', 0, 2, command=lambda: Globals.app_treeview.move_node(
            Globals.app_treeview.focus(),
            Globals.editag_dictionary[Globals.app_treeview.focus()].get_treeview_index() + 1))

        Utils.create_button(self, 'button_moveBeginnnig', 0, 3, command=lambda: Globals.app_treeview.move_node(
            Globals.app_treeview.focus(),
            0))

        Utils.create_button(self, 'button_moveEnd', 0, 4, command=lambda: Globals.app_treeview.move_node(
            Globals.app_treeview.focus(),
            'end'))

        if 'label_encoding' not in self.app.exclude_buttons:
            label_encoding = self.add_widget('Label', 'label_encoding')
            label_encoding.configure(padding=(10, 0, 0, 0))
            label_encoding.grid(row=0, column=5, sticky='e')

    def update_label_encoding(self):
        self.dic['label_encoding'].config(text=Globals.xml_encoding)

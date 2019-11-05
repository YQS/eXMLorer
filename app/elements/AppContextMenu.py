# encoding: UTF-8
import tkMessageBox
from Tkinter import *
from ttk import *

from app.EdiTag import EdiTag
from app.elements import AppMessageBox
from config import Globals
from app import module_interface
from xml_parser import XmlParser


class AppContextMenu(Menu):
    def __init__(self, parent, event):
        Menu.__init__(self, parent, tearoff=0)
        self.focus_tag = self.get_focus_tag(event)
        Globals.app_treeview.focus(self.focus_tag.id)

        self.action_provider = ContextMenuActions(self.focus_tag)

        self.build(event)

    def build(self, event):
        self.load_edit_submenu()

        self.add_separator()
        self.load_fold_submenu()

        self.add_separator()
        self.load_comment_submenu()

        self.add_separator()
        self.load_subname_submenu()

        self.run_modules()
        self.post(event.x_root, event.y_root)

    def load_edit_submenu(self):
        self.add_command(label=Globals.lang['submenu_edittag'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.edit_tag())

        self.add_command(label=Globals.lang['submenu_copytag'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.copy_to_clipboard())

        self.add_command(label=Globals.lang['submenu_cuttag'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.copy_to_clipboard(mode='CUIT'))

        self.add_command(label=Globals.lang['submenu_pastetag'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.paste_from_clipboard())

        self.add_command(label=Globals.lang['submenu_pastetagaschild'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.paste_from_clipboard(mode='CHILD'))

    def load_fold_submenu(self):
        self.add_command(label=Globals.lang['submenu_fold'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.unfold_all(False))

        self.add_command(label=Globals.lang['submenu_unfold'],
                         state=ACTIVE,
                         command=lambda: self.action_provider.unfold_all(True))

    def load_comment_submenu(self):
        if self.focus_tag.is_comment:
            self.add_command(label=Globals.lang['submenu_uncomment'],
                             state=ACTIVE,
                             command=lambda: self.action_provider.uncomment_tag())
        else:
            self.add_command(label=Globals.lang['submenu_comment'],
                             state=ACTIVE,
                             command=lambda: self.action_provider.comment_tag())

    def load_subname_submenu(self):
        cmd_state = ACTIVE if self.focus_tag.parent_editag is None else DISABLED

        self.add_command(label=Globals.lang['submenu_selectParentSubname'],
                         state=cmd_state,
                         command=lambda: self.action_provider.set_as_parent_subname()
                         )
        self.add_command(label=Globals.lang['submenu_cleanParentSubname'],
                         state=cmd_state,
                         command=lambda: self.action_provider.clear_subname())

    def run_modules(self):
        params = {'parent': self, 'parentTIG': self.focus_tag, 'mainApp': Globals.app}
        module_interface.runModules('TREEVIEW_MENU', params)

    @staticmethod
    def get_focus_tag(event):
        focus_id = Globals.app_treeview.identify_row(event.y)
        return Globals.editag_dictionary[focus_id]


class ContextMenuActions:
    def __init__(self, focus_tag):
        self.focus_tag = focus_tag

    def edit_tag(self):
        container = {'Tag': self.focus_tag.get_tag_actual_name(), 'Value': self.focus_tag.get_tag_value()}
        edit_window = Globals.app.get_aux_window(Globals.lang['message_edittag'], container)

        edit_window.form_constructor('Tag', 0)
        edit_window.form_constructor('Value', 1)

        edit_window.show()

        if len(container) > 0:
            self.focus_tag.update_tag(container['Tag'], container['Value'])
            Globals.app.refresh_treeview()

    def copy_to_clipboard(self, mode='COPY'):
        if self.focus_tag is not None:
            xml_string = XmlParser.get_string_from_xml_node(self.focus_tag.xmltag)
            xml_string = xml_string[xml_string.find('\n') + 1:]

            Globals.app.clipboard_clear()
            Globals.app.clipboard_append(xml_string)

            if mode == 'CUT':
                del self.focus_tag

    def paste_from_clipboard(self, mode='SIBLING'):
        if self.focus_tag is not None:
            xml_string = Globals.app.get_clipboard_string()

            clipboard_root = XmlParser.get_xml_from_string(xml_string)

            root_editag = EdiTag.build(self.focus_tag, mode, xml_tag=clipboard_root)

            Globals.app.refresh_treeview()
            Globals.app_treeview.select_and_focus(root_editag.id)

    def unfold_all(self, is_open):
        self.do_unfold(self.focus_tag.id, is_open)

    def do_unfold(self, node_id, is_open):
        Globals.app_treeview.item(node_id, open=is_open)
        for child_id in Globals.app_treeview.get_children(node_id):
            self.do_unfold(child_id, is_open)

    def comment_tag(self):
        if self.focus_tag is not None:
            EdiTag.build(self.focus_tag, 'SIBLING', is_comment=True)
            del self.focus_tag

    def uncomment_tag(self):
        xml_string = self.focus_tag.get_tag_value()
        new_editag = None

        try:
            new_editag = EdiTag.build(self.focus_tag,
                                      'SIBLING',
                                      xml_tag=XmlParser.get_xml_from_string(xml_string))
        except:
            response = AppMessageBox.warning(Globals.lang['message_uncomment_newtag'],
                                             warning_type=tkMessageBox.YESNO)

            if response == 'yes':
                new_editag = EdiTag.build(self.focus_tag,
                                          'SIBLING',
                                          text=xml_string)

        if new_editag is not None:
            self.create_child_editags(new_editag, level=0)
            del self.focus_tag
            Globals.app_treeview.select_and_focus(new_editag.id)

    def create_child_editags(self, editag, level):
        children_qty = editag.get_number_of_children()

        for child_tag in editag.xmltag:
            print 'paste has child level', level, 'Q', children_qty
            child_editag = EdiTag.build(editag, 'CHILD', xml_tag=child_tag)
            self.create_child_editags(child_editag, level=level + 1)

            children_qty -= 1
            if children_qty <= 0:
                break

    def set_as_parent_subname(self):
        parent_editag = self.focus_tag.get_parent()

        Globals.subnames.update(parent_editag.get_tag_actual_name(), self.focus_tag.get_tag_actual_name())
        parent_editag.update_subname(self.focus_tag.get_tag_value())

    def clear_subname(self):
        self.focus_tag.update_subname('')
        Globals.subnames.delete(self.focus_tag.get_tag_actual_name())

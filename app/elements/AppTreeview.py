# encoding: UTF-8

from Tkinter import *
from ttk import *
import tkMessageBox

from config import Globals
from xml_parser import XmlParser
import app.module_interface as MOD
import app.SSF
import app.App
from app.EdiTag import EdiTag
from app.elements.AppContextMenu import AppContextMenu, ContextMenuActions


class AppTreeview(Treeview):
    def __init__(self, app):
        self.treeview_parent = app.frames.treeview
        Treeview.__init__(self, self.treeview_parent, columns=('data', 'subname',))

        self.do_pack()
        self.fill()

    def do_pack(self):
        self.pack(side='left', fill=BOTH)

    def fill(self):
        self.set_scrollbar()
        self.set_columns()
        self.bind_events()

    def get_focused_editag(self):
        return Globals.editag_dictionary.setdefault(self.focus(), None)

    def select_and_focus(self, id):
        if not id is None:
            self.see(id)
            self.focus(id)
            self.selection_set(id)

    def delete_selection(self):
        for id in self.selection():
            del Globals.editag_dictionary[id]

    def set_scrollbar(self):
        scrollbar = Scrollbar(self.treeview_parent, orient=VERTICAL, command=self.yview)
        self.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

    def set_columns(self):
        self.column('subname', width=120, anchor='w', stretch=True)
        self.column('data', width=480, anchor='w', stretch=True)
        self.heading('subname', text=Globals.lang['column-subname'])
        self.heading('data', text=Globals.lang['column-data'])

        self.configure(displaycolumns=('subname', 'data'))

    def bind_events(self):
        self.bind('<<TreeviewSelect>>', lambda event: self.fill_buttons_frame())
        self.bind('<Button-3>', lambda event: AppContextMenu(self, event))
        self.bind('<Shift-Up>', lambda event: self.move_node_bind(event))
        self.bind('<Shift-Down>', lambda event: self.move_node_bind(event))
        self.bind('<Control-Key-c>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .copy_to_clipboard())
        self.bind('<Control-Key-C>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .copy_to_clipboard())
        self.bind('<Control-Key-x>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .copy_to_clipboard('CUT'))
        self.bind('<Control-Key-X>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .copy_to_clipboard('CUT'))
        self.bind('<Control-Key-v>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .paste_from_clipboard())
        self.bind('<Control-Key-V>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .paste_from_clipboard())
        self.bind('<Control-Alt-Key-v>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .paste_from_clipboard(mode='CHILD'))
        self.bind('<Control-Alt-Key-V>',
                  lambda: ContextMenuActions(Globals.editag_dictionary.setdefault(self.focus(), None))
                  .paste_from_clipboard(mode='CHILD'))

        self.bind('<Control-Key-n>', lambda: EdiTag.build(self.get_focused_editag(), 'SIBLING'))
        self.bind('<Control-Key-N>', lambda: EdiTag.build(self.get_focused_editag(), 'SIBLING'))
        self.bind('<Control-Key-i>', lambda: EdiTag.build(self.get_focused_editag(), 'CHILD'))
        self.bind('<Control-Key-I>', lambda: EdiTag.build(self.get_focused_editag(), 'CHILD'))

        self.bind('<Delete>', lambda: self.delete_selection())

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
              justify=LEFT) \
            .grid(column=0, row=0, stick='nw', pady=5, columnspan=2)

        focused_editag.get_as_button_row(scrolling_frame.frame, 1)
        scrolling_frame.create_separator()

        row = 3
        for child_editag in focused_editag:
            child_editag.get_as_button_row(scrolling_frame.frame, row)
            row += 1

    def move_node_bind(self, event):
        direction = 0
        if event.keycode == 38:  # Up
            direction = -1
        elif event.keycode == 40:  # Down
            direction = 1

        focus_id = self.focus()
        parent_id = Globals.editag_dictionary[focus_id].parent_id
        position = Globals.editag_dictionary[focus_id].get_treeview_index() + direction
        self.move_node(focus_id, parent_id, position)

    def move_node(self, focus_id, parent_id, position):
        focus_editag = Globals.editag_dictionary[focus_id]

        self.move(focus_id, focus_editag.get_parent().id, position)

        if position == 'end':
            position = focus_editag.get_number_of_siblings()

        XmlParser.move_tag(Globals.editag_dictionary[parent_id].xmltag,
                           focus_editag.xmltag,
                           position)

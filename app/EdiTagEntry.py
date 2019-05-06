# encoding: UTF-8

from Tkinter import *
from ttk import *

from config import Globals


class EdiTagEntry:
    def __init__(self, editag, parent_band, value, row):
        self.editag = editag
        self.parent_band = parent_band
        self.row = row
        self.value = value.strip()
        self.widget = None
        self.button = None
        self.set_widget()

    def set_widget(self):
        if self.value.title() in Globals.entry_bool_options:
            self.set_bool_combobox()
        elif self.value == '':
            self.set_disabled_entry()
        elif len(self.value) < (Globals.button_width + Globals.margin_to_extend_for_text):
            self.set_entry()
        else:
            self.set_big_entry()

    def set_bool_combobox(self):
        self.widget = Combobox(self.parent_band,
                               values=Globals.entry_bool_options,
                               width=(Globals.button_width - 3))
        self.set_grid('wn')
        self.set_widget_focus_update_configuration()
        self.widget.set(self.value.title())

    def set_disabled_entry(self):
        self.widget = Entry(self.parent_band)
        self.set_widget_focus_update_configuration()
        self.set_grid('w')

        if self.editag.has_child():
            self.widget.insert(0, '<...>')
            self.widget.config(width=Globals.button_width)
        else:
            self.widget.insert(0, '</>')
            self.widget.config(width=Globals.button_width - Globals.label_extra_button_width)
            self.button = Button(self.parent_band,
                                 text=Globals.lang['button_open'],
                                 width=Globals.label_extra_button_width)
            self.button.grid(column=1, row=self.row, sticky='e')
            self.button.config(command=lambda: self.activate_text_entry())

    def set_widget_focus_update_configuration(self):
        self.widget.configure(validate='focus',
                              validatecommand=lambda widget=self.widget, editag=self.editag:
                              editag.update_tree_node(self.widget.get()))

    def set_grid(self, sticky):
        self.widget.grid(column=1, row=self.row, sticky=sticky)

    def set_entry(self, width=Globals.button_width, value=''):
        if value == '':
            value = self.value
        self.widget = Entry(self.parent_band, width=width)
        self.set_widget_focus_update_configuration()
        self.widget.bind('<Return>', lambda event,
                                            widget=self.widget,
                                            editag=self.editag: editag.update_tree_node(widget.get()))
        self.widget.bind('<Control-Key-a>', lambda: self.entry_select_all_text())
        self.widget.bind('<Control-Key-A>', lambda: self.entry_select_all_text())
        self.set_grid('wn')
        self.widget.insert(0, value)

    def entry_select_all_text(self):
        self.widget.tag_add(SEL, "1.0", END)
        self.widget.mark_set(INSERT, "1.0")
        self.widget.see(INSERT)
        return 'break'  # porque si no, el tkinter lee el siguiente evento

    def set_big_entry(self):
        self.set_entry(width=Globals.button_width - Globals.label_extra_button_width,
                       value=self.value[:Globals.button_width])
        self.widget.configure(state=DISABLED)
        self.button = Button(self.parent_band, text='...', width=Globals.label_extra_button_width)
        self.button.grid(column=1, row=self.row, sticky='e')
        self.button.config(command=lambda: self.open_text_window())

    def open_text_window(self):
        container = {}
        label = Globals.lang['message_value']
        title = Globals.lang['message_editing'] + ' ' + self.editag.get_tag_name()
        text_window = Globals.app.get_aux_window(title, container)

        text_window.text_field_constructor(label, self.editag.xmltag().text)
        text_window.show()

        if len(container) > 0:
            self.editag.update_tree_node(container[label])
            self.widget.delete(0, END)
            self.widget.insert(0, container[label][:Globals.label_button_width])

    def activate_text_entry(self):
        self.widget.destroy()
        self.button.destroy()
        self.set_entry()

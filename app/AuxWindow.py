# Encoding: UTF-8
from Tkinter import *
from ttk import *
from ScrolledText import ScrolledText

from config import Globals
import module_interface


class AuxWindow(Toplevel):
    def __init__(self, master, title, container, use_sql_buttons=True):
        Toplevel.__init__(self)
        self.transient(master)
        self.title(title)

        self.parent = master
        self.result = container
        self.entries = {}
        self.upper = Frame(self)
        self.body = Frame(self)
        self.buttons = Frame(self)
        self.first_field = None

        self.use_sql_buttons = use_sql_buttons

        self.upper.pack(side=TOP, fill=X)
        self.body.pack(side=TOP, fill=BOTH, expand=True)
        self.buttons.pack(side=BOTTOM, fill=X)
        self.create_ok_cancel_buttons()

        self.geometry('+%d+%d' % (master.winfo_rootx() + 50, master.winfo_rooty() + 50))
        self.protocol('WM_DELETE_WINDOW', lambda: self.cancel())

        self.bind('<Alt-a>', lambda event: self.apply())
        self.bind('<Alt-A>', lambda event: self.apply())

    def create_ok_cancel_buttons(self):
        Button(self.buttons, text=Globals.lang['button_ok'], width=Globals.button_width,
               command=lambda: self.apply()).grid(
            row=0, column=0)
        Button(self.buttons, text=Globals.lang['button_cancel'], width=Globals.button_width,
               command=lambda: self.cancel()).grid(row=0, column=1)

    def form_constructor(self, label, row):
        Label(self.body, text=label).grid(row=row, column=0, sticky='e')
        entry = Entry(self.body, width=30)
        entry.grid(row=row, column=1, sticky='w')
        string_to_insert = self.result.setdefault(label, '')
        if string_to_insert is None:
            string_to_insert = ''
        entry.insert(0, string_to_insert)
        self.entries[label] = entry
        if self.first_field is None:
            self.first_field = entry

    def text_field_constructor(self, label, value=''):
        def select_all_text(event):
            field = event.widget
            field.tag_add(SEL, '1.0', 'end')
            field.mark_set(INSERT, "1.0")
            field.see(INSERT)
            return 'break'

        Label(self.body, text=label).pack(side=TOP)

        textbox = ScrolledText(self.body)
        textbox.bind('<Control-Key-a>', lambda event: select_all_text(event))
        textbox.bind('<Control-Key-A>', lambda event: select_all_text(event))
        textbox.pack(side=BOTTOM, fill=BOTH, expand=True)
        textbox.insert('1.0', value)
        self.entries[label] = textbox
        if self.first_field is None:
            self.first_field = textbox

        # SQL buttons from module
        params = {'parent': self.upper, 'field': self.first_field, 'useButtons': self.use_sql_buttons}
        module_interface.runModules('TOPLEVEL', params)

    def show(self):
        self.wait_visibility()
        self.grab_set()
        self.focus_set()
        if self.first_field is not None:
            self.first_field.focus_set()
        self.wait_window()

    def apply(self):
        for key in self.entries:
            if isinstance(self.entries[key], Text):
                self.result[key] = self.entries[key].get('1.0', 'end')
            else:
                self.result[key] = self.entries[key].get()
        self.close()

    def cancel(self):
        self.entries.clear()
        self.close()

    def close(self):
        self.grab_release()
        self.parent.focus_set()
        self.destroy()

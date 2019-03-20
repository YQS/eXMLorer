# Encoding: UTF-8
from ttk import *


class FrameExtension(Frame):
    def __init__(self, master, **kw):
        Frame.__init__(self, master, **kw)
        self.dic = {}

    def add_widget(self, widget, key, parameters='', widget_object=None):
        if widget_object is None:
            exec_string = '%s(self)' % widget
            if parameters != '':
                exec_string = exec_string.replace(')', ', %s)' % parameters)
            print exec_string
            self.dic[key] = eval(exec_string)
        else:
            self.dic[key] = widget_object

        return self.dic[key]

    def clean(self):
        for widget in self.winfo_children():
            widget.destroy()

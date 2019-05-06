# Encoding: UTF-8

import tkMessageBox
import tkFileDialog

from config import Globals

default_warning_type = tkMessageBox.YESNOCANCEL
default_error_type = tkMessageBox.YES


def warning(message, warning_type=default_warning_type):
    return tkMessageBox.showwarning(Globals.app_name,
                                    message,
                                    type=warning_type)


def error(message):
    tkMessageBox.showerror(Globals.app_name,
                           message)


def get_default_filetypes():
    return [
        (Globals.lang['saveas_filetype_xml'], '.xml'),
        (Globals.lang['saveas_filetype_all'], '.*')
    ]


def file_dialog(filetypes=None):
    if filetypes is None:
        filetypes = get_default_filetypes()

    return tkFileDialog.asksaveasfilename(
        filetypes=filetypes,
        initialfile=Globals.config_filename,
        parent=Globals.app
    )

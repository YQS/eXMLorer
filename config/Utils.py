# Encoding: UTF-8

from config import Globals


def create_button(master, name, row, column, command=lambda: ''):
    if name not in master.app.exclude_buttons:
        button = master.add_widget('Button', name)
        button.configure(text=Globals.lang[name], width=Globals.button_width, command=command)
        button.grid(column=column, row=row)

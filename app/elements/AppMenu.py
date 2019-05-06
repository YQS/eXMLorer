# encoding: UTF-8
from Tkinter import *

from config import Globals, Language


class AppMenu(Menu):
    def __init__(self, app, **kw):
        Menu.__init__(self, app, **kw)
        app.config(menu=self)
        self.app = app
        self.fill()

    def fill(self):
        app = self.app

        if 'menu_file' not in app.exclude_buttons:
            menu_file = Menu(self, tearoff=0)
            self.add_cascade(label=Globals.lang['menu_file'], menu=menu_file)
            menu_file.add_command(label=Globals.lang['menu_file_open'], command=lambda: self.app.open_xml())
            menu_file.add_command(label=Globals.lang['menu_file_save'], command=lambda: App.saveXML(app, 'SAVE'))
            menu_file.add_command(label=Globals.lang['menu_file_saveas'], command=lambda: App.saveXML(app, 'SAVEAS'))
            menu_file.add_command(label=Globals.lang['menu_file_exit'], command=lambda: App.quit_app(app))

        if 'menu_config' not in app.exclude_buttons:
            # seteo menu Configuración
            menu_config = Menu(self, tearoff=0)
            self.add_cascade(label=Globals.lang['menu_config'], menu=menu_config)

            menu_config_language = Menu(self, tearoff=0)
            menu_config.add_cascade(label=Globals.lang['menu_config_language'] + ' ', menu=menu_config_language)

            # seteo lenguajes
            menu_config_language.add_checkbutton(label=Globals.lang['menu_config_language_spa'],
                                                 variable=app.bool_menu_config_lang_spa,
                                                 command=lambda: self.change_lang('SPA'))
            menu_config_language.add_checkbutton(label=Globals.lang['menu_config_language_eng'],
                                                 variable=app.bool_menu_config_lang_eng,
                                                 command=lambda: self.change_lang('ENG'))

            # menu de visualizacion
            menu_config_visualization = Menu(self, tearoff=0)
            menu_config.add_cascade(label=Globals.lang['menu_config_visualization'], menu=menu_config_visualization)
            menu_config_visualization.add_checkbutton(label=Globals.lang['menu_config_visualization_showcomments'],
                                                      variable=app.bool_menu_config_showComments,
                                                      command=lambda: self.switch_global_and_refresh('show_comments'))

            # seteo config de print modes
            menu_config_printmode = Menu(self, tearoff=0)
            menu_config.add_cascade(label=Globals.lang['menu_config_printmode'], menu=menu_config_printmode)
            menu_config_printmode.add_checkbutton(label=Globals.lang['menu_config_printmode_prettyprint'],
                                                  variable=app.bool_menu_config_prettyprint,
                                                  command=lambda: self.switch_global('pretty_print'))
            menu_config_printmode.add_checkbutton(label=Globals.lang['menu_config_printmode_nospaceclosedtag'],
                                                  variable=app.bool_menu_config_noSpaceInSelfClosingTag,
                                                  command=lambda: self.switch_global('no_spaces_in_closed_tag'))
            menu_config_printmode.add_checkbutton(label=Globals.lang['menu_config_printmode_linefyatsave'],
                                                  variable=app.bool_menu_config_linefyAtSave,
                                                  command=lambda: self.switch_global('no_spaces_in_closed_tag'))

            # menu de búsqueda
            menu_config_search = Menu(self, tearoff=0)
            menu_config.add_cascade(label=Globals.lang['menu_config_search'], menu=menu_config_search)
            menu_config_search.add_checkbutton(label=Globals.lang['menu_config_search_caseSensitive'],
                                               variable=app.bool_menu_config_caseSensitive,
                                               command=lambda: self.switch_global('case_sensitive'))

            # menu otros
            menu_config_others = Menu(self, tearoff=0)
            menu_config.add_cascade(label=Globals.lang['menu_config_others'], menu=menu_config_others)
            menu_config_others.add_checkbutton(label=Globals.lang['menu_config_others_SQLButtons'],
                                               variable=app.bool_menu_config_others_SQLButtons,
                                               command=lambda: self.switch_global('use_SQL_buttons'))
            menu_config_others.add_checkbutton(label=Globals.lang['menu_config_others_ShowFileFullPath'],
                                               variable=app.bool_menu_config_others_showFileFullPath,
                                               command=lambda: self.change_filename_label(
                                                   app.frames.menu.dic['label_filename']))

    def switch_global_and_refresh(self, variable_name):
        self.switch_global(variable_name)
        app.App.refreshTreeview(self.app)

    def switch_global(self, variable_name):
        if eval('Globals.' + variable_name):
            exec ('%s = False' % variable_name)
            Globals.config.update('Configuration', variable_name, 'False')
        else:
            exec ('%s = True' % variable_name)
            Globals.config.update('Configuration', variable_name, 'True')

    def change_lang(self, new_language):
        if new_language == 'ENG':
            new_dictionary = Language.english
            self.app.bool_menu_config_lang_eng.set(True)
            self.app.bool_menu_config_lang_spa.set(False)

        elif new_language == 'SPA':
            new_dictionary = Language.spanish
            self.app.bool_menu_config_lang_eng.set(False)
            self.app.bool_menu_config_lang_spa.set(True)

        else:
            return

        if new_dictionary['lang'] != Globals.lang['lang']:
            Globals.lang = new_dictionary
            Globals.config.update('Configuration', 'language', new_dictionary['lang'])
            self.app.refresh()
            # App.refreshTreeview(self.app)

    def change_filename_label(self, label_filename):
        self.switch_global('show_file_full_path')
        self.app.frames.button_bar.set_filename_label()

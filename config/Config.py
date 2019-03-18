# Encoding: UTF-8

import ConfigParser
from os.path import isfile

import app_language
import Globals


class ConfigFile:
    filename = ''

    def __init__(self):
        # global pretty_print, no_spaces_in_closed_tag, case_sensitive_search, use_sql_buttons, \
        #     show_comments, language, show_file_full_path, linefy_at_save
        self.filename = Globals.config_filename

        if not isfile(self.filename):
            self.create()

        # TODO: ver si el parser puede quedar instanciado con el objeto en vez de llamarlo en cada función
        config_parser = ConfigParser.RawConfigParser()
        config_parser.read(self.filename)

        Globals.pretty_print = config_parser.getboolean('Configuration', 'pretty_print')
        Globals.no_spaces_in_closed_tag = config_parser.getboolean('Configuration', 'no_spaces_in_closed_tag')
        Globals.linefy_at_save = config_parser.getboolean('Configuration', 'linefy_at_save')
        Globals.case_sensitive_search = config_parser.getboolean('Configuration', 'case_sensitive_search')
        Globals.use_sql_buttons = config_parser.getboolean('Configuration', 'use_sql_buttons')
        Globals.show_comments = config_parser.getboolean('Configuration', 'show_comments')
        Globals.show_file_full_path = config_parser.getboolean('Configuration', 'show_file_full_path')

        if config_parser.get('Configuration', 'language') != 'English':
            Globals.language = app_language.spanish
        else:
            Globals.language = app_language.english

    def create(self):
        config_parser = ConfigParser.RawConfigParser()
        config_parser.add_section('Configuration')
        config_parser.set('Configuration', 'pretty_print', 'True')
        config_parser.set('Configuration', 'no_spaces_in_closed_tag', 'True')
        config_parser.set('Configuration', 'linefy_at_save', 'True')
        config_parser.set('Configuration', 'case_sensitive_search', 'False')
        config_parser.set('Configuration', 'use_sql_buttons', 'False')
        config_parser.set('Configuration', 'show_comments', 'True')
        config_parser.set('Configuration', 'show_file_full_path', 'True')
        config_parser.set('Configuration', 'language', 'Español')
        with open(self.filename, 'wb') as configfile:
            config_parser.write(configfile)

    def update(self, section, field, value):
        config_parser = ConfigParser.RawConfigParser()
        config_parser.read(self.filename)

        config_parser.set(section, field, value)
        with open(self.filename, 'wb') as configfile:
            config_parser.write(configfile)

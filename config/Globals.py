# encoding: UTF-8

import Language
from app.dicext import DictionaryFile


# GLOBAL VARIABLES
last_folder_visited = ''
xml_tree = None
xml_encoding = ''
tags_in_tree_dictionary = {}
app = None
app_treeview = None
last_treeview_focus = None
config = None

# TEMP RELATED
temp_data_file = 'temp'
temp_data_sections = ['GLOBAL', 'FILE']

# MODULES GLOBALS
modules_directory = 'modules'
modules = {}

# CONFIGURABLES FROM CFG
config_filename = 'config.cfg'
pretty_print = True
no_spaces_in_closed_tag = True
linefy_at_save = True
case_sensitive_search = False
use_sql_buttons = False
show_comments = True
show_file_full_path = True
lang = Language.spanish

# SIZES
button_width = 15
label_button_width = 50
label_extra_button_width = 8

margin_to_extend_for_text = 30
data_column_text_size = 100

tag_subnames = DictionaryFile('namedic')

# MODULE: SQL Buttons

# importing eXMLorer directory to PYTHONPATH
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import re

from config import Globals as GL
from app import module_interface

context = 'TOPLEVEL'


def run(parent=None, field=None, use_buttons=True):
    if GL.use_sql_buttons and use_buttons:
        module_interface.create_button(parent, 'toplevel_sql_linefy', lambda: sql_button(field, simple_linefy),
                                       align='grid',
                                       align_params={'row': 0, 'column': 0})
        module_interface.create_button(parent, 'toplevel_sql_prettyprint', lambda: sql_button(field, simple_prettify),
                                       align='grid',
                                       align_params={'row': 0, 'column': 1})


def sql_button(field, action):
    # asumo que si uso estas funciones, el firstField es el campo que me interesa
    text = field.get('1.0', 'end')
    text = action(text)
    field.delete('1.0', 'end')
    field.insert('1.0', text)


# formatting functions (ex-sql_formatter)
def simple_prettify(raw_text):
    def insert_cr_after(text, word, times=1):
        return text.replace(word, '\n' * times + word)

    raw_text = raw_text.upper()
    raw_text = raw_text.replace(', ', ', \n')
    raw_text = insert_cr_after(raw_text, 'FROM', 2)
    raw_text = insert_cr_after(raw_text, 'LEFT JOIN')
    raw_text = insert_cr_after(raw_text, 'LEFT OUTER JOIN')
    raw_text = insert_cr_after(raw_text, 'WHERE', 2)
    raw_text = insert_cr_after(raw_text, 'ORDER BY', 2)
    raw_text = insert_cr_after(raw_text, 'GROUP BY', 2)
    raw_text = insert_cr_after(raw_text, 'LIMIT', 2)

    return raw_text


def simple_linefy(raw_text):
    return re.sub('[\s]+', ' ', raw_text.strip())

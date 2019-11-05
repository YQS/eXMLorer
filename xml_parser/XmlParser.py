# encoding: UTF-8

import xml.etree.ElementTree as ElementTree
import re
import StringIO

from config import Globals
import FileEncoding


class ParserWithComments(ElementTree.XMLParser):
    # robado del mismisimo autor del módulo ElementTree
    # http://effbot.org/zone/element-pi.htm
    def __init__(self, use_encoding):
        if use_encoding:
            ElementTree.XMLParser.__init__(self, encoding='utf-8')
        else:
            ElementTree.XMLParser.__init__(self)
        # asume ElementTree 1.2.X
        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(ElementTree.Comment, {})
        self._target.data(data)
        self._target.end(ElementTree.Comment)


def get_xml_root(filename, use_encoding=False):
    load_global_xml_tree(filename, use_encoding)
    return Globals.xml_tree.getroot()


def load_global_xml_tree(filename, use_encoding=False):
    try:
        parser = ParserWithComments(use_encoding)
        Globals.xml_tree = ElementTree.parse(filename, parser)
        Globals.xml_encoding = FileEncoding.get_encoding(filename)
    except ElementTree.ParseError:
        Globals.xml_tree = None
        raise Exception("not valid file")


def get_xml_root_from_string(string_xml):
    # se genera un objeto en memoria con StringIO para usar el ET.parse y que sin importar el origen, se parsee igual
    file_obj = StringIO.StringIO(string_xml)
    root = get_xml_root(file_obj, use_encoding=True)
    file_obj.close()
    return root


def get_xml_from_string(string_xml):
    # TODO: agregar la excepción en get_xml_root_from_string() y get_xml_root()
    return ElementTree.fromstring(string_xml)


def save_xml(xml_tree, filename):
    with open(filename, 'w') as file_obj:
        file_obj.write(get_string_from_xml_node(xml_tree.getroot()))


def get_string_from_xml_node(node, method='xml'):
    if Globals.pretty_print:
        prettify(node, linefy=Globals.linefy_at_save)

    # se agrega el encoding, si existe
    if Globals.xml_encoding != '':
        string_xml = ElementTree.tostring(node, Globals.xml_encoding, method=method)
    else:
        string_xml = ElementTree.tostring(node, method=method)

    if Globals.no_spaces_in_closed_tag:
        string_xml = string_xml.replace(' />', '/>')

    return string_xml


def prettify(elem, level=0, identation='	', linefy=False):
    """default indentation is Tab"""
    i = "\n" + level * identation
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + identation
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            prettify(elem, level + 1, linefy=linefy)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            if elem.text:
                if linefy:
                    # copiado de simple_linefy del modulo sql_buttons.py
                    elem.text = re.sub('[\s]+', ' ', elem.text.strip())
                else:
                    elem.text = elem.text.rstrip()


def new_element(parent, tag, text, attributes, position):
    element = ElementTree.Element(tag, attributes)
    insert_element(parent, element, position)
    element.text = text
    return element


def new_comment(parent, text, position):
    comment = ElementTree.Comment(text)
    insert_element(parent, comment, position)
    return comment


def insert_element(parent, element, position):
    parent.insert(position, element)


def move_tag(parent, tag, position):
    parent.remove(tag)
    parent.insert(position, tag)


def file_has_changed(root_tag, filename):
    try:
        root2 = ElementTree.parse(filename)
    except ElementTree.ParseError:
        print "couldn't parse filename"
        return None

    return ElementTree.tostring(root_tag).strip() != ElementTree.tostring(root2.getroot()).strip()

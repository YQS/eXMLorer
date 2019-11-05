# encoding: UTF-8

from operator import methodcaller
from ttk import *

from app.EdiTagEntry import EdiTagEntry
from config import Globals
from config.Utils import TagRelation
from xml_parser import XmlParser


class EdiTag(object):
    def __init__(self, xmltag, parent_editag, treeview=None, order='end', is_comment=False, is_root=False):
        self.id = None
        self.parent_editag = parent_editag
        self.xmltag = xmltag
        self.name = ''
        self.subname = ''
        self.treenode = None
        self.entry = None
        self.treeview = treeview
        self.treeview_order = order
        self.tag_order = 0
        self.is_comment = is_comment
        ##########
        self.set_xmltag_info()
        if is_root:
            self.root_set_tree_node()
        else:
            self.set_tree_node()
        self.set_column_value('data', self.xmltag.text)
        self.set_column_value('subname', self.subname)

    def __del__(self):
        self.parent_editag.remove(self.xmltag)
        if Globals.app_treeview.exists(self.id):
            Globals.app_treeview.delete(self.id)
        del Globals.editag_dictionary[self.id]

    def __repr__(self):
        return self.id

    def __iter__(self):
        # TODO optimize
        child_list = []
        for editag in Globals.editag_dictionary.values():
            if (editag.parent_editag is not None) and (editag.parent_editag.id == self.id):
                child_list.append(editag)
        child_list = sorted(child_list, key=methodcaller('get_xml_position'))

        for child in child_list:
            yield child

    # SETS
    def set_xmltag_info(self):
        if self.is_comment:
            self.name = '<!-- comment -->'
            self.subname = ''
        else:
            self.name = self.get_tag_name()
            self.subname = self.get_subname()

    def set_tree_node(self):
        # TODO: parent_editag viene como el xmltag, ver como trabajar con eso
        self.set_new_id()
        Globals.editag_dictionary[self.id] = self
        if self.treeview is None:
            # self.treeview = self.parent_editag.treeview
            self.treeview = Globals.app_treeview
            self.treenode = self.treeview.insert(self.parent_editag.id,
                                                 self.treeview_order,
                                                 self.id,
                                                 text=self.name)
        else:
            self.treenode = self.treeview.insert('',
                                                 self.treeview_order,
                                                 self.id,
                                                 text=self.name)

        if self.is_comment:
            self.treeview.tag_bind('comment', '<TreeviewOpen>', self.treenode)
            self.treeview.tag_configure('comment', background='green')

    def root_set_tree_node(self):
        self.set_new_id()
        Globals.editag_dictionary[self.id] = self
        self.treeview = Globals.app_treeview
        self.treenode = self.treeview.insert('',
                                             self.treeview_order,
                                             self.id,
                                             text=self.name)

    def set_column_value(self, column, value):
        if value is not None:
            value = value[:Globals.data_column_text_size].replace('\n', '')
            self.treeview.set(self.id, column, value)

    def has_child(self):
        for child in self.xmltag:
            return True
        return False

    def update_tag(self, new_tag, new_value):
        self.xmltag.tag = new_tag
        self.xmltag.text = new_value
        self.name = self.get_tag_name()
        self.subname = self.get_subname()

        self.treeview.item(self.id, text=self.name)
        self.set_column_value('data', self.xmltag.text)
        self.set_column_value('subname', self.subname)

    def update_subname(self, subname):
        self.subname = subname

    # GETS
    def get_tag_name(self):
        return '<' + self.xmltag.tag + '>'

    def get_tag_actual_name(self):
        return self.xmltag.tag

    def get_tag_value(self):
        try:
            return self.xmltag.text
        except:
            return ''

    def get_parent(self):
        try:
            return Globals.editag_dictionary[self.treeview.parent(self.id)]
        except KeyError:
            return None

    def get_treeview_index(self):
        return self.treeview.index(self.id)

    def get_xml_position(self):
        try:
            return self.parent_editag.xmltag.getchildren().index(self.xmltag)
        except ValueError:
            return '<Root>'

    def get_number_of_siblings(self):
        return len(self.parent_editag.xmltag.getchildren())

    def get_number_of_children(self):
        return len(self.xmltag.getchildren())

    def get_xml_path(self):
        if self.is_comment:
            tag_name = 'comment'
        else:
            tag_name = self.xmltag.tag

        if self.get_parent() is None:
            return tag_name
        else:
            return self.get_parent().get_xml_path() + '/' + tag_name

    def get_subname(self):
        subname = ''
        candidate_child = None
        candidate_tag_name = Globals.subnames.dic.get(self.xmltag.tag,
                                                      '*******')  # I hope that I don't find a tag like this!
        for xmlchild in self.xmltag:
            if type(xmlchild.tag).__name__ == 'str':
                # if child.tag is a XML tag and not a Comment
                if xmlchild.tag.find(candidate_tag_name, 0) >= 0:
                    try:
                        subname = str(xmlchild.text)
                    except UnicodeEncodeError:
                        subname = xmlchild.text.encode('utf-8')
                    break
                elif xmlchild.tag.find('Name', 0) >= 0:
                    candidate_child = xmlchild

        if subname == '':
            if candidate_child is not None:
                subname = str(candidate_child.text)
                Globals.subnames.update(self.xmltag.tag, candidate_child.tag)

        return subname

    def set_new_id(self):
        i = 0
        new_id = self.xmltag.tag + str(i)

        while new_id in Globals.editag_dictionary:
            i += 1
            new_id = self.xmltag.tag + str(i)
        Globals.editag_dictionary[new_id] = 0

        self.id = new_id

    def get_as_button_row(self, parent_band, row):
        self.get_as_label(parent_band, row)
        self.entry = EdiTagEntry(self, parent_band, self.get_tag_value(), row)

    def get_as_label(self, parent_band, row):
        Label(parent_band, text=self.get_tag_name()) \
            .grid(column=0, row=row, sticky='wn')

    def update_tree_node(self, new_value):
        self.xmltag.text = new_value
        self.set_column_value('data', new_value)
        return True

    @staticmethod
    def build(base_editag, mode, xml_tag=None, is_comment=False, text=''):
        if base_editag is not None:
            if base_editag.get_parent() is not None:
                # consigo datos para xml tag
                tag_label = ''
                if is_comment:
                    tag_label = 'comment'
                    xml_string = XmlParser.get_string_from_xml_node(base_editag.xmltag)
                    tag_text = xml_string[xml_string.find('\n') + 1:]
                elif text <> '':
                    tag_label = Globals.app.get_tag_from_user()
                    tag_text = text
                elif not xml_tag:
                    tag_label, tag_text = Globals.app.get_tag_from_user(get_value=True)

                # consigo datos para editag
                if (tag_label <> '') or (not xml_tag is None):
                    if mode == TagRelation.SIBLING:
                        parent_tag = base_editag.get_parent()
                        order = base_editag.get_treeview_index() + 1
                    elif mode == TagRelation.CHILD:
                        parent_tag = base_editag.xmltag
                        order = base_editag.get_number_of_children() +1

                # creo o inserto el tag en el XML
                if is_comment:
                    new_tag = XmlParser.new_comment(parent_tag, tag_text, order)
                elif xml_tag is None:
                    new_tag = XmlParser.new_element(parent_tag, tag_label, tag_text, {}, order)
                else:
                    XmlParser.insert_element(parent_tag, xml_tag, order)
                    new_tag = xml_tag

                # creo nuevo EdiTag
                new_editag = EdiTag(new_tag, base_editag, order=order, is_comment=is_comment)

                Globals.app_treeview.select_and_focus(new_editag.id)
                return new_editag

    @staticmethod
    def copy(old_editag, new_parent=None):
        if not old_editag is None:
            if new_parent:
                parent_tag = new_parent.xmltag
            else:
                parent_tag = old_editag.get_parent()

            order = old_editag.get_treeview_index() + 1

            new_tag = XmlParser.new_element(parent_tag,
                                            old_editag.xmltag.tag,
                                            old_editag.xmltag.text,
                                            old_editag.xmltag.attrib,
                                            order)
            new_editag = EdiTag(new_tag, parent_tag, order=order)

            for child_editag in old_editag:
                EdiTag.copy(child_editag, new_parent=new_editag)

            Globals.app_treeview.select_and_focus(new_editag.id)



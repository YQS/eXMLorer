# encoding: UTF-8

from operator import methodcaller
from ttk import *

from app.EdiTagEntry import EdiTagEntry
from config import Globals


class EdiTag(object):
    def __init__(self, xmltag, parent_editag, treeview=None, order='end', is_comment=False):
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
        self.set_tree_node()
        self.set_column_value('data', self.xmltag().text)
        self.set_column_value('subname', self.subname)

    def __del__(self):
        pass

    def __repr__(self):
        return self.id

    def __iter__(self):
        # TODO optimize
        child_list = []
        for editag in Globals.editag_dictionary.values():
            if editag.parent_id == self.id:
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

    def get_tag_name(self):
        return '<' + self.xmltag.tag + '>'

    def get_tag_value(self):
        try:
            return self.xmltag.text
        except:
            return ''

    def set_tree_node(self):
        self.set_new_id()
        if self.treeview is None:
            self.treeview = self.parent_editag.treeview
            self.treenode = self.treeview.insert(self.parent_editag.id,
                                                 self.treeview_order,
                                                 self.id,
                                                 text=self.name)
        else:
            self.treenode = self.treeview.insert(None,
                                                 self.treeview_order,
                                                 self.id,
                                                 text=self.name)

        if self.is_comment:
            self.treeview.tag_bind('comment', '<TreeviewOpen>', self.treenode)
            self.treeview.tag_configure('comment', background='green')

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
        self.set_column_value('data', self.xmltag().text)
        self.set_column_value('subname', self.subname)

    def update_subname(self, subname):
        self.subname = subname

    # GETS
    def get_parent(self):
        try:
            return Globals.editag_dictionary[self.treeview.parent(self.id)]
        except KeyError:
            return None

    def get_treeview_index(self):
        return self.treeview.index(self.id)

    def get_xml_position(self):
        try:
            return self.parent_editag.xmltag.getchildren().index(self.xmltag())
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

# encoding: UTF-8

import re
from operator import attrgetter

from config import Globals


class BasicSearch(object):
    def __init__(self, search_string, dictionary, mode, starting_point):
        self.search_string = search_string
        self.dictionary = dictionary
        self.starting_point = starting_point
        self.result = []
        self.output = None
        self.flags = 0

        self.number_tags()

        # defino si es case sensitive (y para otros flags del regex, si se llegan a usar)
        if not Globals.case_sensitive_search:
            self.flags = re.IGNORECASE

        if mode == 'XPath':
            self.xpath_search()
        else:
            # defino campo de busqueda
            if mode == 'Tags':
                self.attrName = 'tag'
            else:  # mode == 'Values' or 'Valores'
                self.attrName = 'text'

            # defino modo de busqueda
            if '*' in self.search_string:
                self.regex_search()
            else:
                self.simple_search()

    def output_generator(self):
        self.result = sorted(self.result, key=attrgetter('tag_order'))
        from_start = False

        while True:
            if len(self.result) > 0:
                for elem in self.result:
                    if from_start:
                        yield elem
                    else:
                        if elem.tag_order < self.starting_point:
                            continue
                        else:
                            from_start = True
                            yield elem
            else:
                yield ''

    def simple_search(self):
        self.search_string += '(.)*'

        for xTIG in self.dictionary.values():
            raw_text = getattr(xTIG.xmltag, self.attrName)
            if raw_text is None:
                raw_text = ''
            if re.search(self.search_string, raw_text, self.flags):
                self.result.append(xTIG)

        self.output = self.output_generator()

    def regex_search(self):
        pattern = self.search_string.replace('*', '(.)*').replace('?', '(.)')

        for xTIG in self.dictionary.values():
            if re.search(pattern, getattr(xTIG.xmltag, self.attrName), self.flags):
                self.result.append(xTIG)

        self.output = self.output_generator()

    def xpath_search(self):
        root = Globals.xml_tree.getroot()
        found_tags = root.findall(self.search_string)

        for xTIG in self.dictionary.values():
            if xTIG.xmltag in found_tags:
                self.result.append(xTIG)

        self.output = self.output_generator()

    def number_tags(self):
        def number_childs(editag, n):
            for child_editag in editag:
                child_editag.tag_order = n
                n += 1
                n = number_childs(child_editag, n)
            return n

        n = 1
        root_editag = Globals.editag_dictionary[Globals.xml_tree.getroot().tag]
        root_editag.tag_order = n
        n += 1
        number_childs(root_editag, n)


def xpath_search(path, tag=None):
    if tag is not None:
        return tag.findall(path)
    else:
        return Globals.xml_tree.getroot().findall(path)


'''
class XPathSearch(object):
	def __init__(self, root, path):
		self.root = root
		self.path = path
		#self.returnList = returnList
'''

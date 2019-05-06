# encoding: UTF-8
import os.path


class DictionaryFile(object):
    def __init__(self, filename):
        self.dic = {}
        self.filename = filename
        self.load_dictionary()

    def load_dictionary(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as txt:
                txt.write('')

        with open(self.filename, 'r') as txt:
            dic_as_string = txt.read()
            if dic_as_string != '':
                self.dic = eval(dic_as_string)
            else:
                self.dic = {}

    def save(self):
        with open(self.filename, 'w') as txt_file:
            dic_as_string = repr(self.dic).replace(',', ',\n\r')
            txt_file.write(dic_as_string)

    def update(self, key, value):
        self.dic[key] = value
        self.save()

    def delete(self, key):
        del self.dic[key]
        self.save()

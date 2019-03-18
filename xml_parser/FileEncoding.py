# encoding: UTF-8

import StringIO
import re


def get_encoding(filename):
    first_line = get_first_line(filename)
    return extract_encoding_from_first_line(first_line)


def get_first_line(file_candidate):
    if isinstance(file_candidate, StringIO.StringIO):
        return file_candidate.getvalue()
    else:
        # es un path
        with open(file_candidate, 'r') as fileObject:
            return fileObject.readline()


def extract_encoding_from_first_line(first_line):
    if first_line[0:2] == '<?':
        raw_encoding_string = regex_search_in_string('encoding=(\'|")(\S)*(\'|")', first_line)
        return clean_encoding_string(raw_encoding_string)
    else:
        return ''


def clean_encoding_string(encoding_string):
    return encoding_string.replace('encoding=', '').replace('\'', '').replace('"', '')


def regex_search_in_string(pattern, string):
    try:
        return re.search(pattern, string).group(0)
    except re.error:
        return ''

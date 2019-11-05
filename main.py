# encoding: UTF-8

import argparse

from config import Globals
from config import Config
from app import App, module_interface


def main(filepath=''):
    exclude_items_from_menu = ['button_analyze',
                               'button_glTreeView',
                               'button_dicSubnames',
                               'button_getDicSubnames',
                               'button_printEncoding',
                               'button_printPrettyPrint',
                               'button_showCurrentSearch',
                               'button_showDicTagsInTree',
                               'button_showXMLParentMap',
                               'button_showCaseSensitive',
                               'button_captureStringXML',
                               'button_showSearchResult',
                               'button_showSearchStartingPoint',
                               'button_lastFolder',
                               'button_foldTest',
                               'button_showChildQty',
                               ]

    Globals.config = Config.ConfigFile()
    module_interface.start_modules()

    Globals.app = App.App(exclude_buttons=exclude_items_from_menu)
    if filepath is not None:
        Globals.app.open_xml(filepath)

    Globals.app.focus_set()
    Globals.app.mainloop()

    try:
        Globals.app.destroy()
    except:
        pass


if __name__ == '__main__':
    # parsing CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', nargs="?")

    args = parser.parse_args()

    main(filepath=args.filepath)

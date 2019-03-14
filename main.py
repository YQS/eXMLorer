# encoding: UTF-8

import argparse

from config import globals as GL
from app import tk_app, module_interface as MOD


def main(mode='main', filepath=''):
    lExcludeMenu = ['button_analyze',
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

    GL.globalVarsStart()
    MOD.startModules()

    mainApp = tk_app.MainApp(lExcludeMenu=lExcludeMenu)
    # if filepath == None:
    #	tk_app.openXML(mainApp)
    # else:
    if filepath <> None:
        tk_app.openXML(mainApp, filename=filepath)

    mainApp.focus_set()
    mainApp.mainloop()

    try:
        mainApp.destroy()
    except:
        pass


if __name__ == '__main__':
    # parsing CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', nargs="?")

    args = parser.parse_args()

    main(filepath=args.filepath)

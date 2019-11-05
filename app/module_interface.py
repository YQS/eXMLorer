# encoding: UTF-8
# module interface

import os
from os.path import splitext
from Tkinter import *
from ttk import *

from config import Globals


def gather_modules():
    # busco que archivos .py existen dentro del directorio local /modules
    # module_path = os.getcwd() + '\\%s' % GL.moduleDirectory
    module_path = os.path.join(os.getcwd(), Globals.modules_directory)
    print 'module_path ' + module_path
    if os.path.exists(module_path):
        return [splitext(f)[0] for f in os.listdir(module_path) if (splitext(f)[1] == '.py') and ('__' not in f)]
    else:
        print "'%s' folder not found!" % Globals.modules_directory
        return []


def start_modules():
    modules = gather_modules()
    print 'load', modules
    for mod in modules:
        context = ''
        # exec('global %s' % mod)
        # import module
        command = 'import {modDir}.{mod} as {mod}'.format(modDir=Globals.modules_directory, mod=mod)
        print command
        exec (command, globals(), globals())
        # exec('import {modDir}.{mod}'.format(modDir=GL.moduleDirectory, mod=mod))
        # get context
        command = 'context = %s.context' % mod
        print command
        exec command
        # exec('context = %s.context' % mod)
        print 'context', context
        Globals.modules[mod] = context


def run_modules(context, params):
    for modPair in Globals.modules.items():
        print modPair
        # modPair = (modName, context)
        if modPair[1] == context:
            command = '{mod}.run(**params)'.format(mod=modPair[0])
            print command
            exec command


# BUILDERS

def create_button(parent, label, function, align='pack', align_params={}):
    button = Button(parent, text=Globals.lang[label], width=Globals.button_width, command=function)

    if align == 'pack':
        button.pack(**align_params)
    else:  # 'grid'
        button.grid(**align_params)

    return button


def create_menu_element(parent, label, function, state=ACTIVE):
    parent.add_command(label=Globals.lang[label], state=state, command=function)


'''
primero armo una lista de modulos a cargar (veo de buscar las carpetas, o algo)
una vez que tengo la lista, importo los modulos con start_modules()

cada modulo tiene que tener una funcion run(), que es la que crea los botones, comportamientos, etc.
cada modulo tiene que tener un contexto sobre el cual se ejecuta (elegir dentro de una lista estática)
en cada contexto posible (TOPLEVEL, TREEVIEW, TREEVIEW_MENU, etc) tiene que estar la función run_modules()
'''

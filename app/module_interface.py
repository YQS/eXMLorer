#encoding: UTF-8
#module interface

import os
from os.path import splitext
from Tkinter import *
from ttk import *

from config import globals as GL


def gatherModules():
	#busco que archivos .py existen dentro del directorio local /modules
	#module_path = os.getcwd() + '\\%s' % GL.moduleDirectory
	module_path = os.path.join(os.getcwd(), GL.moduleDirectory)
	print 'module_path ' + module_path
	if os.path.exists(module_path):
		return [splitext(f)[0]  for f in  os.listdir(module_path) if (splitext(f)[1] == '.py') and ('__' not in f)]
	else:
		print "'%s' folder not found!" % GL.moduleDirectory
		return []

def startModules():
	modules = gatherModules()
	print 'load', modules
	for mod in modules:
		xContext = ''
		#exec('global %s' % mod)
		#import module
		command = 'import {modDir}.{mod} as {mod}'.format(modDir=GL.moduleDirectory, mod=mod)
		print command
		exec(command, globals(), globals())
		#exec('import {modDir}.{mod}'.format(modDir=GL.moduleDirectory, mod=mod))
		#get context
		command = 'xContext = %s.context' % mod
		print command
		exec(command)
		#exec('xContext = %s.context' % mod)
		print 'xContext', xContext
		GL.moduleDic[mod] = xContext


def runModules(context, params):
	for modPair in GL.moduleDic.items():
		print modPair
		#modPair = (modName, context)
		if modPair[1] == context:
			command = '{mod}.run(**params)'.format(mod=modPair[0])
			print command
			exec(command)


#BUILDERS

def createButton(parent, label, function, align='pack', alignParams={}):
	button = Button(parent, text=GL.names[label], width=GL.buttonWidth, command=function)

	if align == 'pack':
		button.pack(**alignParams)
	else: #'grid'
		button.grid(**alignParams)

	return button

def createMenuElement(parent, label, function, state=ACTIVE):
	parent.add_command(label=GL.names[label], state=state, command=function)


'''
primero armo una lista de modulos a cargar (veo de buscar las carpetas, o algo)
una vez que tengo la lista, importo los modulos con startModules()

cada modulo tiene que tener una funcion run(), que es la que crea los botones, comportamientos, etc.
cada modulo tiene que tener un contexto sobre el cual se ejecuta (elegir dentro de una lista estática)
en cada contexto posible (TOPLEVEL, TREEVIEW, TREEVIEW_MENU, etc) tiene que estar la función runModules()
'''

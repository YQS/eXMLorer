# encoding: UTF-8

from Tkinter import *
from ttk import *
import main as MAIN

## GLOBALS

gl_buttonWidth = MAIN.gl_buttonWidth
gl_dicTagsInTree = MAIN.gl_dicTagsInTree
#gl_appTreeView = MAIN.gl_appTreeView
#gl_dicTagsInTree = MAIN.gl_dicTagsInTree

def fillMenuFrame(xFrame):
	mainApp = xFrame.master

	label_filename = xFrame.addWidget('Label', 'label_filename')
	label_filename.configure(padding=(10,0,0,0))
	label_filename.grid(column=3, row=0)
	
	button_open = xFrame.addWidget('Button', 'button_open')
	button_open.configure(text = 'Abrir', 
						 #image = ico_open,
						 width=gl_buttonWidth, 
						 command = lambda: MAIN.openXML(mainApp.frames.treeview, mainApp.frames.buttons, xFrame.dic['label_filename'] ))
	button_open.grid(column=0, row=0)
	
	button_save = xFrame.addWidget('Button', 'button_save')
	button_save.configure(text= 'Guardar', width= gl_buttonWidth, command= lambda: MAIN.saveXML(mainApp, 'SAVE'))
	button_save.grid(column=1, row=0)
	
	button_saveAs = xFrame.addWidget('Button', 'button_saveAs')
	button_saveAs.configure(text= 'Guardar como...', width= gl_buttonWidth, command= lambda: MAIN.saveXML(mainApp, 'SAVEAS'))
	button_saveAs.grid(column=2, row=0)
	
	button_copyTag = xFrame.addWidget('Button', 'button_copyTag')
	button_copyTag.configure(text='Copiar tag', 
							width= gl_buttonWidth, 
							command= lambda: MAIN.copyTagInTree(MAIN.gl_dicTagsInTree.setdefault( MAIN.gl_appTreeView.focus(), None), 0 ))
	button_copyTag.grid(column=0, row=1)
	
	#button_analyze = xFrame.addWidget('Button', 'button_analyze')
	#button_analyze.configure(text= 'Print band_buttons', width= gl_buttonWidth, command= lambda: MAIN.bCheckEntries(mainApp.frames.buttons))
	#button_analyze.grid(column=0, row=1)
	

class FrameExt(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.dic = {}
		
	def addWidget(self, sWidget, sKey):
		sCodeLine = '%s(self)' % sWidget
		print sCodeLine
		self.dic[sKey] = eval(sCodeLine)
		return self.dic[sKey]

class BandPack(object):
	def __init__(self):
		self.menu = None
		self.treeview = None
		self.buttons = None

class MainApp(Tk):
	def __init__(self, iconfile='test.gif'): #añadir opciones de generar botonos y bandas a eleccion
		Tk.__init__(self)
		self.title('eXMLorer')
		self.iconImage = PhotoImage(file= iconfile)
		self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
		
		#elementos del main
		self.frames = BandPack()
		
		self.frames.menu = FrameExt(self)
		self.frames.menu.pack(side=TOP, fill=X)
		fillMenuFrame(self.frames.menu)
		
		self.frames.treeview = FrameExt(self)
		self.frames.treeview.pack(side=LEFT, fill=BOTH)
		
		self.frames.buttons = FrameExt(self)
		self.frames.buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
		
		self.bind('<F5>', lambda event: refreshTreeView(event, self.frames.treeview, self.frames.buttons))
		
		
		
	
if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

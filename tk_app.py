# encoding: UTF-8

from Tkinter import *
from ttk import *
import globals as GL
import main as MAIN


def fillMenuFrame(xFrame, dicExcludeMenu):
	mainApp = xFrame.master

	if not 'label_filename' in dicExcludeMenu:
		label_filename = xFrame.addWidget('Label', 'label_filename')
		label_filename.configure(padding=(10,0,0,0))
		label_filename.grid(column=3, row=0)
	
	if not 'button_open' in dicExcludeMenu:
		button_open = xFrame.addWidget('Button', 'button_open')
		button_open.configure(text = 'Abrir', 
							 #image = ico_open,
							 width= GL.buttonWidth, 
							 command = lambda: MAIN.openXML(mainApp.frames.treeview, mainApp.frames.buttons, xFrame.dic['label_filename'] ))
		button_open.grid(column=0, row=0)
		
	if not 'button_save' in dicExcludeMenu:
		button_save = xFrame.addWidget('Button', 'button_save')
		button_save.configure(text= 'Guardar', width= GL.buttonWidth, command= lambda: MAIN.saveXML(mainApp, 'SAVE'))
		button_save.grid(column=1, row=0)
	
	if not 'button_saveAs' in dicExcludeMenu:
		button_saveAs = xFrame.addWidget('Button', 'button_saveAs')
		button_saveAs.configure(text= 'Guardar como...', width= GL.buttonWidth, command= lambda: MAIN.saveXML(mainApp, 'SAVEAS'))
		button_saveAs.grid(column=2, row=0)
	
	if not 'button_copyTag' in dicExcludeMenu:
		button_copyTag = xFrame.addWidget('Button', 'button_copyTag')
		button_copyTag.configure(text='Copiar tag', 
								width= GL.buttonWidth, 
								command= lambda: MAIN.copyTagInTree(GL.dicTagsInTree.setdefault( GL.appTreeView.focus(), None), 0 ))
		button_copyTag.grid(column=0, row=1)
		
	if not 'button_deleteTag' in dicExcludeMenu:
		button_deleteTag = xFrame.addWidget('Button', 'button_deleteTag')
		button_deleteTag.configure(text='Borrar tag',
								   width= GL.buttonWidth, 
								   command= lambda: MAIN.deleteTagInTree( GL.appTreeView.focus() ))
		button_deleteTag.grid(column=1, row=1)
	
	def checkTreeView():
		if GL.appTreeView == None:
			print 'TreeView does not exist'
		else:
			print 'TreeView is A-OK!'
		
	if not 'button_glTreeView' in dicExcludeMenu:
		button_glTreeView = xFrame.addWidget('Button', 'button_glTreeView')
		button_glTreeView.configure(text='Check TreeView',
									width= GL.buttonWidth,
									command= lambda: checkTreeView())
		button_glTreeView.grid(column=1, row=1)
	
	if not 'button_analyze' in dicExcludeMenu:
		button_analyze = xFrame.addWidget('Button', 'button_analyze')
		button_analyze.configure(text= 'Print band_buttons', width= GL.buttonWidth, command= lambda: MAIN.bCheckEntries(mainApp.frames.buttons))
		button_analyze.grid(column=0, row=1)
	

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
	def __init__(self, iconfile='test.gif', dicExcludeMenu = []): #añadir opciones de generar botonos y bandas a eleccion
		Tk.__init__(self)
		self.title('eXMLorer')
		self.iconImage = PhotoImage(file= iconfile)
		self.tk.call('wm', 'iconphoto', self._w, self.iconImage)
		
		#elementos del main
		self.frames = BandPack()
		
		self.frames.menu = FrameExt(self)
		self.frames.menu.pack(side=TOP, fill=X)
		fillMenuFrame(self.frames.menu, dicExcludeMenu)
		
		self.frames.treeview = FrameExt(self)
		self.frames.treeview.pack(side=LEFT, fill=BOTH)
		
		self.frames.buttons = FrameExt(self)
		self.frames.buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
		
		self.bind('<F5>', lambda event: MAIN.refreshTreeView(event, self.frames.treeview, self.frames.buttons))
		
		
if __name__ == '__main__':
	mainApp = MainApp('test.gif')
	mainApp.mainloop()
	try:
		mainApp.destroy()
	except:
		print 'error trying to close mainApp'

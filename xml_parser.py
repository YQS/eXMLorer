# encoding: UTF-8

import xml.etree.ElementTree as ET
from Tkinter import *
from ttk import *
import tkFileDialog
import TagInTree as TIG

################
def getFilename():
	filename = tkFileDialog.askopenfilename(defaultextension='xml')
	print filename
	return filename

def cleanFrame(frame):
	for widget in frame.winfo_children():
		widget.destroy()

def getXML(filename):
	#parseo el xml y instancio el root, para analizarlo todo
	tree = ET.parse(filename)
	#tree = ET.parse('stylers.xml')
	root = tree.getroot()

	print root.tag
	print root.attrib
	print

	#funcion para imprimir el tag y todos sus child
	def showChilds(xBase, xLevel):
		xText = "	" * xLevel
		for xChild in xBase:
			print xText + xChild.tag
			showChilds(xChild, xLevel + 1)

	print root.tag
	showChilds(root, 1)
	
	return root

def getIDForTreeView(xTag, dicTagsInTree):
	i = 0
	while dicTagsInTree.has_key(xTag + str(i)):
		i += 1
	dicTagsInTree[xTag + str(i)] = 0
	return xTag + str(i)

def addXMLToTree(xBase, xBaseID, dicTagsInTree, appTreeView):
	for xChild in xBase:
		xID = getIDForTreeView(xChild.tag, dicTagsInTree)
		dicTagsInTree[xID] = TIG.TagInTree(xBaseID, xID, xChild, appTreeView)
		addXMLToTree(xChild, xID, dicTagsInTree, appTreeView)
		
def getTreeView(mainApp, band_buttons, dicTagsInTree):
	appTreeView = Treeview(mainApp, columns=('data','name', 'size')) #, height=20
	appTreeView.pack(side="left",fill=BOTH)
	
	scroll_treeview = Scrollbar(mainApp,command=appTreeView.yview)
	appTreeView.configure(yscrollcommand=scroll_treeview.set)
	scroll_treeview.pack(side="right",fill="y")
	
	appTreeView.column('data', width=500, anchor='w')
	appTreeView.column('name', width=200, anchor='e')
	appTreeView.column('size', width=200, anchor='e')
	appTreeView.heading('data', text='Data')
	appTreeView.heading('name', text='Nombre')
	appTreeView.heading('size', text='Tamanio')
	
	#indico que solo muestre la columna 'data'
	appTreeView.configure(displaycolumns=('data'))
	
	
	def fillBandButtons(event, band_buttons, dicTagsInTree):
		cleanFrame(band_buttons)
		
		def updateTreeNode(value, oTagInTree):
			#print entry.get()
			print value
			oTagInTree.getTag().text = value
			oTagInTree.setColumn( 'data', value)
			return True
		
		#######
		def getEntry(value, band_buttons, xRow, oTagInTree):
			xBoolOptions = ('True', 'False')
			xButtonWidth = 50
			if value in xBoolOptions:
				'''
				print 'OptionMenu'
				xStringVar = StringVar()
				xStringVar.set(value)
				OptionMenu(band_buttons, xStringVar, 'True', 'False').grid(column=1, row=xRow)
				'''
				print 'Combobox'
				xCombobox = Combobox(band_buttons, values=xBoolOptions, width=(xButtonWidth - 3), validate='focus')
				xCombobox.configure(validatecommand = lambda xCombobox=xCombobox, oTagInTree=oTagInTree: updateTreeNode(xCombobox.get(), oTagInTree) )
				xCombobox.grid(column=1, row=xRow)
				xCombobox.set(value)
			elif value == '':
				print 'disEntry'
				xEntry = Entry(band_buttons, width=xButtonWidth)
				xEntry.grid(column=1, row=xRow)
				if oTagInTree.hasChild():
					xEntry.insert(0, '<...>')
				xEntry.configure(state=DISABLED)
				#xEntry.insert(0, value)
			else:
				print 'Entry'
				xEntry = Entry(band_buttons, width=xButtonWidth, validate='focus')
				xEntry.configure(validatecommand = lambda xEntry=xEntry, oTagInTree=oTagInTree: updateTreeNode(xEntry.get(), oTagInTree))
				xEntry.grid(column=1, row=xRow)
				xEntry.insert(0, value)
		
		def getLabel(name, band_buttons, xRow):
			Label(band_buttons, text=name).grid(column=0, row=xRow, sticky='w')
			
		def getButtonRow(id, band_buttons, xRow):
			getLabel(dicTagsInTree[id].tagname, band_buttons, xRow)
			try:
				value = dicTagsInTree[id].getTag().text.strip()
			except:
				value = ''
			getEntry(value, band_buttons, xRow, dicTagsInTree[id])
		#######
		
		appTreeView = event.widget
		xIDFocus = appTreeView.focus()
		print 'focus in ' + xIDFocus 
		print 'is in dicTagsInTree? ' + str(xIDFocus in dicTagsInTree)
		
		xRow = 0
		xStringVar = StringVar()
		xGotItems = False
		
		for xIDChild in appTreeView.get_children(xIDFocus):
			xGotItems = True
			getButtonRow(xIDChild, band_buttons, xRow)
			xRow += 1
		
		if not xGotItems:
			getButtonRow(xIDFocus, band_buttons, xRow)
			
		
	#appTreeView.bind('<1>', lambda event, band_buttons = band_buttons, appTreeView = appTreeView, xFocus=appTreeView.focus(): getLabel(event, band_buttons, appTreeView, xFocus))
	appTreeView.bind('<<TreeviewSelect>>', lambda event, 
												  band_buttons = band_buttons,
												  dicTagsInTree = dicTagsInTree:
												  fillBandButtons(event, band_buttons, dicTagsInTree))
	
	return appTreeView

def openXML(band_treeview, band_buttons, label_filename):
	cleanFrame(band_treeview)
	cleanFrame(band_buttons)
	
	filename = getFilename()
	root = getXML(filename)
	#root = getXML('stylers.xml')
	
	label_filename.config(text=filename)
	
	dicTagsInTree = {}
	appTreeView = getTreeView(band_treeview, band_buttons, dicTagsInTree)
	
	dicTagsInTree[root.tag] = TIG.TagInTree('', root.tag, root, appTreeView)
	addXMLToTree(root, root.tag, dicTagsInTree, appTreeView)
	
def checkEntries(band_buttons):
	for widget in band_buttons.winfo_children():
		if isinstance(widget, Entry):
			print widget.get()
	
	
def main():
	mainApp = Tk()
	mainApp.title('eXMLorer')
	mainApp.update()		#hace que el getFilename no deje abierta una ventana
	
	band_menu = Frame(mainApp)
	band_menu.pack(side=TOP, fill=X)
	
	band_treeview = Frame(mainApp)
	band_treeview.pack(side=LEFT, fill=BOTH)
	
	band_buttons = Frame(mainApp)
	band_buttons.pack(side=LEFT, fill=BOTH, ipadx=0, pady=20)
	
	label_filename = Label(band_menu, padding=(10,0,0,0))
	label_filename.grid(column=1, row=0)
	
	button_open = Button(band_menu, 
						 text = 'Abrir', 
						 width=15, 
						 command = lambda band_treeview=band_treeview, 
										  band_buttons=band_buttons,
										  label_filename=label_filename: 
										  openXML(band_treeview, band_buttons, label_filename))
	button_open.grid(column=0, row=0)
	
	button_analyze = Button(band_menu, text= 'Print band_buttons', width=15, command= lambda band_buttons = band_buttons: checkEntries(band_buttons))
	button_analyze.grid(column=0, row=1)
	
	openXML(band_treeview, band_buttons, label_filename)
	mainApp.focus_set()
	mainApp.mainloop()

if __name__ == '__main__':
	main()

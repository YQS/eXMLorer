import xml.etree.ElementTree as ET
from Tkinter import *
from ttk import *
import tkFileDialog

################
def getFilename():
	filename = tkFileDialog.askopenfilename(defaultextension='xml')
	print filename
	return filename

def cleanFrame(frame):
	for widget in frame.winfo_children():
		widget.destroy()
		
def inList(list, selectedElement):
	found = False
	for element in list:
		if element == selectedElement:
			found = True
			break
			
	return found
	

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

def getIDForTreeView(xTag, dicIDsTreeView):
	i = 0
	while dicIDsTreeView.has_key(xTag + str(i)):
		i += 1
	dicIDsTreeView[xTag + str(i)] = 0
	return xTag + str(i)
	
def getNameOfTag(xTag):
	xName = ''
	for xChild in xTag:
		if (xChild.tag.find('Name', 0) >= 0):
			xName = xChild.text
			break
			
	#if xName == '':
	#	xName = xTag.tag
		
	return xName

def addXMLToTree(xBase, xBaseID, dicIDsTreeView, appTreeView):
	for xChild in xBase:
		xID = getIDForTreeView(xChild.tag, dicIDsTreeView)
		dicIDsTreeView[xID] = appTreeView.insert(xBaseID, 'end', xID, text="<" + xChild.tag + "> " + getNameOfTag(xChild))
		appTreeView.set(xID, 'name', xID)
		appTreeView.set(xID, 'data', xChild.text)
		appTreeView.set(xID, 'size', getNameOfTag(xChild))
		
		addXMLToTree(xChild, xID, dicIDsTreeView, appTreeView)
		
def getTreeView(mainApp, band_buttons):
	appTreeView = Treeview(mainApp, columns=('data','name', 'size')) #, height=20
	appTreeView.pack(side="left",fill=BOTH)
	
	myscrollbar=Scrollbar(mainApp,command=appTreeView.yview)
	appTreeView.configure(yscrollcommand=myscrollbar.set)
	myscrollbar.pack(side="right",fill="y")
	
	appTreeView.column('data', width=500, anchor='w')
	appTreeView.column('name', width=200, anchor='e')
	appTreeView.column('size', width=200, anchor='e')
	appTreeView.heading('data', text='Data')
	appTreeView.heading('name', text='Nombre')
	appTreeView.heading('size', text='Tamanio')
	
	#indico que solo muestre la columna 'data'
	appTreeView.configure(displaycolumns=('data'))
	
	
	def getLabels(event, band_buttons):
		cleanFrame(band_buttons)
		
		appTreeView = event.widget
		xIDFocus = appTreeView.focus()
		print 'focus in ' + xIDFocus 
		
		xRow = 0
		xStringVar = StringVar()
		xGotLabel = False
		
		#******
		
		def getButton(value, band_buttons, xRow):
			xBoolOptions = ('True', 'False')
			xButtonWidth = 50
			if inList(xBoolOptions, value):
				'''
				print 'OptionMenu'
				xStringVar = StringVar()
				xStringVar.set(value)
				OptionMenu(band_buttons, xStringVar, 'True', 'False').grid(column=1, row=xRow)
				'''
				print 'Combobox'
				xCombobox = Combobox(band_buttons, values=xBoolOptions, width=(xButtonWidth - 3))
				xCombobox.grid(column=1, row=xRow)
				xCombobox.set(value)
			elif value == '':
				print 'disButton'
				xEntry = Entry(band_buttons, width=xButtonWidth, state=DISABLED)
				xEntry.grid(column=1, row=xRow)
				#xEntry.insert(0, value)
			else:
				print 'Button'
				xEntry = Entry(band_buttons, width=xButtonWidth)
				xEntry.grid(column=1, row=xRow)
				xEntry.insert(0, value)
		
		#*****
		
		for xIDChild in appTreeView.get_children(xIDFocus):
			xGotLabel = True
			xLabelText = appTreeView.item( xIDChild, 'text')
			xLabelText = xLabelText[0 : xLabelText.find('>', 0) + 1]
			Label(band_buttons, text = xLabelText ).grid(column=0, row=xRow, sticky='w')
			#xStringVar.set( appTreeView.item( xIDChild, 'values')[0] )
			try:
				value = appTreeView.item( xIDChild, 'values')[0].strip()
			except:
				value = ''
			print value
			getButton(value, band_buttons, xRow)
			xRow += 1
		
		if not xGotLabel:
			Label(band_buttons, text=appTreeView.item(xIDFocus, 'text')).grid(column=0, row=0)
			try:
				value = appTreeView.item( xIDFocus, 'values')[0].strip()
			except:
				value = ''
			print value
			getButton(value, band_buttons, xRow)
			xRow += 1
			
		
	#appTreeView.bind('<1>', lambda event, band_buttons = band_buttons, appTreeView = appTreeView, xFocus=appTreeView.focus(): getLabel(event, band_buttons, appTreeView, xFocus))
	appTreeView.bind('<<TreeviewSelect>>', lambda event, band_buttons = band_buttons: getLabels(event, band_buttons))
	
	
	return appTreeView

def openXML(band_treeview, band_buttons, label_filename):
	cleanFrame(band_treeview)
	cleanFrame(band_buttons)
	
	filename = getFilename()
	root = getXML(filename)
	#root = getXML('stylers.xml')
	
	label_filename.config(text=filename)
	
	appTreeView = getTreeView(band_treeview, band_buttons)
	
	dicIDsTreeView = {}
	dicIDsTreeView[root.tag] = appTreeView.insert('', 0, root.tag, text="<" + root.tag + ">")
	addXMLToTree(root, root.tag, dicIDsTreeView, appTreeView)
		
	
def main():
	mainApp = Tk()
	mainApp.title('eXMLplorer')
	mainApp.update()		#hace que el getFilename no deje abierta una ventana
	
	band_menu = Frame(mainApp)
	band_menu.pack(side=TOP, fill=X)
	
	band_treeview = Frame(mainApp)
	band_treeview.pack(side=LEFT, fill=BOTH)
	
	band_buttons = Frame(mainApp)
	band_buttons.pack(side=RIGHT, fill=BOTH, ipadx=0, pady=20)
	
	label_filename = Label(band_menu, padding=(10,0,0,0))
	label_filename.grid(column=1, row=0)
	
	button_open = Button(band_menu, 
						 text = "Abrir", 
						 width=15, 
						 command = lambda band_treeview=band_treeview, 
										  band_buttons=band_buttons,
										  label_filename=label_filename: 
										  openXML(band_treeview, band_buttons, label_filename))
	button_open.grid(column=0, row=0)
	
	openXML(band_treeview, band_buttons, label_filename)
	mainApp.focus_set()
	mainApp.mainloop()

if __name__ == '__main__':
	main()

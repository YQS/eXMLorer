# encoding: UTF-8

import globals as GL
import tk_app

def main(mode = 'main'):
	lExcludeMenu = ['button_analyze', 
					'button_glTreeView',
					'button_dicSubnames',
					'button_getDicSubnames',
					'button_printEncoding'
					]

	mainApp = tk_app.MainApp(lExcludeMenu=lExcludeMenu)
	tk_app.openXML(mainApp.frames.treeview, mainApp.frames.buttons, mainApp.frames.menu.dic['label_filename'])
		
	#mainApp.focus_set()
	mainApp.mainloop()
	
	try:
		mainApp.destroy()
	except:
		pass

if __name__ == '__main__':
	main('testing')

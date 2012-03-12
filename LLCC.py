# Lobo LessCSS Compiler
# Version: 1.0
# License: MIT
# Author: Luis Lobo Borobia
# Email: lobo@fictioncity.net, luislobo@gmail.com
# Uses https://github.com/seb-m/pyinotify to get notifications from file disk
# Uses libnode-less Ubuntu package for compiling LESS files
"""
Lobo LessCSS Compiler

@author: Luis Lobo Borobia
@license: MIT License
@contact: luislobo@gmail.com
"""
import os
import wx
import pyinotify
import json

def alert(message):
	wx.MessageBox(message, 'Alert', wx.OK | wx.ICON_INFORMATION)

class MainWindow(wx.Frame):
	def __init__(self, parent, title):

		# Initializes pyinotify objects
		self.wm = pyinotify.WatchManager()
		self.notifier = None
		
		# Create main frame
		wx.Frame.__init__(self, parent, title=title, size=(400, 500))

		# Init the GUI
		self.InitGUI()

		#show GUI
		self.Show(True)

	def OnExit(self, e):
		self.Close(True)  # Close the frame.

	def InitGUI(self):
		
		# Main Panel
		self.mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
		
		# add button to pannel
		hbButtons = wx.BoxSizer(wx.HORIZONTAL)
		self.addButton = wx.Button(self.mainPanel, 1, "Add Directory to watch")
		self.startButton = wx.ToggleButton(self.mainPanel, 2, "Start watching")
		hbButtons.Add(self.addButton, 2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
		hbButtons.Add(self.startButton, 2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

		# Add config list to panel
		self.configList = ConfigListBox(self.mainPanel)

		# Add controls to vertical box sizer
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbButtons, 0, flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, border=5)
		vbox.Add(wx.StaticText(self.mainPanel, -1, "Folders being watched", style=wx.ALIGN_CENTRE),
			0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
		vbox.Add(self.configList, 2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

		self.mainPanel.SetSizer(vbox)

		# A StatusBar in the bottom of the window
		self.statusBar = self.CreateStatusBar() 

		# Setting up the menu.
		filemenu = wx.Menu()

		# wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
		self.menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		self.Centre()

		# Set events.
		self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
		self.Bind(wx.EVT_BUTTON, self.OnAdd, self.addButton)
		self.Bind(wx.EVT_TOGGLEBUTTON, self.OnStartWatching, self.startButton)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

	def OnClose(self, event):
		# stop notifier
		self.StopWatching()
		self.configList.saveList()
		self.Destroy()

	def StartWatching(self):
		# TODO: handle a better way to see if thread is running
		if self.notifier is None:
			self.notifier = pyinotify.ThreadedNotifier(self.wm, EventHandler())
			self.notifier.start()
			for directory in self.configList.Items:
				self.AddPathToWatch(directory)
				self.setSBMessage("Adding: " + directory)
			self.setSBMessage("Watching...")
		
	def StopWatching(self):
		# TODO: handle a better way to see if thread is running
		if not self.notifier is None:
			for directory in self.wm.watches():
				self.wm.rm_watch(directory, True, True)
			self.notifier.stop()
			self.notifier = None
		self.setSBMessage("Not Watching...")

	def AddPathToWatch(self, path):
		# watched events
		mask = pyinotify.IN_CLOSE_WRITE
		self.wdd = self.wm.add_watch(path, mask, rec=True)

	def OnAdd(self, event):
		self.OpenDirectory()

	def OnStartWatching(self, event):
		# TODO: handle a better way to see if thread is running
		# If it's pressed, means it is already running
		startIsPressed = self.startButton.GetValue()

		if startIsPressed:
			self.startButton.SetLabel("Stop Watching")
			self.StartWatching()
		else:
			self.startButton.SetLabel("Start Watching")
			self.StopWatching()
		
	def OpenDirectory(self):
		dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
		if dlg.ShowModal() == wx.ID_OK:
			self.configList.Append(dlg.GetPath())
			self.configList.saveList()
			self.AddPathToWatch(dlg.GetPath())
		dlg.Destroy()
		
	def setSBMessage(self, message):
		frame.statusBar.SetStatusText(message)

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CLOSE_WRITE(self, event):
		fileName, fileExtension = os.path.splitext(event.pathname)
		if fileExtension == ".less":
			frame.setSBMessage("Compiling: " + fileName + '.css')
			#os.system('lessc -x %s > %s' % (event.pathname, fileName + '.css'))
			frame.setSBMessage("Compiled: " + fileName + '.css')

class ConfigListBox(wx.ListBox):

	def __init__(self, *args, **kwargs):
		wx.ListBox.__init__(self, *args, **kwargs)
		self.config = wx.Config("LLCCConfig")
		self.fillList()

	def fillList(self):
		dirsToWatch = None
		try:
			# load rows and check for error too, if no data
			if self.config.Exists(u"DirectoriesToWatch"):
				dirsToWatch = str(self.config.Read(u"DirectoriesToWatch", ""))
				if not dirsToWatch == "":
					self.Items = json.loads(dirsToWatch)
		except:
			pass

	def saveList(self):
		itemsJson = json.dumps(self.Items)
		self.config.Write("DirectoriesToWatch", itemsJson)
		self.config.Flush()

if __name__ == '__main__':
	app = wx.App(False)
	frame = MainWindow(None, "Lobo LessCSS compiler")
	app.MainLoop()

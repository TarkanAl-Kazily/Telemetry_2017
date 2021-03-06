#!/usr/bin/env python
try:  # import as appropriate for 2.x vs. 3.x
	import tkinter as tk
except:
	import Tkinter as tk
import graphics as gw
import display as disp
import threading
import time
from tkFileDialog import askopenfilename

class ThreadManager():
	
	def __init__(self):
		self.threads = {}
		self.size = 0
		
	def addThread(self, name, thread):
		self.threads.update({name:thread})
		
	def getThread(self, name):
		try:
			if (self.threads.has_key(name)):
				self.size = self.size + 1
				return self.threads.get(name)
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
		return None
	
	def pauseThread(self, name):
		try:
			if (self.threads.has_key(name)):
				self.threads[name].paused.set()
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
	def stopThread(self, name):
		try:
			if (self.threads.has_key(name) and 
				self.threads[name].running.isSet()):
				self.threads[name].paused.clear()
				self.threads[name].running.clear()
				self.threads[name].join()
				self.removeThread(name)
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
	
	def isRunning(self, name):
		try:
			if (self.threads.has_key(name)):
				return self.threads[name].running.isSet()
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
		return False
	
	def isPaused(self, name):
		try:
			if (self.threads.has_key(name)):
				return self.threads[name].paused.isSet()
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
		return False
	
	#FIX THIS 
	def removeThread(self, name):
		try:
			if (self.threads.has_key(name)):
				self.size = self.size - 1
				del self.threads[name]
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
	def numberKeys(self):
		return self.size
	
	def resumeThread(self, name):
		try:
			if (self.threads.has_key(name)):
				if (self.isPaused(name)):
					self.threads[name].paused.clear()
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
	
	def contains(self, name):
		try:
			return name in self.threads
		except (AttributeError, TypeError):
			raise AssertionError('Wrong type')
		
#Class which  creates a user interface window 
class Application(tk.Frame):
	"""
		initializes the frames 
	"""
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.windows={}#Dictionary to hold windows
		self.windowList = [None] * 5
		self.tm = ThreadManager() #house all the threads
		self.pathName = 'test_script.txt'
		self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
		self.createWidgets()

		master.minsize(width=666, height=666)#Change to new window

	def createWidgets(self):
		top=self.winfo_toplevel() 
		top.rowconfigure(0, weight=1) 
		top.columnconfigure(0, weight=1) 
		self.rowconfigure(0, weight=1) 
		self.columnconfigure(0, weight=1) 
		
		#Quit Button
		self.quitB = tk.Button(self, text='Quit', command=self.quit)
		self.quitB.grid(row=0, column=8, sticky=tk.N+tk.E)
		
		#File selection button
		self.fileS = tk.Button(self, text='Select Script', command=self.fsel)
		self.fileS.grid(row=0, column=7, sticky=tk.N+tk.E)
		
		#Unnecessary without multi window functionality 
		#Window button
		#self.addWinB = tk.Button(self, text='New Window', command=self.insertWindow)
		#self.addWinB.grid(row=0, column=6, columnspan=2,sticky=tk.N+tk.E)
		
		self.insertWindow()

	# Method for opening a filepath
	def fsel(self):
		if (not self.tm.isRunning(self.activeName)):
			filename = askopenfilename()
			self.pathName = filename
			print filename
		else:
			print 'thing running no blocking'

	# Overrides the default functionality for quitting the Frame
	# while attempting to shut down all currently active threads
	def quit(self):
		try:
			self.stop_all()
		except:
			print "Error: deletion issues"
		finally:
			tk.Frame.quit(self)

	# Makes a new window in the scope of the Frame
	def insertWindow(self):
		#limit to the number of threads which can be run simultaneously
		if (len(self.windows) < 1):
			
			index = len(self.windows)
			name = "DataWin " + str(index)
			self.setUpWindow(name)
			
			#Unnecessary without multi window functionality 
			#Window Button 
			#self.windowList[index] = name
			#self.v = tk.StringVar()
			#self.v.set(self.windowList[0])
			#self.winOM = tk.OptionMenu(self,self.v, *self.windowList,command=self.selectOpt)
			#self.winOM.grid(row=3, column=0)
			
			#Start Test button
			self.winStartB = tk.Button(self, text='Start Test',
									   command=self.start_test)
			self.winStartB.grid(row=1, column=6)
			
			#pause Test button
			self.winPauseB = tk.Button(self, text='Pause',
									   command=self.pause_test)
			self.winPauseB.grid(row=1, column=7)
			
			#Stop Test button
			self.winStopB = tk.Button(self, text='Stop', command=self.stop_test)
			self.winStopB.grid(row=1, column=8)
		
			root.update()

	# Initializes a new window with the given name
	def setUpWindow(self, name):
		#Set up window and display
		newWin = gw.GraphWin("Data",1200 ,600 , master=self)
		newWin.grid(row=2, column=0, columnspan=20, rowspan=5)

		#set as active window and add to window dictionary
		self.activeWindow = newWin
		self.activeName = name
		self.windows.update({name : newWin})
		
		dWin = disp.DataWindow(name=name, kwargs={'window':self.activeWindow,
												  'path':self.pathName})
		dWin.setUp()
		
		self.tm.addThread(name, dWin)

	# Starts running the test and collecting data in the active window
	def start_test(self):
		name = self.activeName
		if(not self.tm.isRunning(name)):
			if (self.tm.getThread(self.activeName) == None):
				self.setUpWindow(self.activeName)
			t1 = self.tm.getThread(self.activeName)
			t1.update_path(self.pathName)
			t1.start()
			self.tm.addThread(name, t1)
		else:
			self.tm.resumeThread(name)

	# Puts a pause on the execution of the data window
	def pause_test(self):
		self.tm.pauseThread(self.activeName)

	# Stops the currently running thread if it is active
	def stop_test(self):
		self.tm.stopThread(self.activeName)

	# Switches the active window to another window
	# Now defunct since we are using only one window
	def selectOpt(self, value):
		print "Swithcing active window to " + value
		self.activeWindow = self.windows[value]
		self.activeName = value
		disp.setUp(self.activeWindow)
		root.update()

	# Halts the execution of all threads and windows
	def stop_all(self):
		print "Deleting all threads"
		for name in self.tm.threads.keys():
			self.tm.stopThread(name)

#-------------------------------------------------------------------------------
# SCRIPT TO RUN
#-------------------------------------------------------------------------------
if __name__ == "__main__":
	root = gw._root
	app = Application(root)
	app.master.title('SARP Data Dominator')
	app.mainloop()

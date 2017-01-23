#!/usr/bin/env python
import Tkinter as tk
import graphics as gw
import display as disp
import threading
import time
#from docutils.nodes import target
#from concurrent.futures._base import RUNNING

#Tkinter root 
root = gw._root

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
			if (self.threads.has_key(name)):
				self.threads[name].paused.clear()
				self.threads[name].running.clear()
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
				#if (not self.isPaused(name)):
					#include thread.join?
				#	self.pauseThread(name)
				self.size = self.size - 1
				self.threads.remove(name)
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
		self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
		self.createWidgets()
		self.tm = ThreadManager() #house all the threads
		master.minsize(width=666, height=666)#Change to new window
		
		self.windows={}#Dictionary to hold windows
		self.windowList = [5]
		
	def createWidgets(self):
		top=self.winfo_toplevel() 
		top.rowconfigure(0, weight=1) 
		top.columnconfigure(0, weight=1) 
		self.rowconfigure(0, weight=1) 
		self.columnconfigure(0, weight=1) 
		
		#Quit Button
		self.quitB = tk.Button(self, text='Quit', command=self.quit)
		self.quitB.grid(row=0, column=8, sticky=tk.N+tk.E)
		
		#Window button
		self.addWinB = tk.Button(self, text='New Window', command=self.insertWindow)
		self.addWinB.grid(row=0, column=6, columnspan=2,sticky=tk.N+tk.E)

	def quit(self):
		try:
			self.stop_test()
		except:
			pass
		
		tk.Frame.quit(self)
	
	def insertWindow(self):
		if (len(self.windows) < 5):
			#Set up window and display
			newWin = gw.GraphWin("Data",1200,600, master=self)
			newWin.grid(row=4, column=0, columnspan=5, rowspan=5)
			disp.setUp(newWin)
	
			#set as active window and add to window dictionary
			self.activeWindow = newWin
			index = len(self.windows)
			name = "DataWin " + str(index)
			self.windows.update({name : newWin})
			
			#Window Button
			self.windowList[index] = name
			self.v = tk.StringVar()
			self.v.set(self.windowList[0])
			self.winOM = tk.OptionMenu(self,self.v, *self.windowList)
			self.winOM.grid(row=3, column=6, rowspan=3)
			
			#Start Test button
			self.winStartB = tk.Button(self, text='Start Test', command=self.start_test)
			self.winStartB.grid(row=1, column=6)
			
			#pause Test button
			self.winPauseB = tk.Button(self, text='Pause', command=self.pause_test)
			self.winPauseB.grid(row=1, column=7)
			
			#Stop Test button
			self.winStopB = tk.Button(self, text='Stop', command=self.stop_test)
			self.winStopB.grid(row=1, column=8)
			
			self.dWin = disp.DataWindow(kwargs={'window':self.activeWindow})
			root.update()
	
	def start_test(self):
		name = "Data Window" #hard code for now
		if(not self.tm.contains(name)):
			t1 = self.dWin
			t1.start()
			#self.winStartB.set
			self.tm.addThread("Data Window", t1)
		else:
			self.tm.resumeThread("Data Window")
		
	def pause_test(self):
		self.tm.pauseThread("Data Window")
		
	def stop_test(self):
		self.tm.stopThread("Data Window")
	
def test_thread():
	t = threading.currentThread()
	while getattr(t, "do_run", True):
		print "Hello"
		time.sleep(3)
	

app = Application(root)
app.master.title('SARP Data Dominator')
app.mainloop()




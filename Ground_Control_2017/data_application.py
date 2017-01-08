#!/usr/bin/env python
import Tkinter as tk
import graphics as gw
import display as disp
import threading
import time

#Tkinter root 
root = gw._root

#Class which  creates a user interface window 
class Application(tk.Frame):
	
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
		self.createWidgets()
		self.threads = [] #house all the threads
		master.minsize(width=666, height=666)
		
	def createWidgets(self):
		top=self.winfo_toplevel() 
		top.rowconfigure(0, weight=1) 
		top.columnconfigure(0, weight=1) 
		self.rowconfigure(0, weight=1) 
		self.columnconfigure(0, weight=1) 
		
		self.quitB = tk.Button(self, text='Quit', command=self.quit)
		self.quitB.grid(row=0, column=1, sticky=tk.N+tk.E)
		
		self.addWinB = tk.Button(self, text='New Window', command=self.insert_shit)
		self.addWinB.grid(row=0, column=0, sticky=tk.N+tk.E)
	
	def insert_shit(self):
		
		self.newWin = gw.GraphWin("Data",1200,600, master=self)
		self.newWin.grid(row=3, column=0)
		disp.setUp(self.newWin)
		self.activeWindow = self.newWin
		
		self.winStartB = tk.Button(self, text='Start Test', command=self.start_test)
		self.winStartB.grid(row=1, column=0)
		
		self.winStopB = tk.Button(self, text='Stop', command=self.stop_test)
		self.winStopB.grid(row=1, column=1)
		
		self.dWin = disp.DataWindow(self.newWin)
		root.update()
	
	def start_test(self):
		self.t1 = threading.Thread(target=self.dWin.run, kwargs={'window':self.activeWindow})
		self.t1.start()
		#self.t1.join()
		self.threads.append(self.t1)
		
	def stop_test(self):
		self.threads[0].do_run = False

	
def test_thread():
	t = threading.currentThread()
	while getattr(t, "do_run", True):
		print "Hello faggot"
		time.sleep(3)
		
"""
class App(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		#self.start()
	
	def callback(self):
		self.root.quit()
		
	def run(self):
		self.root = tk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.callback)
		
		self.subapp = Application(self.root)
		self.subapp.master.title('SARP Data Dominator')
		self.subapp.mainloop()
		self.root.withdraw()
		#label = tk.Label(self.root, text="Hello Worldddd")
		#label.pack()
		#self.root.mainloop()
			
app = App()
app.start()
"""

app = Application(root)
app.master.title('SARP Data Dominator')
app.mainloop()




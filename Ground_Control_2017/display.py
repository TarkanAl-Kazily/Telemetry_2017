import graphics as gw
import time as time_mod
import math
import threading
import utility as util
from sqlite3.test import types

# Do I need this???
GraphWin = gw.GraphWin
Point = gw.Point
Line = gw.Line
Circle = gw.Circle
Oval = gw.Oval
Rectangle = gw.Rectangle
Polygon = gw.Polygon
Text = gw.Text
Entry  = gw.Entry
Image = gw.Image

#Set up Global
inputFile = "input1.txt" # name of file to read input from
outputFile = "savedData.txt" # name of file where data is recorded
aTempMax = 1000 # the temp/press when the bars are full
bTempMax = 50
cTempMax = 500
pressMax = 1000
sampleTime = 0.5 # time between samples in seconds
portName = "COM5"
location = [0.0,0.0] # GPS location of device
#Container box buffer
buffer = 5

# initialize output
#output = open(outputFile, "a")

#initialize parser
parser = util.Parser()
try:
    parser.open_port(portName)
except:
    print "No serial connected with "+ portName

class DataWindow(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        
        super(DataWindow, self).__init__(group=group, target=target, 
                                      name=name, verbose=verbose)
        # initialize tracked data and stuff
        self.speed = 0 # m/s
        self.altitude = 0 # m
        self.currentAltMax = 1000.0 # graph starts with max at 1 km
        self.currentTMax = 5.0 # graph starts with max at 5 seconds
        #75, 525 
        self.origin = Point(75,525) # pixel at graph origin
        self.yMax = 315 # pixel length of y axis #315
        self.xMax = 465 # pixel length of x axis #465
        
        
        #Grab Args
        #self.args=args
        self.kwargs=kwargs
        self.name = name
        
        #Grab window from kwargs
        self.window = kwargs['window']
        self.types_to_objects = {}
        
        #Old, unneccessary initializations
        '''
        self.altData = DataField(self.window, Point(350,75), "(m)", 
                                 "Altitude: ", 32, "ALTI1")
        self.speedData = DataField(self.window, Point(780,30), "(m/s)",
                                   "Speed: ",15,"SPED1")
        self.yLabel = DataField(self.window, Point(40,225), "")
        self.xLabel = DataField(self.window, Point(540,545), "")
        
        self.dataFields = (self.altData, self.speedData, self.acclData, 
                   self.aTempData, self.bTempData, self.cTempData, 
                   self.press)  
        '''
        
        # initialize data fields
        self.altData = DataField(self.window, Point(350,75), "(m)", 
                                 "Altitude: ", 32, "ACL1")
        self.speedData = DataField(self.window, Point(780,30), "(m/s)",
                                   "Speed: ",15,"ACL1")
        self.acclData = DataField(self.window, Point(1050,30), "(m/s^2)",
                                  "Y-Accel: ",15,"ACL1")
        
        #init temperature objects
        self.aTempData = DataWithBar(self.window, Point(950,200), 
                                     "*C",Point(750,190),Point(1150,210), 
                                     aTempMax, "green", "Temp A: ", "TEM1")
        
        self.bTempData = DataWithBar(self.window, Point(950,250), 
                                     "*C",Point(750,240),Point(1150,260), 
                                     bTempMax, "red", "Temp B: ", "TEM2")
        
        self.cTempData = DataWithBar(self.window, Point(950,300), 
                                     "*C",Point(750,290),Point(1150,310), 
                                     cTempMax, "pink", "Temp C: ","TEM3")
        
        #makes a pressure bar graph
        self.press = DataWithBar(self.window,Point(975,100),"(tor)",
                                 Point(775,90), Point(1175,110),pressMax, 
                                 "blue", "Pressure: ", "PRE1", 1)
        

        
        # Make the altitude graph (which is actually acceleration rn)
        self.altGraph = Graph(self.window, self.origin, self.yMax, self.xMax, 
                              self.currentAltMax, self.currentTMax, "blue", 
                              "Time", "Alt", "ACL1")


        
        #make a bunch of containers
        self.containers = []
        #graph container
        container1 = Container(self.window, self, Point(5, 150), 600, 445)
        container1.add(self.altGraph)
        #temperature container
        container2 = Container(self.window, self, Point(610, 155), 580, 190)
        container2.add(self.aTempData)
        container2.add(self.bTempData)
        container2.add(self.cTempData)
        #pressure and readings container
        container3 = Container(self.window, self, Point(610, 5), 580, 140)
        container3.add(self.press)
        container3.add(self.acclData)
        container3.add(self.speedData)
        #altitude container
        container4 = Container(self.window, self, Point(5,5), 600, 140)
        container4.add(self.altData)
        
        
        #self.__register_type_callback(self.altGraph)
        #self.__register_type_callback(self.aTempData)
        #self.__register_type_callback(self.bTempData)
        #self.__register_type_callback(self.cTempData)
        #self.__register_type_callback(self.press)
        #self.__register_type_callback(self.acclData)
        #Instead register a speed object with reference to speedData
        #self.__register_type_callback(self.speedData)
        #self.__register_type_callback(Speed(object=self.speedData, 
         #                                   type=self.speedData.type))
        #self.__register_type_callback(self.altData)
        

        #add the containers
        self.containers.append(container1);
        self.containers.append(container2);
        self.containers.append(container3);
        self.containers.append(container4);
        
        #Thread events
        self.running = threading.Event()
        self.paused = threading.Event()
        
    def run(self):        
        #output.write("////////// " + time.asctime(time.localtime(time.time())) + " //////////\n")
        #output.write("Time (min, s) Accl (m/s^2)  y-speed (m/s) altitude (m)  aTemp (*C)    bTemp (*C)    cTemp (*C)    pressure (atm)\n")
        
        self.running.set()
        self.paused.clear()
        
        while self.running.isSet():
            timeStart = time_mod.time()
            
            #updates new data points
            parser.update()
            
            #get data from parser and apply it
            if (parser.is_available()): 
                #for each available data type, check to 
                #see if new data came in
                for key in self.types_to_objects.keys():
                    data = parser.get_data_tuple(key)
                    
                    if data != None:
                        doota = float(data[0])
                        data_time = data[1]
                        #update all the items linked to this data type
                        for item in self.types_to_objects[key]:
                            item.update(doota, data_time)
            
            # reports if render time is greater than sample time.
            if time_mod.time() - timeStart > sampleTime:
                print("TIME! " + str(round(time_mod.time() - timeStart, 3)))
            while time_mod.time() - timeStart < sampleTime:
                time_mod.sleep(0.03)
            
            #pauses runtime
            while self.paused.isSet():
                time_mod.sleep(0.03)
            
            # updates GPS location of device and saves it as "location"
            
            #end of loop
            
        #close the input stream    
        #inputData.close()    
        print("Exited Thread and Stopped")  
               
    def setUp(self): # sets up the static elements of the data display
        '''
        Sets up all the containers in this display.
        '''
        for container in self.containers:
            try:
                container.setUp()
            except:
                print ("Illegal Container")
                
    def __register_type_callback__(self, object):
        '''
        @todo: enforce that object has type field and update method
        '''
        type = object.type
        
        '''
        @todo: can be reduced to one line i think
        '''
        if (self.types_to_objects.has_key(type)):
            self.types_to_objects[type].append(object)
        else:
            self.types_to_objects.update({type:[object]})
                
def record(output, spacing, data):
    for d in data:
        output.write(str(d) + (spacing - len(str(d))) * " ")
    output.write("\n")

    
#-------------------------------------------------------------------------------
#        CLASSES
#-------------------------------------------------------------------------------
        
#A class for holding other items, orienting them, and printing them
#Used for eventual automatic display of elements on the screen which
#organizes items in boxes on the screen.
#CAN ALSO BE USED FOR DTECTING WHEN A GROUP OF ITEMS ARE SELECTED
class Container:    
    def __init__(self, window, origin, position=Point(0,0), max_length=0, max_height=0, ):
        #the Items in this containers
        self.items = []
        #the window to draw stuff to
        self.window = window
        self.types = [] #The type of data to update
        self.origin = position #top left of where container is drawn
        self.max_x = max_length #max length 
        self.max_y = max_height #max height
        self.parent = origin
    
    def add(self, item):
        '''
        @todo: update container dimensions
        '''
        self.items.append(item)
        self.parent.__register_type_callback__(item)
        
        
    def setUp(self):
        Rectangle(self.origin, Point(self.origin.getX()+self.max_x,
                                     self.origin.getY()+self.max_y)
                                    ).draw(self.window)
        for component in self.items:
            try:
                component.setUp()
            except:
                print("Illegal Component Detected")
        
# A Data field that displays data... 
class DataField:
    # Parameters: window: the Graphics Window 
    #           location: the Point at the center of the display
    #               unit: the unit associated with the data
    def __init__(self, window, location, unit, text="Default", text_size=15,
                 type="DEF"):
        self.line = Text(location, "READY") #initialize text field
        self.line.setSize(text_size) #intialize text size
        self.window = window #keeps a window reference
        self.line.draw(self.window) #draws inital
        self.unit = unit
        self.location = location #Location of the field on the screen
        self.text_size = text_size # size of the text
        self.text = text #Label
        self.type = type #keeps track of type 
        self.max_len = 0 #max length to be used 
        
    # sets and displays new data
    def update(self, data, time):
        if data != None:
            temp = self.line.getText()
            if (len(temp) > self.max_len):
                self.max_len = len(temp)
            self.line.setText(str(round(data, 1)) + " " + self.unit)
            diff = len(self.line.getText()) - self.max_len
            if diff > 0:
                self.line._move(diff*self.text_size*0.5, 0)
        else:
            self.line.setText("(No Data)")
        self.line.undraw()
        self.line.draw(self.window)
    
    #         window, x_start=0, y_start=0, name="default", size=15    
    def setUp(self):
        txt = Text(Point(self.location.getX() - len(self.text) * 
                         self.text_size * 0.6, self.location.getY()), 
                         self.text) # Altitude text
        
        txt.setSize(self.text_size)
        txt.draw(self.window)

# displays data with a "temperature bar" that fills left to right based on value. 
class DataWithBar:
    # Parameters: window: the Graphics Window
    #        txtLocation: the middle of the location of the data readout
    #               unit: the unit associated with the data
    #            corner1: the upper left corner of the "temperature bar"
    #            corner2: the lower right corner of the "temperature bar"
    #            maximum: the value at which the bar is completely filled
    #              color: the color of the bar
    #               text: the text that is the label
    #               type: the thing that manages the data ??
    #         isVertical: is non zero if the bar is fills vertically
    def __init__(self, window, txtLocation, unit, corner1, corner2, 
                 maximum, color, text="Default", type="DEF", isVertical=0):
        self.line = Text(txtLocation, "READY")
        self.line.draw(window)
        self.window = window
        self.unit = unit
        self.upperLeft = corner1
        self.bottomRight = corner2
        self.max = maximum
        self.color = color
        self.box = Rectangle(Point(0,0),Point(0,0))
        self.label = text
        self.type = type
        self.isVertical = isVertical

    def update(self, data, time):
        self.box.undraw()
        if data == "NO":
            self.line.setText("(No Data)")
        else:
            self.line.setText(str(float(data)) + " " + self.unit)
            if float(data) > self.max:
                data = self.max
            if self.isVertical:
                self.box = Rectangle(self.bottomRight,Point(self.upperLeft.getX(),self.bottomRight.getY() - float(data) / self.max *(self.bottomRight.getY() - self.upperLeft.getY())))
            else:
                self.box = Rectangle(self.upperLeft,Point(float(data) / self.max * 
                                (self.bottomRight.getX() - self.upperLeft.getX()) +
                                 self.upperLeft.getX(),self.bottomRight.getY()))
        self.box.setFill(self.color)
        self.box.draw(self.window)
        self.line.undraw()
        self.line.draw(self.window)
    

    #        window, name, name_x, name_y, bar_x, bar_y, length_x, length_y    
    def setUp(self):
        Text(Point(self.upperLeft.getX() - 50, self.upperLeft.getY() + (self.bottomRight.getY() - self.upperLeft.getY()) / 2), 
             self.label).draw(self.window)
        Rectangle(self.upperLeft, self.bottomRight).draw(self.window)
    
# Creates a 1-quadrant graph at specified location with vertical and horizontal
#     length. New data can be added and will be plotted with respect to time. 
#     Plots data at time when method called.
class Graph:
    # Parameters: window: the Graphics Window
    #             origin: a Point location for the origin of the graph.
    #            yLength: the pixel length of the Y-axis.
    #            tLength: the pixel length of the T-axis.
    #           initYmax: the initial data value for the maximum of the Y-axis.
    #           initTmax: the initial data value for the maximum of the T-axis.
    #            x_label: label for the bottom axis
    #            y_label: label for the top axis
    def __init__(self, window, origin, yLength, tLength, initYMax, 
                 initTMax, color, x_label, y_label, type="DEF"):
        self.window = window # window reference
        self.origin = origin #origin of y axis
        self.yLength = yLength #y axis height
        self.tLength = tLength  # x- axis width
        self.graphicsFactor = 4.8 # the higher, the sooner the lines stop rendering. 5 causes no initial lag
        self.currentYMax = initYMax
        self.currentTMax = initTMax
        self.color = color # color of the lines and points
        self.points = [] # the data recorded and scaled
        self.displayPoints = [] # the data to be displayed
        self.displayLines = [] # the connecting lines
        self.oldTime = 0 # tracks last time reading
        self.x_label = x_label
        self.y_label = y_label
        self.type = type
        self.nib_const = 0.9
        self.time = 0;
        self.x_bounds = Text(Point(origin.getX()+self.tLength*self.nib_const+35,
                                   origin.getY()+15), "READY") #displays the x bounds
        self.y_bounds = Text(Point(origin.getX()-30, 
                                   origin.getY()-self.yLength*self.nib_const-20), 
                                   "READY") #displays the y bounds
        

    # adds a data point and redraws graph
    def update(self, data, time): # takes a data point and redraws the graph
        if len(self.points) == 0:
            self.points.append(Point(0, data * self.yLength / self.currentYMax))
            #self.oldTime = time_mod.time()
        else: 
            self.points.append(Point(self.points[-1].getX() + self.tLength * 
                                     (time - self.time) / 
                                     self.currentTMax, 
                                     data * self.yLength / self.currentYMax))
            #self.oldTime = time_mod.time()
        self.time = time
        
        doRedraw = False
        while(data > self.currentYMax or data < - self.currentYMax):
            doRedraw = True
            oldMax = self.currentYMax
            # extends y-axis  by 1.5 each time max data 
            # is reached (change later?)
            self.currentYMax  = self.currentYMax * 1.5
            for i in range(0,len(self.points)):
                self.points[i] = Point(self.points[i].getX(), 
                                       self.points[i].getY() * oldMax / 
                                       self.currentYMax)
                
        while self.points[-1].getX() > self.tLength:
            doRedraw = True
            oldMax = self.currentTMax
            # extends t-axis 10 seconds each time the max time 
            # is reached (change later?)
            self.currentTMax += 10
            for i in range(0,len(self.points)):
                self.points[i] = Point(self.points[i].getX() * oldMax / 
                                       self.currentTMax, self.points[i].getY())
        if doRedraw:
            self.redraw() # redraws all points and lines
        else: # draw new point only
            p = Point(self.origin.getX() + self.points[-1].getX(), 
                      self.origin.getY() - self.points[-1].getY())
            p.setFill(self.color)
            self.displayPoints.append(p)
            p.draw(self.window)
            if len(self.displayPoints) > 1 and \
               len(self.displayPoints) < self.tLength / self.graphicsFactor:
                l = Line(p,self.displayPoints[-2])
                l.setFill(self.color)
                l.draw(self.window)
                self.displayLines.append(l)
                oldP = p
        
        '''
        @todo: make update only work if values need it.
        @todo: implement resizing
        '''
        new_bounds = self.getAxisValues()
        self.x_bounds.setText(new_bounds[1])
        self.y_bounds.setText(new_bounds[0])
        self.x_bounds.undraw()
        self.x_bounds.draw(self.window)
        self.y_bounds.undraw()
        self.y_bounds.draw(self.window)
            
    # Returns the maximum y and t axis values for labeling purposes  
    def getAxisValues(self):
        return (self.currentYMax, self.currentTMax)
    

    # Helps update method.
    def redraw(self):
        for p in self.displayPoints:
            p.undraw()
        for l in self.displayLines:
            l.undraw()
        newPoints = []
        for i in range(0,len(self.points)):
            p = Point(self.origin.getX() + self.points[i].getX(),self.origin.getY() - self.points[i].getY())
            p.setFill(self.color)
            newPoints.append(p)
        self.displayPoints =  newPoints
        oldP = self.origin
        for p in self.displayPoints:
            p.draw(self.window)
            if len(self.displayPoints) < self.tLength / self.graphicsFactor:
                l = Line(p,oldP)
                l.setFill(self.color)
                l.draw(self.window)
                self.displayLines.append(l)
                oldP = p
        #print("REDREW!")
        
    '''
    @todo: turn calls into a variable assignment
    '''
    def setUp(self):
        #Buffer which seeks to select the best buffer appropriate for the dimensions
        #based on the dimensions of the smaller of the two dimensions
        #axis_buffer = max(70, min(self.tLength, self.yLength) * 0.05)
        
        
        #magic buffer for the line is fifty
        Line(Point(self.origin.getX(),self.origin.getY()),
             Point(self.origin.getX(),self.origin.getY()-self.yLength)
             ).draw(self.window) # graph y axis
             
        #10 is the length for now. Make scalable?
        Line(Point(self.origin.getX()-10, 
                   self.origin.getY() - self.yLength * self.nib_const),
             Point(self.origin.getX(),self.origin.getY() - self.yLength * 
                   self.nib_const)).draw(self.window) #lil nub thingie
             
        Line(Point(self.origin.getX(), self.origin.getY()),
             Point(self.origin.getX()+self.tLength, self.origin.getY())
             ).draw(self.window) # graph x axis
             
        Line(Point(self.origin.getX()+self.tLength * self.nib_const,
                   self.origin.getY()+10),
             Point(self.origin.getX()+self.tLength * self.nib_const,
                   self.origin.getY())
             ).draw(self.window)
        
        Text(Point(self.origin.getX() + self.tLength * 0.5,self.origin.getY() 
                   + 10), self.x_label).draw(self.window) # graph x label
        
        Text(Point(self.origin.getX(), self.origin.getY()-self.yLength-10), 
             self.y_label).draw(self.window) # graph y label
             
        self.x_bounds.draw(self.window)
        self.y_bounds.draw(self.window)
        
class PolarGraph:
    # Parameters: window: graphics window
    #          upperLeft: the upper left point where the graph will be drawn
    #           diameter: the width across the graph (and height because it is a circle)
    #               rMax: the maximum value of 
    #              label: the label for the max value of the graph
    #    currentLocation: the current location of the device for mobility
    def __init__(self, window, upperLeft, diameter, rMax, label, currentLocation=[0.0,0.0]):
        self.window = window
        self.upperLeft = upperLeft
        self.diameter = diameter
        self.rMax = rMax
        self.label = label
        self.currentLocation = currentLocation
            
    def update(self):
        pass
    
    def setUp(self):
        Line(Point(self.upperLeft.getX() + diameter / 2, self.upperLeft.getY()),
             Point(elf.upperLeft.getX() + diameter / 2, self.upperLeft.getY() + diameter)).draw(self.window)
        Line(Point(self.upperLeft.getX(),self.uppereLeft.getY() + diameter / 2),
             Point(self.upperLeft.getX() + diameter, self.uppereLeft.getY() + diameter / 2)).draw(self.window)
        Circle(Point(upperLeft.getX() + diameter / 2, upperLeft.getY()), diameter / 2).draw(self.window)

class Speed:
    def __init__(self, object, type="ACL1"):
        self.type = type
        self.callback_ref = object
        self.speed = 0.0
        self.time = 0
        
    def update(self, data, time):
        '''
        if currentData[0] != "NO":
                self.speed += float(currentData[0]) * sampleTime
                '''
        self.speed += float(data) * (time - self.time);
        self.time = time
        self.callback_ref.update(self.speed, time)
        
# record output
#recordTime = str(time_mod.localtime(time.time())[4]) + ", " + str(round(time.localtime(time.time())[5] + math.modf(time.time())[0],2))
#record(output, 14, (recordTime, currentData[0], round(self.speed, 2), round(self.altitude, 2), currentData[1], currentData[2], currentData[3], currentData[4]))
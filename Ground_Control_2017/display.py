import graphics as gw
import time
import math
import threading
import utility as util

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
pressMax = 1.5
sampleTime = 0.5 # time between samples in seconds
portName = "COM4"
#box buffer
buffer = 5

# initialize output
output = open(outputFile, "a")

#initialize parser
parser = util.Parser()
#parser.open_port(portName)

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
        self.args=args
        self.kwargs=kwargs
        
        self.name = name
        
        #IMPLEMENT GRABBING WINDOW FROM KWARGS
        self.window = kwargs['window']
        
        
        # initialize data fields
        self.altData = DataField(self.window, Point(350,75), "(m)", "Altitude: ", 32)
        self.speedData = DataField(self.window, Point(780,30), "(m/s)", "Speed: ")
        self.acclData = DataField(self.window, Point(1050,30), "(m/s^2)", "Y-Accel: ")
        
        #init temperature objects
        self.aTempData = DataWithBar(self.window, Point(950,200), 
                                     "*C",Point(750,190),Point(1150,210), 
                                     aTempMax, "green", "Temp A: ")
        self.bTempData = DataWithBar(self.window, Point(950,250), 
                                     "*C",Point(750,240),Point(1150,260), 
                                     bTempMax, "red", "Temp B: ")
        self.cTempData = DataWithBar(self.window, Point(950,300), 
                                     "*C",Point(750,290),Point(1150,310), 
                                     cTempMax, "pink", "Temp C: ")
        
        self.yLabel = DataField(self.window, Point(40,225), "")
        self.xLabel = DataField(self.window, Point(540,545), "")
        
        self.press = DataWithBar(self.window,Point(975,100),"(atm)",
                                 Point(775,90), Point(1175,110),pressMax, 
                                 "blue", "Pressure: ")
        self.dataFields = (self.altData, self.speedData, self.acclData, self.aTempData, 
                           self.bTempData, self.cTempData, self.yLabel, self.xLabel, self.press)
        
        
        # GRAPH
        self.altGraph = Graph(self.window, self.origin, self.yMax, self.xMax, 
                              self.currentAltMax, self.currentTMax, "blue", 
                              "Time", "Alt")
        
        #make a bunch of containers
        self.containers = []
        #graph container
        container1 = Container(self.window, Point(5, 150), 600, 445)
        container1.add(self.altGraph)
        #temperature container
        container2 = Container(self.window, Point(610, 155), 580, 190)
        container2.add(self.aTempData)
        container2.add(self.bTempData)
        container2.add(self.cTempData)
        #pressure and readings container
        container3 = Container(self.window, Point(610, 5), 580, 140)
        container3.add(self.press)
        container3.add(self.acclData)
        container3.add(self.speedData)
        #altitude container
        container4 = Container(self.window, Point(5,5), 600, 140)
        container4.add(self.altData)
        
        #add the containers
        self.containers.append(container1);
        self.containers.append(container2);
        self.containers.append(container3);
        self.containers.append(container4);
        
        #Thread events
        self.running = threading.Event()
        self.paused = threading.Event()
        
        '''
        #Default: 595, 445
        setUpGraph(self.window, 10, 150, 600, 440, "Altitude (m)", 
                   "Time Since Launch (s)")
        '''
        
    def run(self):
        '''
        @todo:  change
        '''
        window = self.window
        
        #debug
        print "running " + self.name
        
        #output.write("////////// " + time.asctime(time.localtime(time.time())) + " //////////\n")
        #output.write("Time (min, s) Accl (m/s^2)  y-speed (m/s) altitude (m)  aTemp (*C)    bTemp (*C)    cTemp (*C)    pressure (atm)\n")
        
        self.running.set()
        self.paused.clear()
        
        while self.running.isSet():
            timeStart = time.time()
            
            # collect data for manipulation (acclY, aTemp, bTemp, cTemp)
            inputData = open(inputFile, "r")
            currentData = []
            for i in range(0,5):
                data = inputData.readline()
                if data[0:len(data)-1]:
                    currentData.append(round(float(data[0:len(data)-1]),1))
                else:
                    currentData.append("NO")
            #print(currentData)
        
            # approximate alt
            if currentData[0] != "NO":
                self.speed += float(currentData[0]) * sampleTime
            self.altitude += self.speed * sampleTime
            
            '''
            @todo: add options for derived measurements
            '''
            #get data from parser and apply it
            if (parser.is_available()): 
                for container in self.containers:
                    for widget in container.widgets:
                        result = parser.get(widget.type)
                        if (result != None):
                            #feed in the data
                            widget.update(result)
            
            
            '''
            self.dataFields = (self.altData, self.speedData, self.acclData, self.aTempData, 
                           self.bTempData, self.cTempData, self.yLabel, self.xLabel, self.press)
            '''
            #update data fields
            self.dataFields[0].update(self.altitude) #update alt data
            self.dataFields[1].update(self.speed)#update speed data
            self.dataFields[2].update(currentData[0])# update accel data
            self.dataFields[3].update(currentData[1])# update tempa
            self.dataFields[4].update(currentData[2])# update tempb
            self.dataFields[5].update(currentData[3])# update tempc
            self.dataFields[6].update(self.altGraph.getAxisValues()[0]) #update y axis bounds
            self.dataFields[7].update(self.altGraph.getAxisValues()[1]) #update x axis bounds
            self.dataFields[8].update(currentData[4]) #update pressure
            # graph: 
            self.altGraph.update(self.altitude)
            
            
            # record output
            #recordTime = str(time.localtime(time.time())[4]) + ", " + str(round(time.localtime(time.time())[5] + math.modf(time.time())[0],2))
            #record(output, 14, (recordTime, currentData[0], round(self.speed, 2), round(self.altitude, 2), currentData[1], currentData[2], currentData[3], currentData[4]))
            
            
            # reports if render time is greater than sample time.
            if time.time() - timeStart > sampleTime:
                print("TIME! " + str(round(time.time() - timeStart, 3)))
            while time.time() - timeStart < sampleTime:
                time.sleep(0.03)
            
            #pauses runtime
            while self.paused.isSet():
                time.sleep(0.03)
            #end of loop
            
        #close the input stream    
        inputData.close()    
        print("Exited Thread and Stopped")  
               
    def setUp(self): # sets up the static elements of the data display
        '''
        @todo: fill out
        '''
        for container in self.containers:
            try:
                container.setUp()
            except:
                print ("Illegal Container")
                
def record(output, spacing, data):
    for d in data:
        output.write(str(d) + (spacing - len(str(d))) * " ")
    output.write("\n")
    
#-------------------------------------------------------------------------------
#        CLASSES
#-------------------------------------------------------------------------------

#A class for holding other widgets, orienting them, and printing them
class Container:
    '''
    Rectangle(Point(self.origin.getX(),self.origin.getY()),
               Point(self.origin.getX()+self.tLength,self.origin.getY()
                     +self.yLength)).draw(self.window) # Altitude graph box
    '''
    
    def __init__(self, window, position=Point(0,0), max_length=0, max_height=0):
        #the Items in this containers
        self.widgets = []
        #the window to draw stuff to
        self.window = window
        #The type of data to update
        self.types = []
        self.origin = position #top left of where container is drawn
        self.max_x = max_length #max length 
        self.max_y = max_height
    
    def add(self, component):
        '''
        @todo: update container dimensions
        '''
        self.widgets.append(component)
        
    def setUp(self):
        Rectangle(self.origin, Point(self.origin.getX()+self.max_x,
                                     self.origin.getY()+self.max_y)
                                    ).draw(self.window)
        for component in self.widgets:
            try:
                component.setUp()
            except:
                print("Illegal Component Detected")
        
# A Data field that displays data... 
class DataField:
    # Parameters: window: the Graphics Window 
    #           location: the Point at the center of the display
    #               unit: the unit associated with the data
    def __init__(self, window, location, unit, text="Default", text_size=15):
        self.line = Text(location, "READY")
        self.line.setSize(text_size)
        self.window = window
        self.line.draw(self.window)
        self.unit = unit
        self.location = location
        self.text_size =text_size
        self.text = text
        
    # sets and displays new data
    def update(self, data):
        if data != None:
            temp = self.line.getText()
            self.line.setText(str(round(data, 1)) + " " + self.unit)
            diff = len(self.line.getText()) - len(temp)
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

# displays data wiht a "temperature bar" that fills left to right based on value. 
class DataWithBar:
    # Parameters: window: the Graphics Window
    #        txtLocation: the middle of the location of the data readout
    #               unit: the unit associated with the data
    #            corner1: the upper left corner of the "temperature bar"
    #            corner2: the lower right corner of the "temperature bar"
    #            maximum: the value at which the bar is completely filled
    #              color: the color of the bar
    def __init__(self, window, txtLocation, unit, corner1, corner2, 
                 maximum, color, text="Default"):
        
        self.line = Text(txtLocation, "READY")
        self.line.draw(window)
        self.window = window
        self.unit = unit
        self.upperLeft = corner1
        self.bottom = corner2.getY()
        self.right = corner2.getX()
        self.max = maximum
        self.color = color
        self.box = Rectangle(Point(0,0),Point(0,0))
        self.corner2 = corner2
        self.label = text

    def update(self, data):
        self.box.undraw()
        if data == "NO":
            self.line.setText("(No Data)")
        else:
            self.line.setText(str(float(data)) + " " + self.unit)
            if float(data) > self.max:
                data = self.max
            self.box = Rectangle(self.upperLeft,Point(float(data) / self.max * 
                                (self.right - self.upperLeft.getX()) +
                                 self.upperLeft.getX(),self.bottom))
        self.box.setFill(self.color)
        self.box.draw(self.window)
        self.line.undraw()
        self.line.draw(self.window)
    
    #        window, name, name_x, name_y, bar_x, bar_y, length_x, length_y    
    def setUp(self):
        Text(Point(self.upperLeft.getX() + 10, self.upperLeft.getY()), 
             self.label).draw(self.window)
        Rectangle(self.upperLeft, self.corner2).draw(self.window)
    
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
                 initTMax, color, x_label, y_label):
        self.window = window
        self.origin = origin
        self.yLength = yLength #y axis height
        self.tLength = tLength  # x- axis width
        self.currentYMax = initYMax
        self.currentTMax = initTMax
        self.color = color # color of the lines and points
        self.points = [] # the data recorded and scaled
        self.displayPoints = [] # the data displayed
        self.displayLines = [] # the connecting lines
        self.oldTime = 0 # tracks last 
        self.x_label = x_label
        self.y_label = y_label
    
    # adds a data point and redraws graph
    def update(self, data): # takes a data point and redraws the graph
        if len(self.points) == 0:
            self.points.append(Point(0, data * self.yLength / self.currentYMax))
            self.oldTime = time.time()
        else: 
            self.points.append(Point(self.points[-1].getX() + self.tLength * (time.time() - self.oldTime) / self.currentTMax, 
                                     data * self.yLength / self.currentYMax))
            self.oldTime = time.time()
        while(data > self.currentYMax):
            oldMax = self.currentYMax
            self.currentYMax  = self.currentYMax * 1.5 # extends y-axis  by 1.5 each time max data is reached (change later?)
            for i in range(0,len(self.points)):
                self.points[i] = Point(self.points[i].getX(), self.points[i].getY() * oldMax / self.currentYMax)
        while self.points[-1].getX() > self.tLength:
            oldMax = self.currentTMax
            self.currentTMax += 10 # extends t-axis 10 seconds each time the max time is reached (change later?)
            for i in range(0,len(self.points)):
                self.points[i] = Point(self.points[i].getX() * oldMax / self.currentTMax, self.points[i].getY())
        for p in self.displayPoints:
            p.undraw()
        for l in self.displayLines:
            l.undraw()
        self.convert()
        oldP = self.origin
        for p in self.displayPoints:
            p.draw(self.window)
            if len(self.displayPoints) < self.tLength:
                l = Line(p,oldP)
                l.setFill(self.color)
                l.draw(self.window)
                self.displayLines.append(l)
                oldP = p
    
    # Returns the maximum y and t axis values for labeling purposes  
    def getAxisValues(self):
        return [self.currentYMax, self.currentTMax]
    
    # Helps update method.
    def convert(self):
        newPoints = []
        for i in range(0,len(self.points)):
            p = Point(self.origin.getX() + self.points[i].getX(),self.origin.getY() - self.points[i].getY())
            p.setFill(self.color)
            newPoints.append(p)
        self.displayPoints =  newPoints
        
    #window, start_x, start_y, length, height, y_label="y", x_label="x"
    '''
    @todo: turn calls into a variable assignment
    '''
    def setUp(self):
        #Buffer which seeks to select the best buffer appropriate for the dimensions
        #based on the dimensions of the smaller of the two dimensions
        #axis_buffer = max(70, min(self.tLength, self.yLength) * 0.05)
        
        nib_const = 0.9
        
                
        #magic buffer for the line is fifty
        Line(Point(self.origin.getX(),self.origin.getY()),
             Point(self.origin.getX(),self.origin.getY()-self.yLength)
             ).draw(self.window) # graph y axis
             
        #10 is the length for now. Make scalable?
        Line(Point(self.origin.getX()-10, 
                   self.origin.getY() - self.yLength * 0.9),
             Point(self.origin.getX(),self.origin.getY() - self.yLength * 0.9)
             ).draw(self.window) #lil nub thingie
             
        Line(Point(self.origin.getX(), self.origin.getY()),
             Point(self.origin.getX()+self.tLength, self.origin.getY())
             ).draw(self.window) # graph x axis
             
        Line(Point(self.origin.getX()+self.tLength * 0.9,self.origin.getY()+10),
             Point(self.origin.getX()+self.tLength * 0.9,self.origin.getY())
             ).draw(self.window)
        
        Text(Point(self.origin.getX() + self.tLength * 0.5,self.origin.getY() 
                   + 10), self.x_label).draw(self.window) # graph x label
        
        Text(Point(self.origin.getX(), self.origin.getY()-self.yLength-10), 
             self.y_label).draw(self.window) # graph y label

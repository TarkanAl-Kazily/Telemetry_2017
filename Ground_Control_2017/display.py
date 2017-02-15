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

# initialize output
output = open(outputFile, "a")


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
        self.altData = DataField(self.window, Point(350,75), "(m)")
        self.altData.line.setSize(32)
        self.speedData = DataField(self.window, Point(780,30), "(m/s)")
        self.acclData = DataField(self.window, Point(1050,30), "(m/s^2)")
        
        self.aTempData = DataWithBar(self.window, Point(950,200), 
                                     "*C",Point(750,190),Point(1150,210), 
                                     aTempMax, "green")
        self.bTempData = DataWithBar(self.window, Point(950,250), 
                                     "*C",Point(750,240),Point(1150,260), 
                                     bTempMax, "red")
        self.cTempData = DataWithBar(self.window, Point(950,300), 
                                     "*C",Point(750,290),Point(1150,310), 
                                     bTempMax, "pink")
        
        self.yLabel = DataField(self.window, Point(40,225), "")
        self.xLabel = DataField(self.window, Point(540,545), "")
        
        self.press = DataWithBar(self.window,Point(975,100),"(atm)",Point(775,90),Point(1175,110),pressMax, "blue")
        self.dataFields = (self.altData, self.speedData, self.acclData, self.aTempData, 
                           self.bTempData, self.cTempData, self.yLabel, self.xLabel, self.press)
        
        # GRAPH
        self.altGraph = Graph(self.window, self.origin, self.yMax, self.xMax, self.currentAltMax, self.currentTMax, "blue")
        
        #Thread events
        self.running = threading.Event()
        self.paused = threading.Event()
        
        
        return
        
    def run(self):
        #CHANGE 
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
            inputData.close()
        
            # approximate alt
            if currentData[0] != "NO":
                self.speed += float(currentData[0]) * sampleTime
            self.altitude += self.speed * sampleTime
        
            # set data fields
            self.dataFields[0].set(self.altitude)
            self.dataFields[1].set(self.speed)
            self.dataFields[2].set(currentData[0])
            self.dataFields[3].set(currentData[1])
            self.dataFields[4].set(currentData[2])
            self.dataFields[5].set(currentData[3])
            self.dataFields[6].set(self.altGraph.getAxisValues()[0])
            self.dataFields[7].set(self.altGraph.getAxisValues()[1])
            self.dataFields[8].set(currentData[4])
            # graph: 
            self.altGraph.addData(self.altitude)
            

            # record output
            #recordTime = str(time.localtime(time.time())[4]) + ", " + str(round(time.localtime(time.time())[5] + math.modf(time.time())[0],2))
            #record(output, 14, (recordTime, currentData[0], round(self.speed, 2), round(self.altitude, 2), currentData[1], currentData[2], currentData[3], currentData[4]))
            
            
            # reports if render time is greater than sample time.
            if time.time() - timeStart > sampleTime:
                print("TIME! " + str(round(time.time() - timeStart, 3)))
            while time.time() - timeStart < sampleTime:
                time.sleep(0.03)
            
            
            while self.paused.isSet():
                time.sleep(0.03)
            #end of loop
            
        print("Exited Thread and Stopped")  
            
        
    

def record(output, spacing, data):
    for d in data:
        output.write(str(d) + (spacing - len(str(d))) * " ")
    output.write("\n")
    
def setUp(window): # sets up the static elements of the data display
        Rectangle(Point(5,5),Point(600,140)).draw(window) # Altidude display box
        
        txt = Text(Point(90,75), "Altitude:") # Altitude text
        txt.setSize(30)
        txt.draw(window)
        
        setUpGraph(window)
        
        
        Rectangle(Point(610,5),Point(1195,145)).draw(window) # other display box
        txt = Text(Point(680,30), "Speed:") # speed text
        txt.setSize(15)
        txt.draw(window)
        
        txt = Text(Point(950,30), "Y-accl:") # accl text
        txt.setSize(15)
        txt.draw(window)
        
        txt = Text(Point(700, 100), "Pressure:") # pressure text
        txt.setSize(15)
        txt.draw(window)
        
        
        
        Rectangle(Point(775,90),Point(1175,110)).draw(window) # pressure bar
        
        #margin of 40
        Rectangle(Point(635,160),Point(1190,350)).draw(window) # temp display box
        
        setUpHorBarGraph(window, "PartA Temp:", 675, 200, 750, 190, 1150, 210)
        setUpHorBarGraph(window, "PartB Temp:", 675, 250, 750, 240, 1150, 260)
        setUpHorBarGraph(window, "PartC Temp:", 675, 290, 750, 290, 1150, 310)
        #Text(Point(675,250), "PartB Temp:").draw(window)
        #Rectangle(Point(750,240),Point(1150,260)).draw(window)
        #Text(Point(675,300), "PartC Temp:").draw(window)
        #Rectangle(Point(750,290),Point(1150,310)).draw(window)
        
        #Rectangle(Point(1100,550),Point(1195,595)).draw(window) # button box
        
#Add Sizing parameters
def setUpGraph(window):
    Rectangle(Point(5,150),Point(600,595)).draw(window) # Altitude graph box
        
    Line(Point(75,200),Point(75,525)).draw(window) # graph y axis
    Line(Point(75,210),Point(65,210)).draw(window)
    
    Line(Point(550,525),Point(75,525)).draw(window) # graph x axis
    Line(Point(540,535),Point(540,525)).draw(window)
    
    Text(Point(75,180), "Altitude (m)").draw(window) # graph y label
    Text(Point(313,570), "Time Since Launch (s)").draw(window) # graph x label
    
def setUpHorBarGraph(window, name, name_x, name_y, bar_x, bar_y, barf_x, barf_y):
    Text(Point(name_x, name_y), "PartA Temp:").draw(window)
    Rectangle(Point(bar_x,bar_y),Point(barf_x, barf_y)).draw(window)
    
# A Data field that displays data... 
class DataField:
    # Parameters: window: the Graphics Window 
    #           location: the Point at the center of the display
    #               unit: the unit associated wiht the data
    def __init__(self, window, location, unit):
        self.line = Text(location, "READY")
        self.window = window
        self.line.draw(self.window)
        self.unit = unit
    
    # sets and displays new data
    def set(self, data):
        if data != "NO":
            self.line.setText(str(round(data, 1)) + " " + self.unit)
        else:
            self.line.setText("(No Data)")
        self.line.undraw()
        self.line.draw(self.window)

# displays data wiht a "temperature bar" that fills left to right based on value. 
class DataWithBar:
    # Parameters: window: the Graphics Window
    #        txtLocation: the middle of the location of the data readout
    #               unit: the unit associated with the data
    #            corner1: the upper left corner of the "temperature bar"
    #            corner2: the lower right corner of the "temperature bar"
    #            maximum: the value at which the bar is completely filled
    #              color: the color of the bar
    def __init__(self, window, txtLocation, unit, corner1, corner2, maximum, color):
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

    def set(self, data):
        self.box.undraw()
        if data == "NO":
            self.line.setText("(No Data)")
        else:
            self.line.setText(str(float(data)) + " " + self.unit)
            if float(data) > self.max:
                data = self.max
            self.box = Rectangle(self.upperLeft,Point(float(data) / self.max * (self.right - self.upperLeft.getX()) + self.upperLeft.getX(),self.bottom))
        self.box.setFill(self.color)
        self.box.draw(self.window)
        self.line.undraw()
        self.line.draw(self.window)
    
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
    def __init__(self, window, origin, yLength, tLength, initYMax, initTMax, color):
        self.window = window
        self.origin = origin
        self.yLength = yLength
        self.tLength = tLength
        self.currentYMax = initYMax
        self.currentTMax = initTMax
        self.color = color # color of the lines and points
        self.points = [] # the data recorded and scaled
        self.displayPoints = [] # the data displayed
        self.displayLines = [] # the connecting lines
        self.oldTime = 0 # tracks last 
    
    # adds a data point and redraws graph
    def addData(self, data): # takes a data point and redraws the graph
        if len(self.points) == 0:
            self.points.append(Point(0, data * self.yLength / self.currentYMax))
            self.oldTime = time.time()
        else: 
            self.points.append(Point(self.points[-1].getX() + self.tLength * (time.time() - self.oldTime) / self.currentTMax, data * self.yLength / self.currentYMax))
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
    
    # Helps addData method.
    def convert(self):
        newPoints = []
        for i in range(0,len(self.points)):
            p = Point(self.origin.getX() + self.points[i].getX(),self.origin.getY() - self.points[i].getY())
            p.setFill(self.color)
            newPoints.append(p)
        self.displayPoints =  newPoints


"""def convert(points, origin):
    newPoints = [origin,]
    for i in range(0,len(points)):
        p = Point(origin.getX() + points[i].getX(),origin.getY() - points[i].getY())
        p.setFill("blue")
        newPoints.append(p)
    return newPoints
    
    (OLD GRAPH)
    self.points.append(Point(self.points[-1].getX() + self.xMax * sampleTime / self.currentTMax, self.altitude * self.yMax / self.currentAltMax))
            while self.altitude > self.currentAltMax:
                oldMax = self.currentAltMax
                self.currentAltMax  = self.currentAltMax * 1.5
                for i in range(0,len(self.points)):
                    self.points[i] = Point(self.points[i].getX(), self.points[i].getY() * oldMax / self.currentAltMax)
            while self.points[-1].getX() > self.xMax:
                oldMax = self.currentTMax
                self.currentTMax += 10
                for i in range(0,len(self.points)):
                    self.points[i] = Point(self.points[i].getX() * oldMax / self.currentTMax, self.points[i].getY())
            for p in self.displayPoints:
                p.undraw()
            for l in self.displayLines:
                l.undraw()
            self.displayPoints = convert(self.points, self.origin)
            oldP = self.origin
            for p in self.displayPoints:
                p.draw(window)
                if len(self.displayPoints) < self.xMax:
                    l = Line(p,oldP)
                    l.setFill("Blue")
                    l.draw(window)
                    self.displayLines.append(l)
                    oldP = p"""

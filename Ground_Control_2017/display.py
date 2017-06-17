import graphics as gw
import time as time_mod
import math
import threading
import utility as util
import colors

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
outputFile = "savedData.txt" # name of file where data is recorded
aTempMax = 1000 # the temp/press when the bars are full
bTempMax = 50
cTempMax = 500
pressMax = 1000
sampleTime = 0.5 # time between samples in seconds

portName = "/dev/ttyACM0"
location = [0.0,0.0] # GPS location of device
#Container box buffer
buffer = 5

# initialize output
#output = open(outputFile, "a")

class DataWindow(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        
        super(DataWindow, self).__init__(group=group, target=target, 
                                        name=name, verbose=verbose)
        #Grab Args
        #self.args=args
        self.kwargs=kwargs
        self.name = name
        
        #Grab window from kwargs
        self.window = kwargs['window']
        self.path = kwargs['path']
        self.types_to_objects = {}
        
        #initialize parser
        self.parser = util.Parser()
        #print "Serial is open: " + str(self.parser.open_port(portName))
        
        #make a bunch of containers
        self.containers = load_layout(self.path, self)
        
        #Thread events
        self.running = threading.Event()
        self.paused = threading.Event()
        
    def run(self):
        self.running.set()
        self.paused.clear()
        
        
        while self.running.isSet():
            timeStart = time_mod.time()
            
            #updates new data points
            self.parser.update()
            
            #get data from parser and apply it
            if (self.parser.is_available()): 
                #for each available data type, check to 
                #see if new data came in
                for key in self.types_to_objects.keys():
                    data = self.parser.get_data_tuple(key)
                    if data != None:
                        data_time = data[1]
                        try:
                            float_data = float(data[0])
                        except:
                            print "Cannot convert " + data[0] + " to float"
                            continue
                        #update all the items linked to this data type
                        for item in self.types_to_objects[key]:
                            item.update(float_data, data_time)

            # reports if render time is greater than sample time.
            if time_mod.time() - timeStart > sampleTime:
                print("Graphics taxed: " + str(round(time_mod.time() - timeStart, 3)))
            while time_mod.time() - timeStart < sampleTime:
                time_mod.sleep(0.02)
            

            #pauses runtime only checking the rm connection
            while self.paused.isSet():
                time_mod.sleep(0.03)
                self.parser.update()
            
            # updates GPS location of device and saves it as "location"
            
            #end of loop
        self.parser.close()
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
        #NOW A TUPLE ITERATE OVER 
        type_tup = object.type
        
        '''
        @todo: can be reduced to one line i think
        '''
        for type in type_tup:
            if (self.types_to_objects.has_key(type)):
                self.types_to_objects[type].append(object)
            else:
                self.types_to_objects.update({type:[object]})
                
    def update_path(self, pathName):
        if (self.path == pathName):
            return
        self.path = pathName

        # remake all your containers
        self.containers = load_layout(self.path, self)
        self.setUp()
        
        
            
#-------------------------------------------------------------------------------
#        MODULE FUNCTIONS
#-------------------------------------------------------------------------------
def record(output, spacing, data):
    for d in data:
        output.write(str(d) + (spacing - len(str(d))) * " ")
    output.write("\n")

def load_layout(filepath, parent):
    '''
    Loads a layout for the screen from a layout file.
    @param filepath: The file to be read
    @param parent: The object with which to register the type calls
    '''
    try:
        filehandler = open(filepath, "r")
    except:
        print "Illegal Path: "+ filepath
        return
    
    cont_dict = {}
    
    for f in filehandler:
        f = f.strip()
        #ignore blank lines
        if (len(f) == 0):
            continue
        #echo comments to console
        if (f[0] == '#'):
            print f
            continue
        
        tokens = f.split(':')
        if (len(tokens) != 2):
            print "Illegal string: " + f
            continue
        function = tokens[0]
        args = tokens[1].strip().split(' ')
        
        #Python was crafted by Satan himself and
        #has no switch structure. Here instead is this bs
        if (function == 'new_cont'):
            add_container(args, cont_dict, parent)
        elif (function == 'add_graph'):
            add_graph(args, cont_dict, parent.window)
        elif (function == 'add_vert_bar'):
            add_vert_bar(args, cont_dict, parent.window)
        elif (function == 'add_hor_bar'):
            add_hor_bar(args, cont_dict, parent.window)
        elif (function == 'add_field'):
            add_field(args, cont_dict, parent.window)
        elif (function == 'change_port'):
            if (len(args) != 1):
                print "Illegal argument number for port change"
                continue
            parent.parser.close()
            parent.parser.open_port(args[0])
        elif (function == 'change_baudrate'):
            if (len(args) != 1):
                print "Illegal argument number for Baudrate" \
                " expected 1 but got " + str(len(args))
                continue
            try:
                parent.parser.change_baudrate(int(args[0]))
            except:
               print args[0].strip() + " cannot be converted to int"
        else:
            print "Error command "+function+" cannot be determined"
    
    filehandler.close()
    
    return cont_dict.values()

def add_container(args, cont_dict, parent):
    if (len(args) != 5):
        print "Error: Illegal argument number."
        return
    cont = Container(parent, Point(int(args[1]), int(args[2])), 
                     int(args[3]), int(args[4]))
    cont_dict.update({args[0]:cont})
    
def add_graph(args, cont_dict, window):
    if (len(args) != 11):
        print "Error: Illegal argument number."
        return
    if (args[0] in cont_dict):
        container = cont_dict[args[0]]
        '''
        if (not check_bounds(make_rect(container.origin, container.max_x, container.max_y), 
                     make_rect(Point(int(args[5]), int(args[6])),int(args[7]),int(args[8])))):
            return
        '''
        
        #grab the type args
        types = (args[1])[1:-1]
        types = types.split(',')
        for string in types:
            string = string.strip()
        
        #Unsafe casting: Add checking
        container.add(
        Graph(window, Point(int(args[5]), int(args[6])), int(args[7]), int(args[8]), 
                              float(args[10]), float(args[9]), args[4], 
                              args[2], args[3], types))
    else:
        print "No container: " + args[0]

def add_vert_bar(args, cont_dict, window):
    if (len(args) != 10):
        print "Error: Illegal argument number."
        return
    if (len(args[4]) > 8):
        print "Error: Bar name too long"
        return
    if (args[5] not in colors.COLORS):
        print "Illegal color: " + str(args[5])
        return
        
    if (args[0] in cont_dict):
        container = cont_dict[args[0]]
        if (not check_bounds(make_rect(container.origin, container.max_x, container.max_y), 
                     make_rect(Point(int(args[6]), int(args[7])),int(args[8]),int(args[9])))):
            print "Out of bounds"
            return
        #grab the type args
        types = (args[1])[1:-1]
        types = types.split(',')
        for string in types:
            string = string.strip()

        #Unsafe casting: Add checking
        container.add(
        DataWithBar(window, 
                    Point(int(args[6]), int(args[7])), 
                    args[3], 
                    Point(int(args[6]), int(args[7])), 
                    Point(int(args[6])+int(args[8]), int(args[7])+int(args[9])),
                    int(args[2]),
                    args[5], 
                    args[4], 
                    types, 1))
    else:
        print "No container: " + args[0]
        
def add_hor_bar(args, cont_dict, window):
    '''
    self.aTempData = DataWithBar(self.window, Point(950,200), 
                                     "*C",Point(750,190),Point(1150,210), 
                                     aTempMax, "green", "Temp A: ", ("TEM1",))
    '''
    if (len(args) != 10):
        print "Error: Illegal argument number."
        return
    if (len(args[4]) > 8):
        print "Error: Bar name too long"
        return
    if (args[5] not in colors.COLORS):
        print "Illegal color: " + str(args[5])
        return
    if (args[0] in cont_dict):
        container = cont_dict[args[0]]
        if (not check_bounds(make_rect(container.origin, container.max_x, container.max_y), 
                     make_rect(Point(int(args[6]), int(args[7])),int(args[8]),int(args[9])))):
            return
        
        #grab the type args
        types = (args[1])[1:-1]
        types = types.split(',')
        for string in types:
            string = string.strip()
        
        #Unsafe casting: Add checking
        container.add(
        DataWithBar(window, 
                    Point(int(args[6]) + int(args[8]) / 2,
                          int(args[7]) + int(args[9]) / 2), 
                    args[3], 
                    Point(int(args[6]), int(args[7])), 
                    Point(int(args[6])+int(args[8]), int(args[7])+int(args[9])),
                    int(args[2]),
                    args[5], 
                    args[4], 
                    types, 0))
    else:
        print "No container: " + args[0]

def add_field(args, cont_dict, window):
    if (len(args) != 7):
        print "Error: Illegal argument number."
        return
    if (args[0] in cont_dict):
        container = cont_dict[args[0]]
        
        #grab the type args
        types = (args[1])[1:-1]
        types = types.split(',')
        for string in types:
            string = string.strip()

        #Unsafe casting: Add checking
        container.add(
        DataField(window, Point(int(args[5]), int(args[6])), 
              args[3], args[4],int(args[2]), types))
    else:
        print "No container: " + args[0]
        
#returns true if rect_2 fits within rect_1
def check_bounds(rect_1, rect_2):
    x1 = rect_1.p1.x
    x2 = rect_1.p2.x
    x3 = rect_2.p1.x
    x4 = rect_2.p2.x
    y1 = rect_1.p1.y
    y2 = rect_1.p2.y
    y3 = rect_2.p1.y
    y4 = rect_2.p2.y
    if (x1 > x3 or x1 > x4):
        return False
    if (x2 < x3 or x2 < x4):
        return False
    if (y1 > y3 or y1 > y4):
        return False
    if (y2 < y3 or y2 < y4):
        return False
    return True

def make_rect(origin, length, height):
    return Rectangle(origin, Point(origin.x+length, origin.y+height))

#-------------------------------------------------------------------------------
#        CLASSES
#-------------------------------------------------------------------------------
        
#A class for holding other items, orienting them, and printing them
#Used for eventual automatic display of elements on the screen which
#organizes items in boxes on the screen.
#CAN ALSO BE USED FOR DETECTING WHEN A GROUP OF ITEMS ARE SELECTED
class Container(object):    
    def __init__(self, parent, position=Point(0,0), max_length=0, max_height=0, ):
        #the Items in this containers
        self.items = []
        #the window to draw stuff to
        self.window = parent.window
        self.types = [] #The type of data to update
        self.origin = position #top left of where container is drawn
        self.max_x = max_length #max length 
        self.max_y = max_height #max height
        self.parent = parent
    
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
        self.line = Text(location, text + " READY") #initialize text field
        self.line.setSize(text_size) #intialize text size
        self.window = window #keeps a window reference
        self.line.draw(self.window) #draws inital
        self.unit = unit
        self.location = location #Location of the field on the screen
        self.text_size = text_size # size of the text
        self.label = text #Label
        self.type = type #keeps track of type 
        self.max_len = 0 #max length to be used 
        
    # sets and displays new data
    def update(self, data, time):
        if data != None:
            temp = self.line.getText()
            if (len(temp) > self.max_len):
                self.max_len = len(temp)
            self.line.setText(self.label + " " + str(round(data, 1)) 
                              + " " + self.unit)
            #diff = len(self.line.getText()) - self.max_len
            #if diff > 0:
            #    self.line._move(diff*self.text_size*0.5, 0)
        else:
            self.line.setText("(No Data)")

        self.line.undraw()
        self.line.draw(self.window)
    
    #         window, x_start=0, y_start=0, name="default", size=15    
    def setUp(self):
        #txt = Text(Point(self.location.getX() - len(self.text) * 
                        # self.text_size * 0.9, self.location.getY()), 
                         #self.text) # Altitude text
        
        #txt.setSize(self.text_size)
        #txt.draw(self.window)
        pass

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
                self.box = Rectangle(self.bottomRight,Point(self.upperLeft.getX(),
                                    self.bottomRight.getY() - float(data) / 
                                    self.max *(self.bottomRight.getY() - 
                                               self.upperLeft.getY())))
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
        self.initYMax = initYMax
        self.initTMax = initTMax
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
        self.x_scale_factor = 1
        self.y_scale_factor = 1

    # adds a data point and redraws graph
    def update(self, data, time): # takes a data point and redraws the graph
        if len(self.points) == 0: # no points currently
            self.points.append(Point(0, data * self.yLength / self.currentYMax))
            self.oldTime = time
            self.init_time = time
        else:
            ''' 
            self.points.append(Point(self.points[-1].getX() + self.tLength * 
                                     (time - self.init_time) / 
                                     self.currentTMax, 
                                     data * self.yLength / self.currentYMax))
            '''
            self.points.append(Point(self.points[-1].getX() + self.tLength * 
                                    ((time - self.init_time) / 
                                     self.currentTMax) * self.x_scale_factor, 
                                     data * (self.yLength / self.currentYMax)))
        
        #print str(time) + " " + str(data)
            #self.oldTime = time_mod.time()
        self.time = time
        doRedraw = False
        
        # check if too long for y axis
        while(data > self.currentYMax or data < (-1 * self.currentYMax)):
            doRedraw = True
            # extends y-axis  by 1.5 each time max data 
            # is reached (change later?)
            self.currentYMax  = self.currentYMax * 2
            old_sf = self.y_scale_factor
            self.y_scale_factor = self.initYMax / self.currentYMax
            
            for i in range(0, len(self.points)):
                self.points[i] = Point(self.points[i].getX(), 
                                       self.points[i].getY() * (1/old_sf) * 
                                       self.y_scale_factor)
        #check if too long for x axis
        while self.points[-1].getX() > self.tLength:
            doRedraw = True
            # extends t-axis 10 seconds each time the max time 
            # is reached (change later?)
            self.currentTMax += 10
            old_sf = self.x_scale_factor
            self.x_scale_factor = float(self.initTMax) / self.currentTMax
            assert(self.x_scale_factor < old_sf)
            
            for i in range(0,len(self.points)):
                self.points[i] = Point(self.points[i].getX() * (1/old_sf) * 
                                       self.x_scale_factor, self.points[i].getY())
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
        
        #update the bounds
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
            p = Point(self.origin.getX() + self.points[i].getX(), self.origin.getY() - self.points[i].getY())
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


        
'''
Code has a hard time working and is not worth the massive amout of effort to get
working        
class ParallelParser:
    def __init__(self):
        self.dataDict = {}
        self.parser = util.Parser(self.dataDict)
            
    def start(self):
        self.parser.start();
            
    def get(self, dataType):
        
            @todo: do error checking on the data type
            Gets the first value in the queue of the given Name
            @param: takes in the name of a data type for which the user wants
            to receive data.
            @return: if the name is not None and is in the dictionary, return
            the first object in the queue if there exists one.
            Otherwise, return None
        
        if (self.dataDict.get(dataType) == None or 
            self.isEmpty(self.dataDict.get(dataType))):
            return None
        else:
            data = self.dataDict.get(dataType).get()
            self.dataItemsAvailable -= 1
                
            return data
    def is_available(self):
        return True
''' 
        
'''        
#Need list or items and the contianer to put them in
def place_items_in_container(items, container):
    sum = 0
    for item in items:
        #something in here is too long
        if (item.length > container.length):
            return None
        sum += item.length * item.height
    
    #elts can't possibly fit in container
    if (sum > (container.height * container.length)):
        # Throw error?
        return None
    
    #use a sorted list as a queue.
    minqueue = items.copy()
    #add all the items to the queue and sort
    minqueue.sort()
    
    mh_height = sum
    
    #continue until we have an acceptable height
    while (mh_height > container.height):
        #grab the smallest elt from the sorted list
        smallest = minqueue.pop()
        
        index = minqueue
        item_placed == False
        while(item_placed):
            largest = minqueue[index]
            if (largest == A BUNDLE):
                #Try to place in bundle
                item_placed == True
            else if ((largest.length + smallest.length) < container.length):
                #put the largest and the smallest in the same bundle
                item_placed == True
            index--
            if (index < 0):
                #smallest item cannot be put anywhere else in the container
                #and height is too high.
                #bad layout
                return None
        
        #successfully placed top elt somewhere else
        mh_height -= smallest.height
        
class PlacementContainer:
    def __init__(self, height, length):
        self.items = []
        self.height = height
        self.length = length
        
    def can_place_to_right(self, item1, item2):
'''   
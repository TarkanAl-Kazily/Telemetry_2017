#!/usr/bin/env python
import multiprocessing as mp
import serial
from collections import deque
import re
baudrate=115200
inputFile = "sample_input.txt"
outputFile = "log.txt"

class Parser():
    
    #Initializes fields in the class
    #contains a serial object for receiving 
    #data from the radio module
    def __init__(self):
        self.ser = serial.Serial()
        #self.ser._baudrate=115200
        #number of items left in queue
        self.dataItemsAvailable = 0
        self.dataDict = {}
        
    
    def open_port(self, portName):
        '''
        Opens serial port which was initialized with given name
        -For windows, name will be like 'COM4' or 'COM5'
        -For pi, the name will be something like '/dev/tty.usbserial'
        @param: portName the name of the serial port to be opened
        @return: a boolean indicating whether the port was 
                opened successfully or not
        '''
        try:
            self.ser = serial.Serial(portName, timeout=2, baudrate=baudrate) #open serial port
            self.ser.reset_input_buffer()
        except:
            print "Going into file mode"
            #TESTING FOR NOW
            self.input = open(inputFile, "r")
            #raise IllegalSerialAccess("No serial port with name: " + portName)
        self.output = open(outputFile, "w")
        
        #returns whether or not the port is open
        return self.ser.is_open
    
    def update(self):
        '''
            Checks If data is waiting in the serial port
            then, if it is, parses it and adds it to the data queues
            @requires: serial port is open.
            @raise IllegalStateException: if the serial port is not open 
        '''
        if (self.ser.isOpen()):
            #temp = self.ser.readline().strip()
            temp = self.ser.read_all().strip()
        else:
            temp = self.input.readline().strip()
            #OLD CODE FOR 1 value at a time

        print temp
            
        if len(temp) > 0 :
            #write input to output file
            self.output.write(temp +"\n")
            self.output.flush()
            
            parsed_output = self.parse_string_multiple(temp)
            
            if parsed_output != None:
                i = 0
                while i < len(parsed_output):
                    string = parsed_output[i]
                    #pass on empty strings
                    if (string != ''): 
                        if len(string) == 4:
                            type = string
                            measurement = parsed_output[i+1]
                            if not self.dataDict.has_key(type):
                                temp = {type : deque([])}
                                self.dataDict.update(temp)
                    
                            self.add_to_queue(type, measurement)
                            i += 1
                    
                    i += 1
                
            #OLD CODE FOR 1 val at a time
            '''
            type, measurement = self.parse_string(temp)
            print type
            print measurement
            
            #@todo: check for consistency in types and measurements
            
            if not self.dataDict.has_key(type):
                temp = {type : deque([])}
                self.dataDict.update(temp)
                
            self.add_to_queue(type, measurement)
            '''
            
    def isEmpty(self, queue):
        return queue == deque([])
        
    def parse_string(self, string): 
        '''
            Parses string of data
            @param: takes in a string of the form "'NAME+ID':'double'"
            @return: returns a dictionary of data 
            names and their values or None if data 
            cannot be extracted
        '''
        #Should check for multiple data points?
        type, measurement = string.strip().split(":")
        return type[1:], measurement[:-1]
    
    def parse_string_multiple(self, string):
        '''
            Parses an input of the correct format into a list
            of data types and values
            @todo: do a lot more error checking on inputs
            @param takes in a string of multiple data values which are 
            concatenated and of the form !XXXX:DATAXXXXX;
            @return: A even list of strings with even indices corresponding
            to a data type and odd indices as float data values. Returns
            None if no usable data points could be parsed
        '''
        
        string = string.strip()
        parsed_string = None
        
        #Check that string is correct length
        if (len(string) % 16 == 0):
            parsed_string = re.split('[!;:]*', string)
        else:
            #should fix bad inputs in the future and try to 
            #salvage something from data
            pass
            
        return parsed_string

    def add_to_queue(self, dataType, value):
        '''
            Adds a value to the end of the queue for the given name
            @param: takes in the name of the queue to be added to and a value
            @modifies: if the queueName is not None and is not in the dictionary 
            of queues, add it to the dictionary and update;
            @todo: edit to only accept correct vals? 
        '''
        self.dataDict.get(dataType).append(value)
        self.dataItemsAvailable += 1
    
    def is_available(self):
        '''
            Says whether or not a queue has at least on element available
            @return: returns a boolean indicating whether or not any of the 
            queues in the dictionary contain at least one value
        '''
        
        return self.dataItemsAvailable > 0
        
    def get(self, dataType):
        '''
            Gets the first value in the queue of the given Name
            @param: takes in the name of a data type for which the user wants
            to receive data.
            @return: if the name is not None and is in the dictionary, return
            the first value in the queue if there exists one. else, return None
        '''
        if (self.dataDict.get(dataType) == None or 
            self.isEmpty(self.dataDict.get(dataType))):
            return None
        else:
            data = self.dataDict.get(dataType).pop()
            self.dataItemsAvailable -= 1
                
            return float(data)
        
        
class IllegalSerialAccess(Exception):   
    '''
        Exception for when the serial port is incorrectly named.
    '''
    def __init__(self, message):
        self.message = message
#!/usr/bin/env python
from serial import Serial
from collections import deque
import re
import time
baudrate=115200
inputFile = "sample_input.txt"
outputFile = "log.txt"
regex = "![A-Z0-9]{1}[: ][-.0-9]+;"
#"![A-Z0-9]{1}:[.0-9]+;"
#use re.findall to split input strings

class Parser():
    
    #Initializes fields in the class
    #contains a serial object for receiving 
    #data from the radio module
    def __init__(self, dict={}):
        
        #self.ser._baudrate=115200
        #number of items left in queue
        self.ser = Serial()
        self.dataItemsAvailable = 0
        self.dataDict = dict

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
            self.ser = Serial(portName, timeout=2, baudrate=baudrate) #open serial port
            self.ser.reset_input_buffer()
            self.is_open = True
            if (not self.input.closed):
                self.input.close()
        except:
            print "Going into file mode"
            #TESTING FOR NOW
            self.input = open(inputFile, "r")
            self.ser.close()
            self.is_open = False
            #raise IllegalSerialAccess("No serial port with name: " + portName)
        self.output = open(outputFile, "w")
        
        #returns whether or not the port is open
        return self.ser.isOpen()

    def update(self):
        '''
            Checks If data is waiting in the serial port
            then, if it is, parses it and adds it to the data queues
            @requires: serial port is open.
            @raise IllegalStateException: if the serial port is not open 
        '''
        
        if (self.is_open):
            temp = self.ser.read_all().strip()
        else:
            temp = self.input.readline().strip()
        
        timestamp = time.time()
        
        if len(temp) > 0 :
            #write input to output file
            self.output.write(temp +"\n")
            self.output.flush()
            
            #Parse the input
            parsed_output = self.parse_string_multiple(temp)
            
            if parsed_output != None:
                for data_string in parsed_output:
                    assert(data_string[0] == '!')
                    assert(data_string[-1] == ';')
                    #take away the side markers 
                    data_string = re.sub('[!;]', '', data_string)
                    #split down middle
                    vals = data_string.split(':')
                    
                    #ONLY TO DEAL WITH ERROR WITH SPACE ERROR
                    if (len(vals) == 1):
                        vals = data_string.split(' ')
                    type = vals[0]
                    #create a tuple of the data type and the timestamp
                    measurement = (vals[1], timestamp)
                    if not self.dataDict.has_key(type):
                        #add empty queue of new data type
                        temp = {type : deque([])}
                        self.dataDict.update(temp)
                    #Add the measurement to the queue
                    self.add_to_queue(type, measurement)

    def is_empty(self, queue):
        return len(queue) == 0

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
            @requires string is not None
            @param takes in a string of multiple data values which are 
            concatenated and of the form !X:DATAXXXXX;
            @return: A even list of strings with even indices corresponding
            to a data type and odd indices as float data values. Returns
            None if no usable data points could be parsed
        '''
        string = string.strip()
        parsed_string = re.findall(regex, string)

        if (parsed_string == []):
            return None

        return parsed_string

    def add_to_queue(self, dataType, value):
        '''
            Adds a value to the end of the queue for the given name
            @param: takes in the name of the queue to be added to and a value
            @modifies: if the queueName is not None and is not in the dictionary 
            of queues, add it to the dictionary and update;
        '''
        if (value != None):
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
            @return: if the name is not None and is in the dictionary, returns
            the first value in the queue converted to a float if there exists 
            one. Otherwise, return None
            @deprecated: Use get_data_tuple instead.
        '''
        if (self.dataDict.get(dataType) == None or 
            self.is_empty(self.dataDict.get(dataType))):
            return None
        else:
            data = self.dataDict.get(dataType).pop()
            self.dataItemsAvailable -= 1
                
            return float(data[0])

    def get_data_tuple(self, dataType):
        '''
            Gets the first value in the queue of the given Name
            @param: takes in the name of a data type for which the user wants
            to receive data.
            @return: if the name is not None and is in the dictionary, return
            the first object in the queue if there exists one.
            Otherwise, return None
        '''
        if (self.dataDict.get(dataType) == None or 
            self.is_empty(self.dataDict.get(dataType))):
            return None
        else:
            data = self.dataDict.get(dataType).pop()
            self.dataItemsAvailable -= 1
            return data

    def close(self):
        if (self.is_open):
            self.ser.close()
        else:
            try:
                self.input.close()
            except:
                print "Error closing filestream"

    def change_baudrate(self, new_rate):
        self.ser.baudrate(new_rate)

class IllegalSerialAccess(Exception):   
    '''
        Exception for when the serial port is incorrectly named.
    '''
    def __init__(self, message):
        self.message = message
#!/usr/bin/env python
import multiprocessing as mp
import serial
from collections import deque
'''
@
'''

class Parser():
    
    #Initializes fields in the class
    #contains a serial object for recieving the string from  
    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate(9600)
        #number of items left in queue
        self.dataItemsAvailable = 0
        
        self.velQ = deque([])         # initializing as empty queues
        self.accelQ = deque([])
        self.altQ = deque([])
        self.aTempQ = deque([])
        self.bTempQ = deque([])
        self.cTempQ = deque([])
        self.pressQ = deque([])
        self.gyroQ = deque([])
        self.dataDict = {'Vel': self.velQ, 'Accel': self.accelQ, 'Alt': self.altQ, 'aTemp': self.aTempQ, 'bTemp': self.bTempQ,
                        'cTemp': self.cTempQ,'Press': self.pressQ, 'Gyro': self.gyroQ}
        
    #opens serial port which was initialized with given name
    #For windows, name will be like 'COM4'
    #For pi, the name will be something like '/dev/tty.usbserial'
    def open_port(self, portName):
        try:
            self.ser = serial.Serial(portName, timeout=2) #open serial port
        except:
            raise IllegalSerialAccess("No serial port with name: " + portName)
        
        #prints the name to console to ensure the connection is accurate
        print self.ser.name
        
        #returns whether or not the port is open
        return self.ser.is_open
    
    
    
    #Checks the serial report for strings, then parses string
    def update(self):
        '''
            @requires: serial port is open.
            @raise IllegalStateException: if the serial port is not open 
        '''
        if (self.ser.isOpen()):
            type, measurement = parse_string(self.ser.next())
            print type
            print measurement
            add_to_queue(type, measurement)
        
    
    def isEmpty(self, queue):
        return queue == deque([])
        
    
    #parses string of data
    def parse_string(self, string): 
        '''
            @param: takes in a string of the form "'NAME+ID':'double'"
            @return: returns a dictionary of data names and their values or None
        '''
        #Should check for multiple data points?
        type, measurement = string.strip().split(":")
        return type, measurement
    
    #adds a value to the end of the queue for the given name
    def add_to_queue(self, dataType, value):
        '''
            @param: takes in the name of the queue to be added to and a value
            @modifies: if the queueName is not None and is not in the dictionary 
            of queues, add it to the dictionary and update;
        '''
        self.dataDict.get(dataType).append(measurement)
        self.dataItemsAvailable += 1
    
    #says whether or not a queue has at least one element    
    def is_available(self):
        '''
            @return: returns a boolean indicating whether or not any of the 
            queues in the dictionary contain at least one value
        '''
        
        return self.dataItemsAvailable > 0
        
    #gets the first value in the queue of the given Name
    def get(self, dataType):
        '''
            @param: takes in the name of a data type for which the user wants
            to receive data.
            @return: if the name is not None and is in the dictionary, return
            the first value in the queue if there exists one. else, return None
        '''
        if (self.isEmpty(dataDict.get(type))):
            return None
        else:
            data = self.dataDict.get(type).pop()
            self.dataItemsAvailable -= 1
                
            return data
        
        
class IllegalSerialAccess(Exception):   
    '''
        Exception for when the serial port is incorrectly named.
    '''
    
    def __init__(self, message):
        self.message = message
        
        
        

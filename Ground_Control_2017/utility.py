#!/usr/bin/env python
import multiprocessing as mp
import serial


class Parser():
    
    def __init__(self):
        self.set = serial.Serial()
        #print(ser.name)
    
    def open_port(self, name):
        try:
            self.ser = serial.Serial(name, timeout=2) #open serial port
        except:
            raise IOError("Serial port not found")
        print self.ser.name
        
        return self.ser.is_open
    
    def update(self):
        
    #if __name__ == '__main__':
        #Do scripty stuff
        
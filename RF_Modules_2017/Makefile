### DISCLAIMER -- WORK IN PROGRESS
### For detailed explanations about all of the available options, please refer
### to https://github.com/sudar/Arduino-Makefile/blob/master/arduino-mk-vars.md
### Original project where this Makefile comes from:
### https://github.com/WeAreLeka/Bare-Arduino-Project

### PROJECT_DIR
### The path to the project directory.
PROJECT_DIR = ~/Desktop/Clubs/SARP/Telemetry_2017/RF_Modules_2017/

### ARDMK_DIR
### Path to the Arduino-Makefile directory.
ARDMK_DIR = /usr/local

### ARDUINO_DIR
### Path to the Arduino application and resources directory.
ARDUINO_DIR = /Applications/Arduino.app/Contents/Java

### USER_LIB_PATH
### Path to where your project's libraries are stored.
USER_LIB_PATH := $(PROJECT_DIR)/lib

### BOARD_TAG
### The board you are currently using.
BOARD_TAG = teensy32

### AVR_TOOLS_DIR
### Path to the AVR tools directory such as avr-gcc, avr-g++, etc.
AVR_TOOLS_DIR = /usr/local

### AVRDUDE
### Path to avrdude directory
AVRDUDE = /usr/local/bin/avrdude

### CFLAGS_STD
### Set the C standard to be used during compilation. Documentation (https://github.com/WeAreLeka/Arduino-Makefile/blob/std-flags/arduino-mk-vars.md#cflags_std)
CFLAGS_STD        = -std=gnu11

### CXXFLAGS_STD
### Set the C++ standard to be used during compilation. Documentation (https://github.com/WeAreLeka/Arduino-Makefile/blob/std-flags/arduino-mk-vars.md#cxxflags_std)
CXXFLAGS_STD      = -std=gnu++11

### CXXFLAGS
### Flags you might want to set for debugging purpose. Comment to stop.
CXXFLAGS         += -pedantic -Wall -Wextra

### MONITOR_PORT
### The port your board is connected to. Using an '*' tries all the ports and finds the right one.
MONITOR_PORT      = /dev/tty.usbmodem*

### CURRENT_DIR
### Do not touch - used for binaries path
CURRENT_DIR       = $(shell basename $(CURDIR))

### OBJDIR
### This is where you put the binaries you just compile using 'make'
OBJDIR            = $(PROJECT_DIR)/bin/$(BOARD_TAG)/$(CURRENT_DIR)

### Do not touch - the path to Arduino.mk, inside the ARDMK_DIR
include $(ARDMK_DIR)/Arduino.mk

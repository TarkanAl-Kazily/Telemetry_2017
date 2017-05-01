## Telemetry 2017 - Data Diagnostics Telemetry system

This directory is contains the source files and documentation for the
University of Washington's Society for Advanced Rocket Propulsion (SARP)
Avionics project, the Data Diagnostics Telemetry system.
The purpose of this system is to transmit the sensor data collected
during the flight of the rocket.

### Directory contents

- README.md : The file you are reading right now.
- recieve_ground/ : This directory contains the .ino code for the ground
    station reciever module.
- serial_transmit/ : This directory contains the .ino code for the rocket
    transmitter module.
- Tests/ : This directory contains prior expirmental code that is under
    no guarantees of usefulness or completeness.

### Usage

The important files for this system are those in recieve_ground/ and
serial_transmit/. Each repository contains the .ino code for the program,
as well as a Makefile to compile and download the code. To use the Makefile,
_make_ must be installed, along with _Arduino-Makefile_ which can be found at:
https://github.com/sudar/Arduino-Makefile/
Arduino must be installed, as well as Teensyduino. Additionally, the code
requires the use of the RadioHead libraries.

The following environment variables must be set according to your development
platform:

_ARDUINO_DIR_ must be set to the directory where Arduino is insalled.
_ARDMK_DIR_ must be set to the directory where Arduino-Makefile is installed.
_AVR_TOOLS_DIR_ must be set to the directory where the avr build tools are
installed.
_ARDUINO_LIBRARIES_ must be set to the directory where the libraries are
stored.

Once these variables have been properly set, typing "make" from within the
recieve_ground/ or serial_transmit/ folders should compile the code, producing
a build folder in the same directory. To upload, type "make upload" after,
and follow the standard process to upload code to the Teensy.

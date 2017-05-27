/* 
 * serial_transmit.ino
 * Author: Tarkan Al-Kazily
 *
 * This program is designed for the University of Washington's undergraduate
 * rocket club, The Society for Advanced Rocket Propulsion, for use in
 * ESRA's Intercollegiate Rocket Engineering Competition in 2017.
 *
 * This program is part of the Data Diagnostics Telemetry system. It processes
 * data from the first serial port and transmits it using an RFM23BP board.
 * Additionally it logs the data it receives to a Micro SD card using a Sparkfun
 * OpenLog over Serial3.
 *
 * See the RadioHead libraries for documentation on how to use the RFM23BP.
 */

#include <RHReliableDatagram.h>
#include <RH_RF22.h>
#include <SPI.h>

// Define a debug macro if the DEBUG tag was set during compilation
#ifdef DEBUG
#define DEBUG_MESSAGE(x) Serial.println(x)
#else
#define DEBUG_MESSAGE(x)
#endif

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

// The standard delay in milliseconds
#define DELAY 500 
// The period in milliseconds to transmit call sign - 600000 ms is 10 minutes
#define CALL_FREQ 500

#define TRANSMIT_FREQ 434.0
#define TRANSMIT_POWER RH_RF22_RF23B_TXPOW_1DBM 

#define DATA_BAUD 115200

// Singleton instance of the radio driver
RH_RF22 driver;

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, CLIENT_ADDRESS);

// Dont put this on the stack:
uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];
// The amateur radio call sign - MAKE SURE TO UPDATE THIS 
uint8_t call[10] = {'[', 'K', 'I', '7', 'A', 'F', 'R', '-', '2', ']'};
// A counter to keep track of whether to send out call sign
unsigned long time;

uint8_t data[RH_RF22_MAX_MESSAGE_LEN];

// Prints an acknowledgement message
void printAck(uint8_t from);

// Logs a buffer to the SD card
void logBuf(uint8_t *buf, int len);

// Logs a string to the SD card
void logMessage(char *msg);

void setup() {
  Serial.begin(9600);
  Serial.println("Starting up");
  delay(2000);

  if (!manager.init()) {
    // Init failed
    logMessage("Init failed");
    while (1);
  }

  // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
  driver.setFrequency(TRANSMIT_FREQ);
  driver.setTxPower(TRANSMIT_POWER);
  time = millis();
  Serial1.begin(DATA_BAUD);
  while (Serial1.available() == 0) {
    Serial.println("Nothing to read");
    delay(50);
  }
}

void loop() {
  if (Serial1.available() > 0) {
    // Read the data from the Serial 1 port
    uint8_t result = Serial1.readBytes((char*) data, sizeof(data));
    Serial.write(data, result);
    // If any data was read
    if (result != 0) {
      // log the data
      logBuf(data, result);
      // and send the data
      DEBUG_MESSAGE("TRANSMITTING");
      if (manager.sendtoWait(data, result, RH_BROADCAST_ADDRESS)) {
        logMessage("Acknowledged msg");
      } else {
        logMessage("No ack on msg");
      }
      DEBUG_MESSAGE("FINISHED");
      delay(DELAY);
    }
  }

  if (millis() - time > CALL_FREQ) {
    logMessage("Sending call");
    DEBUG_MESSAGE("TRANSMITTING");
    if (manager.sendtoWait(call, 10, RH_BROADCAST_ADDRESS)) {
      logMessage("Acknowledged call");
    } else {
      logMessage("No ack on call");
    }
    DEBUG_MESSAGE("FINISHED");
    time = millis();
    delay(DELAY);
  }
}

// Prints out to the serial port an acknowledgement message
void printAck(uint8_t from) {
  DEBUG_MESSAGE("got reply from : 0x");
  DEBUG_MESSAGE(from);
  DEBUG_MESSAGE(": ");
  DEBUG_MESSAGE((char*)buf);
  DEBUG_MESSAGE("\n");
}

void logBuf(uint8_t *buf, int len) {
  /*
  Serial3.print(millis());
  Serial3.print("ms:");
  Serial3.write(buf, len);
  Serial3.write(13);
  */
}

void logMessage(char *msg) {
  DEBUG_MESSAGE(msg);
  DEBUG_MESSAGE("\n");
  /*
  Serial3.print(millis());
  Serial3.print("ms:");
  Serial3.print(msg);
  Serial3.write(13);
  */
}

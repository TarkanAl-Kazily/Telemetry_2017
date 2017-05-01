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
 * OpenLog.
 *
 * See the RadioHead libraries for documentation on how to use the RFM23BP.
 */

#include <RHReliableDatagram.h>
#define RH_RF22_MAX_MESSAGE_LEN 120
#include <RH_RF22.h>
#include <SPI.h>

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

// The standard delay in milliseconds
#define DELAY 300 
// The period in milliseconds to transmit call sign
#define CALL_FREQ 3000

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

void setup() {
  Serial.begin(9600);
  if (!manager.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
  Serial3.begin(9600);
  Serial3.print("Beginning test\r");
  time = millis();
}

void loop() {
  if (Serial.available() > 0) {
    for (int i = 0; i < sizeof(data); i++) {
      data[i] = 0;
    }
    uint8_t result = Serial.readBytes((char*) data, sizeof(data));
    Serial.print("RESULT WAS : ");
    Serial.println(result);
    if (result != 0) {

      // log incoming data
      Serial3.write(data, result);
      Serial3.write(13); // new line as int

      Serial.println("Sending to rf22_reliable_datagram_server");

      // Send a message to manager_server
      if (manager.sendtoWait(data, result, SERVER_ADDRESS)) {
        // Now wait for a reply from the server
        uint8_t len = sizeof(buf);
        uint8_t from;
        if (manager.recvfromAckTimeout(buf, &len, 2000, &from)) {
          printAck(from);
        } else {
          Serial.println("Yippie!");
        }
      } else {
        Serial.println("Did not recieve acknowledgement");
        Serial3.print("Did not recieve acknowledgement\r");
      }

      delay(DELAY);
    }
  }

  if (millis() - time > CALL_FREQ) {
    Serial.println("Sending callsign");
    if (manager.sendtoWait(call, 10, SERVER_ADDRESS)) {
      // Now wait for a reply from the server
      uint8_t len = sizeof(buf);
      uint8_t from;
      if (manager.recvfromAckTimeout(buf, &len, 2000, &from)) {
        printAck(from);
      } else {
        Serial.println("She noticed me!");
      }
    } else {
      Serial.println("Did not recieve acknowledgement");
    }
    time = millis();
    delay(DELAY);
  }
}

// Prints out to the serial port an acknowledgement message
void printAck(uint8_t from) {
  Serial.print("got reply from : 0x");
  Serial.print(from, HEX);
  Serial.print(": ");
  Serial.println((char*)buf);
}

/* 
 * numbers_transmit.ino
 * Author: Tarkan Al-Kazily
 *
 * This program is designed for the University of Washington's undergraduate
 * rocket club, The Society for Advanced Rocket Propulsion, for use in
 * ESRA's Intercollegiate Rocket Engineering Competition in 2017.
 *
 * This program sends incrementing numbers from an RFM23BP system
 *
 * See the RadioHead libraries for documentation on how to use the RFM23BP.
 */

#include <RHReliableDatagram.h>
#include <RH_RF22.h>
#include <SPI.h>

// Define a debug macro if the DEBUG tag was set during compilation
#ifdef DEBUG
#define DEBUG_MESSAGE(x) Serial.print(x)
#else
#define DEBUG_MESSAGE(x)
#endif

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

// The standard delay in milliseconds
#define DELAY 100 
// The period in milliseconds to transmit call sign - 600000 ms is 10 minutes
#define CALL_FREQ 300000

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

// A buffer to send data from
uint8_t data[RH_RF22_MAX_MESSAGE_LEN];

// Prints an acknowledgement message
void printAck(uint8_t from);

// Logs a buffer to the SD card
void logBuf(uint8_t *buf, int len);

// Logs a string to the SD card
void logMessage(char *msg);

void makeCountBuf(uint8_t buf[]);

unsigned int count = 0;

void setup() {
  Serial.begin(9600);
  DEBUG_MESSAGE(RH_RF22_MAX_MESSAGE_LEN);
  DEBUG_MESSAGE("\n");
  delay(2000);
  Serial.println("FINISHED DELAY");
  if (!manager.init()) {
    DEBUG_MESSAGE("init failed\n");
  }
  // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
  Serial3.begin(9600);
  Serial3.print("Beginning test\r");
  time = millis();
}

void loop() {
  count++;
  if (count > 10000000) {
    count = 0;
  }
  
  makeCountBuf(data);
  Serial.write(data, 12);
  logBuf(data, 12);

  // Send message as a broadcast - do not block for a confirmation
  if (manager.sendtoWait(data, 12, RH_BROADCAST_ADDRESS)) {
    logMessage("Sent msg");
  } 

  delay(DELAY);

  if (millis() - time > CALL_FREQ) {
    logMessage("Sending call");
    if (manager.sendtoWait(call, 10, RH_BROADCAST_ADDRESS)) {
      logMessage("Acknowledged call");
    } else {
      logMessage("No ack on call");
    }
  }
}

void logBuf(uint8_t *buf, int len) {
  Serial3.print(millis());
  Serial3.print("ms:");
  Serial3.write(buf, len);
  Serial3.write(13);
}

void logMessage(char *msg) {
  DEBUG_MESSAGE(msg);
  DEBUG_MESSAGE("\n");
  Serial3.print(millis());
  Serial3.print("ms:");
  Serial3.print(msg);
  Serial3.write(13);
}

void makeCountBuf(uint8_t buf[]) {
  buf[0] = '!';
  buf[1] = 'A';
  buf[2] = ':';
  unsigned int num = count;
  for (uint8_t i = 10; i >= 3; i--) {
    uint8_t digit = num % 10;
    buf[i] = digit + '0';
    num /= 10;
  }
  buf[11] = ';';
}

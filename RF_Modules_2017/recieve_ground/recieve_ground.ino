// rf22_reliable_datagram_server.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable messaging server
// with the RHReliableDatagram class, using the RH_RF22 driver to control a RF22 radio.
// It is designed to work with the other example rf22_reliable_datagram_client
// Tested on Duemilanove, Uno with Sparkfun RFM22 wireless shield
// Tested on Flymaple with sparkfun RFM22 wireless shield
// Tested on ChiKit Uno32 with sparkfun RFM22 wireless shield

#include <RHReliableDatagram.h>
#include <RH_RF22.h>
#include <SPI.h>

#ifdef DEBUG
#define DEBUG_MESSAGE(x) Serial.print(x)
#else
#define DEBUG_MESSAGE(x)
#endif

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

#define TRANSMIT_FREQ 434.0
#define TRANSMIT_POWER RH_RF22_RF23BP_TXPOW_30DBM

#define DELAY 100

// Singleton instance of the radio driver
RH_RF22 driver;

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, SERVER_ADDRESS);

void setup() 
{
  Serial.begin(9600);
  delay(2000);
  if (!manager.init())
    Serial.println("init failed");
  // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
  driver.setFrequency(TRANSMIT_FREQ);
  driver.setTxPower(TRANSMIT_POWER);
  DEBUG_MESSAGE(RH_RF22_MAX_MESSAGE_LEN);
}

// Dont put this on the stack:
uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];

void loop()
{
  if (manager.available())
  {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    if (manager.recvfromAck(buf, &len, &from))
    {
      DEBUG_MESSAGE("got request from : 0x");
      DEBUG_MESSAGE(from);
      DEBUG_MESSAGE(": ");
      Serial.write(buf, len);
      Serial.write('\n');
    }
  }
}


// rf22_reliable_datagram_client.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable messaging client
// with the RHReliableDatagram class, using the RH_RF22 driver to control a RF22 radio.
// It is designed to work with the other example rf22_reliable_datagram_server
// Tested on Duemilanove, Uno with Sparkfun RFM22 wireless shield
// Tested on Flymaple with sparkfun RFM22 wireless shield
// Tested on ChiKit Uno32 with sparkfun RFM22 wireless shield

// ===============
// Example code from RadioHead's RF22 Examples. Augmented with a simple Serial
// communication interface to send received messages from the Diagnostics MCU
//
// Notable changes between this and planned product:
// This example uses the RHReliableDatagram, which features message
// confirmations. This increases reliability, but also time and might not be
// worth keeping. There is a Manager class that foregoes this feature.
//
// Serial data confirmations are desired to increase the reliability of
// recieving the correct message to send from the Diagnostics MCU.
//
// Call Signs will need to be sent in the message data fields. At least
// once every ten minutes
// ===============


#include <RHReliableDatagram.h>
#include <RH_RF22.h>
#include <SPI.h>

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

#define MAX_DATA_SIZE 128 // Must be less than RH_RF22_MAX_MESSAGE_LEN (255)

// Singleton instance of the radio driver
RH_RF22 driver;

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, CLIENT_ADDRESS);

void setup()
{
    Serial.begin(9600);
    char received[20];
    do {
        // Send a message to the Diagnostic MCU to ensure
        // serial communication is connected
        Serial.write("ARDUINO_READY");
        // Wait until recieve a message over Serial
        while (!Serial.available()) {
            // Add code to blink an LED to show that the device is attempting to
            // connect to the Diagnostics MCU
        }
        // Check to see if received "DIAGNOSTICS_READY"
        Serial.readBytes(recieved, sizeof(received));

    } while (!recieved.equals("DIAGNOSTICS_READY"));
    // Connection has been established
    Serial.write("CONNECTED");
    // Set LED to be solid
    delay(2000);

    if (!manager.init()) {
        //Serial.println("init failed");
        Serial.write("TRANSMITTER_INIT_FAILED");
        // Set LED to be off
    }

    uint8_t connect_msg[] = "ARDUINO_TRANSMITTING";
    boolean connected = false;
    do {
        // Send a message with automatic confirmation, and then wait for reply
        // message
        if (manager.sendtoWait(connect_msg, sizeof(connect_msg), SERVER_ADDRESS)) {
            uint8_t len = sizeof(buf);
            uint8_t from;
            if (manager.recvfromAckTimeout(buf, &len, 2000, &from)) {
                String received_msg = (char *) buf;
                if (received_msg.startsWith("GROUND_CONFIRM")) {
                    // Recieved confirmation of connection
                    connected = true;
                }
            } else {
                // no reply, still not connected.
            }
        }
    } while (!connected);
    // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
}

uint8_t data[] = "Hello World!";
// Dont put this on the stack:
uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];

void loop()
{
    //Serial.println("Sending to rf22_reliable_datagram_server");
    char diagnostic_data[MAX_DATA_SIZE];
    if (Serial.available()) {
        getDiagnosticData(diagnostic_data, MAX_DATA_SIZE);
    } else {
        diagnostic_data = "NO_NEW_DATA";
    }

    // Send a message to manager_server
    if (manager.sendtoWait(data, sizeof(data), SERVER_ADDRESS))
    {
        // LED Output to show that message sent
    }
    else
    //Serial.println("sendtoWait failed");
    delay(100);
}

void getDiagnosticData(char &array, int len) {
    char start = Serial.read();
    // While start isn't the <stx> ascii character
    while (start != 2 && Serial.available()) {
        start = Serial.read();
    }
    // Read everything in Serial buffer until reading the <etx> character
    Serial.readBytesUntil((char) 3, array, len);
    // May need to trim off the <etx> character - depending on
    // how the method is implemented.
}

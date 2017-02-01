/*
 * RF_Basic_Comm_Test.cpp
 *
 * This program is intended to be used as a starting point for prototyping SARP's
 * radio data telemetry system. This system is designed to use the RFM23BP modules.
 *
 * This program will send increasing integers every 5 seconds to a reciever module,
 * which will print these integers out onto a computer screen over Serial.
 * The RFM23BP communicates with the Arduino via SPI.
 *
 * Pin connections:
 * Arduino      | RFM23BP
 * GND ---------- GND --\ (Ground in)
 *                SDN --/ (Shutdown in)
 *
 * 5V ----------- VCC (5V in) Both supplied externally
 * 
 * D2 ----------- NIRQ (Interrupt request out)
 * D10 ---------- NSEL (Slave Select)
 * D13 ---------- SCK  (SPI Clock)
 * D11 ---------- SDI  (SPI Master Out Slave In)
 * D10 ---------- SDO  (SPI Master In Slave Out)
 *
 *            /-- GPIO0 (Out to control receiver antenna RXON) 
 *            \-- RXON  (RX antenna control in)
 *            /-- GPIO1 (Out to control transmitter antenna TXON)
 *            \-- TXON  (TX antenna control in)
 *
 *
 */

#include <RH_RF22.h>

// Singleton instance of the radio driver
RH_RF22 rf22;

int count = 0;

void setup() {
    Serial.begin(9600);
    while (!Serial);
    Serial.println("Initializing...");
    if (!rf22.init()) {
        Serial.println("rf22 driver init failed");
    } else {
        rf22.setTxPower(RH_RF22_RF23B_TXPOW_1DBM);
        Serial.println("rf22 driver is initialized");
    }
    // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36

}

void loop() {
    Serial.println("Sending to rf22_server");
    // Send a message to rf22_server
    uint8_t data[] = "Hello World!";
    rf22.send(data, sizeof(data));

    rf22.waitPacketSent();
    // Now wait for a reply
    uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf22.waitAvailableTimeout(500))
    {
        // Should be a reply message for us now   
        if (rf22.recv(buf, &len))
        {
            Serial.print("got reply: ");
            Serial.println((char*)buf);
        }
        else
        {
            Serial.println("recv failed");
        }
    }
    else
    {
        Serial.println("No reply, is rf22_server running?");
    }
    delay(400);
}

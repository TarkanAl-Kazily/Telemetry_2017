/*
 * driver_server.ino
 *
 * This program is intended to be used as a starting point for prototyping SARP's
 * radio data telemetry system. This system is designed to use the RFM23BP modules.
 *
 * This program will recieve and print the recieved array of bytes as characters
 * onto a computer screen over Serial.
 *
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

void setup()
{
    Serial.begin(9600);
    if (!rf22.init())
        Serial.println("init failed");
    // Defaults after init are 434.0MHz, 0.05MHz AFC pull-in, modulation FSK_Rb2_4Fd36
}

void loop()
{
    if (rf22.available())
    {
        // Should be a message for us now   
        uint8_t buf[RH_RF22_MAX_MESSAGE_LEN];
        uint8_t len = sizeof(buf);
        if (rf22.recv(buf, &len))
        {
            //      RF22::printBuffer("request: ", buf, len);
            Serial.print("got request: ");
            Serial.println((char*)buf);
            //      Serial.print("RSSI: ");
            //      Serial.println(rf22.lastRssi(), DEC);

            // Send a reply
            uint8_t data[] = "And hello back to you";
            rf22.send(data, sizeof(data));
            rf22.waitPacketSent();
            Serial.println("Sent a reply");
        }
        else
        {
            Serial.println("recv failed");
        }
    }
}


#define DATA_BAUD 115200

void setup() {
  Serial.begin(DATA_BAUD);

}

void loop() {
  Serial.print("!A:HELLOTUA;");
  Serial.print("!B:00007331;");
  delay(250);
}

#include <Regexp.h>
#define BAUD 9600

// Regexp docs: http://www.gammon.com.au/forum/?id=11063

// MEGA 2 (Ground)

void setup() {
  // To ground station
  Serial.begin(BAUD);
  // From Mega 1
  Serial1.begin(BAUD);
  Serial.println("Initialized");
  Serial1.println("TEST");
}

void loop() {

  //String typed_data;

  // Get incoming data
  if (Serial1.available()) {
    Serial.println(Serial.readStringUntil('\n'));
  } else {
    //typed_data = "";
  }
/*
  // Output to Ground Station
  if (typed_data != "") {
    Serial.println(typed_data);
  }*/
    //Serial1.println("TEST");

  delay(10);
  
}

/*
   This method determines if the given data value is properly formatted -
   Formatting accepted is of the following: !---#:#########;
   In regex it is "![A-Z]{3}[0-9]:[0-9]{9};"
*/
boolean formatted(String data) {
  char buf[data.length() + 1];
  data.toCharArray(buf, data.length() + 1);
  MatchState ms;
  ms.Target(buf);
  char result = ms.Match("![A-Z][A-Z][A-Z]%d:%d%d%d%d%d%d%d%d%d;");
  return result == 1;

}


#include <Regexp.h>
#define BAUD 115200
// Regexp docs: http://www.gammon.com.au/forum/?id=11063

// MEGA 1 (ROCKET)

void setup() {

    Serial.begin(BAUD);
    Serial1.begin(BAUD);
}

void loop() {
    
    String typed_data;
  // put your main code here, to run repeatedly:

  // Get data from Diagnostics
  if (Serial.available()) {
      typed_data = Serial.readStringUntil('\n');
  } else {
      typed_data = "";
  }
  
  // OUTPUT to next mega
  if (typed_data != "") {
      Serial1.println(typed_data);
  }

}

/*
 * This method determines if the given data value is properly formatted -
 * Formatting accepted is of the following: !---#:#########;
 * In regex it is "![A-Z]{3}[0-9]:[0-9]{9};"
 */
boolean formatted(String data) {
    char buf[data.length() + 1];
    data.toCharArray(buf, data.length() + 1);
    MatchState ms;
    ms.Target(buf);
    char result = ms.Match("![A-Z][A-Z][A-Z]%d:%d%d%d%d%d%d%d%d%d;");
    return result == 1;

}

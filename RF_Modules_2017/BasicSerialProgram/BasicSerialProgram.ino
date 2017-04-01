#include <Regexp.h>
// Regexp docs: http://www.gammon.com.au/forum/?id=11063


// WORKS!
void setup() {

    Serial.begin(9600);
    Serial1.begin(9600);
    Serial.println("Hello World");
    boolean result = formatted("!ABC4:123456789;");
    if (result) {
          Serial.println("\tFIRST Data Formatted Correctly");
      } else {
          Serial.println("\tFISRT Data Format Error");
      }
}

void loop() {
  /*   
    String typed_data;
  // put your main code here, to run repeatedly:

  if (Serial.available()) {
      typed_data = Serial.readStringUntil('\n');
      if (formatted(typed_data)) {
          Serial.println("\tData Formatted Correctly");
      } else {
          Serial.println("\tData Format Error");
      }
  } else {
      typed_data = "";
  }
  
    
  if (typed_data != "") {
      Serial1.println(typed_data);
  }*/

  if (Serial1.available()) {
      Serial.println(Serial1.readStringUntil('\n'));
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


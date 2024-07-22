bool status_open = true;
bool status_run = false;
bool status_finish = false;

void setup() {
  Serial.begin(9600);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  attachInterrupt(digitalPinToInterrupt(2), interuptFunc2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(3), interuptFunc3, RISING);
  digitalWrite(10, digitalRead(2));
  digitalWrite(11, HIGH);

}

void loop() {
  if (digitalRead(2) == LOW && status_open == false) {
    if (status_run) {
      digitalWrite(9, HIGH);
      delay(500);
      digitalWrite(9, LOW);
      Serial.println("NANO : ALERT! THE LID OPEN WHILE PROCESS.");
      status_run = false;
    }
    status_open = true;
    Serial.println("NANO : LID OPEN");
    delay(500);
  }
  if (digitalRead(2) == HIGH && status_open == true) {
    status_open = false;
    Serial.println("NANO : LID CLOSE");
    delay(500);
  }

  if(status_finish == true){
    delay(100);
    status_finish = false;
  }

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command.length() > 0) {
      if (command == "PC : STATUS") {
        if (digitalRead(2) == LOW) {
          Serial.println("NANO : LID OPEN");
        } else {
          Serial.println("NANO : LID CLOSE");
        }
      }
      if (command == "PC : OPEN") {
        if (status_run) {
          digitalWrite(9, HIGH);
          delay(500);
          digitalWrite(9, LOW);
          delay(1000);
          status_run = false;
        }
        digitalWrite(11, LOW);
        delay(200);
        digitalWrite(8, HIGH);
        delay(500);
        digitalWrite(8, LOW);
        delay(1000);
        digitalWrite(11, HIGH);
        if (digitalRead(2) == HIGH) {
          Serial.println("NANO : LID CLOSE");
        } else {
          Serial.println("NANO : LID OPEN");
        }
      }
      if (command == "PC : RUN") {
        Serial.println("NANO : RUN");
        digitalWrite(9, HIGH);
        delay(500);
        digitalWrite(9, LOW);
        status_run = true;
      }
      if (command == "PC : STOP") {
        Serial.println("NANO : STOP");
        digitalWrite(9, HIGH);
        delay(500);
        digitalWrite(9, LOW);
        status_run = false;
      }
    }
  }

  // // Send "Red" or "Green" based on some condition
  // // For demonstration, we'll send "Red" every 2 seconds, then "Green"
  // static bool toggle = true;
  // if (digitalRead(2) == HIGH) {
  //   Serial.println("NANO BT2 : ON 2");
  // }
  // if (digitalRead(3) == HIGH) {
  //   Serial.println("NANO BT2 : ON 3");
  // }
  // if (toggle) {
  //   Serial.println("NANO : Red");
  //   digitalWrite(8, HIGH);
  // } else {
  //   Serial.println("NANO : Green");
  //   digitalWrite(8, LOW);
  // }
  // toggle = !toggle;
  // delay(2000);  // Change color every 2 seconds
}

void interuptFunc2() {
  digitalWrite(10, digitalRead(2));
  // if (digitalRead(2) == HIGH) {
  //   Serial.println("NANO BT2 INT : ON 2");
  //   digitalWrite(9, HIGH);
  //   delay(1000);
  //   digitalWrite(9, LOW);
  // }
}
void interuptFunc3() {
  if(status_finish == false && status_run == true){
    Serial.println("NANO : FINISH");
    status_finish = true;
  }
}

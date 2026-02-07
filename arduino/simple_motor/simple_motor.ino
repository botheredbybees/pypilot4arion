// Pypilot Arduino PWM Servo for IBT_2 H-bridge
// D9 = RPWM (Port), D10 = LPWM (Starboard)
// Full pypilot protocol minimal

void setup() {
  Serial.begin(38400);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  analogWrite(9, 0);
  analogWrite(10, 0);
}

void loop() {
  if (Serial.available() >= 4) {
    uint8_t cmd = Serial.read();
    uint8_t b1 = Serial.read();
    uint8_t b2 = Serial.read();
    uint8_t crc = Serial.read();

    if (cmd == 0xc7) {  // Command packet
      int16_t demand = (b1 << 8) | b2;
      uint8_t pwm = constrain(abs(demand - 1000) * 255 / 1000, 0, 255);

      if (demand > 1000) {  // Port
        analogWrite(9, pwm);
        analogWrite(10, 0);
        digitalWrite(LED_BUILTIN, HIGH);
      } else if (demand < 1000) {  // Starboard
        analogWrite(9, 0);
        analogWrite(10, pwm);
        digitalWrite(LED_BUILTIN, HIGH);
      } else {  // Stop
        analogWrite(9, 0);
        analogWrite(10, 0);
        digitalWrite(LED_BUILTIN, LOW);
      }

      // Respond neutral position
      Serial.write(0x8f); // Flags
      Serial.write(0xe8);
      Serial.write(0x03); 
      Serial.write(0x1a); // CRC
    }
  }
}

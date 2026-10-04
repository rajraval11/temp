const int lm35Pin = A0;
const int greenLedPin = 7;
const int redLedPin = 8;
const int buzzerPin = 9;

const float NORMAL_LIMIT = 35.0;
const float WARNING_LIMIT = 40.0;

void setup() {
  Serial.begin(9600);
  pinMode(greenLedPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
}

void loop() {
  int sensorValue = analogRead(lm35Pin);
  
  float voltage = sensorValue * (5.0 / 1023.0);
  
  float temperature = voltage * 100.0;
  
  Serial.print("TEMP:");
  Serial.println(temperature);
  
  if (temperature < NORMAL_LIMIT) {
    digitalWrite(greenLedPin, HIGH);
    digitalWrite(redLedPin, LOW);
    noTone(buzzerPin);
  } else if (temperature < WARNING_LIMIT) {
    digitalWrite(greenLedPin, HIGH);
    digitalWrite(redLedPin, HIGH);
    noTone(buzzerPin);
  } else {
    digitalWrite(greenLedPin, LOW);
    digitalWrite(redLedPin, HIGH);
    tone(buzzerPin, 1000); // 1kHz tone for buzzer
  }
  
  delay(2000);
}

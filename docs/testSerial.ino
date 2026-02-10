int niveau = 0;
float uArduino;
float uPile;
void setup() {
  Serial.begin(9600);
}


void  loop() {
  niveau = analogRead(A0);
  uArduino = niveau * 5. /1023.;
  uPile = uArduino * 9.2;
  Serial.println(uArduino);
  Serial.println(uPile);
  delay(500);
}


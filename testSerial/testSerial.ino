int temps = 0;
void setup() {
  Serial.begin(9600);

}

void  loop() {
  while (Serial.available()){
  //Serial.write(temps);
 // Serial.write(90);
  Serial.println(temps);
  Serial.println(90);
  temps += 1;
  delay(1000);
  }
}

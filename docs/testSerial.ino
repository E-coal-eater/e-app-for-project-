int niveau = 0;
int pourcentage = 0;
float uArduino;
float uPile;

const int Vmax = 42;
const int Vmin = 36;

void setup() {
  Serial.begin(9600);
}


void  loop() {
  niveau = analogRead(A0);
  uArduino = niveau * 5. /1023;
  uPile = uArduino * 9.2;
  Serial.println(uArduino);
  Serial.println(uPile);
  pourcentage = (uPile - Vmin)/(Vmax - Vmin)*100
  delay(500);
}


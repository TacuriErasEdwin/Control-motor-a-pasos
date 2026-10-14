
const int DIR_PIN = 7;
const int STEP_PIN = 3;

const int TIEMPO_PULSO = 1500; // microsegundos
const long MAX_PASOS = 2000;  // límite para esta prueba

String comando = "";

void setup() {
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  digitalWrite(STEP_PIN, LOW);

  Serial.begin(9600);
  Serial.println("ARDUINO_LISTO");
}

void moverMotor(char direccion, long pasos) {
  // R = derecha, L = izquierda.
  // Si el sentido físico resulta invertido, intercambia HIGH y LOW.
  digitalWrite(DIR_PIN, direccion == 'R' ? HIGH : LOW);
  delay(10);

  for (long i = 0; i < pasos; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(TIEMPO_PULSO);

    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(TIEMPO_PULSO);
  }
}

void loop() {
  if (Serial.available() > 0) {
    comando = Serial.readStringUntil('\n');
    comando.trim();

    if (comando.length() >= 3 &&
        comando.charAt(1) == ',' &&
        (comando.charAt(0) == 'R' ||
         comando.charAt(0) == 'L')) {

      char direccion = comando.charAt(0);
      long pasos = comando.substring(2).toInt();

      if (pasos > 0 && pasos <= MAX_PASOS) {
        Serial.print("EJECUTANDO ");
        Serial.println(comando);

        moverMotor(direccion, pasos);

        Serial.print("OK ");
        Serial.println(comando);
      } else {
        Serial.println("ERROR: PASOS FUERA DE LIMITE");
      }
    } else {
      Serial.println("ERROR: COMANDO INVALIDO");
    }
  }
}

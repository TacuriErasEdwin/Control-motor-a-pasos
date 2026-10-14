
/*
  PROYECTO: CONTROL DE MOTOR A PASOS PARA ESTRIBOS
  PLACA: Arduino Mega 2560
  DRIVER: HY-DIV268N-5A

  DIR         = Pin 7
  STEP/PUL    = Pin 3
  SENSOR CERO = Pin 22 (NO)

  COMANDOS DESDE PYTHON:
  HOME      -> Referenciar
  R,200     -> Mover 200 pasos a la derecha
  L,100     -> Mover 100 pasos a la izquierda
  END       -> Finalizar ciclo y exigir nueva referencia
*/

const int DIR_PIN = 7;
const int STEP_PIN = 3;
const int LIMITE_CERO = 22;

const int TIEMPO_PULSO = 1500;

const char HOME_DIR = 'R';

const long MAX_PASOS_MOVIMIENTO = 2000;
const long MAX_PASOS_BUSQUEDA = 10000;
const long MAX_PASOS_LIBERACION = 2000;

const int PASOS_RETROCESO = 20;

bool referenciado = false;

// --------------------------------------------------
// LECTURA DEL SENSOR
// INPUT_PULLUP: LOW = activado, HIGH = libre
// --------------------------------------------------
bool sensorPresionado() {
  return digitalRead(LIMITE_CERO) == LOW;
}

// --------------------------------------------------
// GENERAR UN PASO
// --------------------------------------------------
void darPaso(char direccion) {
  digitalWrite(DIR_PIN, direccion == 'R' ? HIGH : LOW);

  delayMicroseconds(10);

  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(TIEMPO_PULSO);

  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(TIEMPO_PULSO);
}

// --------------------------------------------------
// REFERENCIACION HOME
// Conserva la lógica original
// --------------------------------------------------
bool buscarCero() {
  referenciado = false;

  Serial.println("HOMING_START");
  Serial.print("Sensor inicial: ");
  Serial.println(sensorPresionado() ? "ACTIVADO" : "LIBRE");

  Serial.print("Direccion de busqueda: ");
  Serial.println(HOME_DIR);

  char direccionAtras = (HOME_DIR == 'R') ? 'L' : 'R';

  long pasos = 0;

  // 1. Si el sensor está activado, liberarlo.
  while (sensorPresionado() &&
         pasos < MAX_PASOS_LIBERACION) {
    darPaso(direccionAtras);
    pasos++;
  }

  if (sensorPresionado()) {
    Serial.println("ERROR: SENSOR_NO_LIBERA");
    return false;
  }

  Serial.println("BUSCANDO_CERO");

  // 2. Buscar el sensor.
  pasos = 0;

  while (!sensorPresionado() &&
         pasos < MAX_PASOS_BUSQUEDA) {
    darPaso(HOME_DIR);
    pasos++;
  }

  if (!sensorPresionado()) {
    Serial.println("ERROR: CERO_NO_ENCONTRADO");
    return false;
  }

  Serial.println("CERO_DETECTADO");

  // 3. Retroceder hasta liberar el sensor.
  pasos = 0;

  while (sensorPresionado() &&
         pasos < MAX_PASOS_LIBERACION) {
    darPaso(direccionAtras);
    pasos++;
  }

  if (sensorPresionado()) {
    Serial.println("ERROR: SENSOR_NO_LIBERA");
    return false;
  }

  // 4. Retroceso adicional para dejar libre el sensor.
  for (int i = 0; i < PASOS_RETROCESO; i++) {
    darPaso(direccionAtras);
  }
    if (sensorPresionado()) {
      Serial.println("ERROR: SENSOR_REACTIVADO");
      return false;
    }
  

  referenciado = true;

  Serial.println("ZERO_OK");
  return true;
}

// --------------------------------------------------
// MOVIMIENTO NORMAL
// El sensor no cancela el movimiento normal.
// --------------------------------------------------
bool moverMotor(char direccion, long pasos) {

  if (!referenciado) {
    Serial.println("ERROR: REFERENCIAR_PRIMERO");
    return false;
  }

  if (direccion != 'R' && direccion != 'L') {
    Serial.println("ERROR: DIRECCION_INVALIDA");
    return false;
  }

  if (pasos <= 0 || pasos > MAX_PASOS_MOVIMIENTO) {
    Serial.println("ERROR: PASOS_INVALIDOS");
    return false;
  }

  for (long i = 0; i < pasos; i++) {
    darPaso(direccion);
  }

  Serial.print("OK ");
  Serial.print(direccion);
  Serial.print(",");
  Serial.println(pasos);

  return true;
}

// --------------------------------------------------
// PROCESAMIENTO DE COMANDOS DESDE PYTHON
// --------------------------------------------------
void procesarComando(String comando) {

  comando.trim();

  if (comando.length() == 0) {
    return;
  }

  if (comando == "HOME") {
    buscarCero();
    return;
  }

  if (comando == "END") {
    referenciado = false;
    Serial.println("SEQUENCE_DONE");
    return;
  }

  // Formato: R,200 o L,100
  int separador = comando.indexOf(',');

  if (separador > 0) {

    char direccion = comando.charAt(0);
    String textoPasos = comando.substring(separador + 1);

    textoPasos.trim();

    if (textoPasos.length() == 0) {
      Serial.println("ERROR: PASOS_INVALIDOS");
      return;
    }

    for (unsigned int i = 0;
         i < textoPasos.length(); i++) {
      if (!isDigit(textoPasos.charAt(i))) {
        Serial.println("ERROR: PASOS_INVALIDOS");
        return;
      }
    }

    long pasos = textoPasos.toInt();

    moverMotor(direccion, pasos);
    return;
  }

  Serial.println("ERROR: COMANDO_DESCONOCIDO");
}

// --------------------------------------------------
// CONFIGURACION INICIAL
// --------------------------------------------------
void setup() {

  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  pinMode(LIMITE_CERO, INPUT_PULLUP);

  digitalWrite(STEP_PIN, LOW);

  Serial.begin(9600);

  Serial.println("ARDUINO_LISTO");
}

// --------------------------------------------------
// BUCLE PRINCIPAL
// --------------------------------------------------
void loop() {

  if (Serial.available() > 0) {

    String comando = Serial.readStringUntil('\n');

    procesarComando(comando);
  }
}

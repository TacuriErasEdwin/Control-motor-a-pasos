
// ======================================================
// CONTROL MOTOR PASO A PASO
// ARDUINO MEGA 2560
//
// MANUAL + REFERENCIACION + AUTOMATICO
// ======================================================


// ======================================================
// PINES
// ======================================================

const byte DIR  = 7;       // Dirección del motor
const byte STEP = 3;       // Pulso PUL

const byte MANUAL_AUTO = 10;   // Selector MANUAL/AUTOMATICO

const byte IZQUIERDA = 8;      // Pulsador izquierda
const byte DERECHA   = 9;      // Pulsador derecha

const byte START = 11;         // Inicio del ciclo
const byte REFERENCIAR = 12;   // Pulsador de referencia

const byte FIN_CERO = 22;      // Final de carrera


// ======================================================
// PARAMETROS DEL MOTOR
// ======================================================

const int PASOS_VUELTA = 200;

// Tiempo del pulso
const unsigned int tiempoPulso = 1500;


// ======================================================
// ESTADOS DEL AUTOMATICO
// ======================================================

enum EstadoAuto
{
  ESPERANDO_REFERENCIA,
  REFERENCIADO,
  EJECUTANDO_CICLO
};

EstadoAuto estadoAuto = ESPERANDO_REFERENCIA;


// ======================================================
// CONTROL DE CAMBIO MANUAL -> AUTOMATICO
// ======================================================

bool modoAnteriorManual = true;


// ======================================================
// GENERAR UN PASO
// ======================================================

void darPaso()
{
  digitalWrite(STEP, HIGH);
  delayMicroseconds(tiempoPulso);

  digitalWrite(STEP, LOW);
  delayMicroseconds(tiempoPulso);
}


// ======================================================
// REFERENCIACION
// ======================================================
//
// Secuencia:
//
// 1. Si ya esta sobre el final de carrera,
//    se aleja hacia la izquierda.
//
// 2. Busca nuevamente el final de carrera
//    moviéndose hacia la derecha.
//
// 3. Cuando lo encuentra, retrocede 10 pasos
//    hacia la izquierda.
//
// ======================================================

bool referenciar()
{
  // ----------------------------------------------------
  // SI YA ESTA ACTIVADO EL FINAL DE CARRERA
  // ----------------------------------------------------

  if (digitalRead(FIN_CERO) == LOW)
  {
    // Dirección izquierda
    digitalWrite(DIR, LOW);

    // Alejarse hasta liberar el final de carrera
    while (digitalRead(FIN_CERO) == LOW)
    {
      darPaso();
    }

    delay(200);
  }


  // ----------------------------------------------------
  // BUSCAR EL FINAL DE CARRERA
  // MOVIMIENTO HACIA LA DERECHA
  // ----------------------------------------------------

  digitalWrite(DIR, HIGH);

  while (digitalRead(FIN_CERO) == HIGH)
  {
    darPaso();
  }


  // Detener pulsos
  digitalWrite(STEP, LOW);

  delay(200);


  // ----------------------------------------------------
  // RETROCEDER 10 PASOS
  // ----------------------------------------------------

  digitalWrite(DIR, LOW);

  for (int i = 0; i < 10; i++)
  {
    darPaso();
  }


  // Detener motor
  digitalWrite(STEP, LOW);

  return true;
}


// ======================================================
// MODO MANUAL
// ======================================================
//
// En manual el motor puede moverse libremente.
// El final de carrera NO se utiliza.
//
// ======================================================

void modoManual()
{
  // ----------------------------------------------------
  // IZQUIERDA
  // ----------------------------------------------------

  if (digitalRead(IZQUIERDA) == LOW)
  {
    digitalWrite(DIR, LOW);

    darPaso();
  }

  // ----------------------------------------------------
  // DERECHA
  // ----------------------------------------------------

  else if (digitalRead(DERECHA) == LOW)
  {
    digitalWrite(DIR, HIGH);

    darPaso();
  }

  // ----------------------------------------------------
  // NINGUN PULSADOR
  // ----------------------------------------------------

  else
  {
    digitalWrite(STEP, LOW);
  }
}


// ======================================================
// MOVER MOTOR UNA CANTIDAD DE PASOS
// ======================================================

void moverMotor(int pasos, bool direccion)
{
  // Seleccionar dirección
  digitalWrite(DIR, direccion);


  // Generar cantidad de pasos
  for (int i = 0; i < pasos; i++)
  {
    darPaso();
  }


  // Detener pulsos
  digitalWrite(STEP, LOW);
}


// ======================================================
// CICLO AUTOMATICO
// ======================================================
//
// 2 vueltas DERECHA
// 1 vuelta IZQUIERDA
// 2 vueltas DERECHA
// 1 vuelta IZQUIERDA
//
// ======================================================

void cicloAutomatico()
{
  // ----------------------------------------------------
  // 2 VUELTAS DERECHA
  // ----------------------------------------------------

  moverMotor(PASOS_VUELTA * 2, HIGH);


  // ----------------------------------------------------
  // 1 VUELTA IZQUIERDA
  // ----------------------------------------------------

  moverMotor(PASOS_VUELTA, LOW);


  // ----------------------------------------------------
  // 2 VUELTAS DERECHA
  // ----------------------------------------------------

  moverMotor(PASOS_VUELTA * 2, HIGH);


  // ----------------------------------------------------
  // 1 VUELTA IZQUIERDA
  // ----------------------------------------------------

  moverMotor(PASOS_VUELTA, LOW);


  // ----------------------------------------------------
  // FIN DEL CICLO
  // ----------------------------------------------------

  digitalWrite(STEP, LOW);
}


// ======================================================
// CONFIGURACION INICIAL
// ======================================================

void setup()
{
  // ----------------------------------------------------
  // SALIDAS
  // ----------------------------------------------------

  pinMode(DIR, OUTPUT);
  pinMode(STEP, OUTPUT);


  // ----------------------------------------------------
  // ENTRADAS
  // Todos los pulsadores utilizan INPUT_PULLUP
  // Pulsado = LOW
  // ----------------------------------------------------

  pinMode(MANUAL_AUTO, INPUT_PULLUP);

  pinMode(IZQUIERDA, INPUT_PULLUP);
  pinMode(DERECHA, INPUT_PULLUP);

  pinMode(START, INPUT_PULLUP);
  pinMode(REFERENCIAR, INPUT_PULLUP);

  pinMode(FIN_CERO, INPUT_PULLUP);


  // ----------------------------------------------------
  // MOTOR DETENIDO AL ENCENDER
  // ----------------------------------------------------

  digitalWrite(STEP, LOW);
  digitalWrite(DIR, LOW);
}


// ======================================================
// PROGRAMA PRINCIPAL
// ======================================================

void loop()
{
  // ----------------------------------------------------
  // LEER SELECTOR
  //
  // LOW  = MANUAL
  // HIGH = AUTOMATICO
  // ----------------------------------------------------

  bool esManual = (digitalRead(MANUAL_AUTO) == LOW);


  // ====================================================
  // MODO MANUAL
  // ====================================================

  if (esManual)
  {
    // Movimiento libre izquierda/derecha
    modoManual();


    // Al volver a automático
    // será necesario referenciar nuevamente
    estadoAuto = ESPERANDO_REFERENCIA;


    // Guardamos que estamos en manual
    modoAnteriorManual = true;


    return;
  }


  // ====================================================
  // ENTRADA A MODO AUTOMATICO
  // ====================================================

  if (modoAnteriorManual == true)
  {
    // Al entrar a automático
    // obligatoriamente debe referenciar

    estadoAuto = ESPERANDO_REFERENCIA;

    digitalWrite(STEP, LOW);

    modoAnteriorManual = false;
  }


  // ====================================================
  // AUTOMATICO
  // ====================================================


  // ----------------------------------------------------
  // ESTADO 1
  // ESPERANDO REFERENCIA
  // ----------------------------------------------------

  if (estadoAuto == ESPERANDO_REFERENCIA)
  {
    // El pulsador REFERENCIAR inicia la referencia

    if (digitalRead(REFERENCIAR) == LOW)
    {
      // Ejecutar referencia
      referenciar();


      // Referencia terminada
      estadoAuto = REFERENCIADO;


      // Motor detenido
      digitalWrite(STEP, LOW);


      // ------------------------------------------------
      // ESPERAR QUE SE SUELTE REFERENCIAR
      // ------------------------------------------------

      while (digitalRead(REFERENCIAR) == LOW)
      {
        delay(10);
      }
    }
  }


  // ----------------------------------------------------
  // ESTADO 2
  // REFERENCIADO / LISTO
  // ----------------------------------------------------

  else if (estadoAuto == REFERENCIADO)
  {
    // START inicia el ciclo automático

    if (digitalRead(START) == LOW)
    {
      // Cambiar estado
      estadoAuto = EJECUTANDO_CICLO;


      // Ejecutar ciclo
      cicloAutomatico();


      // Al terminar queda listo
      // para otro START
      estadoAuto = REFERENCIADO;


      // ------------------------------------------------
      // ESPERAR QUE SE SUELTE START
      // ------------------------------------------------

      while (digitalRead(START) == LOW)
      {
        delay(10);
      }
    }
  }


  // ----------------------------------------------------
  // ESTADO 3
  // EJECUTANDO CICLO
  // ----------------------------------------------------

  else if (estadoAuto == EJECUTANDO_CICLO)
  {
    // El ciclo ya se ejecuta dentro
    // de cicloAutomatico()
  }
}

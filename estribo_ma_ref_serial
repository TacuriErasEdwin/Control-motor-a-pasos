
// ============================================================
// MAQUETA DE ESTRIBOS - ARDUINO MEGA 2560
// ============================================================
//
// MODOS:
//
// 1. MANUAL
//    - IZQUIERDA
//    - DERECHA
//
// 2. AUTOMATICO
//    - REFERENCIAR
//    - START
//    - 90°
//    - 90°
//    - 90°
//    - 90°
//    - 135°
//
// 3. SERIAL
//    - Preparado para recibir datos posteriormente
//
// IMPORTANTE:
//    Después de terminar un ciclo, START queda bloqueado.
//    Para volver a iniciar se debe REFERENCIAR nuevamente.
//
// ============================================================


// ------------------------------------------------------------
// PINES
// ------------------------------------------------------------

const int DIR = 7;
const int STEP = 3;

const int MANUAL_AUTO = 10;

const int IZQUIERDA = 8;
const int DERECHA = 9;

const int START = 11;
const int REFERENCIAR = 12;

const int FIN_CERO = 22;


// ------------------------------------------------------------
// PARAMETROS DEL MOTOR
// ------------------------------------------------------------

const int PASOS_VUELTA = 200;

// Según la prueba realizada:
// 50 pasos = 90°
const int PASOS_90 = 50;

// 75 pasos = 135°
const int PASOS_135 = 75;

// Tiempo del pulso
const int tiempoPulso = 1500;


// ------------------------------------------------------------
// ESTADO DEL SISTEMA
// ------------------------------------------------------------

// false = no está referenciado
// true  = referencia realizada
bool referenciado = false;


// ------------------------------------------------------------
// VARIABLES PARA SERIAL
// ------------------------------------------------------------

int ancho = 0;
int alto = 0;
int cantidad = 0;

int secuencia = 0;


// ============================================================
// DAR UN PASO
// ============================================================

void darPaso()
{
  digitalWrite(STEP, HIGH);
  delayMicroseconds(tiempoPulso);

  digitalWrite(STEP, LOW);
  delayMicroseconds(tiempoPulso);
}


// ============================================================
// REFERENCIACION
// ============================================================

bool referenciar()
{
  Serial.println();
  Serial.println("================================");
  Serial.println("INICIANDO REFERENCIACION");
  Serial.println("================================");


  // ----------------------------------------------------------
  // Si ya está presionado el final de carrera,
  // primero nos alejamos.
  // ----------------------------------------------------------

  if (digitalRead(FIN_CERO) == LOW)
  {
    Serial.println("Final de carrera activo.");
    Serial.println("Alejando...");

    digitalWrite(DIR, LOW);

    while (digitalRead(FIN_CERO) == LOW)
    {
      darPaso();
    }

    delay(200);
  }


  // ----------------------------------------------------------
  // Buscar posición cero
  // ----------------------------------------------------------

  Serial.println("Buscando posicion cero...");

  digitalWrite(DIR, HIGH);

  while (digitalRead(FIN_CERO) == HIGH)
  {
    darPaso();
  }


  digitalWrite(STEP, LOW);

  delay(200);


  // ----------------------------------------------------------
  // Retroceder 10 pasos
  // ----------------------------------------------------------

  Serial.println("Liberando final de carrera...");

  digitalWrite(DIR, LOW);

  for (int i = 0; i < 10; i++)
  {
    darPaso();
  }

  digitalWrite(STEP, LOW);


  Serial.println("REFERENCIACION TERMINADA.");
  Serial.println("START HABILITADO.");
  Serial.println();

  return true;
}


// ============================================================
// MODO MANUAL
// ============================================================

void modoManual()
{
  // ----------------------------------------------------------
  // IZQUIERDA
  // ----------------------------------------------------------

  if (digitalRead(IZQUIERDA) == LOW)
  {
    digitalWrite(DIR, LOW);

    darPaso();
  }


  // ----------------------------------------------------------
  // DERECHA
  // ----------------------------------------------------------

  else if (digitalRead(DERECHA) == LOW)
  {
    digitalWrite(DIR, HIGH);

    darPaso();
  }


  // ----------------------------------------------------------
  // NINGUN PULSANTE
  // ----------------------------------------------------------

  else
  {
    digitalWrite(STEP, LOW);
  }
}


// ============================================================
// DOBLAR 90 GRADOS
// ============================================================

void doblar90()
{
  Serial.println("DOBLADO: 90 grados");

  digitalWrite(DIR, HIGH);

  for (int i = 0; i < PASOS_90; i++)
  {
    darPaso();
  }

  digitalWrite(STEP, LOW);

  delay(500);
}


// ============================================================
// DOBLAR 135 GRADOS
// ============================================================

void doblar135()
{
  Serial.println("DOBLADO: 135 grados");

  digitalWrite(DIR, HIGH);

  for (int i = 0; i < PASOS_135; i++)
  {
    darPaso();
  }

  digitalWrite(STEP, LOW);

  delay(500);
}


// ============================================================
// CICLO ACTUAL DE PRUEBA
// ============================================================

void fabricarEstribo()
{
  Serial.println();
  Serial.println("================================");
  Serial.println("INICIANDO CICLO");
  Serial.println("================================");


  // DOBLADO 1
  doblar90();


  // DOBLADO 2
  doblar90();


  // DOBLADO 3
  doblar90();


  // DOBLADO 4
  doblar90();


  // DOBLADO 5
  doblar135();


  digitalWrite(STEP, LOW);


  Serial.println();
  Serial.println("================================");
  Serial.println("CICLO TERMINADO");
  Serial.println("START BLOQUEADO");
  Serial.println("REFERENCIAR PARA NUEVO CICLO");
  Serial.println("================================");
  Serial.println();
}


// ============================================================
// MOSTRAR CONFIGURACION
// ============================================================

void mostrarConfiguracion()
{
  Serial.println();
  Serial.println("========== CONFIGURACION ==========");

  Serial.print("Secuencia: ");
  Serial.println(secuencia);

  Serial.print("Ancho: ");
  Serial.print(ancho);
  Serial.println(" mm");

  Serial.print("Alto: ");
  Serial.print(alto);
  Serial.println(" mm");

  Serial.print("Cantidad: ");
  Serial.println(cantidad);

  Serial.println("===================================");
  Serial.println();
}


// ============================================================
// LEER DATOS POR SERIAL
// ============================================================

void leerSerial()
{
  if (Serial.available() > 0)
  {
    char comando = Serial.read();


    // --------------------------------------------------------
    // S = seleccionar secuencia
    // --------------------------------------------------------

    if (comando == '1')
    {
      secuencia = 1;

      Serial.println("Secuencia 1 seleccionada.");
    }


    else if (comando == '2')
    {
      secuencia = 2;

      Serial.println("Secuencia 2 seleccionada.");
    }


    else if (comando == '3')
    {
      secuencia = 3;

      Serial.println("Secuencia 3 seleccionada.");
    }


    // --------------------------------------------------------
    // V = ver configuracion
    // --------------------------------------------------------

    else if (comando == 'V' || comando == 'v')
    {
      mostrarConfiguracion();
    }


    // --------------------------------------------------------
    // R = referenciar
    // --------------------------------------------------------

    else if (comando == 'R' || comando == 'r')
    {
      if (referenciar())
      {
        referenciado = true;
      }
    }


    // --------------------------------------------------------
    // P = mostrar menu
    // --------------------------------------------------------

    else if (comando == 'P' || comando == 'p')
    {
      Serial.println();
      Serial.println("========== MENU ==========");
      Serial.println("1 = Secuencia 1");
      Serial.println("2 = Secuencia 2");
      Serial.println("3 = Secuencia 3");
      Serial.println("V = Ver configuracion");
      Serial.println("R = Referenciar");
      Serial.println("==========================");
      Serial.println();
    }
  }
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
  Serial.begin(9600);


  // Motor
  pinMode(DIR, OUTPUT);
  pinMode(STEP, OUTPUT);


  // Selector
  pinMode(MANUAL_AUTO, INPUT_PULLUP);


  // Pulsantes
  pinMode(IZQUIERDA, INPUT_PULLUP);
  pinMode(DERECHA, INPUT_PULLUP);
  pinMode(START, INPUT_PULLUP);
  pinMode(REFERENCIAR, INPUT_PULLUP);


  // Final de carrera
  pinMode(FIN_CERO, INPUT_PULLUP);


  // Motor detenido
  digitalWrite(STEP, LOW);


  Serial.println();
  Serial.println("======================================");
  Serial.println("     MAQUINA DE ESTRIBOS");
  Serial.println("       ARDUINO MEGA 2560");
  Serial.println("======================================");
  Serial.println();

  Serial.println("Sistema SIN REFERENCIAR.");
  Serial.println("Pulse REFERENCIAR.");
  Serial.println("Escriba P para ver el menu.");
  Serial.println();
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
  // ----------------------------------------------------------
  // Leer Serial
  // ----------------------------------------------------------

  leerSerial();


  // ==========================================================
  // MODO MANUAL
  // ==========================================================

  if (digitalRead(MANUAL_AUTO) == LOW)
  {
    modoManual();

    return;
  }


  // ==========================================================
  // MODO AUTOMATICO
  // ==========================================================


  // ----------------------------------------------------------
  // REFERENCIAR CON PULSANTE
  // ----------------------------------------------------------

  if (digitalRead(REFERENCIAR) == LOW)
  {
    delay(50);

    while (digitalRead(REFERENCIAR) == LOW)
    {
      delay(10);
    }

    if (referenciar())
    {
      referenciado = true;
    }

    return;
  }


  // ----------------------------------------------------------
  // START
  // ----------------------------------------------------------

  if (digitalRead(START) == LOW && referenciado == true)
  {
    delay(50);

    // Esperar que se suelte START
    while (digitalRead(START) == LOW)
    {
      delay(10);
    }


    // Ejecutar ciclo
    fabricarEstribo();


    // --------------------------------------------------------
    // MUY IMPORTANTE:
    //
    // Al terminar el ciclo la posición cambió.
    //
    // Por eso ya NO consideramos que estamos referenciados.
    // --------------------------------------------------------

    referenciado = false;


    Serial.println("START BLOQUEADO.");
    Serial.println("Debe REFERENCIAR nuevamente.");

    delay(300);

    return;
  }


  // ----------------------------------------------------------
  // Si no está referenciado, START no funciona
  // ----------------------------------------------------------

  if (referenciado == false)
  {
    digitalWrite(STEP, LOW);
  }
}

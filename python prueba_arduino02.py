
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time

BAUDIOS = 9600
MAX_PASOS = 2000

arduino = None
referenciado = False
ocupado = False
secuencia = []


def estado(texto):
    ventana.after(0, estado_var.set, texto)


def conectar():
    global arduino, referenciado

    if arduino is not None and arduino.is_open:
        messagebox.showinfo("USB", "Arduino ya está conectado.")
        return

    puerto = puerto_var.get().strip()

    try:
        arduino = serial.Serial(
            puerto,
            BAUDIOS,
            timeout=1,
            write_timeout=3
        )

        # El Mega suele reiniciarse al abrir el puerto.
        time.sleep(2)
        arduino.reset_input_buffer()

        referenciado = False
        boton_home.config(state="normal")
        actualizar_botones()

        estado_var.set(f"Conectado a {puerto}. Debes referenciar.")
        messagebox.showinfo(
            "Conexión correcta",
            "Arduino conectado. Pulsa REFERENCIAR."
        )

    except Exception as error:
        arduino = None
        messagebox.showerror("Error USB", str(error))


def leer_hasta(respuestas_validas, timeout):
    inicio = time.monotonic()
    mensajes = []

    while time.monotonic() - inicio < timeout:
        if arduino is None or not arduino.is_open:
            raise RuntimeError("Puerto USB desconectado.")

        linea = arduino.readline().decode(
            "utf-8", errors="replace"
        ).strip()

        if not linea:
            continue

        mensajes.append(linea)
        estado("Arduino: " + linea)

        # Guardar en la consola de Python cada mensaje recibido.
        print("[ARDUINO]", linea)

        if linea.startswith("ERROR:"):
            detalle = "\n".join(mensajes)
            raise RuntimeError(detalle)

        if linea in respuestas_validas:
            return linea

    detalle = "\n".join(mensajes)

    raise TimeoutError(
        "Arduino no respondió a tiempo.\n"
        "Mensajes recibidos:\n" +
        (detalle if detalle else "(ninguno)")
    )



def referenciar():
    global ocupado, referenciado

    if arduino is None or not arduino.is_open:
        messagebox.showwarning(
            "Sin conexión", "Primero conecta el Arduino."
        )
        return

    if ocupado:
        return

    ocupado = True
    referenciado = False
    actualizar_botones()

    threading.Thread(
        target=ejecutar_home,
        daemon=True
    ).start()


def ejecutar_home():
    global ocupado, referenciado

    try:
        arduino.write(b"HOME\n")
        arduino.flush()

        estado("Buscando posición cero...")

        respuesta = leer_hasta({"ZERO_OK"}, 40)

        if respuesta == "ZERO_OK":
            referenciado = True
            estado("Cero reconocido. Listo para secuencias.")

    except Exception as error:
        referenciado = False
        estado("Error de referenciación: " + str(error))
        ventana.after(
            0,
            lambda mensaje=str(error): messagebox.showerror(
                "Referenciación fallida", mensaje
            )
        )

    finally:
        ocupado = False
        ventana.after(0, actualizar_botones)


def agregar():
    direccion = direccion_var.get()

    try:
        pasos = int(pasos_var.get())
    except ValueError:
        messagebox.showerror("Error", "Ingresa los pasos.")
        return

    if pasos < 1 or pasos > MAX_PASOS:
        messagebox.showwarning(
            "Límite",
            f"Usa entre 1 y {MAX_PASOS} pasos."
        )
        return

    secuencia.append((direccion, pasos))
    refrescar_tabla()


def refrescar_tabla():
    for item in tabla.get_children():
        tabla.delete(item)

    for numero, (direccion, pasos) in enumerate(
        secuencia, start=1
    ):
        nombre = "Derecha" if direccion == "R" else "Izquierda"
        tabla.insert(
            "", "end",
            values=(numero, nombre, pasos)
        )


def eliminar():
    seleccion = tabla.selection()

    indices = sorted(
        [tabla.index(item) for item in seleccion],
        reverse=True
    )

    for indice in indices:
        del secuencia[indice]

    refrescar_tabla()


def limpiar():
    if ocupado:
        return

    secuencia.clear()
    refrescar_tabla()


def enviar_secuencia():
    global ocupado

    if arduino is None or not arduino.is_open:
        messagebox.showwarning(
            "Sin conexión", "Conecta primero el Arduino."
        )
        return

    if not referenciado:
        messagebox.showwarning(
            "Sin referencia",
            "Pulsa REFERENCIAR antes de mover el motor."
        )
        return

    if ocupado:
        return

    if not secuencia:
        messagebox.showwarning(
            "Secuencia vacía",
            "Agrega movimientos antes de enviar."
        )
        return

    movimientos = list(secuencia)
    ocupado = True
    actualizar_botones()

    threading.Thread(
        target=ejecutar_secuencia,
        args=(movimientos,),
        daemon=True
    ).start()


def ejecutar_secuencia(movimientos):
    global ocupado, referenciado

    try:
        for numero, (direccion, pasos) in enumerate(
            movimientos, start=1
        ):
            comando = f"{direccion},{pasos}"

            arduino.write((comando + "\n").encode("utf-8"))
            arduino.flush()

            estado(
                f"Movimiento {numero}/{len(movimientos)}: {comando}"
            )

            respuesta = leer_hasta(
                {f"OK {comando}"},
                15
            )

            if respuesta != f"OK {comando}":
                raise RuntimeError("Movimiento no confirmado.")

        # Termina la secuencia y exige referenciar otra vez.
        arduino.write(b"END\n")
        arduino.flush()

        leer_hasta({"SEQUENCE_DONE"}, 5)
        referenciado = False

        estado("Secuencia terminada. Referencia requerida.")

        ventana.after(
            0,
            lambda: messagebox.showinfo(
                "Secuencia finalizada",
                "Todos los movimientos fueron confirmados.\n"
                "Para otro ciclo, vuelve a referenciar."
            )
        )

    except Exception as error:
        referenciado = False
        estado("Error: " + str(error))

        ventana.after(
            0,
            lambda mensaje=str(error): messagebox.showerror(
                "Error de movimiento",
                mensaje + "\nVerifica la máquina antes de continuar."
            )
        )

    finally:
        ocupado = False
        ventana.after(0, actualizar_botones)


def actualizar_botones():
    conectado = arduino is not None and arduino.is_open

    boton_conectar.config(
        state="disabled" if conectado else "normal"
    )
    boton_home.config(
        state="normal" if conectado and not ocupado else "disabled"
    )
    boton_enviar.config(
        state="normal"
        if conectado and referenciado and not ocupado
        else "disabled"
    )
    boton_agregar.config(
        state="normal" if not ocupado else "disabled"
    )
    boton_eliminar.config(
        state="normal" if not ocupado else "disabled"
    )
    boton_limpiar.config(
        state="normal" if not ocupado else "disabled"
    )


def cerrar():
    global arduino

    if ocupado:
        messagebox.showwarning(
            "Ocupado",
            "Espera a que termine la operación antes de cerrar."
        )
        return

    if arduino is not None and arduino.is_open:
        arduino.close()

    ventana.destroy()


# Interfaz gráfica
ventana = tk.Tk()
ventana.title("Control de motor - Arduino Mega")
ventana.geometry("650x570")

marco = ttk.Frame(ventana, padding=15)
marco.pack(fill="both", expand=True)

ttk.Label(
    marco,
    text="CONTROL DEL MOTOR PASO A PASO",
    font=("Arial", 15, "bold")
).pack(anchor="w", pady=(0, 12))

fila_usb = ttk.Frame(marco)
fila_usb.pack(fill="x", pady=5)

ttk.Label(fila_usb, text="Puerto COM:").pack(side="left")

puerto_var = tk.StringVar(value="COM8")
ttk.Entry(
    fila_usb, textvariable=puerto_var, width=10
).pack(side="left", padx=8)

boton_conectar = ttk.Button(
    fila_usb, text="CONECTAR USB", command=conectar
)
boton_conectar.pack(side="left", padx=5)

boton_home = ttk.Button(
    fila_usb,
    text="REFERENCIAR CERO",
    command=referenciar,
    state="disabled"
)
boton_home.pack(side="left", padx=5)

grupo = ttk.LabelFrame(
    marco, text="Agregar movimiento", padding=10
)
grupo.pack(fill="x", pady=10)

ttk.Label(grupo, text="Dirección:").grid(
    row=0, column=0, padx=5, pady=5
)

direccion_var = tk.StringVar(value="R")
ttk.Combobox(
    grupo,
    textvariable=direccion_var,
    values=("R", "L"),
    state="readonly",
    width=10
).grid(row=0, column=1, padx=5, pady=5)

ttk.Label(
    grupo, text="R = Derecha / L = Izquierda"
).grid(row=0, column=2, padx=5)

ttk.Label(grupo, text="Pasos:").grid(
    row=1, column=0, padx=5, pady=5
)

pasos_var = tk.StringVar(value="200")
ttk.Entry(
    grupo, textvariable=pasos_var, width=12
).grid(row=1, column=1, padx=5, pady=5)

boton_agregar = ttk.Button(
    grupo, text="Agregar", command=agregar
)
boton_agregar.grid(row=1, column=2, padx=5, pady=5)

ttk.Label(marco, text="Secuencia de movimientos:").pack(
    anchor="w", pady=(5, 3)
)

tabla = ttk.Treeview(
    marco,
    columns=("n", "direccion", "pasos"),
    show="headings",
    height=9
)
tabla.heading("n", text="N.º")
tabla.heading("direccion", text="Dirección")
tabla.heading("pasos", text="Pasos")
tabla.column("n", width=50, anchor="center")
tabla.column("direccion", width=200, anchor="center")
tabla.column("pasos", width=100, anchor="center")
tabla.pack(fill="both", expand=True)

fila = ttk.Frame(marco)
fila.pack(fill="x", pady=10)

boton_eliminar = ttk.Button(
    fila, text="Eliminar", command=eliminar
)
boton_eliminar.pack(side="left", padx=3)

boton_limpiar = ttk.Button(
    fila, text="Limpiar", command=limpiar
)
boton_limpiar.pack(side="left", padx=3)

boton_enviar = ttk.Button(
    fila,
    text="ENVIAR SECUENCIA",
    command=enviar_secuencia,
    state="disabled"
)
boton_enviar.pack(side="right", padx=3)

estado_var = tk.StringVar(value="Desconectado")
ttk.Label(
    marco, textvariable=estado_var, wraplength=600
).pack(anchor="w", pady=5)

ventana.protocol("WM_DELETE_WINDOW", cerrar)
ventana.mainloop()

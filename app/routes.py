from flask import render_template, request, jsonify
import subprocess
import threading
import time
from app import app  # Importamos la app para definir las rutas

# Ruta para mostrar el formulario o página inicial
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Ruta para manejar los comandos enviados desde el cliente
@app.route("/comando", methods=["POST"])
def ejecutar_comando():
    data = request.get_json()
    comando = data.get("comando")
    link = data.get("link")
    try:
        time_limit = int(data.get("temporizador", 30))  # Convertir a entero
    except ValueError:
        return jsonify({"error": "El temporizador debe ser un número válido."}), 400

    entry_time_limit = data.get("entry_time_limit")
    if entry_time_limit:
        try:
            entry_time_limit = int(entry_time_limit)  # Convertir a entero si se proporciona
        except ValueError:
            return jsonify({"error": "El tiempo de entrada debe ser un número válido."}), 400

    if not link:
        return jsonify({"error": "El enlace es obligatorio"}), 400

    if comando == "youtube":
        return open_video_on_devices(link, time_limit)
    elif comando == "enlace":
        selected_option = data.get("option", "default")
        return open_link_on_devices(link, selected_option, time_limit, entry_time_limit)
    else:
        return jsonify({"error": "Comando no reconocido"}), 400

# Función para abrir enlaces generales y establecer el temporizador
def open_link_on_devices(link, selected_option, time_limit, entry_time_limit=None):
    try:
        devices_output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        devices = [line.split("\t")[0] for line in devices_output.splitlines() if "device" in line]

        if not devices:
            return {"error": "No se encontraron dispositivos conectados."}, 400

        for device in devices:
            if selected_option == "default":
                subprocess.run(["adb", "-s", device, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", link])
            elif selected_option == "chrome":
                subprocess.run([
                    "adb", "-s", device, "shell", "am", "start", "-a", "android.intent.action.VIEW",
                    "-d", link, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"
                ])

        # Usar entry_time_limit si está definido, de lo contrario usar time_limit
        final_time_limit = int(entry_time_limit) if entry_time_limit else time_limit

        threading.Thread(target=start_timer_and_go_home, args=(final_time_limit, devices)).start()

        return {"message": f"Enlace abierto en {len(devices)} dispositivos y el temporizador de {final_time_limit} segundos ha comenzado."}, 200
    except subprocess.CalledProcessError as e:
        return {"error": f"Hubo un problema ejecutando ADB: {e}"}, 500
    except Exception as e:
        return {"error": f"Ocurrió un error inesperado: {e}"}, 500

# Función para abrir enlaces de YouTube y establecer el temporizador
def open_video_on_devices(link, time_limit):
    if not link.startswith("https://www.youtube.com/watch"):
        return {"error": "Por favor ingresa un enlace válido de YouTube."}, 400

    try:
        devices_output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        devices = [line.split("\t")[0] for line in devices_output.splitlines() if "device" in line]

        if not devices:
            return {"error": "No se encontraron dispositivos conectados."}, 400

        for device in devices:
            subprocess.run([
                "adb", "-s", device, "shell", "am", "start", "-a", "android.intent.action.VIEW",
                "-d", link, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"
            ])
            start_page_refresh(device)

        threading.Thread(target=start_timer_and_go_home, args=(time_limit, devices)).start()

        return {"message": f"Video de YouTube abierto en {len(devices)} dispositivos y el temporizador ha comenzado."}, 200
    except subprocess.CalledProcessError as e:
        return {"error": f"Hubo un problema ejecutando ADB: {e}"}, 500
    except Exception as e:
        return {"error": f"Ocurrió un error inesperado: {e}"}, 500

# Variable global para controlar los hilos de refresco
refresh_stop_events = {}

# Función para refrescar la página cada 20 segundos
def start_page_refresh(device):
    stop_event = threading.Event()
    refresh_stop_events[device] = stop_event  # Asociar el evento al dispositivo

    def refresh_page():
        while not stop_event.is_set():  # Revisar si se debe detener
            try:
                subprocess.run(["adb", "-s", device, "shell", "input", "keyevent", "KEYCODE_F5"])
                time.sleep(20)  # Refrescar cada 20 segundos
            except Exception as e:
                print(f"Error al refrescar la página en el dispositivo {device}: {e}")

    refresh_thread = threading.Thread(target=refresh_page, daemon=True)
    refresh_thread.start()

# Función para manejar el temporizador y detener el refresco
def start_timer_and_go_home(time_limit, devices):
    print(f"Iniciando temporizador de {time_limit} segundos.")
    time.sleep(time_limit)

    for device in devices:
        try:
            # Detener el refresco de página para el dispositivo
            if device in refresh_stop_events:
                refresh_stop_events[device].set()  # Detener el bucle del refresco
                del refresh_stop_events[device]   # Limpiar el evento de la lista

            # Enviar el dispositivo a la pantalla principal
            subprocess.run(["adb", "-s", device, "shell", "input", "keyevent", "KEYCODE_HOME"])
            print(f"Dispositivo {device} enviado a la pantalla de inicio.")
        except Exception as e:
            print(f"Error al intentar enviar {device} a inicio: {e}")

    print(f"Temporizador de {time_limit} segundos completado.")

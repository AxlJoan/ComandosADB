import os
from app import app  # Importa la instancia de Flask desde app/__init__.py
from flask import request, jsonify, render_template
import subprocess

# Ruta para manejar los comandos ADB
@app.route('/comando', methods=['POST'])
def send_command():
    try:
        # Leer datos enviados desde el cliente
        data = request.json
        link = data.get("link")
        option = data.get("option", "default")
        time_limit = data.get("time_limit", 30)

        if not link:
            return jsonify({"error": "No se proporcionó un enlace"}), 400

        # Obtener la lista de dispositivos conectados con ADB
        devices_output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
        devices = [line.split("\t")[0] for line in devices_output.splitlines() if "device" in line]

        if not devices:
            return jsonify({"error": "No hay dispositivos conectados"}), 400

        # Ejecutar comandos en cada dispositivo
        for device in devices:
            if option == "default":
                subprocess.run(["adb", "-s", device, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", link])
            elif option == "chrome":
                subprocess.run([
                    "adb", "-s", device, "shell", "am", "start", "-a", "android.intent.action.VIEW",
                    "-d", link, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"
                ])

        return jsonify({"message": f"Enlace enviado a {len(devices)} dispositivos.", "devices": devices}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error ejecutando ADB: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Usar el puerto de entorno si está disponible

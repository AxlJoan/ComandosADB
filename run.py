import os
from flask import Flask, request, jsonify, render_template
import requests  # Para enviar solicitudes HTTP a los clientes

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app', 'templates'))

@app.route('/send_command', methods=['POST'])
def send_command():
    try:
        # Leer datos enviados desde el cliente web
        data = request.json
        client_address = data.get("client_address")  # Dirección IP del cliente
        link = data.get("link")
        option = data.get("option", "default")
        time_limit = data.get("time_limit", 30)

        if not client_address:
            return jsonify({"error": "No se proporcionó la dirección del cliente"}), 400

        if not link:
            return jsonify({"error": "No se proporcionó un enlace"}), 400

        # Crear el payload para enviar al cliente
        payload = {
            "link": link,
            "option": option,
            "time_limit": time_limit
        }

        # Enviar la solicitud al cliente
        client_url = f"http://{client_address}:8001/execute_adb_command"  # Cliente escucha en el puerto 8001
        response = requests.post(client_url, json=payload)

        if response.status_code == 200:
            return jsonify({"message": f"Comando enviado al cliente {client_address}.", "response": response.json()}), 200
        else:
            return jsonify({"error": f"Error desde el cliente: {response.text}"}), response.status_code

    except requests.RequestException as e:
        return jsonify({"error": f"Error comunicándose con el cliente: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Usar el puerto de entorno si está disponible

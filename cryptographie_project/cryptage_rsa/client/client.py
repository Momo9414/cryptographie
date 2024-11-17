from flask import Flask, render_template, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import requests

app = Flask(__name__)

# Route de base pour afficher l'interface
@app.route("/")
def index():
    return render_template("client.html")

# Route pour envoyer un message au serveur
@app.route("/send", methods=["POST"])
def send_message():
    message = request.form["message"]

    # Récupérer la clé publique du serveur
    response = requests.get("http://127.0.0.1:5000/public_key")
    server_public_key = response.json()["public_key"]

    # Chiffrement du message
    key = RSA.import_key(server_public_key)
    cipher = PKCS1_OAEP.new(key)
    encrypted_message = base64.b64encode(cipher.encrypt(message.encode())).decode()

    # Envoyer le message chiffré au serveur
    payload = {"encrypted_message": encrypted_message}
    response = requests.post("http://127.0.0.1:5000/decrypt", json=payload)

    if response.status_code == 200:
        return jsonify({"status": "success", "encrypted_message": encrypted_message})
    else:
        return jsonify({"status": "error", "message": "Échec de l'envoi au serveur."})

if __name__ == "__main__":
    app.run(port=5001, debug=True)

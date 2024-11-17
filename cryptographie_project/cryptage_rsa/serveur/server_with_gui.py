from flask import Flask, render_template, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

app = Flask(__name__)

# Génération des clés RSA
key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

# Stocker les messages reçus et déchiffrés
messages = []

@app.route("/")
def index():
    return render_template("index.html", messages=messages)

# Route pour obtenir la clé publique
@app.route("/public_key", methods=["GET"])
def get_public_key():
    return jsonify({"public_key": public_key.export_key().decode()})

# Route pour déchiffrer un message
@app.route("/decrypt", methods=["POST"])
def decrypt_message():
    data = request.get_json()
    encrypted_message = base64.b64decode(data["encrypted_message"])

    # Déchiffrer le message
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message).decode()

    # Ajouter aux messages
    messages.append({"encrypted": data["encrypted_message"], "decrypted": decrypted_message})

    return jsonify({"decrypted_message": decrypted_message})

if __name__ == "__main__":
    app.run(debug=True)

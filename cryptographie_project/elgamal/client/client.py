from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("client.html")

@app.route("/send", methods=["POST"])
def send_message():
    try:
        message = request.form["message"]
        
        # Récupération de la clé publique du serveur
        response = requests.get("http://127.0.0.1:5000/public_key")
        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Impossible de récupérer la clé publique"
            })
        
        public_key = response.json()["public_key"]
        
        # Extraction des composants de la clé publique
        p = public_key['p']
        g = public_key['g']
        h = public_key['h']
        
        # Conversion du message en nombre
        m = int.from_bytes(message.encode(), byteorder='big')
        
        # Chiffrement
        k = random.randint(2, p-2)
        c1 = pow(g, k, p)  # c1 = g^k mod p
        s = pow(h, k, p)   # s = h^k mod p
        c2 = (m * s) % p   # c2 = m * s mod p
        
        # Envoi du message chiffré au serveur
        payload = {"c1": str(c1), "c2": str(c2)}
        response = requests.post("http://127.0.0.1:5000/decrypt", json=payload)
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "encrypted_message": f"c1: {c1}, c2: {c2}",
                "decrypted_message": response.json()["decrypted_message"]
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Échec de l'envoi au serveur."
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
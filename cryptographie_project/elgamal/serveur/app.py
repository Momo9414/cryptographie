import random
import math
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def miller_rabin(n, k=5):
    """Test de primalité de Miller-Rabin plus efficace"""
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False

    # Écrire n-1 comme 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Témoin
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits: int) -> int:
    """Génère un grand nombre premier avec vérification optimisée"""
    # Liste des petits nombres premiers pour pré-vérification
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    while True:
        # Générer un nombre impair dans la plage souhaitée
        n = random.getrandbits(bits) | 1
        
        # Vérification rapide avec les petits nombres premiers
        if any(n % p == 0 for p in small_primes if n != p):
            continue
            
        # Test de Miller-Rabin
        if miller_rabin(n):
            return n

def find_primitive_root(p: int) -> int:
    """Trouve une racine primitive modulo p de manière optimisée"""
    if not miller_rabin(p):
        raise ValueError("Le nombre doit être premier")
    
    # Factorisation optimisée de p-1
    phi = p - 1
    factors = set()
    
    # Vérifier les facteurs 2
    while phi % 2 == 0:
        factors.add(2)
        phi //= 2
    
    # Vérifier les facteurs impairs
    for i in range(3, int(math.sqrt(phi)) + 1, 2):
        while phi % i == 0:
            factors.add(i)
            phi //= i
    if phi > 1:
        factors.add(phi)

    # Recherche d'une racine primitive
    for g in range(2, p):
        if all(pow(g, (p-1)//f, p) != 1 for f in factors):
            return g

def generate_keypair(bits: int = 32):  # Réduit à 32 bits pour un test plus rapide
    """Génère une paire de clés ElGamal avec une taille de clé réduite"""
    p = generate_large_prime(bits)
    g = find_primitive_root(p)
    x = random.randint(2, p-2)
    h = pow(g, x, p)
    
    public_key = {'p': p, 'g': g, 'h': h}
    private_key = {'x': x, 'p': p}
    
    return public_key, private_key

# Variables globales pour stocker les clés et messages
try:
    PUBLIC_KEY, PRIVATE_KEY = generate_keypair()
    print("Clés générées avec succès!")
    print(f"Clé publique: {PUBLIC_KEY}")
except Exception as e:
    print(f"Erreur lors de la génération des clés: {e}")
    # Valeurs de secours pour le test
    PUBLIC_KEY = {'p': 2357, 'g': 2, 'h': 1751}
    PRIVATE_KEY = {'x': 1234, 'p': 2357}

messages = []

@app.route("/")
def index():
    return render_template("server.html", messages=messages)

@app.route("/public_key", methods=["GET"])
def get_public_key():
    return jsonify({"public_key": PUBLIC_KEY})

@app.route("/decrypt", methods=["POST"])
def decrypt_message():
    try:
        data = request.get_json()
        c1 = int(data["c1"])
        c2 = int(data["c2"])
        
        x = PRIVATE_KEY['x']
        p = PRIVATE_KEY['p']
        
        # Déchiffrement
        s = pow(c1, x, p)
        s_inv = pow(s, p-2, p)
        m = (c2 * s_inv) % p
        
        try:
            decrypted_message = m.to_bytes((m.bit_length() + 7) // 8, byteorder='big').decode()
        except:
            decrypted_message = str(m)
        
        messages.append({
            "encrypted": f"c1: {c1}, c2: {c2}",
            "decrypted": decrypted_message
        })
        
        return jsonify({
            "status": "success",
            "decrypted_message": decrypted_message
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
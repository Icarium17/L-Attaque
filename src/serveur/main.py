from flask import Flask, request, jsonify

app = Flask(__name__)

# Service pour l'inscription et la connexion
@app.route('/sign', methods=['POST'])
def handle_sign():
    return jsonify({"status": "success", "message": "Enregistre!"})

# Service pour les mouvements des pieces
@app.route('/move', methods=['POST'])

def handle_valid_move():
    data = request.get_json()
    pion = data.get('pion')
    col = data.get('colonne')
    lig = data.get('ligne')
    destination = data.get('destination')

    print(f"Mouvement reçu : {pion} vers {col}{lig}")

    return jsonify({
        "status": "success",
        "message_serveur": f"Le deplacement est valide pour : {pion}",
        "data_recue": data
    })
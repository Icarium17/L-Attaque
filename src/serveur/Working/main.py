from flask import Flask, request, jsonify
from lobbyManager import LobbyManager

app = Flask(__name__)
lobby = LobbyManager()

# Test connexion Eddy (Inscription)
@app.route('/signup', methods=['POST'])
def handle_signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logged_in = lobby.execute_action("signup", (username, password))

    return jsonify({
        "status": logged_in[0],
        "key" : logged_in[1],
        "username": username
    })

@app.route('/signin', methods=['POST'])
def handle_signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logged_in = lobby.execute_action("signin", (username, password))

    return jsonify({
        "status": logged_in[0],
        "key": logged_in[1],
        "username": username
    })

@app.route('/signout', methods=['POST'])
def handle_signout():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    return jsonify({
        "status": "success",
        "key": "thekeyhere",
        "username": username
    })

@app.route('/')
def index():
    return "Serveur Python Flask OK"

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
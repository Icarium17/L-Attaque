"""Server routes and expected data for this Flask app.

Routes (endpoint -> HTTP method):

- POST /signup
    - Payload: {"username": username, "password": password}
    - Response: {"status": ..., "key": session key, "username": username}

- POST /signin
    - Payload: {"username": username, "password": password}
    - Response: {"status": ..., "key": session key, "username": username}

- POST /signout
    - Payload: {"key": session_key}
    - Response: {"status": ...}

- GET /
    - Payload: none
    - Response: "Serveur Python Flask OK"

- POST /get_all_users
    - Payload: none
    - Response: {"users" : list of existing users and their statuses}

- POST /delete_user
    - Payload: {"user_id": int}
    - Response: {"deleted": boolean}

- POST /start_game
    - Payload: {"key": session_key}
    - Response: {"status": ..., "opponent_username": opponent's username}

- POST /set_pieces
    - Payload: {"key": session_key, "pieces": list or dict of pieces and their positions}
    - Response: {"status": ..., "player_status": player's new status}

- POST /make_move
    - Payload: {"user_key": session_key, "colonne": original column, "ligne": original row,
                             "destination_colonne": destination column, "destination_ligne": destination row}
    - Response: {"status": ...}

- POST /get_status
    - Payload: {"key": session_key}
    - Response: {"status": ...}

Notes:
 - All endpoints expect JSON payloads unless noted otherwise.
 - Exact response contents and types are determined by LobbyManager and DAO implementations.
"""

from flask import Flask, request, jsonify
from lobbyManager import LobbyManager

app = Flask(__name__)
lobby = LobbyManager()


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
    key = data.get('key')

    result = lobby.execute_action("signout", (key,))
    return jsonify({
        "status" : result
    })

@app.route('/')
def index():
    return "Serveur Python Flask OK"

@app.route('/get_all_users', methods=['POST'])
def handle_get_all_users():
    users = lobby.execute_action("getActivePlayers", ())

    return jsonify({"users": users})

@app.route('/delete_user', methods=['POST'])
def handle_delete_user():
    data = request.get_json()
    user_id = data.get('user_id')
    result = lobby.DAOUsers.delete_user(user_id)
    return jsonify({"deleted": result})

@app.route('/start_game', methods=["POST"])
def handle_start_game():
    data = request.get_json()
    my_key = data.get('key')
    result = lobby.execute_action("startGame", (my_key,))

    return jsonify({   
        "status": result[0],
        "opponent_username": result[1]
    })

@app.route('set_pieces', methods=['POST'])
def handle_set_pieces():
    data = request.get_json()
    my_key = data.get('key')
    my_pieces = data.get('pieces')
    result = lobby.execute_action("setPieces", (my_key, my_pieces))

    return jsonify({
        "status": result[0],
        "player_status": result[1]
    })

 
@app.route('/make_move', methods=['POST'])
def handle_valid_move():
    data = request.get_json()
    user_key = data.get('user_key')
    x_0 = data.get('colonne')
    y_0 = data.get('ligne')
    x_1 = data.get('destination_colonne')
    y_1 = data.get('destination_ligne')

    result = lobby.execute_action("move", (user_key, x_0, y_0, x_1, y_1))

    return jsonify({
        "status": result[1]
    })

##Pour avoir le statut du joueur
@app.route('/get_status', methods=['POST'])
def handle_get_status():
    data = request.get_json()
    key = data.get('key')

    result = lobby.execute("getStatus", (key,))
    return jsonify({
        "status" : result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

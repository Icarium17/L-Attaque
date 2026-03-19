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
    users = lobby.DAOUsers.get_all_users()
    active_usernames = [user.username for user in lobby.active_users.values()]

    for user in users:
        user["connected"] = user["username"] in active_usernames

    return jsonify({"users": users})

@app.route('/delete_user', methods=['POST'])
def handle_delete_user():
    data = request.get_json()
    user_id = data.get('user_id')
    result = lobby.DAOUsers.delete_user(user_id)
    return jsonify({"deleted": result})
 
@app.route('/make_move', methods=['POST'])
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
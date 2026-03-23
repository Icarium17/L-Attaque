from flask import Flask, request, jsonify
from lobbyManager import LobbyManager

app = Flask(__name__)
lobby = LobbyManager()

@app.route('/signup', methods=['POST'])
def handle_signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    status, key = lobby.execute_action("signup", (username, password))

    return jsonify({
        "status": status,
        "key" : key,
        "username": username
    })

@app.route('/signin', methods=['POST'])
def handle_signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    status, key = lobby.execute_action("signin", (username, password))

    return jsonify({
        "status": status,
        "key": key,
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
    
    data = request.get_json()
    my_key = data.get('key')
    users = lobby.execute_action("getActivePlayers", (my_key,))
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
    user_key = data.get('user_key')
    x_0 = data.get('colonne')
    y_0 = data.get('ligne')
    x_1 = data.get('destination_colonne')
    y_1 = data.get('destination_ligne')

    result = lobby.execute_action("move", (user_key, x_0, y_0, x_1, y_1))

    return jsonify({
        "status": result[0],
        "message": result[1]
    })

    # print(f"Mouvement reçu : {pion} vers {col}{lig}")

    # return jsonify({
    #     "status": "success",
    #     "message_serveur": f"Le deplacement est valide pour : {pion}",
    #     "data_recue": data
    # })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
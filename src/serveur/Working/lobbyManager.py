import time

from GAME.move import Move
from gameManager import GameManager
from USERS.player import Player
from USERS.aiPlayer import AIPlayer
from DAO.DAOUsers import DAOUsers
from USERS.user import User
from GAME.piece import Piece, PieceType

class LobbyManager():
    def __init__(self):
        self.games = {} ## dict, pour chaque player_id, donne la game. donc 2 entrées pour chaque jeu
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []

        self.actions = {
            "signup" : self.create_profile,
            "signin" : self.login,
            "signout" : self.logout,
            "deleteProfile" : self.logout,
            "modifyProfile" : self.modify_profile,
            "startGame" : self.start_game,
            "getActivePlayers" : self.get_active_players,
            "startGameSpecificPlayer" : self.start_game_specific_player,
            "challenge" : self.challenge,
            "answerChallenge" : self.answer_challenge,
            "restartGame" : self.restart_game,
            "surrender" : self.surrender,
            "save" : self.save,
            "set_pieces" : self.set_pieces,
            "move" : self.move,
            "chat" : self.chat,
            "leaderboard" : self.leaderboard            
        }

        self.DAOUsers = DAOUsers()
    
    def execute_action(self, player_action, *args):
        action = self.actions.get(player_action)
        if action:
            return action(*args)

    ## Authentication
    def create_profile(self, args) -> str:
        print("create_profile called")

        username, password = args ## TODO : modifier pour que ça prenne en compte les autres paramètres (langue, etc)
        user_created, user_id, session_key, score = self.DAOUsers.create_user(
            username, password, 'French', 0, 'User', True, True
        )

        if user_created:
            user = User(user_id, session_key, username, score, "IDLE")
            self.active_users[user.key] = user
            return "USER_CREATED", session_key
        return "ERROR", -1

    def login(self, args):
        print("login called")
        username, password = args
        user_connected, user_id, session_key, score = self.DAOUsers.connect(
            username, password
            )
        
        if user_connected:
            user = User(user_id, session_key, username, score, "IDLE")
            self.active_users[user.key] = user
            return "USER_CONNECTED", session_key

        return "INVALID_USERNAME_PASSWORD", -1

    def logout(self, args):
        print("logout called")
        (session_id,) = args
        if session_id in self.active_users:
            del self.active_users[session_id]
            return "USER_DISCONNECTED"
        return "INVALID_KEY"
        

    def delete_profile(self, args):
        print("delete_profile called")
        (my_key,) = args

        return self.DAOUsers.delete_user(my_key)
    
    def modify_profile(self):
        print("modify_profile called")


    ## Start/End Game
    def start_game(self, args): ## tout à changer une fois que les joueurs pourront se connecter et loop awaiting player
        print("start_game called")
        my_key, their_key = args
        player1 = Player(self.active_users[my_key], 0)

        player2 = Player(self.active_users[their_key], 1)

        game = GameManager(self, [player1, player2])
        self.games[my_key] = game
        self.games[their_key] = game

        return "Le jeu est commencé"

    def get_active_players(self):
        print("get_active_players called")
        users = self.DAOUsers.get_all_users()
        active_usernames = [user.username for user in self.active_users.values()]

        for user in users:
            user["connected"] = user["username"] in active_usernames
        
        return users
    
    def start_game_specific_player(self):
        print("start_game_specific_player called")

    def challenge(self):
        print("challenge called")

    def answer_challenge(self):
        print("answer_challenge called")

    def restart_game(self):
        print("restart_game called")

    def surrender(self):
        print("surrender called")

    def save(self):
        print("save called")


    ## Play Game
    def set_pieces(self, args):
        print("set_pieces called")
        my_key, pieces = args
        print(pieces)

        game = self.games[my_key] ##this might be a problem with how start_game works, but itll change so its fine for now
        valid = game.check_valid_setup(my_key, pieces)
        if valid:
            return valid

    def move(self, args):
        print("move called")
        my_key, x_0, y_0, x_1, y_1 = args

        move = Move((x_0, y_0), (x_1, y_1))
        game = self.games[my_key]
        status, message = game.make_move(my_key, move)
        return status, message
        


    ## Other
    def chat(self):
        print("chat called")

    def leaderboard(self):
        print("leaderboard called")


    ##Return to Player
    def end_game(self, winner, loser, reason):
        winner.user.status = "IDLE"
        loser.user.status = "IDLE"
        ##TODO : Implement self.DAOUsers.update_score(winner.id, winner.user.score)  # Increment winner's score
        ##self.DAOUsers.update_score(loser.id, loser.user.score)   # Decrement loser's score
        del self.games[winner.key]
        del self.games[loser.key]
        ##TODO : Send end game message to both players with reason and updated scores
    

    ##TESTING
    def test(self):
        user1 = User(0, 0, "Player1", 0)
        user2 = User(1, 1, "Player2", 0)
        lobby.active_users[user1.key] = user1
        lobby.active_users[user2.key] = user2

        # Start a game (simulate as user1)
        lobby.start_game([user1.key, user2.key])

        # Get the game instance
        game = lobby.games[user1.key]

        pieces1 = lobby.create_full_piece_setup(0, 0)   # Player 1, rows 0-3
        pieces2 = lobby.create_full_piece_setup(1, 6)   # Player 2, rows 6-9
        lobby.set_pieces([user1.key, pieces1])
        lobby.set_pieces([user2.key, pieces2])


        # Make a move for player 1
        move = Move((0, 3), (0, 4))
        game.make_move(user1.key, move)

        # Check if move was made and timer updated
        print(f"Move made: {game.move_made}")
        print(f"Player 1 time remaining: {game.players[0].time_remaining}")

    def create_full_piece_setup(self, player_order, starting_row):
        """
        Returns a list of 40 Piece objects for a player.
        player_order: 0 for player 1, 1 for player 2
        starting_row: the row where the player's pieces start (e.g., 0 or 6)
        """

        pieces = []
        # Example: Place all pieces in the first 4 rows for each player
        # You should adjust the types and positions to match your game rules
        piece_types = [
            PieceType.Maréchal, PieceType.Général, PieceType.Colonel, PieceType.Colonel,
            PieceType.Major, PieceType.Major, PieceType.Major,
            PieceType.Capitaine, PieceType.Capitaine, PieceType.Capitaine, PieceType.Capitaine,
            PieceType.Lieutenant, PieceType.Lieutenant, PieceType.Lieutenant, PieceType.Lieutenant,
            PieceType.Sergent, PieceType.Sergent, PieceType.Sergent, PieceType.Sergent,
            PieceType.Démineur, PieceType.Démineur, PieceType.Démineur, PieceType.Démineur, PieceType.Démineur,
            PieceType.Éclaireur, PieceType.Éclaireur, PieceType.Éclaireur, PieceType.Éclaireur,
            PieceType.Éclaireur, PieceType.Éclaireur, PieceType.Éclaireur, PieceType.Éclaireur,
            PieceType.Espion, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe,
            PieceType.Drapeau
        ]
        idx = 0
        for row in range(starting_row, starting_row + 4):
            for col in range(10):
                if idx < 40:
                    pieces.append(Piece(idx, piece_types[idx], (col, row), player_order))
                    idx += 1
        return pieces



if __name__ == "__main__":
    lobby = LobbyManager()
    lobby.test()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    
    

    
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

        username, password = args
        user_id = self.DAOUsers.create_user(
            username, password, 'French', 0, 'User', True, True
        )

        if user_id[0] == True:
            user = User(user_id[1], user_id[2], username, user_id[3], "IDLE")
            self.active_users[user.unique_id] = user
            return "USER_CREATED", user_id[1]
        return "ERROR", 0

    def login(self, args):
        print("login called")
        username, password = args
        user_id = self.DAOUsers.connect(username, password)
        if user_id[0] == True:
            user = User(user_id[1], user_id[2], username, user_id[3], "IDLE")
            self.active_users[user.unique_id] = user
            return "USER_CONNECTED", user_id[1]

        return "INVALID_USERNAME_PASSWORD", 0

    def logout(self, args):
        print("logout called")
        session_id = args[0]
        if session_id in self.active_users:
            del self.active_users[session_id]
            return "USER_DISCONNECTED"
        return "INVALID_KEY"
        

    def delete_profile(self):
        print("delete_profile called")
    
    def modify_profile(self):
        print("modify_profile called")


    ## Start/End Game
    def start_game(self, args): ## tout à changer une fois que les joueurs pourront se connecter et loop awaiting player
        print("start_game called")
        my_id = args[0]
        their_id = args[1]
        player1 = Player(self.active_users[my_id], 0)

        player2 = Player(self.active_users[their_id], 1)

        game = GameManager([player1, player2])
        self.games[my_id] = game
        self.games[their_id] = game

        return "Le jeu est commencé"

    def get_active_players(self, args) -> list[str]:
        print("get_active_players called")
        my_id = args[0]
        list_users = [user for key, user in self.active_users.items() if key != my_id]
        return list_users
    
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
        my_id = args[0]
        pieces = args[1]
        print(pieces)

        game = self.games[my_id] ##this might be a problem with how start_game works, but itll change so its fine for now
        valid = game.check_valid_setup(my_id, pieces)
        if valid:
            return valid


    def move(self, args):
        print("move called")
        my_id = args[0]
        move = args[1]

        game = self.games[my_id]
        game.make_move(my_id, move)


    ## Other
    def chat(self):
        print("chat called")

    def leaderboard(self):
        print("leaderboard called")

    
    def test(self):
        user1 = User(0, "Player1")
        user2 = User(1, "Player2")
        lobby.active_users[user1.unique_id] = user1
        lobby.active_users[user2.unique_id] = user2

        # Start a game (simulate as user1)
        lobby.start_game([user1.unique_id, user2.unique_id])

        # Get the game instance
        game = lobby.games[user1.unique_id]

        # Simulate both players are ready (skip placement for test)
        game.players_ready = 2

        pieces1 = lobby.create_full_piece_setup(0, 0)   # Player 1, rows 0-3
        pieces2 = lobby.create_full_piece_setup(1, 6)   # Player 2, rows 6-9
        lobby.set_pieces([user1.unique_id, pieces1])
        lobby.set_pieces([user2.unique_id, pieces2])


        # Make a move for player 1
        move = Move((0, 3), (0, 4))
        game.make_move(user1.unique_id, move)

        # Check if move was made and timer updated
        print(f"Move made: {game.move_made}")
        print(f"Player 1 time remaining: {game.players[0].time_remaining}")

    def create_full_piece_setup(self, player_order, starting_row):
        """
        Returns a list of 40 Piece objects for a player.
        player_order: 0 for player 1, 1 for player 2
        starting_row: the row where the player's pieces start (e.g., 0 or 6)
        """
        from GAME.piece import Piece, PieceType

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
    

    
import time

from DAO.DAOUsers import DAOUsers
from USERS.player import Player
from GAME.move import Move
from gameManager import GameManager
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from GAME.piece import Piece, PieceType


class LobbyManager:
    def __init__(self):
        self.games = {}  # dict: pour chaque player_id, donne la game, donc 2 entrées par jeu
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []

        self.actions = {
            "signup": self.create_profile,
            "signin": self.login,
            "signout": self.logout,
            "getStatus" : self.get_status,
            "deleteProfile" : self.logout,
            "modifyProfile" : self.modify_profile,
            "startGame" : self.start_game,
            "setPieces" : self.set_pieces,
            "startGameSpecificPlayer" : self.start_game_specific_player,
            "challenge" : self.challenge,
            "answerChallenge" : self.answer_challenge,
            "restartGame" : self.restart_game,
            "surrender" : self.surrender,
            "save" : self.save,
            "move" : self.move,
            "chat" : self.chat,
            "leaderboard" : self.leaderboard,
            "getActivePlayers" : self.get_active_players,  
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
        ##Eventuellement, il faudra faire en sorte que le joueur puisse choisir de jouer contre un autre joueur ou contre l'ia
        (my_key,) = args
        player1 = Player(self.active_users[my_key], 0)

        user_p2 = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")

        player2 = AIPlayer(user_p2, 1, 0)

        game = GameManager(self, [player1, player2])
        self.games[my_key] = game
        self.games[1] = game

        return "GAME_STARTED", player2.username

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
        my_key, pieces_recieved = args
        pieces_set = []

        pieces_set = self.convert_pieces(pieces_recieved, self.active_users[my_key])

        if my_key not in self.games: ##TODO : this is just for testing, it should be changed when the game loop is implemented, because the game will be created when the player starts searching for a game, not when they set their pieces, so this condition will never be true. For now, it allows us to test the set_pieces function without having to implement the game loop and the search for a game first.
            self.start_game((my_key,))

        if not self.games[my_key]:
            self.start_game((my_key,))
        game = self.games[my_key] ##this might be a problem with how start_game works, but itll change so its fine for now
        valid = game.check_valid_setup(my_key, pieces_set)
        if valid:
            return valid, self.active_users[my_key].status
        return "INVALID_PIECE_SETUP", self.active_users[my_key].status
    
    def convert_pieces(self, pieces_data, owner):
        pieces = []

        for i, piece_dict in enumerate(pieces_data):
            try:
                type_str = piece_dict["type"].replace("é", "e").replace("É", "E")

                ptype = PieceType[type_str]

                piece = Piece(
                    id=i,
                    type=ptype,
                    position=tuple(piece_dict["position"]),
                    owner=owner
                )

                pieces.append(piece)

            except KeyError as e:
                raise ValueError(f"Invalid piece data: missing {e} in {piece_dict}")
            except Exception as e:
                raise ValueError(f"Error processing piece {piece_dict}: {e}")

        return pieces

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

    def get_status(self, args):
        print("get_status called")
        (my_key,) = args
        if my_key not in self.games:
            return {"status": "IDLE"}
        game = self.games[my_key]
        return game.get_status(my_key)


    ##Return to Player
    def end_game(self, winner, loser, reason):
        winner.user.status = "IDLE"
        loser.user.status = "IDLE"
        ##TODO : Implement self.DAOUsers.update_score(winner.id, winner.user.score)  # Increment winner's score
        ##self.DAOUsers.update_score(loser.id, loser.user.score)   # Decrement loser's score
        del self.games[winner.key]
        del self.games[loser.key]
        ##TODO : Send end game message to both players with reason and updated scores
    
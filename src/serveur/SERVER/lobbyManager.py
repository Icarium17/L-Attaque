import threading

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
        self.game_types = ["ai", "multiplayer", "challenge"]

        self.actions = {
            "signup": self.create_profile,
            "signin": self.login,
            "signout": self.logout,
            "getStatus" : self.get_status,
            "deleteProfile" : self.logout,
            "modifyProfile" : self.modify_profile,
            "startGame" : self.start_game,
            "setPieces" : self.set_pieces,
            "restartGame" : self.restart_game,
            "surrender" : self.surrender,
            "save" : self.save,
            "move" : self.move,
            "chat" : self.chat,
            "leaderboard" : self.leaderboard,
            "getActivePlayers" : self.get_active_players,  
            "pause" : self.pause,
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
        user_created, user_id, session_key, status = self.DAOUsers.create_user(
            username, password, 'French', 0, 'User', True, True
        )

        if user_created:
            user = User(user_id, session_key, username, 0, "IDLE")
            self.active_users[user.key] = user
            return "USER_CREATED", session_key, status
        return "ERROR", -1, "ERROR"

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
    def start_game(self, args): 
        print("start_game called")
        (my_key, mode) = args

        if mode == "ai":
            return self._start_ai_game(my_key)

        elif mode == "multiplayer":
            return self._start_pvp_game(my_key)
        
        return "ERROR", ""

    def _start_pvp_game(self, my_key): 
        if self.wait_list:
            player1_key = self.wait_list.pop(0)
            player1 = Player(self.active_users[player1_key], 0)
            player2 = Player(self.active_users[my_key], 1)
            if player1_key in self.games and len(self.games[player1_key].players) == 1:
                game = self.games[player1_key]
                self.games[my_key] = game
                game.add_second_player(player2)
            else:
                game = GameManager(self, [player1, player2])
            self.games[player1_key] = game
            self.games[my_key] = game
            return "GAME_STARTED", player2.username
        else:
            self.wait_list.append(my_key)
            player1 = Player(self.active_users[my_key], 0)
            game = GameManager(self, [player1])
            self.games[my_key] = game
            return "WAITING_FOR_OPPONENT", ""

    def _start_ai_game(self, my_key):
        player = Player(self.active_users[my_key], 0)
        ai_user = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")
        ai_player = AIPlayer(ai_user, 1, 0)
        game = GameManager(self, [player, ai_player])
        self.games[my_key] = game

        return "GAME_STARTED", ai_player.username

    def get_active_players(self, args):
        print("get_active_players called")
        users = self.DAOUsers.get_all_users()
        active_usernames = [user.username for user in self.active_users.values()]

        for user in users:
            user["connected"] = user["username"] in active_usernames
        
        return users
    
    def restart_game(self):
        print("restart_game called")

    def surrender(self, args):
        print("surrender called")
        (my_key,) = args
        game = self.games[my_key] 
        game.surrender(my_key)

        return ("GAME_SURRENDERED")

    def pause(self, args):
        print("pause called")
        (my_key,) = args
        game = self.games[my_key]

        result = game.pause(my_key)

        return result


    def save(self):
        print("save called")

    def too_long_wait(self, player_key): #TODO : rework
        print("Its been too long")
        self.games[player_key] 


    ## Play Game
    def set_pieces(self, args):
        print("set_pieces called")
        my_key, pieces_recieved = args
        pieces_set = []
        
        game = self.games[my_key] 
        player = game.get_player(self.active_users[my_key].key)
        pieces_set = self.convert_pieces(pieces_recieved, player)
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
                    owner=owner.order
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
        return self.DAOUsers.get_high_scores()

    def get_status(self, args):
        print("get_status called")
        (my_key,) = args
        if my_key not in self.games:
            user = self.active_users.get(my_key)
            return {"status": user.status if user is not None else "IDLE"}
        game = self.games[my_key]
        return game.get_status(my_key)


    def end_game(self, winner, loser, reason): ##TODO : do something with reason
        game = None
        for player in (winner, loser):
            if not isinstance(player, AIPlayer) and player.key in self.games:
                game = self.games[player.key]
                break

        if game is not None:
            game.cleanup()

        if not isinstance(winner, AIPlayer):
            winner.user.status = "LAST_GAME_WON"
            self._cleanup(winner.user)
        if not isinstance(loser, AIPlayer):
            loser.user.status = "LAST_GAME_LOST"
            self._cleanup(loser.user)

    def _cleanup(self, user):
        self.games.pop(user.key, None)
        self.DAOUsers.update_score(user.account_id, user.score)


    
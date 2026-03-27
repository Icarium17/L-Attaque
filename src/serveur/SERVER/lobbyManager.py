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
        ##Eventuellement, il faudra faire en sorte que le joueur puisse choisir de jouer contre un autre joueur ou contre l'ia, et dans ce cas, on créera une instance d'AIPlayer au lieu de Player pour le second joueur. Pour l'instant, on fait juste une partie contre l'ia pour tester le fonctionnement du lobby manager et du game manager
        (my_key,) = args
        player1 = Player(self.active_users[my_key], 0)

        user_p2 = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")

        player2 = Player(user_p2, 1)

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
        my_key, pieces = args
        print(pieces)

        game = self.games[my_key] ##this might be a problem with how start_game works, but itll change so its fine for now
        valid = game.check_valid_setup(my_key, pieces)
        if valid:
            return valid, self.active_users[my_key].status
        return "INVALID_PIECE_SETUP", self.active_users[my_key].status

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
        pass


    ##Return to Player
    def end_game(self, winner, loser, reason):
        winner.user.status = "IDLE"
        loser.user.status = "IDLE"
        ##TODO : Implement self.DAOUsers.update_score(winner.id, winner.user.score)  # Increment winner's score
        ##self.DAOUsers.update_score(loser.id, loser.user.score)   # Decrement loser's score
        del self.games[winner.key]
        del self.games[loser.key]
        ##TODO : Send end game message to both players with reason and updated scores
    
from gameManager import GameManager
from player import Player
from aiPlayer import AIPlayer
from connexion import ConnexionUsers
from user import User

class LobbyManager():
    def __init__(self):
        self.games = {} ## dict, pour chaque player_id, donne la game. donc 2 entrées pour chaque jeu
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []

        self.actions = {
            "signup" : self.create_profile,
            "signin" : self.login,
            "logout" : self.logout,
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

        self.connexionUsers = ConnexionUsers()
    
    def execute_action(self, player_action, *args):
        action = self.actions.get(player_action)
        if action:
            return action(*args)
            

    ## Authentication
    def create_profile(self, args) -> bool:
        print("create_profile called")
        
        username, password = args
        user_created = self.connexionUsers.create_user(username, password, 'French', 0, 'User', True, True)
        ##username, password, preferred_language, id_avatar, rights, animation, contrast = args
        ##user_created = self.connexionUsers.create_user(username, password, preferred_language, id_avatar, rights, animation, contrast)
        if user_created:
            return "User created!"
        return "Error"

    def login(self, args):
        print("login called")
        username, password = args
        user_id = self.connexionUsers.connect(username, password)
        if user_id[0] == True:
            user = User(user_id[1], username)
            self.active_users[user.unique_id] = user
            return "User connected", user_id[1]
        
        return "Error, the username and the password do not match", 0

    def logout(self):
        print("logout called")

    def delete_profile(self):
        print("delete_profile called")
    
    def modify_profile(self):
        print("modify_profile called")


    ## Start/End Game
    def start_game(self, args): ## tout à changer une fois que les joueurs pourront se connecter et loop awaiting player
        print("start_game called")
        my_id = args[0]
        player = Player(self.active_users[my_id], 0)

        player_ai = AIPlayer()

        game = GameManager([player, player_ai])
        self.games[my_id] = game
        self.games[0] = game

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

        game = self.games[my_id]
        valid = game.check_valid_setup(my_id, pieces)
        if valid:
            return valid


    def move(self, args):
        print("move called")
        my_id = args[0]
        move = args[1]




    
    ## Other
    def chat(self):
        print("chat called")

    def leaderboard(self):
        print("leaderboard called")

    

    
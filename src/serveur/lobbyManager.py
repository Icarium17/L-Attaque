class LobbyManager():
    def __init__(self):
        self.games = {}
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []

        self.actions = {
            "login" : self.login,
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
    
    def execute_action(self, player_action, *args):
        action = self.actions.get(player_action)
        if action:
            action(*args)
            

    ## Authentication
    def login(self):
        print("login called")

    def logout(self):
        print("logout called")

    def delete_profile(self):
        print("delete_profile called")
    
    def modify_profile(self):
        print("modify_profile called")


    ## Start/End Game
    def start_game(self):
        print("start_game called")

    def get_active_players(self, my_id) -> list[str]:
        print("get_active_players called")
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
    def set_pieces(self):
        print("set_pieces called")

    def move(self):
        print("move called")

    
    ## Other
    def chat(self):
        print("chat called")

    def leaderboard(self):
        print("leaderboard called")

    

    
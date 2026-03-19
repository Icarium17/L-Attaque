from DAO.DAOUsers import DAOUsers
from USERS.user import User

class LobbyManager:
    def __init__(self):
        self.games = {}  # dict: pour chaque player_id, donne la game, donc 2 entrées par jeu
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []

        self.actions = {
            "signup": self.create_profile,
            "signin": self.login,
            "signout": self.logout
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
            return "USER_CREATED", user_id[1]
        return "Error", 0

    def login(self, args):
        print("login called")
        username, password = args
        user_id = self.DAOUsers.connect(username, password)
        if user_id[0] == True:
            user = User(user_id[1], username)
            self.active_users[user.unique_id] = user
            return "USER_CONNECTED", user_id[1]

        return "Error, the username and the password do not match", 0

    def logout(self, args):
        print("logout called")
        session_id = args[0]
        if session_id in self.active_users:
            del self.active_users[session_id]
            return "USER_DISCONNECTED"
        return "INVALID_KEY"







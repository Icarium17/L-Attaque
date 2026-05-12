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
            "surrender" : self.surrender,
            "save" : self.save,
            "load" : self.load,
            "move" : self.move,
            "chat" : self.chat,
            "leaderboard" : self.leaderboard,
            "getActivePlayers" : self.get_active_players,  
            "pause" : self.pause,
        }

        self.DAOUsers = DAOUsers()

    def execute_action(self, player_action, *args):
        """
        Execute a lobby action by name with provided arguments.
        Args:
            player_action: The action name as a string.
            *args: Arguments to pass to the action function.
        Returns:
            The result of the action function, or None if not found.
        """
        action = self.actions.get(player_action)
        if action:
            return action(*args)

    ## Authentication
    def create_profile(self, args) -> str:
        """
        Create a new user profile and add to active users.
        Args:
            args: Tuple containing username, password, and optionally rights.
        Returns:
            Tuple of (status, session_key, status_message)
        """

        username, password, *rest = args ## TODO : modifier pour que ça prenne en compte les autres paramètres (langue, etc)
        rights = rest[0] if rest else 'User'
        
        user_created, user_id, session_key, status = self.DAOUsers.create_user(
            username, password, 'French', 0, rights, True, True
        )

        if user_created:
            user = User(user_id, session_key, username, 0, "IDLE")
            self.active_users[user.key] = user
            return "USER_CREATED", session_key, status
        return "ERROR", -1, "ERROR"

    def login(self, args):
        """
        Log in a user and add to active users.
        Args:
            args: Tuple containing username and password.
        Returns:
            Tuple of (status, session_key) or error message.
        """
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
        """
        Log out a user and remove from active users.
        Args:
            args: Tuple containing session_id.
        Returns:
            Status message.
        """
        (session_id,) = args
        if session_id in self.active_users:
            del self.active_users[session_id]
            return "USER_DISCONNECTED"
        return "INVALID_KEY"
        

    def delete_profile(self, args):
        """
        Delete a user profile.
        Args:
            args: Tuple containing session_id.
        Returns:
            Result of DAOUsers.delete_user.
        """
        (my_key,) = args

        return self.DAOUsers.delete_user(my_key)
    
    def modify_profile(self):
        """
        Modify a user profile. (Not implemented)
        """


    ## Start/End Game
    def start_game(self, args):
        """
        Start a new game (AI or multiplayer).
        Args:
            args: Tuple containing session_key and mode.
        Returns:
            Tuple of (status, opponent_username or message).
        """
        (my_key, mode) = args

        if mode == "ai":
            return self._start_ai_game(my_key)

        elif mode == "multiplayer":
            return self._start_pvp_game(my_key)
        
        return "ERROR", ""

    def _start_pvp_game(self, my_key):
        """
        Start a player-vs-player game or add player to wait list.
        Args:
            my_key: The session key of the player starting the game.
        Returns:
            Tuple of (status, opponent_username or message).
        """
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
        """
        Start a game against an AI opponent.
        Args:
            my_key: The session key of the player starting the game.
        Returns:
            Tuple of (status, ai_username).
        """
        player = Player(self.active_users[my_key], 0)
        ai_user = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")
        ai_player = AIPlayer(ai_user, 1, 0)
        game = GameManager(self, [player, ai_player])
        self.games[my_key] = game

        return "GAME_STARTED", ai_player.username

    def get_active_players(self, args):
        """
        Get all users and mark which are currently active.
        Args:
            args: Not used.
        Returns:
            List of user dicts with 'connected' status.
        """
        users = self.DAOUsers.get_all_users()
        active_usernames = [user.username for user in self.active_users.values()]

        for user in users:
            user["connected"] = user["username"] in active_usernames
        
        return users


    def surrender(self, args):
        """
        Surrender the current game for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            Status message.
        """
        (my_key,) = args
        game = self.games[my_key] 
        game.surrender(my_key)

        return ("GAME_SURRENDERED")

    def pause(self, args):
        """
        Pause the current game for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            Result of game.pause.
        """
        (my_key,) = args
        game = self.games[my_key]

        result = game.pause(my_key)

        return result


    def save(self, args):
        """
        Save the current game state for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            Result of DAOUsers.save.
        """

        (my_key,) = args
        game = self.games[my_key]

        ai_difficulty, game_state_json, player_to_move, user_id = game.save()
        
        result = self.DAOUsers.save(ai_difficulty, game_state_json, player_to_move, user_id)

        return result

    def load(self, args):
        """
        Load a saved game for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            None. Updates self.games.
        """
        (my_key,) = args

        user = self.active_users[my_key]

        saved_game = self.DAOUsers.load_game(user.id)

        ai_difficulty = saved_game.get("ai_difficulty")
        player_to_move = saved_game.get("player_to_move")
        player_boards = saved_game.get("player_boards")
        board = saved_game.get("board")
        scores = saved_game.get("scores")
        times_remaining = saved_game.get("times")
        last_moves = saved_game.get("last_moves")

        player_score = scores[0] if scores else 0
        ai_score = scores[1] if scores else 0


        player = Player(user, player_score)
        player.load(player_boards[0], times_remaining[0], last_moves[0])


        ai_user = User(-1, "AI_KEY", "AI_Opponent", ai_score, "IDLE")
        ai_player = AIPlayer(ai_user, 1, ai_difficulty)
        ai_player.load(player_boards[1], times_remaining[1], last_moves[1])

        players = [player, ai_player]

        game = GameManager.load(self, players, player_to_move, board)

        self.games[player.key] = game


    

    def too_long_wait(self, player_key): #TODO : rework
        """
        Handle case where a player has waited too long. (Not implemented)
        Args:
            player_key: The session key of the waiting player.
        """
        self.games[player_key] 


    ## Play Game
    def set_pieces(self, args):
        """
        Set up the pieces for a player at the start of a game.
        Args:
            args: Tuple containing session_key and pieces_received.
        Returns:
            Tuple of (status, user_status).
        """
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
                # Use the id from the input data if present, else fallback to index
                piece_id = piece_dict.get("id", i)
                piece = Piece(
                    id=piece_id,
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
        """
        Make a move in the current game for a user.
        Args:
            args: Tuple containing session_key and move coordinates.
        Returns:
            Tuple of (status, message).
        """
        my_key, x_0, y_0, x_1, y_1 = args

        move = Move((x_0, y_0), (x_1, y_1))
        game = self.games[my_key]
        status, message = game.make_move(my_key, move)
        return status, message
        
    ## Other
    def chat(self):
        """
        Handle chat messages. (Not implemented)
        """

    def leaderboard(self):
        """
        Get the leaderboard (high scores).
        Returns:
            List of high scores from DAOUsers.
        """
        return self.DAOUsers.get_high_scores()

    def get_status(self, args):
        """
        Get the current status of a user or their game.
        Args:
            args: Tuple containing session_key.
        Returns:
            Status dict or result of game.get_status.
        """
        (my_key,) = args
        if my_key not in self.games:
            user = self.active_users.get(my_key)
            return {"status": user.status if user is not None else "IDLE"}
        game = self.games[my_key]
        return game.get_status(my_key)


    def end_game(self, winner, loser, reason):
        """
        End a game, clean up resources, and update player statuses.
        Args:
            winner: The Player or AIPlayer who won.
            loser: The Player or AIPlayer who lost.
            reason: Reason for game end (unused).
        """
        game = None
        for player in (winner, loser):
            if not isinstance(player, AIPlayer) and player.key in self.games:
                game = self.games[player.key]
                break

        if game is not None:
            game.cleanup()

        # Set statuses immediately
        if not isinstance(winner, AIPlayer):
            winner.user.status = "LAST_GAME_WON"
            threading.Timer(10, self._cleanup, args=(winner.user, 1)).start()
        if not isinstance(loser, AIPlayer):
            loser.user.status = "LAST_GAME_LOST"
            threading.Timer(10, self._cleanup, args=(loser.user, 0)).start()

    def _cleanup(self, user, win):
        """
        Remove a user's game and update their score after a delay.
        Args:
            user: The User object to clean up.
            win: 1 if the user won, 0 if lost.
        """
        self.games.pop(user.key, None)
        self.DAOUsers.update_score(user.account_id, user.score, win)


    
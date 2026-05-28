import threading

from DAO.DAOUsers import DAOUsers
from DAO.DAOStats import DAOStats
from DAO.DAOSave import DAOSave
from USERS.player import Player
from GAME.move import Move
from gameManager import GameManager
from USERS.aiPlayer import AIPlayer
from USERS.user import User
from GAME.piece import Piece, PieceType, BeliefPiece


class LobbyManager:
    """
    Coordinate connected users, active games, persistence, and lobby-level actions.
    """
    def __init__(self):
        """
        Initialize lobby state, action routing, and DAO helpers.
        """
        self.games = {}  # dict: pour chaque player_id, donne la game, donc 2 entrées par jeu
        self.wait_list = []
        self.active_users = {}
        self.active_challenges = []
        self.game_types = ["ai", "multiplayer", "challenge"]

        self.actions = {
            "signup": self.create_profile,
            "register" : self.register_profile,
            "signin": self.login,
            "signout": self.logout,
            "getStatus" : self.get_status,
            "deleteProfile" : self.delete_profile,
            "modifyProfile" : self.modify_profile,
            "difficulty" : self.update_difficulty,
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
        self.DAOStats = DAOStats()
        self.DAOSave = DAOSave()

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

    def _get_or_reattach_user(self, session_key):
        user = self.active_users.get(session_key)
        if user is not None:
            return user

        found, user_id, username, score = self.DAOUsers.get_user_by_session_key(session_key)
        if not found:
            return None

        user = User(user_id, session_key, username, score, "IDLE")
        self.active_users[user.key] = user
        return user

    def _get_active_game(self, session_key):
        game = self.games.get(session_key)
        if game is None:
            return None
        if not getattr(game, "players", None):
            return None
        return game

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
        return status, -1, status
    
    def register_profile(self, args):
        username, password, *rest = args ## TODO : modifier pour que ça prenne en compte les autres paramètres (langue, etc)
        rights = rest[0] if rest else 'User'
        
        user_created, _, _, status = self.DAOUsers.create_user(
            username, password, 'French', 0, rights, True, True, False
        )

        if user_created:
            return "USER_CREATED", None, status
        return status, -1, status

    def login(self, args):
        """
        Log in a user and add to active users.
        Args:
            args: Tuple containing username and password.
        Returns:
            Tuple of (status, session_key) or error message.
        """
        username, password = args
        result = self.DAOUsers.connect(username, password)
        if not result[0]:
            return "INVALID_USERNAME_PASSWORD", -1
        _, user_id, score = result

        if any(active_user.account_id == user_id for active_user in self.active_users.values()):
            return "USER_ALREADY_CONNECTED", -1

        session_key = self.DAOUsers.start_session(user_id)
        if session_key is None:
            return "ERROR", -1

        user = User(user_id, session_key, username, score, "IDLE")

        self.active_users[user.key] = user
        return "USER_CONNECTED", session_key

    def logout(self, args):
        """
        Log out a user and remove from active users.
        Args:
            args: Tuple containing session_id.
        Returns:
            Status message.
        """
        (my_key,) = args
        user = self._get_or_reattach_user(my_key)
        if user is not None:
            self.DAOUsers.logout(user.account_id)
            self.active_users.pop(my_key, None)
            self.games.pop(my_key, None)
            normalized_wait_list = []
            for entry in self.wait_list:
                key = entry[0] if isinstance(entry, tuple) else entry
                if key != my_key:
                    normalized_wait_list.append(key)
            self.wait_list = normalized_wait_list
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
        user = self._get_or_reattach_user(my_key)
        if user is None:
            return False

        self.logout(args)

        return self.DAOUsers.delete_user(user.account_id)
    
    def modify_profile(self):
        """
        Modify a user profile. (Not implemented)
        """
        pass

    def update_difficulty(self, args):
        (my_key, difficulty) = args

        if not isinstance(difficulty, int) or isinstance(difficulty, bool):
            return "INVALID_DIFFICULTY"

        difficulty -= 1

        user = self._get_or_reattach_user(my_key)
        if user is not None:
            result = self.DAOUsers.update_difficutly(user.account_id, difficulty)

            if result == 1 :
                return "DIFFICULTY_UPDATED"
            
            return "ERROR"

        return "INVALID_KEY"

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

        if self._get_or_reattach_user(my_key) is None:
            return "INVALID_KEY", ""

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
            entry = self.wait_list.pop(0)
            player1_key = entry[0] if isinstance(entry, tuple) else entry
            player2 = Player(self.active_users[my_key], 1)
            if player1_key in self.games and len(self.games[player1_key].players) == 1:
                game = self.games[player1_key]
                self.games[my_key] = game
                game.add_second_player(player2)
            else:
                player1_user = self.active_users.get(player1_key)
                if player1_user is None:
                    self.wait_list.insert(0, player1_key)
                    return "WAITING_FOR_OPPONENT", ""
                player1 = Player(player1_user, 0)
                game = GameManager(self, [player1, player2])
            self.games[player1_key] = game
            self.games[my_key] = game
            return "GAME_STARTED", player2.username
        else:
            player1 = Player(self.active_users[my_key], 0)
            self.wait_list.append(my_key)
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
        difficulty = self.DAOUsers.get_difficulty(player.user.account_id)
        ai_user = User(-1, "AI_KEY", "AI_Opponent", 0, "IDLE")
        ai_player = AIPlayer(ai_user, 1, difficulty)
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
        if args:
            (my_key,) = args
            if self._get_or_reattach_user(my_key) is None:
                return []

        users = self.DAOStats.get_all_users()
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
        if self._get_or_reattach_user(my_key) is None:
            return "INVALID_KEY"

        game = self._get_active_game(my_key)
        if game is None:
            return "NO_ACTIVE_GAME"

        result = game.surrender(my_key)
        if isinstance(result, tuple):
            if result[0] == 0:
                return result[1]
            return result[1]

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
        if self._get_or_reattach_user(my_key) is None:
            return "INVALID_KEY"

        game = self._get_active_game(my_key)
        if game is None:
            return (0, "NO_ACTIVE_GAME")

        result = game.pause(my_key)

        return result


    def save(self, args):
        """
        Save the current game state for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            Result of DAOSave.save.
        """

        (my_key,) = args
        if self._get_or_reattach_user(my_key) is None:
            return (0, "INVALID_KEY")

        game = self._get_active_game(my_key)
        if game is None:
            return (0, "NO_ACTIVE_GAME")

        user_id, ai_difficulty, player_to_move, game_state_json = game.save(my_key)

        if user_id == 0:
            return (0, ai_difficulty)
        
        result = self.DAOSave.save(ai_difficulty, game_state_json, player_to_move, user_id)
        print(user_id)

        return result

    def load(self, args):
        """
        Load a saved game for a user.
        Args:
            args: Tuple containing session_key.
        Returns:
            Result of game.load
        """
        (my_key,) = args

        user = self._get_or_reattach_user(my_key)
        if user is None:
            return (0, "INVALID_KEY")

        print(user.account_id)

        saved_game = self.DAOSave.load_game(user.account_id)

        if not saved_game:
            return (0, "NO_SAVED_GAME")

        ai_difficulty = saved_game.get("ai_difficulty")
        player_to_move = saved_game.get("player_to_move")
        player_boards = saved_game.get("player_boards")
        board = saved_game.get("board")
        scores = saved_game.get("scores")
        times_remaining = saved_game.get("times")
        last_moves = saved_game.get("last_moves")

        if (
            not isinstance(player_boards, list) or len(player_boards) < 2
            or not isinstance(board, list)
            or not isinstance(times_remaining, list) or len(times_remaining) < 2
            or not isinstance(last_moves, list) or len(last_moves) < 2
        ):
            return (0, "CORRUPTED_SAVE")

        board_p0 = player_boards[0]
        board_p1 = player_boards[1]
        if not isinstance(board_p0, list) or not isinstance(board_p1, list):
            return (0, "CORRUPTED_SAVE")

        time_p0 = times_remaining[0]
        time_p1 = times_remaining[1]
        if not isinstance(time_p0, (int, float)) or not isinstance(time_p1, (int, float)):
            return (0, "CORRUPTED_SAVE")

        moves_p0 = last_moves[0] if isinstance(last_moves[0], list) else []
        moves_p1 = last_moves[1] if isinstance(last_moves[1], list) else []

        player_to_move = player_to_move if player_to_move in (0, 1) else 0

        valid_scores = scores if isinstance(scores, (list, tuple)) else []
        player_score = valid_scores[0] if len(valid_scores) > 0 and isinstance(valid_scores[0], (int, float)) else 0
        ai_score = valid_scores[1] if len(valid_scores) > 1 and isinstance(valid_scores[1], (int, float)) else 0

        try:
            boards = [
                self.convert_pieces(board),
                self.convert_pieces(board_p0),
                self.convert_pieces(board_p1),
            ]
        except ValueError:
            return (0, "CORRUPTED_SAVE")

        user.status = "PLAYING"

        player = Player(user, 0, player_score)
        player.load(boards[1], time_p0, moves_p0)
        player.status = "PLAYING"


        ai_user = User(-1, "AI_KEY", "AI_Opponent", ai_score, "IDLE")
        ai_player = AIPlayer(ai_user, 1, ai_difficulty)
        ai_player.load(boards[2], time_p1, moves_p1)

        players = [player, ai_player]

        game = GameManager.load(self, players, player_to_move, boards[0])

        self.games[player.key] = game

        print(self.games)

        return (1, "RESTORED")

    def too_long_wait(self, player_key):
        """
        Handle case where a player has waited too long.
        Cleans up the game immediately and sets the user status to TIMED_OUT
        for 10 seconds, then resets it to IDLE.
        Args:
            player_key: The session key of the waiting player.
        """
        game = self.games.get(player_key)
        if game is None:
            return
        game.cleanup()
        self.games.pop(player_key, None)

        user = self.active_users.get(player_key)
        if user is None:
            return
        user.status = "TIMED_OUT"

        def reset_status():
            if user.status == "TIMED_OUT":
                user.status = "IDLE"

        timer = threading.Timer(10.0, reset_status)
        timer.daemon = True
        timer.start()


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

        user = self._get_or_reattach_user(my_key)
        if user is None:
            return "INVALID_KEY", "IDLE"
        
        game = self._get_active_game(my_key)
        if game is None:
            return "NO_ACTIVE_GAME", user.status

        player = game.get_player(user.key)
        if player is None:
            return "INVALID_KEY", user.status

        try:
            pieces_set = self.convert_pieces(pieces_recieved, player)
        except ValueError:
            return "INVALID_PIECE_SETUP", user.status
        valid = game.check_valid_setup(my_key, pieces_set)

        if valid:
            return valid, user.status
        return "INVALID_PIECE_SETUP", user.status
    
    def convert_pieces(self, pieces_data, owner = None):
        """
        Convert serialized piece payloads into `Piece` or `BeliefPiece` objects.

        Args:
            pieces_data: Iterable of serialized piece dictionaries.
            owner: Optional player object whose order should override serialized ownership.

        Returns:
            list: Converted piece objects.

        Raises:
            ValueError: Raised when the serialized payload is malformed.
        """
        if not isinstance(pieces_data, list):
            raise ValueError("Invalid piece data: expected a list of pieces")

        pieces = []
        for i, piece_dict in enumerate(pieces_data):
            try:
                if not isinstance(piece_dict, dict):
                    raise ValueError(f"Invalid piece data: expected object, got {type(piece_dict).__name__}")

                if owner is not None:
                    piece_owner = owner.order
                else:
                    piece_owner = piece_dict["owner"]
                piece_id = piece_dict.get("id", i)
                if piece_dict["type"] is None:
                    # Create a BeliefPiece
                    piece = BeliefPiece(
                        id=piece_id,
                        position=tuple(piece_dict["position"]),
                        owner=piece_owner
                    )
                    # Restore probabilities and evidence_weights if present
                    if "probabilities" in piece_dict:
                        piece.probabilities = BeliefPiece.restore_dict_with_enum_keys(piece_dict["probabilities"])
                    if "evidence_weights" in piece_dict:
                        piece.evidence_weights = BeliefPiece.restore_dict_with_enum_keys(piece_dict["evidence_weights"])
                else:
                    type_str = piece_dict["type"].replace("é", "e").replace("É", "E")
                    ptype = PieceType[type_str]
                    piece = Piece(
                        id=piece_id,
                        type=ptype,
                        position=tuple(piece_dict["position"]),
                        owner=piece_owner
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
        if self._get_or_reattach_user(my_key) is None:
            return "INVALID_KEY", "INVALID_KEY"

        if any(not isinstance(coord, int) or isinstance(coord, bool) for coord in (x_0, y_0, x_1, y_1)):
            return 0, "INVALID_MOVE_FORMAT"

        move = Move((x_0, y_0), (x_1, y_1))
        game = self._get_active_game(my_key)
        if game is None:
            return 0, "NO_ACTIVE_GAME"

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
        return self.DAOStats.get_high_scores()

    def get_status(self, args):
        """
        Get the current status of a user or their game.
        Args:
            args: Tuple containing session_key.
        Returns:
            Status dict or result of game.get_status.
        """
        (my_key,) = args
        user = self._get_or_reattach_user(my_key)
        if user is None:
            return {"status": "IDLE"}

        game = self.games.get(my_key)
        if game is None or not game.players:
            return {"status": user.status}
        return game.get_status(my_key)


    def end_game(self, winner, loser, reason):
        """
        End a game, clean up resources, and update player statuses.
        Args:
            winner: The Player or AIPlayer who won.
            loser: The Player or AIPlayer who lost.
            reason: Reason for game end (unused).
        """
        print(reason)
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
            self._cleanup(winner.user, 1)
        if not isinstance(loser, AIPlayer):
            loser.user.status = "LAST_GAME_LOST"
            self._cleanup(loser.user, 0)

    def _cleanup(self, user, win):
        """
        Remove a user's game and update their score after a delay.
        Args:
            user: The User object to clean up.
            win: 1 if the user won, 0 if lost.
        """
        self.games.pop(user.key, None)
        self.DAOUsers.update_score(user.account_id, user.score, win)


    
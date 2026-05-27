import json

from DAO.DAOConnection import Connection

class DAOSave():
    """
    Data-access helpers for persisting and restoring saved game state.
    """
    def save(self, ai_difficulty, board, player_to_move, user_id):
        """
        Replace the saved game associated with one user.

        Args:
            ai_difficulty: Difficulty level of the saved AI opponent.
            board: Serialized game state payload.
            player_to_move: Player index whose turn it is.
            user_id: Database id of the user owning the save.

        Returns:
            tuple: Status tuple indicating whether the save completed.
        """
        with Connection() as db:
            db.execute("DELETE FROM saved_games WHERE user_id = %s", (user_id,))

            try :
                db.execute("INSERT INTO saved_games (ai_difficulty, board, player_to_move, user_id) VALUES (%s, %s, %s, %s)", (ai_difficulty, board, player_to_move, user_id))
                return (1, "SAVE_COMPLETE")
                
            except Exception as e:
                return (0, "ERROR")
                

    def load_game(self, user_id):
        """
        Load the saved game state associated with one user.

        Args:
            user_id: Database id of the user whose save should be loaded.

        Returns:
            dict | None: Restored game-state payload, or `None` when no save exists.
        """
        with Connection() as db:
            saved_games = db.fetch("SELECT ai_difficulty, board, player_to_move FROM saved_games WHERE user_id = %s ", (user_id,))
            if not saved_games:
                print("ohoh")
                return None 
            saved_game = saved_games[0]
            try:
                game_state = json.loads(saved_game["board"])
            except (TypeError, ValueError, json.JSONDecodeError):
                return {
                    "ai_difficulty": saved_game.get("ai_difficulty"),
                    "player_to_move": saved_game.get("player_to_move"),
                    "player_boards": None,
                    "board": None,
                    "scores": None,
                    "times": None,
                    "last_moves": None,
                }

            if not isinstance(game_state, dict):
                return {
                    "ai_difficulty": saved_game.get("ai_difficulty"),
                    "player_to_move": saved_game.get("player_to_move"),
                    "player_boards": None,
                    "board": None,
                    "scores": None,
                    "times": None,
                    "last_moves": None,
                }

            return {
                "ai_difficulty": saved_game.get("ai_difficulty"),
                "player_to_move": saved_game.get("player_to_move"),
                "player_boards": game_state.get("player_boards"),
                "board": game_state.get("board"),
                "scores": game_state.get("scores"),
                "times": game_state.get("times"),
                "last_moves": game_state.get("last_moves")
            }
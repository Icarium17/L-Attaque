import json

from DAO.DAOConnection import Connection

class DAOSave():
    def save(self, ai_difficulty, board, player_to_move, user_id):
        with Connection() as db:
            db.execute("DELETE FROM saved_games WHERE user_id = %s", (user_id,))

            try :
                db.execute("INSERT INTO saved_games (ai_difficulty, board, player_to_move, user_id) VALUES (%s, %s, %s, %s)", (ai_difficulty, board, player_to_move, user_id))
                return (1, "SAVE_COMPLETE")
                
            except Exception as e:
                return (0, "ERROR")
                

    def load_game(self, user_id):
        with Connection() as db:
            saved_games = db.fetch("SELECT ai_difficulty, board, player_to_move FROM saved_games WHERE user_id = %s ", (user_id,))
            if not saved_games:
                print("ohoh")
                return None 
            saved_game = saved_games[0]
            game_state = json.loads(saved_game["board"])

            return {
                "ai_difficulty": saved_game["ai_difficulty"],
                "player_to_move": saved_game["player_to_move"],
                "player_boards": game_state["player_boards"],
                "board": game_state["board"],
                "scores": game_state["scores"],
                "times": game_state["times"],
                "last_moves": game_state["last_moves"]
            }
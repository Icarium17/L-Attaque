import json

from DAO.DAOConnection import Connection

class DAOSauvegarde():
    def sauvegarde_jeu(self, user_id, ai_difficulty, player_to_move, board, ai_belief_states, player_ai_known_pieces, last_moves, times):
        json_board = {
            "board_state": board.return_pieces(),
            "ai_belief_states": ai_belief_states,
            "player_ai_known_pieces": player_ai_known_pieces,
            "last_moves": last_moves,
            "times_remaining": times
        }

        with Connection() as db:
            existing_user = db.fetch("SELECT * FROM saved_games WHERE user_id=%s", (user_id,))
            if existing_user:
                return (False, "USER_ALREADY_SAVED_GAME")
            

            sql = """
            INSERT INTO saved_games (ai_difficulty, board, player_to_move, user_id)
            VALUES (%s, %s, %s, %s)
            """

            params = (ai_difficulty, json.dumps(json_board), player_to_move, user_id)

            if db.execute(sql, params):
                return (True, "GAME_SAVED")
            
            return (False, "WRROR_SAVING_GAME")
            

        def load_game(self, user_id):
            with Connection as db:
                game = db.fetch("SELECT * FROM saved_games WHERE user_id=%s", (user_id,))


            if game is None:
                return (False, "NO_SAVED_GAME")
            
            else: 
                pass




        
    






        
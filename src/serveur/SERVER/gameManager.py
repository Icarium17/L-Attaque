import time
import threading

from GAME.board import Board
from GAME.gameRules import GameRules
from GAME.piece import BeliefPiece
from USERS.aiPlayer import AIPlayer

class GameManager():
    def __init__(self, lobbyManager, players, game_type = "original"):
        self.lobbyManager = lobbyManager
        self.game_type = game_type
        self.board = Board(self.game_type)
        self.game_rules = GameRules(self.board, self.game_type)
        self.players = players
        self.set_player_boards()
        self.player_to_move = 0
        self.players_ready = set()
        self.timers = PlayerTimer(self.players, [player.time_remaining for player in self.players], self.timer_expired) 
        self.winner = None
        self.loser = None
        self.end_reason = None

    ###### Start and Setup ###### 

    def get_player(self, key):
        for player in self.players:
            if hasattr(player, "key") and player.key == key:
                return player
            if hasattr(player, "user") and hasattr(player.user, "key") and player.user.key == key:
                return player
        return None
    
    def set_player_boards(self):
        for player in self.players:
            player.known_board = Board(self.game_type)
            player.user.status = "SETTING_UP"

    def check_valid_setup(self, player_id, pieces) -> str:
        player_order = self.get_order(player_id)
        if player_order == -1:
            return ("Le joueur n'est pas valide")
        
        positions = self.game_rules.validate_placement(player_order, pieces)
        if positions[0] == 0:
            return positions
        
        self.board.set_pieces(pieces)
        self.players[player_order].position_pieces(pieces) 
        self.players[player_order].pieces = {piece.id: piece for piece in pieces} 
        self.set_unknowns_pieces(player_id, pieces) 
        self.players_ready.add(player_id)

        ##setup pieces AI. TODO : change once it works
        for player in self.players:
            if isinstance(player, AIPlayer):
                print("AI")
                self.setup_ai_player(player.order)
        ##self.check_board() ## TODO : Retirer une fois que tout fonctionne
        if all(p.key in self.players_ready for p in self.players):
            self.timers.start(0)
            for p in self.players:
                p.user.status = "GAME_READY"
        else :
            self.players[player_order].user.status = "WAITING_FOR_OPPONENT"
        
        return ("SETUP_SUCCESS")

    def setup_ai_player(self, order):
        ai_player = self.players[order]
        ai_pieces = ai_player.set_up_random_pieces()
        self.board.set_pieces(ai_pieces) ##ok
        ai_player.position_pieces(ai_pieces)
        ai_player.pieces = {piece.id: piece for piece in ai_pieces}
        self.set_unknowns_pieces(ai_player.key, ai_pieces) ##ok
        self.players_ready.add(ai_player.key)
        ai_player.game_rules = self.game_rules
        ai_player.players = self.players

    def set_unknowns_pieces(self, player_id, pieces):
        player_order = self.get_order(player_id)
        
        belief_pieces = []
        for piece in pieces:
            belief = BeliefPiece(piece.id, piece.position, player_order)
            belief_pieces.append(belief)
        for opponent in self.players[:player_order] + self.players[player_order + 1:]:
            opponent.position_pieces(belief_pieces)
        self.players[player_order].belief_pieces = belief_pieces
        
    def check_board(self):
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                tile = self.board.tiles[y][x]
                if tile.piece:
                    print(f"Tile ({x}, {y}) has piece owned by player {tile.piece.owner} at position {tile.piece.position}")
                else:
                    print(f"Tile ({x}, {y}) is empty")


    ###### Game Logic ######
    
    def get_order(self, player_id) -> int:
        player_order = next((i for i, obj in enumerate(self.players) if obj.key == player_id), -1)
        return player_order
    
    def make_move(self, player_id, move):
        player = self.players[self.get_order(player_id)]
        if player.order == -1:
            return (0, "INVALID_KEY")
        
        valid_move = self.game_rules.validate_move(player.order, move)
        print(valid_move[1])
        if valid_move[0] == 0:
            return valid_move
        
        tileFrom = self.board.tiles[move.moveFrom[1]][move.moveFrom[0]]
        pieceFrom = tileFrom.piece
        tileTo = self.board.tiles[move.moveTo[1]][move.moveTo[0]]

        if tileTo.piece and tileTo.piece.owner != player.order:
            move = self.combat(pieceFrom, tileFrom, tileTo.piece, tileTo)

        else :
            self.board.move(move)
            for player in self.players:
                player.move(move)
            ## TODO : Update belief states for all players based on the move and the result of the move (e.g. if a piece was captured, update the probabilities for that piece being in certain positions)

        self.change_turn()
        
        return (1, "MOVE_SUCCESS")
    
    def change_turn(self):
        ##if not self.check_end_state(): ##TODO : add afterwards
        self.player_to_move = (self.player_to_move + 1) % len(self.players)
        self.timers.switch_player(self.player_to_move)
        player = self.players[self.player_to_move]
        if isinstance(player, AIPlayer):
            player.player_to_move = self.player_to_move
            move = player.choose_move()
            print(move)
            self.make_move(self.player_to_move, move)

    def combat(self, attacker, attacker_tile, defender, defender_tile):
        winner = self.game_rules.combat(attacker, defender)
        # Remove both if tie
        if winner is None:
            self.board.remove_piece(attacker_tile)
            self.board.remove_piece(defender_tile)
            for player in self.players:
                player.remove_piece(attacker)
                player.remove_piece(defender)
        elif attacker == winner:
            self.board.remove_piece(defender_tile)
            for player in self.players:
                player.remove_piece(defender)
        else:
            self.board.remove_piece(attacker_tile)
            for player in self.players:
                player.remove_piece(attacker)

        for player in self.players:
            player.update_belief_states(attacker)
            player.update_belief_states(defender)

        return winner == attacker

    def get_status(self, player_id):
        player = self.players[self.get_order(player_id)]
        if player.order == -1:
            return {"status": "INVALID_KEY"}
        
        list_pieces = self.board.return_pieces()
        times_remaining = [player.time_remaining for player in self.players]
        status = {
            "status": "PLAYING", ## À modifier 
            "board": list_pieces,
            "turn": "blue" if self.player_to_move == 0 else "red",
            "time_remaining": times_remaining
        }
        return status
    

    ###### End Game ######

    ## TODO : Check the end game conditions after each moves
    def check_end_state(self):
        for player in self.players:
            ended, result = self.game_rules.check_player_end_state(player, self.players)
            if ended:
                self.timers.stop()
                winner, loser, reason = result
                self.declare_winner(winner, loser, reason)
                return True
        return False
            

    def declare_winner(self, winner, loser, reason):
        self.winner = winner
        self.loser = loser
        self.end_reason = reason
        self.end_game()

    def end_game(self):
        print(f"Game ended! Winner: {self.winner.username}, Loser: {self.loser.username}, Reason: {self.end_reason}")
        for player in self.players:
            player.user.score += self.game_rules.calc_score(player)
        self.lobbyManager.end_game(self.winner, self.loser, self.end_reason)

    def timer_expired(self, player):
        self.declare_winner(self.players[(player + 1) % len(self.players)], self.players[player], f"{self.players[player].username}'s timer expired")

    

class PlayerTimer:
    def __init__(self, players, times, timer_expired_callback):
        self.players = players
        self.times = times  
        self.current_player = 0
        self.delay = 1
        self.running = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.timer_expired_callback = timer_expired_callback
        self.last_switch_time = None

    def start(self, player):
        with self.lock:
            self.current_player = player
            self.running = True
            self.last_switch_time = time.time()
            if not self.thread.is_alive():
                self.thread.start()

    def switch_player(self, next_player):
        with self.lock:
            now = time.time()
            if self.running and self.last_switch_time is not None:
                elapsed = now - self.last_switch_time
                self.times[self.current_player] -= elapsed
            self.current_player = next_player
            self.last_switch_time = now

    def stop(self):
        with self.lock:
            if self.running and self.last_switch_time is not None:
                elapsed = time.time() - self.last_switch_time
                self.times[self.current_player] -= elapsed
            self.running = False
            self.last_switch_time = None

    def _run(self):
        while True:
            time.sleep(self.delay)
            with self.lock:
                if self.running and self.last_switch_time is not None:
                    self.players[self.current_player].time_remaining -= self.delay
                    if self.players[self.current_player].time_remaining <= 0:
                        self.players[self.current_player].time_remaining = 0
                        self.running = False
                        self.timer_expired_callback(self.current_player)
                        self.last_switch_time = None

    def get_times(self):
        with self.lock:
            times_copy = self.times[:]
            if self.running and self.last_switch_time is not None:
                elapsed = time.time() - self.last_switch_time
                times_copy[self.current_player] -= elapsed
                if times_copy[self.current_player] < 0:
                    times_copy[self.current_player] = 0
            return times_copy



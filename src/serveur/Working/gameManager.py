import asyncio
import time

import threading

from GAME.board import Board
from GAME.gameRules import GameRules
from GAME.piece import BeliefPiece
from USERS.player import Player

class GameManager():
    def __init__(self, lobbyManager, players, game_type = "original"):
        self.lobbyManager = lobbyManager
        self.game_type = game_type
        self.board = Board(self.game_type)
        self.game_rules = GameRules(self.board, self.game_type)
        self.players = players
        self.set_player_boards()
        self.player_to_move = 0
        self.players_ready = 0
        self.move_made = False
        self.timers = PlayerTimer(self.players, [player.time_remaining for player in self.players], self.timer_expired) 
        self.winner = None
        self.loser = None
        self.end_reason = None

    ###### Start and Setup ###### 
    
    def set_player_boards(self):
        for player in self.players:
            player.known_board = Board(self.game_type)

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
        self.players_ready+=1
        self.check_board() ## TODO : Retirer une fois que tout fonctionne
        if self.players_ready == len(self.players):
            self.timers.start(0)  # Start with player 0
            return ("Tous les joueurs sont prêts. Le jeu va commencer")
        return ("Les pièces sont correctement positionnées. En attente d'un autre joueur.") 

    def set_unknowns_pieces(self, player_id, pieces):
        belief_pieces = []
        for piece in pieces:
            belief = BeliefPiece(piece.id, piece.position, player_id)
            belief_pieces.append(belief)
        for opponent in self.players[:player_id] + self.players[player_id + 1:]:
            opponent.position_pieces(belief_pieces)
        self.players[player_id].belief_pieces = belief_pieces
        
    def check_board(self):
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                tile = self.board.tiles[y][x]
                if tile.piece:
                    print(f"Tile ({x}, {y}) has piece owned by player {tile.piece.owner} at position {tile.piece.position}")
                else:
                    print(f"Tile ({x}, {y}) is empty")

    def start_game(self):
        pass


    ###### Game Logic ######
    
    def get_order(self, player_id) -> int:
        player_order = next((i for i, obj in enumerate(self.players) if obj.key == player_id), -1)
        return player_order
    
    def make_move(self, player_id, move):
        player = self.players[self.get_order(player_id)]
        if player.order == -1:
            return (0, "Le joueur n'est pas valide")
        
        valid_move = self.game_rules.validate_move(player, move)
        if valid_move[0] == 0:
            return valid_move
        self.board.move(move)
        for player in self.players:
            player.move(move)
            ## TODO : Update belief states for all players based on the move and the result of the move (e.g. if a piece was captured, update the probabilities for that piece being in certain positions)

        for player in self.players:
            self.game_rules.check_flag_captured(player)

        
        self.player_to_move = (self.player_to_move + 1) % len(self.players)
        self.timers.switch_player(self.player_to_move)
        self.move_made = True
        
        return (1, "Le mouvement a été effectué avec succès")
    
    def combat(self, attacker, defender):
        pass
        ## If both pieces are the same, they are both removed from the board. If they are, we need to check if they were the last pieces the players had and call a tie if so.
    

    ###### End Game ######

    ## TODO : Check the end game conditions after each moves
    def check_end_game(self):
        for player in self.players:
            if self.game_rules.check_flag_captured(player):
                self.timers.stop()
                self.declare_winner(
                    self.players[(player.order + 1) % len(self.players)], 
                    player, 
                    f"{player.username}'s flag was captured")
                return
            
            if not self.game_rules.check_remaining_moves(player):
                self.timers.stop()
                self.declare_winner(
                    self.players[(player.order + 1) % len(self.players)], 
                    player, 
                    f"{player.username} has no moves left")
                return
            
            if self.game_rules.check_impassable_bomb_wall(player, self.players[(player.order + 1) % len(self.players)]):
                self.timers.stop()
                self.declare_winner(
                    self.players[(player.order + 1) % len(self.players)], 
                    player, 
                    f"{player.username} has no way to win")
                return
            
            if not self.game_rules.check_no_mobile_pieces(player):
                self.timers.stop()
                self.declare_winner(
                    self.players[(player.order + 1) % len(self.players)], 
                    player, 
                    f"{player.username} has no mobile pieces left")
                return
            
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



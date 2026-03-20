import asyncio
from time import time

from GAME.board import Board
from GAME.gameRules import GameRules

class GameManager():
    def __init__(self, players, game_type = "original"):
        self.game_type = game_type
        self.board = Board(self.game_type)
        self.game_rules = GameRules(self.board, self.game_type)
        self.players = players
        self.set_player_boards()
        self.player_to_move = 0
        self.players_ready = 0
        self.move_made = False
        self.game_active = False
        self.sleep_interval = 0.05


    def set_player_boards(self):
        for player in self.players:
            player.board = self.board

    def check_valid_setup(self, player_id, pieces) -> str:
        player_order = self.get_order(player_id)
        if player_order == -1:
            return ("Le joueur n'est pas valide")
        
        positions = self.game_rules.validate_placement(player_order, pieces)
        if positions[0] == 0:
            return positions
        
        self.board.set_pieces(pieces)
        self.players[player_order].position_pieces(pieces) # TODO : after all players have set their pieces, set the unknown pieces of their board too
        self.players_ready+=1
        self.check_board()
        return ("Les pièces sont correctement positionnées") ##ajouter un check si tous les joueurs sont prêts à jouer
        
    
    def check_board(self):
        for y in range(self.board.rows):
            for x in range(self.board.cols):
                tile = self.board.tiles[y][x]
                if tile.piece:
                    print(f"Tile ({x}, {y}) has piece owned by player {tile.piece.owner} at position {tile.piece.position}")
                else:
                    print(f"Tile ({x}, {y}) is empty")
    

    def get_order(self, player_id) -> int:
        player_order = next((i for i, obj in enumerate(self.players) if obj.unique_id == player_id), -1)
        return player_order
    
    def make_move(self, player_id, move):
        player = self.players[self.get_order(player_id)]
        if player.order == -1:
            return ("Le joueur n'est pas valide")
        
        valid_move = self.game_rules.validate_move(player, move)
        if valid_move[0] == 0:
            return valid_move
        
        self.board.move(move)
        player.board.move(move)
        self.move_made = True
    

    ## TODO : Add a function to check if the game has ended after each move, and call end_game() if it has
    def end_game(self):
        self.game_active = False

    
    ## TODO : Implement a function to check if the game has ended, and return the result (e.g. which player won, or if it's a draw) or None
    def check_end_game(self):
        pass
    
    def start_game(self):
        self.game_active = True
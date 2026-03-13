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
        self.players[player_order].board.set_pieces(pieces)
        self.players_ready+=1
        return ("Les pièces sont correctement positionnées") ##ajouter un check si tous les joueurs sont prêts à jouer
    

    def get_order(self, player_id) -> int:
        player_order = next((i for i, obj in enumerate(self.players) if obj.id == player_id), -1)
        return player_order
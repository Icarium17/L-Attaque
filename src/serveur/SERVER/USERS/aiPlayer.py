from USERS.player import Player

class AIPlayer(Player):
    def __init__(self, difficulty, board):
        self.difficulty = difficulty
        self.board = board

    def position_pieces(self):
        pass

    def initialize_game(self):
        return super().initialize_game()
    
    def turn(self):
        pass

    def update_board(self):
        pass
    


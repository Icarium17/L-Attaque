from copy import copy

class InfoSet:
    def __init__(self, board_state, player_turn, game_rules):
        self.board_state = board_state
        self.player_turn = player_turn
        self.game_rules = game_rules

    def get_all_possible_moves(self):
        pieces = self.board_state.get_pieces(self.player_turn)
        possible_moves = self.game_rules.get_possible_moves(pieces)
        return possible_moves
    
    def simulate_move(self, move):
        new_board_state = copy.deepcopy(self.board_state)
        new_board_state.move(move)
        return new_board_state
    
    def new_infoSet(self, move): 
        ## TODO : add checks for move validity and returns None if move is invalid. Check in Node if the return is invalid too
        new_board_state = self.simulate_move(move)
        return InfoSet(new_board_state, 1 - self.player_turn, self.game_rules)
    
    def update_infoSet(self, move):
        ## TODO : add checks for move validity and returns False if move is invalid. Check in Node if the return is invalid too
        self.board_state.move(move)
        self.player_turn = 1 - self.player_turn
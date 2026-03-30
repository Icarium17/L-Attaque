from USERS.player import Player
from GAME.piece import Piece, PieceType

class AIPlayer(Player):
    def __init__(self, user_instance, order, difficulty, time_remaining = (1*15)):
        super().__init__(user_instance, order, time_remaining)
        self.difficulty = difficulty
        self.player_to_move = 0

    def initialize_game(self):
        return super().initialize_game()

    
    def set_up_random_pieces(self):
        """
        Returns a list of 40 Piece objects for a player.
        player_order: 0 for player 1, 1 for player 2
        starting_row: the row where the player's pieces start (e.g., 0 or 6)
        """



        pieces = []
        # Example: Place all pieces in the first 4 rows for each player
        # You should adjust the types and positions to match your game rules
        piece_types = [
            PieceType.Marechal, PieceType.General, PieceType.Colonel, PieceType.Colonel,
            PieceType.Major, PieceType.Major, PieceType.Major,
            PieceType.Capitaine, PieceType.Capitaine, PieceType.Capitaine, PieceType.Capitaine,
            PieceType.Lieutenant, PieceType.Lieutenant, PieceType.Lieutenant, PieceType.Lieutenant,
            PieceType.Sergent, PieceType.Sergent, PieceType.Sergent, PieceType.Sergent,
            PieceType.Demineur, PieceType.Demineur, PieceType.Demineur, PieceType.Demineur, PieceType.Demineur,
            PieceType.Eclaireur, PieceType.Eclaireur, PieceType.Eclaireur, PieceType.Eclaireur,
            PieceType.Eclaireur, PieceType.Eclaireur, PieceType.Eclaireur, PieceType.Eclaireur,
            PieceType.Espion, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe, PieceType.Bombe,
            PieceType.Drapeau
        ]
        idx = 0
        for row in range(0, 4):
            for col in range(10):
                if idx < 40:
                    pieces.append(Piece(idx, piece_types[idx], (col, row), self))
                    idx += 1
        return pieces


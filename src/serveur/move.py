class Move():
    def __init__(self, piece, moveTo):
        self.piece = piece
        self.moveTo = moveTo ## tuple(x, y)

    def getParams(self):
        return self.piece, self.moveTo
    

    def __eq__(self, other):
            if not isinstance(other, Move):
                return False
            return self.piece == other.piece and self.moveTo == other.moveTo
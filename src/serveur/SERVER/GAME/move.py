class Move():
    def __init__(self, moveFrom, moveTo):
        self.moveFrom = moveFrom ## tuple(x, y)
        self.moveTo = moveTo ## tuple(x, y)

    def get_params(self):
        x_0, y_0 = self.moveFrom
        x_1, y_1 = self.moveTo
        return x_0, y_0, x_1, y_1
    
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.moveFrom == other.moveFrom and self.moveTo == other.moveTo) or (self.moveFrom == other.moveTo and self.moveTo == other.moveFrom)

    def __hash__(self):
        return hash((self.moveFrom, self.moveTo))
    
    def invert(self):
        x0, y0 = self.moveFrom
        x1, y1 = self.moveTo
        self.moveFrom = (9 - x0, 9 - y0)
        self.moveTo = (9 - x1, 9 - y1)
    
  
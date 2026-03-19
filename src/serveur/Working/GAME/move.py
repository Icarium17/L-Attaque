class Move():
    def __init__(self, moveFrom, moveTo):
        self.moveFrom = moveFrom ## tuple(x, y)
        self.moveTo = moveTo ## tuple(x, y)

    def getParams(self):
        x_0, y_0 = self.moveFrom
        x_1, y_1 = self.moveTo
        return x_0, y_0, x_1, y_1
    

    def __eq__(self, other):
            if not isinstance(other, Move):
                return False
            return self.moveFrom == other.moveFrom and self.moveTo == other.moveTo
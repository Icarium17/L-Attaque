class Tile():
    def __init__(self, id, x, y, state = 0):
        self.id = id
        self.x = x
        self.y = y
        self.state = state
        self.piece = None
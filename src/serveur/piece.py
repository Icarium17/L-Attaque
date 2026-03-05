class Piece():
    def __init__(self, id, type, position, owner):
        self.id = id
        self.type = type
        self.position = position
        self.owner = owner ## int avec l'ordre du joueur
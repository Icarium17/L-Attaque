from enum import Enum


class PieceType(Enum):
    Maréchal = (10, 1)
    Général = (9, 1)
    Colonel = (8, 2)
    Major = (7, 3)
    Capitaine = (6, 4)
    Lieutenant = (5, 4)
    Sergent = (4, 4)
    Démineur = (3, 5)
    Éclaireur = (2, 8)
    Espion = (None, 1)
    Bombe = (None, 6)
    Drapeau = (None, 1)

    def __init__(self, power, count):
        self._power = power
        self._count = count

    @property
    def power(self):
        return self._power

    @property
    def count(self):
        return self._count


class Piece():
    def __init__(self, id, type, position, owner):
        self.id = id
        self.type = type
        self.position = position
        self.owner = owner ## int avec l'ordre du joueur
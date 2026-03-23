from enum import Enum


class PieceType(Enum):
    Maréchal = (10, 1, 10)
    Général = (9, 1, 9)
    Colonel = (8, 2, 8)
    Major = (7, 3, 7)
    Capitaine = (6, 4, 6)
    Lieutenant = (5, 4, 5)
    Sergent = (4, 4, 4)
    Démineur = (3, 5, 3)
    Éclaireur = (2, 8, 2)
    Espion = (None, 1, 1)
    Bombe = (None, 6, 6)
    Drapeau = (-1, 1, 1)

    def __init__(self, power, count, score):
        self._power = power
        self._count = count
        self.score = score

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

class BeliefPiece(Piece):
    def __init__(self, id, position, owner):
        super().__init__(id, None, position, owner)
        self.probabilities = {}
        self.set_probabilities() # TODO : À modifier quand le jeu va fonctionner, pour que tout puisse être updaté rapidement.
        
    def set_probabilities(self):
        total_pieces = sum(piece.count for piece in PieceType)
        for piece in PieceType:
            self.probabilities[piece] = piece.count / total_pieces

    def normalize(self): #when a piece becomes impossible (when it moves, it cant be a flag...)
        s = sum(self.probabilities.values())
        if s == 0:
            return ("No more ennemy pieces")
        for type in self.probabilities:
            self.probabilities[type] /= s

    def update_probabilities(self, pieces_left):
        total_pieces = sum(pieces_left.values())

        for type in self.probabilities:
            if self.probabilities[type] > 0 :
                self.probabilities[type] = pieces_left[type] / total_pieces
            else:
                self.probabilities[type] = 0

        self.normalize()

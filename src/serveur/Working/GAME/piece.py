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

class BeliefPiece(Piece):
    def __init__(self, id, position, owner):
        super.__init__(self, id, None, position, owner)
        self.probabilities = self.set_probabilities() # TODO : À modifier quand le jeu va fonctionner, pour que tout puisse être updaté rapidement.
        
    def set_probabilities(self):
        total_pieces = sum(piece.count for piece in PieceType)
        for piece in PieceType:
            self.probabilities[piece] = piece.count / total_pieces

    def normalize(self): //when a piece becomes impossible (when it moves, it cant be a flag...)
        s = sum(self.probabilities.values())
        if s == 0:
            return ("No more ennemy pieces")
        for type in self.probabilities:
            prob.probabilities(type) /= s

    def update_probabilities(self, pieces_left):
        total_pieces = sum(remaining_count.values())

        for type in self.probabilities:
            if self.probabilities[type] > 0 :
                self.probabilities[type] = pieces_left[type] / total_pieces
            else:
                self.probabilities[type] = 0

        self.normalize()

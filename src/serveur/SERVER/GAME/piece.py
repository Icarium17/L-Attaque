from enum import Enum


class PieceType(Enum):
    Marechal = (10, 1, 10)
    General = (9, 1, 9)
    Colonel = (8, 2, 8)
    Major = (7, 3, 7)
    Capitaine = (6, 4, 6)
    Lieutenant = (5, 4, 5)
    Sergent = (4, 4, 4)
    Demineur = (3, 5, 3)
    Eclaireur = (2, 8, 2)
    Espion = (None, 1, 1)
    Bombe = (None, 6, 5)
    Drapeau = (-1, 1, 100)

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
    def __init__(self, id, type, position, owner, revealed = True):
        self.id = id
        self.type = type
        self.position = position
        self.owner = owner ## int avec l'ordre du joueur
        self.revealed = revealed

    def clone(self):
        return Piece(self.id, self.type, self.position, self.owner)

    def send(self):
        piece = {
            "id": self.id,
            "type": self.type.name if self.type else None,
            "position": self.position,
            "owner": self.owner
        }
        return piece
    
class BeliefPiece(Piece):
    def __init__(self, id, position, owner):
        super().__init__(id, None, position, owner, False)
        self.evidence_weights = {}
        self.probabilities = {}
        self.set_probabilities() 

    def clone(self):
        belief_piece = BeliefPiece(self.id, self.position, self.owner)
        belief_piece.evidence_weights = self.evidence_weights.copy()
        belief_piece.probabilities = self.probabilities.copy()
        return belief_piece
    
    def upgrade(self, type_piece):
        piece = Piece(self.id, type_piece, self.position, self.owner)
        return piece
        
    ## At the start, all types are equally compatible, and probabilities follow piece counts
    def set_probabilities(self):
        total_pieces = sum(piece.count for piece in PieceType)
        for piece in PieceType:
            self.evidence_weights[piece] = 1.0
            self.probabilities[piece] = piece.count / total_pieces

    def normalize(self): #when a piece becomes impossible (when it moves, it cant be a flag...)
        s = sum(self.probabilities.values())
        if s == 0:
            return ("No more ennemy pieces")
        for type in self.probabilities:
            self.probabilities[type] /= s


    def update_probabilities(self, pieces_left):
        for t in self.probabilities:
            self.probabilities[t] = self.evidence_weights[t] * pieces_left[t]

        self.normalize()
    
    def update_probabilities_on_move(self, distance):
        # Any movement eliminates immobile pieces
        self.evidence_weights[PieceType.Drapeau] = 0
        self.evidence_weights[PieceType.Bombe] = 0

        # Scout rule (long movement)
        if distance > 1:
            for t in self.evidence_weights:
                if t != PieceType.Eclaireur:
                    self.evidence_weights[t] = 0

    def check_upgrade_bp_to_piece(self):
        possible_types = [
            piece_type
            for piece_type, probability in self.probabilities.items()
            if probability > 0
        ]

        if len(possible_types) == 1:
            return self.upgrade(possible_types[0])

        return None
    
    def save(self):
        save = self.send()
        save["evidence_weights"] = self.evidence_weights
        save["probabilities"] = self.probabilities

        return save

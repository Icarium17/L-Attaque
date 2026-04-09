import random
from ALGO.infoSet import InfoSet
from ALGO.node import Node
import copy

class MCTS:
    def __init__(self, ai, game_rules, players):
        self.ai = ai
        self.infoSet = InfoSet(copy.deepcopy(ai.known_board), ai.order, game_rules)
        self.game_rules = game_rules
        self.player_to_move = self.ai.order
        self.players = players

        self.node_0 = Node(None, self.infoSet, None)
        self.current_node = self.node_0

        self.heuristic_evaluation = {
            0: self.heuristic_evaluation_easy,
            1: self.heuristic_evaluation_medium,
            2: self.heuristic_evaluation_hard
        }
        self.difficulty = self.ai.difficulty


    def algo(self):
        self.node_0.infoSet.board_state = copy.deepcopy(self.ai.known_board)
        self.node_0.infoSet.actualize_belief_pieces(self.ai.opponent_pieces_left.copy())
        self.current_node = self.node_0

        self.selection()
        self.expansion()
        win_score = self.simulation()
        self.backpropagation(win_score)
    

    def selection(self):
        print("selection")
        while True:
            next_node = self.current_node.selection()
            if next_node is not None:
                self.current_node = next_node
            else:
                break

    def expansion(self):
        print("expansion")
        next_node = self.current_node.expand()
        if next_node is not None:
            self.current_node = next_node
            self.player_to_move = self.current_node.infoSet.player_turn
            self.infoSet = self.current_node.infoSet
            

    def simulation(self): 
        print("simulation") 
        game_over = 0
        s = 0
        while not game_over and  s < 1000:
            self.heuristic_evaluation[self.difficulty]()
            # # Debug: print board state
            # print("Board state:")
            # for y, row in enumerate(self.infoSet.board_state.tiles):
            #     row_str = []
            #     for x, tile in enumerate(row):
            #         if tile.piece is None:
            #             row_str.append(".")
            #         else:
            #             owner = getattr(tile.piece, 'owner', '?')
            #             ptype = str(getattr(tile.piece, 'type', '?'))
            #             if '.' in ptype:
            #                 ptype_name = ptype.split('.')[-1]
            #             else:
            #                 ptype_name = ptype
            #             # Use 'Df' for Drapeau (flag), 'Dm' for Demineur, else first letter
            #             if ptype_name == 'Drapeau':
            #                 code = 'Df'
            #             elif ptype_name == 'Demineur':
            #                 code = 'Dm'
            #             else:
            #                 code = ptype_name[0]
            #             row_str.append(f"{owner}{code}")
            #     print(' '.join(row_str))
                
            game_over = self.game_over()
            s += 1

        print("game_over", game_over, "s", s)
        print("simulation phase done")

        return game_over

    def backpropagation(self, win_score):
        ## TODO : modifier player_to_move to match the current infoSet`s
        node = self.current_node
        while node is not None:
            node.visit_count += 1
            if node.infoSet.player_turn == self.player_to_move:
                node.win_score += win_score
            else:
                node.win_score -= win_score
            node = node.parent
        

    def heuristic_evaluation_easy(self): ## TODO : right now, entirely random
        possible_moves = self.infoSet.get_all_possible_moves()
        if len(possible_moves) == 0:
            return 
        move = random.choice(possible_moves)
        self.infoSet.update_infoSet(move)

    def heuristic_evaluation_medium(self):
        # TODO : implement a better heuristic evaluation for the medium difficulty
        self.heuristic_evaluation_easy()

    def heuristic_evaluation_hard(self):
        # TODO : implement a perfect heuristic evaluation for the hard difficulty
        self.heuristic_evaluation_easy()
        

    def game_over(self):
        for player in self.players:
            my_pieces = self.infoSet.board_state.get_pieces(player.order)
            opponent_pieces = self.infoSet.board_state.get_pieces(1- player.order)

            ended, reason = self.game_rules.check_player_end_state(player, self.players, self.infoSet.board_state, my_pieces, opponent_pieces, 1)
            if ended:
                print(reason)
                # # Print all pieces with at least one valid move
                # from GAME.move import Move
                # print(f"Checking all possible moves for {player.username} (order {player.order}) at game end:")
                # for pid, piece in my_pieces.items():
                #     if hasattr(piece, 'type') and piece.type.name not in ['Drapeau', 'Bombe']:
                #         for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                #             new_x, new_y = piece.position[0] + dx, piece.position[1] + dy
                #             move = Move(piece.position, (new_x, new_y))
                #             valid, reason2 = self.game_rules.validate_move(player.order, move)
                #             print(f"  Piece {piece.type.name} at {piece.position} -> ({new_x},{new_y}): valid={valid}, reason={reason2}")
                return 1
        return 0
    
    def get_best_move(self):
        if self.node_0.children:
            best_child = max(self.node_0.children, key=lambda x: x.win_score)
        else:
            best_child = self.node_0.get_random_child()
        return best_child.move
    

        

    

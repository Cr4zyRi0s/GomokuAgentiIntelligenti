import random
from gomoku import Game,is_valid_move

def place_random_stones(board, n_stones : int) -> list:
    positions = []
    for _ in range(n_stones):          
        pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))         
        while not is_valid_move(pos[0], pos[1], board):            
            pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))
        positions.append(pos)
    return positions

class Player:
    def __init__(self):
        self.game = None
        self.color = None

        self.first_placement = False    
        self.accept_or_place = False
        self.second_placement = False
        self.select_color = False      

    def can_play(self):
        if self.color == "black" and self.game.black_turn:
            return True
        elif self.color == "white" and not self.game.black_turn:
            return True
        return False

    def swap2_first_place_stones(self):    
        pass
    
    def swap2_second_place_stones(self):
        pass

    def swap2_accept_or_place(self):
        pass

    def swap2_select_color(self):
        pass

    def play_turn(self):
        pass
    
class AIPlayer(Player):    
    def swap2_first_place_stones(self):
        pass
    def swap2_second_place_stones(self):                        
        pass
    def swap2_accept_or_place(self):
        pass
    def swap2_select_color(self):
        pass

    def play_turn(self):
        if not self.can_play():
            return

        
class AIRandomPlayer(AIPlayer):
    def swap2_first_place_stones(self):
        b_positions = place_random_stones(self.game.board_state.grid, 2)
        w_positions = place_random_stones(self.game.board_state.grid, 1)
        self.game.swap2_first_placement(b_positions, w_positions)
    
    def swap2_second_place_stones(self):                        
        b_positions = place_random_stones(self.game.board_state.grid, 1)
        w_positions = place_random_stones(self.game.board_state.grid, 1)
        self.game.swap2_second_placement(b_positions, w_positions)

    def swap2_accept_or_place(self):
        self.game.swap2_accept_or_place(self,self.color)

    def swap2_select_color(self):
        self.game.swap2_select_color(self,self.color)

    def play_turn(self):
        if not self.can_play():
            return

        while not self.game.turn(self,
        (random.randint(0,self.game.size - 1),
        random.randint(0,self.game.size - 1))):
            pass


class HumanPlayer(Player):
    def swap2_first_place_stones(self):    
        self.first_placement = True
        self.black_stones_placed = 0
        self.white_stones_placed = 0

    def swap2_second_place_stones(self):
        self.second_placement = True
        self.black_stones_placed = 0
        self.white_stones_placed = 0

    def swap2_accept_or_place(self):
        pass

    def swap2_select_color(self):
        pass

    def on_click_grid(self,x,y,c,r):
        if self.first_placement:
            if self.black_stones_placed < 2:
                if self.game.place_stone((c,r),True):
                    self.black_stones_placed += 1               
            elif self.white_stones_placed < 1:
                if self.game.place_stone((c,r),False):
                    self.white_stones_placed += 1            
                    self.first_placement = False
                    self.game.swap2_first_placement()
        elif self.second_placement:
            if self.black_stones_placed < 1:
                if self.game.place_stone((c,r),True):
                    self.black_stones_placed += 1               
            elif self.white_stones_placed < 1:
                if self.game.place_stone((c,r),False):
                    self.white_stones_placed += 1
                    self.second_placement = False
                    self.game.swap2_second_placement()
        else:
            if self.can_play():
                self.game.turn(self,(c,r))

    def on_button_click(self, text):
        print(text)

        




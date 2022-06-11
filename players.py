import random
from boardstate import deepcopy_boardstate
from utils import is_valid_move
from minimax import DEFAULT_SEARCH_DEPTH, gomoku_get_best_move, gomoku_state_static_eval

def place_random_stones(board, n_stones : int) -> list:
    positions = []
    for _ in range(n_stones):          
        pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))         
        while not is_valid_move(pos[0], pos[1], board):            
            pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))
        positions.append(pos)
    return positions

def place_stone_not_aligned(board_size : int, other_stones : list):
    accept = False

    while not accept:
        accept = True
        rand_pos = (random.randint(2,board_size - 3), 
                    random.randint(2,board_size - 3))
        off45 = rand_pos[0] - rand_pos[1]
        off315 = rand_pos[0] + rand_pos[1] - board_size + 1
        for s in other_stones: 
            c_off45 = s[0] - s[1]
            c_off315 = s[0] + s[1] - board_size + 1
            if c_off45 == off45:
                accept = False
            elif c_off315 == off315:
                accept = False
            elif s[0] == rand_pos[0]:
                accept = False
            elif s[1] == rand_pos[1]:
                accept = False

    return rand_pos


class Player:
    def __init__(self):
        self.name = 'BasePlayer'
        self.game = None
        self.color = None

        self.first_placement = False    
        self.accept_or_place = False
        self.second_placement = False
        self.select_color = False      

    def can_play(self):
        if self.game.winning_player is not None:
            return False
        if self.color == "black" and self.game.black_turn:
            return True
        elif self.color == "white" and not self.game.black_turn:
            return True            
        return False

    def assign_color(self, color):
        self.color = color
        self.name = '_'.join([self.name.split('_')[0], self.color])

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
    def __init__(self,search_depth = DEFAULT_SEARCH_DEPTH, seed = 24):
        super().__init__()
        self.seed = seed
        self.name = self.__name__
        self.search_depth = search_depth
        random.seed(self.seed)

    def swap2_first_place_stones(self):        
        #place the first black stone at random
        b_stone_placements = []
        b_stone_placements[0] = (
        random.randint(2,self.game.size - 3), 
        random.randint(2,self.game.size - 3))
        #then choose to place a second stone so that it does not share a line with the first one
        b_stone_placements[1] = place_stone_not_aligned(self.game.size, b_stone_placements)
        #same goes for the white stone
        w_stone_placement = place_stone_not_aligned(self.game.size, b_stone_placements)

        self.game.swap2_first_placement(b_stone_placements, [w_stone_placement])

    def swap2_accept_or_place(self):
        bstate = self.game.board_state
        bl_nft = bstate.b_threats['nforcing'] 

        for t in bl_nft:
            if t.info['type'][0] > 1:
                break
        else:
            self.game.swap2_accept_or_place(self,'place')

        self.game.swap2_accept_or_place(self,'white')
                
    def swap2_second_place_stones(self):                        
        pass    

    def swap2_select_color(self):
        bstate = self.game.board_state
        bl_ft = bstate.b_threats['forcing']        
        if len(bl_ft) > 0:
            self.game.swap2_select_color(self, 'black')
            return

        state_score = gomoku_state_static_eval(bstate)
        if state_score > 0:
            best_white_move = gomoku_get_best_move(bstate,False,self.search_depth)
            bstate.make_move(best_white_move, False)
            new_state_score = gomoku_state_static_eval(bstate)
            bstate.unmake_last_move()
            if new_state_score <= 0:
                self.game.swap2_select_color('white')
                if not self.game.turn(self, best_white_move):
                    raise Exception('%s player was supposed to play but couldn\'t.' % (self.color))
            else:
                self.game.swap2_select_color('black')
        else:
            self.game.swap2_select_color('white')
                                            

    def play_turn(self):
        if not self.can_play():
            return

        print('ai', self.color,'thinking...')
        maximize = True if self.color == 'black' else False
        best_move = gomoku_get_best_move(self.game.board_state, maximize)
        if not self.game.turn(self,best_move):
            raise Exception('%s player was supposed to play but couldn\'t.' % (self.color))
        print('ai', self.color,'done')

        
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
    def __init__(self):
        super.__init__()
        self.name = self.__name__

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


if __name__ == '__main__':
    pass






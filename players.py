from operator import xor
import random
from shutil import ExecError
from threats import B_THREAT_DATA, W_THREAT_DEP, B_THREAT_DEP, _get_threat_class_from_info
from time import time
from utils import is_valid_move
from minimax import DEFAULT_SEARCH_DEPTH, gomoku_get_best_move, gomoku_state_static_eval
import networkx as nx

OPENINGS = [
    ([(7,7),(8,10)],[(8,7)]),
    ([(7,7), (7,10)],[(8,8)]),
    ([(7,7), (7,10)],[(8,7)]),
    ([(7,7),(8,10)],[(8,8)]),
    ([(7,7),(10,7)],[(8,7)]),
    ([(7,7),(6,10)],[(8,8)])
]  
OPENING_CNT = 0

def place_random_stones(board, n_stones : int) -> list:
    positions = []
    for _ in range(n_stones):          
        pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))         
        while not is_valid_move(pos[0], pos[1], board):            
            pos = (random.randint(0, board.shape[1] - 1), random.randint(0, board.shape[0] - 1))
        positions.append(pos)
    return positions

def place_stone_not_aligned(board_size : int, other_stones : list, square_size : int = 5):
    accept = False
    padding = (board_size - square_size) // 2

    while not accept:
        accept = True
        rand_pos = (random.randint(padding,board_size - padding), 
                    random.randint(padding,board_size - padding))
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

    def swap2_first_place_stones(self):    
        raise NotImplementedError()    
    def swap2_second_place_stones(self):
        raise NotImplementedError()
    def swap2_accept_or_place(self):
        raise NotImplementedError()
    def swap2_select_color(self):
        raise NotImplementedError()
    def play_turn(self):
        raise NotImplementedError()
    def get_definition() -> dict:
        raise NotImplementedError() 
    
class AIPlayer(Player):
    def __init__(self,         
                search_depth : int = DEFAULT_SEARCH_DEPTH,
                seed : int = None,
                t_weights : dict = None,
                version : int = 1,
                opening_version : int = 1
                ):

        super().__init__()
        if seed is None:
            self.seed = int(time())
        else:
            self.seed = seed
        self.name = self.__class__.__name__
        self.search_depth = search_depth
        self.version = version
        self.opening_version = opening_version
        self.agg_sdata_coll = {}

        if t_weights is None:
            self.t_weights = {
                'forcing' : 100,
                'nforcing' : 1
            }
        else:
            self.t_weights = t_weights
        random.seed(self.seed)

    def swap2_first_place_stones(self):      
        # global OPENINGS
        # global OPENING_CNT   
        # opening = OPENINGS[OPENING_CNT % len(OPENINGS)]
        # OPENING_CNT+=1
        # b_stone_placements = opening[0]
        # w_stone_placements = opening[1]

        #place the first black stone at random
        if self.opening_version == 1:
            b_stone_placements = []
            b_stone_placements.append((
            random.randint(2,self.game.size - 3), 
            random.randint(2,self.game.size - 3)))
            #then choose to place a second stone so that it does not share a line with the first one
            b_stone_placements.append(place_stone_not_aligned(self.game.size, b_stone_placements))
            #same goes for the white stone
            w_stone_placements = [place_stone_not_aligned(self.game.size, b_stone_placements)]

            self.game.swap2_first_placement(b_stone_placements, w_stone_placements)
        elif self.opening_version == 2:
            b_stone_placements = list()
            b_stone_placements.append((
            random.randint(5,self.game.size - 5), 
            random.randint(5,self.game.size - 5)))

            wstone =list(b_stone_placements[0])
            randx=random.randint(-1,1)
            randy = random.choice([-1,1]) if randx == 0 else random.randint(-1,1)
            wstone[0] += randx
            wstone[1] += randy
            wstone = tuple(wstone)
            w_stone_placements = [wstone]            

            b_stone_placements.append(
                place_stone_not_aligned(
                    self.game.board_state.grid.shape[0],
                    b_stone_placements,
                    square_size=5
                    )
                )
            self.game.swap2_first_placement(b_stone_placements,w_stone_placements)
        else:
            raise Exception(f"Invalid Opening version number({self.opening_version})")

    def swap2_accept_or_place(self):
        bstate = self.game.board_state
        #bl_nft = bstate.b_threats['nforcing'] 
        # for t in bl_nft:
        #     if t.info['type'][0] > 1:
        #         break
        # else:
        #     self.game.swap2_accept_or_place(self,'white')           
        #     return
        
        # self.game.swap2_accept_or_place(self,'place')        
        move,_=gomoku_get_best_move(
            state=bstate,
            maximize=False,
            t_weights=self.t_weights,
            search_depth=self.search_depth,
            version=self.version)            
        bstate.make_move(move,False)
        eval=gomoku_state_static_eval(state=bstate,t_weights=self.t_weights,version=self.version)
        bstate.unmake_last_move()        
    
        if abs(eval) <= 0:
            # for bt in bstate.b_threats['nforcing']: 
            #     for next_bt in B_THREAT_DEP[bt.group]:
            #         next_bt_info = B_THREAT_DATA[next_bt]
            #         if _get_threat_class_from_info(next_bt_info) == 'forcing':
            #             self.game.swap2_accept_or_place('black')
            #             return
            self.game.swap2_accept_or_place(self, 'white')        
        else:             
            self.game.swap2_accept_or_place(self,'black')  

                
    def swap2_second_place_stones(self):     
        bstate = self.game.board_state        
        other_stones = [(m[0],m[1]) for m in bstate.moves]         
        black_stone = place_stone_not_aligned(bstate.size, other_stones)

        other_stones.append(black_stone)

        white_stone = place_stone_not_aligned(bstate.size, other_stones)
        self.game.swap2_second_placement([black_stone], [white_stone])

    def swap2_select_color(self):
        bstate = self.game.board_state
        bl_ft = bstate.b_threats['forcing']        
        if len(bl_ft) > 0:
            self.game.swap2_select_color(self, 'black')
            return

        # state_score = gomoku_state_static_eval(state=bstate,t_weights=self.t_weights,version=self.version)
        # if state_score > 0:
        best_white_move,_ = gomoku_get_best_move(
            state=bstate,
            maximize=False,
            t_weights=self.t_weights,
            search_depth=self.search_depth,                
            version=self.version
            )
        bstate.make_move(best_white_move, False)
        new_state_score = gomoku_state_static_eval(state=bstate,t_weights=self.t_weights,version=self.version)
        bstate.unmake_last_move()
        if new_state_score <= 0:
            self.game.swap2_select_color(self,'white')
            if not self.game.turn(self, best_white_move):
                raise Exception('%s player was supposed to play but couldn\'t.' % (self.color))
        else:
            self.game.swap2_select_color(self,'black')

    def get_definition(self) -> dict:
        return {
            'search_depth' : self.search_depth,
            'version' : self.version,
            'seed' : self.seed
        }

    def play_turn(self):
        if not self.can_play():
            return

        print('ai', self.color,'thinking...')
        maximize = True if self.color == 'black' else False
        best_move,agg_sdata = gomoku_get_best_move(
                                        state=self.game.board_state,
                                        search_depth=self.search_depth,
                                        maximize=maximize,
                                        t_weights=self.t_weights,
                                        version=self.version
                                        )
        
        self.agg_sdata_coll[str((best_move[0],best_move[1],maximize))] = agg_sdata
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
        super(HumanPlayer, self).__init__()
        self.name = self.__class__.__name__
        
        self.swap2_state = {
            'first_pl' : False,
            'second_pl' : False,
            'accept_or_pl' : False,
            'select_col' : False
            }

    def swap2_first_place_stones(self): 
        print('allow first stone placement')   
        for k in self.swap2_state:
            self.swap2_state[k] = False
        self.swap2_state['first_pl'] = True

        self.black_positions = []
        self.white_positions = []

    def swap2_second_place_stones(self):
        for k in self.swap2_state:
            self.swap2_state[k] = False
        self.swap2_state['second_pl'] = True

        self.black_positions = []
        self.white_positions = []

    def swap2_accept_or_place(self):
        for k in self.swap2_state:
            self.swap2_state[k] = False
        self.swap2_state['accept_or_pl'] = True

    def swap2_select_color(self):
        for k in self.swap2_state:
            self.swap2_state[k] = False
        self.swap2_state['select_col'] = True

    def get_definition(self) -> dict:
        return {}

    def on_click_grid(self,x,y,c,r):
        if self.swap2_state['first_pl']:
            if self._stone_placement(2,1,(c,r)):
                self.swap2_state['first_pl'] = False
                self.game.swap2_first_placement(self.black_positions, self.white_positions)
        elif self.swap2_state['second_pl']:
            if self._stone_placement(1,1,(c,r)):
                self.swap2_state['second_pl'] = False
                self.game.swap2_second_placement(self.black_positions, self.white_positions)
        else:
            if self.can_play():
                self.game.turn(self,(c,r))

    def on_button_click(self, text : str):
        if self.swap2_state['select_col']:
            selection = text.lower()
            assert selection in ['white', 'black'], 'Expected \'white\' or \'black\' got %s' % (text) 
            self.game.swap2_select_color(self,selection)
            self.swap2_state['select_col'] = False       
        elif self.swap2_state['accept_or_pl']:
            selection = text.lower()
            assert selection in ['white', 'black','place'], 'Expected [\'white\',\'black\',\'place\'] got %s' % (text) 
            self.game.swap2_accept_or_place(self,selection)
            self.swap2_state['accept_or_pl'] = False
    
    def _stone_placement(self, n_black, n_white, pos) -> bool:
        c,r = pos
        l_b = len(self.black_positions)
        l_w = len(self.white_positions)
        if l_b < n_black:
            if is_valid_move(c,r,self.game.board_state.grid):
                self.black_positions.append((c,r))  
                self.game.board_state.grid[c,r] = 1
                self.game.gui_draw()
                #print('black %d %d'% (c,r))        
        elif l_w < n_white:
            if is_valid_move(c,r,self.game.board_state.grid):
                self.white_positions.append((c,r))      
                self.game.board_state.grid[c,r] = 2
                self.game.gui_draw()
                #print('white %d %d'% (c,r))     

        l_b = len(self.black_positions)
        l_w = len(self.white_positions)

        if l_b == n_black and l_w == n_white:
            self.game.board_state.grid.fill(0)
            return True
        else:
            return False

class ReplayPlayer(Player):
    def __init__(self, match_data : dict, player_id : str):
        super().__init__()        
        self.player_id = player_id
        self.start_color = match_data['player_data'][self.player_id]['start_color']
        self.swap2_data = match_data['swap2_data']
        self.last_move_index = 0

        move_start_index = 5 if 'second_placement' in match_data['swap2_data'] else 3

        self.moves = [(int(m[0]), int(m[1]), bool(m[2])) 
        for m in match_data['moves'][move_start_index:] 
        if not xor(bool(m[2]), self.swap2_data['select_color']['black'] == player_id)]

    def swap2_first_place_stones(self):
        black_positions = [(int(pos[0]), int(pos[1])) 
                            for pos in self.swap2_data['first_placement']['black']]
        white_positions = [(int(pos[0]), int(pos[1])) 
                            for pos in self.swap2_data['first_placement']['white']]
        self.game.swap2_first_placement(black_positions, white_positions)

    def swap2_accept_or_place(self):
        if 'second_placement' in self.swap2_data:
            self.game.swap2_accept_or_place(self,'place')
        else:
            self.swap2_select_color()

    def swap2_second_place_stones(self):
        black_positions = [(int(pos[0]), int(pos[1])) 
                            for pos in self.swap2_data['second_placement']['black']]
        white_positions = [(int(pos[0]), int(pos[1])) 
                            for pos in self.swap2_data['second_placement']['white']]
        self.game.swap2_second_placement(black_positions, white_positions)
    
    def swap2_select_color(self):
        chosen_colors = [self.swap2_data['select_color']['black'],self.swap2_data['select_color']['white']]
        if self.player_id == chosen_colors[0]:
            self.game.swap2_select_color(self, 'black')
        if self.player_id == chosen_colors[1]:
            self.game.swap2_select_color(self, 'white')
        
    def play_turn(self):
        move = self.moves[self.last_move_index]
        move = (move[0], move[1])
        self.last_move_index += 1
        assert self.game.turn(self, move) , 'Expected to play move (%d,%d) but couldn\'t' % (move[0], move[1])
    
    def revert_turn(self):
        self.last_move_index -= 1


if __name__ == '__main__':
    def test_place_not_aligned():
        bsize = 15
        stones = [(7,7)]
        naligned_stones = [place_stone_not_aligned(bsize,stones) for _ in range(100)]

        for s in naligned_stones:
            assert s[0] != s[1]
            assert s[0] != 7
            assert s[1] != 7
            assert s[0] != bsize - 1 - s[1]

    def test_place_not_aligned2():
        bsize = 15
        stones = [(7,7),(3,5)]
        naligned_stones = [place_stone_not_aligned(bsize,stones) for _ in range(100)]        

        for s in naligned_stones:
            assert s[0] != s[1]
            assert s[0] != 7
            assert s[1] != 7
            assert s[0] != bsize - 1 - s[1]

    test_place_not_aligned()
    test_place_not_aligned2()





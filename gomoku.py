from operator import xor

from boardstate import BoardState
from utils import DEFAULT_BOARD_SIZE,is_valid_move, no_moves_possible
from players import Player

class Game:
    def __init__(self, 
                whitePlayer : Player,
                blackPlayer : Player,
                size : int = DEFAULT_BOARD_SIZE):
                
        self.board_state = BoardState(size) 
        self.size = size

        self.on_turn_change_callbacks = []
        self.on_game_end_callbacks = []

        self.black_turn = True          
        self.winning_player = None        

        self.whitePlayer = whitePlayer
        self.whitePlayer.game = self
        # self.whitePlayer.color = "white"

        self.blackPlayer = blackPlayer
        self.blackPlayer.game = self
        # self.blackPlayer.color = "black"

        self.gui = None
        self.swap2_phase = True
        self.swap2_state = {
        "first_placement" : True,
        "accept_or_place" : False ,
        "second_placement" : False,
        "select_color" : False}
        self.swap2_data = {}

    def add_turn_change_callback(self, func):
        self.on_turn_change_callbacks.append(func)
    
    def add_game_end_callback(self, func):
        self.on_game_end_callbacks.append(func)

    def gui_draw(self):
        if self.gui is not None:
            self.gui.draw()

    def skip_swap2(self):
        self.swap2_phase = False
        self.blackPlayer.assign_color('black')
        self.whitePlayer.assign_color('white')

    def pass_move(self):
        self.black_turn = not self.black_turn
        self.draw()

    def swap2_init(self):
        self.swap2_data = {}
        self.blackPlayer.swap2_first_place_stones()

    def swap2_first_placement(self, black_positions : list = [], white_positions : list = []):
        n_stones = len(white_positions) + len(black_positions)
        if n_stones  != 3:
            raise Exception("Incorrect number of stones in first placement. Expected 3 got %d" % (n_stones))

        if not self.place_stones(black_positions,True):
            return
        if not self.place_stones(white_positions,False):
            return

        self.swap2_state["first_placement"] = False
        self.swap2_state["accept_or_place"] = True
        self.gui_draw()

        self.swap2_data['first_placement'] = {
            'black' : black_positions,
            'white' : white_positions 
        }

        self.whitePlayer.swap2_accept_or_place()

    def swap2_accept_or_place(self, player, choice):
        if choice == "white" or choice == "black":            
            self.swap2_select_color(player,choice)
            self.swap2_state["accept_or_place"] = False
        else:          
            self.swap2_state["accept_or_place"] = False
            self.swap2_state["second_placement"] = True
            self.gui_draw()
            player.swap2_second_place_stones()
        
    def swap2_second_placement(self, black_positions : list = None, white_positions: list = None):
        n_stones = len(white_positions) + len(black_positions)
        if n_stones  != 2:
            raise Exception("Incorrect number of stones in first placement. Expected 2 got %d" % (n_stones))
        if not self.place_stones(black_positions,True):
            return
        if not self.place_stones(white_positions,False):
            return
        self.swap2_state["second_placement"] = False
        self.swap2_state["select_color"] = True

        self.swap2_data['second_placement'] = {
            'black' : black_positions,
            'white' : white_positions 
        }

        self.gui_draw()
        self.blackPlayer.swap2_select_color()

    def swap2_select_color(self, player, choice):
        other = self.whitePlayer if player == self.blackPlayer else self.blackPlayer
        self.swap2_state["select_color"] = False
        if choice == "white":
            self.whitePlayer = player
            self.blackPlayer = other                    
        elif choice == "black":
            self.whitePlayer = other
            self.blackPlayer = player
        
        self.swap2_data['select_color'] = {
            'black' : self.blackPlayer.name,
            'white' : self.whitePlayer.name
        }    

        self.blackPlayer.assign_color('black')
        self.whitePlayer.assign_color('white')

        self.swap2_end()                    
        self.gui_draw()

    def swap2_end(self):
        #print('swap2 phase end.')
        self.new_turn()
        self.swap2_phase = False        
        self.gui_draw()
        
    def place_stone(self,move,black) -> bool:    
        if not is_valid_move(*move, self.board_state.grid):            
            return False
        # update board array
        self.board_state.make_move(move,black)
        self.gui_draw()
        return True

    def place_stones(self, positions : list, black: bool) -> bool:
        for pos in positions:
            if not is_valid_move(*pos, self.board_state.grid):
                return False
  
        for pos in positions:
            self.board_state.make_move(pos, black)
        
        self.gui_draw()
        return True

    def turn(self, player, move) -> bool:
        if self.winning_player is not None:
            return False

        player_black = player == self.blackPlayer
        if xor(player_black, self.black_turn):
            return False

        if self.place_stone(move,self.black_turn):
            #if check_winning_condition(self.board_state.grid, move, player.color):
            if check_winning_condition(self):
                self.winning_player = player.color
                for cback in self.on_game_end_callbacks:
                    cback()
            self.new_turn()
            self.gui_draw()
            return True
        return False

    def revert_turn(self):
        self.board_state.unmake_last_move()
        self.winning_player = None
        self.new_turn()
        self.gui_draw()   

    def new_turn(self):
        self.black_turn = not self.black_turn
        for cback in self.on_turn_change_callbacks:
            cback()     

def check_winning_condition(game : Game):
    if len(game.board_state.b_threats['winning']) > 0 or len(game.board_state.w_threats['winning']) > 0:
        return True
    elif no_moves_possible(game.board_state.grid):
        return True
    return False



# def check_line(board, last_move, last_player, direction):
#     c,r = last_move
#     r1 = r
#     c1 = c
#     stone = 1 if last_player == "black" else 2
#     count = 1
#     while board[c1,r1] == stone:
#         r1 -= direction[0]
#         c1 -= direction[1]

#         if r1 < 0 or r1 >= board.shape[1]:
#             break
#         if c1 < 0 or c1 >= board.shape[0]:
#             break    
        
#         if board[c1,r1] == stone:            
#             count += 1

#     r1 = r
#     c1 = c
#     while board[c1,r1] == stone:
#         r1 += direction[0]
#         c1 += direction[1]

#         if r1 < 0 or r1 >= board.shape[1]:
#             break
#         if c1 < 0 or c1 >= board.shape[0]:
#             break    

#         if board[c1,r1] == stone:
#             count += 1
    
#     return count

# def check_winning_condition(board, last_move, last_player):
#     count_hor = check_line(board, last_move,last_player, (0,1))
#     count_ver = check_line(board, last_move,last_player, (1,0))
#     count_diag = check_line(board, last_move,last_player, (1,1))
#     count_diag1 = check_line(board, last_move,last_player, (-1,1))

#     if count_hor == 5 or count_ver == 5 or count_diag == 5 or count_diag1 == 5:
#         return True
    
#     return False

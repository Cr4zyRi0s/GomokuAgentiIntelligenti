from operator import xor
import numpy as np

from boardstate import BoardState




def check_line(board, last_move, last_player, direction):
    c,r = last_move
    r1 = r
    c1 = c
    stone = 1 if last_player == "black" else 2
    count = 1
    while board[c1,r1] == stone:
        r1 -= direction[0]
        c1 -= direction[1]

        if r1 < 0 or r1 >= board.shape[1]:
            break
        if c1 < 0 or c1 >= board.shape[0]:
            break    
        
        if board[c1,r1] == stone:            
            count += 1

    r1 = r
    c1 = c
    while board[c1,r1] == stone:
        r1 += direction[0]
        c1 += direction[1]

        if r1 < 0 or r1 >= board.shape[1]:
            break
        if c1 < 0 or c1 >= board.shape[0]:
            break    

        if board[c1,r1] == stone:
            count += 1
    
    return count

def check_winning_condition(board, last_move, last_player):
    count_hor = check_line(board, last_move,last_player, (0,1))
    count_ver = check_line(board, last_move,last_player, (1,0))
    count_diag = check_line(board, last_move,last_player, (1,1))
    count_diag1 = check_line(board, last_move,last_player, (-1,1))

    #print(count_hor, count_ver, count_diag, count_diag1)

    if count_hor == 5 or count_ver == 5 or count_diag == 5 or count_diag1 == 5:
        return True
    
    return False

def no_moves_possible(board : np.array) -> bool:
    n_avail = np.count_nonzero(board)
    return n_avail > 0

def is_valid_move(col : int, row : int, board : np.array) -> bool:
    """Check if placing a stone at (col, row) is valid on board
    Args:
        col (int): column number
        row (int): row number
        board (object): board grid (size * size matrix)
    Returns:
        boolean: True if move is valid, False otherewise
    """
    # TODO: check for ko situation (infinite back and forth)
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False    
    return board[col, row] == 0


class Game:
    def __init__(self, size, whitePlayer, blackPlayer):
        #self.board = np.zeros((size, size))
        self.board_state = BoardState(size) 
        self.size = size

        self.black_turn = True          
        self.winning_player = None        

        self.whitePlayer = whitePlayer
        self.whitePlayer.game = self
        self.whitePlayer.color = "white"

        self.blackPlayer = blackPlayer
        self.blackPlayer.game = self
        self.blackPlayer.color = "black"

        self.gui = None
        self.swap2_phase = True
        self.swap2_state = {
        "first_placement" : True,
        "accept_or_place" : False ,
        "second_placement" : False,
        "select_color" : False}

    def pass_move(self):
        self.black_turn = not self.black_turn
        self.draw()

    def swap2_init(self):
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
        self.gui.draw()
        self.whitePlayer.swap2_accept_or_place()

    def swap2_accept_or_place(self, player, choice):
        if choice == "white" or choice == "black":            
            self.swap2_select_color(player,choice)
            self.swap2_state["accept_or_place"] = False
        else:          
            self.swap2_state["accept_or_place"] = False
            self.swap2_state["second_placement"] = True
            self.gui.draw()
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
        self.gui.draw()
        self.blackPlayer.swap2_select_color()

    def swap2_select_color(self, player, choice):
        other = self.whitePlayer if player == self.blackPlayer else self.blackPlayer
        self.swap2_state["select_color"] = False
        if choice == "white":
            self.whitePlayer = player
            self.blackPlayer = other
            self.swap2_end()
        elif choice == "black":
            self.whitePlayer = other
            self.blackPlayer = player
            self.swap2_end()
        self.gui.draw()

    def swap2_end(self):
        self.new_turn()
        self.swap2_phase = False        
        self.gui.draw()
        
    def place_stone(self,move,black) -> bool:    
        if not is_valid_move(*move, self.board_state.grid):            
            return False
        # update board array
        self.board_state.make_move(move,black)
        if self.gui is not None:
            self.gui.draw()
        return True

    def place_stones(self, positions : list, black: bool) -> bool:
        for pos in positions:
            if not is_valid_move(*pos, self.board_state.grid):
                return False
  
        for pos in positions:
            self.board_state.make_move(pos, black)
        
        if self.gui is not None:
            self.gui.draw()
        return True

    def turn(self, player, move) -> bool:
        if self.winning_player is not None:
            return False

        player_black = player == self.blackPlayer
        if xor(player_black, self.black_turn):
            return False
        if self.place_stone(move,self.black_turn):
            if check_winning_condition(self.board_state.grid, move, player.color):
                self.winning_player = player.color
                if self.gui is not None:
                    self.gui.draw()
                return True
            self.new_turn()
            return True
        return False

    def new_turn(self):
        self.black_turn = not self.black_turn      
        '''  
        if self.black_turn:
            self.blackPlayer.play_turn()
        else:
            self.whitePlayer.play_turn()
        '''
    
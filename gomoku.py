from tkinter.tix import DirTree
import numpy as np


def is_valid_move(col, row, board):
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
        self.board = np.zeros((size, size))        
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

    def swap2_first_placement(self, black_positions : list, white_positions : list):       
        for bpos in black_positions:
            if not self.place_stone(bpos, True):
                return     
        for wpos in white_positions:
            if not self.place_stone(wpos, False):
                return 
        self.swap2_state["first_placement"] = False
        self.swap2_state["accept_or_place"] = True
        self.gui.draw()
        self.whitePlayer.swap2_accept_or_place()

    def swap2_accept_or_place(self, player, choice):
        if choice == "white" or choice == "black":            
            self.swap2_select_color(player,choice)
        else:          
            self.swap2_state["accept_or_place"] = False
            self.swap2_state["second_placement"] = True
            self.gui.draw()
            player.swap2_second_place_stones()
        
    def swap2_second_placement(self, black_position : tuple, white_position: tuple):
        self.place_stone(black_position, True)
        self.place_stone(white_position, False)        
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
        self.black_turn = False
        self.swap2_phase = False
        self.gui.draw()
        
    def place_stone(self,move,black):
        c,r = move        
        if not is_valid_move(c, r, self.board):            
            return False
        # update board array
        self.board[c,r] = 1 if black else 2
        if self.gui is not None:
            self.gui.draw()
        return True

    '''
    def handle_click(self):
        if self.winning_player is not None:
            return        

        if self.swap2_phase:
            self.swap2((col,row))

        if not self.place_stone((col,row)):
           return

        # get stone groups for black and white
        self_color = "black" if self.black_turn else "white"
        
        if self.check_winning_condition((row,col),self_color):
            print("%s player won." % (self_color))
            self.winning_player = self_color

        # change turns and draw screen
        self.CLICK.play()                
        self.black_turn = not self.black_turn
        self.draw()
    '''       
    '''

''' 

    def check_winning_condition(self, last_move, last_player):
        count_hor = self.check_line(last_move,last_player, (0,1))
        count_ver = self.check_line(last_move,last_player, (1,0))
        count_diag = self.check_line(last_move,last_player, (1,1))
        count_diag1 = self.check_line(last_move,last_player, (-1,1))

        if count_hor == 5 or count_ver == 5 or count_diag == 5 or count_diag1 == 5:
            return True
        
        return False

    
    def check_line(self, last_move, last_player, direction):
        r,c = last_move
        r1 = r
        c1 = c
        stone = 1 if last_player == "black" else 2
        count = 1
        while self.board[c1,r1] == stone:
            r1 -= direction[0]
            c1 -= direction[1]

            if r1 < 0 or r1 >= self.board.shape[1]:
                break
            if c1 < 0 or c1 >= self.board.shape[0]:
                break    
            
            if self.board[c1,r1] == stone:            
                count += 1

        r1 = r
        c1 = c
        while self.board[c1,r1] == stone:
            r1 += direction[0]
            c1 += direction[1]

            if r1 < 0 or r1 >= self.board.shape[1]:
                break
            if c1 < 0 or c1 >= self.board.shape[0]:
                break    

            if self.board[c1,r1] == stone:
                count += 1
        
        return count
    
   


        '''
        if "bs_placed2" not in self.swap2_state.keys():
            self.swap2_state["bs_placed2"] = 0
        if "ws_placed2" not in self.swap2_state.keys():
            self.swap2_state["ws_placed2"] = 0    

        if self.swap2_state["ws_placed2"] < 1:
            if self.place_stone(move,black = True):        
                self.swap2_state["ws_placed2"] += 1
        elif self.swap2_state["bs_placed2"] < 1:
            if self.place_stone(move,black = False):
                self.swap2_state["bs_placed2"] += 1
                self.swap2_end()   
        '''


        '''        
        c,r = move        

        if "bs_placed1" not in self.swap2_state.keys():
            self.swap2_state["bs_placed1"] = 0
        if "ws_placed1" not in self.swap2_state.keys():
            self.swap2_state["ws_placed1"] = 0        

        if self.swap2_state["bs_placed1"] < 2:
            if self.place_stone(move,black = True):        
                self.swap2_state["bs_placed1"] += 1
        elif self.swap2_state["ws_placed1"] < 1:
            if self.place_stone(move,black = False):
                self.swap2_state["ws_placed1"] += 1   
                self.swap2_state["first_done"] = True 
        '''
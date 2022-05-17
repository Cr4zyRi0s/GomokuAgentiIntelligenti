from gomoku import Game

class Player:
    def __init__(self):
        self.game = None
        self.color = None
        self.first_placement = False    
        self.accept_or_place = False
        self.second_placement = False
        self.select_color = False

    def notify_turn(self):
        pass           

    def swap2_first_place_stones(self) -> list:    
        pass
    
    def swap2_second_place_stones(self) -> list:
        pass

    def swap2_accept_or_place(self) -> str:
        pass

    def swap2_select_color(self) -> str:
        pass

    def play_turn(self, col, row):
        pass

    def set_color(self, color):
        pass    
    
class AIPlayer(Player):    
    pass

class HumanPlayer(Player):
    def swap2_first_place_stones(self):    
        self.first_placement = True
        self.black_stones_placed = 0
        self.white_stones_placed = 0

    def swap2_second_place_stones(self):
        self.first_placement = True

    def swap2_accept_or_place(self) -> str:
        pass

    def swap2_select_color(self) -> str:
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
                    self.game.swap2_first_placement([], [])
        elif self.second_placement:
            if self.black_stones_placed < 1:
                if self.game.place_stone((c,r),True):
                    self.black_stones_placed += 1               
            elif self.white_stones_placed < 1:
                if self.game.place_stone((c,r),False):
                    self.white_stones_placed += 1
                    self.second_placement = False
                    self.game.swap2_second_placement([], [])
    
    def on_button_click(self, text):
        print(text)

        




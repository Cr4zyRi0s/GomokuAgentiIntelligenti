from fileinput import filename
import os

from typing import List
from players import Player
from gomoku import Game
from gui import GUIHandler

class Match:
    def __init__(self, 
                playerBlack : Player,
                playerWhite : Player,
                gui_enabled = True,
                save_match_data : bool = False,                
                match_id : str = 'match',
                tags : List[str]  = []):

        self.playerBlack = playerBlack
        self.playerWhite = playerWhite        
        self.gui_enabled = gui_enabled
        self.save_match_data = save_match_data
        self.match_id = match_id

        self.game = Game(self.playerWhite, self.playerBlack)
        if self.gui_enabled:
            self.gui = GUIHandler(self.game)
            self.game.gui = self.gui                       
            self.gui.init_pygame()
            self.gui.clear_screen()
            self.gui.draw()

        if self.save_match_data:
            self.game.add_game_end_callback(self.save_match)
    
    def update(self):  
        self.gui.update()  

    def save_match(self):        
        filename_parts = [self.match_id]
        

        path = os.path.join('match_data', filename)


if __name__ == '__main__':
    pass
        






        

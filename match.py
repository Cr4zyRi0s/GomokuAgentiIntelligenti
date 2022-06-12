import os
import json
from time import time

from typing import List
from boardstate import BoardState
from players import Player
from gomoku import Game
from gui import GUIHandler

last_time = time()

class Match:
    def __init__(self, 
                playerBlack : Player,
                playerWhite : Player,
                gui_enabled = True,
                save_match_data : bool = False,                
                match_id : str = 'match',
                skip_swap2 : bool = False,
                tags : List[str]  = []):

        self.playerBlack = playerBlack
        self.playerWhite = playerWhite        
        self.gui_enabled = gui_enabled
        self.save_match_data = save_match_data
        self.match_id = match_id
        self.tags = tags
        
        self.move_data = {}

        self.game = Game(self.playerWhite, self.playerBlack)
        if skip_swap2:
            self.game.skip_swap2()
        else:
            self.game.swap2_init()
        if self.gui_enabled:
            self.gui = GUIHandler(self.game)
            self.game.gui = self.gui                       
            self.gui.init_pygame()
            self.gui.clear_screen()
            self.gui.draw()

        if self.save_match_data:
            self.game.add_turn_change_callback(self._update_move_data)
            self.game.add_game_end_callback(self.save_match)
    
    def update(self):  
        self.gui.update()  

    def save_match(self):        
        filename_parts = [self.match_id, self.game.blackPlayer.name, self.game.whitePlayer.name]
        filename_parts.extend(self.tags)
        filename = '_'.join(filename_parts)
        path = 'match_data'

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                pass
            
        filelist = os.listdir(path)
        instances = [int(fn.split('.')[0].split('_')[-1]) for fn in filelist if fn.startswith(filename)]
        if len(instances) > 0:
            last_index = max(instances)
        else:
            last_index = 0

        filename = '_'.join([filename,str(last_index + 1)]) + '.json'
        full_path = os.path.join(path, filename)

        with open(full_path, 'w') as file:
            json.dump({
            'swap2_data' : self.game.swap2_data,
            'moves' : self.game.board_state.moves,
            'move_data' : self.move_data
            }
            ,file)

    def _update_move_data(self):
        global last_time

        curr_time = time()     
        bstate = self.game.board_state
        moves = bstate.moves
        last_move = moves[-1]
        self.move_data[str(last_move)] = {}
        if len(moves) == 1:
            self.move_data[str(last_move)]['time'] = 0.0
        else:
            self.move_data[str(last_move)]['time'] = round(curr_time - last_time,4) 
        self.move_data[str(last_move)]['n_bthreats'] = (
            len(bstate.b_threats['nforcing']),
            len(bstate.b_threats['forcing']),
            len(bstate.b_threats['winning'])
        )
        self.move_data[str(last_move)]['n_wthreats'] = (
            len(bstate.w_threats['nforcing']),
            len(bstate.w_threats['forcing']),
            len(bstate.w_threats['winning'])
        )            
        last_time = time()
                    
if __name__ == '__main__':
    pass

        






        

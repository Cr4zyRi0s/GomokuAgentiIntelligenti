import os
import json

from time import time,sleep
from typing import List
from boardstate import BoardState
from players import Player, ReplayPlayer
from gomoku import Game
from gui import GUIHandler
from utils import generate_random_string

last_time = time()

class Match:
    def __init__(self, 
                playerBlack : Player,
                playerWhite : Player,
                gui_enabled = True,
                save_match_data : bool = False,
                match_data_path : str = 'match_data',                
                match_id : str = 'match',
                skip_swap2 : bool = False,
                tags : List[str]  = []):

        self.playerBlack = playerBlack
        self.playerWhite = playerWhite        

        if self.playerBlack.name == self.playerWhite.name:
            rand_str_bl = generate_random_string(5)
            rand_str_wh = generate_random_string(5)
            while rand_str_bl == rand_str_wh:
                rand_str_bl = generate_random_string(5)
                rand_str_wh = generate_random_string(5)
            self.playerBlack.name = '_'.join([self.playerBlack.name,rand_str_bl])
            self.playerWhite.name = '_'.join([self.playerWhite.name,rand_str_wh])


        self.gui_enabled = gui_enabled
        self.match_id = match_id
        self.tags = tags

        self.game = Game(self.playerWhite, self.playerBlack)

        if save_match_data:
            self.save_match_data = save_match_data
            self.match_data_path = match_data_path
            self.player_data = {
                self.playerBlack.name : {
                    'start_color' : 'black',  
                    'def' : self.playerBlack.get_definition()
                },
                self.playerWhite.name : {
                    'start_color' : 'white',  
                    'def' : self.playerWhite.get_definition()
                }
            }                    
            self.move_data = {}
            self.game.add_turn_change_callback(self._update_move_data)
            self.game.add_game_end_callback(self.save_match)
    
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

    
    def update(self):          
        self.gui.update()  

    def save_match(self):        
        filename_parts = [self.match_id]
        filename_parts.extend(self.tags)
        filename = '_'.join(filename_parts)
        path = self.match_data_path

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
            'player_data' : self.player_data,
            'swap2_data' : self.game.swap2_data,
            'winner' : self.game.winning_player,
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

class ReplayMatch(Match):
    def __init__(self, match_data_path : str):
        with open(match_data_path,'r') as file:
            data = json.load(file)
        
        ids = list(data['player_data'].keys())
        player1_id = ids[0]
        player2_id = ids[1]

        self.player1 = ReplayPlayer(data, player1_id)
        self.player2 = ReplayPlayer(data, player2_id)
        
        p_b,p_w = (self.player1,self.player2) if self.player1.start_color == 'black' else  (self.player2,self.player1)
        self.game = Game(p_b, p_w)
        self.gui = GUIHandler(self.game)
        self.game.gui = self.gui                       
        self.gui.init_pygame()
        self.gui.clear_screen()
        self.gui.draw()

        self.game.swap2_init()

        advance_turn = lambda x,y : p_b.play_turn() if self.game.black_turn else p_w.play_turn()
        self.gui.add_on_click_callback(advance_turn)
        

if __name__ == '__main__':
    #Codice di esempio per visualizzare il replay di una partita
    #Per eseguire i turni basta semplicemente cliccare in un punto qualsiasi all'interno della 
    #finestra
    replay = ReplayMatch('experiments\experiment-test3\match_ai_sd2_bl_ai_sd2_wh_1.json')
    while True:
        replay.update()
        sleep(0.1)

        






        

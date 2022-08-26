from boardstate import BoardState
from match import Match, draw_threat_hints
from gomoku import Game,check_winning_condition
from gui import  xy_to_colrow
from players import AIPlayer, AIRandomPlayer, HumanPlayer
from boardstate import FORCING_THREAT_TYPES

import pygame
import re

last_move = (0,0)

def print_threats_of_player(game : Game, black : bool):
    for type, ts in game.board_state.b_threats.items() if black else game.board_state.w_threats.items():
        if type == 'forcing':
            for t in ts:
                print(t)
    print('-------------------\n')

def update_last_move(x,y):
    global last_move     
    last_move = xy_to_colrow(x,y,15)

def print_lines_of_last_moves(game : Game):
    global last_move
    if game.black_turn:
        _, line = game.board_state._get_line(last_move)
        _, line45 = game.board_state._get_line45(last_move)
        _, line90 = game.board_state._get_line90(last_move)
        _, line315 = game.board_state._get_line315(last_move)

        print('0°:\t', str(list(re.finditer('[01]{5,}',line))))
        print('45°:\t',str(list(re.finditer('[01]{5,}',line45))))
        print('90°:\t',str(list(re.finditer('[01]{5,}',line90))))
        print('315°:\t',str(list(re.finditer('[01]{5,}',line315))),'\n',line315)    
        print('-------------------\n')    

def ai_play(game: Game):
    if check_winning_condition(game):
        return
    if isinstance(game.blackPlayer,AIPlayer) and game.black_turn:
        game.blackPlayer.play_turn()
    elif isinstance(game.whitePlayer, AIPlayer) and not game.black_turn:
        game.whitePlayer.play_turn()

if __name__ == "__main__":
    ai_white = AIPlayer(search_depth=4)
    ai_black = AIRandomPlayer()
    human  = HumanPlayer()

    match = Match(human,ai_white,save_match_data=True)
    
    update_threat_hints = lambda: draw_threat_hints(match.game,match.gui)
    match.game.add_turn_change_callback(update_threat_hints)
        
    while True:        
        match.update()
        ai_play(match.game)
        pygame.time.wait(100)
        
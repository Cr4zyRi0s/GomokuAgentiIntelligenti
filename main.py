from threading import Thread
from time import sleep
from match import Match
from gomoku import Game,check_winning_condition
from gui import GUIHandler, xy_to_colrow
from players import AIPlayer, AIRandomPlayer, HumanPlayer
import pygame

from boardstate import get_index_transform_func
import re

last_move = (0,0)

def draw_threats_for_player(game : Game, gui : GUIHandler, black : bool):
    pthreats = game.board_state.b_threats if black else game.board_state.w_threats
    for lvl, ts in pthreats.items():    
        for t in ts:
            if lvl == 5:
                trans_func = get_index_transform_func(t.angle)
                gui.add_winning_streak_line(trans_func(t.span[0]), trans_func(t.span[1] - 1))
            else:
                t_lvl = t.info['type'][0]          
                if t_lvl >= 3:
                    for s in t.get_open_slots():                                  
                        gui.add_threat_hint(*s,t_lvl)

def draw_threat_hints(game : Game, gui : GUIHandler):
    gui.reset_threat_hints()
    draw_threats_for_player(game,gui,True)
    draw_threats_for_player(game,gui,False)

def print_threats_of_player(game : Game, black : bool):
    for type, ts in game.board_state.b_threats.items() if black else game.board_state.w_threats.items():
        print('\n\n',type,'\n----------------')
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
    ai_white = AIPlayer()
    ai_black = AIRandomPlayer()
    human  = HumanPlayer()

    match = Match(human,ai_white,save_match_data=True)
    
    update_threat_hints = lambda: draw_threat_hints(match.game,match.gui)
    match.game.add_turn_change_callback(update_threat_hints)

    #ai_play_lambda = lambda x,y: ai_play(match.game)
    #ai_play_lambda2 = lambda : ai_play(match.game)
    #match.gui.add_on_click_callback(ai_play_lambda)
    #match.game.add_turn_change_callback(ai_play_lambda2)
    #draw_thread = Thread(target = lambda : draw_loop(match.gui))
    #draw_thread.start()

    #play_thread = Thread(target = ai_play_lambda)
        
    while True:        
        match.update()
        ai_play(match.game)
        pygame.time.wait(500)
        
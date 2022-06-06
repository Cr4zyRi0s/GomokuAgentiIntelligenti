from gomoku import Game
from gui import GUIHandler, xy_to_colrow
from players import AIPlayer, AIRandomPlayer, HumanPlayer
import pygame

from boardstate import get_index_transform_func
from threats import Threat

import re

PERIOD = 20
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

if __name__ == "__main__":
    ai_white = AIRandomPlayer()
    #ai_black = AIPlayer()
    human  = HumanPlayer()
    game = Game(whitePlayer=ai_white, blackPlayer=human)    
    gui = GUIHandler(game, [])
    game.gui = gui
    game.skip_swap2()

    gui.init_pygame()
    gui.clear_screen()
    gui.draw()

    update_threat_hints = lambda: draw_threat_hints(game,gui) 
    game.on_turn_change_callbacks.append(update_threat_hints)
    
    ai_white_play = lambda: ai_white.play_turn()
    game.on_turn_change_callbacks.append(ai_white_play)

    # print_threats = lambda: print_threats_of_player(game,True)
    # game.on_turn_change_callbacks.append(print_threats)

    gui.on_click_callbacks.append(update_last_move)

    pllm = lambda : print_lines_of_last_moves(game)
    game.on_turn_change_callbacks.append(pllm)

    #game.swap2_init()
    #one_turn_ahead = lambda x,y : ai_white.play_turn() if not game.black_turn else ai_black.play_turn()
    #gui.add_on_click_callback(one_turn_ahead)
    timer = 0
    while True:    
        gui.update()
        pygame.time.wait(100)
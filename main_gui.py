from gomoku import Game
from gui import GUIHandler
from players import AIPlayer, AIRandomPlayer, HumanPlayer
import pygame
import random

from boardstate import get_index_transform_func
from threats import Threat

MOVE_TIME = 15

def draw_threats_for_player(game : Game, gui : GUIHandler, black : bool):
    pthreats = game.board_state.b_threats if black else game.board_state.w_threats
    for lvl, ts in pthreats.items():    
        for t in ts:
            if lvl == 5:
                trans_func = get_index_transform_func(t.angle)
                gui.add_winning_streak_line(trans_func(t.span[0]), trans_func(t.span[1] - 1))
            else:
                for s in t.get_open_slots():                    
                    gui.add_threat_hint(*s,t.info['type'][0])


def draw_threat_hints(game : Game, gui : GUIHandler):
    draw_threats_for_player(game,gui,True)
    draw_threats_for_player(game,gui,False)

if __name__ == "__main__":
    ai_white = AIRandomPlayer()
    #ai_black = AIPlayer()
    human  = HumanPlayer()
    game = Game(size=15, whitePlayer=ai_white, blackPlayer=human)    
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

    print_threats = lambda: print('black threats:', game.board_state.b_threats)
    game.on_turn_change_callbacks.append(print_threats)
    #game.swap2_init()
    #one_turn_ahead = lambda x,y : ai_white.play_turn() if not game.black_turn else ai_black.play_turn()
    #gui.add_on_click_callback(one_turn_ahead)
    while True:    
        gui.update()
        pygame.time.wait(100)


    '''
    for j in range(game.board_state.grid.shape[1]):
        for i in range(game.board_state.grid.shape[0]):
            rand = random.randint(1,3)
            if rand > 1:
                if rand == 2:
                    game.board_state.make_move((j,i), True)
                else:
                    game.board_state.make_move((j,i), False)

    '''
    '''
    game.board_state.make_move((0,1),True)
    game.board_state.make_move((0,2),True)
    game.board_state.make_move((0,3),True)
    game.board_state.make_move((0,4),True)
    
    game.board_state.make_move((2,2),True)
    game.board_state.make_move((3,3),True)
    game.board_state.make_move((4,4),True)
    game.board_state.make_move((5,5),True)
    
    game.board_state.make_move((5,10),True)
    game.board_state.make_move((6,10),True)
    game.board_state.make_move((7,10),True)
    game.board_state.make_move((8,10),True)
    '''
    '''
    w_t,f_t,nf_t = game.board_state.get_current_threats((0,0), True)

    for lvl,ts in w_t.items():
        for t in ts:
            gui.add_winning_streak_line((t.cells[0], t.cells[-1]))
    
    for lvl,ts in f_t.items():
        for t in ts:
            for s in t.get_open_slots():
                gui.add_threat_hint(*s,2)
    
    for lvl,ts in nf_t.items():
        for t in ts:
            for s in t.get_open_slots():
                gui.add_threat_hint(*s,1)
    '''
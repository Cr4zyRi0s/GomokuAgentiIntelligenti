from gomoku import Game
from gui import GUIHandler
from players import AIPlayer, HumanPlayer
import pygame
import random

MOVE_TIME = 15

if __name__ == "__main__":
    ai_white = AIPlayer()
    ai_black = AIPlayer()
    #human  = HumanPlayer()
    game = Game(size=15, whitePlayer=ai_white, blackPlayer=ai_black)    
    gui = GUIHandler(game, [])
    game.gui = gui
    
    print(game.board_state.grid.shape)

    for j in range(game.board_state.grid.shape[1]):
        for i in range(game.board_state.grid.shape[0]):
            rand = random.randint(1,3)
            if rand > 1:
                if rand == 2:
                    game.board_state.make_move((j,i), True)
                else:
                    game.board_state.make_move((j,i), False)

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

    gui.init_pygame()
    gui.clear_screen()
    gui.draw()

    #game.swap2_init()

    one_turn_ahead = lambda x,y : ai_white.play_turn() if not game.black_turn else ai_black.play_turn()
    #gui.add_on_click_callback(one_turn_ahead)

    while True:    
        gui.update()
        pygame.time.wait(100)
        
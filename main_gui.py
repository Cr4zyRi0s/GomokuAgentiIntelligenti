from gomoku import Game
from gui import GUIHandler
from players import AIPlayer, HumanPlayer
import pygame

MOVE_TIME = 15

if __name__ == "__main__":
    ai_white = AIPlayer()
    ai_black = AIPlayer()
    #human  = HumanPlayer()
    game = Game(size=15, whitePlayer=ai_white, blackPlayer=ai_black)    
    gui = GUIHandler(game, [])
    game.gui = gui

    gui.init_pygame()
    gui.clear_screen()
    gui.draw()

    game.swap2_init()

    cnt = 0
    
    while True:    
        cnt += 1
        if cnt >= MOVE_TIME:            
            ai_white.play_turn()            
            ai_black.play_turn()
            cnt = 0
        gui.update()
        pygame.time.wait(100)
        
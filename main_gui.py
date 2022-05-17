from gomoku import Game
from gui import GUIHandler
from players import AIPlayer, HumanPlayer
import pygame

if __name__ == "__main__":
    ai = AIPlayer()
    human  = HumanPlayer()
    game = Game(size=15, whitePlayer=ai, blackPlayer=human)    
    gui = GUIHandler(game, [human])
    game.gui = gui

    game.swap2_init()

    gui.init_pygame()
    gui.clear_screen()
    gui.draw()

    while True:
        gui.update()
        pygame.time.wait(100)
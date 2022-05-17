from gomoku import Game
import pygame

if __name__ == "__main__":
    g = Game(size=15)
    g.init_pygame()
    g.clear_screen()
    g.draw()

    while True:
        g.update()
        pygame.time.wait(100)
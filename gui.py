from platform import python_branch
from pyparsing import White
from gomoku import Game
from pygame import gfxdraw
import pygame
import sys
import itertools
import numpy as np

from players import HumanPlayer
from pygamebutton import Button

THREAT_COLORS = {
    1 : (0, 255, 0),
    2 : (128,255,0),
    3 : (255, 255, 0),
    4 : (255,128,0),
    5 : (255,0,0)
}
BOARD_BROWN = (199, 105, 42)
BOARD_WIDTH = 1000
BOARD_BORDER = 150
STONE_RADIUS = 22
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TURN_POS = (int(BOARD_BORDER / 2.0), int(BOARD_BORDER / 2.0))
WIN_POS = (int(BOARD_BORDER / 2.0), BOARD_WIDTH - BOARD_BORDER + 30 )

DOT_RADIUS = 4

def xy_to_colrow(x, y, size):
    """Convert x,y coordinates to column and row number
    Args:
        x (float): x position
        y (float): y position
        size (int): size of grid
    Returns:
        Tuple[int, int]: column and row numbers of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x_dist = x - BOARD_BORDER
    y_dist = y - BOARD_BORDER
    col = int(round(x_dist / inc))
    row = int(round(y_dist / inc))
    return col, row


def colrow_to_xy(col, row, size):
    """Convert column and row numbers to x,y coordinates
    Args:
        col (int): column number (horizontal position)
        row (int): row number (vertical position)
        size (int): size of grid
    Returns:
        Tuple[float, float]: x,y coordinates of intersection
    """
    inc = (BOARD_WIDTH - 2 * BOARD_BORDER) / (size - 1)
    x = int(BOARD_BORDER + col * inc)
    y = int(BOARD_BORDER + row * inc)
    return x, y

def make_grid(size):
    """Return list of (start_point, end_point pairs) defining gridlines
    Args:
        size (int): size of grid
    Returns:
        Tuple[List[Tuple[float, float]]]: start and end points for gridlines
    """
    start_points, end_points = [], []

    # vertical start points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_BORDER)
    start_points += list(zip(xs, ys))

    # horizontal start points (constant x)
    xs = np.full((size), BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    start_points += list(zip(xs, ys))

    # vertical end points (constant y)
    xs = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    ys = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    end_points += list(zip(xs, ys))

    # horizontal end points (constant x)
    xs = np.full((size), BOARD_WIDTH - BOARD_BORDER)
    ys = np.linspace(BOARD_BORDER, BOARD_WIDTH - BOARD_BORDER, size)
    end_points += list(zip(xs, ys))

    return (start_points, end_points)

class GUIHandler:
    def __init__(self, game : Game, buttons : list = []):
        self.game = game
        self.start_points, self.end_points = make_grid(self.game.size)
        self.humanPlayers = [p for p in [game.blackPlayer,game.whitePlayer] if isinstance(p, HumanPlayer)]
        self.buttons = buttons
        self.reset_threat_hints()
        self.winning_streak_lines = []
        self.on_click_callbacks = []
        self.on_right_click_callbacks = []
        
    def add_on_click_callback(self, func):
        self.on_click_callbacks.append(func)

    def add_on_right_click_callback(self,func):
        self.on_right_click_callbacks.append(func)

    def reset_threat_hints(self):
        self.threat_hints = {i : [] for i in range(1,6)}

    def add_threat_hint(self, col, row, t_level):
        self.threat_hints[t_level].append((col,row))

    def remove_threat_hint(self, col, row, t_level):
        self.threat_hints[t_level].remove((col,row))

    def add_winning_streak_line(self, endpoints : tuple):
        self.winning_streak_lines.append(endpoints)

    def handle_click(self):
        x, y = pygame.mouse.get_pos()
        for cback in self.on_click_callbacks:
            cback(x,y)

        button_clicked = False
        for b in self.buttons:
            if b.check_click(x,y):
                for hp in self.humanPlayers:
                    hp.on_button_click(b.label)
                button_clicked = True

        if not button_clicked:
            c, r = xy_to_colrow(x,y,self.game.size)                 
            for p in self.humanPlayers:
                p.on_click_grid(x,y,c,r)

    def handle_right_click(self):
        x, y = pygame.mouse.get_pos()
        for cback in self.on_right_click_callbacks:
            cback(x,y)

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
        self.screen = screen
        self.ZOINK = pygame.mixer.Sound("wav/zoink.wav")
        self.CLICK = pygame.mixer.Sound("wav/click.wav")
        self.font = pygame.font.SysFont("arial", 30)

    def _draw_stone(self, col : int, row : int, color : pygame.Color):
        x, y = colrow_to_xy(col, row, self.game.size)
        gfxdraw.aacircle(self.screen, x, y, STONE_RADIUS, color)
        gfxdraw.filled_circle(self.screen, x, y, STONE_RADIUS, color)

    def _draw_threat_hint(self, col : int, row : int, t_level: int):
        self._draw_stone(col,row,THREAT_COLORS[t_level])

    def draw(self):
        # draw stones - filled circle and antialiased ring
        self.clear_screen()
        for col, row in zip(*np.where(self.game.board_state.grid == 1)):
            self._draw_stone(col,row,BLACK)
        for col, row in zip(*np.where(self.game.board_state.grid == 2)):
            self._draw_stone(col,row,WHITE)


        for line in self.winning_streak_lines:
            pygame.draw.line(self.screen,
            (0,0,255),
            colrow_to_xy(*line[0],self.game.size),
            colrow_to_xy(*line[1],self.game.size),
            5)

        # text for score and turn info    
        if self.game.winning_player is not None:
            win_msg = "%s won." % (self.game.winning_player) 
            txt = self.font.render(win_msg, True, BLACK)
            self.screen.blit(txt, WIN_POS)
        else:         
            if self.game.swap2_phase:
                if self.game.swap2_state["first_placement"]:
                    swap2_msg = "Black player can place 2 black stones and 1 white stone"
                if self.game.swap2_state["accept_or_place"]:
                    swap2_msg = "White player is deciding his color or to place more stones"
                    if isinstance(self.game.blackPlayer, HumanPlayer):
                        w_button = Button(
                        label = "White",
                        pos = (200, BOARD_WIDTH - int(BOARD_BORDER / 2.0) + 30),
                        font = 30,
                        bg = BLACK)
                        w_button.draw(self.screen)
                        b_button = Button(label = "Black",
                        pos = (100, BOARD_WIDTH - int(BOARD_BORDER / 2.0) + 30),
                        font = 30,
                        bg = BLACK)
                        b_button.draw()
                else:
                    self.buttons = []
                if self.game.swap2_state["second_placement"]:
                    swap2_msg = "White player can place 1 black stone and 1 white stone"                    
                if self.game.swap2_state["select_color"]:                    
                    swap2_msg = "Black player is deciding his color"
                    if isinstance(self.game.blackPlayer, HumanPlayer):
                        w_button = Button(
                        label = "White",
                        pos = (200, BOARD_WIDTH - int(BOARD_BORDER / 2.0) + 30),
                        font = 30,
                        bg = BLACK)
                        w_button.draw(self.screen)
                        b_button = Button(label = "Black",
                        pos = (100, BOARD_WIDTH - int(BOARD_BORDER / 2.0) + 30),
                        font = 30,
                        bg = BLACK)
                        b_button.draw(self.screen)
                        self.buttons = [w_button,b_button]
                else:
                    self.buttons = []        

                txt = self.font.render(swap2_msg, True, BLACK)
                self.screen.blit(txt,WIN_POS)
            else:
                turn_msg = (
                    f"{'Black' if self.game.black_turn else 'White'} to move. "
                    + "Click to place stone, press P to pass."
                )
                txt = self.font.render(turn_msg, True, BLACK)
                self.screen.blit(txt, TURN_POS)

        
        for lvl,hints in self.threat_hints.items():
            for h in hints:
                self._draw_threat_hint(*h, lvl)
        pygame.display.flip()

    def clear_screen(self):
        # fill board and add gridlines
        self.screen.fill(BOARD_BROWN)
        for start_point, end_point in zip(self.start_points, self.end_points):
            pygame.draw.line(self.screen, BLACK, start_point, end_point)

        # add guide dots
        guide_dots = [3, self.game.size // 2, self.game.size - 4]
        for col, row in itertools.product(guide_dots, guide_dots):
            x, y = colrow_to_xy(col, row, self.game.size)
            gfxdraw.aacircle(self.screen, x, y, DOT_RADIUS, BLACK)
            gfxdraw.filled_circle(self.screen, x, y, DOT_RADIUS, BLACK)

        pygame.display.flip()
    
    def update(self):        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.handle_click()
                elif event.button == 3:
                    self.handle_right_click()
            if event.type == pygame.QUIT:
                sys.exit()
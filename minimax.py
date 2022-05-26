from gomoku import no_moves_possible, check_winning_condition, check_line
import math
import numpy as np


def minimax(state : tuple, depth, maximize, alpha = -math.inf, beta = math.inf) -> float:
    if depth == 0 or gomoku_game_over(state):
        return gomoku_state_static_eval(state)
    if maximize:
        maxEval = -math.inf
        for child in gomoku_get_state_children(state):
            eval = minimax(child, depth - 1, False, alpha, beta)
            maxEval = max(maxEval,eval)
            alpha = max(alpha,eval)
            if beta <= alpha:
                break     
        return maxEval
    else:
        minEval = math.inf
        for child in gomoku_get_state_children(state):
            eval = minimax(child, depth - 1, True, alpha, beta)
            minEval = min(minEval,eval)
            beta = min(beta,eval)
            if beta <= alpha:
                break
        return minEval
    
def gomoku_game_over(state) -> bool:
    board,last_move,is_black = state
    color = "black" if is_black else "white"
    return check_winning_condition(board, last_move, color) or no_moves_possible(board)

def gomoku_get_state_children(state : tuple) -> list:
    board,_,is_black= state
    children = []
    for j in range(board.shape[1]):
        for i in range(board.shape[0]):
            if board[j,i] == 0 and check_neighbours(board, (j,i)):
                children.append((board,(j,i), not is_black))
    return children
                
def check_neighbours(board:np.array, pos: tuple):
    for j in range(-1,2):
        for i in range(-1,2):
            if pos[0] + j < 0 or pos[0] + j > board.shape[1] - 1:
                continue
            if pos[1] + i < 0 or pos[1] + i > board.shape[0] - 1:
                continue
            if i == 0 and j == 0:
                continue
            if board[pos[0] + j, pos[1] + i] != 0:
                return True
    return False
             
def gomoku_state_static_eval(state) :
    pass
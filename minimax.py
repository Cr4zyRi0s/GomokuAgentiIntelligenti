from boardstate import BoardState
from gomoku import no_moves_possible
from boardstate import BoardState

import math
import numpy as np

DEFAULT_SEARCH_DEPTH = 2

def gomoku_check_winner(state : BoardState) -> tuple:
    if len(state.b_winning_threats) > 0:
        return True,'black'
    elif len(state.w_winning_threats) > 0:
        return False,'white'
    else:
        return False,''

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

def gomoku_get_state_children(state : BoardState, maximize : bool) -> list:
    children = []
    nf_t, f_t,_ = state.get_all_threats(None, not maximize)    
    n_threats = 0

    for lvl, ts in nf_t:
        for t in ts:
            for slot in t.get_open_slots():
                children.append(slot, maximize)
            n_threats += 1
    
    for lvl,ts in f_t:
        for t in ts:
            for slot in t.get_open_slots():
                children.append(slot, maximize)
            n_threats += 1

    #If no threats are found just return one of the cells with an adjacent stone
    if n_threats == 0:
        for j in range(state.size):
            for i in range(state.size):
                if state.grid[j,i] == 0 and check_neighbours(state.grid,(j,i)):
                    children.append(((j, i), maximize))
    
    #If the board doesn't have a stone yet, then pick the central intersection
    if len(children) == 0:
        children.append(((state.size / 2 - 1,state.size / 2 - 1), maximize))
    
    return children

def gomoku_state_static_eval(state : BoardState):
    score = 0
    for lvl,ts in state.b_forcing_threats:
        for t in ts: 
            score += lvl * 3         

    for lvl,ts in state.b_nforcing_threats:
        for t in ts: 
            score += lvl


    for lvl,ts in state.w_forcing_threats:
        for t in ts:
            score -= lvl * 3

    for lvl,ts in state.w_forcing_threats:
        for t in ts:
            score -= lvl
    
    return score


def minimax(state : BoardState, depth, maximize, alpha = -math.inf, beta = math.inf) -> float:
    win,winner = gomoku_check_winner(state)
    if win:
        return math.inf if winner == 'black' else -math.inf
    
    if no_moves_possible(state.grid):
        return 0
    
    if depth == 0:
        return gomoku_state_static_eval(state)

    if maximize:
        maxEval = -math.inf
        for child in gomoku_get_state_children(state,maximize):
            move,_ = child

            state.make_move(move, maximize)
            eval = minimax(child, depth - 1, False, alpha, beta)
            state.unmake_last_move()

            maxEval = max(maxEval,eval)
            alpha = max(alpha,eval)
            if beta <= alpha:
                break     
        return maxEval
    else:
        minEval = math.inf
        for child in gomoku_get_state_children(state,maximize):
            move,_ = child

            state.make_move(move, maximize)            
            eval = minimax(child, depth - 1, True, alpha, beta)
            state.unmake_last_move()

            minEval = min(minEval,eval)
            beta = min(beta,eval)
            if beta <= alpha:
                break

        return minEval
    
def gomoku_get_best_move(state : BoardState, maximize : bool, search_depth : int = DEFAULT_SEARCH_DEPTH) -> tuple:
    best = None
    best_score = -math.inf if maximize else math.inf
    for child in gomoku_get_state_children(state):
        state.make_move(child[0], maximize)
        score = minimax(state,DEFAULT_SEARCH_DEPTH,maximize)
        if maximize:
            if score > best_score:
                best_score = score
                best = child
        else:
            if score < best_score:
                best_score = score
                best = child
    return best


        
'''      
def gomoku_get_state_children(state : BoardState) -> list:
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
'''             
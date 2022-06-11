from threading import Thread
from typing import Tuple

from boardstate import BoardState,deepcopy_boardstate
from utils import no_moves_possible
from joblib import Parallel,delayed

import math
import numpy as np
import time

DEFAULT_SEARCH_DEPTH = 2

SEARCH_DEPTHS = []
BRANCHING_FACTOR = []

parallel = Parallel(n_jobs=4,backend='threading')

def gomoku_check_winner(state : BoardState) -> tuple:
    if len(state.b_threats['winning']) > 0:
        return True,'black'
    elif len(state.w_threats['winning']) > 0:
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
    n_threats = 0
    f_t, opp_f_t = (state.b_threats['forcing'],state.w_threats['forcing']) if maximize else (state.w_threats['forcing'],state.b_threats['forcing'])
    nf_t, opp_nf_t = (state.b_threats['nforcing'],state.w_threats['nforcing']) if maximize else (state.w_threats['nforcing'],state.b_threats['nforcing'])
    
    for ft in opp_f_t:
        children.extend([(m, maximize) for m in ft.get_counter_moves()])
        n_threats += 1

    if len(children) > 0:
        return children

    for ft in f_t:
        children.extend([(m, maximize) for m in ft.get_counter_moves()])
        n_threats += 1

    if len(children) > 0:
        return children

    for nft in nf_t:
        children.extend([(m, maximize) for m in nft.get_counter_moves()])
        n_threats += 1

    for nft in opp_nf_t:
        if nft.info['type'][0] == 3:
            children.extend([(m, maximize) for m in nft.get_counter_moves()])
            n_threats += 1

    #If no threats are found just return one of the cells with an adjacent stone
    if n_threats == 0:
        for j in range(state.size):
            for i in range(state.size):
                if state.grid[j,i] == 0 and check_neighbours(state.grid,(j,i)):
                    children.append(((j, i), maximize))
    
    #If the board doesn't have a stone yet, then pick the central intersection
    if len(children) == 0:
        children.append(((state.size // 2, state.size // 2), maximize))
    
    return children


def gomoku_state_static_eval(state : BoardState):
    score = 0

    bl_f_t, wh_f_t = state.b_threats['forcing'],state.w_threats['forcing']
    bl_nf_t, wh_nf_t = state.b_threats['nforcing'],state.w_threats['nforcing']
    
    score += sum([t.info['type'][0] * 10 + 100 for t in bl_f_t])   
    score += sum([nft.info['type'][0] ^ 2 for nft in bl_nf_t])
    
    score -= sum([t.info['type'][0] * 10 + 100 for t in wh_f_t])
    score -= sum([nft.info['type'][0] ^ 2 for nft in wh_nf_t])
    
    return score


def minimax(state : BoardState, depth : int, maximize : bool, alpha = -math.inf, beta = math.inf) -> float:
    global BRANCHING_FACTOR
    win,winner = gomoku_check_winner(state)
    if win:
        return math.inf if winner == 'black' else -math.inf
    
    if no_moves_possible(state.grid):        
        return 0
    
    if depth == 0:
        return gomoku_state_static_eval(state)

    if maximize:
        maxEval = -math.inf
        children = gomoku_get_state_children(state,maximize)
        BRANCHING_FACTOR.append(len(children))
        for child in children:
            move,_ = child

            state.make_move(move, maximize)
            eval = minimax(state, depth - 1, False, alpha, beta)
            state.unmake_last_move()

            maxEval = max(maxEval,eval)
            alpha = max(alpha,eval)
            if beta <= alpha:
                break     
        return maxEval
    else:
        minEval = math.inf
        children = gomoku_get_state_children(state,maximize)
        BRANCHING_FACTOR.append(len(children))
        for child in children:
            move,_ = child

            state.make_move(move, maximize)            
            eval = minimax(state, depth - 1, True, alpha, beta)
            state.unmake_last_move()

            minEval = min(minEval,eval)
            beta = min(beta,eval)
            if beta <= alpha:
                break
        return minEval
    
def gomoku_get_best_move(state : BoardState, maximize : bool, search_depth : int = DEFAULT_SEARCH_DEPTH) -> Tuple[int,int]:
    global BRANCHING_FACTOR        
    start_time = time.time() 
    children = gomoku_get_state_children(state,maximize)
    best = None

    if len(children) == 0:
        pass
    elif len(children) == 1:        
        best = children[0]
        BRANCHING_FACTOR.append(1)
    else:
        results = Parallel(n_jobs=6,backend='threading')(delayed(_eval_move)(
        deepcopy_boardstate(state), child, maximize, search_depth) for child in children)

        max_index = np.argmax(results)
        best = children[max_index]        
    
    print(int(sum(BRANCHING_FACTOR) / len(BRANCHING_FACTOR)))
    print('elapsed time: ', time.time() - start_time)
    return best[0]

def _eval_move(state : BoardState, child: tuple, maximize : bool, search_depth : int):
    state.make_move(child[0], maximize)
    score = minimax(state,search_depth,maximize)
    state.unmake_last_move()
    return score        
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
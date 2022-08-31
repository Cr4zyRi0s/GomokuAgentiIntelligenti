from typing import List, Tuple

from boardstate import BoardState,deepcopy_boardstate, FORCING_THREAT_TYPES, NON_FORCING_THREAT_TYPES
from utils import no_moves_possible
from joblib import Parallel,delayed

import math
import numpy as np
import time

DEFAULT_SEARCH_DEPTH = 2
THREAT_PRIORITY = [
    [1,1,1,1,1],
    [2,2,2,2],
    [3,6,6],
    [7,8],
    [8]
]

parallel = Parallel(n_jobs=4,backend='threading')


def gomoku_check_winner(state : BoardState) -> tuple:
    if len(state.b_threats['winning']) > 0:
        return True,'black'
    elif len(state.w_threats['winning']) > 0:
        return True,'white'
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
    children = set()
    f_t, opp_f_t = (state.b_threats['forcing'],state.w_threats['forcing']) if maximize else (state.w_threats['forcing'],state.b_threats['forcing'])
    nf_t, opp_nf_t = (state.b_threats['nforcing'],state.w_threats['nforcing']) if maximize else (state.w_threats['nforcing'],state.b_threats['nforcing'])
    
    for ft in opp_f_t:
        children.update([(m, maximize) for m in ft.get_counter_moves()])

    if len(children) > 0:
        return list(children)

    for ft in f_t:
        children.update([(m, maximize) for m in ft.get_counter_moves()])

    if len(children) > 0:
        return list(children)

    for nft in nf_t:
        children.update([(m, maximize) for m in nft.get_counter_moves()])

    for nft in opp_nf_t:
        if nft.info['type'][0] >= 2:
            children.update([(m, maximize) for m in nft.get_counter_moves()])

    #If no threats are found just return one of the cells with an adjacent stone
    if len(children) == 0:
        for j in range(state.size):
            for i in range(state.size):
                if state.grid[j,i] == 0 and check_neighbours(state.grid,(j,i)):
                    children.add(((j, i), maximize))
    
    #If the board doesn't have a stone yet, then pick the central intersection
    if len(children) == 0:
        children.add(((state.size // 2, state.size // 2), maximize))
    
    return list(children)


def _get_threat_score(t_info : dict, t_weights : dict):
    n = t_info['type'][0] - 1
    w = t_info['type'][1] - 1
    n = n if n <= 4 else 4
    w = w if w <= n - 1 else n - 1

    score = THREAT_PRIORITY[n][w]
    if t_info['type'] in FORCING_THREAT_TYPES:
        score *= t_weights['forcing']
    if t_info['type'] in NON_FORCING_THREAT_TYPES:
        score *= t_weights['nforcing']
    return score

def gomoku_state_static_eval(state : BoardState, t_weights : dict, version : int = 1):
    score = 0

    bl_f_t = state.b_threats['forcing']
    wh_f_t = state.w_threats['forcing']

    bl_nf_t = state.b_threats['nforcing']
    wh_nf_t = state.w_threats['nforcing']

    bft_score = sum([_get_threat_score(t.info,t_weights) for t in bl_f_t])
    bnft_score = sum([_get_threat_score(nft.info,t_weights) for nft in bl_nf_t])
    if version == 2:
        bhook_score = 0
        bhooks = state.get_hooks(True)
        if bhooks is not None:            
            bhook_score = sum([
            _get_threat_score(hook[0].info, t_weights)*_get_threat_score(hook[1].info,t_weights)
            for hook in bhooks])
 
    wft_score = sum([_get_threat_score(t.info,t_weights) for t in wh_f_t])
    wnft_score = sum([_get_threat_score(nft.info,t_weights) for nft in wh_nf_t])
    if version == 2:
        whook_score = 0
        whooks = state.get_hooks(False)
        if whooks is not None:
            whook_score = sum([
            _get_threat_score(hook[0].info, t_weights)*_get_threat_score(hook[1].info,t_weights)
            for hook in whooks])
 

    
    score += bft_score + bnft_score
    if version == 2:
        score += bhook_score

    score -= wft_score + wnft_score
    if version == 2:
        score -= whook_score

    return score

def minimax(state : BoardState,
            depth : int,
            maximize : bool,
            t_weights : dict,
            alpha : float = -math.inf,
            beta : float = math.inf,
            version : int = 1) -> float:

    win,winner = gomoku_check_winner(state)
    if win:
        return 1000000000 / (10 - depth) if winner == 'black' else -1000000000 / (10 - depth)
    
    if no_moves_possible(state.grid):        
        return 0
    
    if depth == 0:
        return gomoku_state_static_eval(state, t_weights,version=version)

    # if version == 2:
    #     instersect_score = _get_hook_scores(state, children, maximize, t_weights)

    if maximize:
        maxEval = -math.inf
        children = gomoku_get_state_children(state,maximize)

        for i,child in zip(range(len(children)),children):
            move,_ = child

            state.make_move(move, maximize)
            eval = minimax(state, depth - 1, False, t_weights, alpha, beta,version=version)
            # if version == 2:
            #     eval += instersect_score[i]            

            state.unmake_last_move()

            maxEval = max(maxEval,eval)
            alpha = max(alpha,eval)
            if beta <= alpha:
                break     
        return maxEval
    else:
        minEval = math.inf
        children = gomoku_get_state_children(state,maximize)
        for  i,child in zip(range(len(children)),children):
            move,_ = child

            state.make_move(move, maximize)            
            eval = minimax(state, depth - 1, True, t_weights, alpha, beta,version=version)
            # if version == 2:
            #     eval += instersect_score[i]   

            state.unmake_last_move()

            minEval = min(minEval,eval)
            beta = min(beta,eval)
            if beta <= alpha:
                break
        return minEval
    
def gomoku_get_best_move(state : BoardState, 
                        maximize : bool,
                        t_weights : dict,
                        search_depth : int = DEFAULT_SEARCH_DEPTH,
                        version : int = 1) -> Tuple[int,int]:     
    assert search_depth >= 1
    assert version >= 1 and version <= 2

    start_time = time.time() 
    threats = state.b_threats if maximize else state.w_threats
    for ft in threats['forcing']:
        if ft.info['type'][0] == 4:      
            return list(ft.get_counter_moves())[0]

    children = gomoku_get_state_children(state,maximize)
    results = _eval_next_moves(state, children, t_weights, maximize, search_depth, version)
    
    if maximize:
        index = np.argmax(results)                
    else:
        index = np.argmin(results)

    print('Black options:' if maximize else 'White options:')
    print(children[index], results[index])
    best = children[index][0]  

    print('elapsed time: ', time.time() - start_time)
    return best


        
def _eval_next_moves(state : BoardState,
                        children : List[Tuple],
                        t_weights : dict,
                        maximize : bool,
                        search_depth : int = DEFAULT_SEARCH_DEPTH,
                        version : int = 1) -> Tuple[int,int]:

    if len(children) == 1:        
        return [0]
    else:
        results = Parallel(n_jobs=6,backend='threading')(delayed(_eval_move)(
        deepcopy_boardstate(state), child, t_weights, maximize, search_depth - 1,version) for child in children)
        return results

def _eval_move(state : BoardState,
                child : tuple,
                t_weights : dict, 
                maximize : bool,
                search_depth : int,
                version : int = 1,
                debug : bool = False):    
    
    state.make_move(child[0], maximize)
    score = minimax(state, search_depth, not maximize, t_weights, version=version)
    state.unmake_last_move()
    return score      


# def _get_hook_scores(state : BoardState,
#                     children : List[Tuple],                    
#                     t_weights : dict):

#         b_phooks_pos = _get_potential_hooks(state,True)
#         w_phooks_pos = _get_potential_hooks(state,False)

#         scores = [0 for _ in range(len(children))]
#         for i,child in zip(range(len(children)),children):
#             pos,_ = child
#             for t,next_t_info in b_phooks_pos:
#                 scores[i] += int(0.5 * _get_threat_score(next_t_info, t_weights))
#             for t,next_t_info in w_phooks_pos:
#                 scores[i] -= int(0.5 * _get_threat_score(next_t_info, t_weights))
#         return scores          

# def _get_potential_hooks(state : BoardState,
#                         maximize : bool):
#     p_threats = state.b_threats if maximize else state.w_threats
#     p_nf_threats = [t for t in p_threats['nforcing'] if t.info['type'][0] >= 2]
#     pos_to_threat = {}
#     for nft in p_nf_threats:
#         cmoves = nft.get_counter_moves_with_offsets()
#         for cmove in cmoves:
#             k = str(cmove[0])
#             if k not in pos_to_threat:
#                 pos_to_threat[k] = []

#             if maximize:
#                 next_t_seq = replace_char(nft.group, cmove[1], '1')
#                 next_t = state.b_threats_info[next_t_seq]
#             else:
#                 next_t_seq = replace_char(nft.group, cmove[1], '2')
#                 next_t = state.w_threats_info[next_t_seq]

#             pos_to_threat[k].append((nft,next_t))
#         return pos_to_threat

from ast import expr_context
from shutil import ExecError
import numpy as np
import re

from utils import *

from threats import Threat, load_precomputed_threats

BLACK_SEQUENCE_RGX = '[01]{5,}'
WHITE_SEQUENCE_RGX = '[02]{5,}'

WINNING_THREAT_TYPES = [(5,1)]
FORCING_THREAT_TYPES = [(4,2),(4,1),(3,3),(3,2)]
NON_FORCING_THREAT_TYPES = [(3,1)]
for i in range(1,3):
    NON_FORCING_THREAT_TYPES.extend([(i,j) for j in range(1, 6 - i + 1)])

def check_correctness(threat : Threat, bucket : str):
    type = threat.info['type']
    if type in WINNING_THREAT_TYPES:
        if bucket != 'winning':
            raise Exception('wrong threat identification (%s != %s)' % (bucket,'winning'))
    elif type in FORCING_THREAT_TYPES:
        if bucket != 'forcing':
            raise Exception('wrong threat identification (%s != %s)' % (bucket,'forcing'))
    else:
        if bucket != 'nforcing':
            raise Exception('wrong threat identification (%s != %s)' % (bucket,'nforcing'))

#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
#BOARD STATE CLASS
#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------

class BoardState:
    def __init__(self,size = 15):
        self.size = size    
        self.moves = []   

        board = np.full((self.size + 2, self.size + 2), 3, dtype='int8')
        board[1:self.size + 1,1:self.size + 1] = 0
        self.grid = board[1:self.size+1, 1:self.size+1]

        board_45 = rot45(board)
        board_45 = board_45[2:2 * self.size + 1,:]
        board_315 = rot315(board)
        board_315 = board_315[2:2 * self.size + 1,:]
        board = board[1:self.size+1,:]

        self.board = ''.join([str(el) for el in board.flatten()])
        self.board_45 = ''.join([str(el) for el in board_45.flatten()])
        self.board_90 = ''.join([str(el) for el in board.flatten()])
        self.board_315 = ''.join([str(el) for el in board_315.flatten()])

        b_threats_info, w_threats_info = load_precomputed_threats()

        self.b_threats_info = b_threats_info
        self.w_threats_info = w_threats_info
        self.w_threats = {'winning' : set(), 'forcing' : set(), 'nforcing' : set()}
        self.b_threats = {'winning' : set(), 'forcing' : set(), 'nforcing' : set()}
        self.threat_updates = {}
    
    def make_move(self,move,is_black):
        self.grid[move[0], move[1]] = 1 if is_black else 2 
        stone = '1' if is_black else '2' 
        self._update_boards(move, stone)
        self._update_threats(move, is_black)
        self.moves.append((*move,is_black))
        
    def unmake_last_move(self):
        c,r,_ = self.moves.pop()

        self.grid[c, r] = 0
        self._update_boards((c,r), '0')
        updt = self.threat_updates[str((c,r))]

        #print(c,r,is_black)
        #print(updt)
        try:
            for add in updt['white']['added']:
                self.w_threats[add[1]].remove(add[0])
            for rem in updt['white']['removed']:
                self.w_threats[rem[1]].add(rem[0])
        except KeyError:        
            pass

        try:
            for add in updt['black']['added']:
                self.b_threats[add[1]].remove(add[0])
            for rem in updt['black']['removed']:
                self.b_threats[rem[1]].add(rem[0])
        except KeyError:
            pass

    def get_all_threats(self, black : bool) -> tuple:         
        raise NotImplementedError()

    def _get_repr_from_angle(self, angle : int) -> str:
        if angle == 0:
            return self.board
        elif angle == 45:
            return self.board_45
        elif angle == 90:
            return self.board_90
        elif angle == 315:
            return self.board_315
        else:
            raise Exception('invalid angle value %d' % (angle))

    def _prune_old_threats(self, spans : tuple, black : bool):
        pthreats = self.b_threats if black else self.w_threats
        to_remove = set()
        removed = set()
        for type, ts in pthreats.items():
            for t in ts:
                s = spans[t.angle]
                if t.span[0] >= s[0] and t.span[0] < s[1]:
                    to_remove.add(t)
                if t.span[1] > s[0] and t.span[1] <= s[1]:
                    to_remove.add(t)                    
            ts.difference_update(to_remove)
            removed.update([(tr,type) for tr in to_remove])   
        
        return removed

    def _update_threats(self, last_move : tuple, black : bool):                
        #check new threats in intersecting lines
        span, line = self._get_line(last_move)
        span90, line90 = self._get_line90(last_move)
        span45, line45 = self._get_line45(last_move)
        span315, line315 = self._get_line315(last_move)

        spans = {0 : span, 45 : span45, 90 : span90, 315 : span315}
        self.threat_updates[str(last_move)] = {
            'black': {
                'added' : set(),
                'removed' : self._prune_old_threats(spans, True)
            },  
            'white' : {
                'added' : set(),
                'removed' :self._prune_old_threats(spans, False) 
            }
        }

        # self._prune_old_threats(spans, True)
        # self._prune_old_threats(spans, False)   
        
        ts = self.b_threats if black else self.w_threats

        added_threats = set()
        added_threats.update(self._get_threats_in_repr(ts, line, black, span[0], 0))
        added_threats.update(self._get_threats_in_repr(ts, line90, black, span90[0], 90))
        added_threats.update(self._get_threats_in_repr(ts, line45, black, span45[0], 45))
        added_threats.update(self._get_threats_in_repr(ts, line315, black, span315[0], 315))

        self.threat_updates[str(last_move)]['black' if black else 'white']['added'] = added_threats

    def _get_threats_in_repr(self, dst : dict,  repr : str, black : bool, offset : int = 0, angle : int = 0):
        rgx = BLACK_SEQUENCE_RGX if black else WHITE_SEQUENCE_RGX
        t_info = self.b_threats_info if black else self.w_threats_info
        added = set()
        for match in re.finditer(rgx, repr):
            group = match.group()
            l = len(group)
            # if group in t_info[l]:
            if group in t_info:
                # info = t_info[l][group]
                info = t_info[group]                
                span = (match.span()[0] + offset, match.span()[1] + offset)
                threat = Threat(group,info,span,angle)
                #added.add((threat))

                if info['type'] in WINNING_THREAT_TYPES:
                    dst['winning'].add(threat)
                    added.add((threat, 'winning'))
                elif info['type'] in FORCING_THREAT_TYPES:
                    dst['forcing'].add(threat)
                    added.add((threat, 'forcing'))
                else:
                    dst['nforcing'].add(threat)    
                    added.add((threat, 'nforcing'))
            # else:
            #     print('%s not found as a threat sequence' % group)
        for add in added:
            check_correctness(add[0], add[1])
        return added

    def _get_threats(self, black : bool):
        threats = self.b_threats if black else self.w_threats
        # for level,patts in threat_patterns.items():
        #     threats[level] = []
        self._get_threats_in_repr(self.board, black, angle = 0)
        self._get_threats_in_repr(self.board_90, black, angle = 90)
        self._get_threats_in_repr(self.board_45, black, angle = 45)
        self._get_threats_in_repr(self.board_315, black, angle = 315)
        return threats

    def print_boards(self):
        b = np.array([list(self.board[i : i + self.size + 2]) for i in range(0,(self.size + 2) * self.size, self.size + 2)])
        print(b)
        b = np.array([list(self.board_90[i : i + self.size + 2]) for i in range(0,(self.size + 2) * self.size, self.size + 2)])
        print(b)
        b = np.array([list(self.board_45[i : i + self.size + 2]) for i in range(0,(self.size + 2) * (2 * self.size - 1), self.size + 2)])
        print(b)
        b = np.array([list(self.board_315[i : i + self.size + 2]) for i in range(0,(self.size + 2) * (2 * self.size - 1), self.size + 2)])
        print(b)

    def _get_line(self, pos:tuple) -> tuple:
        extr = ((0,pos[1]), (self.size - 1,pos[1]))
        bounds = (cr_to_index(*extr[0], self.size), cr_to_index(*extr[1], self.size))
        return bounds, self.board[bounds[0] : bounds[1] + 1]

    def _get_line90(self, pos:tuple) -> tuple:
        extr = ((pos[0],0), (pos[0],self.size - 1))
        bounds = (cr_to_index90(*extr[0], self.size), cr_to_index90(*extr[1], self.size))
        return bounds, self.board_90[bounds[0] : bounds[1] + 1]

    def _get_line45(self, pos : tuple) -> tuple:
        c,r = pos

        if r + c < self.size:
            extr = ((c + r,0),(0,c + r))            
        elif r + c == self.size - 1:
            extr = [(self.size - 1, 0),(0, self.size - 1)]            
        else:
            extr = ((self.size - 1, c + r - self.size + 1),(c + r - self.size + 1, self.size - 1))

        bounds = (cr_to_index45(*extr[1],self.size), cr_to_index45(*extr[0],self.size))
        return bounds, self.board_45[bounds[0] : bounds[1] + 1]      

    def _get_line315(self, pos : tuple) -> tuple:
        c,r = pos        
        if c < r:
            offset = c + self.size - 1 - r
            extr = ((0, self.size - 1 - offset),(offset, self.size - 1))            
        elif r == c:
            extr = [(0, 0),(self.size - 1, self.size - 1)]            
        else:
            offset = r + self.size - 1 - c
            extr = ((self.size - 1 - offset, 0),(self.size - 1, offset))

        #print('extr: ', extr)                
        bounds = (cr_to_index315(*extr[0], self.size), cr_to_index315(*extr[1], self.size))
        return bounds, self.board_315[bounds[0] : bounds[1] + 1]    


    def deepcopy(self):
        pass   

    def _update_boards(self, move, stone):
        c,r = move
        self.board = replace_char(self.board, cr_to_index(c,r, self.size), stone)
        self.board_90 = replace_char(self.board_90, cr_to_index90(c,r, self.size), stone)
        self.board_45 = replace_char(self.board_45, cr_to_index45(c,r, self.size), stone)
        self.board_315 = replace_char(self.board_315, cr_to_index315(c,r, self.size), stone)

if __name__ == '__main__':
    bstate = BoardState(10)
    moves = [(i + 2,i)  for i in range(5)]

    for m in moves:
        bstate.make_move(m, True if m[0] % 2 == 0 else False)

    print(bstate.board_315)
    for i in range(len(moves)):
        print(moves[i])
        print(bstate._get_line315(moves[i]))



# span = match.span()
# if offset != 0:      
#     span = list(span)           
#     span[0] += offset
#     span[1] += offset
#     span = tuple(span)                
# if not isinstance(dst[level], set):
#     dst[level].append(Threat(match.group(), span, level, angle))
# else:
#     dst[level].add(Threat(match.group(), span, level, angle))

# w_t = self.b_winning_threats if black else self.w_winning_threats
# f_t = self.b_forcing_threats if black else self.w_forcing_threats
# nf_t = self.b_nforcing_threats if black else self.w_nforcing_threats

# for lvl,patts in f_t.items():
#     self._get_threats_in_repr(line, black, span[0], 0)
#     self._get_threats_in_repr(line90, black, span90[0], 90)
#     self._get_threats_in_repr(line45, black, span45[0], 45)
#     self._get_threats_in_repr(line315, black, span315[0], 315)

# for lvl,patts in nf_t.items():
#     self._get_threats_in_repr(line, black, span[0], 0)
#     self._get_threats_in_repr(line90, black, span90[0], 90)
#     self._get_threats_in_repr(line45, black, span45[0], 45)
#     self._get_threats_in_repr(line315, black, span315[0], 315)

# self.w_winning_threats = generic_to_white_threat(WINNING_THREAT)
# self.b_winning_threats = generic_to_black_threat(WINNING_THREAT)

# self.w_forcing_threats = generic_to_white_threat(FORCING_THREATS)
# self.b_forcing_threats = generic_to_black_threat(FORCING_THREATS)    

# self.w_nforcing_threats = generic_to_white_threat(NON_FORCING_THREATS)
# self.b_nforcing_threats = generic_to_black_threat(NON_FORCING_THREATS)   

        # win_threats = self._get_threats(self.b_winning_threats if black else self.w_winning_threats)
        # force_threats = self._get_threats(self.b_forcing_threats if black else self.w_forcing_threats)
        # nforce_threats = self._get_threats(self.b_nforcing_threats if black else self.w_nforcing_threats)

        # #TEMPORANEO
        # if black:
        #     self.b_winning_threats = win_threats
        #     self.b_forcing_threats = force_threats
        #     self.b_nforcing_threats = nforce_threats
        # else:
        #     self.w_winning_threats = win_threats
        #     self.w_forcing_threats = force_threats
        #     self.w_nforcing_threats = nforce_threats

        # return win_threats, force_threats, nforce_threats
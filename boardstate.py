from copy import copy, deepcopy
import itertools
import numpy as np
import re

from tqdm import tqdm

from utils import *

from threats import Threat, load_precomputed_threats

BLACK_SEQUENCE_RGX = '[01]{5,}'
WHITE_SEQUENCE_RGX = '[02]{5,}'

WINNING_THREAT_TYPES = [(5,1)]
FORCING_THREAT_TYPES = [(4,2),(4,1),(3,3),(3,2)]
NON_FORCING_THREAT_TYPES = [(3,1)]
for i in range(1,3):
    NON_FORCING_THREAT_TYPES.extend([(i,j) for j in range(1, 6 - i + 1)])

b_threats_info = None
w_threats_info = None

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

def get_threat_priority_from_type(type : tuple) -> str:
    if type[0] == 5:
        return 'winning'
    elif type[0] == 4 or (type[0] == 3 and type[1] > 1):
        return 'forcing'
    else:
        return 'nforcing'


#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
#BOARD STATE CLASS
#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------

class BoardState:
    def __init__(self,size = 15, copy_instance = False):
        global b_threats_info
        global w_threats_info

        if b_threats_info is None or w_threats_info is None:
            b_threats_info, w_threats_info = load_precomputed_threats()
        self.b_threats_info = b_threats_info
        self.w_threats_info = w_threats_info

        if not copy_instance:
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

            self.w_threats = {'winning' : set(), 'forcing' : set(), 'nforcing' : set()}
            self.b_threats = {'winning' : set(), 'forcing' : set(), 'nforcing' : set()}
            self.threat_updates = {}
    
    def make_move(self,move,is_black):
        self.grid[move[0], move[1]] = 1 if is_black else 2 
        stone = '1' if is_black else '2' 
        self._update_boards(move, stone)
        #self._update_threats(move, is_black)
        self._update_threats(move)
        self.moves.append((*move,is_black))

    def get_hooks(self,
                maximize : bool):
        p_threats = self.b_threats if maximize else self.w_threats
        #p_threat_list = [t for t in p_threats['nforcing'] if t.info['type'][0] >= 2]
        p_threat_list = [t for t in p_threats['forcing']]
        hooks = []
        for t0, t1 in itertools.combinations(p_threat_list,r=2):
            p0,p1 = t0.get_grid_span()
            q0,q1 = t1.get_grid_span()
            intersect = line_intersect(p0,p1,q0,q1)
            if intersect is not None:
                intersect = (int(intersect[0]),int(intersect[1]))
                if intersect[0] > 14 or intersect[1] > 14:
                    raise Exception('intersection out of grid')
                if maximize and self.grid[intersect[0], intersect[1]] == 1:
                    hooks.append((t0,t1))
                elif not maximize and self.grid[intersect[0], intersect[1]] == 2:
                    hooks.append((t0,t1))


    def unmake_last_move(self):
        c,r,_ = self.moves.pop()

        self.grid[c, r] = 0
        self._update_boards((c,r), '0')
        self._update_threats((c,r))

        #updt = self.threat_updates[str((c,r))]

        #print(c,r,is_black)
        #print(updt)
        # try:
        #     for add in updt['white']['added']:
        #         self.w_threats[add[1]].remove(add[0])
        #     for rem in updt['white']['removed']:
        #         self.w_threats[rem[1]].add(rem[0])
        # except KeyError:        
        #     pass

        # try:
        #     for add in updt['black']['added']:
        #         self.b_threats[add[1]].remove(add[0])
        #     for rem in updt['black']['removed']:
        #         self.b_threats[rem[1]].add(rem[0])
        # except KeyError:
        #     pass

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

    def _find_threats_intersecting(self, lines : dict,  spans : dict, black : bool):
        ts = self.b_threats if black else self.w_threats
        for angle, line in lines.items():
            self._get_threats_in_repr(ts, line, black, spans[angle][0], angle)

    def _update_threats(self,last_move):
        #check new threats in intersecting lines
        span, line = self._get_line(last_move)
        span90, line90 = self._get_line90(last_move)
        span45, line45 = self._get_line45(last_move)
        span315, line315 = self._get_line315(last_move)

        spans = {0 : span, 45 : span45, 90 : span90, 315 : span315}
        lines = {0 : line, 45 : line45, 90 : line90, 315 : line315}

        self._prune_old_threats(spans, True)
        self._prune_old_threats(spans, False)   

        self._find_threats_intersecting(lines,spans,True)
        self._find_threats_intersecting(lines,spans,False)
        


    # def _update_threats(self, last_move : tuple, black : bool):                
    #     #check new threats in intersecting lines
    #     span, line = self._get_line(last_move)
    #     span90, line90 = self._get_line90(last_move)
    #     span45, line45 = self._get_line45(last_move)
    #     span315, line315 = self._get_line315(last_move)

    #     spans = {0 : span, 45 : span45, 90 : span90, 315 : span315}
    #     self.threat_updates[str(last_move)] = {
    #         'black': {
    #             'added' : set(),
    #             'removed' : self._prune_old_threats(spans, True)
    #         },  
    #         'white' : {
    #             'added' : set(),
    #             'removed' :self._prune_old_threats(spans, False) 
    #         }
    #     }

    #     # self._prune_old_threats(spans, True)
    #     # self._prune_old_threats(spans, False)   
        
    #     ts = self.b_threats if black else self.w_threats

    #     added_threats = set()
    #     added_threats.update(self._get_threats_in_repr(ts, line, black, span[0], 0))
    #     added_threats.update(self._get_threats_in_repr(ts, line90, black, span90[0], 90))
    #     added_threats.update(self._get_threats_in_repr(ts, line45, black, span45[0], 45))
    #     added_threats.update(self._get_threats_in_repr(ts, line315, black, span315[0], 315))

    #     self.threat_updates[str(last_move)]['black' if black else 'white']['added'] = added_threats

    def _get_threats_in_repr(self, dst : dict,  repr : str, black : bool, offset : int = 0, angle : int = 0):
        rgx = BLACK_SEQUENCE_RGX if black else WHITE_SEQUENCE_RGX
        t_info = self.b_threats_info if black else self.w_threats_info
        added = set()
        for match in re.finditer(rgx, repr):
            group = match.group()
            l = len(group)            

            if group in t_info:
                info = t_info[group]                
                span = (match.span()[0] + offset, match.span()[1] + offset)
                threat = Threat(group,info,span,angle)
                if info['type'] in WINNING_THREAT_TYPES:
                    dst['winning'].add(threat)
                    added.add((threat, 'winning'))
                elif info['type'] in FORCING_THREAT_TYPES:
                    dst['forcing'].add(threat)
                    added.add((threat, 'forcing'))
                else:
                    dst['nforcing'].add(threat)    
                    added.add((threat, 'nforcing'))
        for add in added:
            check_correctness(add[0], add[1])
        return added

    def _get_threats(self, black : bool):
        threats = self.b_threats if black else self.w_threats
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

    def _update_boards(self, move, stone):
        c,r = move
        self.board = replace_char(self.board, cr_to_index(c,r, self.size), stone)
        self.board_90 = replace_char(self.board_90, cr_to_index90(c,r, self.size), stone)
        self.board_45 = replace_char(self.board_45, cr_to_index45(c,r, self.size), stone)
        self.board_315 = replace_char(self.board_315, cr_to_index315(c,r, self.size), stone)

def deepcopy_boardstate(bstate: BoardState) -> BoardState:
    bcopy = BoardState(copy_instance=True)
    
    bcopy.size = bstate.size
    bcopy.moves = bstate.moves[:]

    bcopy.grid = np.copy(bstate.grid)
    bcopy.board = bstate.board[:]
    bcopy.board_45 = bstate.board_45[:]
    bcopy.board_90 = bstate.board_90[:]
    bcopy.board_315 = bstate.board_315[:]

    bcopy.b_threats = deepcopy(bstate.b_threats)
    bcopy.w_threats = deepcopy(bstate.w_threats)
    return bcopy


if __name__ == '__main__':
    from time import time
    
    def test_time_make_unmake():
        bstate = BoardState(15)
        moves = [(i + 2,i)  for i in range(10)]    
        start = time()
        for _ in tqdm(range(1000000)):
            for m in moves:
                bstate.make_move(m, True)
            for _ in range(len(moves)):
                bstate.unmake_last_move()
        print('elapsed time:', round(time() - start,4))

    def test_deep_copy():
        start = time()
        bstate = BoardState(15)
        print('original creation time:', time() - start)
        start = time()
        bstate_copy = deepcopy_boardstate(bstate)
        print('custom copy creation time:', time() - start)
        assert id(bstate) != id (bstate_copy)
        assert id(bstate.grid) != id (bstate_copy.grid)
        assert id(bstate.b_threats) != id(bstate_copy.b_threats)
        for type,ts in bstate.b_threats.items():
            assert id(bstate_copy.b_threats[type]) != id(ts)

        assert id(bstate.w_threats) != id(bstate_copy.w_threats)
        for type,ts in bstate.w_threats.items():
            assert id(bstate_copy.w_threats[type]) != id(ts)

    def test_deep_copy2():
        bstate = BoardState(15)
        bstate.make_move((7,7), True)
        bcopy = deepcopy_boardstate(bstate)
        
        assert np.array_equal(bcopy.grid, bstate.grid)
        assert bstate.b_threats == bcopy.b_threats
        assert bstate.w_threats == bcopy.w_threats

        bcopy.make_move((7,8), True)
        
        assert not np.array_equal(bcopy.grid, bstate.grid)
        assert bstate.b_threats != bcopy.b_threats
        assert bstate.w_threats == bcopy.w_threats

    def test_get_threat_priority_from_type():
        pass

    test_deep_copy()
    test_deep_copy2()
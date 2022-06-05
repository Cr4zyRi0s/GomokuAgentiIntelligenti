import numpy as np
import re
import itertools
import networkx as nx
import time

'''
WINNING_THREAT = {
 5 : 
 ['[0Y3]X{5}[0Y3]']
}
FORCING_THREATS = {
    4 : [
    #Open fours
    '[0Y3]0X{4}0[0Y3]',
    '[Y3]X{2}0X{2}0X{2}[Y3]',
    '[Y3]X{3}0X0X{3}[Y3]',
    #Simple fours
    '[Y3]X{4}0[03Y]',
    '[Y3]X{2}0X{2}[Y3]',
    '[Y3]X0X{3}[Y3]',
    '[Y3]X{3}0X[Y3]',
    '[Y3]X{4}0X[Y3]',
    '[03Y]0X{4}[3Y]'],
    #Open threes    
    3 : [
    '[0Y3]0{2}X{3}0{2}[0Y3]',
    '[0Y3]0X0X{2}0X0[0Y3]',
    'X0X0X0X0X',
    #Broken threes
    '0X0X{2}0',
    '0X{2}0X0',
    '[Y3]0X{3}0{2}',
    '0{2}X{3}0[Y3]'
    ]
}

NON_FORCING_THREATS = {
    3 : [
        '[Y3]X{3}0{2}[0Y3]',
        '[0Y3]0{2}X{3}[Y3]'
        ],
    2 : []
}
'''


#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
#UTILITY FUNCTIONS

#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
def replace_char(string : str, index : int, char):
    return string[:index] + char + string[index + 1:]

def rot45(mat : np.array):
    n,m = mat.shape
    ctr = 0    
    new_mat = np.full((2 * n - 1, n), 3, mat.dtype)
    while(ctr < 2 * n -1):     
        for i in range(m):                
            for j in range(n):
                if i + j == ctr:
                    new_mat[ctr, j] = mat[i,j]
        ctr += 1
    return new_mat

def rot315(mat : np.array):
    n,m = mat.shape
    ctr = 0    
    new_mat = np.full((2 * n - 1, n), 3, dtype = mat.dtype)
    while(ctr < 2 * n -1):     
        for i in range(m):                
            for j in range(n):
                if i + (m - j) - 1 == ctr:
                    new_mat[ctr, j] = mat[i,j]
        ctr += 1
    return new_mat

def generic_to_white_threat(generic_threats : dict) -> dict:
    return { k:
    [pattern.replace('X','2').replace('Y','1') for pattern in v]
    for k,v in generic_threats.items()}

def generic_to_black_threat(generic_threats : dict) -> dict:
    return { k:
    [pattern.replace('X','1').replace('Y','2') for pattern in v]
    for k,v in generic_threats.items()}

def cr_to_index(c,r,size) -> int:
    return r * (size + 2) + c + 1
def cr_to_index90(c,r,size) -> int:
    return c * (size + 2) + r + 1
def cr_to_index45(c,r,size) -> int:
    return (r + c) * (size + 2) + c + 1
def cr_to_index315(c,r,size) -> int:
    return (r + size - c - 1) * (size + 2) + c + 1

def index_to_cr(index,size) -> tuple:
    r = index // (size + 2)
    c = index - r * (size + 2) - 1
    return c,r
def index90_to_cr(index,size) -> tuple:
    c = index // (size + 2)
    r = index - c * (size + 2) - 1
    return c,r     
def index45_to_cr(index,size)  -> tuple:
    rc = index // (size + 2)
    c = index - rc * (size + 2) - 1
    r = rc - c
    return c,r 
def index315_to_cr(index,size)  -> tuple:
    rc = index // (size + 2)
    c = index - rc * (size + 2) - 1
    r = rc - size + c + 1
    return c,r

def get_index_transform_func(angle : int):
    if angle == 0:
        return index_to_cr
    elif angle == 45:
        return index45_to_cr
    elif angle == 90:
        return index90_to_cr
    elif angle == 315:
        return index315_to_cr
    else:
        raise Exception('Invalid angle value %d' % (angle))

#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------


def generate_all_sequences_of_len(length : int) -> set:
    all_seqs = set(itertools.product('01', repeat = length))
    all_seqs = {''.join(s) for s in all_seqs}
    all_seqs.remove(''.join(['0' for _ in range(length)]))    

    to_remove = set()
    for s in all_seqs:
        if len(re.findall('1{6,}',s)) > 0:
            to_remove.add(s)

        #elif len(re.findall('10{2,}1',s)) > 0:
        #    to_remove.add(s)
        
        elif length > 5 and s.count('1') >= length - 1:
            to_remove.add(s)

    all_seqs.difference_update(to_remove)
    return all_seqs

def generate_threat_info(seq : str):    
    if len(list(re.finditer('(?<!1)1{5}(?!1)', seq))) == 1:
        return {seq},{},{}

    n_ones = seq.count('1')
    zeros_pos = [m.span()[0] for m in re.finditer('0', seq)]
    perms = itertools.product('01', repeat=len(zeros_pos))    

    possible_moves = set()
    possible_5s = set()
    for p in perms:        
        candidate = seq[:]

        for i in range(len(zeros_pos)):
            candidate = replace_char(candidate, zeros_pos[i], p[i])

        if candidate.count('1') < 5:
            continue
        if candidate.count('1') > 5 and n_ones < 5:
            continue

        win_seq_match = list(re.finditer('(?<!1)1{5}(?!1)', candidate))
        if len(win_seq_match) == 1:
            possible_5s.add(candidate)
            ones_pos = [zeros_pos[m.span()[0]] for m in re.finditer('1', ''.join(p))]
            for i in range(len(ones_pos)):
                possible_moves.add((ones_pos[i]))

    best_defences = get_best_defence_for_threat(seq,possible_5s)
    return possible_5s, possible_moves, best_defences    

def get_best_defence_for_threat(threat : str, possible_5s : set) -> list:
    zeros_pos = [m.span()[0] for m in re.finditer('0', threat)]
    n_of_blocks = [0 for _ in range(len(zeros_pos))]
    for five in possible_5s:
        for zi in range(len(zeros_pos)):
            if five[zeros_pos[zi]] == '1':
                n_of_blocks[zi] += 1
    
    max_blocks = max(n_of_blocks)
    best_def = {zeros_pos[i] for i in range(len(zeros_pos)) if n_of_blocks[i] == max_blocks}
    return best_def


def precompute_threats(max_seq_len = 7) -> dict:
    threats = {i:dict() for i in range(5, max_seq_len + 1)}
    all_seqs = {i: generate_all_sequences_of_len(i) for i in range(5, max_seq_len + 1)}
    
    for s in all_seqs[5]:
        p_5s,p_moves,b_def = generate_threat_info(s)
        sev = len(p_5s)
        if sev == 0:
            continue        
        lvls = [threats[5][s[i : i + 5]]['type'][0] for i in range(0,1) if s[i : i + 5] in threats[5].keys()]
        threats[5][s] = {'type' : (s.count('1'), sev), 'p_moves' : p_moves, 'b_def' : b_def}

    for l in range(6,max_seq_len + 1):
        for s in all_seqs[l]:
            p_5s,p_moves,b_def = generate_threat_info(s)
            sev = len(p_5s)
            if sev == 0:
                continue        
            lvls = [threats[5][s[i : i + 5]]['type'][0] for i in range(0, l - 4) if s[i : i + 5] in threats[5].keys()]
            threats[l][s] = {'type' : (max(lvls), sev), 'p_moves' : p_moves, 'b_def' : b_def}
    return threats

def generate_dependency_graph(threats : dict, max_seq_len : int = 7) -> dict:    
    graphs = {}
    for l in range(5,max_seq_len + 1):
        curr_g = nx.DiGraph()
        curr_g.add_nodes_from(threats[l].keys())
        for seq,info in threats[l].items():
            for m in info['p_moves']:
                curr_g.add_edge(seq, replace_char(seq,m,'1'), move = m)   
        graphs[l] = curr_g
                
    return graphs        


#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------
#THREAT CLASS
#-----------------------------------------------------------------------------------------
#////////////////////////////////////////////////////////////////////////////////////////
#-----------------------------------------------------------------------------------------

class Threat:
    def __init__(self, group : str, span : tuple, level : int, angle:int, board_size : int  = 15):
        t_func = get_index_transform_func(angle)
        self.cells = [t_func(index, board_size) for index in range(span[0], span[1])]
        self.group = group
        self.span = span
        self.level = level
        self.angle = angle

    def get_open_slots(self) -> set:
        l = []
        for m in re.finditer('01', self.group):            
            l.append(self.cells[m.span()[0]])
        for m in re.finditer('10', self.group):            
            l.append(self.cells[m.span()[1] - 1])
        return set(l)

    def get_counter_move(self):
        pass

    def get_next_level_threats(self) -> dict:
        pass

    def __hash__(self) -> int:
        return 23 * self.cells[0][0] + 29 * self.cells[0][1] + 71 * self.cells[1][0] + 73 * self.cells[1][1]
    
    def __eq__(self, other) -> bool:
        if not isinstance(other,Threat):
            return False        
        #Check
        if self.group == other.group \
            and self.cells[0] == other.cells[0] \
            and self.cells[-1] == other.cells[-1]:
            return True
        return False

    def __str__(self) -> str:
        return '(Threat / group = \'%s\', level = %d, span = (%d, %d))' % (self.group, self.level, self.span[0], self.span[1])

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
        '''
        self.w_winning_threats = generic_to_white_threat(WINNING_THREAT)
        self.b_winning_threats = generic_to_black_threat(WINNING_THREAT)

        self.w_forcing_threats = generic_to_white_threat(FORCING_THREATS)
        self.b_forcing_threats = generic_to_black_threat(FORCING_THREATS)    
        
        self.w_nforcing_threats = generic_to_white_threat(NON_FORCING_THREATS)
        self.b_nforcing_threats = generic_to_black_threat(NON_FORCING_THREATS)   
        '''
        self.w_threats = {5 : set(), 4 : set(), 3 : set()}
        self.b_threats = {5 : set(), 4 : set(), 3 : set()}
    
    def make_move(self,move,is_black):
        self.grid[move[0], move[1]] = 1 if is_black else 2 
        stone = '1' if is_black else '2' 
        self._update_boards(move, stone)
        self._update_threats(move, is_black)
        #self._update_threats(move, not is_black)
        self.moves.append((*move,is_black))
        
    def unmake_last_move(self):
        c,r,is_black = self.moves.pop()
        self.grid[c, r] = 0
        self._update_boards((c,r), '0')
        self._update_threats((c,r), is_black)

    def get_all_threats(self, black : bool) -> tuple:         
        win_threats = self._get_threats(self.b_winning_threats if black else self.w_winning_threats)
        force_threats = self._get_threats(self.b_forcing_threats if black else self.w_forcing_threats)
        nforce_threats = self._get_threats(self.b_nforcing_threats if black else self.w_nforcing_threats)

        #TEMPORANEO
        if black:
            self.b_winning_threats = win_threats
            self.b_forcing_threats = force_threats
            self.b_nforcing_threats = nforce_threats
        else:
            self.w_winning_threats = win_threats
            self.w_forcing_threats = force_threats
            self.w_nforcing_threats = nforce_threats

        return win_threats, force_threats, nforce_threats

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
        for lvl, ts in pthreats.items():
            for t in ts:
                #repr = self._get_repr_from_angle(t.angle)
                s = spans[t.angle]
                if t.span[0] >= s[0] or t.span[0] < s[1]:
                    to_remove.add(t)
                if t.span[1] > s[0] or t.span[1] <= s[1]:
                    to_remove.add(t)

            ts.difference_update(to_remove)                                                                                

    def _update_threats(self, last_move : tuple, black : bool):                
        #check new threats in intersecting lines
        span, line = self._get_line(last_move)
        span90, line90 = self._get_line90(last_move)
        span45, line45 = self._get_line_45(last_move)
        span315, line315 = self._get_line_315(last_move)

        spans = {0 : span, 45 : span45, 90 : span90, 315 : span315}

        self._prune_old_threats(spans, True)
        self._prune_old_threats(spans, False)   

        w_t = self.b_winning_threats if black else self.w_winning_threats
        f_t = self.b_forcing_threats if black else self.w_forcing_threats
        nf_t = self.b_nforcing_threats if black else self.w_nforcing_threats
        
        ts = self.b_threats if black else self.w_threats

        for lvl,patts in w_t.items():
            self._get_threats_in_repr(line, patts, lvl, ts, span[0], 0)
            self._get_threats_in_repr(line90, patts, lvl, ts, span90[0], 90)
            self._get_threats_in_repr(line45, patts, lvl, ts, span45[0], 45)
            self._get_threats_in_repr(line315, patts, lvl, ts, span315[0], 315)

        for lvl,patts in f_t.items():
            self._get_threats_in_repr(line, patts, lvl, ts, span[0], 0)
            self._get_threats_in_repr(line90, patts, lvl, ts, span90[0], 90)
            self._get_threats_in_repr(line45, patts, lvl, ts, span45[0], 45)
            self._get_threats_in_repr(line315, patts, lvl, ts, span315[0], 315)

        for lvl,patts in nf_t.items():
            self._get_threats_in_repr(line, patts, lvl, ts, span[0], 0)
            self._get_threats_in_repr(line90, patts, lvl, ts, span90[0], 90)
            self._get_threats_in_repr(line45, patts, lvl, ts, span45[0], 45)
            self._get_threats_in_repr(line315, patts, lvl, ts, span315[0], 315)


    def _get_threats_in_repr(self, repr:str, patterns, level:int, dst : dict, offset:int = 0, angle = 0):
        for patt in patterns:
            for match in re.finditer(patt, repr):
                span = match.span()
                if offset != 0:      
                    span = list(span)           
                    span[0] += offset
                    span[1] += offset
                    span = tuple(span)                
                if not isinstance(dst[level], set):
                    dst[level].append(Threat(match.group(), span, level, angle))
                else:
                    dst[level].add(Threat(match.group(), span, level, angle))

    def _get_threats(self, threat_patterns: dict):
        threats = {}
        for level,patts in threat_patterns.items():
            threats[level] = []
            self._get_threats_in_repr(self.board, patts, level, threats, angle = 0)
            self._get_threats_in_repr(self.board_90, patts, level, threats, angle = 90)
            self._get_threats_in_repr(self.board_45, patts, level, threats, angle = 45)
            self._get_threats_in_repr(self.board_315, patts, level, threats, angle = 315)
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

    def deepcopy(self):
        pass
    
    def _get_line(self, pos:tuple) -> tuple:
        extr = ((pos[0],0), (pos[1], self.size - 1))
        bounds = (cr_to_index(*extr[0], self.size), cr_to_index(*extr[1], self.size))
        return bounds, self.board[bounds[0] : bounds[1] + 1]


    def _get_line90(self, pos:tuple) -> tuple:
        extr = ((0,pos[0]), (self.size - 1, pos[1]))
        bounds = (cr_to_index90(*extr[0], self.size), cr_to_index90(*extr[1], self.size))
        return bounds, self.board_90[bounds[0] : bounds[1] + 1]

    def _get_line_45(self, pos : tuple) -> tuple:
        c,r = pos

        if r + c < self.size:
            extr = ((c + r,0),(0,c + r))            
        elif r + c == self.size - 1:
            extr = [(self.size - 1, 0),(0, self.size - 1)]            
        else:
            extr = ((self.size - 1, c + r - self.size + 1),(c + r - self.size + 1, self.size - 1))
 
        bounds = (cr_to_index45(*extr[1],self.size), cr_to_index45(*extr[0],self.size))
        return bounds, self.board_45[bounds[0] : bounds[1] + 1]      

    def _get_line_315(self, pos : tuple) -> tuple:
        c,r = pos
        
        if c < r:
            offset = c + self.size - 1 - r
            extr = ((self.size - 1 - offset, 0),(self.size - 1, offset))            
        elif r == c:
            extr = [(0, 0),(self.size - 1, self.size - 1)]            
        else:
            offset = r + self.size - 1 - c
            extr = ((0,  - offset + self.size - 1),( offset, self.size - 1))
             
        bounds = (cr_to_index315(*extr[0], self.size), cr_to_index315(*extr[1], self.size))
        return bounds, self.board_315[bounds[0] : bounds[1] + 1]    

    def _update_boards(self, move, stone):
        c,r = move
        self.board = replace_char(self.board, cr_to_index(c,r, self.size), stone)
        self.board_90 = replace_char(self.board_90, cr_to_index90(c,r, self.size), stone)
        self.board_45 = replace_char(self.board_45, cr_to_index45(c,r, self.size), stone)
        self.board_315 = replace_char(self.board_315, cr_to_index315(c,r, self.size), stone)

if __name__ == '__main__':
    t = time.time
    threats = precompute_threats()
    print('elapsed time:', round(time.time - t,4))

    for threat in threats[7].items():
        print(threat)
    
    
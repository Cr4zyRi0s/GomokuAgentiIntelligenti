import numpy as np
import re

WINNING_THREAT = ['[0Y3]X{5}[0Y3]']
FORCING_THREATS = {
    4 : [
    #Open fours
    '0X{4}0',
    '[Y3]X{2}0X{2}0X{2}[Y3]',
    '[Y3]X{3}0X0X{3}[Y3]',
    #Simple fours
    '[Y3]X{4}0[03Y]',
    '[Y3]X{2}0X{2}[Y3]',
    '[Y3]X0X{3}[Y3]',
    '[Y3]X{4}0X[Y3]',
    '[03Y]0X{4}[3Y]'],
    #Open threes    
    3 : []
}

NON_FORCING_THREATS = {}


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

def rot135(mat : np.array):
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


class Threat:
    def __init__(self, cells: list, pattern : str, level : int):
        self.cells = cells
        self.pattern = pattern
        self.level = level

    def get_counter_move(self):
        pass

    def get_next_level_threats(self) -> dict:
        pass

    def __eq__(self, other) -> bool:
        if not isinstance(other,Threat):
            return False        
        #Check
        if self.pattern == other.pattern \
            and self.cells[0] == other.cells[0] \
            and self.cells[-1] == other.cells[-1]:
            return True
        return False

class BoardState:
    def __init__(self,size = 15):
        self.size = size    
        self.moves = []   

        board = np.full((self.size + 2, self.size + 2), 3, dtype='int8')
        board[1:self.size + 1,1:self.size + 1] = 0
        board_45 = rot45(board)
        board_45 = board_45[2:2 * self.size + 1,:]
        board_135 = rot135(board)
        board_135 = board_135[2:2 * self.size + 1,:]
        board = board[1:self.size+1,:]

        self.grid = board[1:self.size+1, 1:self.size+1]
        self.board = ''.join([str(el) for el in board.flatten()])
        self.board_45 = ''.join([str(el) for el in board_45.flatten()])
        self.board_90 = ''.join([str(el) for el in board.flatten()])
        self.board_135 = ''.join([str(el) for el in board_135.flatten()])

        self.w_winning_threats = generic_to_white_threat(WINNING_THREAT)
        self.b_winning_threats = generic_to_white_threat(WINNING_THREAT)

        self.w_forcing_threats = generic_to_white_threat(FORCING_THREATS)
        self.b_forcing_threats = generic_to_black_threat(FORCING_THREATS)    
        
        self.w_nforcing_threats = generic_to_white_threat(NON_FORCING_THREATS)
        self.b_nforcing_threats = generic_to_black_threat(NON_FORCING_THREATS)   
        
        self.w_threats = {5 : set(), 4 : set(), 3 : set(), 2 : set(), 1 : set()}
        self.b_threats = {5 : set(), 4 : set(), 3 : set(), 2 : set(), 1 : set()}
    
    def make_move(self,move,is_black):
        stone = '1' if is_black else '2' 
        self._update_boards(move, stone)
        self.moves.append((*move,is_black))
        
    def unmake_last_move(self):
        c,r,_ = self.moves.pop()
        self._update_boards((c,r), '0')

    def get_current_threats(self, last_move : tuple, black : bool) -> tuple:         
        win_threats = self._get_threats(self.b_winning_threats if black else self.w_winning_threats)
        force_threats = self._get_threats(self.b_forcing_threats if black else self.w_forcing_threats)
        nforce_threats = self._get_threats(self.b_nforcing_threats if black else self.w_nforcing_threats)
        return win_threats, force_threats, nforce_threats

    def _get_threats(self, threat_patterns: dict):
        threats = {}
        for level,patts in threat_patterns:
            for patt in patts:
                for match in re.find_iter(patt, self.board):
                    span = match.span()
                    cells = [self._index_to_cr(i) for i in range(span[0], span[1])]
                    threats[level].append(Threat(cells, patt, level))
                for match in re.finditer(patt,self.board_90):
                    span = match.span()
                    cells = [self._index_to_cr(i) for i in range(span[0], span[1])]
                    threats[level].append(Threat(cells, patt, level))
                for match in re.finditer(patt,self.board_45):
                    span = match.span()
                    cells = [self._index_to_cr(i) for i in range(span[0], span[1])]
                    threats[level].append(Threat(cells, patt, level))
                for match in re.finditer(patt,self.self.board_135):
                    span = match.span()
                    cells = [self._index_to_cr(i) for i in range(span[0], span[1])]
                    threats[level].append(Threat(cells, patt, level))
        return threats

    def print_boards(self):
        b = np.array([list(self.board[i : i + self.size + 2]) for i in range(0,(self.size + 2) * self.size, self.size + 2)])
        print(b)
        b = np.array([list(self.board_90[i : i + self.size + 2]) for i in range(0,(self.size + 2) * self.size, self.size + 2)])
        print(b)
        b = np.array([list(self.board_45[i : i + self.size + 2]) for i in range(0,(self.size + 2) * (2 * self.size - 1), self.size + 2)])
        print(b)
        b = np.array([list(self.board_135[i : i + self.size + 2]) for i in range(0,(self.size + 2) * (2 * self.size - 1), self.size + 2)])
        print(b)

    def deepcopy(self):
        pass

    def _cr_to_index(self,c,r) -> int:
        return r * (self.size + 2) + c + 1
    def _cr_to_90index(self,c,r) -> int:
        return c * (self.size + 2) + r + 1
    def _cr_to_45index(self,c,r) -> int:
        return (r + c) * (self.size + 2) + c + 1
    def _cr_to_135index(self,c,r) -> int:
        return (r + self.size - c - 1) * (self.size + 2) + c + 1

    def _index_to_cr(self, index) -> tuple:
        r = index // (self.size + 2)
        c = index - r * (self.size + 2) - 1
        return c,r

    def _90index_to_cr(self, index) -> tuple:
        c = index // (self.size + 2)
        r = index - c * (self.size + 2) - 1
        return c,r
        
    def _45index_to_cr(self, index)  -> tuple:
        rc = index // (self.size + 2)
        c = index - rc * (self.size + 2) - 1
        r = rc - c
        return c,r
    
    def _135index_to_cr(self, index)  -> tuple:
        rc = index // (self.size + 2)
        c = index - rc * (self.size + 2) - 1
        r = rc - self.size + c + 1
        return c,r

    def _update_boards(self, move, stone):
        c,r = move
        self.board = replace_char(self.board, self._cr_to_index(c,r), stone)
        self.board_90 = replace_char(self.board_90, self._cr_to_90index(c,r), stone)
        self.board_45 = replace_char(self.board_45, self._cr_to_45index(c,r), stone)
        self.board_135 = replace_char(self.board_135, self._cr_to_135index(c,r), stone)

if __name__ == '__main__':
    state = BoardState(15)
    moves = [(i,1) for i in range(2,6)]

    for m in moves:
        state.make_move(m,True)
    

    '''
    test = [state._index_to_cr(state._cr_to_index(*m)) for m in moves]
    test_90 = [state._90index_to_cr(state._cr_to_90index(*m)) for m in moves]
    test_45 = [state._45index_to_cr(state._cr_to_45index(*m)) for m in moves]
    test_135 = [state._135index_to_cr(state._cr_to_135index(*m)) for m in moves]

    for i in range(5):
        if moves[i][0] != test[i][0] or moves[i][1] != test[i][1]:
            print('ERROR')
        if moves[i][0] != test_90[i][0] or moves[i][1] != test_90[i][1]:
            print('ERROR')
        if moves[i][0] != test_45[i][0] or moves[i][1] != test_45[i][1]:
            print('ERROR')
        if moves[i][0] != test_135[i][0] or moves[i][1] != test_135[i][1]:
            print('ERROR')

    print('done')
    '''
    '''
    state.make_move((0,1), True)
    state.make_move((1,1), True)
    state.make_move((2,1), True)
    state.make_move((3,1), True)
    state.make_move((4,1), True)
    state.print_boards()
    
    print('\n\nUNMAKING MOVES\n\n')
    state.unmake_last_move()
    state.unmake_last_move()
    state.unmake_last_move()
    state.unmake_last_move()
    state.unmake_last_move()
    state.print_boards()
    '''
    
import string
import random 
import numpy as np

DEFAULT_BOARD_SIZE = 15

def generate_random_string(length : int) -> str:
    letters = string.ascii_lowercase
    return ''.join([random.choice(letters) for _ in range(length)])

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

def cr_to_index(c,r,size : int = DEFAULT_BOARD_SIZE) -> int:
    return r * (size + 2) + c + 1
def cr_to_index90(c,r,size : int = DEFAULT_BOARD_SIZE) -> int:
    return c * (size + 2) + r + 1
def cr_to_index45(c,r,size : int = DEFAULT_BOARD_SIZE) -> int:
    return (r + c) * (size + 2) + c + 1
def cr_to_index315(c,r,size : int = DEFAULT_BOARD_SIZE) -> int:
    return (r + size - c - 1) * (size + 2) + c + 1

def index_to_cr(index,size : int = DEFAULT_BOARD_SIZE) -> tuple:
    r = index // (size + 2)
    c = index - r * (size + 2) - 1
    return c,r
def index90_to_cr(index,size : int = DEFAULT_BOARD_SIZE) -> tuple:
    c = index // (size + 2)
    r = index - c * (size + 2) - 1
    return c,r     
def index45_to_cr(index,size : int = DEFAULT_BOARD_SIZE)  -> tuple:
    rc = index // (size + 2)
    c = index - rc * (size + 2) - 1
    r = rc - c
    return c,r 

def index315_to_cr(index,size : int = DEFAULT_BOARD_SIZE)  -> tuple:
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

def no_moves_possible(board : np.array) -> bool:
    n_avail = np.count_nonzero(board)
    return n_avail >= board.shape[0] * board.shape[1]

def is_valid_move(col : int, row : int, board : np.array) -> bool:
    """Check if placing a stone at (col, row) is valid on board
    Args:
        col (int): column number
        row (int): row number
        board (object): board grid (size * size matrix)
    Returns:
        boolean: True if move is valid, False otherewise
    """
    if col < 0 or col >= board.shape[0]:
        return False
    if row < 0 or row >= board.shape[0]:
        return False    
    return board[col, row] == 0

if __name__ == '__main__':
    pass



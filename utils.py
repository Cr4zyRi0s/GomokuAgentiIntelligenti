import numpy as np

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
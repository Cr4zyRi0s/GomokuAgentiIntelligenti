import numpy as np

from bitarray import bitarray
from scipy.ndimage.interpolation import rotate

def get_board_bit_representation(board, check_black, rotation = 0)->bitarray:
    bits = bitarray()    
    for j in range(board.shape[1]):        
        for i in range(board.shape[0]):
            if check_black:
                bits.append(1 if board[j,i] == 1 else 0)
            else:
                bits.append(1 if board[j,i] == 2 else 0)
    return bits


if __name__ == "__main__":
    board = None
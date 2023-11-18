import numpy as np 
from tabulate import tabulate 

'''
White pieces (P=1, N=2, B=3, R=4, Q=5, K=6), 
Black pieces (P=-1, N=-2, B=-3, R=-4, Q=-5, K=-6)
lambda=1 : White's turn
lambda=-1 : Black's turn
'''

# board = np.array([
# [4, 2, 3, 5, 6, 3, 2, 4],
# [1, 1, 1, 1, 1, 1, 1, 1],
# [0, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0],
# [0, 0, 0, 0, 0, 0, 0, 0],
# [-1, -1, -1, -1, -1, -1, -1, -1],
# [-4, -2, -3, -5, -6, -3, -2, -4]
# ])
board = np.array([[0 for _ in range(8)] for _ in range(8)])
class Piece:
    def __init__(self, color, type, capturable=False):
        self.color = color
        self.type = type
        self.capturable = capturable

    def what_piece(self):
        return self.color * self.type

wp = Piece(1, 1)
bp = Piece(-1, 1)
wn = Piece(1, 2)
bn = Piece(-1, 2)
wb = Piece(1, 3)
bb = Piece(-1, 3)
wr = Piece(1, 4)
br = Piece(-1, 4)
wq = Piece(1, 5)
bq = Piece(-1, 5)
wk = Piece(1, 6)
bk = Piece(-1, 6)

PIECES = [wp,bp,wn,bn,wb,bb,wr,br,wq,bq,wk,bk]
for i in range(8):
    board[1,i] = Piece.what_piece(bp)
    board[6,i] = Piece.what_piece(wp)

first_row = [wr, wn, wb, wq, wk, wb, wn, wr]
last_row = [br, bn, bb, bq, bk, bb, bn, br]

for idx,piece in enumerate(last_row):
    board[0,idx] = Piece.what_piece(piece)

for idx,piece in enumerate(first_row):
    board[7,idx] = Piece.what_piece(piece)

labels_column = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H']
labels_row = [i in range(1,9)]


import random
print(random.randint(0,2))
for row in range(1,9):
    print(row)

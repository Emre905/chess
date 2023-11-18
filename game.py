class Game:
    def __init__(self):
        self.tiles = []
        for coll in range(1,9):
            row = []
            for roww in range(1,9):
                row.append(Tile(f'{coll}{roww}'))
            self.tiles.append(row)


    def setup_board(self):
        # Place pawns
        for col in range(1, 9):
            self.get_tile(f'2{col}').occupy(Pawn('white'))
            self.get_tile(f'7{col}').occupy(Pawn('black'))

        # Place other pieces
        white_back_row = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']
        black_back_row = white_back_row[::-1]  

        for col, piece in enumerate(white_back_row, start=1):
            self.get_tile(f'1{col}').occupy(eval(piece)("white"))
            self.get_tile(f'8{col}').occupy(eval(piece)("black"))


    def print_board(self):
        for i in range(1,9):
            row = ''
            for j in range(1,9):
                tile = self.get_tile(str(i)+str(j))
                if tile.is_occupied():
                    row += tile.piece.symbol + ' '
                else:
                    row += '0 '
            print(row)
                
        #  to get which tiles are occupied
        # self.pawn = Pawn('purple')
        # self.get_tile('11').occupy(self.pawn)
        # self.move(self.pawn, '11', '31')
        # # self.tiles[].occupy(self.pawn)
    
    def move(self, start, end):
        start = self.get_tile(start)
        end = self.get_tile(end)
        
        if start.is_occupied() and (not end.is_occupied() or start.piece.color != end.piece.color):
            piece = start.piece
            if piece.move(start, end, self):
                self.get_notation(piece, start, end)
                start.leave()
                end.occupy(piece)
                return True
                
        else:
            return False
        return False  # If the move is invalid
    
    # This function takes the move and converts it into standart notation with the help of coordinate function
    def get_notation(self, piece, start, end):
        end_new = self.coordinate(end.position)
        if end.is_occupied():
            notation = f'{piece.symbol}x{end_new}'
        else:
            notation = f'{piece.symbol}{end_new}'
        print(notation)

    # This function is just for converting the column part in end and giving corresponding letter for standart notation
    def coordinate(self, end):
        coordinates={'1':'A', '2':'B', '3':'C', '4':'D', '5':'E', '6':'F', '7':'G', '8':'H'}
        return coordinates.get(end[1]) + end[0]
    
    # This function is for getting tile numbers in easier way
    def get_tile(self, pos):
        r,c = pos[0], pos[1]
        return self.tiles[int(r)-1][int(c)-1]

    # This function will run the game according to all other rules
    def run(self):
        self.setup_board()
        while True:
            user_move = input('Make your move: ')
            start = user_move.split()[0]
            end = user_move.split()[1]
            self.move(start,end)
            self.print_board()

class Tile:
    def __init__(self, position) -> None:
        self.position = position 
        self.occupied = False
        self.piece = None
    
    def is_occupied(self):
        if self.piece: 
            return True
        else:
            return False
        
    def occupy(self, piece):
        self.piece = piece

    def leave(self):
        self.piece = None


class Piece:
    def __init__(self, color) -> None:
        self.color = color
        self.captured = False
        self.position = None

    def move(self, start, end):
        pass
    
    def __str__(self):
        return f'{self.__class__.__name__}'

    
class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        # self.attack = False
        self.symbol = 'P'
        if self.color == 'white':
            self.direction = 1
        else: 
            self.direction = -1

    def move(self, start, end, game):
        # Check if the pawn moves one square forward
        if end.position[1] == start.position[1] and int(end.position[0]) - int(start.position[0]) == self.direction:
            # Implement logic for moving one square forward
            if not end.is_occupied():
                self.position = end.position
                return True

        # Check if the pawn moves two squares forward from the starting row
        if end.position[1] == start.position[1] and \
                int(end.position[0]) - int(start.position[0]) == 2 * self.direction and \
                (start.position[0] == '2' or start.position[0] == '7'):
            # in_between_tile = game.get_tile(str((int(start.position[0])+1)) + start.position[1])
            # if not in_between_tile.is_occupied() and not end.is_occupied():
            if not self.is_blocked(start, end, game) and not end.is_occupied():
                self.position = end.position
                return True

        # Check if the pawn captures diagonally
        if (int(end.position[1]) - int(start.position[1]) == self.direction) or \
           (int(end.position[1]) - int(start.position[1]) == -self.direction)  and \
                int(end.position[0]) - int(start.position[0]) == self.direction:
            if end.is_occupied() and end.piece.color != self.color:
                end.piece.captured = True
                end.piece.position = None
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules
    
    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        if start_col != end_col:  # Check if there's a piece diagonally
            if end.is_occupied() and end.piece.color != self.color:
                return False  # Can capture enemy piece diagonally

        if start_col == end_col:  # Check for obstruction along the same column
            increment = 1 if self.color == 'white' else -1
            current_row = start_row + increment

            while current_row != end_row:
                current_tile = game.get_tile(str(current_row) + str(start_col))
                if current_tile.is_occupied():
                    return True  # Path is obstructed by another piece
                current_row += increment

        return False  # Path is clear for movement
    

class Bishop(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'B'

    def move(self, start, end, game):
        row_distance = abs(int(end.position[0]) - int(start.position[0]))
        col_distance = abs(int(end.position[1]) - int(start.position[1]))

        # Check if the Bishop moves diagonally
        if row_distance == col_distance:
            # Implement logic for diagonal movement
            if not self.is_blocked(start, end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_increment = 1 if end_row > start_row else -1
        col_increment = 1 if end_col > start_col else -1

        current_row, current_col = start_row + row_increment, start_col + col_increment

        while current_row != end_row and current_col != end_col:
            current_tile = game.get_tile(str(current_row) + str(current_col))
            if current_tile.is_occupied():
                return True  # Path is obstructed by another piece
            current_row += row_increment
            current_col += col_increment

        return False  # Path is clear for movement


class Knight(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'N'

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Check if the Knight moves in an L-shape
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            # Implement logic for Knight's L-shaped movement
            self.position = end.position
            return True

        return False  # Movement didn't match any valid rules

class Rook(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'R'

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        # Check if the Rook moves along a rank (row) or file (column)
        if start_row == end_row or start_col == end_col:
            # Implement logic for rank or file movement
            if not self.is_blocked(start, end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        # Check for obstruction along the same row or column
        if start_row == end_row:  # Same row
            col_increment = 1 if end_col > start_col else -1
            current_col = start_col + col_increment

            while current_col != end_col:
                current_tile = game.get_tile(str(start_row) + str(current_col))
                if current_tile.is_occupied():
                    return True  # Path is obstructed by another piece
                current_col += col_increment

        elif start_col == end_col:  # Same column
            row_increment = 1 if end_row > start_row else -1
            current_row = start_row + row_increment

            while current_row != end_row:
                current_tile = game.get_tile(str(current_row) + str(start_col))
                if current_tile.is_occupied():
                    return True  # Path is obstructed by another piece
                current_row += row_increment

        return False  # Path is clear for movement


class Queen(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'Q'

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_distance = abs(start_row - end_row)
        col_distance = abs(start_col - end_col)

        # Check if the Queen moves diagonally or along a rank or file
        if start_row == end_row or start_col == end_col or row_distance == col_distance:
            # Implement logic for diagonal or rank/file movement
            if not self.is_blocked(start, end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_increment = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_increment = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_increment, start_col + col_increment

        # Check for obstruction along the same row, column, or diagonal
        while current_row != end_row or current_col != end_col:
            current_tile = game.get_tile(str(current_row) + str(current_col))
            if current_tile.is_occupied():
                return True  # Path is obstructed by another piece

            current_row += row_increment
            current_col += col_increment

        return False  # Path is clear for movement

class King(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'K'

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Check if the King moves within one square in any direction
        if row_diff <= 1 and col_diff <= 1:
            # Implement logic for King's movement
            if not self.is_blocked(end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, tile, game):
        # Check if other pieces are threatening the end
        return False


game = Game()
game.run()
from tabulate import tabulate 

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

        # Storing king positions to later to define is_check function
        self.white_king_position = '15'
        self.black_king_position = '85'


    def print_board(self):
        board = []
        # column_labels = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        column_labels = [str(i) for i in range(1,9)]
        column_labels.insert(0, '')
        for i in range(1, 9):
            row = [i]
            for j in range(1, 9):
                tile = self.get_tile(str(i) + str(j))
                if tile.is_occupied():
                    row.append(tile.piece.symbol)
                else:
                    row.append(' ')
            board.append(row)

        board = board[::-1]
        print(tabulate(board, headers=column_labels, tablefmt='fancy_grid'))

    # Function to check if a king is under threat
    def track_king(self, color):
        king_position = self.white_king_position if color == 'white' else self.black_king_position
        return king_position

    def get_possible_moves(self, color):
        possible_moves = []

        for row in self.tiles:
            for tile in row:
                if tile.is_occupied() and tile.piece.color == color:
                    piece = tile.piece
                    for i in range(1, 9):
                        for j in range(1, 9):
                            end_tile = self.get_tile(f"{i}{j}")
                            if piece.move(tile, end_tile, self) and not piece.is_blocked(tile, end_tile, game):
                                possible_moves.append((tile.position, end_tile.position))

        return possible_moves

    def move(self, start, end):
        start = self.get_tile(start)
        end = self.get_tile(end)
        
        if start.is_occupied() and not end.is_occupied():
            piece = start.piece
            if piece.move(start, end, self):
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
            possible_moves = self.get_possible_moves('white')  # Change 'white' to the current player's color
            print(f"There are {len(possible_moves)} moves. These are: ")
            for move in possible_moves:
                print(move)
            user_move = input('Make your move: ')
            try:
                if len(user_move.split()) == 2:
                    start = user_move.split()[0]
                    end = user_move.split()[1]
                    if 10 < int(start) <89 and 10 < int(end) <89:
                        self.move(start,end)
                        self.print_board()
                    else:
                        print('Please enter 2 coordinates between 11-88')
                        continue
                elif user_move.lower() == 'resign':
                    print('Game has ended')
                    print(self.track_king('white'))
                    break
                else:
                    print('Please enter valid moves')
                    continue
            except ValueError:
                print('Please enter coordinates as numbers')
                continue


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
    
    def get_possible_moves(self, position, game):
        # Default implementation for pieces that don't move
        return []
    
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
            if not self.is_blocked(start, end, game) and not end.is_occupied():
                self.position = end.position
                return True

        # Check if the pawn captures diagonally
        if abs(int(end.position[1]) - int(start.position[1])) == 1 and \
                int(end.position[0]) - int(start.position[0]) == self.direction:
            if end.is_occupied() and not self.is_blocked(start, end, game):
                end.piece.captured = True
                end.piece.position = None
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules
    
    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])
        
        if end.is_occupied():
            if end.piece.color == self.color:
                return True

        if start_col == end_col:  # Check for obstruction along the same column
            current_row = start_row + self.direction

            while current_row != end_row:
                current_tile = game.get_tile(str(current_row) + str(start_col))
                if current_tile.is_occupied():
                    return True  # Path is obstructed by another piece
                current_row += self.direction
                
        if abs(start_col - end_col) == 1 and \
            (end_row - start_row) == self.direction:  # Check if there's a piece diagonally
            if end.is_occupied():
                return False  # Can capture enemy piece diagonally

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
        
        if end.is_occupied():
            if end.piece.color == self.color:
                return True

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
    def is_blocked(self, start, end, game):
        if end.is_occupied():
            if end.piece.color == self.color:
                return True
        else:
            return False

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
        
        if end.is_occupied():
            if end.piece.color == self.color:
                return True
            
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

        if end.is_occupied():
            if end.piece.color == self.color:
                return True
            
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
            if not self.is_blocked(start, end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start, end, game):
        if end.is_occupied:
            return True
        else:
            return False


game = Game()
game.run()
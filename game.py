from tabulate import tabulate 
'''current problems: 
- en passant and castling is just a sketch, I'll add it

to add:
- all notations
- evaluator
''' 

class Game:
    def __init__(self):
        self.tiles = []
        self.player = 'white'
        self.player_opposite = 'black'
        self.possible_moves_opposite = self.get_possible_moves(self.player_opposite)
        self.legal_moves_opposite = self.get_legal_moves(self.player_opposite)

        self.legal_moves = self.get_legal_moves(self.player)
        self.legal_moves_notation = self.get_legal_moves_notation(self.player)
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
        self.white_rook1_position = '11'
        self.white_rook2_position = '18'
        self.black_rook1_position = '81'
        self.black_rook2_position = '88'


    def setup_board_check(self):
        self.get_tile('55').occupy(King('white'))
        self.get_tile('67').occupy(King('black'))
        self.get_tile('68').occupy(Queen('black'))
        self.get_tile('22').occupy(Pawn('white'))
        self.white_king_position = '55'
        self.black_king_position = '67'

    def setup_board_castle(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('18').occupy(Rook('white'))
        self.get_tile('11').occupy(Rook('white'))
        self.white_king_position = '15'
        self.black_king_position = '85'

    def print_board(self):
        board = []
        column_labels = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
#         column_labels = [str(i) for i in range(1,9)]
#         column_labels.insert(0, '')
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

    def get_possible_moves(self, color):
        possible_moves = []

        for row in self.tiles:
            for tile in row:
                if tile.is_occupied() and tile.piece.color == color:
                    piece = tile.piece
                    for i in range(1, 9):
                        for j in range(1, 9):
                            end_tile = self.get_tile(f"{i}{j}")
                            start_pos = tile.position
                            end_pos = end_tile.position
                            if piece.move(tile, end_tile, self):
                                possible_moves.append((start_pos, end_pos))  
        return possible_moves
    
    def get_legal_moves(self, color):
        possible_moves = self.get_possible_moves(color)
        legal_moves = []
        for move in possible_moves:
            if self.is_legal_move(move[0], move[1]):
                legal_moves.append(move)
        return legal_moves
    
    def get_legal_moves_notation(self,color):
        legal_moves = self.get_legal_moves(color)
        legal_moves_notation = []
        for move in legal_moves:
            piece = self.get_tile(move[0]).piece
            notation = self.get_notation(piece, self.get_tile(move[0]), self.get_tile(move[1]))
            legal_moves_notation.append(notation)
        return legal_moves, legal_moves_notation
        
    # This function will simulate a move and decide if it's legal. I put is_check function inside this function to avoid recursions
    def is_legal_move(self, start_pos, end_pos):
        start = self.get_tile(start_pos)
        end = self.get_tile(end_pos)
        self.player = start.piece.color

        piece = start.piece
        temp_piece = end.piece
        # Simulate the move
        start.leave()
        end.occupy(piece)
        # If a king has moved the position needs to be updated
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_position = end.position
            if piece.color == 'black':
                self.black_king_position = end.position

        # Check if such move gives a check
        in_check = self.is_check(self.player)
        is_kings_kissing = self.is_kings_neighbor()

        # Putting all rules together
        combined_rule_check = (not in_check) and (not is_kings_kissing)

        start.occupy(piece)
        end.occupy(temp_piece)

        # Reverse the king position
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_position = start.position
            if piece.color == 'black':
                self.black_king_position = start.position
        return combined_rule_check

    # This function will decide if the player is under check 
    def is_check(self, player):
        self.player_opposite = 'black' if self.player == 'white' else 'white'
        possible_moves_opposite = self.get_possible_moves(self.player_opposite)
        king_position = self.track_king(self.player)[0]
        # If king is in a position that opponent threats
        for idx in possible_moves_opposite: # Try to make this self and remove upper line
            if king_position == idx[1]:
                return True
        return False
    
    # This function will decide if 2 kings are at adjacent squares (it's illegal move)
    def is_kings_neighbor(self):
        king1, king2 = self.track_king(self.player)
    
        if abs(int(king1[0]) - int(king2[0])) <= 1 and \
        abs(int(king1[1]) - int(king2[1])) <= 1:
            # print(f'kings are here: {king1}, {king2}')
            return True
        return False
        
    
    def move(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        
        # Check if castling is attempted
        if self.castle(start, end):
            self.round_count += 1
            return True

        # # Check if en passant capture is possible
        # self.en_passant_capture(start, end)
        
        if not start_tile.is_occupied():
            return False
                    
        elif not self.is_legal_move(start, end):
            print('Illegal move')
            return False
        else:
            piece = start_tile.piece
            start_tile.leave()
            end_tile.occupy(piece)

        # Update position of kings, if they have moved
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_position = end_tile.position
            if piece.color == 'black':
                self.black_king_position = end_tile.position

        # Check for pawn promotion
        if isinstance(piece, Pawn) and (end_tile.position[0] in ('1', '8')) and piece.is_promote:
            piece = self.promote_pawn(piece)
            end_tile.occupy(piece)

        self.round_count += 1
        return True
    
    # This function takes the move and converts it into standart notation with the help of coordinate function
    def get_notation(self, piece, start, end):
        start_new = self.coordinate(start.position)
        end_new = self.coordinate(end.position)

        if end.is_occupied(): #capturing a piece
            notation = f'{piece.symbol}x{end_new}'
            if isinstance(piece, Pawn):
                notation = start_new[0] + notation[1:]
        else:
            notation = f'{piece.symbol}{end_new}'
            if isinstance(piece, Pawn):
                notation = notation[1:]

        return notation

    # This function is just for converting the column part in end and giving corresponding letter for standart notation
    def coordinate(self, end):
        coordinates={'1':'A', '2':'B', '3':'C', '4':'D', '5':'E', '6':'F', '7':'G', '8':'H'}
        return coordinates.get(end[1]) + end[0]
    
    # This function is for getting tile numbers in easier way
    def get_tile(self, pos):
        r,c = pos[0], pos[1]
        return self.tiles[int(r)-1][int(c)-1]
    
    def track_king(self, color):
        king_positions = [self.white_king_position, self.black_king_position] if color == 'white' else \
            [self.black_king_position, self.white_king_position]
        return king_positions
    
    def promote_pawn(self, pawn):
        promote_to = input('''Choose which piece you\'d like: 
                      Queen
                      Rook
                      Bishop
                      Knight: ''')
        color = pawn.color
        if promote_to.lower() == 'queen':
            return Queen(color)
        elif promote_to.lower() == 'rook':
            return Rook(color)
        elif promote_to.lower() == 'bishop':
            return Bishop(color)
        elif promote_to.lower() == 'knight':
            return Knight(color)
        else:
            # self.promote(start, end, game)
            return Queen(color)
        
    def en_passant_capture(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)

        # Check if the move is an en passant capture
        if isinstance(start_tile.piece, Pawn) and abs(int(start[1]) - int(end[1])) == 1:
            captured_pawn_pos = f"{start[0]}{end[1]}"  # Get the position of the captured pawn

            # Remove the captured pawn from the board
            captured_tile = self.get_tile(captured_pawn_pos)
            captured_tile.leave()

    def castle(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        
        if isinstance(start_tile.piece, King) and abs(int(start[1]) - int(end[1])) == 2 and start[0] == end[0]:
            # Check conditions for castling
            if King.is_castle(self, start, end, game):
            
                # Move the King
                king = start_tile.piece
                start_tile.leave()
                end_tile.occupy(king)

                # Move the Rook
                if end[1] == 'g' or end[1] == '7':
                    rook_start = self.get_tile(f'{end[0]}8')  # Adjust for the Rook's position
                    rook_end = self.get_tile(f'{end[0]}f')
                else:
                    rook_start = self.get_tile(f'{end[0]}1')  # Adjust for the Rook's position
                    rook_end = self.get_tile(f'{end[0]}d')

                rook = rook_start.piece
                rook_start.leave()
                rook_end.occupy(rook)

            return True

        return False
        

    # This function will run the game according to all other rules
    def run(self):
        # self.setup_board()
        # self.setup_board_check()
        self.setup_board_castle()
        self.round_count = 0
        while True:
            self.player = 'black' if self.round_count % 2 else 'white'
            self.legal_moves, self.legal_moves_notation = self.get_legal_moves_notation(self.player)
            self.legal_moves_opposite_notation = self.get_legal_moves_notation(self.player_opposite)[1]

            # if it's checkmate (there are no legal moves), the game ends
            if len(self.legal_moves) == 0:
                self.print_board()
                print(f'Checkmate! {self.player} player won')
                break

            print(f"There are {len(self.legal_moves)} moves for {self.player_opposite}. These are: ") # Should be self.player but somehow got reversed
            print(f"All possible moves are {','.join(self.legal_moves_notation)}") 
            print(f"legal opposite moves are {','.join(self.legal_moves_opposite_notation)}")

            # Printing the board and starting with first move
            self.print_board()
            user_move = input('Make your move: ')
            try:
                # Checking if the input is given by standard notation
                if user_move in self.legal_moves_notation:
                    idx = self.legal_moves_notation.index(user_move)
                    self.move(self.legal_moves[idx][0],self.legal_moves[idx][1])

                # Checking if the input is given by coordinates
                elif len(user_move.split()) == 2:
                    split_move = user_move.split()
                    if (split_move[0], split_move[1]) in self.legal_moves:
                        self.move(split_move[0], split_move[1])
        
                elif user_move.lower() == 'resign':
                    print(f'Game has ended. {self.player} won')
                    break

                else:
                    print('Please enter 2 coordinates between 11-88')
                    continue
            except ValueError:
                print('Please enter 2 coordinates between 11-88')
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
        return []
    
    def __str__(self):
        return f'{self.__class__.__name__}'

    
class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'P'
        self.is_promote = False
        self.is_en_passant = False
        self.direction = 1 if self.color == 'white' else -1

    def move(self, start, end, game):
        if not self.is_blocked(start, end, game):

            # This part is for promoting a Pawn
            if (start.position[0] == '7' and end.position[0] == '8' and self.color == 'white') or \
                (start.position[0] == '2' and end.position[0] == '1' and self.color == 'black'):  
                self.is_promote = True

            self.position = end.position
            return True

        return False  # Movement didn't match any valid rules

    
    def is_blocked(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])
        row_diff = end_row - start_row
        col_diff = end_col - start_col

        if not end.is_occupied():
            # Moving one square
            if col_diff == 0 and row_diff == self.direction:
                return False # Can advance 1 move forward
            # Moving two square
            if col_diff == 0 and row_diff == 2 * self.direction and start_row in [2, 7]:
                mid_tile = game.get_tile(str(start_row + 2 * self.direction) + str(start_col))
                if not mid_tile.is_occupied():
                    return False # Can advance 2 squares in the beginning
                return True
        else:
            # Capturing diagonally
            if abs(col_diff) == 1 and row_diff == self.direction and self.color != end.piece.color:
                return False
            
            # # Checking for en passant. Marking such pieces 
            # if start.position[0] == '2' and end.position[0] == '4' and self.color == 'white':
            #     self.self.is_en_passant = True
            #     return False
            # elif start.position[0] == '7' and end.position[0] == '5' and self.color == 'black':
            #     self.self.is_en_passant = True
            #     return False
            return True  # Return True if the move is successful

        return True

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
        if ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)) and not self.is_blocked(start, end, game) :
            # Implement logic for Knight's L-shaped movement
            self.position = end.position
            return True

        return False  # Movement didn't match any valid rules
    def is_blocked(self, start, end, game):
        if end.is_occupied() and end.piece.color == self.color:
            return True 
        else:
            return False

class Rook(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'R'
        self.has_moved = False

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        # Check if the Rook moves along a rank (row) or file (column)
        if start_row == end_row or start_col == end_col:
            # Implement logic for rank or file movement
            if not self.is_blocked(start, end, game):
                self.position = end.position
                self.has_moved = True
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
    
    # This function will check if a rook can castle
    def is_castle(self, game):
        if not self.has_moved:
            return True
        return False


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
        self.has_moved = False

    def move(self, start, end, game):
        start_row, start_col = int(start.position[0]), int(start.position[1])
        end_row, end_col = int(end.position[0]), int(end.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        if self.is_castle(start, end, game):
            return True

        # Check if the King moves within one square in any direction
        if row_diff < 2 and col_diff < 2:
            if not self.is_blocked(start, end, game):
                self.position = end.position
                return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start, end, game):
        if end.is_occupied() and end.piece.color == self.color:
            return True
        else:
            return False
        
    # This function will check if the king can castle
    def is_castle(self, start, end, game):

        if not self.has_moved:
            if abs(int(start.position[1]) - int(end.position[1])) == 2 and start.position[0] == end.position[0]:
                # self.has_moved = True
                return True
        return False
        

game = Game()
game.run()
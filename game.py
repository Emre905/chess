import itertools as it
import numpy as np
from time import time
import timeit 
# import matplotlib.pyplot as plt 
# from IPython.display import display, Image
'''
current problems: 
1- legal moves get called after calling castle function. therefore there may be illegal castling moves (but not playable)
2- get legal moves swaps colors

to improve:
- find_checkmate_in1() should be faster for deeper analysis 
- Castling and en passant returns few outputs, could be better
- Think how to use self.position for piece classes (maybe to store positions of pieces)

to add:
- evaluator
- all notations (no need I guess)
''' 

class Game:
    def __init__(self):
        self.tiles = []
        self.player = 'white'
        self.player_opposite = 'black'
        self.possible_moves_opposite = []
        self.legal_moves_opposite = []
        self.legal_moves = []
        self.legal_moves_notation = []
        self.legal_mw = []
        self.legal_mb = []

        self.has_moved = False
        self.king_positions = ['15', '85']

        self.played_moves = [('11','11')]
        self.PIECES = {
    "R": "♖", "r": "♜",
    "N": "♘", "n": "♞",
    "B": "♗", "b": "♝",
    "Q": "♕", "q": "♛",
    "K": "♔", "k": "♚",
    "P": "♙", "p": "♟",
}
        keys = [str(i+1) for i in range(9)]  
        values = list('ABCDEFGH')
        self.coordinates = { k:v for (k,v) in zip(keys, values)} 

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

    def setup_board_check(self):
        self.get_tile('55').occupy(King('white'))
        self.get_tile('67').occupy(King('black'))
        self.get_tile('68').occupy(Queen('black'))
        self.get_tile('22').occupy(Pawn('white'))

    def setup_board_castle(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        # self.get_tile('17').occupy(Rook('white'))
        self.get_tile('11').occupy(Rook('white'))
        self.get_tile('81').occupy(Rook('black'))
        self.get_tile('88').occupy(Rook('black'))

    def setup_board_castle2(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('84').occupy(King('black'))
        self.get_tile('25').occupy(Rook('white'))
        self.get_tile('23').occupy(Rook('white'))
        self.get_tile('11').occupy(Rook('white'))

    def setup_board_pawn(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('72').occupy(Pawn('white'))
        self.get_tile('53').occupy(Pawn('white'))
        self.get_tile('74').occupy(Pawn('black'))
        self.get_tile('77').occupy(Rook('white'))

    def setup_board_pawn2(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('42').occupy(Pawn('black'))
        self.get_tile('21').occupy(Pawn('white'))
        self.get_tile('23').occupy(Pawn('white'))

    def setup_board_checkmate(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('77').occupy(Rook('white'))
        self.get_tile('38').occupy(Rook('white'))

    def setup_board_checkmate2(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('77').occupy(Rook('white'))
        self.get_tile('38').occupy(Rook('white'))
        self.get_tile('36').occupy(Bishop('white'))
        self.get_tile('28').occupy(Bishop('white'))
        self.get_tile('22').occupy(Pawn('white'))
        self.get_tile('23').occupy(Pawn('white'))
        self.get_tile('24').occupy(Pawn('white'))
        self.get_tile('25').occupy(Pawn('white'))

    def print_board(self):
        board = []
        column_labels = list('ABCDEFGH')
        fg = lambda text, color: "\33[38;5;" + str(color) + "m" + text + "\33[0m"
        bg = lambda text, color: "\33[48;5;" + str(color) + "m" + text + "\33[0m"
        for i in range(8, 0, -1):
            row = ""
            for j in range(1, 9):
                # Determine background color based on position for the checkered pattern
                if (i + j) % 2 == 0:
                    background_color = 208  # Use black for even-positioned squares
                else:
                    background_color = 255  # Use white for odd-positioned squares

                tile = self.get_tile(str(i) + str(j))
                if tile.is_occupied():
                    # Apply background color to the entire square including text space for pieces
                    if tile.piece.color == 'white':
                        text = f" {self.PIECES.get(tile.piece.symbol)} "
                    else:
                        text = f" {self.PIECES.get(tile.piece.symbol.lower())} "
                else:
                    text = " " * 3  # Space for squares without pieces

                # Apply background color to the entire square
                colored_text = fg(bg(text, background_color), 0)
                row += colored_text
            
            print(i, row)
        print("   " + "  ".join(column_labels))

    def get_possible_moves(self, player):
        possible_moves = []
        for row in self.tiles:
            for start_tile in row:
                if start_tile.is_occupied() and start_tile.piece.color == player:
                    piece = start_tile.piece
                    color = piece.color
                    start = start_tile.position
                    possible_ends = piece.move_recommend(start_tile)
                    for end in possible_ends:
                        end_tile = self.get_tile(end)
                        if piece.move(start_tile, end_tile, self):
                            possible_moves.append((start, end))
        return possible_moves
    
    def get_possible_moves_improved(self):
        pos_mw = []
        pos_mb = []
        for row in self.tiles:
            for start_tile in row:
                if start_tile.is_occupied():
                    piece = start_tile.piece
                    color = piece.color
                    start = start_tile.position
                    possible_ends = piece.move_recommend(start_tile)
                    for end in possible_ends:
                        end_tile = self.get_tile(end)
                        if piece.move(start_tile, end_tile, self):
                            pos_mw.append((start, end)) if color == 'white' else pos_mb.append((start, end))
                            # print(f'end squares for {start} is {end}')
        return pos_mw, pos_mb
    
    def get_legal_moves_improved(self):
        pos_mw, pos_mb = self.get_possible_moves_improved()
        legal_mw = []
        legal_mb = []
        legal_mw_not = []
        legal_mb_not = []
        for move in pos_mw:
            if self.is_legal_move(move[0], move[1]):
                legal_mw.append(move)
                # This 5 lines are for appending notation, not so necessary
                start_tile = self.get_tile(move[0])
                end_tile = self.get_tile(move[1])
                piece = start_tile.piece
                notation = self.get_notation(piece, start_tile, end_tile)
                legal_mw_not.append(notation)
        for move in pos_mb:
            if self.is_legal_move(move[0], move[1]):
                legal_mb.append(move)
                start_tile = self.get_tile(move[0])
                end_tile = self.get_tile(move[1])
                piece = start_tile.piece
                notation = self.get_notation(piece, start_tile, end_tile)
                legal_mb_not.append(notation)
        return legal_mw, legal_mb, legal_mw_not, legal_mb_not
    
    def evaluate_board(self):
        piece_values = {'P': 1, 'B': 3, 'N': 3, 'R': 5, 'Q': 9, 'K': 200}
        sum_white = 0
        sum_black = 0
        # pieces_white = []
        # pieces_black = []
        for row in self.tiles:
            for tile in row:
                if tile.is_occupied():
                    piece_symbol = tile.piece.symbol
                    if tile.piece.color == 'white':
                        # pieces_white.append(piece_symbol)
                        sum_white += piece_values.get(piece_symbol)
                    if tile.piece.color == 'black':
                        # pieces_white.append(piece_symbol)
                        sum_black += piece_values.get(piece_symbol)    
        return sum_white, sum_black
    
    def get_legal_moves(self, player):
        possible_moves = self.get_possible_moves(player)
        legal_moves = []
        for move in possible_moves:
            if self.is_legal_move(move[0], move[1]):
                legal_moves.append(move)
        return legal_moves
    
    def get_legal_moves_notation(self, player):
        legal_moves = self.get_legal_moves(player)
        legal_moves_notation = []
        for move in legal_moves:
            piece = self.get_tile(move[0]).piece
            notation = self.get_notation(piece, self.get_tile(move[0]), self.get_tile(move[1]))
            legal_moves_notation.append(notation)
        return legal_moves_notation, legal_moves
        
    # This function will simulate a move and decide if it's legal. I put is_check function inside this function to avoid recursions
    def is_legal_move(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)

        if not start_tile.is_occupied():
            return False
        self.player = start_tile.piece.color
        piece = start_tile.piece
        temp_piece = end_tile.piece

        # Check if castling is possible
        if isinstance(piece, King) and abs(int(start[1]) - int(end[1])) == 2:
            if not self.castle(start, end)[0]:
                return False

        # Check if en passant capture is possible
        elif isinstance(piece, Pawn) and abs(int(start[1]) - int(end[1])) == 1 and not end_tile.is_occupied():
            if not self.en_passant_capture(start, end)[0]:
                return False
            
        # Simulate the move
        start_tile.leave()
        end_tile.occupy(piece)

        # If a king has moved the position needs to be updated
        if isinstance(piece, King):
            self.update_king_position(start, end)

        # Check if such move gives a check or makes 2 kings touch each other
        in_check = self.is_check(self.player)
        is_kings_kissing = self.is_kings_neighbor()

        # Putting all rules together
        combined_rule_check = in_check or is_kings_kissing

        start_tile.occupy(piece)
        end_tile.occupy(temp_piece)

        # Reverse the king position
        if isinstance(piece, King):
            self.update_king_position(end, start)
                
        return not combined_rule_check

    # This function will decide if the player is under check 
    def is_check(self, player):
        player_opposite = 'black' if player == 'white' else 'white'
        possible_moves_opposite = self.get_possible_moves(player_opposite)
        king_position = self.track_king(player)

        # If king is in a position that opponent threats
        for idx in possible_moves_opposite: # Try to make this self and remove upper line
            if king_position == idx[1]:
                return True
        return False
    
    def is_check_test(self, player):
        self.player_opposite = 'black' if self.player == 'white' else 'white'
        possible_moves = self.get_possible_moves(self.player)
        king_position = self.track_king(self.player_opposite)
        # If king is in a position that opponent threats
        for idx in possible_moves: # Try to make this self and remove upper line
            if king_position == idx[1]:
                return True
        return False
    
    # This function will decide if 2 kings are at adjacent squares (it's illegal move)
    def is_kings_neighbor(self):
        king1, king2 = self.king_positions
    
        if abs(int(king1[0]) - int(king2[0])) <= 1 and \
        abs(int(king1[1]) - int(king2[1])) <= 1:
            return True
        return False
    
    def update_king_position(self, start, end):
        piece = self.get_tile(end).piece
        piece.position = end
        if piece.color == 'white':
            self.king_positions[0] = piece.position
        elif piece.color == 'black':
            self.king_positions[1] = piece.position
    
    def move(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        piece = start_tile.piece
        
        if not start_tile.is_occupied():
            return False

        # Check if castling is attempted
        if isinstance(piece, King) and abs(int(start[1]) - int(end[1])) == 2:
            if self.castle(start, end)[0]:
                rook_start_tile, rook_end_tile = self.castle(start, end)[1:3]
                # Move the King
                king = start_tile.piece
                start_tile.leave()
                end_tile.occupy(king)

                # Move the rooks
                rook = rook_start_tile.piece
                rook_start_tile.leave()
                rook_end_tile.occupy(Rook(piece.color))
            else:
                return False
        
        # Check for en passant
        elif isinstance(piece, Pawn) and abs(int(start[1]) - int(end[1])) == 1 and not end_tile.is_occupied():
            if self.en_passant_capture(start, end)[0]:
                captured_tile = self.en_passant_capture(start, end)[1]
                start_tile.leave()
                captured_tile.leave()
                end_tile.occupy(piece)
                    
        # Check for pawn promotion
        elif isinstance(piece, Pawn) and (end_tile.position[0] in ['1', '8']):
            promoted_piece = self.promote_pawn(piece)
            start_tile.leave()
            end_tile.occupy(promoted_piece)

        elif not self.is_legal_move(start, end):
            print('Illegal move')
            return False
        
        else:
            start_tile.leave()
            end_tile.occupy(piece)

        # Update position of kings, if they have moved
        if isinstance(piece, King):
            piece.has_moved = True
            self.update_king_position(start, end)
        
        # Update position of rooks, if they have moved
        elif isinstance(piece, Rook):
            piece.has_moved = True

        return True
    
    def simulate_move(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        piece = start_tile.piece
        
        if not start_tile.is_occupied():
            return False

        # Check if castling is attempted
        if isinstance(start_tile.piece, King) and abs(int(start[1]) - int(end[1])) == 2:
            if self.castle(start, end)[0]:
                rook_start_tile, rook_end_tile = self.castle(start, end)[1:3]
                # Move the King
                king = start_tile.piece
                start_tile.leave()
                end_tile.occupy(king)
                self.update_king_position(start, end)

                # Move the rooks
                rook = rook_start_tile.piece
                rook_start_tile.leave()
                rook_end_tile.occupy(rook)
            else:
                return False
        
        # Check for en passant
        elif isinstance(piece, Pawn) and abs(int(start[1]) - int(end[1])) == 1 and not end_tile.is_occupied():
            if self.en_passant_capture(start, end)[0]:
                captured_tile = self.en_passant_capture(start, end)[1]
                start_tile.leave()
                captured_tile.leave()
                end_tile.occupy(piece)
                    
        # Check for pawn promotion
        elif isinstance(piece, Pawn) and (end_tile.position[0] in ['1', '8']):
            promoted_piece = self.promote_pawn(piece)
            start_tile.leave()
            end_tile.occupy(promoted_piece)

        elif not self.is_legal_move(start, end):
            print('Illegal move')
            return False
        
        else:
            start_tile.leave()
            end_tile.occupy(piece)
            # Update position of kings, if they have moved
            if isinstance(piece, King):
                self.update_king_position(start, end)
    
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
                if start_new[0] != end_new[0]: # If the move was en passant
                    notation = f'{start_new[0]}x{end_new}'

        return notation

    # These 2 functions are for converting the user input into standart notation
    def coordinate(self, end):
        return self.coordinates.get(end[1]) + end[0]

    def coordinate_reverse(self, end):
        reverse_coordinates={value:key for (key,value) in self.coordinates.items()}
        return end[1] + reverse_coordinates.get(end[0])
    
    # This function is for getting tile numbers in easier way
    def get_tile(self, pos):
        r,c = pos[0], pos[1]
        return self.tiles[int(r)-1][int(c)-1]
    
    def track_king(self, color):
        king_positions = self.king_positions[0] if color == 'white' else self.king_positions[1]
        return king_positions
    
    def promote_pawn(self, pawn):
        while True:
            promote_to = input('''Choose which piece you'd like (It's enough to enter the first letter of the piece): 
                        Queen
                        Rook
                        Bishop
                        Knight: ''').lower()
            color = pawn.color
            if promote_to == 'queen' or promote_to == 'q':
                return Queen(color)
            elif promote_to == 'rook' or promote_to == 'r':
                return Rook(color)
            elif promote_to == 'bishop' or promote_to == 'b':
                return Bishop(color)
            elif promote_to == 'knight'or promote_to == 'k':
                return Knight(color)
            else:
                print('Please enter a valid piece name')
                continue
        
    def en_passant_capture(self, start, end):
        previous_move = self.played_moves[-1]
        prev_start = previous_move[0]
        prev_end = previous_move[1]
        captured_tile = self.get_tile(prev_end)
        captured_pawn = captured_tile.piece
        # Check if the previous move fits to an en passant move
        if isinstance(captured_pawn, Pawn) and abs(int(prev_start[0]) - int(prev_end[0])) == 2 and end[1] == prev_end[1]:
            # if start == '42': 
            # import pdb;pdb.set_trace()
            return [True, captured_tile]
        return [False]
    

    def castle(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        
        if isinstance(start_tile.piece, King) and abs(int(start[1]) - int(end[1])) == 2 and start[0] == end[0]:
            if self.is_check(start_tile.piece.color) or start_tile.piece.has_moved:
                return [False]

            self.player = 'black' if self.round_count % 2 else 'white'
            self.legal_moves_opposite = self.legal_mw if self.player == 'black' else self.legal_mb

            if end[1] == '3' or end[1] == '7':
                # if start == '85' and end == '83' and self.round_count == 1:
                #     import pdb; pdb.set_trace()
                rook_start_tile = self.get_tile(f'{start[0]}1') if end[1] == '3' else self.get_tile(f'{start[0]}8')
                # Check if the corresponding rook has moved
                if isinstance(rook_start_tile.piece, Rook) and not rook_start_tile.piece.has_moved:
                    # Check if the middle squares are under threat
                    middle_tile = self.get_tile(f'{start[0]}{(int(end[1]) + int(start[1]))//2}')
                    middle_square = middle_tile.position
                    if middle_tile.is_occupied():
                        return [False]
                    for move in self.legal_moves_opposite: # should be opposite
                        if move[1] == middle_square or move[1] == end:
                            return [False]
                    rook_end_tile = middle_tile
                    return [True, rook_start_tile, rook_end_tile]        
            return [False]

        return [False]
    
    def find_checkmate_in1(self):
        notations = []
        for move in self.legal_moves:
            start_tile = self.get_tile(move[0])
            end_tile = self.get_tile(move[1])
            temp_piece = end_tile.piece
            piece = start_tile.piece
            color = piece.color
            opp_color = 'black' if color == 'white' else 'white'

            # Adding extra condition for promotion of a pawn 
            if move[1][0] in ['1', '8'] and isinstance(piece, Pawn):
                for promoted_piece in [Knight, Bishop, Rook, Queen]:
                    end_tile.occupy(promoted_piece(color))
                    if self.get_tile(move[1]).piece.color != color:
                        end_tile.leave()
                        continue
                    start_tile.leave()
                    prom_piece = end_tile.piece
                    self.legal_moves_opposite = self.get_legal_moves(opp_color)
                    start_tile.occupy(Pawn(color))
                    end_tile.leave()
                    end_tile.occupy(temp_piece)
                    if not self.legal_moves_opposite:
                        notation = self.get_notation(start_tile.piece, start_tile, end_tile)
                        notation += f'={prom_piece.symbol}' 
                        notations.append(notation)
                continue
            
            # Adding extra condition for castling
            elif isinstance(piece, King) and abs(int(move[0][1]) - int(move[1][1])) == 2:
                notation = self.get_notation(start_tile.piece, start_tile, end_tile)
                self.simulate_move(move[0], move[1])
                self.legal_moves_opposite = self.get_legal_moves(opp_color)
                is_check = self.is_check(opp_color)

                rook_start_tile = self.get_tile(f'{move[0][0]}1') if move[1][1] == '3' else self.get_tile(f'{move[0][0]}8')
                rook_end_tile = self.get_tile(f'{move[0][0]}{(int(move[1][1]) + int(move[0][1]))//2}')
                rook_end_tile.leave()
                rook_start_tile.occupy(Rook(color))
                if not self.legal_moves_opposite and is_check:
                    notations.append(notation)

            # Adding extra condition for en passant capture
            elif isinstance(piece, Pawn) and abs(int(move[0][1]) - int(move[1][1])) == 1 and not end_tile.is_occupied():
                notation = self.get_notation(start_tile.piece, start_tile, end_tile)
                self.simulate_move(move[0], move[1])
                self.legal_moves_opposite = self.get_legal_moves(opp_color)
                is_check = self.is_check(opp_color)
                
                if color == 'white':
                    captured_pawn = self.get_tile(f'{str(int(move[1][0])-1)}{move[1][1]}') 
                else:
                    captured_pawn = self.get_tile(f'{str(int(move[1][0])+1)}{move[1][1]}') 
                captured_pawn.occupy(Pawn(opp_color))
            else:
                self.simulate_move(move[0], move[1])
                self.legal_moves_opposite = self.get_legal_moves(opp_color)

                if not self.legal_moves_opposite and self.is_check(opp_color): # If the opponent has no moves it's checkmate
                    start_tile.occupy(end_tile.piece)
                    end_tile.leave()
                    end_tile.occupy(temp_piece)
                    notation = self.get_notation(start_tile.piece, start_tile, end_tile)
                    notations.append(notation)
                    continue
                
            start_tile.occupy(piece)
            end_tile.leave()
            end_tile.occupy(temp_piece)
        return notations

    # This function will do the necessary print statements and get the user input to make the run function shorter
    def handle_setup(self):
        self.legal_mw, self.legal_mb, self.legal_mw_not, self.legal_mb_not = self.get_legal_moves_improved()
        # thie line shouldn't be repeated. check current problems -1
        self.legal_mw, self.legal_mb, self.legal_mw_not, self.legal_mb_not = self.get_legal_moves_improved()
        self.player = 'black' if self.round_count % 2 else 'white'
        self.player_opposite = 'black' if self.player == 'white' else 'white'
        self.legal_moves = self.legal_mw if self.player == 'white' else self.legal_mb
        self.legal_moves_notation = self.legal_mw_not if self.player == 'white' else self.legal_mb_not

        print(f"There are {len(self.legal_mw)} moves for white. Legal moves are: {','.join(self.legal_mw_not)}") 
        print(f"There are {len(self.legal_mb)} moves for black. Legal moves are: {','.join(self.legal_mb_not)}")
        print(f'Turn for {self.player}')

        # Printing the board and starting with first move
        self.print_board()

        # if it's checkmate or stalemate (there are no legal moves), the game ends
        if not self.legal_moves:
            if self.is_check(self.player):
                print(f'Checkmate! {self.player_opposite} player won')
            else:
                print('Stelamete! The game is draw')
            return False

        if self.is_check(self.player):
            print('Check!')
        
        # Print if there's checkmate in one
        start_time = time()
        is_checkmate_in1 = self.find_checkmate_in1()
        if is_checkmate_in1:
            print(f"{len(is_checkmate_in1)} checkmate in 1 move has found: {','.join(is_checkmate_in1)}")
        print(f"--- {time() - start_time} seconds ---")
        self.player = 'black' if self.round_count % 2 else 'white'
        self.player_opposite = 'black' if self.player == 'white' else 'white'

        user_move = input('Make your move: ').strip().upper()
        
        if len(user_move) > 1 and user_move[1] == 'X':
            notation = list(user_move)
            # Replace X with x
            notation[1] = 'x'
            user_move = ''.join(notation)
            
        if user_move.lower() == 'resign':
            print(f'Game has ended. {self.player_opposite} won')
            return False

        return user_move

    # This function will run the game according to all other rules
    def run(self):
        print('''
Welcome to the chess game! To make a move you have 3 options: 
1- Use the chess notation (without +, ++, =, o-o, o-o-o)
2- Use locations as (row, column). For example in the beginning NF3 would be '17 36' referring to the piece at 17 goes to 36. 
3- Use locations as (letter, row). For example in the beginning NF3 would be 'G1 F3' referring to the piece at G1 goes to F3''')
        self.setup_board_castle()
        self.round_count = 0

        while True:
            user_move = self.handle_setup()  # Get all the prints and necessary variables
            if not user_move:   # Finish the game if there's a checkmate
                break
            try:
                # Check if the input is given by standard notation
                if user_move in self.legal_moves_notation:
                    idx = self.legal_moves_notation.index(user_move)
                    self.move(self.legal_moves[idx][0],self.legal_moves[idx][1])
                    self.played_moves.append((self.legal_moves[idx][0],self.legal_moves[idx][1]))
                    self.round_count += 1

                # Check if the input is given by coordinates
                elif len(user_move.split()) == 2:
                    split_move = user_move.split()
                    # If the move is given like '17 36'
                    if (split_move[0], split_move[1]) in self.legal_moves:
                        self.move(split_move[0], split_move[1])
                        self.played_moves.append((split_move[0], split_move[1]))
                        self.round_count += 1
                    # If the move is given like 'E2 E4'
                    elif (self.coordinate_reverse(split_move[0]), self.coordinate_reverse(split_move[1])) in self.legal_moves:
                        self.move(self.coordinate_reverse(split_move[0]), self.coordinate_reverse(split_move[1]))
                        self.played_moves.append((self.coordinate_reverse(split_move[0]), self.coordinate_reverse(split_move[1])))
                        self.round_count += 1

                else:
                    print('Please enter 2 coordinates between 11-88')
                    continue

            except (IndexError, TypeError):
                print('Please enter 2 coordinates between 11-88')
                continue


    def print_evaluation_score(self):
            white_score, black_score = self.evaluate_board()
            # Calculate the proportions
            total = white_score + black_score
            white_score_proportion = white_score / total
            black_score_proportion = black_score / total

            # Create a bar chart with stacked bars
            plt.figure(figsize=(1, 5))

            # Plot the white
            plt.bar(0, white_score_proportion, color='white')

            # Plot the second value on top of the first with another color
            plt.bar(0, black_score_proportion, bottom=white_score_proportion, color='black')

            # Remove y-axis ticks and label
            plt.xticks([])
            plt.xlabel('')
            # Set axis limits
            plt.ylim(0, 1)
            plt.xlim(0, 0.3)

            plt.show()
            # Convert the plot to an image
            # plt.savefig('plot.png', bbox_inches='tight')

            # Display the image
            # display(Image('plot.png'))

    def print_board_as_png(self):
        # table = self.print_board()
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, table, ha='center', va='center', fontsize=12)
        ax.axis('off')
        plt.savefig('printed_board.png')
        plt.show()

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

    def move(self, start_tile, end_tile, game):
        if not self.is_blocked(start_tile, end_tile, game):
            return True
        return False  # Movement didn't match any valid rules
    
    def get_possible_moves(self, position, game):
        return []
    
    def __str__(self):
        return f'{self.__class__.__name__}'

    
class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'P'
        self.direction = 1 if self.color == 'white' else -1
    
    def is_blocked(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])
        row_diff = end_row - start_row
        col_diff = end_col - start_col

        if not end_tile.is_occupied():
            # Moving one square
            if col_diff == 0 and row_diff == self.direction:
                return False # Can advance 1 move forward
            # Moving two square
            if col_diff == 0 and row_diff == 2 * self.direction and start_row in [2, 7]:
                mid_tile = game.get_tile(str(start_row + self.direction) + str(start_col))
                if not mid_tile.is_occupied():
                    return False # Can advance 2 squares in the beginning
                return True
            
            # Check for en passant
            if abs(col_diff) == 1 and row_diff == self.direction and not end_tile.is_occupied():
                if self.direction * start_row in [5, -4]:  # Check if the pawn is at 5th(for white) or 4th(for black) row
                    if game.en_passant_capture(start_tile.position, end_tile.position):
                        return False
                    return True
        else:
            # Capturing diagonally
            if abs(col_diff) == 1 and row_diff == self.direction and self.color != end_tile.piece.color:
                return False
            return True  # Return True if the move is successful

        return True
    
    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position
        direction = 1 if start_tile.piece.color == 'white' else -1

        potential_moves = np.array([(2,0), (1,0), (1,1), (1,-1)])
        potential_moves = (direction, 1) * potential_moves

        for move in potential_moves:
            row, col = int(start[0]) + move[0], int(start[1]) + move[1]
            if 1 <= row <= 8 and 1 <= col <= 8:
                end_squares.append(f"{row}{col}")

        return end_squares

class Bishop(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'B'

    def is_blocked(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_increment = 1 if end_row > start_row else -1
        col_increment = 1 if end_col > start_col else -1

        current_row, current_col = start_row + row_increment, start_col + col_increment
        
        if end_tile.is_occupied():
            if end_tile.piece.color == self.color:
                return True

        while current_row != end_row and current_col != end_col:
            current_tile = game.get_tile(str(current_row) + str(current_col))
            if current_tile.is_occupied():
                return True  # Path is obstructed by another piece
            current_row += row_increment
            current_col += col_increment

        return False  # Path is clear for movement
    
    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position

        # Generating potential moves for bishop (diagonal)
        for i in range(1, 9):
            if i != int(start[0]):
                if 1<= int(start[1]) - int(start[0]) + i <= 8:
                    end_squares.append(f"{i}{int(start[1]) - int(start[0]) + i}")  # Diagonal top-right
                if 1<= int(start[1]) + int(start[0]) - i <= 8:
                    end_squares.append(f"{i}{int(start[1]) + int(start[0]) - i}")  # Diagonal top-left

        return end_squares



class Knight(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'N'

    def move(self, start_tile, end_tile, game):
        if not self.is_blocked(start_tile, end_tile, game):
            return True
        
        return False  # Movement didn't match any valid rules
    
    def is_blocked(self, start_tile, end_tile, game):
        if end_tile.is_occupied() and end_tile.piece.color == self.color:
            return True 
        
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Check if the Knight moves in an L-shape
        if row_diff * col_diff == 2:
            return False
        
        return True
        
    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position

        # This part will give us all combinations of 2 and 1 with altering signs 
        numbers = np.array(list(it.permutations([1,2])))
        directions = np.array(list(it.product([1,-1], repeat = 2)))
        potential_moves = [x*y for x in numbers for y in  directions]

        for move in potential_moves:
            row, col = int(start[0]) + move[0], int(start[1]) + move[1]
            if 1 <= row <= 8 and 1 <= col <= 8:
                end_squares.append(f"{row}{col}")

        return end_squares


class Rook(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'R'
        self.has_moved = False

    def is_blocked(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])
        
        if end_tile.is_occupied():
            if end_tile.piece.color == self.color:
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

    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position

        # Generating potential moves for rook (vertical and horizontal)
        for i in range(1, 9):
            if i != int(start[0]):
                end_squares.append(f"{i}{start[1]}")  # Moves along row
            if i != int(start[1]):
                end_squares.append(f"{start[0]}{i}")  # Moves along column

        return end_squares


class Queen(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'Q'

    def is_blocked(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_increment = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_increment = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_increment, start_col + col_increment

        if end_tile.is_occupied():
            if end_tile.piece.color == self.color:
                return True
            
        # Check for obstruction along the same row, column, or diagonal
        while current_row != end_row or current_col != end_col:
            current_tile = game.get_tile(str(current_row) + str(current_col))
            if current_tile.is_occupied():
                return True  # Path is obstructed by another piece

            current_row += row_increment
            current_col += col_increment

        return False  # Path is clear for movement

    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position

        # Generating potential moves for queen (combination of rook and bishop movements)
        for i in range(1, 9):
            if i != int(start[0]):
                end_squares.append(f"{i}{start[1]}")  # Moves along rows
                if 1<= int(start[1]) - int(start[0]) + i <= 8:
                    end_squares.append(f"{i}{int(start[1]) - int(start[0]) + i}")  # Diagonal top-right
                if 1<= int(start[1]) + int(start[0]) - i <= 8:
                    end_squares.append(f"{i}{int(start[1]) + int(start[0]) - i}")  # Diagonal top-left
            if i != int(start[1]):
                end_squares.append(f"{start[0]}{i}")  # Moves along columns

        return end_squares

class King(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.symbol = 'K'
        self.has_moved = False
        self.position = '15' if self.color == 'white' else '85'

    def is_blocked(self, start_tile, end_tile, game):
        if end_tile.is_occupied() and end_tile.piece.color == self.color:
            return True
        
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)
        
        # Check if the King moves within one square in any direction
        if row_diff < 2 and col_diff < 2:
            return False

        elif abs(int(start_tile.position[1]) - int(end_tile.position[1])) == 2 and start_tile.position[0] == end_tile.position[0]:
            return False

        return True  # Path is obstructed by another piece
        
    def move_recommend(self, start_tile):
        end_squares = []
        start = start_tile.position

        directions = [1,-1,0]
        potential_moves = list(it.product(directions, repeat = 2)) # Adding regular moves
        potential_moves.remove((0,0)) # Removing pass move
        potential_moves.extend([(0,2), (0,-2)]) # Adding castling options

        for move in potential_moves:
            row, col = int(start[0]) + move[0], int(start[1]) + move[1]
            if 1 <= row <= 8 and 1 <= col <= 8:
                end_squares.append(f"{row}{col}")

        return end_squares

game = Game()
game.run()
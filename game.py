from tabulate import tabulate 
import itertools as it
import numpy as np
from time import time
# import matplotlib.pyplot as plt 
# from IPython.display import display, Image
'''
current problems: 
- check why calling self.get_legal_moves swaps colors (not a big issue)

to improve:
- find_checkmate_in1() works okay but slow for more possible moves (around O(logx)).
- Castling and en passant returns few outputs, could be better
- Fix overlapping parts in piece is_blocked and move functions
- is_check doesn't work to print if it's check in that position. made is_check_test to fix it but can be a better solution

to add:
- all notations
- evaluator
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

        self.has_moved = False
        self.white_has_castled = False
        self.black_has_castled = False
        self.rook11_has_moved = False
        self.rook18_has_moved = False
        self.rook81_has_moved = False
        self.rook88_has_moved = False
        self.white_king_position = None
        self.black_king_position = None

        self.played_moves = [('11','11')]

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
        self.get_tile('17').occupy(Rook('white'))
        self.get_tile('11').occupy(Rook('white'))
        self.get_tile('84').occupy(Rook('black'))
        self.get_tile('88').occupy(Rook('black'))
        self.white_king_position = '15'
        self.black_king_position = '85'

    def setup_board_pawn(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('72').occupy(Pawn('white'))
        self.get_tile('53').occupy(Pawn('white'))
        self.get_tile('74').occupy(Pawn('black'))
        self.white_king_position = '15'
        self.black_king_position = '85'

    def setup_board_checkmate(self):
        self.get_tile('15').occupy(King('white'))
        self.get_tile('85').occupy(King('black'))
        self.get_tile('77').occupy(Rook('white'))
        self.get_tile('38').occupy(Rook('white'))
        self.white_king_position = '15'
        self.black_king_position = '85'

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
        self.white_king_position = '15'
        self.black_king_position = '85'

    def print_board(self):
        board = []
        column_labels = list(' ABCDEFGH')
#         column_labels = [' '] + [str(i) for i in range(1,9)]
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
        table = tabulate(board, headers=column_labels, tablefmt='fancy_grid')
        print(table)

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
    def is_legal_move(self, start_pos, end_pos):
        start = self.get_tile(start_pos)
        end = self.get_tile(end_pos)

        if not start.is_occupied():
            return False
        self.player = start.piece.color
        piece = start.piece
        temp_piece = end.piece

        # Check if castling is possible
        if isinstance(piece, King) and abs(int(start_pos[1]) - int(end_pos[1])) == 2:
            if not self.castle(start_pos, end_pos)[0]:
                return False

        # Check if en passant capture is possible
        elif isinstance(piece, Pawn) and abs(int(start_pos[1]) - int(end_pos[1])) == 1 and not end.is_occupied():
            if not self.en_passant_capture(start_pos, end_pos)[0]:
                return False
            
        # Simulate the move
        start.leave()
        end.occupy(piece)
        # If a king has moved the position needs to be updated

        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_position = end.position
            if piece.color == 'black':
                self.black_king_position = end.position

        # Check if such move gives a check or makes 2 kings touch each other
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
            elif piece.color == 'black':
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
    
    def is_check_test(self, player):
        self.player_opposite = 'black' if self.player == 'white' else 'white'
        possible_moves = self.get_possible_moves(self.player)
        king_position = self.track_king(self.player_opposite)[0]
        # If king is in a position that opponent threats
        for idx in possible_moves: # Try to make this self and remove upper line
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

                # Move the rooks
                rook = rook_start_tile.piece
                rook_start_tile.leave()
                rook_end_tile.occupy(rook)

                if king.color == 'white':
                    self.white_has_castled = True
                if king.color == 'black':
                    self.black_has_castled = True
            else:
                return False
        
        # Check if en_passant is attempted
        elif isinstance(piece, Pawn) and abs(int(start[1]) - int(end[1])) == 1 and not end_tile.is_occupied():
            if self.en_passant_capture(start, end)[0]:
                captured_tile = self.en_passant_capture(start, end)[1]
                start_tile.leave()
                captured_tile.leave()
                end_tile.occupy(piece)
                    
        elif not self.is_legal_move(start, end):
            print('Illegal move')
            return False
        else:
            start_tile.leave()
            end_tile.occupy(piece)

        # Update position of kings, if they have moved
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_position = end_tile.position
            if piece.color == 'black':
                self.black_king_position = end_tile.position
        
        # Update position of rooks, if they have moved
        elif isinstance(piece, Rook):
            if start == '11':
                self.rook11_has_moved = True
            if start == '18':
                self.rook18_has_moved = True
            if start == '81':
                self.rook81_has_moved = True
            if start == '88':
                self.rook88_has_moved = True

        # Check for pawn promotion
        elif isinstance(piece, Pawn) and (end_tile.position[0] in ('1', '8')):
            piece = self.promote_pawn(piece)
            end_tile.occupy(piece)

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
                if start_new[0] != end_new[0]: # If the move was en passant
                    notation = f'{start_new[0]}x{end_new}'

        return notation

    # This function is just for converting the column part in end and giving corresponding letter for standart notation
    def coordinate(self, end):
        coordinates={'1':'A', '2':'B', '3':'C', '4':'D', '5':'E', '6':'F', '7':'G', '8':'H'}
        return coordinates.get(end[1]) + end[0]
    
    def coordinate_reverse(self, end):
        coordinates={'A':'1', 'B':'2', 'C':'3', 'D':'4', 'E':'5', 'F':'6', 'G':'7', 'H':'8'}
        return end[1] + coordinates.get(end[0])
    
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

        previous_move = self.played_moves[-1]
        prev_start = previous_move[0]
        prev_end = previous_move[1]
        captured_tile = self.get_tile(prev_end)
        captured_pawn = captured_tile.piece
        # Check if the previous move fits to an en passant move
        if isinstance(captured_pawn, Pawn) and abs(int(prev_start[0]) - int(prev_end[0])) == 2 and end[1] == prev_end[1]:
            return True, captured_tile
        return [False]
    

    def castle(self, start, end):
        start_tile = self.get_tile(start)
        end_tile = self.get_tile(end)
        
        if isinstance(start_tile.piece, King) and abs(int(start[1]) - int(end[1])) == 2 and start[0] == end[0]:

            if self.is_check(start_tile.piece.color):
                return [False]
            if start_tile.piece.color == 'white' and self.white_has_castled:
                return [False]
            elif start_tile.piece.color == 'black' and self.black_has_castled:
                return [False]
            
            self.legal_moves_opposite = self.get_possible_moves(self.player_opposite)  # Better to put this line in a previous function
            # print(self.legal_moves_opposite)
            if end[1] == '7':
                # Check if the corresponding rook has moved
                if ((not self.rook18_has_moved and start_tile.piece.color == 'white') or \
                (not self.rook88_has_moved and start_tile.piece.color == 'black')) and isinstance(self.get_tile(f'{end[0]}8').piece, Rook):
                    # Check if the middle squares are under threat
                    middle_tile = self.get_tile(f'{end[0]}6')
                    middle_square = middle_tile.position
                    if middle_tile.is_occupied():
                        return [False]
                    for move in self.legal_moves_opposite:
                        if move[1] in [middle_square, start, end]:
                            return [False]
                    rook_start_tile = self.get_tile(f'{end[0]}8')  # Adjust for the Rook's position
                    rook_end_tile = self.get_tile(f'{end[0]}6')
                    return [True, rook_start_tile, rook_end_tile]

            elif end[1] == '3':
                if ((not self.rook11_has_moved and start_tile.piece.color == 'white') or \
                (not self.rook81_has_moved and start_tile.piece.color == 'black')) and isinstance(self.get_tile(f'{end[0]}1').piece, Rook):
            
                    # Check if the middle squares are under threat
                    middle_tile = self.get_tile(end[0] + '4')
                    middle_square = middle_tile.position 
                    if middle_tile.is_occupied():
                        return [False]
                    for move in self.legal_moves_opposite:
                        if move[1] in [middle_square, start, end]:
                            return [False]
                        
                    rook_start_tile = self.get_tile(f'{end[0]}1')  # Adjust for the Rook's position
                    rook_end_tile = self.get_tile(f'{end[0]}4')

                    return [True, rook_start_tile, rook_end_tile]
        
            return [False]

        return [False]
    
    def find_checkmate_in1(self):
        for move in self.legal_moves:
            start_time = time()
            start_tile = self.get_tile(move[0])
            end_tile = self.get_tile(move[1])
            temp_piece = end_tile.piece

            self.move(move[0], move[1])
            self.legal_moves_opposite = self.get_legal_moves(self.player_opposite)

            if not self.legal_moves_opposite: # If the opponent has no moves it's checkmate
                start_tile.occupy(end_tile.piece)
                end_tile.leave()
                end_tile.occupy(temp_piece)
                notation = self.get_notation(start_tile.piece, start_tile, end_tile)
                return notation
            
            start_tile.occupy(end_tile.piece)
            end_tile.leave()
            end_tile.occupy(temp_piece)
        else:
            return False
        
    def test(self):
        time1 = time()
        for i in range(30):
            self.setup_board()
            a, b, c, d = self.get_legal_moves_improved()
        print(f"--- {time() - time1} seconds ---")

        time2 = time()
        for i in range(30):
            self.setup_board()
            a, b = self.get_legal_moves_notation('white')
            c, d = self.get_legal_moves_notation('black')
        print(f"--- {time() - time2} seconds ---")

    # This function will do the necessary print statements and get the user input to make the run function shorter
    def handle_setup(self):
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
        if self.find_checkmate_in1():
            print(f'checkmate in 1 move has found: {self.find_checkmate_in1()}')
        print(f"--- {time() - start_time} seconds ---")

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
        self.setup_board()
        # self.setup_board_checkmate2()
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
                    if (split_move[0], split_move[1]) in self.legal_moves: # If the move is given like '17 36'
                        self.move(split_move[0], split_move[1])
                        self.played_moves.append((split_move[0], split_move[1]))
                        self.round_count += 1

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
        self.is_en_passant = False
        self.direction = 1 if self.color == 'white' else -1

    def move(self, start_tile, end_tile, game):
        if not self.is_blocked(start_tile, end_tile, game):
            return True
        return False  # Movement didn't match any valid rules

    
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

    def move(self, start_tile, end_tile, game):
        row_distance = abs(int(end_tile.position[0]) - int(start_tile.position[0]))
        col_distance = abs(int(end_tile.position[1]) - int(start_tile.position[1]))

        # Check if the Bishop moves diagonally
        if row_distance == col_distance:
            # Implement logic for diagonal movement
            if not self.is_blocked(start_tile, end_tile, game):
                self.position = end_tile.position
                return True

        return False  # Movement didn't match any valid rules

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
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Check if the Knight moves in an L-shape
        if ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)) and not self.is_blocked(start_tile, end_tile, game) :
            # Implement logic for Knight's L-shaped movement
            self.position = end_tile.position
            return True

        return False  # Movement didn't match any valid rules
    def is_blocked(self, start_tile, end_tile, game):
        if end_tile.is_occupied() and end_tile.piece.color == self.color:
            return True 
        else:
            return False
        
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

    def move(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        # Check if the Rook moves along a rank (row) or file (column)
        if start_row == end_row or start_col == end_col:
            # Implement logic for rank or file movement
            if not self.is_blocked(start_tile, end_tile, game):
                self.position = end_tile.position
                self.has_moved = True
                return True

        return False  # Movement didn't match any valid rules

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
    
    # This function will check if a rook can castle
    def is_castle(self, game):
        if not self.has_moved:
            return True
        return False

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

    def move(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_distance = abs(start_row - end_row)
        col_distance = abs(start_col - end_col)

        # Check if the Queen moves diagonally or along a rank or file
        if start_row == end_row or start_col == end_col or row_distance == col_distance:
            if not self.is_blocked(start_tile, end_tile, game):
                self.position = end_tile.position
                return True

        return False  # Movement didn't match any valid rules

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
        self.has_castled = False

    def move(self, start_tile, end_tile, game):
        start_row, start_col = int(start_tile.position[0]), int(start_tile.position[1])
        end_row, end_col = int(end_tile.position[0]), int(end_tile.position[1])

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        if self.is_blocked(start_tile, end_tile, game):
            return False

        # Check if the King moves within one square in any direction
        elif row_diff < 2 and col_diff < 2:
            self.position = end_tile.position
            return True

        elif abs(int(start_tile.position[1]) - int(end_tile.position[1])) == 2 and start_tile.position[0] == end_tile.position[0]:
            return True

        return False  # Movement didn't match any valid rules

    def is_blocked(self, start_tile, end_tile, game):
        if end_tile.is_occupied() and end_tile.piece.color == self.color:
            return True
        else:
            return False
        
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
# game.test()
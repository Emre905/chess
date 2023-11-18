class Game:
    def __init__(self):
        self.tiles = []
        for coll in range(1,9):
            row = []
            for roww in range(1,9):
                row.append(Tile(f'{coll}{roww}'))
            self.tiles.append(row)
        
        for i in range(1,9):
            self.get_tile('2'+str(i)).occupy(Pawn('white'))
            self.get_tile('7'+str(i)).occupy(Pawn('black'))
            # print(self.get_tile('1'+str(i)).piece)
            # print(self.get_tile('1'+str(i)).position)

        # for i in range(1,9):
        #     for j in range(1,9):
        #         tile = self.get_tile(str(i)+str(j))
        #         if tile.is_occupied():
        #             print(f'yes {i}{j} is {tile.piece.symbol}')

        # pawn capture attempt: successfull
        # self.get_tile('38').occupy(Pawn('white'))
        # self.get_tile('47').occupy(Pawn('black'))
        # print(self.get_tile('38').piece.color)
        # print(self.get_tile('47').piece.color)
        # self.move('38','47')
        # print(self.get_tile('47').piece.color)
        # print(self.get_tile('38').piece)

        # advance a pawn from 53 to 43 to 33 to 23
        self.move('21','41')
        self.move('22','32')
        self.move('23','13')
        self.move('24','64')

        self.move('71','61')
        self.move('72','52')
        self.move('73','83')
        self.move('74','44')
        self.print_board()
    


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
        if start.is_occupied():
            piece = start.piece
            if piece.move(start, end, self):
                start.leave()
                end.occupy(piece)
                return True
        return False  # If the move is invalid
    
    
    def get_tile(self, pos):
        r,c = pos[0], pos[1]
        return self.tiles[int(r)-1][int(c)-1]

    def run(self):
        pass



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

    # def __str__(self):
    #     return self.color
    # to get names instead of memory locations


    def move(self, start, end):
        pass

class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color)
        self.attack = False
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
            in_between_tile = game.get_tile(str((int(start.position[0])+1)) + start.position[1])
            if not in_between_tile.is_occupied() and not end.is_occupied():
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



game = Game()
class Game:
    def __init__(self):
        self.tiles = []
        for coll in range(1,9):
            row = []
            for roww in range(1,9):
                row.append(Tile(f'{coll}{roww}'))
            self.tiles.append(row)
        
        for i in range(1,9):
            self.get_tile('5'+str(i)).occupy(Pawn('purple'))
            print(self.get_tile('1'+str(i)).piece)
            print(self.get_tile('1'+str(i)).position)

        # for i in range(1,9):
        #     for j in range(1,9):
        #         tile = self.get_tile(str(i)+str(j))
        #         if tile.is_occupied():
        #             print(f'yes {i}{j} is {tile.piece.symbol}')
        self.move('52', '62')
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
        piece = start.piece
        start.leave()
        end.occupy(piece)

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

    def move(self, start, end):
        pass

game = Game()
        

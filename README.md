# Chess Game on Terminal

## :chess_pawn: Project description
This is a classic Chess game played on terminal

## How to play
There are 3 options for making a move (can be used interchangeably)

Let's say it's beginning of the game and we want to play
the knight on G1 to F3. The input (bold part) can be one of the following:

 - Coordinates:  **17 36**. Use (row, column) format. The piece on 17 moves to 36.
 - Coordinates with letters: **G1 F3** or **g1 f3**. The piece on G1 moves to F3.
 - Standard notation: **NF3** or **nf3**. Standard chess notation (doesn't work when there are 2 same type of pieces 
 and they can move to the target square. Castling doesn't have a 
special notation like normal. Short castle for white is simply **KG1** or corresponding notation from other 2 options.)

List of possible moves in standard notation will be printed before each move. 

## Extra Features
- Checkmate in 1 move notifier. When the current player has checkmate in 1, the move is printed

- Tabulate is used for printing board. So, it looks colorful and cells have fixed width

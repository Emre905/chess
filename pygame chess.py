import pygame
import os

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((560, 560))
pygame.display.set_caption("Chess")

# Directory path where your images are stored
image_folder = r"C:\Users\Aš\Desktop\chess\pieces"  # Use a raw string for the path

# Load all images in the directory
images = {}
for filename in os.listdir(image_folder):
    if filename.endswith(".png"):  # Filter to load only PNG files, adjust as needed
        img_path = os.path.join(image_folder, filename)
        img_name = os.path.splitext(filename)[0]  # Get the image name without extension
        images[img_name] = pygame.image.load(img_path)

# Sample board setup
board = [
    ['white-rook', 'white-knight', 'white-bishop', 'white-queen', 'white-king', 'white-bishop', 'white-knight', 'white-rook'],
    ['white-pawn', 'white-pawn', 'white-pawn', 'white-pawn', 'white-pawn', 'white-pawn', 'white-pawn', 'white-pawn'],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    ['black-pawn', 'black-pawn', 'black-pawn', 'black-pawn', 'black-pawn', 'black-pawn', 'black-pawn', 'black-pawn'],
    ['black-rook', 'black-knight', 'black-bishop', 'black-queen', 'black-king', 'black-bishop', 'black-knight', 'black-rook']
]

# Function to draw the board
def draw_board():
    square_size = 70  # Change this size according to your board
    piece_size = 60  # Set the size for the pieces
    
    for i in range(8):
        for j in range(8):
            square_color = (255, 255, 255) if (i + j) % 2 == 0 else (200, 200, 200)
            pygame.draw.rect(screen, square_color, (i * square_size, j * square_size, square_size, square_size))
            piece = board[j][i]
            if piece != ' ':
                piece_image = images[piece]  # Access the image using the piece name as the key
                # Resize the image to fit the square size
                piece_image = pygame.transform.scale(piece_image, (piece_size, piece_size))
                screen.blit(piece_image, (i * square_size + (square_size - piece_size) // 2, j * square_size + (square_size - piece_size) // 2))
# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Fill the screen with black
    draw_board()  # Draw the board
    pygame.display.flip()

pygame.quit()

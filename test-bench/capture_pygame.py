import pygame
import sys

# pygame is based on SDL2, which is a cross-platform wrapper around OpenGL for rendering shapes and shaders in a high-refresh-rate window for games. With pygame, you have high-speed control of each pixel and everything else (getting input, layout, sprites and images) is left to your own design. 

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Keypress Display")

# Font settings
font = pygame.font.SysFont("Arial", 72)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def display_key(key):
    """Displays the pressed key at the center of the screen."""
    screen.fill(WHITE)  # Clear the screen with a white background
    text_surface = font.render(key, True, BLACK)  # Render the key as text
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  # Center the text
    screen.blit(text_surface, text_rect)  # Draw the text on the screen
    pygame.display.flip()  # Update the display

def main():
    """Main loop to capture keypresses and display them."""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit when the window is closed
                running = False
            elif event.type == pygame.KEYDOWN:  # Detect key press
                key_pressed = event.unicode  # Get the character of the key pressed
                display_key(key_pressed)  # Display the pressed key
    
    pygame.quit()  # Quit pygame
    sys.exit()  # Exit the program

if __name__ == "__main__":
    main()

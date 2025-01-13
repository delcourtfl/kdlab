import pygame
import sys

# pygame is based on SDL2, which is a cross-platform wrapper around OpenGL for rendering shapes and shaders in a high-refresh-rate window for games. With pygame, you have high-speed control of each pixel and everything else (getting input, layout, sprites and images) is left to your own design. 

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
# Hardware acceleration and double buffering
screen = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF, 8)
# Disable alpha channel for better performance
screen.set_alpha(None)
pygame.display.set_caption("Keypress Display")
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])

# Font settings
font = pygame.font.SysFont("Arial", 300)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

pre_rendered_key_surfaces = {}

def main():
    """Main loop to capture keypresses and display them."""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit when the window is closed
                running = False
            elif event.type == pygame.KEYDOWN:  # Detect key press
                key_pressed = event.unicode  # Get the character of the key pressed

                screen.fill(WHITE)
                if key_pressed not in pre_rendered_key_surfaces:
                    # Render without anti-aliasing
                    pre_rendered_key_surfaces[key_pressed] = font.render(key_pressed, False, BLACK)  # Render and store the surface

                text_rect = pre_rendered_key_surfaces[key_pressed].get_rect(center=CENTER)
                screen.blit(pre_rendered_key_surfaces[key_pressed], text_rect)
                
                # Update only the area where the text was blitted
                pygame.display.update(text_rect)  # Update the specific rectangle
    
    pygame.quit()  # Quit pygame
    sys.exit()  # Exit the program

if __name__ == "__main__":
    main()

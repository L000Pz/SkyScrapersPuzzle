import pygame
import sys
from gui import GameGUI

def main():
    pygame.init()
    WINDOW_SIZE = 800
    game = GameGUI(WINDOW_SIZE)
    
    print("Click to select a cell")
    print("Type numbers 1-6 to fill cells")
    print("Backspace/Delete to clear a cell")
    print("Press SPACE to auto-solve")
    print("ESC to quit")
    
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(pygame.mouse.get_pos())
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                game.handle_key(event.key)
                    
        game.draw_grid()
        clock.tick(60)

if __name__ == "__main__":
    main()
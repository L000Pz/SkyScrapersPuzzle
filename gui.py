import pygame
from typing import Optional, Tuple
from logic import SkyscraperPuzzle, GRID_SIZE
import time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
HIGHLIGHT = (176, 224, 230)
GREEN = (50, 205, 50)

class GameGUI:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.cell_size = window_size // (GRID_SIZE + 4)
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Skyscrapers Puzzle")
        self.puzzle = SkyscraperPuzzle()
        self.font = pygame.font.Font(None, 36)
        self.selected_cell = None
        self.offset = self.cell_size * 2  # Space for clues
        self.solving = False
        self.solved = False
        
    def get_cell_from_mouse(self, pos) -> Optional[Tuple[int, int]]:
        x, y = pos
        # Convert mouse coordinates to grid coordinates
        grid_x = (x - self.offset) // self.cell_size
        grid_y = (y - self.offset) // self.cell_size
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return (grid_y, grid_x)  # Return row, col
        return None

    def draw_grid(self):
        self.screen.fill(WHITE)
        
        # Draw clues
        for direction, clues in self.puzzle.clues.items():
            for i, clue in enumerate(clues):
                text = self.font.render(str(clue), True, BLUE)
                if direction == 'top':
                    pos = (self.offset + i * self.cell_size + self.cell_size//3, self.cell_size)
                elif direction == 'right':
                    pos = (self.offset + GRID_SIZE * self.cell_size + self.cell_size//2,
                          self.offset + i * self.cell_size + self.cell_size//3)
                elif direction == 'bottom':
                    pos = (self.offset + i * self.cell_size + self.cell_size//3,
                          self.offset + GRID_SIZE * self.cell_size + self.cell_size//2)
                else:  # left
                    pos = (self.cell_size, self.offset + i * self.cell_size + self.cell_size//3)
                self.screen.blit(text, pos)
        
        # Draw cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = self.offset + col * self.cell_size
                y = self.offset + row * self.cell_size
                
                # Highlight selected cell
                if self.selected_cell == (row, col):
                    pygame.draw.rect(self.screen, HIGHLIGHT,
                                   (x, y, self.cell_size, self.cell_size))
                
                # Draw cell borders
                pygame.draw.rect(self.screen, BLACK,
                               (x, y, self.cell_size, self.cell_size), 1)
                
                # Draw numbers
                if self.puzzle.grid[row][col] != 0:
                    text = self.font.render(str(self.puzzle.grid[row][col]), True, BLACK)
                    text_rect = text.get_rect(center=(x + self.cell_size//2,
                                                    y + self.cell_size//2))
                    self.screen.blit(text, text_rect)
        
        # Draw thick grid lines
        for i in range(GRID_SIZE + 1):
            thickness = 3 if i % GRID_SIZE == 0 else 1
            pygame.draw.line(self.screen, BLACK,
                           (self.offset, self.offset + i * self.cell_size),
                           (self.offset + GRID_SIZE * self.cell_size,
                            self.offset + i * self.cell_size), thickness)
            pygame.draw.line(self.screen, BLACK,
                           (self.offset + i * self.cell_size, self.offset),
                           (self.offset + i * self.cell_size,
                            self.offset + GRID_SIZE * self.cell_size), thickness)
        
        # Draw solved message
        if self.solved:
            text = self.font.render("Puzzle Solved!", True, GREEN)
            text_rect = text.get_rect(center=(self.window_size//2, 30))
            self.screen.blit(text, text_rect)
            
        pygame.display.flip()

    def handle_click(self, pos):
        cell = self.get_cell_from_mouse(pos)
        if cell:
            self.selected_cell = cell

    def handle_key(self, key):
        if key == pygame.K_SPACE and not self.solving:
            self.solving = True
            start_time = time.time()
            if self.puzzle.solve():
                self.solved = True
                end_time = time.time()
                print(f"Solved in {end_time - start_time:.2f} seconds!")
            else:
                print("No solution exists!")
            return
            
        if not self.selected_cell:
            return
            
        row, col = self.selected_cell
        if key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self.puzzle.clear_cell(row, col)
        elif pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0  # Convert key to number
            self.puzzle.make_move(row, col, num)
            
        # Check for win after each move
        if self.puzzle.check_win():
            self.solved = True
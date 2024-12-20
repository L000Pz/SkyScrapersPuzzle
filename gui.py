import pygame
from typing import Optional, Tuple
from logic import SkyscraperPuzzle, GRID_SIZE
import time
import sys
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 149, 237)
RED = (255, 99, 71)
HIGHLIGHT = (176, 224, 230)
GREEN = (50, 205, 50)
YELLOW = (255, 255, 0, 128)  # For current attempt
PURPLE = (147, 112, 219)     # For backtracking
LIGHT_GRAY = (220, 220, 220)
SELECTED_CLUE = (255, 223, 186)

class GameGUI:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.cell_size = window_size // (GRID_SIZE + 4)
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Skyscrapers Puzzle")
        self.puzzle = SkyscraperPuzzle()
        self.font = pygame.font.Font(None, 36)
        self.selected_cell = None
        self.offset = self.cell_size * 2
        self.solving = False
        self.solved = False
        self.current_try = None  # Current cell being attempted
        self.current_num = None  # Current number being tried
        self.delay = 50  # Milliseconds between steps
        self.stop_solving = False
        self.setup_mode = True  # Start in setup mode
        self.selected_clue = None  # (direction, index)
        self.directions = ['top', 'right', 'bottom', 'left']
        self.status_message = "Enter clues (1-6) around the edges. Press ENTER when done."
        
    def solve_instantly(self):
        """Instant solve without visualization"""
        start_time = time.time()
        if self.puzzle.solve():
            end_time = time.time()
            print(f"Solved instantly in {end_time - start_time:.2f} seconds!")
            self.solved = True
        else:
            print("No solution exists!")

    def solve_with_visualization(self):
        """Solve with step-by-step visualization"""
        self.solving = True
        self.stop_solving = False
        start_time = time.time()
        
        if self._solve_step():
            self.solved = True
            end_time = time.time()
            print(f"Solved with visualization in {end_time - start_time:.2f} seconds!")
        else:
            print("No solution exists!")
        
        self.solving = False
        self.current_try = None
        self.current_num = None
        self.stop_solving = False
        
    def get_clue_from_mouse(self, pos) -> Optional[Tuple[str, int]]:
        """Convert mouse position to clue position"""
        x, y = pos
        cell_size = self.cell_size
        offset = self.offset

        # Check each edge for clue positions
        if y < offset:  # Top clues
            idx = (x - offset) // cell_size
            if 0 <= idx < GRID_SIZE:
                return ('top', idx)
                
        elif y > offset + GRID_SIZE * cell_size:  # Bottom clues
            idx = (x - offset) // cell_size
            if 0 <= idx < GRID_SIZE:
                return ('bottom', idx)
                
        elif x < offset:  # Left clues
            idx = (y - offset) // cell_size
            if 0 <= idx < GRID_SIZE:
                return ('left', idx)
                
        elif x > offset + GRID_SIZE * cell_size:  # Right clues
            idx = (y - offset) // cell_size
            if 0 <= idx < GRID_SIZE:
                return ('right', idx)
                
        return None
    
    def _solve_step(self) -> bool:
        # Check for stop request
        if self.stop_solving:
            return False
            
        if self.puzzle.check_win():
            return True
            
        pos = self.puzzle.get_mrv()
        if not pos:
            return False
            
        row, col = pos
        self.current_try = (row, col)
        
        for num in range(1, GRID_SIZE + 1):
            if self.stop_solving:  # Check for stop request
                return False
                
            self.current_num = num
            self.draw_grid()
            pygame.time.delay(self.delay)
            
            # Process events to check for stop key
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    self.stop_solving = True
                    return False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if self.puzzle.is_valid_move(row, col, num, check_visibility=True):
                self.puzzle.grid[row][col] = num
                if self._solve_step():
                    return True
                    
                if self.stop_solving:  # Check for stop after recursion
                    return False
                    
                self.puzzle.grid[row][col] = 0
                self.draw_grid()
                pygame.time.delay(self.delay)
        
        self.current_try = None
        return False

    def draw_grid(self):
        self.screen.fill(WHITE)
        
        # Draw clues
        for direction, clues in self.puzzle.clues.items():
            for i, clue in enumerate(clues):
                # Determine background color for clue cell
                bg_color = SELECTED_CLUE if self.selected_clue == (direction, i) else LIGHT_GRAY
                
                if direction == 'top':
                    rect = pygame.Rect(self.offset + i * self.cell_size, self.cell_size, 
                                     self.cell_size, self.cell_size)
                elif direction == 'right':
                    rect = pygame.Rect(self.offset + GRID_SIZE * self.cell_size, 
                                     self.offset + i * self.cell_size,
                                     self.cell_size, self.cell_size)
                elif direction == 'bottom':
                    rect = pygame.Rect(self.offset + i * self.cell_size, 
                                     self.offset + GRID_SIZE * self.cell_size,
                                     self.cell_size, self.cell_size)
                else:  # left
                    rect = pygame.Rect( self.cell_size, self.offset + i * self.cell_size,
                                     self.cell_size, self.cell_size)
                
                # Draw clue cell background
                pygame.draw.rect(self.screen, bg_color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                
                # Draw clue number if set
                if clue != 0:
                    text = self.font.render(str(clue), True, BLUE)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
        
        # Draw cells and numbers
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = self.offset + col * self.cell_size
                y = self.offset + row * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                # Highlight current attempt
                if self.solving and self.current_try == (row, col):
                    pygame.draw.rect(self.screen, YELLOW, cell_rect)
                # Highlight selected cell
                elif self.selected_cell == (row, col):
                    pygame.draw.rect(self.screen, HIGHLIGHT, cell_rect)
                
                # Draw cell border
                pygame.draw.rect(self.screen, BLACK, cell_rect, 1)
                
                # Draw numbers
                if self.puzzle.grid[row][col] != 0:
                    color = GREEN if self.solving and (row, col) == self.current_try else BLACK
                    text = self.font.render(str(self.puzzle.grid[row][col]), True, color)
                    text_rect = text.get_rect(center=(x + self.cell_size//2, y + self.cell_size//2))
                    self.screen.blit(text, text_rect)
                elif self.solving and (row, col) == self.current_try:
                    # Show number being tried
                    text = self.font.render(str(self.current_num), True, PURPLE)
                    text_rect = text.get_rect(center=(x + self.cell_size//2, y + self.cell_size//2))
                    self.screen.blit(text, text_rect)
        
        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            thickness = 3 if i % GRID_SIZE == 0 else 1
            pygame.draw.line(self.screen, BLACK,
                           (self.offset, self.offset + i * self.cell_size),
                           (self.offset + GRID_SIZE * self.cell_size, self.offset + i * self.cell_size),
                           thickness)
            pygame.draw.line(self.screen, BLACK,
                           (self.offset + i * self.cell_size, self.offset),
                           (self.offset + i * self.cell_size, self.offset + GRID_SIZE * self.cell_size),
                           thickness)
        
        # Draw status messages
        if self.solving:
            msg = f"Trying {self.current_num} at position {self.current_try}" if self.current_try else "Solving..."
            text = self.font.render(msg, True, BLUE)
            self.screen.blit(text, (10, self.window_size - 40))
        elif self.solved:
            text = self.font.render("Puzzle Solved!", True, GREEN)
            self.screen.blit(text, (self.window_size//2 - 100, 10))
        if self.status_message:
            text = self.font.render(self.status_message, True, BLACK)
            text_rect = text.get_rect(center=(self.window_size//2, 30))
            self.screen.blit(text, text_rect)
            
        pygame.display.flip()

    def handle_click(self, pos):
        if self.setup_mode:
            clue_pos = self.get_clue_from_mouse(pos)
            if clue_pos:
                self.selected_clue = clue_pos
                self.selected_cell = None
            else:
                self.selected_clue = None
        else:
            cell = self.get_cell_from_mouse(pos)
            if cell:
                self.selected_cell = cell
                self.selected_clue = None

    def handle_key(self, key):
        if self.setup_mode:
            if key == pygame.K_RETURN:
                # Check if all clues are set
                all_set = all(all(v != 0 for v in clues) 
                            for clues in self.puzzle.clues.values())
                if all_set:
                    self.setup_mode = False
                    self.status_message = "Setup complete! Start playing or press SPACE/V to solve"
                else:
                    self.status_message = "All clues must be set before starting!"
                return
                
            if self.selected_clue:
                direction, idx = self.selected_clue
                if pygame.K_1 <= key <= pygame.K_6:
                    num = key - pygame.K_0
                    self.puzzle.clues[direction][idx] = num
            return
            
        if key == pygame.K_SPACE and not self.solving:
            self.solve_instantly()
            return
        elif key == pygame.K_v and not self.solving:
            self.solve_with_visualization()
            return
        elif key == pygame.K_s and self.solving:
            self.stop_solving = True
            return
            
        if not self.selected_cell:
            return
            
        row, col = self.selected_cell
        if key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            self.puzzle.clear_cell(row, col)
        elif pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0
            self.puzzle.make_move(row, col, num)
            if self.puzzle.check_win():
                self.solved = True

    def get_cell_from_mouse(self, pos) -> Optional[Tuple[int, int]]:
        x, y = pos
        grid_x = (x - self.offset) // self.cell_size
        grid_y = (y - self.offset) // self.cell_size
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return (grid_y, grid_x)
        return None
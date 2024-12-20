from typing import List, Tuple, Optional, Dict
import time

GRID_SIZE = 6

class SkyscraperPuzzle:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # self.clues = {
        #     'top': [1, 2, 2, 3, 4, 3],
        #     'right': [4, 3, 1, 2, 3, 2],
        #     'bottom': [3, 3, 2, 1, 3, 2],
        #     'left': [1, 2, 4, 2, 3, 2]
        # }
        self.clues = {
            'top': [4, 1, 2, 2, 5, 3],
            'right': [3, 2, 3, 4, 1, 2],
            'bottom': [2, 4, 3, 4, 1, 2],
            'left': [2, 3, 3, 1, 4, 2]
        }
        self.stats = {
            'nodes_explored': 0,
            'backtracks': 0,
            'start_time': 0,
            'solve_time': 0
        }

    def is_valid_move(self, row: int, col: int, num: int, check_visibility: bool = False) -> bool:
        # Check range
        if num < 1 or num > 6:
            return False
            
        # Check row and column conflicts
        for i in range(GRID_SIZE):
            if (i != col and self.grid[row][i] == num) or \
               (i != row and self.grid[i][col] == num):
                return False

        if check_visibility:
            # Test the move with visibility constraints
            temp_grid = [row[:] for row in self.grid]
            temp_grid[row][col] = num
            if not self.check_visibility_constraints(temp_grid):
                return False
                
        return True

    def check_visibility_from_direction(self, line: List[int]) -> int:
        if 0 in line:  # Skip incomplete lines
            return -1
            
        visible = 0
        max_height = 0
        for height in line:
            if height > max_height:
                visible += 1
                max_height = height
        return visible

    def check_visibility_constraints(self, grid: List[List[int]]) -> bool:
        # Check columns (top and bottom views)
        for col in range(GRID_SIZE):
            column = [grid[row][col] for row in range(GRID_SIZE)]
            if 0 not in column:
                visible_top = self.check_visibility_from_direction(column)
                visible_bottom = self.check_visibility_from_direction(column[::-1])
                if visible_top != self.clues['top'][col] or visible_bottom != self.clues['bottom'][col]:
                    return False
                
        # Check rows (left and right views)
        for row in range(GRID_SIZE):
            if 0 not in grid[row]:
                visible_left = self.check_visibility_from_direction(grid[row])
                visible_right = self.check_visibility_from_direction(grid[row][::-1])
                if visible_left != self.clues['left'][row] or visible_right != self.clues['right'][row]:
                    return False
                
        return True

    def find_empty(self) -> Optional[Tuple[int, int]]:
        """Find first empty cell - used in simple backtracking"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    return (row, col)
        return None

    def get_mrv(self) -> Optional[Tuple[int, int]]:
        min_remaining = float('inf')
        best_pos = None
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    valid_count = sum(1 for num in range(1, GRID_SIZE + 1) 
                                   if self.is_valid_move(row, col, num, check_visibility=False))
                    if valid_count > 0 and valid_count < min_remaining:
                        min_remaining = valid_count
                        best_pos = (row, col)
        
        return best_pos

    def solve(self) -> bool:
        """Start solving with MRV backtracking"""
        self.reset_stats()
        self.stats['start_time'] = time.time()
        result = self.solve_with_mrv_backtracking()
        self.stats['solve_time'] = time.time() - self.stats['start_time']
        return result

    def solve_simple(self) -> bool:
        """Start solving with simple backtracking"""
        self.reset_stats()
        self.stats['start_time'] = time.time()
        result = self.solve_with_simple_backtracking()
        self.stats['solve_time'] = time.time() - self.stats['start_time']
        return result

    def solve_with_simple_backtracking(self) -> bool:
        """Backtracking without MRV - just takes first empty cell"""
        if self.check_win():
            return True

        # Find any empty cell
        empty = self.find_empty()
        if not empty:
            return True

        self.stats['nodes_explored'] += 1
        row, col = empty

        # Try each number
        for num in range(1, GRID_SIZE + 1):
            if self.is_valid_move(row, col, num, check_visibility=True):
                self.grid[row][col] = num
                if self.solve_with_simple_backtracking():
                    return True
                # If we get here, this number didn't work
                self.grid[row][col] = 0
                self.stats['backtracks'] += 1

        return False

    def solve_with_mrv_backtracking(self) -> bool:
        """Backtracking with MRV - picks cell with fewest valid options"""
        if self.check_win():
            return True

        # Find cell with fewest valid options
        empty = self.get_mrv()
        if not empty:
            return True

        self.stats['nodes_explored'] += 1
        row, col = empty

        # Try each number
        for num in range(1, GRID_SIZE + 1):
            if self.is_valid_move(row, col, num, check_visibility=True):
                self.grid[row][col] = num
                if self.solve_with_mrv_backtracking():
                    return True
                # If we get here, this number didn't work
                self.grid[row][col] = 0
                self.stats['backtracks'] += 1

        return False

    def check_win(self) -> bool:
        if any(0 in row for row in self.grid):
            return False
        return self.check_visibility_constraints(self.grid)

    def make_move(self, row: int, col: int, num: int) -> bool:
        if self.is_valid_move(row, col, num, check_visibility=True):
            self.grid[row][col] = num
            return True
        return False

    def clear_cell(self, row: int, col: int):
        self.grid[row][col] = 0

    def reset_stats(self):
        self.stats = {
            'nodes_explored': 0,
            'backtracks': 0,
            'start_time': 0,
            'solve_time': 0
        }

    def get_stats_report(self) -> str:
        return f"""
        Performance Statistics:
        ---------------------
        Time taken: {self.stats['solve_time']:.3f} seconds
        Nodes explored: {self.stats['nodes_explored']}
        Backtracks: {self.stats['backtracks']}
        Efficiency (backtracks/nodes): {(self.stats['backtracks'] / self.stats['nodes_explored']):.2%}
        """
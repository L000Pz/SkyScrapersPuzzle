from typing import List, Tuple, Optional, Dict

# Size of the puzzle grid (6x6 in this case)
GRID_SIZE = 6

class SkyscraperPuzzle:
    def __init__(self):
        """
        Initialize the puzzle with an empty grid and clue numbers for all four sides.
        - grid: 6x6 array where 0 represents empty cells
        - clues: Dictionary containing the visibility clues for each side of the grid
        """
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.clues = {
            'top': [1, 2, 2, 3, 4, 3],      # Visible buildings from top view
            'right': [4, 3, 1, 2, 3, 2],    # Visible buildings from right view
            'bottom': [3, 3, 2, 1, 3, 2],   # Visible buildings from bottom view
            'left': [1, 2, 4, 2, 3, 2]      # Visible buildings from left view
        }
    
    def is_valid_move(self, row: int, col: int, num: int, check_visibility: bool = False) -> bool:
        """
        Check if placing 'num' at position (row, col) is valid.
        
        Args:
            row, col: Position in the grid
            num: Number to be placed (1-6)
            check_visibility: Whether to check visibility constraints
        
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Constraint 1: No same number in row/column
        
        # Check if number is within valid range (1-6)
        if num < 1 or num > 6:
            return False
        # Check for conflicts in the same row or column
        for i in range(GRID_SIZE):
            if (i != col and self.grid[row][i] == num) or \
               (i != row and self.grid[i][col] == num):
                return False

        # Constraint 2: Visibility constraints (how many buildings you can see)
        if check_visibility:
            temp_grid = [row[:] for row in self.grid]
            temp_grid[row][col] = num
            if not self.check_visibility_constraints(temp_grid):
                return False
                
        return True

    def check_visibility_from_direction(self, line: List[int]) -> int:
        """
        Count how many buildings are visible when looking along a line of buildings.
        A building is visible if it's taller than all buildings before it.
        
        Args:
            line: List of building heights
        
        Returns:
            int: Number of visible buildings, or -1 if line contains empty cells
        """
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
        """
        Check if all visibility constraints are satisfied for completed lines/columns.
        
        Args:
            grid: Current state of the puzzle grid
            
        Returns:
            bool: True if all visibility constraints are satisfied
        """
        # Check columns (top and bottom views)
        for col in range(GRID_SIZE):
            column = [grid[row][col] for row in range(GRID_SIZE)]
            if 0 not in column:  # Only check completed columns
                visible_top = self.check_visibility_from_direction(column)
                visible_bottom = self.check_visibility_from_direction(column[::-1])
                if visible_top != self.clues['top'][col] or visible_bottom != self.clues['bottom'][col]:
                    return False
                
        # Check rows (left and right views)
        for row in range(GRID_SIZE):
            if 0 not in grid[row]:  # Only check completed rows
                visible_left = self.check_visibility_from_direction(grid[row])
                visible_right = self.check_visibility_from_direction(grid[row][::-1])
                if visible_left != self.clues['left'][row] or visible_right != self.clues['right'][row]:
                    return False
                
        return True
    
    def get_mrv(self) -> Optional[Tuple[int, int]]:
        """
        Implement Minimum Remaining Values (MRV) heuristic.
        Find the empty cell that has the fewest valid numbers that could be placed in it.
        
        Returns:
            Tuple[int, int]: (row, col) of the best cell to fill next, or None if no empty cells
        """
        min_remaining = float('inf')
        best_pos = None
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    # Count how many valid numbers we can put here
                    valid_count = sum(1 for num in range(1, GRID_SIZE + 1) 
                                   if self.is_valid_move(row, col, num))
                    if valid_count > 0 and valid_count < min_remaining:
                        min_remaining = valid_count
                        best_pos = (row, col)
        
        return best_pos

    def solve(self) -> bool:
        """
        Public solving method with error handling.
        
        Returns:
            bool: True if solution found, False otherwise
        """
        try:
            return self._solve_helper()
        except Exception as e:
            print(f"Error during solving: {e}")
            return False

    def _solve_helper(self) -> bool:
        """
        Recursive helper method that implements the backtracking algorithm.
        Uses MRV heuristic to choose next cell to fill.
        
        Returns:
            bool: True if solution found, False if no solution exists
        """
        if self.check_win():
            return True
            
        pos = self.get_mrv()
        if not pos:
            return False
            
        row, col = pos
        for num in range(1, GRID_SIZE + 1):
            if self.is_valid_move(row, col, num, check_visibility=True):
                self.grid[row][col] = num
                if self._solve_helper():
                    return True
                self.grid[row][col] = 0  # Backtrack
                
        return False

    def check_win(self) -> bool:
        """
        Check if the puzzle is solved:
        - All cells filled
        - All visibility constraints satisfied
        
        Returns:
            bool: True if puzzle is solved, False otherwise
        """
        if any(0 in row for row in self.grid):
            return False
        return self.check_visibility_constraints(self.grid)

    def make_move(self, row: int, col: int, num: int) -> bool:
        """
        Try to make a move in the puzzle.
        
        Args:
            row, col: Position in the grid
            num: Number to place (1-6)
            
        Returns:
            bool: True if move was valid and made, False otherwise
        """
        if self.is_valid_move(row, col, num):
            self.grid[row][col] = num
            return True
        return False

    def clear_cell(self, row: int, col: int):
        """
        Clear a cell in the grid by setting it to 0.
        
        Args:
            row, col: Position of cell to clear
        """
        self.grid[row][col] = 0
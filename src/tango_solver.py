"""
Tango Solver - LinkedIn Tango game solver

Game rules:
1. 6x6 board with two types of pieces (0 and 1)
2. Each row and column must have exactly 3 of each type
3. No 3 consecutive pieces of the same type allowed (max 2 in a row)
4. "=" clues indicate adjacent cells must have the same type
5. "x" clues indicate adjacent cells must have different types
"""

class TangoSolver:
    def __init__(self):
        self.size = 6
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.constraints = []
        self.fixed_pieces = []

    def add_constraint(self, constraint_type, pos1, pos2):
        self.constraints.append((constraint_type, pos1, pos2))

    def add_fixed_piece(self, row, col, piece_type):
        self.board[row][col] = piece_type
        self.fixed_pieces.append((row, col, piece_type))

    def is_valid_placement(self, row, col, piece_type):
        temp_board = [row[:] for row in self.board]
        temp_board[row][col] = piece_type

        if not self._check_row_column_constraints(temp_board, row, col):
            return False

        if not self._check_no_three_consecutive(temp_board, row, col):
            return False

        if not self._check_equality_constraints(temp_board, row, col):
            return False

        return True

    def _check_row_column_constraints(self, board, row, col):
        row_count = [0, 0]
        for c in range(self.size):
            if board[row][c] is not None:
                row_count[board[row][c]] += 1

        col_count = [0, 0]
        for r in range(self.size):
            if board[r][col] is not None:
                col_count[board[r][col]] += 1

        return all(count <= 3 for count in row_count + col_count)

    def _check_no_three_consecutive(self, board, row, col):
        piece_type = board[row][col]

        for start_col in range(max(0, col - 2), min(self.size - 2, col + 1)):
            if all(board[row][start_col + i] == piece_type for i in range(3)):
                return False

        for start_row in range(max(0, row - 2), min(self.size - 2, row + 1)):
            if all(board[start_row + i][col] == piece_type for i in range(3)):
                return False

        return True

    def _check_equality_constraints(self, board, row, col):
        for constraint_type, pos1, pos2 in self.constraints:
            r1, c1 = pos1
            r2, c2 = pos2

            if board[r1][c1] is not None and board[r2][c2] is not None:
                if constraint_type == '=':
                    if board[r1][c1] != board[r2][c2]:
                        return False
                elif constraint_type == 'x':
                    if board[r1][c1] == board[r2][c2]:
                        return False

        return True

    def is_complete(self):
        for row in self.board:
            if None in row:
                return False

        for i in range(self.size):
            row_count = [0, 0]
            col_count = [0, 0]

            for j in range(self.size):
                row_count[self.board[i][j]] += 1
                col_count[self.board[j][i]] += 1

            if row_count != [3, 3] or col_count != [3, 3]:
                return False

        return True

    def solve(self):
        return self._backtrack()

    def _backtrack(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] is None:
                    # Try both piece types
                    for piece_type in [0, 1]:
                        if self.is_valid_placement(row, col, piece_type):
                            self.board[row][col] = piece_type

                            if self._backtrack():
                                return True

                            self.board[row][col] = None

                    return False

        return self.is_complete()

    def print_board_with_constraints(self):
        constraint_map = {}

        for constraint_type, pos1, pos2 in self.constraints:
            if constraint_type == '=':
                constraint_map[pos1] = '🟢'
                constraint_map[pos2] = '🟢'
            elif constraint_type == 'x':
                constraint_map[pos1] = '🔴'
                constraint_map[pos2] = '🔴'

        symbols = {0: '🌙', 1: '🟠', None: '⬜'}

        print("Board with constraints (🟢 = equals, 🔴 = not-equals):")
        for row_idx, row in enumerate(self.board):
            row_str = ""
            for col_idx, cell in enumerate(row):
                pos = (row_idx, col_idx)

                if cell is not None:
                    row_str += symbols[cell] + " "
                elif pos in constraint_map:
                    row_str += constraint_map[pos] + " "
                else:
                    row_str += symbols[None] + " "

            print(row_str.strip())
        print()

    def print_board(self):
        symbols = {0: '🌙', 1: '🟠', None: '⬜'}

        for row in self.board:
            print(' '.join(symbols[cell] for cell in row))
        print()

    def print_board_simple(self):
        """Print the board in simple format (for debugging)"""
        for row in self.board:
            print(' '.join(str(cell) if cell is not None else '.' for cell in row))
        print()


if __name__ == "__main__":
    solver = TangoSolver()

    print("Initial board:")
    solver.print_board()

    if solver.solve():
        print("Puzzle solved!")
        solver.print_board()
    else:
        print("Could not solve the puzzle")

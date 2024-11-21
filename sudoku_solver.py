import random
from random import *

from z3 import *

class Sudoku:
    def __init__(self):
        self.puzzle = []
        self.solution = []
        self.unknowns = []

    # Read the puzzle from a .txt file with missing entries marked by 0
    def read_puzzle(self, filename):
        with open(filename, "r") as file:
            for line in file:
                self.puzzle.append([int(x) for x in list(line.strip())])
        self.solution = [row.copy() for row in self.puzzle]

        # Find unknowns
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] == 0:
                    self.unknowns.append((i, j))

    # Print the puzzle
    def print_puzzle(self):
        for row in self.puzzle:
            print(row)

    def print_solution(self):
        for row in self.solution:
            print(row)

    def create_sudoku_solver(self):
        # Constraints
        # 1. Each row must have the numbers 1-9 occuring just once
        # 2. Each column must have the numbers 1-9 occuring just once
        # 3. And the numbers 1-9 must occur just once in each of the 9 3x3 sub-boxes of the 9x9 grid
        # 4. Each cell must have a value between 1-9
        # 5. Cell must have value if specified in the puzzle
        cells = [[Int("cell_%s_%s" % (i, j)) for j in range(9)] for i in range(9)]
        # print(cells)

        # 1. Each row must have the numbers 1-9 occuring just once
        row_c = [Distinct(cells[i]) for i in range(9)]
        # print(row_c)

        # 2. Each column must have the numbers 1-9 occuring just once
        col_c = [Distinct([cells[i][j] for i in range(9)]) for j in range(9)]
        # print(col_c)

        # 3. And the numbers 1-9 must occur just once in each of the 9 3x3 sub-boxes of the 9x9 grid
        box_c = [Distinct([cells[3 * i + j][3 * k + l] for j in range(3) for l in range(3)]) for i in range(3) for k in
                 range(3)]
        # print(box_c)

        # 4. Each cell must have a value between 1-9
        cell_c = [And(cells[i][j] >= 1, cells[i][j] <= 9) for i in range(9) for j in range(9)]
        # print(cell_c)

        # 5. Cell must have value if specified in the puzzle
        puzzle_c = [If(self.puzzle[i][j] == 0, True, cells[i][j] == self.puzzle[i][j]) for i in range(9) for j in
                    range(9)]
        # for i in range(9):
        #     for j in range(9):
        #         print(puzzle_c[i*9 + j])
        #     print("\n")

        # Create base solver
        s = Solver()
        s.add(row_c + col_c + box_c + cell_c + puzzle_c)

        return s

    def solve_sudoku(self):
        # Solve the puzzle
        s = self.create_sudoku_solver()

        if s.check() == sat:
            m = s.model()
            self.solution = [[m.evaluate(Int("cell_%s_%s" % (i, j))) for j in range(9)] for i in range(9)]
            return True
        else:
            return False

    def solve(self):
        if self.solve_sudoku():
            print("The solution is:")
            self.print_solution()
        else:
            print("No solution exists")

    def find_all_solutions(self):
        # Solve the puzzle
        s = self.create_sudoku_solver()

        solution_list = []
        while s.check() == sat:
            m = s.model()
            # Solution constraints for unknowns
            sol_c = [Int("cell_%s_%s" % (i, j)) != m.evaluate(Int("cell_%s_%s" % (i, j))) for i, j in self.unknowns]
            solution_list.append([[m.evaluate(Int("cell_%s_%s" % (i, j))) for j in range(9)] for i in range(9)])
            s.add(Or(sol_c))

        print("There is/are %d solutions" % len(solution_list))
        for i, solution in enumerate(solution_list):
            print("Solution %d:" % (i + 1))
            for row in solution:
                print(row)
        return

    def create_puzzle(self):
        # Create a 9x9 puzzle with 17 clues
        s = Solver()
        cells = [[Int("cell_%s_%s" % (i, j)) for j in range(9)] for i in range(9)]
        # 1. Each row must have the numbers 1-9 occuring just once
        row_c = [Distinct(cells[i]) for i in range(9)]
        # 2. Each column must have the numbers 1-9 occuring just once
        col_c = [Distinct([cells[i][j] for i in range(9)]) for j in range(9)]
        # 3. And the numbers 1-9 must occur just once in each of the 9 3x3 sub-boxes of the 9x9 grid
        box_c = [Distinct([cells[3 * i + j][3 * k + l] for j in range(3) for l in range(3)]) for i in range(3) for k in
                    range(3)]
        # 4. Each cell must have a value between 1-9
        cell_c = [And(cells[i][j] >= 1, cells[i][j] <= 9) for i in range(9) for j in range(9)]

        s.add(row_c + col_c + box_c + cell_c)
        s.check()
        m = s.model()
        solved_puzzle = [[m.evaluate(Int("cell_%s_%s" % (i, j))) for j in range(9)] for i in range(9)]
        # print solved_puzzle as a 2 dimensional array
        for row in solved_puzzle:
            print(row)

        puzzle_c = [cells[i][j] == solved_puzzle[i][j] for i in range(9) for j in range(9)]

        # Remove clues and check if the puzzle still has a unique solution
        for k in range(3):
            solution_list = []
            while len(solution_list) != 1:
                s.push()
                puzzle_c[(random.randint(0, len(puzzle_c) - 1))] = True
                s.add(puzzle_c)
                while s.check() == sat:
                    m = s.model()
                    sol_c = [Int("cell_%s_%s" % (i, j)) != m.evaluate(Int("cell_%s_%s" % (i, j))) for i, j in
                             self.unknowns]
                    solution_list.append([[m.evaluate(Int("cell_%s_%s" % (i, j))) for j in range(9)] for i in range(9)])
                    s.add(Or(sol_c))



                # print("There is/are %d solutions" % len(solution_list))
                # for i, solution in enumerate(solution_list):
                #     print("Solution %d:" % (i + 1))
                #     for row in solution:
                #         print(row)


            s.add(row_c + col_c + box_c + cell_c)
            s.add(cells[i][j] != solved_puzzle[i][j])
            if s.check() == sat:
                solved_puzzle[i][j] = 0




# main function
def main():
    # Create a Sudoku object
    sudoku = Sudoku()

    # Read the Sudoku puzzle from the file
    sudoku.read_puzzle("tests/test2_positive.txt")

    # sudoku.print_puzzle()

    # print("\n")

    # Solve the puzzle
    # sudoku.solve()
    # sudoku.find_all_solutions()
    # sudoku.print_puzzle()

    sudoku.create_puzzle()


# Call the main function
if __name__ == "__main__":
    # main()
    x = Int('x')
    y = Int('y')
    z = Int('z')
    s = Solver()
    s.add(x > 1, y > 1, z == x + y)
    print(s.check())
    print(s.model())
    s.push()
    s.add(z > 10)
    s.add(z < 100)
    s.check()
    print(s.model())
    print(s)
    s.pop()
    print(s)
    s.check()
    print(s.model())
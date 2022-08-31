from sudoku import Sudoku

sdk = Sudoku()
clues = sdk.generate_puzzle()
for i in range(0,100):
    while clues >= 23:
        clues = self.generate_puzzle()
    filename = "hard" + str(i).zfill(2) + ".svg"
    sdk.export_grid(filename)

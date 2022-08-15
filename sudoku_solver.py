class Sudoku:

    def __init__(self,filename):
        self.grid = self.read_grid(filename)
        self.history = []
        if not self.is_valid():
            raise RuntimeError('grid is invalid')
        
    def read_grid(self,filename):
        grid = []
        with open(filename,'r') as fin:
            counter = 0
            while True:
                n = fin.read(1)
                if n == '\n':
                    break
                if n == ' ':
                    grid.append(0)
                else:
                    grid.append(int(n))
                counter = counter+1
            if counter != 81:
                raise RuntimeError('wrong grid format')
                return []
            else:
                return grid
    
    def solve_no_guess(self):
    
        while True:
            num_found_beg = len(self.history)
           
            for r in range(0,9):
                for c in range(0,9):
                    self.solve_cell(r,c)
                    self.solve_square(r,c)
                    self.solve_row(r,c)
                    self.solve_col(r,c)
            
            # check if no change
            num_found_end =  len(self.history)
            if num_found_end == num_found_beg:
                break
        
    def write_grid(self):
        pass
    
    def solve_marginal(self,idx,r,c):
        uniq_other_candidates = set()
        for i in idx:
            (ri,ci) = self.ind2sub(i)
            if ri != r or ci != c:
                other_candidates = self.get_candidate(ri,ci)
                for cand in other_candidates:
                    uniq_other_candidates.add(cand)
        this_candidates = set(self.get_candidate(r,c))
        candidate = list(this_candidates - uniq_other_candidates)
        if len(candidate) == 1:
            self.grid[9*r+c] = candidate[0]
            self.history.append((r,c,candidate[0]))
    
    def solve_cell(self,r,c):
        candidate = self.get_candidate(r,c)
        if len(candidate)==1:
            self.grid[9*r+c] = candidate[0]
            self.history.append((r,c,candidate[0]))
                        
    def solve_square(self,r,c):
        idx = self.sqr_ind(r,c)
        self.solve_marginal(idx,r,c)
        
    def solve_row(self,r,c):
        idx = self.row_ind(r)
        self.solve_marginal(idx,r,c)
    
    def solve_col(self,r,c):
        idx = self.col_ind(c)
        self.solve_marginal(idx,r,c)
    
    def get_candidate(self,r,c):
        if self.grid[9*r+c] == 0:
            row = self.get_row(r,c)
            col = self.get_col(r,c)
            sqr = self.get_square(r,c)
            not_candidate = set(row+col+sqr)
            possible = {i for i in range(1,10)}
            candidate = possible - not_candidate
            return list(candidate)
        else:
            return []
    
    def ind2sub(self,i):
        row = i//9
        col = i%9
        return (row,col)
        
    def sub2ind(self,r,c):
        lin = 9*r+c
        return lin
    
    def row_ind(self,r):
        return [i for i in range(0,81) if i//9==r]
    
    def col_ind(self,c):
        return [i for i in range(0,81) if i%9==c]
    
    def sqr_ind(self,r,c):
        return [i for i in range(0,81) if (i//9)//3==r//3 and (i%9)//3==c//3]
            
    def get_row(self,r,c):
        return [self.grid[i] for i in self.row_ind(r)]
    
    def get_col(self,r,c):
        return [self.grid[i] for i in self.col_ind(c)]
    
    def get_square(self,r,c):
        return [self.grid[i] for i in self.sqr_ind(r,c)]
    
    def is_valid(self):
        """TODO check that the grid is valid"""
        return True
        
    def print_grid(self):
        gridstr = ""
        for r in range(0,9):
            for c in range(0,9):
                if self.grid[9*r+c] == 0:
                    gridstr = gridstr + "  "
                else:
                    gridstr = gridstr + str(self.grid[9*r+c]) + " "
                if c == 2 or c == 5:
                    gridstr = gridstr + "| "
                if c == 8:
                    gridstr = gridstr + "\n"
                    if r == 2 or r == 5:
                        gridstr = gridstr + 21*"-" +  "\n"
        print(gridstr)



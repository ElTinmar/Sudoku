class Sudoku:

    def __init__(self,filename):
        self.grid = self.read_grid(filename)
        self.history = []
        self.track = []
        self.stuck = False
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
    
    def complete(self):
        notdone = [x for x in self.grid if x==0]
        if len(notdone)>0:
            return False
        else:
            return True
        
    def solve_backtrack(self):
        while not self.complete():
            self.solve_grid()
            if not self.complete():
                self.backtrack()
    
    def backtrack(self):
        
        # select the first cell that is the least ambiguous
        least_num_choice = 9
        for r in range(0,9):
            for c in range(0,9):
                candidates = self.get_candidate(r,c)
                num_choice = len(candidates)
                if num_choice > 0 and num_choice < least_num_choice:
                    least_num_choice = num_choice
                    r_sel = r
                    c_sel = c
                    candidates_sel = candidates
        
        # try the alternatives
        for n in candidates_sel:
            self.add_num(r_sel,c_sel,n,True)
            self.track.append(len(self.history))
            self.solve_grid()
            # backtrack if we get stuck
            if self.stuck:
                for step in range(self.track[-1],len(self.history)):
                    r,c,n,b = self.history[step]
                    self.add_num(r,c,0,False)
                self.track.pop()
                self.stuck = False
            else:
                break
                
    def solve_grid(self):
        while True:
            num_found_beg = len(self.history)
           
            for r in range(0,9):
                for c in range(0,9):
                    self.solve_cell(r,c)
                    self.solve_square(r,c)
                    self.solve_row(r,c)
                    self.solve_col(r,c)
            
            # if no change, stop
            num_found_end =  len(self.history)
            if num_found_end == num_found_beg:
                break
        
    def write_grid(self):
        pass
        
    def add_num(self,r,c,n,b):
        idx = self.sub2ind(r,c)
        self.grid[idx] = n
        self.history.append((r,c,n,b))
    
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
            self.add_num(r,c,candidate[0],False)
    
    def solve_cell(self,r,c):
        candidate = self.get_candidate(r,c)
        if len(candidate)==1:
            self.add_num(r,c,candidate[0],False)
                        
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
            row = self.get_row(r)
            col = self.get_col(c)
            sqr = self.get_square(r,c)
            not_candidate = set(row+col+sqr)
            possible = {i for i in range(1,10)}
            candidate = list(possible - not_candidate)
            if len(candidate)==0:
                self.stuck = True
            return candidate
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
        
    def get_row(self,r):
        return [self.grid[i] for i in self.row_ind(r)]
    
    def get_col(self,c):
        return [self.grid[i] for i in self.col_ind(c)]
    
    def get_square(self,r,c):
        return [self.grid[i] for i in self.sqr_ind(r,c)]
    
    def valid_subset(self,numbers):
        seen = set()
        dupes = [x for x in numbers if x in seen and x != 0 or seen.add(x)]
        if len(dupes)>0:
            return False
        else:
            return True
        
    def is_valid(self):
        """check that the grid is valid"""
       
        # check rows
        for r in range(0,9):
            numbers = self.get_row(r)
            if not self.valid_subset(numbers):
                return False
        
        # check columns
        for c in range(0,9):
            numbers = self.get_col(c)
            if not self.valid_subset(numbers):
                return False
        
        # check squares
        for r in range(0,9,3):
            for c in range(0,9,3):
                numbers = self.get_square(r,c)
                if not self.valid_subset(numbers):
                    return False
        
        return True
        
    def grid_string(self):
        gridstr = "\n"
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
        return gridstr
        
    def print_grid(self):
        print(self.grid_string())
        
    def __repr__(self):
        repr_str = "Grid: \n" + self.grid_string() + "\nHistory: \n"
        for r,c,n,b in self.history:
            if b:
                hist = "{0},{1}: {2} *\n".format(r,c,n)
            else:
                hist = "{0},{1}: {2}\n".format(r,c,n)
            repr_str = repr_str + hist
        return repr_str



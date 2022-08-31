#ref https://en.wikipedia.org/wiki/Mathematics_of_Sudoku
#ref https://en.wikipedia.org/wiki/Sudoku_solving_algorithms

import random

class History:
    '''Simple tree class'''
    def __init__(self, grid):
        self.children = []
        self.grid = grid
    
    def add_child(self, node):
        self.children.append(node)
    
    def __repr__(self):
        reprstr = ""
        for i in self.grid:
            reprstr += str(i)
        return reprstr

# TODO fix problems with multiple digits for Sudoku(4) and beyond
# for reading, writing and displaying grids

# TODO check for symmetries

class Sudoku:
    
    def __init__(self, n=3):
        self.tot_size = n**4
        self.max_num = n**2
        self.n = n
        self.grid = []
        for i in range(0,self.tot_size):
            self.grid.append(0)
        self.visited = []
        self.stuck = False
        self.history = History(self.grid)
        
    def reset_grid(self):
        self.visited = []
        self.stuck = False
        for i in range(0,self.tot_size):
            self.grid[i] = 0
        self.history = History(self.grid)
        
    def prune_grid(self): 
        solution = self.grid[:]
        not_prunable = set()
        while True:
            prunable = {i for i,v in enumerate(self.grid) if v != 0} - not_prunable
            if len(prunable)>0:
                idx = random.sample(prunable,1)[0]
                prev_num = self.grid[idx]
                self.grid[idx] = 0
                previous_grid = self.grid[:]
                self.history = History(self.grid)
                valid = self.solve() 
                if not valid or not self.cmp_grid(solution):
                    not_prunable.add(idx)
                    self.grid = previous_grid
                    self.grid[idx] = prev_num
                self.grid = previous_grid
                self.history = History(self.grid)
            else:
                break
        self.visited = []
        self.stuck = False
            
    def generate_full_grid(self):
        # TODO not super satisfying, can I do better ?
        # reset grid
        self.reset_grid()
        
        while not self.complete():
            # select most constrained cell
            (r_sel,c_sel,candidates_sel) = self.get_most_constrained()
        
            if self.stuck:
                 self.reset_grid()
                 (r_sel,c_sel,candidates_sel) = self.get_most_constrained()
                 
            # pick at random among candidates
            num = random.sample(candidates_sel,1)[0]
            idx = self.sub2ind(r_sel,c_sel)
            self.grid[idx] = num
            
        self.history = History(self.grid) 
        self.visited = []
        self.stuck = False
        
    def generate_puzzle(self):
        self.generate_full_grid()
        self.prune_grid()
        return self.puzzle_level()
        
    def read_grid(self,filename):
        self.reset_grid()
        with open(filename,'r') as fin:
            counter = 0
            while True:
                n = fin.read(1)
                if n == '\n':
                    break
                if n == ' ':
                    self.grid[counter] = 0
                else:
                    self.grid[counter] = int(n)
                counter = counter+1
            if counter != self.tot_size:
                raise RuntimeError('wrong grid format')
            else:
                if not self.is_valid():
                    raise RuntimeError('grid is invalid')
                    
        self.history = History(self.grid) 
        
    def puzzle_level(self):
        # number of clues
        num_clues = len([i for i in self.grid if i != 0])
        
        return num_clues
        
    def export_grid(self,filename):
        """export grid as svg"""
        pass
    
    def write_grid(self,filename):
        with open(filename,'w') as fout:
            for num in self.grid:
                if num == 0:
                    fout.write(' ')
                else:
                    fout.write(num)
        
    def complete(self):
        if 0 in self.grid:
            return False
        else:
            return True
            
    def next_move(self, node):
        (r,c,candidates) = self.get_most_constrained()
        for num in candidates:
            grid = self.grid[:]
            idx = self.sub2ind(r,c)
            grid[idx] = num
            child = History(grid)
            node.add_child(child)
        
    def solve(self):
        '''Use DFS to visit the tree of possible moves'''
        
        solution = []
        unique = True
        stack = []
        root = self.history
        self.next_move(root)
        stack.append(root)
        
        while len(stack)>0:
            node = stack.pop()
            if node not in self.visited:
                self.grid = node.grid[:]
                self.next_move(node)
                self.visited.append(node)
                for c in node.children:
                    stack.append(c)
                
                # check if we have solved the puzzle
                if self.complete():
                    if solution == []:
                        solution = self.grid[:]
                    else:
                        if not self.cmp_grid(solution):
                            unique = False
                            break
        
        self.grid = solution
        if self.complete() and unique:
            return True
        else:
            return False
                    
    def get_most_constrained(self):
        least_num_choice = self.max_num+1
        r_sel = 0
        c_sel = 0
        candidates_sel = []
        for r in range(0,self.max_num):
            for c in range(0,self.max_num):
                candidates = self.get_uniq_candidate(r,c)
                num_choice = len(candidates)
                if num_choice > 0 and num_choice < least_num_choice:
                    least_num_choice = num_choice
                    r_sel = r
                    c_sel = c
                    candidates_sel = candidates
    
        return (r_sel,c_sel,candidates_sel)
            
    def cmp_grid(self, grid):
        for i in range(0,self.tot_size):
            if self.grid[i] != grid[i]:
                return False
        return True 
    
    def get_marginal(self,idx,r,c):
        uniq_other_candidates = set()
        for i in idx:
            (ri,ci) = self.ind2sub(i)
            if ri != r or ci != c:
                other_candidates = self.get_candidate(ri,ci)
                for cand in other_candidates:
                    uniq_other_candidates.add(cand)
        this_candidates = set(self.get_candidate(r,c))
        candidate = list(this_candidates - uniq_other_candidates)
        return candidate
    
    def get_uniq_candidate(self,r,c):
        candidate = self.get_candidate(r,c)
        isqr = self.sqr_ind(r,c)
        irow = self.row_ind(r)
        icol = self.col_ind(c)
        uniq_sqr = self.get_marginal(isqr,r,c)
        uniq_row = self.get_marginal(irow,r,c)
        uniq_col = self.get_marginal(icol,r,c)
        if len(uniq_sqr)==1:
            return uniq_sqr
        elif len(uniq_row)==1:
            return uniq_row
        elif len(uniq_col)==1:
            return uniq_col
        else:
            return candidate
    
    def get_candidate(self,r,c):
        idx = self.sub2ind(r,c)
        if self.grid[idx] == 0:
            row = self.get_row(r)
            col = self.get_col(c)
            sqr = self.get_square(r,c)
            not_candidate = set(row+col+sqr)
            possible = {i for i in range(1,self.max_num+1)}
            candidate = list(possible - not_candidate)
            if len(candidate)==0:
                self.stuck = True
            return candidate
        else:
            return []
    
    def ind2sub(self,i):
        row = i//self.max_num
        col = i%self.max_num
        return (row,col)
        
    def sub2ind(self,r,c):
        lin = self.max_num*r+c
        return lin
    
    def row_ind(self,r):
        return [i for i in range(0,self.tot_size) if i//self.max_num==r]
    
    def col_ind(self,c):
        return [i for i in range(0,self.tot_size) if i%self.max_num==c]
    
    def sqr_ind(self,r,c):
        return [i for i in range(0,self.tot_size) 
            if (i//self.max_num)//self.n==r//self.n 
            and (i%self.max_num)//self.n==c//self.n]
        
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
        
    def valid(self):
        # check rows
        for r in range(0,self.max_num):
            numbers = self.get_row(r)
            if not self.valid_subset(numbers):
                return False
        # check columns
        for c in range(0,self.max_num):
            numbers = self.get_col(c)
            if not self.valid_subset(numbers):
                return False
        # check squares
        for r in range(0,self.max_num,self.n):
            for c in range(0,self.max_num,self.n):
                numbers = self.get_square(r,c)
                if not self.valid_subset(numbers):
                    return False
        return True
        
    def __repr__(self):
        gridstr = "\n"
        for r in range(0,self.max_num):
            for c in range(0,self.max_num):
                idx  = self.sub2ind(r,c)
                if c == 0:
                    gridstr = gridstr + " "
                if self.grid[idx] == 0:
                    gridstr = gridstr + "  "
                else:
                    gridstr = gridstr + str(self.grid[idx]) + " "
                if (c+1)//self.n > c//self.n:
                    if c == self.max_num-1:
                        gridstr = gridstr + " \n"
                        if (r+1)//self.n > r//self.n:
                            if r != self.max_num-1:
                                gridstr=gridstr+(self.n*(self.n+1)*2-1)*"-"+"\n"
                    else:
                        gridstr = gridstr + "| "
        return gridstr


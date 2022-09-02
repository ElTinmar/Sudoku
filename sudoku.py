#ref https://en.wikipedia.org/wiki/Mathematics_of_Sudoku
#ref https://en.wikipedia.org/wiki/Sudoku_solving_algorithms

import random

class Tree:
    '''Simple tree class'''
    def __init__(self, grid):
        self.children = []
        self.grid = grid
        self.solution = False
    
    def add_child(self, node):
        self.children.append(node)
        
    def num_branches(self):
        n = 0
        n_children = len(self.children)
        if n_children > 1:
            n += len(self.children)-1
        for c in self.children:
            n += c.num_branches()
        return n
    
    def __repr__(self):
        if self.solution:
            reprstr = "\033[92m"
        else:
            reprstr = ""
            
        for i in self.grid:
            if i==0:
                reprstr += "\033[91m" + "0" + "\033[0m"
            else:
                reprstr += chr(48+i)
            
        if self.solution:
            reprstr += '\033[0m'
            
        reprstr += "\n"
        return reprstr

# TODO check for symmetries

class Sudoku:
    
    def __init__(self, n=3):
        if not 2 <= n <= 4:
            raise(ValueError)
        self.tot_size = n**4
        self.max_num = n**2
        self.n = n
        self.grid = []
        for i in range(0,self.tot_size):
            self.grid.append(0)
        self.visited = []
        self.tree = Tree(self.grid)
        
    def reset_grid(self):
        self.visited = []
        for i in range(0,self.tot_size):
            self.grid[i] = 0
        self.tree = Tree(self.grid)
        
    def prune_grid(self,display=False): 
        solution = self.grid[:]
        not_prunable = set()
        while True:
            prunable = {i for i,v in enumerate(self.grid) if v != 0} - not_prunable
            if len(prunable)>0:
                idx = random.sample(prunable,1)[0]
                prev_num = self.grid[idx]
                self.grid[idx] = 0
                previous_grid = self.grid[:]
                self.tree = Tree(self.grid)
                valid = self.solve() 
                if not valid or not self.cmp_grid(solution):
                    not_prunable.add(idx)
                    self.grid = previous_grid
                    self.grid[idx] = prev_num
                self.grid = previous_grid
                self.tree = Tree(self.grid)
                if display:
                    print(self.tree, end='')
            else:
                break
        self.visited = []
        
    def generate_puzzle(self):
        self.generate_full_grid()
        self.prune_grid()
        return self.puzzle_level()
        
    def puzzle_level(self):
        # check https://www.nature.com/articles/srep00725
        
        # number of clues
        num_clues = len([i for i in self.grid if i != 0])
        
        # structure of the tree 
        grid = self.grid[:]
        self.visited = []
        self.tree = Tree(self.grid)
        self.solve() 
        num_branches = sdk.tree.num_branches()
        self.grid = grid
        self.visited = []
        self.tree = Tree(self.grid)
        
        return num_clues
    
    def read_grid(self, gridstr):
        self.reset_grid()
        for char in range(0,self.tot_size):
            n = gridstr[char]
            if n == '\n':
                break
            if n == ' ':
                self.grid[char] = 0
            else:
                self.grid[char] = ord(n)-48
                    
        self.tree = Tree(self.grid) 
    
    def write_grid(self):
        gridstr = "\n"
        for r in range(0,self.max_num):
            for c in range(0,self.max_num):
                idx  = self.sub2ind(r,c)
                if c == 0:
                    gridstr = gridstr + " "
                if self.grid[idx] == 0:
                    gridstr = gridstr + "  "
                else:
                    gridstr = gridstr + chr(48+self.grid[idx]) + " "
                if (c+1)//self.n > c//self.n:
                    if c == self.max_num-1:
                        gridstr = gridstr + " \n"
                        if (r+1)//self.n > r//self.n:
                            if r != self.max_num-1:
                                gridstr=gridstr+(self.n*(self.n+1)*2-1)*"-"+"\n"
                    else:
                        gridstr = gridstr + "| "
        return gridstr 
                
    def load_grid(self,filename):
        self.reset_grid()
        with open(filename,'r') as fin:
            for char in range(0,self.tot_size):
                n = fin.read(1)
                if n == '\n':
                    break
                if n == ' ':
                    self.grid[char] = 0
                else:
                    self.grid[char] = ord(n)-48
                    
        self.tree = Tree(self.grid) 
        
    def save_grid(self,filename):
        with open(filename,'w') as fout:
            for num in self.grid:
                if num == 0:
                    fout.write(' ')
                else:
                    fout.write(chr(48+num))
                    
    def export_grid(self,filename,cell_size=20):
        """export grid as svg""" 
        svgstring = "<svg height='"
        svgstring += str(cell_size*self.max_num)
        svgstring += "' width='"
        svgstring += str(cell_size*self.max_num)
        svgstring += "'>\n"
        
        # add background
        svgstring += "<rect width='100%' height='100%' fill='white'/>\n"
        
        # add nums
        for r in range(0,self.max_num):
            for c in range(0,self.max_num):
                idx = self.sub2ind(r,c)
                num = self.grid[idx]
                #TODO fontsize
                posx = c*cell_size+2.8/10*cell_size
                posy = r*cell_size+7.8/10*cell_size
                if num > 0:
                    svgstring += "<text" 
                    svgstring += " font-size='" + str(cell_size*72/96) + "'"
                    svgstring += " font-family='monospace'"
                    svgstring += " x='" + str(posx) +"'"
                    svgstring += " y='" + str(posy) +"'>"
                    if num == 12:
                        svgstring += "&lt;"
                    elif num == 14:
                        svgstring += "&gt;"
                    else:
                        svgstring += chr(48+num)
                    svgstring += "</text>\n"
        
        # add rows
        for r in range(0,self.max_num+1):
            x1 = 0
            y1 = r*cell_size
            x2 = cell_size*self.max_num
            y2 = r*cell_size
            if r%self.n == 0:
                lw = 1
            else:
                lw = .5
            svgstring += "<line"
            svgstring += " x1='" + str(x1) + "'"
            svgstring += " y1='" + str(y1) + "'"
            svgstring += " x2='" + str(x2) + "'"
            svgstring += " y2='" + str(y2) + "'"
            svgstring += " style='stroke:rgb(0,0,0);stroke-width:" + str(lw) + "'" 
            svgstring += "/>\n"
        
        # add columns    
        for c in range(0,self.max_num+1):
            x1 = c*cell_size
            y1 = 0
            x2 = c*cell_size
            y2 = cell_size*self.max_num
            if c%self.n == 0:
                lw = 1
            else:
                lw = .5
            svgstring += "<line"
            svgstring += " x1='" + str(x1) + "'"
            svgstring += " y1='" + str(y1) + "'"
            svgstring += " x2='" + str(x2) + "'"
            svgstring += " y2='" + str(y2) + "'"
            svgstring += " style='stroke:rgb(0,0,0);stroke-width:" + str(lw) + "'" 
            svgstring += "/>\n"
                    
        svgstring = svgstring + "</svg>"
        with open(filename,'w') as fout:
            fout.write(svgstring)
        
    def generate_full_grid(self,display=False):
        '''Use DFS to generate grid from an empty grid'''
        
        def grow_tree():
            (r,c,candidates) = self.get_most_constrained()
            for num in candidates:
                grid = self.grid[:]
                idx = self.sub2ind(r,c)
                grid[idx] = num
                child = Tree(grid)
                node.add_child(child)
            random.shuffle(node.children)
            
        self.reset_grid()
        stack = []
        root = self.tree
        stack.append(root)
        
        while len(stack)>0:
            node = stack.pop()
            if node not in self.visited:
                self.grid = node.grid[:]
                grow_tree()
                self.visited.append(node)
                for c in node.children:
                    stack.append(c)
                    
                if display:
                    print(node, end='')
                    
                if self.complete():
                    break
                    
    def solve(self,display=False):
        '''Use DFS to visit the tree of possible moves'''
        
        def grow_tree():
            (r,c,candidates) = self.get_most_constrained()
            for num in candidates:
                grid = self.grid[:]
                idx = self.sub2ind(r,c)
                grid[idx] = num
                child = Tree(grid)
                node.add_child(child)
            
        sol = []
        unique = True
        stack = []
        root = self.tree
        stack.append(root)
        
        while len(stack)>0:
            node = stack.pop()
            if node not in self.visited:
                self.grid = node.grid[:]
                grow_tree()
                self.visited.append(node)
                for c in node.children:
                    stack.append(c)
                
                # check if we have solved the puzzle
                if self.complete():
                    node.solution = True
                    if sol== []:
                        sol = self.grid[:]
                    else:
                        if not self.cmp_grid(sol):
                            unique = False
                
                if display:
                    print(node, end='')
                
                if not unique:
                    break
        
        self.grid = sol
        if self.complete() and unique:
            return True
        else:
            return False
        
    def get_most_constrained(self):
        moves = []
        unknown = [i for i,v in enumerate(self.grid) if v == 0]
        for idx in unknown:
            (r,c) = self.ind2sub(idx)
            candidates = self.get_uniq_candidate(r,c)
            moves.append((r,c,candidates))
    
        # select most constrained moves
        num_choice = [len(cand) for r,c,cand in moves]
        selected_moves = [(r,c,cand) for r,c,cand in moves if len(cand)==min(num_choice)]
        num_selected_moves = len(selected_moves)
        
        # get a random move
        if num_selected_moves>0:
            idx = random.randrange(0,num_selected_moves)
            return selected_moves[idx]
        else:
            return (0,0,[])
            
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
        # if only k same num in k cells, in a row/col/box they are fixed
        
        # TODO https://youtu.be/jU_W53M5aMQ?t=150
        # TODO https://youtu.be/jU_W53M5aMQ?t=204
        # TODO https://youtu.be/jU_W53M5aMQ?t=225
        
        candidate = self.get_candidate(r,c)
        ibox = self.box_ind(r,c)
        irow = self.row_ind(r)
        icol = self.col_ind(c)
        uniq_box = self.get_marginal(ibox,r,c)
        uniq_row = self.get_marginal(irow,r,c)
        uniq_col = self.get_marginal(icol,r,c)
        if len(uniq_box)==1:
            return uniq_box
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
            box = self.get_box(r,c)
            not_candidate = set(row+col+box)
            possible = {i for i in range(1,self.max_num+1)}
            candidate = list(possible - not_candidate)
            return candidate
        else:
            return []
    
    def reduction_rules(self,r,c,uniqueness=False):
        pass
        # check https://www.sudokuwiki.org/Getting_Started
        #
        # we call row/col/box a reduction unit
        
        # if a number is a candidate only in one cell in a reduction unit, then it takes that value
        # if two numbers are candidates only in two cells in a reduction unit, then those two cells can only take those two values
        # if k numbers are candidates only in k cells in a reduction unit, then those k cells can only take those k values
        
        # ideas to implement this:
        #   - with k=1 no problem, you can just update the grid 
        #   - a flag to state that the candidates are fixed so that it can be leveraged somewhere else in the grid
        #   - in general you can leverage that information if the k-uplet is "aligned" along one other reduction unit:
        #   aligned means the k-uplet is entirely contained in the reduction unit
        #   - as soon as fixed cell are identified, propagate this finding to the other two reduction units for each
        #   of the concerned cells (maybe a general list for each row/col/box)
        #   - when looking at each cell in a reduction unit, check if there are k-uplets
        #   - store a "pencil mark" list for each cell
        #   - maintain a global list of candidates and update it each time a number is added
        
        # uniqueness arguments: if the solution is unique, this puts a constraint on the numbers that can be used to guess
        # numbers. This should be an option because we cannot always assume the grid is well-posed 
        # how it works:
        # In the following grid 1 and 2 can be swapped and produce a valid grid.
        # For a solution to be unique, one of those 4 numbers should be a given
        #
        #         1 2   |       |        
        #               |       |        
        #               |       |        
        #        -----------------------
        #         2 1   |       |        
        #               |       |        
        #               |       |        
        #        -----------------------
        #               |       |        
        #               |       |        
        #               |       |   
        #    
        # Remark: this can be used to steer a backtracking attempt. This way it
        # is likely to speed up the process, but we can still land on our feet
        # if the puzzle is ill-posed. This is not as powerful as using uniqueness
        # to reduce the puzzle however
        # https://youtu.be/jU_W53M5aMQ?t=424
        
    def get_reduced_candidates(self,r,c,uniqueness=False):
        # apply reduction rules and return reduced candidates
        pass
        
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
    
    def box_ind(self,r,c):
        return [i for i in range(0,self.tot_size) 
            if (i//self.max_num)//self.n==r//self.n 
            and (i%self.max_num)//self.n==c//self.n]
        
    def get_row(self,r):
        return [self.grid[i] for i in self.row_ind(r)]
    
    def get_col(self,c):
        return [self.grid[i] for i in self.col_ind(c)]
    
    def get_box(self,r,c):
        return [self.grid[i] for i in self.box_ind(r,c)]
        
    def complete(self):
        if 0 in self.grid:
            return False
        else:
            return True
            
    def __repr__(self):
        return self.write_grid()
        


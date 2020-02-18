#!/usr/bin/python
import numpy as np
from tronproblem import TronProblem
import random, queue, math
import time
from implemented_adversarial import alpha_beta_cutoff

"""Moves in a random direction"""
class RandBot():
    def decide(self,asp):
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board,loc))
        if possibilities:
            return random.choice(possibilities)
        return 'U'

    def cleanup(self):
        pass


class WallBot():
    def __init__(self):
        order = ['U','D','L','R']
        random.shuffle(order)
        self.order = order

    def cleanup(self):
        order = ['U','D','L','R']
        random.shuffle(order)
        self.order = order
        
    def decide(self,asp):
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board,loc))
        if not possibilities:
            return 'U'
        decision = possibilities[0]
        for move in self.order:
            if move not in possibilities:
                continue
            next_loc = TronProblem.move(loc, move)
            if len(TronProblem.get_safe_actions(board,next_loc)) < 3:
                decision = move
                break
        return decision


class StudentBot():
    """ Write your student bot here"""
    def decide(self,asp):
        return 'U'

    def cleanup(self):
        pass


class TABot2():
    # a bot that greedily goes to the nearest powerup
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return self.findPower(start, self.player)
        
    def findPower(self, state, play_num):
        #a kind of bfs for the nearest powerup
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()
        
        Q = queue.Queue() 
        visited.add(origin)
        
        start_moves = list(TronProblem.get_safe_actions(board, origin))
        for direction in start_moves:
            neighbor = TronProblem.move(origin,direction)
            r,c = neighbor
            if board[r][c] == '*': #powerup
                return direction
            Q.put((neighbor,direction))
        
        
        while not Q.empty():
            curr, initdir = Q.get()
            r,c = curr
            valid_moves = list(TronProblem.get_safe_actions(board,curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                r,c = neighbor
                if board[r][c] == '*': #powerup
                    return initdir
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put((neighbor,initdir))

        # we couldn't find a powerup
        possibilities = list(TronProblem.get_safe_actions(board,origin))
        if possibilities:
            return random.choice(possibilities)
        return 'U'

    def cleanup(self):
        pass


class TABot1():
    # a bot that tries to leave itself as much space as possible
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return alpha_beta_cutoff(asp,3,self.heur)
        
    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))
        
    def heur(self,state):
        score = self.bfs(state,self.player)
        return self.sigmoid(score/200.0)
        
    def bfs(self,state,play_num): #a bounded search of how many tiles are accessible
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()
        Q = queue.Queue()
        Q.put(origin)
        visited.add(origin)
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(board,curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put(neighbor)
        return len(visited)

    def cleanup(self):
        pass


class TABot3():
    #a bot that tries to avoid getting trapped
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return alpha_beta_cutoff(asp,3,self.heur)

    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))
        
    def heur(self,state):
        me = self.freedom(state,self.player)
        opp = self.freedom(state,1-self.player)
        return self.sigmoid((me-opp)/50.0)

    def cleanup(self):
        pass

    def freedom(self,state,play_num):
        board = state.board
        origin = state.player_locs[play_num]
        freedom = 0
        for d1 in list(TronProblem.get_safe_actions(board,origin)):
            n1 = TronProblem.move(origin,d1)
            for d2 in list(TronProblem.get_safe_actions(board,n1)):
                n2 = TronProblem.move(origin,d2)
                for d3 in list(TronProblem.get_safe_actions(board,n2)):
                    freedom += 1
        return freedom

    def bfs(self,state,play_num): #a bounded search of how many tiles are accessible
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()
        Q = queue.Queue()
        Q.put(origin)
        visited.add(origin)
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(board,curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put(neighbor)
        return len(visited)


class VoronoiBot():
    def __init__(self):
        self.depth = None
        
    def sigmoid(self,x):
        return 1 / (1 + math.exp(-x))
        
    def decide(self,asp):
        #t1 = time.time()
        start = asp.get_start_state()
        if not self.depth:   
            board = start.board
            size = len(board) * len(board[0])
            if size < 300:
                self.depth = 4
            elif size < 700:
                self.depth = 3
            else:
                self.depth = 2
        
        self.player = start.player_to_move()
        decision = alpha_beta_cutoff(asp,self.depth,self.heur)
        #t2 = time.time()
        #print(t2-t1)
        return decision

    def heur(self,state):
        score = self.voronoi(state,self.player)
        return self.sigmoid(score / 200.0)

    def voronoi(self,state,play_num):
        board = state.board
        origin = state.player_locs[play_num]
        visited = {}
        Q = queue.Queue()
        Q.put(origin)
        visited[origin] = 0
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(board,curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                if neighbor not in visited:
                    visited[neighbor] = 1 + visited[curr]
                    Q.put(neighbor)

        score = 0
        
        opp_visited = {}
        
        origin = state.player_locs[1-play_num]
        Q.put(origin)
        opp_visited[origin] = 0
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(board,curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                if neighbor not in opp_visited:
                    opp_visited[neighbor] = 1 + opp_visited[curr]
                    if neighbor in visited:
                        if opp_visited[neighbor] < visited[neighbor]:
                            score -= 1
                        elif opp_visited[neighbor] > visited[neighbor]:
                            score += 1
                    Q.put(neighbor)
        for pos in list(visited.keys()):
            if pos not in opp_visited:
                score += 1
        for pos in list(opp_visited.keys()):
            if pos not in visited:
                score -= 1
        return score

    def cleanup(self):
        self.depth = None


"""
Grant's Ideas:
    Multiple types of modes:
        Space saving (If there is no chance of random things)
        Powerups (if the other bot is close to)
        Safety (If the other bot is close to powerups)
    How to toggle between modes?
    Running things on smaller subsections to a greater depth?
    Learning:
        See if it is a greedy bot/if it is going towards power ups
    Early game vs late game
    Go to clusters of powerups
    
    Have diffrent modes - depending on threshold values, we calculate certain heuristics, combine them, or dont
"""


class gfong1():
    def __init__(self):
        from scipy.stats import norm
        self.powerup_loc = None
        self.state = None
        self.board = None
        self.board_height = None
        self.board_width = None
        self.powerup_heatmap = None
        self.depth = None
        self.player = None

        # Setup the normal map
        dist = norm(0, 2)
        self.max_frame_size = 20
        self.boundary_size = self.max_frame_size * 2 + 1 # always double the size of the arrays in x and y, adding 1 to be odd
        self.normal_map = np.zeros((self.boundary_size, self.boundary_size))
        for i in range(self.boundary_size):
            for j in range(self.boundary_size):
                distance = math.hypot(self.max_frame_size - i, self.max_frame_size - j)
                self.normal_map[i][j] = dist.pdf(distance)

    def setup(self):
        """Set up all variables on the first turn"""
        self.turns_played = 0
        self.board_height = len(self.board)
        self.board_width = len(self.board[0])
        self.powerup_loc = self.find_powerups()
        self.powerup_heatmap = self.smart_powerup_setup()
        self.player = self.state.player_to_move()

        size = len(self.board) * len(self.board[0])
        if size < 300:
            self.depth = 3
        elif size < 700:
            self.depth = 2
        else:
            self.depth = 1

    def max_min(self, val, min_val, max_val):
        return max(min(val, max_val), min_val)

    def sigmoid(self,x):
        return 1 / (1 + math.exp(-x))

    def voronoi_heur(self, state):
        score = self.voronoi(state, self.player)
        return self.sigmoid(score / 200.0)


    ###########################
    #       Scared  BOT       #
    ###########################

    def safe_heur(self, state):
        me = self.freedom(state, self.player)
        opp = self.freedom(state, 1 - self.player)
        return self.sigmoid((me - opp) / 50.0)

    def freedom(self, state, play_num):
        board = state.board
        origin = state.player_locs[play_num]
        freedom = 0
        for d1 in list(TronProblem.get_safe_actions(board, origin)):
            n1 = TronProblem.move(origin, d1)
            for d2 in list(TronProblem.get_safe_actions(board, n1)):
                n2 = TronProblem.move(origin, d2)
                for d3 in list(TronProblem.get_safe_actions(board, n2)):
                    freedom += 1
        return freedom

    def bfs(self, state, play_num):  # a bounded search of how many tiles are accessible
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()
        Q = queue.Queue()
        Q.put(origin)
        visited.add(origin)
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(board, curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put(neighbor)
        return len(visited)

    ###########################
    #    dumb POWERUP BOT     #
    ###########################

    def findPower(self, state, play_num):
        # a kind of bfs for the nearest powerup
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()

        Q = queue.Queue()
        visited.add(origin)

        start_moves = list(TronProblem.get_safe_actions(board, origin))
        for direction in start_moves:
            neighbor = TronProblem.move(origin, direction)
            r, c = neighbor
            if board[r][c] == '*':  # powerup
                return direction
            Q.put((neighbor, direction))

        while not Q.empty():
            curr, initdir = Q.get()
            r, c = curr
            valid_moves = list(TronProblem.get_safe_actions(board, curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                r, c = neighbor
                if board[r][c] == '*':  # powerup
                    return initdir
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put((neighbor, initdir))

        # we couldn't find a powerup
        possibilities = list(TronProblem.get_safe_actions(board, origin))
        if possibilities:
            return random.choice(possibilities)
        return 'U'

    ###########################
    #    smart POWERUP BOT    #
    ###########################
    def find_powerups(self):
        """find all powerups and returns their locations"""
        raw_locations = np.where(self.board == '*')
        cleaned_locations = []
        for i in range(len(raw_locations[0])):
            cleaned_locations.append((raw_locations[0][i], raw_locations[1][i]))
        return np.array(cleaned_locations)

    def clutter(self, loc):
        """calculates how good a powerup will by by caclulating the ratio of how many things are filled in a ring"""
        # I was too lazy to think how to code this nicely so i hard coded it
        hardcoded_indecies = [(-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
                              (-2, -1), (2, -1),
                              (-2, 0), (2, 0),
                              (-2, 1), (2, 1),
                              (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2)]
        total_unfilled = 0
        for i in hardcoded_indecies:
            adjusted_loc = (
                self.max_min(loc[0] + i[0], 0, self.board_width-1),
                self.max_min(loc[1] + i[1], 0, self.board_height-1),
            )
            if self.board[adjusted_loc] in set(['*', ' ']):
                total_unfilled += 1
        return total_unfilled

    def nearest_powerup(self, loc):
        """Returns the nearest powerup"""
        deltas = self.powerup_loc - loc
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return self.powerup_loc[np.argmin(dist_2)]

    def update_powerups(self):
        """if the opponent is on a powerup, or you are on it, update avaliable powerups"""
        locs = self.state.player_locs
        ptm = self.state.ptm
        player_loc = locs[ptm]
        opponent_loc = locs[ptm-1]
        num_removed_elements = 0
        for i in range(len(self.powerup_loc)):
            curr_index = i - num_removed_elements
            powerup = self.powerup_loc[curr_index]
            if np.array_equal(player_loc, powerup) or np.array_equal(opponent_loc, powerup):
                self.powerup_loc = np.delete(self.powerup_loc, curr_index, 0)
                num_removed_elements += 1
        self.powerup_heatmap = self.smart_powerup_setup()

    def smart_powerup_setup(self):
        """evaluate moves based off importance of powerups"""
        self.powerup_heatmap = np.zeros((self.board_height, self.board_width))
        for powerup in self.powerup_loc:
            self.apply_map(powerup[0], powerup[1])
        return self.powerup_heatmap / sum(self.powerup_heatmap)

    def apply_map(self, x, y):
        """Applies the normal map over a certain location"""
        x_lower = self.max_frame_size - x
        x_upper = self.board_width + x_lower
        y_lower = self.max_frame_size - y
        y_upper = self.board_height + y_lower
        section = self.normal_map[y_lower:y_upper, x_lower:x_upper]
        self.powerup_heatmap = np.add(self.powerup_heatmap, section)

    def voronoi_with_powerups(self, state):
        """
        This is used to calculate the manhattan distance for each player to get to a specific location. If a point is
        unreachable, it fills the value with positive infinity

        :param board: The board to be evaluated on
        :param cords: The starting location of the heuristic as a tuple
        :return: Returns a 2D list of values with distances to that point.
        """
        board = state.board
        cords = state.player_locs[state.ptm]
        q = queue.Queue()
        s = set()
        v = [[float("inf") for i in range(self.board_height)] for j in range(self.board_width)]
        for i in range(self.board_height):
            for j in range(self.board_width):
                if board[i][j] == "#":
                    # tuple is (# moves, visited), 1 = visited
                    s.add((i, j))

        q.put(cords)
        v[cords[0]][cords[1]] = 0
        s.add(cords)
        while not q.empty():
            curr = q.get()
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if not (i and j):
                        n = (curr[0] + i, curr[1] + j)
                        if n not in s:
                            # if that node has not been visited, and has a score less than the current value
                            v[n[0]][n[1]] = v[curr[0]][curr[1]] + 1  # set score equal to that
                            s.add(n)
                            q.put(n)
        return np.add(v, self.powerup_heatmap).tolist()

    ###########################
    #       VORONOI BOT       #
    ###########################

    def voronoi(self, state, play_num):
        """Basic voronoi implementation"""
        origin = state.player_locs[play_num]
        visited = {}
        Q = queue.Queue()
        Q.put(origin)
        visited[origin] = 0
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(self.board, curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                if neighbor not in visited:
                    visited[neighbor] = 1 + visited[curr]
                    Q.put(neighbor)

        score = 0

        opp_visited = {}

        origin = state.player_locs[1 - play_num]
        Q.put(origin)
        opp_visited[origin] = 0
        while not Q.empty():
            curr = Q.get()
            valid_moves = list(TronProblem.get_safe_actions(self.board, curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                if neighbor not in opp_visited:
                    opp_visited[neighbor] = 1 + opp_visited[curr]
                    if neighbor in visited:
                        if opp_visited[neighbor] < visited[neighbor]:
                            score -= 1
                        elif opp_visited[neighbor] > visited[neighbor]:
                            score += 1
                    Q.put(neighbor)
        for pos in list(visited.keys()):
            if pos not in opp_visited:
                score += 1
        for pos in list(opp_visited.keys()):
            if pos not in visited:
                score -= 1
        return score

    def decide(self, asp):
        # Update stored states and boards
        if not self.state:
            self.state = asp.get_start_state()
            self.board = np.array(self.state.board)
            self.setup()
        else:
            self.board = np.array(self.state.board)
            self.state = asp.get_start_state()
        #
        # Powerups #
        self.player = self.state.player_to_move()
        self.update_powerups()
        self.turns_played += 1

        # return alpha_beta_cutoff(asp, self.depth, self.voronoi_with_powerups)
        clutter = self.clutter(self.state.player_locs[self.state.ptm])
        if clutter < 4:
            return alpha_beta_cutoff(asp, self.depth, self.voronoi_heur)
        elif clutter < 6:
            return alpha_beta_cutoff(asp, 3, self.safe_heur)

        if self.turns_played < 10:
            # print('Power Mode')
            decision = self.findPower(self.state, self.player)
        elif self.turns_played < 30:
            decision = alpha_beta_cutoff(asp, 3, self.safe_heur)
        else:
            decision = alpha_beta_cutoff(asp, self.depth, self.voronoi_heur)

        return decision


    def cleanup(self):
        pass

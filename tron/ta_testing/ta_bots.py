""" 
File contains TA bots and a TA implementation of alpha_beta_cutoff 
specifically made for tron.
TA1: bot that uses alpha-beta cutoff, with a heuristic that tries to
    leave itself as much space as possible
TA2: bot that uses alpha-beta cutoff, with a heuristic that tries to 
    maximize its space compared to its opponents space
TA2_old: a bot that charges toward the nearest powerup, and acts randomly
    if it can't reach any. 
    ***Not used for grading purposes this year. 

We compiled the code into a .so file using:
python -m nuitka --module <python_file>

Then, we can delete all of the extra files it creates and we can import from 
the .so file as normal. This allow the students to compete against the ta bots 
without showing them the code 
"""

import numpy as np
from tronproblem import TronProblem
from trontypes import CellType
import random, queue, math



def _get_safe_actions_random(board, loc):
    actions = list(TronProblem.get_safe_actions(board, loc))
    random.shuffle(actions)
    return actions

# OUTPUT SPEC: All functions below output an action. More specifically,
# they output an element of asp.get_available_actions(asp.get_start_state())

def alpha_beta_cutoff(asp, cutoff_turn, eval_func):
    """
    An implementation of the alpha_beta_cutoff algorithm that is specifically
    written for the TronProblem (it only considers safe actions)
    """
    state = asp.get_start_state()
    player = state.player_to_move()
    best_action = 'D'
    best_value = -float('inf')
    a = -float('inf')
    b = float('inf')

    for action in _get_safe_actions_random(state.board, state.player_locs[player]):
        next_state = asp.transition(state,action)
        value = abchelper(asp,next_state,cutoff_turn-1,a,b,False,eval_func,player)
        #print 'action: %s' % action
        #print 'value: %s' % value
        if value >= best_value:
            best_value = value
            best_action = action
        a = max(a,best_value)
        if b <= a:
            break
    return best_action

def abchelper(asp,state,depth,a,b,maximizing,eval_func,player):
    if asp.is_terminal_state(state):
        payoffs = asp.evaluate_state(state)
        return payoffs[player]
    if depth == 0:
        return eval_func(state)
    if maximizing:
        best = -float('inf')
        for action in asp.get_available_actions(state):
            next_state = asp.transition(state,action)
            v = abchelper(asp,next_state,depth-1,a,b,not maximizing,eval_func,player)
            best = max(best,v)
            a = max(a,best)
            if b <= a:
                break
        return best
    else:
        best = float('inf')
        for action in asp.get_available_actions(state):
            next_state = asp.transition(state,action)
            v = abchelper(asp,next_state,depth-1,a,b,not maximizing,eval_func,player)
            best = min(best,v)
            b = min(b,best)
            if b <= a:
                break
        return best


class TABot1():
    """a bot that tries to leave itself as much space as possible"""
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return alpha_beta_cutoff(asp,3,self.heur)

    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))

    def heur(self,state):
        score = self.bfs(state,self.player)
        #scale score down so the sigmoid function is more responsive
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
            valid_moves = _get_safe_actions_random(board,curr)
            for direction in valid_moves:
                neighbor = TronProblem.move(curr,direction)
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put(neighbor)
        return len(visited)

    def cleanup(self):
        pass

class TABot2():
    """
    Written by Grant M (when he was a student)
    Uses alpha beta cutoff. The heuristic is a bidirectional BFS search
    from each players location, meant to estimate "controlled" space.
    
    """
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return alpha_beta_cutoff(asp,3,self.heur)

    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))

    def heur(self,state):
        score = self.bfsadverse(state, self.player)
        # scale score down so the sigmoid function is more responsive.
        return self.sigmoid((score+50)/200.0)

    def bfsadverse(self, state, play_num):
        board = state.board
        origin1 = state.player_locs[play_num]
        origin2 = state.player_locs[1-play_num]
        visited1 = set()
        visited2 = set()
        score_1 = 1
        score_2 = 1
        Q1 = queue.Queue()
        Q2 = queue.Queue()

        Q1.put(origin1)
        Q2.put(origin2)

        visited1.add(origin1)
        visited2.add(origin2)

        isQ1 = True

        while (not Q1.empty()) or (not Q2.empty()):
            # determine which queue to draw from and and withdraw
            # from that queue into curr
            if isQ1:
                if Q1.empty():
                    curr = Q2.get()
                    isQ1 = False
                else:
                    curr = Q1.get()
            else:
                if Q2.empty():
                    curr = Q1.get()
                    isQ1 = True
                else:
                    curr = Q2.get()
            valid_moves = _get_safe_actions_random(board, curr)
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                #if its a neighbor we haven't visited, add 1 to the score for
                #the player of the queue we took from
                if(neighbor not in visited1 and neighbor not in visited2):
                    if isQ1:
                        Q1.put(neighbor)
                        visited1.add(neighbor)
                        score_1 +=1
                    else:
                        Q2.put(neighbor)
                        visited2.add(neighbor)
                        score_2 +=1
            #alternate which queue we try to take from
            isQ1 = not isQ1
        assert Q1.empty()
        assert Q2.empty()
        return score_1 - score_2

    def cleanup(self):
        pass


class TABot2_old():
    """a bot that always charges to the nearest powerup"""
    def __init__(self):
        self.powerups = CellType.powerup_list

    # a bot that greedily goes to the nearest powerup
    def decide(self, asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        return self.findPower(start, self.player)

    def findPower(self, state, play_num):
        # a kind of bfs for the nearest powerup
        board = state.board
        origin = state.player_locs[play_num]
        visited = set()

        Q = queue.Queue()
        visited.add(origin)

        start_moves = _get_safe_actions_random(board, origin)
        for direction in start_moves:
            neighbor = TronProblem.move(origin, direction)
            r, c = neighbor
            if board[r][c] in self.powerups:  # powerup
                return direction
            Q.put((neighbor, direction))

        while not Q.empty():
            curr, initdir = Q.get()
            r, c = curr
            valid_moves = _get_safe_actions_random(board, curr)
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                r, c = neighbor
                if board[r][c] in self.powerups:  # powerup
                    return initdir
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put((neighbor, initdir))

        # we couldn't find a powerup
        possibilities = _get_safe_actions_random(board, origin)
        if possibilities:
            return random.choice(possibilities)
        return 'U'

    def cleanup(self):
        pass

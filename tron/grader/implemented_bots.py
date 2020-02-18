#!/usr/bin/python
import numpy as np
from tronproblem_sol import TronProblem
import random, queue, math
import time
from implemented_adversarial_sol import alpha_beta_cutoff

"""Moves in a random direction"""


class RandBot:
    def decide(self, asp):
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if possibilities:
            return random.choice(possibilities)
        return "U"

    def cleanup(self):
        pass


class WallBot:
    def __init__(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def cleanup(self):
        order = ["U", "D", "L", "R"]
        random.shuffle(order)
        self.order = order

    def decide(self, asp):
        state = asp.get_start_state()
        locs = state.player_locs
        board = state.board
        ptm = state.ptm
        loc = locs[ptm]
        possibilities = list(TronProblem.get_safe_actions(board, loc))
        if not possibilities:
            return "U"
        decision = possibilities[0]
        for move in self.order:
            if move not in possibilities:
                continue
            next_loc = TronProblem.move(loc, move)
            if len(TronProblem.get_safe_actions(board, next_loc)) < 3:
                decision = move
                break
        return decision


def _get_safe_actions_random(board, loc):
    actions = list(TronProblem.get_safe_actions(board, loc))
    random.shuffle(actions)
    return actions


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

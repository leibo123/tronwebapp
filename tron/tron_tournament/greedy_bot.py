#!/usr/bin/python
import numpy as np
from tronproblem import TronProblem
import random, queue, math


class GreedyBot:
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

        start_moves = list(TronProblem.get_safe_actions(board, origin))
        for direction in start_moves:
            neighbor = TronProblem.move(origin, direction)
            r, c = neighbor
            if board[r][c] == "*":  # powerup
                return direction
            Q.put((neighbor, direction))

        while not Q.empty():
            curr, initdir = Q.get()
            r, c = curr
            valid_moves = list(TronProblem.get_safe_actions(board, curr))
            for direction in valid_moves:
                neighbor = TronProblem.move(curr, direction)
                r, c = neighbor
                if board[r][c] == "*":  # powerup
                    return initdir
                if neighbor not in visited:
                    visited.add(neighbor)
                    Q.put((neighbor, initdir))

        # we couldn't find a powerup
        possibilities = list(TronProblem.get_safe_actions(board, origin))
        if possibilities:
            return random.choice(possibilities)
        return "U"

    def cleanup(self):
        pass

#!/usr/bin/python

import numpy as np
from tronproblem import TronProblem
import random, Queue, math
from implemented_adversarial import alpha_beta_cutoff

class StudentBot():
    """ Write your student bot here"""
    def __init__(self):
        self.play_num = 0
        self.split = False
    def decide(self,asp):
        start = asp.get_start_state()
        self.asp = asp
        self.player = start.player_to_move()
        self.enemy = (self.player + 1) % 2
        if self.split:
            return alpha_beta_cutoff(asp, 3, self.separated_heur)
        else:
            if self.separated(start, asp):
                self.split = True
                return alpha_beta_cutoff(asp, 3, self.separated_heur)
            else:
                self.powerup_val = 3
        return alpha_beta_cutoff(asp,3,self.heur)
    
    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))

    def heur(self, state):
        score = self.fillboard(state,self.player, self.enemy)
        #scale score down so the sigmoid function is more responsive
        return self.sigmoid(score/200.0)

    def separated_heur(self, state):
        score = self.fillboard_separated(state, self.player, self.enemy)
        return self.sigmoid(score/200.0)

    def separated(self, state, asp):
        myboard = np.array(state.board)
        locs = state.player_locs
        myloc = locs[state.ptm]
        myQ = Queue.Queue()
        myQ.put(myloc)
        myvisited = {myloc}
        enemyloc = locs[state.ptm-1]
        while not myQ.empty():
            mycur = myQ.get()
            allmoves = list(asp.get_available_actions(state))
            for direction in allmoves:
                neighbor = TronProblem.move(mycur, direction)
                if neighbor in myvisited:
                    continue
                if neighbor == enemyloc: # if enemy is accessible, then not seperated
                    return False;
                elif myboard[neighbor] == ' ' or myboard[neighbor] == '*':
                    myQ.put(neighbor)
                    myvisited.add(neighbor)
        return True

    def get_surroundings(self, state, myloc, radius):
        # return how many empty spaces in the surrounding locations
        # when radius is 1 (3x3), 8 locations; when radius is 2 (5x5), 16 locations

        r, c = myloc
        radiusSet = []

        for x in range(-radius, radius+1):
            for a in [-radius, radius]:
                radiusSet.append((r+a, c+x))

        for x in range(-radius + 1, radius):
            for a in [-radius, radius]:
                radiusSet.append((r+x, c+a))

        # remove coordinates out of board boundary

        width = 15
        height = 15
        ret = []

        for a in range(0, len(radiusSet)):
            if radiusSet[a][0] >= 0 and radiusSet[a][0] < height and radiusSet[a][1] >= 0 and radiusSet[a][1] < width:
                ret.append((radiusSet[a][0],radiusSet[a][1]))

        empty_spaces = 0
        floodboard = np.array(state.board)
        for c in ret:
            if floodboard[c] != '#' and floodboard[c] != 'x':
                empty_spaces += 1
        return empty_spaces
    
    def get_wall(self, state, myloc):
        # return how many walls are in U, R, L, D 4 positions

        r, c = myloc
        radiusSet = [(myloc[0]+1, myloc[1]), (myloc[0]-1, myloc[1]), (myloc[0], myloc[1]+1), (myloc[0], myloc[1]-1)]
        walls = 0
        floodboard = np.array(state.board)
        for c in radiusSet:
            if floodboard[c] == '#':
                walls += 1
        return walls

    def fillboard(self, state, me, enemy):
        board = state.board
        locs = state.player_locs
        myloc = locs[me]
        enemyloc = locs[enemy]
        enemyspace = self.get_surroundings(state, enemyloc, 2)
        floodboard = np.array(board)
        closebonus = 0
        if floodboard[myloc] == '*':
            floodboard[myloc] = 'A' #my powerup
            closebonus += 2
        else:
            floodboard[myloc] = 'M' #'M' for me
        if floodboard[enemyloc] == '*':
            floodboard[enemyloc] = 'B' #enemy powerup
        else:
            floodboard[enemyloc] = 'E' #'E' for enemy

        for direction in list(TronProblem.get_safe_actions(board, myloc)):
            neighbor = TronProblem.move(myloc, direction)
            if floodboard[neighbor] == '*':
                closebonus += 1

        myvisited = {myloc}
        enemyvisited = {enemyloc}
        myQ = Queue.Queue()
        myQ.put(myloc)
        enemyQ = Queue.Queue()
        enemyQ.put(enemyloc)
        myneighbors = set()
        enemyneighbors = set()
        colored = False
        # KEY
        # A powerup
        # M colored tile me
        # N non-colored tile me
        # keep going until no new positions are added to the queues
        while not myQ.empty() or not enemyQ.empty():
            while not myQ.empty():
                #I fill first
                mycur = myQ.get()
                valid_moves = list(TronProblem.get_safe_actions(board,mycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(mycur, direction)
                    if neighbor not in myvisited and not (floodboard[neighbor] == 'E' or floodboard[neighbor] == 'F' or floodboard[neighbor] == 'B'):
                        if floodboard[neighbor] == '*': #if tile is a powerup
                            if colored:
                                floodboard[neighbor] = 'A' #Let 'A' represent a 'M' space with powerup
                            else:
                                floodboard[neighbor] = 'C' #not colored mine
                        else:
                            if colored:
                               floodboard[neighbor] = 'M'
                            else:
                                floodboard[neighbor] = 'N'
                        myvisited.add(neighbor)
                        myneighbors.add(neighbor)
            while not enemyQ.empty():
                #Then enemy fills
                enemycur = enemyQ.get()
                valid_moves = list(TronProblem.get_safe_actions(board, enemycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(enemycur, direction)
                    if neighbor not in enemyvisited and not (floodboard[neighbor] == 'M' or floodboard[neighbor] == 'N' or floodboard[neighbor] == 'A'):
                        if floodboard[neighbor] == '*':
                            if colored:
                                floodboard[neighbor] = 'B' #Let 'B' represent a 'E' space with powerup
                            else:  
                                floodboard[neighbor] = 'D' #not colored enemy
                        else:
                            if colored:
                                floodboard[neighbor] = 'E'
                            else:
                                floodboard[neighbor] = 'F'
                        enemyvisited.add(neighbor)
                        enemyneighbors.add(neighbor)
            colored = not colored
            map(myQ.put, myneighbors) #put all the newfound neighbors onto queue for next iteration
            myneighbors = set() #reset neighbors set
            map(enemyQ.put, enemyneighbors)
            enemyneighbors = set()

        numM = np.count_nonzero(floodboard == 'M') #count the number of colored tiles I reach first
        numN = np.count_nonzero(floodboard == 'N') #count the number of non-colored tiles I reach first
        numMpwr = np.count_nonzero(floodboard == 'A') #count the number of powerup tiles I reach first
        numNpwr = np.count_nonzero(floodboard == 'C')
        numE = np.count_nonzero(floodboard == 'E') #count the number of colored tiles that enemy reaches first
        numF = np.count_nonzero(floodboard == 'F') #count the number of non-colored tiles that enemy reaches first
        numEpwr = np.count_nonzero(floodboard == 'B') #count the number of powerup tiles that enemy reaches first
        numFpwr = np.count_nonzero(floodboard == 'D')
        val = (min(numM + numMpwr*self.powerup_val, numN + numNpwr*self.powerup_val) + (numMpwr+ numNpwr)*self.powerup_val) - (min(numE + numEpwr*self.powerup_val, numF + numFpwr*self.powerup_val) + (numEpwr + numFpwr)*self.powerup_val) #maximize the difference between our spaces
        return val + closebonus

    def fillboard_separated(self, state, me, enemy):
        board = state.board
        locs = state.player_locs
        myloc = locs[me]
        enemyloc = locs[enemy]
        floodboard = np.array(board)
        depthM = 0
        depthE = 0
        gamma = .3
        numMpwrDiscounted = 0
        numEpwrDiscounted = 0
        if floodboard[myloc] == '*':
            numMpwrDiscounted += (gamma ** depthM) * 4
            floodboard[myloc] = 'A'
        else:
            floodboard[myloc] = 'M'#'M' for me
        if floodboard[enemyloc] == '*':
            numEpwrDiscounted += (gamma ** depthE) * 4
            floodboard[enemyloc] = 'B' #'E' for enemy
        else:
            floodboard[enemyloc] = 'E'
        myvisited = {myloc}
        enemyvisited = {enemyloc}
        myQ = Queue.Queue()
        myQ.put(myloc)
        enemyQ = Queue.Queue()
        enemyQ.put(enemyloc)
        myneighbors = set()
        enemyneighbors = set()
        numEDisc =0
        numMDisc =0
        # keep going until no new positions are added to the queues
        while not myQ.empty() or not enemyQ.empty():
            while not myQ.empty():
                #I fill first
                mycur = myQ.get()
                depthM +=1
                valid_moves = list(TronProblem.get_safe_actions(board,mycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(mycur, direction)
                    if neighbor not in myvisited and not (floodboard[neighbor] == 'E' or floodboard[neighbor] == 'B'):
                        if floodboard[neighbor] == '*': #if tile is a powerup
                            numMpwrDiscounted += (gamma ** depthM) * 2
                            floodboard[neighbor] = 'A' #Let 'A' represent a 'M' space with powerup
                        else:
                            floodboard[neighbor] = 'M'
                            #numMDisc += (gamma ** depthM) *2
                        myvisited.add(neighbor)
                        myneighbors.add(neighbor)
            while not enemyQ.empty():
                #Then enemy fills
                enemycur = enemyQ.get()
                depthE +=1
                valid_moves = list(TronProblem.get_safe_actions(board, enemycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(enemycur, direction)
                    if neighbor not in enemyvisited and not (floodboard[neighbor] == 'M' or floodboard[neighbor] == 'A'):
                        if floodboard[neighbor] == '*':
                            numEpwrDiscounted += (gamma ** depthE) * 2
                            floodboard[neighbor] = 'B' #Let 'B' represent a 'E' space with powerup
                        else:
                            floodboard[neighbor] = 'E'
                            #numEDisc += (gamma ** depthE) *2
                        enemyvisited.add(neighbor)
                        enemyneighbors.add(neighbor)
            map(myQ.put, myneighbors) #put all the newfound neighbors onto queue for next iteration
            myneighbors = set() #reset neighbors set
            map(enemyQ.put, enemyneighbors)
            enemyneighbors = set()
        numM = np.count_nonzero(floodboard == 'M') #count the number of tiles I reach first
        numMpwr = np.count_nonzero(floodboard == 'A') #count the number of powerup tiles I reach first
        numE = np.count_nonzero(floodboard == 'E') #count the number of tiles that enemy reaches first
        numEpwr = np.count_nonzero(floodboard == 'B') #count the number of powerup tiles that enemy reaches first
        val = (numM + 4*numMpwrDiscounted) - (numE + numEpwrDiscounted) #maximize the difference between our spaces

        return val + 10*self.get_wall(state, myloc)

    def cleanup(self):
        self.split = False

class TournamentBot(StudentBot):
    BOT_NAME = "Dr. Pepper"

class StudentBot2():
    """ Write your student bot here"""
    def __init__(self):
        self.play_num = 0
    def decide(self,asp):
        start = asp.get_start_state()
        self.player = start.player_to_move()
        self.enemy = (self.player + 1) % 2
        return alpha_beta_cutoff(asp,3,self.heur)
    
    def sigmoid(self,x):
        #a function that maps any real number to a value between 0 and 1
        return 1 / (1 + math.exp(-x))

    def heur(self, state):
        score = self.fillboard(state,self.player, self.enemy)
        #scale score down so the sigmoid function is more responsive
        return self.sigmoid(score/200.0)

    def fillboard(self, state, me, enemy):
        board = state.board
        locs = state.player_locs
        myloc = locs[me]
        enemyloc = locs[enemy]
        floodboard = np.array(board)
        if floodboard[myloc] == '*':
            floodboard[myloc] = 'A' #my powerup
        else:
            floodboard[myloc] = 'M' #'M' for me
        if floodboard[enemyloc] == '*':
            floodboard[enemyloc] = 'B' #enemy powerup
        else:
            floodboard[enemyloc] = 'E' #'E' for enemy
        myvisited = {myloc}
        enemyvisited = {enemyloc}
        myQ = Queue.Queue()
        myQ.put(myloc)
        enemyQ = Queue.Queue()
        enemyQ.put(enemyloc)
        myneighbors = set()
        enemyneighbors = set()
        # keep going until no new positions are added to the queues
        while not myQ.empty() or not enemyQ.empty():
            while not myQ.empty():
                #I fill first
                mycur = myQ.get()
                valid_moves = list(TronProblem.get_safe_actions(board,mycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(mycur, direction)
                    if neighbor not in myvisited and not (floodboard[neighbor] == 'E' or floodboard[neighbor] == 'B'):
                        if floodboard[neighbor] == '*': #if tile is a powerup
                            floodboard[neighbor] = 'A' #Let 'A' represent a 'M' space with powerup
                        else: 
                            floodboard[neighbor] = 'M' 
                        myvisited.add(neighbor)
                        myneighbors.add(neighbor)
            while not enemyQ.empty():
                #Then enemy fills
                enemycur = enemyQ.get()
                valid_moves = list(TronProblem.get_safe_actions(board, enemycur))
                for direction in valid_moves:
                    neighbor = TronProblem.move(enemycur, direction)
                    if neighbor not in enemyvisited and not (floodboard[neighbor] == 'M' or floodboard[neighbor] == 'A'):
                        if floodboard[neighbor] == '*':
                            floodboard[neighbor] = 'B' #Let 'B' represent a 'E' space with powerup
                        else: 
                            floodboard[neighbor] = 'E' 
                        enemyvisited.add(neighbor)
                        enemyneighbors.add(neighbor)
            map(myQ.put, myneighbors) #put all the newfound neighbors onto queue for next iteration
            myneighbors = set() #reset neighbors set
            map(enemyQ.put, enemyneighbors)
            enemyneighbors = set()
        numM = np.count_nonzero(floodboard == 'M') #count the number of tiles I reach first
        numMpwr = np.count_nonzero(floodboard == 'A') #count the number of powerup tiles I reach first
        numE = np.count_nonzero(floodboard == 'E') #count the number of tiles that enemy reaches first
        numEpwr = np.count_nonzero(floodboard == 'B') #count the number of powerup tiles that enemy reaches first
        val = (numM + numMpwr) - (numE + numEpwr) #maximize the difference between our spaces
        return val

    def cleanup(self):
        pass

class RandBot():
    """Moves in a random (safe) direction"""
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
    """Hugs the wall"""
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
        Q = Queue.Queue()
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

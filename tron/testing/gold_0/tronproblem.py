from adversarialsearchproblem import AdversarialSearchProblem, GameState
import random

class TronState(GameState):
    def __init__(self, board, player_locs, ptm):
        """
        board: a list of lists of characters representing tiles ('#' for wall, ' ' for space, etc.)
        player_locs: a list of tuples (representing the players' locations)
        ptm: the player whose move it is

        player_locs and ptm are indexed the same way, so player_locs[ptm] would
        give the location of the player whose move it is.

        We don't represent the players' locations anywhere in board, only in player_locs
        So if we call
        r,c = player_locs[ptm]
        print board[r][c]

        we will print whatever the tile was before you moved into it (either a space
        or a powerup). It's only when you make your move that we fill in your previous
        location with a barrier. 
        """
        self.board = board
        self.player_locs = player_locs
        self.ptm = ptm

    def player_to_move(self):
        return self.ptm

W = '#' # character for wall
B = 'x' #character for Barrier
S = ' ' # character for space
P = '*' # character for powerup.
powerup_strength = 3
# directions to move
U = 'U'
D = 'D'
L = 'L'
R = 'R'

class TronProblem(AdversarialSearchProblem):

    def __init__(self, board_file_loc, first_player):
        # write a function to determine those two from the board
        board = TronProblem._board_from_board_file(board_file_loc)
        player_locs = TronProblem._player_locs_from_board(board)
        

        self._start_state = TronState(board, player_locs, first_player)
        self._num_players = len(player_locs)

    ###### ADVERSARIAL SEARCH PROBLEM IMPLEMENTATION ######

    def get_available_actions(self, state):
        """
        We assume that the player to move is never on the edges of the map.
        All pre-made maps are surrounded by walls to validate this assumption.
        """
        return {U, D, L, R}

    def transition(self, state, action):
        assert not(self.is_terminal_state(state))
        assert action in self.get_available_actions(state)

        # prepare parts of result state
        board = [[elt for elt in row] for row in state.board]
        player_locs = [loc for loc in state.player_locs]
        next_ptm = (state.ptm + 1) % self._num_players
        while player_locs[next_ptm] == None:
            next_ptm = (next_ptm + 1) % self._num_players
        # note that, given the assumption that state is non-terminal,
        # there will be at least 2 players still on the board when
        # going through this loop.
        
        # get original position of player to move before transitioning
        r0, c0 = state.player_locs[state.ptm]

        # lay down a barrier where the player was before
        board[r0][c0] = B

        # get target location after moving
        r1, c1 = TronProblem.move((r0, c0), action)

        if state.board[r1][c1] == S:
            # player chose to move into an empty space.
            # fill new space with player symbol
            board[r1][c1] = str(state.ptm + 1)
            player_locs[state.ptm] = (r1, c1)
            return TronState(board, player_locs, next_ptm)
            
        elif state.board[r1][c1] == P:
            #player chose to move into a powerup space.
            #fill new space with player symbol and update 
            board[r1][c1] = str(state.ptm + 1)
            player_locs[state.ptm] = (r1, c1)
            #place barriers in front of next player
            board = TronProblem._add_barriers(board, player_locs[next_ptm])
            return TronState(board, player_locs, next_ptm)

        else:
            # player chose to move into an occupied space.
            player_locs[state.ptm] = None
            return TronState(board, player_locs, next_ptm)

    def is_terminal_state(self, state):
        num_players_left = 0
        for pl in state.player_locs:
            if not(pl == None):
                num_players_left += 1

        return num_players_left == 1

    def evaluate_state(self, state):
        """
        Note that, since players take turns sequentially,
        ties are impossible.
        """
        assert self.is_terminal_state(state)

        values = [0.0 if pl == None else 1 for pl in state.player_locs]
        return values

    ###### STATIC METHODS FOR IMPLEMENTING METHODS ABOVE ######

    @staticmethod
    def _add_barriers(board,loc):
        rows = len(board)
        cols = len(board[0])
        r, c = loc
        valid = []
        
        for i in range(-2,3):
            for j in range(-2,3):
                if r+i >= 0 and r+i < rows:
                    if c + j >= 0 and c+j < cols:
                        if board[r+i][c+j] == S:
                            if abs(i) == 2 or abs(j) == 2:
                                valid.append((r+i,c+j))
                                
        random.shuffle(valid)
        to_place = powerup_strength
        while to_place > 0 and valid:
            row, col = valid.pop()
            board[row][col] = B #place a barrier
            to_place -= 1
        
        return board
    

    @staticmethod
    def _board_from_board_file(board_file_loc):
        board_file = open(board_file_loc)
        board = []
        for line in board_file.readlines():
            row = [c for c in line if not(c == '\n')]
            board.append(row)
        return board

    @staticmethod
    def _player_locs_from_board(board):
        loc_dict = {}
        for r in range(len(board)):
            for c in range(len(board[r])):
                char = board[r][c]
                if TronProblem._is_int(char):
                    index = int(char) - 1
                    loc_dict[index] = (r, c)

        loc_list = []
        num_players = len(loc_dict)
        for index in range(num_players):
            loc_list.append(loc_dict[index])
        return loc_list


    @staticmethod
    def _is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def move(loc, direction):
        """
        Produces the location attained by going in the given direction
        from the given location.

        loc will be a (<row>, <column>) double, and direction will be
        U, L, D, or R.
        """ 
        r0, c0 = loc
        if direction == U:
            return (r0 - 1, c0)
        elif direction == D:
            return (r0 + 1, c0)
        elif direction == L:
            return (r0, c0 - 1)
        elif direction == R:
            return (r0, c0 + 1)
        else:
            raise ValueError('The input direction is not valid.')

    ###### HELPFUL FUNCTIONS FOR YOU ######

    @staticmethod
    def get_safe_actions(board, loc):
        """
        Given a game board and a location (<row>, <column>) on that board,
        returns the set of actions that don't result in immediate collisions.
        """
        safe = set()
        for action in {U, D, L, R}:
            r1, c1 = TronProblem.move(loc, action)
            if board[r1][c1] == S or board[r1][c1] == P:
                safe.add(action)
        return safe


    @staticmethod
    def board_to_pretty_string(board):
        s = ''
        for row in board:
            for cell in row:
                s += cell
            s += '\n'
        return s

    @staticmethod
    def visualize_state(state):
        print TronProblem.board_to_pretty_string(state.board)
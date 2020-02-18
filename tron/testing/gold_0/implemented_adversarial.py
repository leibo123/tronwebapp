from tronproblem import TronProblem

# Throughout this file, ASP means adversarial search problem.

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
    
    for action in TronProblem.get_safe_actions(state.board,state.player_locs[player]):
        next_state = asp.transition(state,action)
        value = abchelper(asp,next_state,cutoff_turn-1,a,b,False,eval_func,player)
        if value > best_value:
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
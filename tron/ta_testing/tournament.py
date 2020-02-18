import math
import random

__author__ = 'Steve James'


def calculate_pairings(players):
    """
    Produce the pairings for the next round, given the players' histories. Not taking into account first move advantage
    :param players: a list of tuples, with each tuple representing a player's ID, score and past opponents
    :return: the matchups
    """

    assert (len(players) % 2 == 0), "List of players must be even. Add a 'bye' player if necessary"

    # Swiss-style tournament. Not doing theoretically optimal backtracking, since worst-case is disastrous
    valid = False
    attempt = 0
    while not valid:
        valid = True
        shuffled = _shuffle(players)  # shuffle not in place. We shuffle so we don't get stuck

        if attempt > len(players) / 2:
            ordered = shuffled  # At this point, screw it!. Give up and find ANY valid pairing
        else:
            ordered = sorted(shuffled, key=lambda x: x[1], reverse=True)
        matchups = list()
        assigned = set()
        for i, player in enumerate(ordered):

            if player[0] not in assigned:
                opponent_id = _find_opponent(ordered[i + 1:], player[2], assigned)
                if opponent_id is None:
                    # fail. No solution :(
                    valid = False
                    attempt += 1
                    break

                assigned.add(player[0])
                assigned.add(opponent_id)
                matchups.append((player[0], opponent_id))

    assert len(assigned) == len(players)
    return matchups


def _shuffle(l):
    """
    Shuffle a list, but not in place!
    :param l: the list to shuffle
    :return: a new list that has been shuffled
    """
    s = l[:]
    random.shuffle(s)
    return s


def _find_opponent(candidates, history, assigned):
    """
    Find an opponent for the current player
    :param candidates: a list of all possible opponents
    :param history: a history of the player's past opponents
    :param assigned: a set containing players already assigned
    :return: an opponent, or None is no such opponent exists
    """
    for opponent in candidates:
        opponent_id = opponent[0]
        if opponent_id not in history and opponent_id not in assigned:
            return opponent_id
    return None


# playerId => (<rating before this round>, <ID of player matched against in this round>,
# <number of points {0, 0.5, or 1} earned in this round>)
def calculate_ratings(results):
    """
    Calculates the new Elo ratings of each player given the results of the previous round
    :param results: the results of a single tournament round.
    :return: a mapping from player ID's to their new Elo rating
    """
    return {player_id: _get_updated_elo(val[0], results[val[1]][0], val[2]) for player_id, val in list(results.items())}


def _get_updated_elo(elo, opponent_elo, result):
    """
    Calculate the new Elo rating for the current player, given his opponent and the result
    :param elo: the current Elo
    :param opponent_elo: the opponent's Elo
    :param result: 0, 0.5 or 1, for a loss, draw and win respectively
    :return: the current player's new Elo
    """
    # You should tweak the K factor depending on number of players, etc.
    # See https://en.wikipedia.org/wiki/Elo_rating_system
    K = 30
    qA = math.exp(elo / 400)
    qB = math.exp(opponent_elo / 400)
    eA = qA / (qA + qB)
    delta = K * (result - eA)
    return elo + delta


if __name__ == '__main__':

    # test with a mock tournament

    n_players = 200
    n_rounds = 9
    history = [['player' + str(i), 0, list()] for i in range(n_players)]
    elos = {'player' + str(i): 1600 for i in list(range(n_players))}

    for round in range(n_rounds):
        print(("\n***********************************************************\nRound " + str(round) + "\n"))
        pairings = calculate_pairings(history)
        results = dict()
        for pair in pairings:
            print((pair[0] + " vs " + pair[1]))
            outcome_a = random.choice([0, 0.5, 1])
            outcome_b = abs(1 - outcome_a)
            print((str(outcome_a) + " - " + str(outcome_b)))
            results[pair[0]] = (elos[pair[0]], pair[1], outcome_a)
            results[pair[1]] = (elos[pair[1]], pair[0], outcome_b)

        for player in history:
            player[1] += results[player[0]][2]
            player[2].append(results[player[0]][1])

        new_elos = calculate_ratings(results)
        print("New ratings:")
        print(new_elos)
        elos = new_elos
    print("Final Standings:\n\nName\t\tScore\tElo\n\n")
    rankings = sorted(history, key=lambda x: (-x[1], -elos[x[0]]))
    for player in rankings:
        print((player[0] + ("\t" if len(player[0]) <= 7 else "") + "\t{0:.1f}".format(player[1]) +
              "\t{0:.6f}".format(elos[player[0]])))
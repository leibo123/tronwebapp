import math
import random
import os, sys, re, copy
import support
import types
import html
import traceback
from glob import glob
from importlib.machinery import SourceFileLoader
from datetime import datetime
from itertools import combinations
from tronproblem import TronProblem
from tournament_gamerunner import run_game, clean_error

__author__ = "Steve James"
GRADING_DIR = "/course/cs1410/grading/TronTournament/"


def calculate_pairings(players):
    """
    Produce the pairings for all rounds.
    """

    print("Calculating pairings for {0} players".format(len(players)))
    assert (
        len(players) % 2 == 0
    ), "List of players must be even. Add a 'bye' player if necessary"

    combos = list(combinations(players, 2))
    random.shuffle(combos)
    return combos


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


def determine_outcome(
    bot_1, bot_2, game_name, num_games=10, path="maps/empty_room.txt"
):
    botlist = [bot_1, bot_2]
    wins = 0
    # vis_game = random.randrange(num_games)
    vis_game = -1
    for n in range(num_games):
        game = TronProblem(path, 0 if n < num_games / 2 else 1)
        if n == vis_game:
            outcome, metadata = run_game(game, botlist, game_name)
        else:
            outcome, metadata = run_game(game, botlist, game_name, visualizer=None)
        winner = outcome.index(1)
        if winner == 0:
            wins += 1
        for bot in botlist:
            bot.cleanup()
    if wins > 6:
        return 1.0, metadata
    elif wins > 3:
        return 0.5, metadata
    else:
        return 0.0, metadata


def load_dynamic(path):
    path = os.path.abspath(path)
    loader = SourceFileLoader("", path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod


def get_all_bots():
    # reads in all student's bots and maps names to bot functions
    # should add a TAbot if necessary to make numbers even
    all_bots = {}
    student_names = {}
    cwd = os.getcwd()
    SL = student_list()
    sys.path.insert(0, os.path.join(GRADING_DIR, "submit-0"))
    for student in SL:
        login = student.split("/")[-1]
        sys.path.insert(0, GRADING_DIR + "submit-0/{0}".format(login))
        old_cwd = os.getcwd()
        os.chdir(student)
        try:
            bots = load_dynamic(student + "/bots.py")

            student_bot = bots.StudentBot()
            name = student_bot.BOT_NAME if hasattr(student_bot, "BOT_NAME") else login
            all_bots[name] = student_bot
            student_names[name] = login
        except Exception:
            print("Error loading bot {0}".format(student))
            error_text = "\n".join(clean_error(traceback.format_exc()))
            with open(
                GRADING_DIR + "submit-0-autoreports/{0}.txt".format(login), "w"
            ) as out:
                out.write("There was an error loading your bot:\n" + error_text)
        os.chdir(old_cwd)

    if len(all_bots) % 2 is not 0:
        import greedy_bot

        GB = greedy_bot.GreedyBot()
        name = "GreedyBot"
        all_bots[name] = GB
        student_names[name] = "TAs"

    return all_bots, student_names


def create_modules():
    SL = student_list()
    os.chdir(GRADING_DIR + "submit-0")
    for student in SL:
        login = student.split("/")[-1]
        f = open(login + "/__init__.py", "w")
        f.close()


def student_list():
    students = glob(GRADING_DIR + "submit-0/*")
    valid = []
    for student in students:
        f = open(student + "/bots.py")
        text = f.read()
        if re.search("StudentBot", text):
            valid.append(student)

    return valid


def run_tournament():
    # test with a mock tournament

    all_bots, student_names = get_all_bots()
    n_rounds = len(all_bots) - 1
    scores = {name: 0 for name in all_bots.keys()}
    elos = {name: 1600 for name in all_bots.keys()}
    metadata = {
        name: {"decisions": 0, "errors": 0, "timeouts": 0, "error_message": ""}
        for name in all_bots.keys()
    }

    pairings = calculate_pairings(all_bots.keys())
    for i, pair in enumerate(pairings):
        print("Round {0} of {1}: {2} vs {3}".format(i, len(pairings), pair[0], pair[1]))
        bot_1 = all_bots[pair[0]]
        bot_2 = all_bots[pair[1]]
        game_name = "game_%s_vs_%s.txt" % (pair[0], pair[1])
        outcome_a, game_metadata = determine_outcome(bot_1, bot_2, game_name)
        # outcome_a, game_metadata = (1, [[0, 0, 0, ""]] * 2)
        outcome_b = 1 - outcome_a
        print(str(outcome_a) + " - " + str(outcome_b))
        elos[pair[0]] = _get_updated_elo(elos[pair[0]], elos[pair[1]], outcome_a)
        elos[pair[1]] = _get_updated_elo(elos[pair[1]], elos[pair[0]], outcome_b)
        scores[pair[0]] += outcome_a
        scores[pair[1]] += outcome_b

        for i in range(2):
            metadata[pair[i]]["decisions"] += game_metadata[i][0]
            metadata[pair[i]]["errors"] += game_metadata[i][1]
            metadata[pair[i]]["timeouts"] += game_metadata[i][2]
            if metadata[pair[i]]["errors"] > 0:
                metadata[pair[i]]["error_message"] = game_metadata[i][3]

    print("Final Standings:\n\nName\t\tScore\tElo\n\n")
    rankings = sorted(all_bots.keys(), key=lambda x: (-scores[x], -elos[x]))
    html_results = "<html><head></head><body><table><tr><th>Player</th><th>Score</th><th>ELO</th></tr>"
    for player in rankings:
        html_results += "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(
            html.escape(player), scores[player], elos[player]
        )
        print(
            player
            + ("\t" if len(player) <= 7 else "")
            + "\t{0:.1f}".format(scores[player])
            + "\t{0:.6f}".format(elos[player])
        )
    html_results += "</table>Published on {0}</body></html>".format(
        datetime.today().strftime("%b %d at %I:%M %p")
    )

    out_path = (
        "/course/cs1410/web/tron_results.html"
        if GRADING_DIR == "/course/cs1410/grading/TronTournament/"
        else GRADING_DIR + "tron_results.html"
    )
    with open(out_path, "w") as out:
        out.write(html_results)

    for name, data in metadata.items():
        decisions = data["decisions"]
        if decisions == 0:
            continue
        if data["timeouts"] / decisions > 0.1:
            with open(
                GRADING_DIR
                + "submit-0-autoreports/{0}.txt".format(student_names[name]),
                "w",
            ) as out:
                out.write(
                    "{0}% of decisions timed out.\n".format(
                        data["timeouts"] / decisions * 100
                    )
                )
        elif data["errors"] / decisions > 0.1:
            with open(
                GRADING_DIR
                + "submit-0-autoreports/{0}.txt".format(student_names[name]),
                "w",
            ) as out:
                out.write(
                    "{0}% of decisions threw an error.\nHere is one arbitrarily chosen error:\n{1}".format(
                        data["errors"] / decisions * 100, data["error_message"]
                    )
                )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        GRADING_DIR = "/course/cs1410/grading/{0}/".format(sys.argv[1])
    run_tournament()

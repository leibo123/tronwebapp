# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 13:35:56 2017

@author: Frisch
"""
from implemented_bots import *
from gamerunner_sol import *

###################
#     Helpers     #
###################


def calculate_grade(score):
    return score * 10
    # return min(max(int(score * 20 - 6), 0), 10)


def run_pairing(game, bots):
    outcome = run_game(game, bots)
    winner = outcome.index(1)
    for bot in bots:
        bot.cleanup()
    return winner


def test_bot(student_bot, ta_bot, num_games=10, map_name="empty_room"):
    student = student_bot()  # instantiate each bot only once, then clean
    path = "/course/cs1410/projects/tron/grader/grading_maps/" + map_name + ".txt"
    bots = [student, ta_bot]
    wins = 0
    for j in range(num_games):
        if j % 2 == 0:
            game = TronProblem(path, 0)
            if run_pairing(game, bots) == 0:
                wins += 1
        else:
            game = TronProblem(path, 0)
            if run_pairing(game, bots[::-1]) == 1:
                wins += 1
    return wins / float(num_games)


######################
#     Random bot     #
######################


def rand_divider(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=RandBot(), map_name="divider")
    return calculate_grade(win_rate)


def rand_hunger_games(student_bot):
    win_rate = test_bot(
        student_bot=student_bot, ta_bot=RandBot(), map_name="hunger_games"
    )
    return calculate_grade(win_rate)


def rand_joust(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=RandBot(), map_name="joust")
    return calculate_grade(win_rate)


def rand_withheld(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=RandBot(), map_name="toronto")
    return calculate_grade(win_rate)


###################
#     Wall bot    #
###################


def wall_divider(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=WallBot(), map_name="divider")
    return calculate_grade(win_rate)


def wall_hunger_games(student_bot):
    win_rate = test_bot(
        student_bot=student_bot, ta_bot=WallBot(), map_name="hunger_games"
    )
    return calculate_grade(win_rate)


def wall_joust(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=WallBot(), map_name="joust")
    return calculate_grade(win_rate)


def wall_withheld(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=WallBot(), map_name="toronto")
    return calculate_grade(win_rate)


###################
#     TA1 bot     #
###################


def TA1_divider(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot1(), map_name="divider")
    return calculate_grade(win_rate)


def TA1_hunger_games(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot1(), map_name="hunger_games")
    return calculate_grade(win_rate)


def TA1_joust(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot1(), map_name="joust")
    return calculate_grade(win_rate)


def TA1_withheld(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot1(), map_name="toronto")
    return calculate_grade(win_rate)


###################
#     TA2 bot     #
###################


def TA2_divider(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot2(), map_name="divider")
    return calculate_grade(win_rate)


def TA2_hunger_games(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot2(), map_name="hunger_games")
    return calculate_grade(win_rate)


def TA2_joust(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot2(), map_name="joust")
    return calculate_grade(win_rate)


def TA2_withheld(student_bot):
    win_rate = test_bot(student_bot=student_bot, ta_bot=TABot2(), map_name="toronto")
    return calculate_grade(win_rate)

def has_capstone(submission):
    return hasattr(submission, "CapstoneBot")

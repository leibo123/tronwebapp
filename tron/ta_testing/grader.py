# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 13:35:56 2017

@author: Frisch
"""
from implemented_bots import *
from gamerunner import *
from collections import defaultdict

def test_bot(stu, num_games = 100):
    maplist = ['empty_room','toronto3','joust','divider']
    botlist = [RandBot(),WallBot(),TABot1(),TABot2()]
    botnames = ['random','wall','TA1','TA2']
    scores = {}
    student = stu() #instantiate each bot only once, then clean
    for mapname in maplist:
        print(mapname)
        path = 'grading_maps/' + mapname + '.txt'
        game = TronProblem(path,0,False)
        wincounts = {}
        for i, opp in enumerate(botlist):
            print(botnames[i])
            bots = [student,opp]
            wins = 0
            for j in range(num_games):
                outcome = run_game(copy.deepcopy(game),bots,None)
                winner = outcome.index(1)
                if winner == 0:
                    wins += 1
                for bot in bots:
                    bot.cleanup()
            wincounts[botnames[i]] = wins
        scores[mapname] = wincounts
    return scores
    
print(test_bot(gfong1))
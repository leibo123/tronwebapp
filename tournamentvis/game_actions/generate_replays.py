import json
from datetime import datetime
import glob
import unicodedata
import htmlmin

masterlistpath = "../tron_replays/all_games.html"

def findnth(string, substring, n):
    parts = string.split(substring, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(string) - len(parts[-1]) - len(substring)

def boardToHTML(board):
    unicodedata.normalize('NFKD', board).encode('ascii','ignore')

    b = "<div class='board-wrapper'><div class='board'>"
    start = False
    for char in board:
        if char == "#" and not start:
            start = True
        if not start:
            continue

        if char == " ":
            b += "<span class='space'></span>"
        if char == "#":
            b += "<span class='wall'></span>"
        if char == "x":
            b += "<span class='barrier'></span>"
        if char == "1":
            b += "<span class='player1'><p>1</p></span>"
        if char == "2":
            b += "<span class='player2'><p>2</p></span>"
        if char == "*":
            b += "<span class='trap'><p>*</p></span>"
        if char == "@":
            b += "<span class='armor'><p>@</p></span>"
        if char == "^":
            b += "<span class='speed'><p>^</p></span>"
        if char == "!":
            b += "<span class='bomb'><p>!</p></span>"

    b += "</div></div>"
    return b

header = '<!doctype html><html><head><title>CS1410 &middot; TRON Replays</title><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"><meta http-equiv="x-ua-compatible" content="ie=edge"><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous"><link rel="stylesheet" href="./results.css"></head>'
bodyEnd = '</main></body><script src="tron_replays.js"></script></html>'
index = 0
games_dict = {}

for filename in glob.glob('*.txt'):
    displayname = filename.replace("%3A", ":")
    tronResults = ""
    p1_ind = findnth(displayname, '_', 3)
    p2_ind = findnth(displayname, '_', 4)
    bucket_ind = findnth(displayname, '_', 5)
    p1 = displayname[p1_ind + 1:p2_ind]
    p2 = displayname[p2_ind + 1:bucket_ind]
    player1 = "<span class='p1'>" + p1 + "</span>"
    player2 = "<span class='p2'>" + p2 + "</span>"
    bucket = displayname[bucket_ind + 1:-4]
    roundstr = filename[:p1_ind].replace("_", " ")
    out_path = "../tron_replays/" + filename.replace("%3A", "%253A")[:-4] + ".html" # handle colon escape sequence

    with open(filename, encoding='utf-8') as f:
        print("opening", filename, "for reading.")
        data = json.load(f)
        p1wincount = 0
        p2wincount = 0
        boardIndex = 0
        for d1, d2 in data:
            tronResults += "<div class='game-wrapper'>"
            tronResults += "<div class='game'>"
            firstturn = True
            flip = False
            for d3, d4 in zip(d1, d2):
                if firstturn:
                    if "x" in d3:
                        flip = True
                    firstturn = False
                if flip:
                    tronResults += boardToHTML(d4)
                    tronResults += boardToHTML(d3)
                else:
                    tronResults += boardToHTML(d3)
                    tronResults += boardToHTML(d4)
            if len(d1) > len(d2):
                tronResults += boardToHTML(d1[len(d1) - 1])
            elif len(d2) > len(d1):
                tronResults += boardToHTML(d2[len(d2) - 1])
            tronResults += "</div><button class='restart' title='Click to restart' onclick='restart(" + str(boardIndex) + ")'>R</button>"
            if len(d1) == len(d2):
                if flip:
                    tronResults += "<p>Winner: Player 2 (" + player2 + ")</p>"
                    p2wincount += 1
                else:
                    tronResults += "<p>Winner: Player 1 (" + player1 + ")</p>"
                    p1wincount += 1 
            else:
                if flip:
                    tronResults += "<p>Winner: Player 1 (" + player1 + ")</p>"
                    p1wincount += 1
                else:
                    tronResults += "<p>Winner: Player 2 (" + player2 + ")</p>"
                    p2wincount += 1
            tronResults += "</div>"
            boardIndex += 1

    bodyStart = '<body><header class="default-header"><a href="' + masterlistpath + '"><h1>TRON-41 Replays</h1></a><p class="bucket">Bucket ' + bucket + ", " + roundstr + "</p><p class='vs'>" + player1 + " v. " + player2 + '</p><p class="score"><span class="p1">' + str(p1wincount) + '</span> : <span class="p2">' + str(p2wincount) + '</span></p><img id="loading" src="https://media0.giphy.com/media/r09BeWEk9JZL2/source.gif"></header><main class="container">'
    html_results = header + bodyStart + tronResults + bodyEnd
    game_str = '<p class="bucket"><a href="' + out_path + '">Bucket ' + bucket + ", " + roundstr + ": " + player1 + " v. " + player2 + ' (<span class="p1">' + str(p1wincount) + '</span> - <span class="p2">' + str(p2wincount) + '</span>)</a></p>'
    games_dict[bucket] = games_dict.get(bucket, []) + [game_str]
    with open(out_path, "w", encoding='utf-8') as out:
        # out.write(htmlmin.minify(html_results, remove_empty_space=True))
        out.write(html_results) # faster but not minified
"""
Begin logic for printing out the list of all matches
"""
htmlBody = '<input type="text" id="myInput" onkeyup="searchNames()" placeholder="Search for names.."><ul id="myUL">'
for i in ['0', '1', '2', '3']:
    games = games_dict[i]
    for gamestr in games:
        htmlBody += '<li>' + gamestr + '</li>'
htmlBody += "</ul>"
bodyStart = '<body><header class="default-header"><a href="' + masterlistpath + '"><h1>TRON-41 Replays</h1></a>'
bodyEnd = '</main></body><script src="tron_replays.js"></script></html>'
html_results = header + bodyStart + htmlBody + bodyEnd
with open(masterlistpath, "w", encoding='utf-8') as out:
    out.write(html_results)
    print("list of all games written to", masterlistpath)





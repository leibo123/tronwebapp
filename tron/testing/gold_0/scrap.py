            # uploc = (myloc[0], myloc[1] + 1)
            # downloc = (myloc[0], myloc[1] - 1)
            # leftloc = (myloc[0] - 1, myloc[1])
            # rightloc = (myloc[0] + 1, myloc[1])
            # up = floodboard[uploc] if myloc[1] < 15 else None
            # down = floodboard[downloc] if myloc[1] > 0 else None
            # left = floodboard[leftloc] if myloc[0] > 0 else None
            # right = floodboard[] if myloc[0] < 15 else None
            # if up is not None and up == ' ':
            #     floodboard[(mycur[0], mycur[1] + 1)] = 'M' #M for me
            #     myvisited.add((mycur[0], mycur[1] + 1))
            #     Q.put(up)
            # if down is not None and down == ' ':
            #     floodboard[(mycur[0], mycur[1] - 1)] = 'M'
            #     Q.put(down)
            # if left is not None and left == ' ':
            #     floodboard[(mycur[0] - 1, mycur[1])] == 'M'
            #     Q.put(left)
            # if right is not None and right == ' ':
            #     floodboard[(mycur[0] + 1, mycur[1])] == 'M'
            #     Q.put(right)

TA
      EMPTY
      P1: 94% win-rate
      P2: 89% win-rate

      DIVIDER
      P1: 91% win-rate
      P2: 30% win-rate

      JOUST
      P1: 95% win-rate
      P2: 74% win-rate

WALL
      EMPTY
      P1: 97% win-rate
      P2: 99% win-rate

      DIVIDER
      P1: 85% win-rate
      P2: 74% win-rate

      JOUST
      P1: 90% win-rate
      P2: 88% win-rate

RANDOM
      EMPTY
      P1: 96% win-rate
      P2: 96% win-rate

      DIVIDER
      P1: 83% win-rate
      P2: 80% win-rate

      JOUST
      P1: 94% win-rate
      P2: 94% win-rate
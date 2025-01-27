import numpy as np
import sys
import time
from pynput import keyboard
import copy
from PIL import Image

N = 0
T0 = 0

# FEATURE FLAGS
PREPROCESSING_1A = True
PREPROCESSING_1B = True
PREPROCESSING_2 = True
PREPROCESSING_3 = True
PREPROCESSING_4 = True

def T(arr):
    return list(zip(*arr))

def checkBoardAgainstRef(board, refFile):
    im = Image.open(refFile)
    pix = im.load()

    for i in range(N):
        for j in range(N):
            if ~board[i][j] & 0b10:
                pass
            elif pix[i, j] == 0 and ~board[i][j] & 0b1:
                pass
            elif pix[i, j] == 255 and board[i][j] & 0b1:
                pass
            else:
                print("ERROR", i, j)

def prettyPrintBoard(board, rows=None, cols=None, jump=True):
    if jump:
        print("\033[%d;%dH" % (0, 0))

    for i, row in enumerate(T(board)):
        for item in row:
            if (~item & 0b10):
                print("?", end='')
            elif (~item & 0b1):
                print("x", end='')
            else:
                print("█", end='')
        
        print(' ', end='')
        if rows is not None:
            print(rows[i], end='')
        print(' ' * 19)

    if cols is not None:
        for i in range(max(map(len, cols))):
            for j, col in enumerate(cols):
                try:
                    if i == len(col) - 1:
                        raise IndexError  # (lol)
                    print(str(col[i])[0], end='')
                except IndexError:
                    print(' ', end='')
            print()
            for j, col in enumerate(cols):
                try:
                    if i == len(col) - 1:
                        raise IndexError  # (lol)
                    print(str(col[i])[1], end='')
                except IndexError:
                    print(' ', end='')
            
            print()
            print()

def rowColParse(inputStr):
    output = []
    for rowCol in inputStr.split(","):
        rowColData = []
        for num in rowCol.split(" "):
            rowColData.append(int(num))

        rowColData.append(0)

        output.append(rowColData)

    return output

def isFullyValid(board, rows, cols):
    """
    LOGIC:
    for each square:
        if -1:
            ensure correct length (<=) of previous box, break
        if 1, add to count
        if 0 and count != 0:
            ensure correct length of previous box, remove current box.
    """

    for boardRow, ruleRow in zip(T(board), rows):
        ruleCounter = 0
        current = 0
        brokenOut = False
        for item in boardRow:
            if (~item & 0b10):
                if current != 0:
                    if current <= ruleRow[ruleCounter]:
                        brokenOut = True
                        break
                    else:
                        return False
                else:
                    brokenOut = True
                    break
            elif (item & 0b1):
                current += 1
            else:
                if current != 0:
                    if current == ruleRow[ruleCounter]:
                        ruleCounter += 1
                    else:
                        return False
                
                    current = 0

        # end of row
        if current != 0 and not brokenOut:
            if current != ruleRow[ruleCounter]:
                return False


    for boardRow, ruleRow in zip(board, cols):  # cba to rename all row -> col lol
        ruleCounter = 0
        current = 0
        brokenOut = False
        for item in boardRow:
            if (~item & 0b10):
                if current != 0:
                    if current <= ruleRow[ruleCounter]:
                        brokenOut = True
                        break
                    else:
                        return False
                else:
                    brokenOut = True
                    break
            elif (item & 0b1):
                current += 1
            else:
                if current != 0:
                    if current == ruleRow[ruleCounter]:
                        ruleCounter += 1
                    else:
                        return False
                
                    current = 0

        # end of row
        if current != 0 and not brokenOut:
            if current != ruleRow[ruleCounter]:
                return False

    return True

def isValid(board, rows, cols, row, col, rowRange=1):
    """
    LOGIC:
    for each square:
        if -1:
            ensure correct length (<=) of previous box, break
        if 1, add to count
        if 0 and count != 0:
            ensure correct length of previous box, remove current box.
    """

    # boardRow = T(board)[col] T is slow!!!
    ruleRow = rows[col]

    ruleCounter = 0
    current = 0
    brokenOut = False
    for i in range(len(board)):
        item = board[i][col]
        if (~item & 0b10):
            if current != 0:
                if current <= ruleRow[ruleCounter]:
                    brokenOut = True
                    break
                else:
                    return False
            else:
                brokenOut = True
                break
        elif (item & 0b1):
            current += 1
        else:
            if current != 0:
                if current == ruleRow[ruleCounter]:
                    ruleCounter += 1
                else:
                    return False
            
                current = 0

    # end of row
    if current != 0 and not brokenOut:
        if current != ruleRow[ruleCounter]:
            return False

    for i in range(row, row + rowRange):
        boardRow = board[i]
        ruleRow = cols[i]

        ruleCounter = 0
        current = 0
        brokenOut = False
        for item in boardRow:
            if (~item & 0b10):
                if current != 0:
                    if current <= ruleRow[ruleCounter]:
                        brokenOut = True
                        break
                    else:
                        return False
                else:
                    brokenOut = True
                    break
            elif (item & 0b1):
                current += 1
            else:
                if current != 0:
                    if current == ruleRow[ruleCounter]:
                        ruleCounter += 1
                    else:
                        return False
                
                    current = 0

        # end of row
        if current != 0 and not brokenOut:
            if current != ruleRow[ruleCounter]:
                return False

    return True

def preprocessing(board, rows, cols):

    if PREPROCESSING_1A:
        # any that are definitely correct should be entered
        for i in range(len(rows)):
            rowRule = rows[i]
            totalDist = sum(rowRule) + len(rowRule) - 2
            if totalDist == N:
                pos = 0
                for item in rowRule[:-1]:
                    for _ in range(item):
                        board[pos][i] = 0b111
                        pos += 1

                    try:
                        board[pos][i] = 0b110
                        pos += 1
                    except IndexError:
                        break  # should already break, just for safety (and silent crashing D:)
            elif totalDist <= 0:
                for j in range(N):
                    board[j][i] = 0b110
            else:

                # TODO: sadly this can be much better
                # b0 overlap
                b0posA = rowRule[0] - 1
                b0posB = N - (sum(rowRule) + len(rowRule) - 2)
                if b0posB < b0posA:
                    for j in range(b0posB, b0posA + 1):
                        board[j][i] = 0b111
                
                #bn-1 overlap
                bnm1posA = N - rowRule[-2]
                bnm1posB = sum(rowRule) + len(rowRule) - 3
                if bnm1posA < bnm1posB:
                    for j in range(bnm1posA, bnm1posB + 1):
                        board[j][i] = 0b111

    if PREPROCESSING_1B:
        for i in range(len(cols)):
            rowRule = cols[i]
            totalDist = sum(rowRule) + len(rowRule) - 2
            if totalDist == N:
                pos = 0
                for item in rowRule[:-1]:
                    for _ in range(item):
                        board[i][pos] = 0b111
                        pos += 1

                    try:
                        board[i][pos] = 0b110
                        pos += 1
                    except IndexError:
                        break  # should already break, just for safety (and silent crashing D:)
            elif totalDist <= 0:
                for j in range(N):
                    board[i][j] = 0b110
            else:
                # b0 overlap
                b0posA = rowRule[0] - 1
                b0posB = N - (sum(rowRule) + len(rowRule) - 2)
                if b0posB < b0posA:
                    for j in range(b0posB, b0posA + 1):
                        board[i][j] = 0b111
                
                #bn-1 overlap
                bnm1posA = N - rowRule[-2]
                bnm1posB = sum(rowRule) + len(rowRule) - 3
                if bnm1posA < bnm1posB:
                    for j in range(bnm1posA, bnm1posB + 1):
                        board[i][j] = 0b111

    if PREPROCESSING_2:
        for i in range(len(rows)):  # we go agane
            rowRule = rows[i]
            totalDist = sum(rowRule) + len(rowRule) - 2
            if 0 < totalDist < N:
                # b0
                rule = rowRule[0]

                b0 = -1
                p0 = -1
                start = True
                for j in range(rule):
                    if board[j][i] == 0b111 and start:
                        start = False
                        p0 = j
                    elif board[j][i] == 0b110 and start:
                        b0 = j

                if p0 != -1:
                    for j in range(p0, rule + b0 + 1):  # eek
                        board[j][i] = 0b111

                    if p0 == 0:
                        board[rule + b0 + 1][i] = 0b110
                    
                # bn-1
                rule = rowRule[-2]

                bnm1 = -1
                pnm1 = -1
                start = True
                for j in range(N - 1, N - rule - 1, -1):
                    if board[j][i] == 0b111 and start:
                        start = False
                        pnm1 = j
                    elif board[j][i] == 0b110 and start:
                        bnm1 = j
                
                if pnm1 != -1:
                    if bnm1 == -1:
                        bnm1 = N
                    for j in range(pnm1, bnm1 - rule - 1, -1):
                        board[j][i] = 0b111

                    if pnm1 == N - 1:
                        board[bnm1 - rule - 1][i] = 0b110

        for i in range(len(cols)):  # we go agane
            rowRule = cols[i]
            totalDist = sum(rowRule) + len(rowRule) - 2
            if 0 < totalDist < N:
                # b0
                rule = rowRule[0]

                b0 = -1
                p0 = -1
                start = True
                for j in range(rule):
                    if board[i][j] == 0b111 and start:
                        start = False
                        p0 = j
                    elif board[i][j] == 0b110 and start:
                        b0 = j

                if p0 != -1:
                    for j in range(p0, rule + b0 + 1):  # eek
                        board[i][j] = 0b111
                    
                    if p0 == 0:
                        board[i][rule + b0 + 1] = 0b110

                # bn-1
                rule = rowRule[-2]

                bnm1 = -1
                pnm1 = -1
                start = True
                for j in range(N - 1, N - rule - 1, -1):
                    if board[i][j] == 0b111 and start:
                        start = False
                        pnm1 = j
                    elif board[i][j] == 0b110 and start:
                        bnm1 = j
                
                if pnm1 != -1:
                    if bnm1 == -1:
                        bnm1 = N
                    for j in range(pnm1, bnm1 - rule - 1, -1):
                        board[i][j] = 0b111

                    if pnm1 == N - 1:
                        board[i][bnm1 - rule - 1] = 0b110
    
    if PREPROCESSING_3:  # search for 'accidentally' fully correct blocks
        for i in range(len(rows)):
            rowRule = rows[i]
            rc = 0
            current = 0
            failed = False

            for j in range(N):
                item = board[j][i]
                if item & 0b1:
                    current += 1
                else:
                    if current != 0:
                        if current == rowRule[rc]:
                            rc += 1
                            current = 0
                        else:
                            failed = True
                            break
            if current != 0:
                if current == rowRule[rc]:
                    rc += 1
                    current = 0
                else:
                    failed = True
                    break
                        
            if not failed and rc == len(rowRule) - 1:
                if (current == 0 or current == rowRule[rc]) and rc == len(rowRule) - 2:
                    for j in range(N):
                        if ~board[j][i] & 0b10:
                            board[j][i] = 0b110
        
        for i in range(len(cols)):
            rowRule = cols[i]
            rc = 0
            current = 0
            failed = False

            for j in range(N):
                item = board[i][j]
                if item & 0b1:
                    current += 1
                else:
                    if current != 0:
                        if current == rowRule[rc]:
                            rc += 1
                            current = 0
                        else:
                            failed = True
                            break
                    
            if current != 0:
                if current == rowRule[rc]:
                    rc += 1
                    current = 0
                else:
                    failed = True
                    break
                        
            if not failed and rc == len(rowRule) - 1:
                if (current == 0 or current == rowRule[rc]) and rc == len(rowRule) - 2:
                    for j in range(N):
                        if ~board[i][j] & 0b10:
                            board[i][j] = 0b110
                
    if PREPROCESSING_4:  # move from x to x looking for block size. If block too small fill with x's, else keep track
        for i in range(len(rows)):
            rowRule = rows[i]
            current = 0
            blocks = [[0, 0, 0]]  # blocks[2]: -1 init, else sum of 0b111 in block

            for j in range(N):
                item = board[j][i]
                if item & 0b1:
                    current += 1
                    blocks[-1][2] += 1
                elif ~item &0b10:
                    current += 1
                else:
                    if current != 0:
                        blocks[-1][1] = j  # exclusive on top
                        blocks.append([j + 1, j + 1, 0])  # inclusive on bottom
                        current = 0
                    else:
                        blocks[-1] = [j + 1, j + 1, 0]
            
            if current != 0:
                blocks[-1][1] = N

            rc = 0
            for block in blocks:
                if block[1] - block[0] == rowRule[rc] and block[2] == rowRule[rc]:
                    rc += 1
                elif block[1] - block[0] == rowRule[rc] and block[2] < rowRule[rc] and block[2] > 0:
                    rc += 1
                    for j in range(block[0], block[1]):
                        board[j][i] = 0b111
                    
                    # print("FILLED", rowRule, block[0], block[1])
                # elif block[2] == rowRule[rc]:  # fill any unfilled squares with blanks
                #     rc += 1
                #     for j in range(block[0], block[1]):
                #         board[j][i] |= 0b110
                    
                    # print("EMPTIED", rowRule, block[0], block[1])

                else:
                    if block[1] - block[0] < rowRule[rc]:
                        if block[2] > 0:
                            print(block, rowRule)
                            print("OOPS")
                            quit()
                        
                        for j in range(block[0], block[1]):
                            board[j][i] = 0b110
                    else:
                        break  # can't tell what goes in this block without more logic
        
            # (occasionally) very important edge case: longest non-full block can only fit one of the rules, in which case wham in as much as possible
            # note: damages blocks!
            tempRowRule = copy.deepcopy(rowRule)
            toRemove = []
            for block in blocks:
                if block[1] - block[0] == block[2]:
                    tempRowRule.remove(block[2])
                    toRemove.append(block)
            
            for item in toRemove:
                blocks.remove(item)
            
            largestCanFitIn = []
            for block in blocks:
                if max(tempRowRule) <= block[1] - block[0]:
                    largestCanFitIn.append([block, max(tempRowRule)])
            
            if len(largestCanFitIn) == 1:
                pa = largestCanFitIn[0][0][0] + largestCanFitIn[0][1]
                pb = largestCanFitIn[0][0][1] - largestCanFitIn[0][1]

                for j in range(pb, pa):
                    board[j][i] = 0b111
            
        for i in range(len(cols)):
            rowRule = cols[i]
            current = 0
            blocks = [[0, 0, 0]]  # blocks[2]: -1 init, else sum of 0b111 in block

            for j in range(N):
                item = board[i][j]
                if item & 0b1:
                    current += 1
                    blocks[-1][2] += 1
                elif ~item &0b10:
                    current += 1
                else:
                    if current != 0:
                        blocks[-1][1] = j  # exclusive on top
                        blocks.append([j + 1, j + 1, 0])  # inclusive on bottom
                        current = 0
                    else:
                        blocks[-1] = [j + 1, j + 1, 0]
            
            if current != 0:
                blocks[-1][1] = N

            rc = 0
            for block in blocks:
                if block[1] - block[0] == rowRule[rc] and block[2] == rowRule[rc]:
                    rc += 1
                elif block[1] - block[0] == rowRule[rc] and block[2] < rowRule[rc] and block[2] > 0:
                    rc += 1
                    for j in range(block[0], block[1]):
                        board[i][j] = 0b111
                    
                    # print("FILLED", rowRule, block[0], block[1])
                # elif block[2] == rowRule[rc]:  # fill any unfilled squares with blanks - oof'd
                #     rc += 1
                #     for j in range(block[0], block[1]):
                #         board[i][j] |= 0b110
                    
                #     print("EMPTIED", rowRule, block[0], block[1])

                else:
                    if block[1] - block[0] < rowRule[rc]:
                        if block[2] > 0:
                            print(block, rowRule)
                            print("OOPS")
                            quit()
                        
                        for j in range(block[0], block[1]):
                            board[i][j] = 0b110
                    else:
                        break  # can't tell what goes in this block without more logic
            
            # (occasionally) very important edge case: longest non-full block can only fit one of the rules, in which case wham in as much as possible
            # note: damages blocks!
            # tempRowRule = copy.deepcopy(rowRule)
            # toRemove = []
            # for block in blocks:
            #     if block[1] - block[0] == block[2]:
            #         tempRowRule.remove(block[2])
            #         toRemove.append(block)
            
            # for item in toRemove:
            #     blocks.remove(item)
            
            # largestCanFitIn = []
            # for block in blocks:
            #     if max(tempRowRule) <= block[1] - block[0]:
            #         largestCanFitIn.append([block, max(tempRowRule)])
            
            # if len(largestCanFitIn) == 1:
            #     pa = largestCanFitIn[0][0][0] + largestCanFitIn[0][1]
            #     pb = largestCanFitIn[0][0][1] - largestCanFitIn[0][1]

            #     for j in range(pb, pa):
            #         board[i][j] = 0b111

    # if PREPROCESSING_3: # need more checks sadge, to fix
    #     for i in range(len(rows)):  # we go agane agane - searching for blocks that are closed on one end and open on the other
    #         rowRule = rows[i]
    #         # closed left
    #         p = 0
    #         rc = 0
    #         for j in range(N):
    #             if board[j][i] & 0b10 and ~board[j][i] & 0b1:
    #                 if p == 2:
    #                     rc += 1
    #                 p = 1
    #             elif board[j][i] & 0b11 == 0b11:
    #                 if p == 1:
    #                     p = 2
    #             elif board[j][i] == 0b0:
    #                 if p == 2:
    #                     print("RC:", rc, rowRule)

    #                     rc += 1
    #                     pass
    #                 else:
    #                     p = 0
                


    # quit()

def getRowRule(board, rows, col):
    # rowData = T(board)[col]
    rowRule = rows[col]
    rc = 0
    current = 0

    for i in range(len(board)):
        item = board[i][col]
        if ~item & 0b10:
            break
        elif item & 0b1:
            current += 1
        else:
            if current != 0:
                rc += 1
                current = 0

    return rowRule[rc], (current == 0) and (rc < len(rows[col]) - 1)

def recur(board, rows, cols, currentPos):
    """
    Init: new recur for every step
    
    Optimisations:
    [x] On failed recursion, return instead of currentPos - 1
    [x] Fill in row blocks that are guaranteed from t0 (80% improvement!)
    [x] Fill in row blocks as they're made (6 must be 6, not just 1, so can fill all 6 when attempting to put 1)
    [x] isValid only needs to check current row and col, all else are guaranteed correct

    TODO: more preprocessing can be done, use `py -m cProfile -s time .\main.py`
    """
    global N, T0

    # print(currentPos)
    prettyPrintBoard(board, rows)

    # while True:
    #     with keyboard.Events() as events:
    #         event = events.get(1e6)
    #         if type(event) is keyboard.Events.Release:
    #             break


    if currentPos == N**2:
        prettyPrintBoard(board)

        print(time.time() - T0)
        quit()

    row = currentPos % N
    col = currentPos // N

    # print(row, ' ' * 20)
    # print(col, ' ' * 20)

    if board[row][col] & 0b100:  # if its definitely correct then leave it alone, do it for a lot to save function calls
        while board[row][col] & 0b100:
            currentPos += 1
            row = currentPos % N
            col = currentPos // N

            if currentPos == N**2:
                prettyPrintBoard(board)

                print(time.time() - T0)
                quit()
        recur(board, rows, cols, currentPos)
        return

    # blocks:
    rowRule, doit = getRowRule(board, rows, col)
    
    addOn = 1
    
    if doit:
        for i in range(row, row + rowRule):
            try:
                if board[i][col] != 0b0:
                    doit = False
            except IndexError:
                doit = False
        
        try:
            if board[row + rowRule][col] != 0b0:
                doit = False
        except IndexError:
            addOn -= 1

    if doit:
        for i in range(row, row + rowRule):
            board[i][col] = 0b11
        
        try:
            board[row + rowRule][col] = 0b10
        except IndexError:
            pass
        
        addOn += rowRule
    else:
        board[row][col] = 0b11

    # recur:
    worked = isValid(board, rows, cols, row, col, addOn)
    # worked = isFullyValid(board, rows, cols)
    if worked:
        recur(board, rows, cols, currentPos + addOn)
    # else:
    #     doit = False
        
    # later...
    board[row][col] = 0b10
    if doit:
        # time.sleep(2)
        for i in range(row + 1, row + rowRule + 1):
            try:
                board[i][col] = 0b0
            except IndexError:
                pass

    worked = isValid(board, rows, cols, row, col, addOn)
    # worked = isFullyValid(board, rows, cols)
    if worked:
        recur(board, rows, cols, currentPos + 1)
    
    # later...
    board[row][col] = 0b00
    return


    
def solve():
    global T0, N

    """
    Board bits:
    high-2: constant (definitely correct) (1) / not constant (0)
    high-1: visited (1) / not visited (0)
    high: on (1) / off (0)
    """

    # board[0][0] = 1
    # board[1][0] = 1
    # board[2][0] = 1
    # board[3][0] = 1
    # board[4][0] = 1
    # board[5][0] = 1
    # board[6][0] = 0
    # board[7][0] = 0
    # board[8][0] = 1

    # board = [[1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]

    # rows = rowColParse("7,5,2 5 2,4 5 4,1 9 1,1 9 1,1 11 1,15,13,11,11,9,9,7,5")
    # cols = rowColParse("5,2 2,2 5,10,1 10,15,15,15,15,15,1 10,10,2 5,2 2,5")

    # rows = rowColParse("6,2 9,6 1 1 1,4 1 5,2 5,1 1 4,2 4 2 3,3 3 1 4,2 2 2 4,1 1 2 3,4 2 3 3,2 2 2 1 2,1 1 2 3 1,2 1 3 2 1,3 2 2 2 3,5 2 2 3,5 2 2 2,7 3 5,1 3 9,3 9")
    # cols = rowColParse("6,2 2 2,1 1 1,2 2 2 2,5 3 1,4 1 3 1,3 2 4 1,2 3 8,2 3 3,3 2 2,2 1 1 2,3 7,2 2 3 4,3 9 3,2 1 3 3 2,1 2 3 5,1 6 2 3,9 4 3,9 6,2 13")

    # rows = [[60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [16, 1, 20, 1, 18, 0], [14, 17, 15, 0], [13, 15, 14, 0], [11, 15, 12, 0], [10, 14, 12, 0], [8, 12, 11, 0], [6, 12, 11, 0], [6, 12, 4, 10, 0], [6, 1, 12, 5, 1, 10, 0], [5, 10, 6, 9, 0], [6, 1, 11, 6, 10, 0], [6, 1, 11, 8, 9, 0], [6, 4, 9, 7, 9, 0], [6, 5, 10, 8, 9, 0], [13, 10, 8, 8, 0], [12, 10, 1, 9, 9, 0], [13, 9, 8, 1, 8, 0], [12, 10, 9, 8, 0], [13, 10, 8, 9, 0], [12, 10, 10, 8, 0], [13, 9, 9, 8, 0], [12, 9, 9, 9, 0], [13, 10, 9, 8, 0], [12, 10, 9, 9, 0], [13, 9, 9, 1, 8, 0], [12, 10, 1, 9, 8, 0], [13, 9, 8, 9, 0], [12, 10, 8, 9, 0], [13, 10, 8, 9, 0], [12, 10, 8, 1, 9, 0], [13, 11, 7, 9, 0], [12, 9, 8, 10, 0], [13, 11, 6, 10, 0], [12, 11, 5, 10, 0], [13, 12, 4, 11, 0], [12, 12, 11, 0], [13, 11, 1, 12, 0], [12, 13, 12, 0], [13, 14, 13, 0], [12, 15, 14, 0], [13, 16, 16, 0], [38, 1, 1, 17, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0]]
    # cols = [[60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [20, 39, 0], [17, 35, 0], [17, 36, 0], [16, 36, 0], [16, 37, 0], [15, 37, 0], [14, 38, 0], [14, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 0], [13, 8, 0], [12, 8, 0], [12, 1, 8, 0], [11, 8, 0], [12, 8, 0], [11, 8, 0], [13, 2, 3, 2, 3, 4, 4, 4, 4, 12, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [31, 3, 24, 0], [23, 1, 17, 0], [20, 15, 0], [17, 12, 0], [16, 11, 0], [15, 1, 1, 10, 0], [14, 9, 0], [13, 1, 1, 1, 1, 8, 0], [12, 1, 17, 1, 8, 0], [12, 24, 8, 0], [12, 28, 7, 0], [11, 28, 8, 0], [12, 28, 7, 0], [11, 28, 8, 0], [12, 26, 7, 0], [12, 21, 8, 0], [12, 1, 1, 2, 2, 1, 9, 0], [13, 9, 0], [14, 1, 10, 0], [14, 1, 11, 0], [16, 13, 0], [18, 1, 1, 15, 0], [20, 1, 18, 0], [25, 1, 1, 1, 1, 23, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0]]

    rows = [[60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 0], [60, 0], [60, 0], [24, 1, 1, 1, 1, 1, 23, 0], [3, 8, 8, 1, 1, 1, 1, 7, 6, 4, 0], [7, 8, 2, 2, 2, 3, 6, 6, 0], [19, 1, 16, 0], [17, 1, 1, 16, 0], [10, 4, 1, 1, 1, 1, 3, 1, 14, 0], [5, 9, 6, 5, 1, 4, 6, 1, 0], [13, 1, 8, 8, 1, 6, 3, 0], [13, 10, 10, 11, 0], [8, 2, 1, 1, 9, 10, 1, 10, 0], [3, 8, 12, 1, 9, 10, 0], [11, 13, 13, 8, 0], [10, 1, 12, 14, 4, 4, 0], [8, 1, 14, 14, 7, 0], [6, 3, 15, 15, 8, 0], [4, 4, 15, 15, 6, 0], [8, 16, 16, 5, 1, 0], [9, 16, 16, 6, 0], [8, 17, 17, 6, 0], [7, 1, 17, 17, 1, 4, 0], [4, 3, 15, 15, 1, 6, 0], [7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 0], [8, 1, 6, 0], [7, 3, 1, 0], [8, 1, 4, 0], [3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 0], [8, 13, 3, 14, 2, 6, 0], [7, 1, 10, 6, 1, 15, 6, 0], [8, 16, 17, 6, 0], [8, 16, 16, 6, 0], [4, 4, 16, 16, 4, 2, 0], [8, 15, 14, 2, 4, 0], [10, 15, 15, 1, 6, 0], [9, 14, 14, 8, 0], [11, 14, 13, 1, 8, 0], [4, 5, 1, 13, 12, 1, 9, 0], [11, 11, 12, 10, 0], [12, 11, 10, 1, 4, 3, 0], [7, 6, 9, 8, 1, 11, 0], [4, 8, 8, 7, 1, 12, 0], [16, 1, 4, 5, 1, 13, 0], [15, 1, 1, 1, 1, 1, 1, 1, 8, 5, 0], [17, 7, 6, 1, 0], [9, 10, 17, 0], [4, 8, 5, 1, 1, 1, 3, 3, 10, 0], [22, 1, 1, 1, 21, 0], [28, 1, 1, 1, 1, 23, 0], [7, 47, 4, 0], [5, 5, 5, 35, 6, 0], [3, 11, 9, 14, 3, 3, 11, 0], [22, 7, 5, 23, 0], [34, 25, 0]]
    cols = [[60, 0], [60, 0], [60, 0], [9, 8, 14, 23, 2, 0], [23, 4, 9, 4, 3, 4, 7, 0], [5, 8, 41, 3, 0], [22, 37, 0], [10, 16, 1, 1, 1, 1, 10, 8, 4, 0], [17, 3, 2, 1, 1, 1, 1, 20, 0], [5, 17, 1, 9, 8, 0], [13, 6, 1, 16, 0], [17, 1, 1, 11, 3, 0], [9, 8, 2, 1, 2, 14, 0], [5, 9, 5, 6, 1, 4, 7, 0], [16, 7, 7, 12, 0], [13, 10, 10, 1, 7, 2, 0], [10, 3, 1, 8, 10, 11, 0], [5, 6, 11, 11, 5, 3, 0], [12, 13, 12, 9, 0], [10, 1, 1, 11, 13, 1, 7, 0], [11, 13, 13, 8, 0], [5, 3, 1, 15, 15, 7, 0], [10, 14, 1, 12, 1, 4, 1, 0], [9, 15, 16, 7, 0], [8, 1, 17, 14, 1, 6, 0], [5, 3, 15, 1, 14, 3, 2, 0], [8, 16, 16, 6, 0], [9, 1, 16, 16, 6, 0], [8, 15, 16, 5, 0], [5, 2, 1, 6, 0], [9, 3, 1, 0], [8, 6, 0], [8, 5, 0], [5, 3, 10, 4, 1, 5, 6, 3, 6, 0], [8, 5, 10, 2, 13, 4, 0], [9, 16, 16, 7, 0], [8, 1, 16, 16, 3, 1, 0], [5, 3, 16, 16, 7, 0], [9, 14, 15, 6, 0], [10, 15, 15, 7, 0], [9, 1, 15, 14, 5, 2, 0], [5, 5, 13, 14, 7, 0], [10, 1, 13, 13, 8, 0], [11, 11, 1, 11, 1, 9, 0], [13, 1, 10, 11, 7, 2, 0], [5, 7, 11, 10, 2, 7, 0], [10, 3, 9, 8, 1, 11, 0], [15, 7, 1, 6, 1, 12, 0], [9, 6, 7, 5, 10, 2, 0], [5, 9, 1, 2, 3, 6, 7, 0], [19, 1, 16, 0], [14, 4, 1, 2, 4, 9, 0], [21, 1, 20, 0], [5, 4, 12, 1, 2, 15, 3, 0], [29, 1, 1, 15, 10, 0], [9, 10, 6, 4, 6, 15, 4, 0], [15, 29, 14, 0], [5, 32, 21, 0], [14, 9, 6, 18, 9, 0], [60, 0]]
    
    N = len(rows)

    T0 = time.time()

    # board = np.zeros((N, N), np.int8)
    board = []
    for _ in range(N):
        board.append([])
        for _ in range(N):
            board[-1].append(0)  # TODO: change to numpy

    preprocessing(board, rows, cols)
    prettyPrintBoard(board, rows, cols, jump=False)
    checkBoardAgainstRef(board, "output.png")
    quit()

    recur(board, rows, cols, 0)

    # prettyPrintBoard(board)
    # print(isvalid(board, rows, cols))

sys.setrecursionlimit(10000)
solve()

# TODO: take image input and make nonogram!!

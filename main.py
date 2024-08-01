import numpy as np
import sys
import time
from pynput import keyboard

N = 0
T0 = 0

def T(arr):
    return list(zip(*arr))

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
                    print(col[i], end='')
                except IndexError:
                    print(' ', end='')
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
                elif board[j][i] == 0b110:
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
                elif board[j][i] == 0b110:
                    bnm1 = j
            
            if pnm1 != -1:
                for j in range(pnm1, N - rule - bnm1 - 2, -1):
                    board[j][i] = 0b111
                
                if pnm1 == N - 1:
                    board[N - rule - bnm1 - 2][i] = 0b110

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
                elif board[i][j] == 0b110:
                    b0 = j

            if p0 != -1:
                for j in range(p0, rule + b0 + 1):  # eek
                    board[i][j] = 0b111
                
                if p0 == 0:
                    board[rule + b0 + 1][i] = 0b110

            # bn-1
            rule = rowRule[-2]

            bnm1 = -1
            pnm1 = -1
            start = True
            for j in range(N - 1, N - rule - 1, -1):
                if board[i][j] == 0b111 and start:
                    start = False
                    pnm1 = j
                elif board[i][j] == 0b110:
                    bnm1 = j
            
            if pnm1 != -1:
                for j in range(pnm1, N - rule - bnm1 - 2, -1):
                    board[i][j] = 0b111

                if pnm1 == N - 1:
                    board[i][N - rule - bnm1 - 2] = 0b110


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
    # prettyPrintBoard(board, rows)

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

    if board[row][col] & 0b100:  # if its definitely correct then leave it alone
        recur(board, rows, cols, currentPos + 1)
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

    rows = rowColParse("6,2 9,6 1 1 1,4 1 5,2 5,1 1 4,2 4 2 3,3 3 1 4,2 2 2 4,1 1 2 3,4 2 3 3,2 2 2 1 2,1 1 2 3 1,2 1 3 2 1,3 2 2 2 3,5 2 2 3,5 2 2 2,7 3 5,1 3 9,3 9")
    cols = rowColParse("6,2 2 2,1 1 1,2 2 2 2,5 3 1,4 1 3 1,3 2 4 1,2 3 8,2 3 3,3 2 2,2 1 1 2,3 7,2 2 3 4,3 9 3,2 1 3 3 2,1 2 3 5,1 6 2 3,9 4 3,9 6,2 13")

    # rows = [[60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [16, 1, 20, 1, 18, 0], [14, 17, 15, 0], [13, 15, 14, 0], [11, 15, 12, 0], [10, 14, 12, 0], [8, 12, 11, 0], [6, 12, 11, 0], [6, 12, 4, 10, 0], [6, 1, 12, 5, 1, 10, 0], [5, 10, 6, 9, 0], [6, 1, 11, 6, 10, 0], [6, 1, 11, 8, 9, 0], [6, 4, 9, 7, 9, 0], [6, 5, 10, 8, 9, 0], [13, 10, 8, 8, 0], [12, 10, 1, 9, 9, 0], [13, 9, 8, 1, 8, 0], [12, 10, 9, 8, 0], [13, 10, 8, 9, 0], [12, 10, 10, 8, 0], [13, 9, 9, 8, 0], [12, 9, 9, 9, 0], [13, 10, 9, 8, 0], [12, 10, 9, 9, 0], [13, 9, 9, 1, 8, 0], [12, 10, 1, 9, 8, 0], [13, 9, 8, 9, 0], [12, 10, 8, 9, 0], [13, 10, 8, 9, 0], [12, 10, 8, 1, 9, 0], [13, 11, 7, 9, 0], [12, 9, 8, 10, 0], [13, 11, 6, 10, 0], [12, 11, 5, 10, 0], [13, 12, 4, 11, 0], [12, 12, 11, 0], [13, 11, 1, 12, 0], [12, 13, 12, 0], [13, 14, 13, 0], [12, 15, 14, 0], [13, 16, 16, 0], [38, 1, 1, 17, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0]]
    # cols = [[60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [20, 39, 0], [17, 35, 0], [17, 36, 0], [16, 36, 0], [16, 37, 0], [15, 37, 0], [14, 38, 0], [14, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 9, 0], [13, 8, 0], [12, 8, 0], [12, 1, 8, 0], [11, 8, 0], [12, 8, 0], [11, 8, 0], [13, 2, 3, 2, 3, 4, 4, 4, 4, 12, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [31, 3, 24, 0], [23, 1, 17, 0], [20, 15, 0], [17, 12, 0], [16, 11, 0], [15, 1, 1, 10, 0], [14, 9, 0], [13, 1, 1, 1, 1, 8, 0], [12, 1, 17, 1, 8, 0], [12, 24, 8, 0], [12, 28, 7, 0], [11, 28, 8, 0], [12, 28, 7, 0], [11, 28, 8, 0], [12, 26, 7, 0], [12, 21, 8, 0], [12, 1, 1, 2, 2, 1, 9, 0], [13, 9, 0], [14, 1, 10, 0], [14, 1, 11, 0], [16, 13, 0], [18, 1, 1, 15, 0], [20, 1, 18, 0], [25, 1, 1, 1, 1, 23, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0], [60, 0]]

    N = len(rows)

    T0 = time.time()

    # board = np.zeros((N, N), np.int8)
    board = []
    for _ in range(N):
        board.append([])
        for _ in range(N):
            board[-1].append(0)  # TODO: change to numpy

    preprocessing(board, rows, cols)
    # prettyPrintBoard(board, rows, cols, jump=False)
    # quit()

    recur(board, rows, cols, 0)

    # prettyPrintBoard(board)
    # print(isvalid(board, rows, cols))

sys.setrecursionlimit(10000)
solve()

# TODO: take image input and make nonogram!!

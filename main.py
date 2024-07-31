import numpy as np
import sys
import time
from pynput import keyboard

N = 0
T0 = 0

def T(arr):
    out = []
    for i in range(len(arr[0])):
        out.append([])
        for j in range(len(arr)):
            out[-1].append(arr[j][i])

    return out

def prettyPrintBoard(board, rows=None, cols=None):
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

    boardRow = T(board)[col]
    ruleRow = rows[col]

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

    # quit()

def getRowRule(board, rows, col):
    rowData = T(board)[col]
    rowRule = rows[col]
    rc = 0
    current = 0

    for item in rowData:
        if ~item & 0b10:
            break
        elif item & 0b1:
            current += 1
        else:
            if current != 0:
                rc += 1
                current = 0
    
    return rowRule[rc], (current == 0) and (rc < len(rows[col]) - 1), rc == len(rowRule) - 2  # -2 because of how the later bit works

def recur(board, rows, cols, currentPos):
    """
    Init: new recur for every step
    
    Optimisations:
    [x] On failed recursion, return instead of currentPos - 1
    [x] Fill in row blocks that are guaranteed from t0 (80% improvement!)
    [x] Fill in row blocks as they're made (6 must be 6, not just 1, so can fill all 6 when attempting to put 1)
    [x] isValid only needs to check current row and col, all else are guaranteed correct
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

    if board[row][col] & 0b100:  # if its definitely correct then leave it alone
        recur(board, rows, cols, currentPos + 1)
        return

    # blocks:
    rowRule, doit, endOfRowFlag = getRowRule(board, rows, col)
    
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
            board[i][col] = 0b1011

        if endOfRowFlag:
            for i in range(row + rowRule, N):
                board[i][col] = 0b1010
            
            addOn += N - row - rowRule - 1
        else:
            try:
                board[row + rowRule][col] = 0b1010
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

    # later...
    board[row][col] = 0b10
    if doit:
        # time.sleep(2)
        for i in range(row + 1, row + addOn):
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
    high-3: part of bandboxed segment (1) / not part of bandboxed segment (0)  - NOT NEEDED!!
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

    # rows = [[100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [14, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 21, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 15, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 12, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 14, 0], [12, 1, 25, 1, 1, 1, 3, 1, 1, 26, 1, 13, 0], [12, 1, 27, 1, 1, 1, 1, 1, 26, 1, 1, 12, 0], [12, 1, 28, 1, 1, 1, 1, 28, 1, 13, 0], [12, 1, 30, 1, 1, 1, 30, 1, 13, 0], [12, 1, 29, 1, 1, 1, 30, 1, 13, 0], [12, 1, 31, 1, 1, 30, 1, 1, 12, 0], [12, 1, 30, 1, 1, 31, 1, 13, 0], [11, 1, 1, 31, 1, 1, 30, 1, 13, 0], [12, 1, 32, 1, 1, 31, 1, 14, 0], [12, 1, 31, 1, 32, 1, 13, 0], [12, 1, 32, 1, 32, 1, 13, 0], [12, 1, 31, 1, 33, 1, 13, 0], [12, 1, 33, 1, 31, 1, 13, 0], [12, 1, 31, 1, 32, 1, 13, 0], [12, 1, 32, 1, 32, 1, 1, 12, 0], [12, 1, 31, 1, 31, 1, 13, 0], [12, 1, 33, 1, 32, 1, 13, 0], [12, 1, 31, 1, 1, 32, 1, 13, 0], [11, 1, 1, 31, 1, 31, 1, 13, 0], [12, 1, 32, 1, 32, 1, 1, 12, 0], [12, 1, 32, 1, 32, 1, 13, 0], [12, 1, 31, 1, 32, 1, 13, 0], [12, 1, 33, 1, 32, 1, 13, 0], [12, 1, 31, 1, 32, 1, 13, 0], [12, 1, 32, 1, 32, 1, 13, 0], [12, 1, 31, 1, 31, 1, 1, 12, 0], [12, 1, 33, 1, 32, 1, 14, 0], [12, 1, 31, 1, 1, 31, 1, 13, 0], [11, 1, 1, 31, 1, 32, 13, 0], [12, 1, 32, 1, 32, 2, 13, 0], [12, 1, 32, 1, 32, 1, 12, 0], [12, 1, 31, 1, 1, 31, 1, 14, 0], [12, 1, 33, 32, 1, 13, 0], [12, 1, 31, 1, 1, 31, 1, 1, 12, 0], [12, 1, 32, 1, 32, 1, 13, 0], [12, 1, 31, 1, 32, 1, 13, 0], [12, 1, 33, 1, 32, 1, 13, 0], [12, 1, 31, 1, 32, 1, 1, 12, 0], [11, 1, 1, 31, 1, 32, 1, 13, 0], [12, 1, 32, 1, 31, 1, 13, 0], [12, 1, 32, 1, 32, 1, 14, 0], [12, 1, 31, 1, 1, 31, 1, 13, 0], [12, 1, 33, 1, 31, 1, 13, 0], [12, 1, 31, 1, 33, 1, 13, 0], [12, 1, 32, 1, 32, 1, 13, 0], [12, 1, 31, 1, 1, 31, 1, 13, 0], [12, 1, 33, 32, 1, 1, 12, 0], [12, 1, 31, 1, 1, 31, 1, 13, 0], [11, 1, 1, 31, 1, 32, 1, 13, 0], [12, 1, 32, 1, 33, 1, 13, 0], [12, 1, 32, 1, 31, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 1, 1, 6, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 13, 0], [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 12, 0], [14, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 14, 0], [42, 1, 1, 1, 1, 2, 43, 0], [43, 1, 1, 1, 1, 45, 0], [45, 1, 1, 1, 46, 0], [46, 1, 1, 1, 46, 0], [46, 1, 1, 1, 47, 0], [47, 1, 49, 0], [48, 1, 49, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0]]
    # cols = [[100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [30, 10, 9, 9, 9, 28, 0], [18, 1, 1, 1, 1, 1, 21, 0], [18, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 21, 0], [17, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 20, 0], [18, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 21, 0], [17, 1, 2, 18, 9, 9, 9, 3, 1, 20, 0], [18, 52, 1, 1, 21, 0], [17, 2, 1, 52, 1, 1, 20, 0], [18, 1, 52, 1, 21, 0], [17, 1, 1, 54, 21, 0], [18, 2, 52, 1, 20, 0], [17, 1, 52, 1, 22, 0], [18, 54, 1, 1, 20, 0], [17, 2, 52, 22, 0], [18, 1, 52, 2, 20, 0], [17, 1, 1, 52, 23, 0], [18, 1, 52, 1, 20, 0], [17, 1, 2, 53, 22, 0], [18, 52, 2, 20, 0], [17, 3, 52, 22, 0], [18, 53, 2, 20, 0], [17, 1, 1, 52, 23, 0], [18, 1, 52, 1, 20, 0], [17, 1, 2, 52, 1, 22, 0], [18, 52, 1, 1, 20, 0], [17, 2, 1, 52, 22, 0], [18, 1, 52, 2, 20, 0], [17, 1, 1, 52, 23, 0], [18, 2, 52, 1, 20, 0], [18, 52, 2, 21, 0], [18, 3, 51, 1, 20, 0], [19, 54, 1, 19, 0], [19, 1, 50, 1, 3, 18, 0], [20, 3, 50, 1, 19, 0], [20, 2, 49, 1, 17, 0], [22, 1, 1, 1, 49, 1, 1, 15, 0], [23, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 14, 0], [24, 1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 13, 0], [26, 1, 3, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 2, 1, 14, 0], [24, 2, 1, 1, 2, 2, 1, 1, 2, 1, 1, 2, 3, 1, 13, 0], [22, 1, 1, 1, 3, 2, 1, 3, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 16, 0], [22, 1, 1, 1, 1, 47, 1, 2, 15, 0], [20, 1, 1, 1, 49, 1, 1, 16, 0], [21, 1, 50, 1, 1, 18, 0], [19, 2, 52, 1, 19, 0], [19, 1, 50, 2, 1, 19, 0], [18, 1, 53, 1, 20, 0], [18, 2, 51, 2, 20, 0], [18, 1, 52, 23, 0], [17, 1, 53, 1, 20, 0], [18, 2, 52, 2, 21, 0], [17, 1, 52, 1, 1, 20, 0], [18, 2, 52, 1, 21, 0], [17, 2, 52, 2, 20, 0], [18, 1, 52, 23, 0], [17, 1, 53, 1, 20, 0], [18, 1, 52, 1, 22, 0], [17, 1, 54, 1, 1, 20, 0], [18, 52, 22, 0], [17, 3, 52, 3, 20, 0], [18, 1, 52, 1, 20, 0], [17, 1, 1, 53, 1, 21, 0], [18, 1, 51, 1, 2, 20, 0], [17, 1, 55, 21, 0], [18, 51, 3, 20, 0], [17, 2, 54, 22, 0], [18, 1, 52, 1, 20, 0], [17, 1, 1, 51, 1, 1, 21, 0], [18, 2, 53, 1, 1, 20, 0], [17, 1, 52, 1, 21, 0], [18, 54, 1, 1, 20, 0], [17, 2, 52, 1, 21, 0], [18, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 20, 0], [17, 1, 1, 3, 1, 3, 3, 2, 3, 1, 4, 1, 3, 3, 1, 21, 0], [18, 2, 2, 1, 3, 3, 3, 1, 1, 2, 1, 3, 3, 3, 20, 0], [18, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 22, 0], [21, 2, 3, 8, 4, 5, 4, 2, 3, 8, 8, 21, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0], [100, 0]]
    
    N = len(rows)

    T0 = time.time()

    # board = np.zeros((N, N), np.int8)
    board = []
    for _ in range(N):
        board.append([])
        for _ in range(N):
            board[-1].append(0)  # TODO: change to numpy

    preprocessing(board, rows, cols)
    # prettyPrintBoard(board, rows, cols)
    # quit()

    recur(board, rows, cols, 0)

    # prettyPrintBoard(board)
    # print(isvalid(board, rows, cols))

sys.setrecursionlimit(10000)
solve()

# TODO: take image input and make nonogram!!

import numpy as np
import sys
import time

N = 0
T0 = 0

def T(arr):
    out = []
    for i in range(len(arr[0])):
        out.append([])
        for j in range(len(arr)):
            out[-1].append(arr[j][i])

    return out

def prettyPrintBoard(board):
    print("\033[%d;%dH" % (0, 0))

    for row in np.array(board).T:
        for item in row:
            if (~item & 0b10):
                print("?", end='')
            elif (~item & 0b1):
                print("x", end='')
            else:
                print("█", end='')
        print(' ' * 20)

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

def isValid(board, rows, cols, row, col):
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


    boardRow = board[row]
    ruleRow = cols[row]

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

def recur(board, rows, cols, currentPos):
    """
    Init: new recur for every step
    
    Optimisations:
    [x] On failed recursion, return instead of currentPos - 1
    [] Fill in row blocks that are guaranteed from t0
    [] Fill in row blocks as they're made (6 must be 6, not just 1, so can fill all 6 when attempting to put 1)
    [x] isValid only needs to check current row and col, all else are guaranteed correct

    Timings:
    No opt: 7.55s
    Recur: 7.88s (oof but it has to be done :p)
    """
    global N, T0

    # print(currentPos)
    # prettyPrintBoard(board)

    if currentPos == N**2:
        prettyPrintBoard(board)

        print(time.time() - T0)
        quit()

    row = currentPos % N
    col = currentPos // N

    # blocks:
    # rowData = T(board)[col]
    # rowRule = rows[col]
    # rc = 0
    # current = 0

    # for item in rowData:
    #     if item & 0b

    # print(rowData, rowRule)

    if board[row][col] & 0b100:  # if its definitely correct then leave it alone
        recur(board, rows, cols, currentPos + 1)
        return

    board[row][col] = 0b11

    # recur:
    worked = isValid(board, rows, cols, row, col)
    if worked:
        recur(board, rows, cols, currentPos + 1)
        
        # later...
        board[row][col] = 0b10
        worked = isValid(board, rows, cols, row, col)
        if worked:
            recur(board, rows, cols, currentPos + 1)
        
        # later...
        board[row][col] = 0b00
        return
    else:
        board[row][col] = 0b10
        worked = isValid(board, rows, cols, row, col)
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

    N = len(rows)

    T0 = time.time()

    # board = np.zeros((N, N), np.int8)
    board = []
    for _ in range(N):
        board.append([])
        for _ in range(N):
            board[-1].append(0)  # TODO: change to numpy

    preprocessing(board, rows, cols)
    prettyPrintBoard(board)
    quit()

    # recur(board, rows, cols, 0)

    # prettyPrintBoard(board)
    # print(isvalid(board, rows, cols))


solve()

# TODO: take image input and make nonogram!!

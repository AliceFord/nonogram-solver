import numpy as np
import sys
import time

N = 20

T0 = 0

def prettyPrintBoard(board):
    print("\033[%d;%dH" % (0, 0))

    for row in np.array(board).T:
        for item in row:
            if item == -1:
                print("?", end='')
            elif item == 0:
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

def isvalid(board, rows, cols):
    """
    LOGIC:
    for each square:
        if -1:
            ensure correct length (<=) of previous box, break
        if 1, add to count
        if 0 and count != 0:
            ensure correct length of previous box, remove current box.
    """

    for boardRow, ruleRow in zip(np.array(board).T, rows):
        ruleCounter = 0
        current = 0
        brokenOut = False
        for item in boardRow:
            if item == -1:
                if current != 0:
                    if current <= ruleRow[ruleCounter]:
                        brokenOut = True
                        break
                    else:
                        return False
                else:
                    brokenOut = True
                    break
            elif item == 1:
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
            if item == -1:
                if current != 0:
                    if current <= ruleRow[ruleCounter]:
                        brokenOut = True
                        break
                    else:
                        return False
                else:
                    brokenOut = True
                    break
            elif item == 1:
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


def recur(board, rows, cols, currentPos):
    """
    Init: new recur for every step
    
    Optimisations:
    - On failed recursion, return instead of currentPos - 1
    - Fill in row blocks that are guaranteed from t0
    - Fill in row blocks as they're made (6 must be 6, not just 1, so can fill all 6 when attempting to put 1)

    Timings:
    No opt: 7.55s
    Recur: 7.88s (oof but it has to be done :p)
    """
    # print(currentPos)
    # prettyPrintBoard(board)

    if currentPos == N**2:
        prettyPrintBoard(board)

        print(time.time() - T0)
        quit()

    row = currentPos % N
    col = currentPos // N

    board[row][col] = 1
    worked = isvalid(board, rows, cols)
    if worked:
        recur(board, rows, cols, currentPos + 1)
        
        # later...
        board[row][col] = 0
        worked = isvalid(board, rows, cols)
        if worked:
            recur(board, rows, cols, currentPos + 1)
        # else:
        #     board[row][col] = -1
        #     return
        
        # later...
        board[row][col] = -1
        return
    else:
        board[row][col] = 0
        worked = isvalid(board, rows, cols)
        if worked:
            recur(board, rows, cols, currentPos + 1)
        # else:
        #     board[row][col] = -1
        #     return

        # later...
        board[row][col] = -1
        return

    
def solve():
    global T0
    board = []
    for _ in range(N):
        board.append([])
        for _ in range(N):
            board[-1].append(-1)

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

    T0 = time.time()

    recur(board, rows, cols, 0)

    # prettyPrintBoard(board)
    # print(isvalid(board, rows, cols))


sys.setrecursionlimit(1000000)
solve()

# TODO: take image input and make nonogram!!

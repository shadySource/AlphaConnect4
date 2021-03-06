'''
Pure python implementation of a connect 4 terminal game object.
Optimizations applied allow computation of one move and one check in approx. 100us.
---Still kinda slow... see connect4tf.py for a (hopefully) faster implementation.---nvm, this is all i got
'''
import numpy as np

class Connect4Board(object):
    def __init__(self, board_shape=(6, 7), winVecs=None):
        if winVecs is not None:
            self.wins=winVecs
        self.grid = np.zeros(board_shape, dtype=np.int8)
        self.height = np.zeros(board_shape[1], dtype=np.int8)
        self.player = 1
    def move(self, prob):# Add a piece to the board
        prob = prob * np.less(self.height, 6)
        if np.sum(prob) > 0:
            slot = np.argmax(prob)
            self.grid[self.height[slot], slot] = self.player
            self.height[slot] += 1
            #self.player *= -1# this is a bit slower than if statements...
            if self.player < 0:# swap players
                self.player = 1
            else:
                self.player = -1
            return None# No tie
        return 0# Game is a tie
    def check(self):# Check if anyone has won
        checked = np.dot(self.grid.reshape(42,), self.wins)
        if np.sum(checked > 3):
            return 1
        if np.sum(checked < -3):
            return -1
        return None# No winner
    def __str__(self):# String for print
        return str(self.grid[::-1])

class BoardExplorer(Connect4Board):
    def __init__(self,  board_shape=(6, 7), toWin=4):
        super().__init__(board_shape)
        self.toWin = toWin
        self.wins = []
    def findHorizWins(self):
        for i in range(self.grid.shape[1]-self.toWin+1):
            horiz = np.zeros(self.grid.shape[1], dtype=np.int8)
            for k in range(self.toWin):
                horiz[i+k] = 1
            for j in range(self.grid.shape[0]):
                self.grid[j] = horiz
                self.wins.append(self.grid)
                # self.wins.append(np.where(self.grid > 0))
                # print(super().__str__())
                super().__init__(self.grid.shape) #reset grid
        # print("winpatterns:", len(self.wins))
    def findVerticalWns(self):
        for i in range(self.grid.shape[0]-self.toWin+1):
            vert = np.zeros((self.grid.shape[0], 1), dtype=np.int8)
            for k in range(self.toWin):
                vert[i+k][0] = 1
            for j in range(self.grid.shape[1]):
                self.grid[:,j] = vert[:,0]
                self.wins.append(self.grid)
                # self.wins.append(np.where(self.grid > 0))
                # print(super().__str__())
                super().__init__(self.grid.shape) #reset grid
        # print("winpatterns:", len(self.wins))
    def findDiagWins(self):
        # first half:
        row = 0
        while(row < self.grid.shape[0]):
            col = 0
            rowTmp = row
            diag = []
            while rowTmp >= 0: # get the diagonal
                diag.append((rowTmp, col))
                rowTmp -= 1
                col += 1
            row += 1
            if len(diag) >= self.toWin:# if diag large enough,
                # step through all positions of a winning sequence on the grid:
                for i in range(len(diag)-self.toWin+1):
                    # Choose points:
                    winDiag = [diag[i+k] for k in range(self.toWin)]
                    # convert points to np.array indices
                    winIdx = (np.array([i for i, j in winDiag]), np.array([j for i, j in winDiag]))
                    self.grid[winIdx] = 1# winning diag = to 1
                    self.wins.append(self.grid)
                    # self.wins.append(np.where(self.grid > 0))#save points
                    # print(super().__str__())
                    self.grid = np.flip(self.grid, axis=0)# flip vertically
                    self.wins.append(self.grid)
                    # self.wins.append(np.where(self.grid > 0))#save points
                    # print(super().__str__())
                    self.grid = np.flip(self.grid, axis=1)# flip horizontally
                    self.wins.append(self.grid)
                    # self.wins.append(np.where(self.grid > 0))#save points
                    # print(super().__str__())
                    self.grid = np.flip(self.grid, axis=0)# flip vertically
                    self.wins.append(self.grid)
                    # self.wins.append(np.where(self.grid > 0))#save points
                    # print(super().__str__())
                    super().__init__(self.grid.shape)# reset grid
        print("winpatterns:", len(self.wins))
    def getWinPatterns(self):
        self.wins = []
        self.findHorizWins()
        self.findVerticalWns()
        self.findDiagWins()
        filters = np.swapaxes(np.array(self.wins, dtype=np.int8).T, 0, 1) #(6x7x69)
        return filters.reshape(42, 69) # single vector for comparison

if __name__ == "__main__":
    explore = BoardExplorer()
    # explore.findHorizWins()
    # explore.findVerticalWns()
    # explore.findDiagWins()
    winVecs = explore.getWinPatterns()
    # np.save("winVecs", winVecs)
    board = Connect4Board(winVecs=winVecs)
    for i in range(5):
        board.move(i+1)
        board.move(i)
        board.move(i+1)
        board.move(i)
        board.move(i+1)
        board.move(i)
    print(board)
    print(board.check())

    winVecs1 = explore.getWinPatterns()

    board = Connect4Board(winVecs=winVecs1)
    import timeit
    print(timeit.timeit("board = Connect4Board(winVecs=winVecs)", setup="from __main__ import Connect4Board, winVecs", number=1000)/1000)
    print(timeit.timeit("board.move(1);board = Connect4Board(winVecs=winVecs)", setup="from __main__ import board, Connect4Board, winVecs", number=10000)/10000)
    print(timeit.timeit("board.check()", setup="from __main__ import board", number=10000)/10000)

    # x = board.grid.reshape((42,))
    # y = winFilters
    # print(np.dot(x, y))
    # exit()


    # print(winFilters)
    # print(winFilters.shape)
    # x = np.matmul(board.grid, winFilters)
    # print(x[:,:,:])
    # x = np.sum(x, axis=0)
    # x = np.sum(x, axis=0)
    # # print(winFilters[:,:,np.where(x == 16)[0][0]])
    # print(x.shape)
    # print(x)
    # exit()

    # print("wins = [")
    # for i in wins:
    #     print("(np.array([{},{},{},{}], dtype=np.int32), np.array([{},{},{},{}], dtype=np.int32)),".format(
    #     i[0][0], i[0][1], i[0][2], i[0][3], i[1][0], i[1][1], i[1][2], i[1][3]))
    # print("]")
    # exit()


    # import timeit
    # x = np.ndarray((6, 7), dtype=np.int8)
    # y = np.ndarray((6, 7, 69), dtype=np.int8)
    # print(timeit.timeit("np.sum(np.dot(x, y))", setup="from __main__ import x, y, np", number=10000)/10000)
    # print(timeit.timeit("np.sum(np.dot(board, winFilters))", setup="from __main__ import board, winFilters, np", number=1000)/1000)
    # print(timeit.timeit("board.check()", setup="from __main__ import board", number=1000)/1000)


    # print(timeit.timeit("board = Connect4Board()", setup="from __main__ import Connect4Board", number=1000)/1000)
    # import time
    # N = 1000
    # start = time.time()
    # for i in range(N):
    #     board = Connect4Board()
    #     for k in range(6):
    #         for j in range(7):
    #             board.move(j)
    #             [np.sum(board.grid[i]) for i in wins]
    #
    # print(1000/(time.time()-start))

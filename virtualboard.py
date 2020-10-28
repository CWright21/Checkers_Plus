class VirtualBoard:
    def __init__(self):
        self.vBoard = [[], [], [], [], [], [], [], []]
        for i in range(8):
            row = self.vBoard[i]
            for j in range(8):
                row.append(None)
            self.vBoard[i] = row

    def add_piece_to_board(self, x, y, piece):
        self.vBoard[x][y] = piece

    def move_piece(self, fromX, fromY, toX, toY):
        piece = None
        piece = self.vBoard[fromY][fromX]
        self.vBoard[fromY][fromX] = None
        self.vBoard[toY][toX] = piece

    '''
        returns true if move is valid
    '''
    def check_move(self, fromX, fromY, toX, toY, team):
        print("checking from", fromX, ',', fromY, ' to ', toX, ',', toY)
        # is piece at starting coords
        isAtStart = self.vBoard[fromY][fromX] is not None
        if isAtStart:
            print("is at start")
        else:
            return False

        # is there a piece aat ending coords
        endOpen = self.vBoard[toY][toX] is None
        #print(self.vBoard[toY][toX])
        if endOpen:
            print("end is open")

        # is the piece yours
        correctTeam = self.vBoard[fromY][fromX].team == team
        if correctTeam:
            print("piece is yours")

        # is valid direction to move (x +/- 1, y + 1)
        if self.vBoard[fromY][fromX].team == "red":
            validPawnMove = (fromY == toY - 1 and toX + 1 == fromX) or \
                            (fromY == toY - 1 and toX - 1 == fromX)
        else:
            validPawnMove = (fromY == toY + 1 and toX + 1 == fromX) or \
                            (fromY == toY + 1 and toX - 1 == fromX)

        if validPawnMove:
            print("valid pawn move")

        # if king and valid king move (x +/- 1, y - 1)
        if self.vBoard[fromY][fromX].team == "red":
            validKingMove = self.vBoard[fromY][fromX].king and \
                            ((fromY - 1  == toY and fromX + 1 == toX) or
                             (fromY - 1  == toY and fromX - 1 == toX))

        else:
            print(self.vBoard[fromY][fromX].king)
            print((fromY + 1 == toY and (fromX + 1 == toX or fromX - 1 == toX)))
            validKingMove = self.vBoard[fromY][fromX].king and \
                            (fromY + 1 == toY and (fromX + 1 == toX or fromX - 1 == toX))

        if validKingMove:
            print("valid king move")

        return isAtStart and endOpen and correctTeam and (validPawnMove or validKingMove)

    def king_piece(self, x, y):
        print()
        self.vBoard[y][x].king_me()

    def get_king(self, x, y):
        if self.vBoard[y][x] is not None:
            return self.vBoard[y][x].king
        return False

    def get_team(self, x, y):
        if self.vBoard[y][x] is not None:
            return self.vBoard[y][x].team
        return None

    def check_jumps(self, team):
        possibleList = []
        for y in range(8):
            for x in range(8):
                returns = self.check_jump(x, y, team)
                if returns.pop(0):
                    print(returns)
                    for jump in returns:
                        possibleList.append(jump)
                        print("found a jump from %d, %d to %d, %d" % (x, y, jump[0], jump[1]))

        if len(possibleList) == 0:
            print("no jumps found")
        print(possibleList)
        return possibleList

    '''
    pre:
    post: returns a list of [bool, (x,y), (x,y)]
    '''
    def check_jump(self, x, y, team):
        #TODO Write code to check for jumps across board
        toReturn = [False]
        #checking jump
        if self.vBoard[y][x] is not None:
            piece = self.vBoard[y][x]

            #if correct team (player ready to move)
            if piece.team == team:

                #check for jumps from target piece
                #check to see if adj to enemy piece
                if team == "red":
                    withinRangeDown = 0 <= y - 1 < 8
                    withinRangeUp = 0 <= y + 1 < 8
                    withinRangeLeft = 0 <= x + 1 < 8
                    withinRangeRight = 0 <= x - 1 < 8
                    enemyDownLeft = enemyDownRight = enemyUpLeft = enemyUpRight = False
                    # target is up-left
                    if withinRangeUp and withinRangeLeft:
                        enemyUpLeft = self.vBoard[y + 1][x + 1] is not None and self.vBoard[y + 1][x + 1].team != team

                    # target is up-right
                    if withinRangeUp and withinRangeRight:
                        enemyUpRight = self.vBoard[y + 1][x - 1] is not None and self.vBoard[y + 1][x - 1].team != team

                    if withinRangeDown and (withinRangeLeft or withinRangeRight):
                        if piece.king and not (enemyUpLeft or enemyUpRight):
                            # target is down-left
                            if withinRangeLeft:
                                enemyDownLeft = self.vBoard[y - 1][x + 1] is not None and self.vBoard[y - 1][
                                    x + 1].team != team
                            # target is down-right
                            if withinRangeRight:
                                enemyDownRight = self.vBoard[y - 1][x - 1] is not None and self.vBoard[y - 1][
                                    x - 1].team != team

                #black
                else:
                    withinRangeUp = 0 <= y - 1 < 8
                    withinRangeDown = 0 <= y + 1 < 8
                    withinRangeLeft = 0 <= x - 1 < 8
                    withinRangeRight = 0 <= x + 1 < 8
                    enemyDownLeft = enemyDownRight = enemyUpLeft = enemyUpRight = False
                    # target is up-left
                    if withinRangeUp and withinRangeLeft:
                        enemyUpLeft = self.vBoard[y - 1][x - 1] is not None and self.vBoard[y - 1][x - 1].team != team

                    # target is up-right
                    if withinRangeUp and withinRangeRight:
                        enemyUpRight = self.vBoard[y - 1][x + 1] is not None and self.vBoard[y - 1][x + 1].team != team

                    if withinRangeDown and (withinRangeLeft or withinRangeRight):
                        if piece.king:
                            # target is down-left
                            if withinRangeLeft:
                                enemyDownLeft = self.vBoard[y + 1][x - 1] is not None and self.vBoard[y + 1][
                                    x - 1].team != team
                            # target is down-right
                            if withinRangeRight:
                                enemyDownRight = self.vBoard[y + 1][x + 1] is not None and self.vBoard[y + 1][
                                    x + 1].team != team

                #if enemy exists
                if enemyUpLeft or enemyUpRight or enemyDownLeft or enemyDownRight:
                    print("\nJump function:\nUpLeft: ", enemyUpLeft, "\nUpRight: ", enemyUpRight, "\nDownLeft: ",
                          enemyDownLeft, "\nDownRight: ", enemyDownRight)
                    #TODO Optimize boolean checks, reduce to functions probably
                    #check if the following tile is empty

                    if team == "red":
                        print("red piece at %d,%d has enemies" % (x,y))
                        withinRangeDown = 0 <= y - 2 < 8
                        withinRangeUp = 0 <= y + 2 < 8
                        withinRangeLeft = 0 <= x + 2 < 8
                        withinRangeRight = 0 <= x - 2 < 8
                        if enemyUpLeft:
                            if withinRangeUp and withinRangeLeft:
                                if self.vBoard[y+2][x+2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x + 2, y + 2))
                                else:
                                    print(y + 2, x + 2, " is occupied")

                        if enemyUpRight:
                            if withinRangeUp and withinRangeRight:
                                if self.vBoard[y+2][x-2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x - 2, y + 2))
                                else:
                                    print(y + 2, x - 2, " is occupied")

                        if enemyDownLeft:
                            if withinRangeDown and withinRangeLeft:
                                if self.vBoard[y-2][x+2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x + 2, y - 2))
                                else:
                                    print(y - 2, x + 2, " is occupied")

                        if enemyDownRight:
                            if withinRangeDown and withinRangeRight:
                                if self.vBoard[y-2][x-2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x - 2, y - 2))
                                else:
                                    print(y - 2, x - 2, " is occupied")

                    #black
                    else:
                        print("black piece at %d,%d has enemies" % (x,y))
                        withinRangeUp = 0 <= y - 2 < 8
                        withinRangeDown = 0 <= y + 2 < 8
                        withinRangeLeft = 0 <= x - 2 < 8
                        withinRangeRight = 0 <= x + 2 < 8
                        if enemyUpLeft:
                            if withinRangeUp and withinRangeLeft:
                                if self.vBoard[y-2][x-2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x - 2, y - 2))
                                else:
                                    print(y-2, x-2, " is occupied")

                        if enemyUpRight:
                            if withinRangeUp and withinRangeRight:
                                if self.vBoard[y-2][x+2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x + 2, y - 2))
                                else:
                                    print(y-2, x+2, " is occupied")

                        if enemyDownLeft:
                            if withinRangeDown and withinRangeLeft:
                                if self.vBoard[y+2][x-2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x - 2, y + 2))
                                else:
                                    print(y+2, x+2, " is occupied")

                        if enemyDownRight:
                            if withinRangeDown and withinRangeRight:
                                if self.vBoard[y+2][x+2] is None:
                                    toReturn[0] = True
                                    toReturn.append((x + 2, y + 2))
                                else:
                                    print(y+2, x-2, " is occupied")
        return toReturn


    def execute_jump(self, fromX, fromY, toX, toY):
        #TODO perform a jump
        piece = self.vBoard[fromY][fromX]

        if toX > fromX:
            middleX = toX-1
        else:
            middleX = toX+1

        if toY > fromY:
            middleY = toY-1
        else:
            middleY = toY+1

        self.vBoard[middleY][middleX] = None

        self.vBoard[toY][toX] = piece
        self.vBoard[fromY][fromX] = None
        pass

    def announce_piece(self, x, y):
        if x < 8 and y < 8:
            piece = self.vBoard[int(x)][int(y)]
            if piece is not None:
                print(piece.team, " piece at %d, %d" % (x, y), "\n")
            else:
                print("No piece at %d, %d" % (x, y), "\n")

    def generate_game_tree(self):
        #TODO Generate Game state tree from current state
        pass

    def check_for_game_end(self):
        redLose = True
        blackLose = True
        for col in self.vBoard:
            for piece in col:
                if piece is not None:
                    if piece.team == 'red':
                        redLose = False
                    elif piece.team == 'black':
                        blackLose = False
        if redLose:
            print("red no more pieces")
            return (True, 'black')
        if blackLose:
            print("black no more pieces")
            return (True, 'red')
        return (False, 'none')

    def __str__(self):
        toReturn = ''
        for c in range(8):
            for r in range(8):
                if self.vBoard[c][r] is not None:
                    if self.vBoard[c][r].team == "red":
                        toReturn += 'r'
                    else:
                        toReturn += 'b'
                else:
                    toReturn += '+'
            toReturn += '\n'
        return toReturn

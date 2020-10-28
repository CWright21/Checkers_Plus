import sys
from alphabeta import AlphaBeta
from gametree import GameTree
from gametree import Coord
from gametree import Move




class Piece:
    def __init__(self, team):
        self.team = team
        self.king = False

    def add_widget(self, widget):
        self.widget = widget

    def king_me(self):
        self.king = True


class VirtualBoard:
    def __init__(self):
        self.vBoard = [[], [], [], [], [], [], [], []]
        for i in range(8):
            row = self.vBoard[i]
            for j in range(8):
                row.append(None)
            self.vBoard[i] = row

    def initFromState(self, state):
        self.vBoard = [[], [], [], [], [], [], [], []]
        for c in range(8):
            self.vBoard[c] = state[c]

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
                        possibleList.append(Move(Coord(x, y), Coord(jump[0], jump[1])))
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

    def generate_game_tree(self, team, diff):
        #TODO Generate Game state tree from current state
        #TODO LOOK into how a move is validated and why there are board states being generated that do not have moves associated or terminals
        '''
        each state should be named according to the format fromX,fromY-toX,toY
        '''
        states =[]
        moves = self.generate_possible_team_moves(team)
        print(moves)
        for move in moves:
            states += self.generate_game_tree_helper(move, diff, diff)

        print('size of states', sys.getsizeof(states))
        print(states)
        print()
        return GameTree(states)

    #returns a list of possible game states assuming the move sent is made looking depth moves deep
    #account for game ending early
    def generate_game_tree_helper(self, move, depth, diff, team='red'):
        newBoard = VirtualBoard()
        newBoard.initFromState(self.vBoard)
        newBoard.move_piece(move.frm.x, move.frm.y, move.to.x, move.to.x)

        #base
        if depth == 0:
            child = (move, newBoard.eval_state(diff))
            return child

        else:
            if team == 'red':
                team = 'black'
            else:
                team = 'red'

            nextMoves = newBoard.generate_possible_team_moves(team)
            children = []
            #for every move possible for the pther team
            for nextMove in nextMoves:
                print("next Moves", nextMoves)
                children.append(newBoard.generate_game_tree_helper(nextMove, depth-1, diff))
            child = [move, children]

            return child

    #returns a list of possible moves given a starting coord
    #format: [((fromx,fromy) , (tox,toy)) , ...]
    #account for if the game ends
    def generate_possible_moves(self, x, y, team):
        moves = []
        #moves += self.check_jumps(team)
        fromX = x
        fromY = y
        for toY in range(y-1, y+2):
            for toX in range(x-1, x+2):
                if 0 <= toX < 8 and 0 <= toY < 8 and self.check_move(fromX, fromY, toX, toY, team):
                    moves.append(Move(Coord(fromX, fromY), Coord(toX, toY)))
        return moves

    # returns a list of possible moves given a team
    # format: [((fromx,fromy) , (tox,toy)) , ...]
    # account for if the game ends
    def generate_possible_team_moves(self, team):
        moves = []
        for y in range(8):
            for x in range(8):
                piece = self.vBoard[y][x]
                if piece is not None:
                    moves += self.generate_possible_moves(x, y, team)
        return moves

    def eval_state(self, diff):
        #TODO grade each board state according to diff
        value = 0
        if diff > 0:
            for c in self.vBoard:
                for piece in c:
                    if piece is not None:
                        if piece.team == 'black':
                            value-=.5
                        elif piece.team == 'red':
                            value+=1
        if diff > 1:
            pass
        if diff > 2:
            pass
        return value

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

    def parse_data_as_text(self, fname):
        with open(fname) as f:
            for r in range(8):
                line = f.readline().rstrip('\n')
                for c in range(len(line)):
                    char = line[c]
                    if char == 'r':
                        self.add_piece_to_board(r, c, Piece('red'))
                    elif char == 'b':
                        self.add_piece_to_board(r, c, Piece('black'))




def main():
    filename = 'testBoardStates.txt'
    print("hello world! " + filename)
    testBoard = VirtualBoard()
    testBoard.parse_data_as_text(filename)
    print(testBoard)
    tree = testBoard.generate_game_tree('red', 3)
    a_b = AlphaBeta(tree)
    a_b.alpha_beta_search(a_b.root)
if __name__ == "__main__":
    main()

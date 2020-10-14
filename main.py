from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import (ObjectProperty,
                             NumericProperty,
                             ReferenceListProperty,
                             ListProperty)

pathToKvlang = ".\\assets\\kvlang\\Checkers.kv"
pathToBlackGrid = ".\\assets\\images\\black_grid.jpg"
pathToWhiteGrid = ".\\assets\\images\\white_grid.jpg"
boardSize = 8
gridXVals = [1, 2, 3, 4, 5, 6, 7, 8]
gridYVals = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

maxSizeWidth = 1000
minSizeWidth = 650
windowSize = (650, 715)


class CustomRow(FloatLayout):
    pass


class CustomGrid(FloatLayout):
    def add_child_to_specific(self, row, col, widget):
        self.ids[row].ids[col].add_widget(widget)
    pass


class CheckerScreen(Widget):
    tabMenu = ObjectProperty(None)
    def __init__(self):
        super(CheckerScreen, self).__init__()
        self.activeGame = False
        self.board = None

    def human_game_button(self, widget):
        self.init_board()

    def del_board(self, widget):
        if self.board is not None:
            self.board.clear_widgets()
            self.pieces.clear_widgets()
            self.ids['board'].opacity = 0
            self.activeGame = False

    def init_board(self):
        self.possibleList = []
        self.ids['board'].opacity = 1
        self.ids['center_text'].color = 0, 0, 0, 1
        self.ids['center_text'].text = ''
        print(self.ids['information_center'].pos, ' ', self.ids['information_center'].anchor_y)
        self.virtualBoard = VirtualBoard()
        self.board = self.ids.board
        self.board.clear_widgets()

        self.pieces = self.ids.pieces
        self.pieces.clear_widgets()

        print(self.pieces)

        self.activeGame = True
        self.activePieceId = None
        self.activeTeam = "red"
        #Generate Grid
        black = True
        for c in range(8):
            for r in range(8):
                if c > 0 and r == 0:
                    black = not black

                if black:
                    inst = ToggleButton(
                        background_normal=".\\assets\\images\\black_grid.jpg",
                        background_down=".\\assets\\images\\down_grid.jpg",
                        group='board',
                    )
                    inst.bind(on_press=self.board_press)
                    inst.bind(on_release=self.board_release)
                    self.board.add_widget(inst)
                    black = not black

                    #adding piece image overlay
                    if c < 3:
                        toAdd = Button(id=str(r) + "," + str(c),
                                       background_normal=".\\assets\\images\\redPawn.png")
                        toAdd.bind(on_press=self.piece_press)
                        toAdd.bind(on_release=self.piece_release)
                        self.pieces.add_widget(toAdd)
                        # adding piece to virtual board
                        self.virtualBoard.add_piece_to_board(c, r, Piece('red'))

                    elif c >= 5:
                        toAdd = Button(background_normal=".\\assets\\images\\blackPawn.png",
                                       id=str(r) + "," + str(c))
                        toAdd.bind(on_press=self.piece_press)
                        toAdd.bind(on_release=self.piece_release)
                        self.pieces.add_widget(toAdd)
                        # adding piece to virtual board
                        self.virtualBoard.add_piece_to_board(c, r, Piece('black'))

                    else:
                        self.pieces.add_widget(Label())

                else:
                    inst = ToggleButton(
                        background_normal=".\\assets\\images\\white_grid.jpg",
                        background_down=".\\assets\\images\\down_grid.jpg",
                        group='board'
                    )
                    inst.bind(on_press=self.board_press)
                    inst.bind(on_release=self.board_release)
                    self.board.add_widget(inst)
                    black = not black

                    #adding blank spaces in image overlay
                    self.pieces.add_widget(Label())

        print(self.pieces.ids)


    def board_press(self, widget):
        print(self.virtualBoard)
        sizeOfGrid = list(widget.parent.size)
        print("Size of grid: ", sizeOfGrid)
        print("Size of screen: ", widget.parent.size)
        sizeOfGrid[0] -= 50
        sizeOfGrid[0] /= 8
        sizeOfGrid[1] -= 50
        sizeOfGrid[1] /= 8
        print("Size of grid: ", sizeOfGrid)
        print()
        print("Widget pos:  %d, %d" % (widget.pos[0], widget.pos[1]))
        x = gridXVals[round(widget.pos[0] / sizeOfGrid[0])]
        print("Raw number: ", widget.pos[0] / sizeOfGrid[0], " Rel coord: ", x)
        y = gridYVals[-(round(widget.pos[1] / sizeOfGrid[1]) + 1)]
        print("Raw number: ", widget.pos[1] / sizeOfGrid[1], " Rel coord: ", y)
        print("Clicked grid: %s, %s" % (x, y))
        self.virtualBoard.announce_piece(round(widget.pos[0] / sizeOfGrid[0]),
                                         8-(round(widget.pos[1] / sizeOfGrid[1])+1))

        if self.activePieceId is not None:
            idArr = self.activePieceId.split(',')
            toY = abs(7 - round(widget.pos[1] / sizeOfGrid[1]))
            toX = round(widget.pos[0] / sizeOfGrid[0])
            fromX = int(idArr[0])
            fromY = int(idArr[1])
            self.move_piece(fromX, fromY, toX, toY, widget)

    def move_piece(self, fromX, fromY, toX, toY, widget):
        print(self.pieces.children)
        if self.activePieceId is not None:
            for child in self.pieces.children:
                if child.id == self.activePieceId:
                    piece = child

            print("move is a jump ", (toX, toY) in self.possibleList)
            print(self.possibleList)
            if not (toX, toY) in self.possibleList and len(self.possibleList) == 0 and\
                    self.virtualBoard.check_move(fromX, fromY, toX, toY, self.activeTeam):

                self.virtualBoard.move_piece(fromX, fromY, toX, toY)
                piece.pos = widget.pos
                piece.id = str(toX) + ',' + str(toY)
                if self.activeTeam == "red" and toY == 7:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\redKing.png"

                elif self.activeTeam == "black" and toY == 0:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\blackKing.png"

                self.ids["center_text"].text = ("Moved the %s piece from %d%s to %d%s" % (self.activeTeam, fromX+1, gridYVals[fromY], toX+1, gridYVals[toY]))

                self.switchTeam()
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None


                #TODO Insert Check and execute Jumps
                self.possibleList = self.virtualBoard.check_jumps(self.activeTeam)

            #TODO execute jump
            elif (toX, toY) in self.possibleList:
                self.possibleList = []
                self.virtualBoard.execute_jump(fromX, fromY, toX, toY)

                piece.pos = widget.pos
                piece.id = str(toX) + ',' + str(toY)
                if self.activeTeam == "red" and toY == 7:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\redKing.png"

                elif self.activeTeam == "black" and toY == 0:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\blackKing.png"

                self.ids["center_text"].text = ("Jumped the %s piece from %d%s to %d%s" % (
                    self.activeTeam, fromX + 1, gridYVals[fromY], toX + 1, gridYVals[toY]))

                if toX > fromX:
                    middleX = toX - 1
                else:
                    middleX = toX + 1

                if toY > fromY:
                    middleY = toY - 1
                else:
                    middleY = toY + 1

                for child in self.pieces.children:
                    if child.id == str(middleX) + ',' + str(middleY):
                        child.opacity = 0
                        break

                self.switchTeam()
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None
                self.possibleList = self.virtualBoard.check_jumps(self.activeTeam)

            else:
                print("invalid move")
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None
                self.ids["center_text"].text = ("Invalid Move")

    def piece_press(self, widget):
        if self.activePieceId is None:
            print("Pressed piece at: ", widget.id)
            self.ids["center_text"].text = ("Pressed piece at: " + widget.id)
            self.activePieceId = widget.id
            widget.background_normal = ".\\assets\\images\\down_grid.jpg"

        else:
            if not (self.activePieceId == widget.id):
                print("Pressed piece at: ", widget.id)
                self.ids["center_text"].text = ("Pressed piece at: " + widget.id)
                for child in self.pieces.children:
                    if child.id == self.activePieceId:
                        self.reset_piece_picture(child)
                self.activePieceId = widget.id
                widget.background_normal = ".\\assets\\images\\down_grid.jpg"

            else:
                self.activePieceId = None
                self.ids["center_text"].text = ""
                self.reset_piece_picture(widget)

    def reset_piece_picture(self, widget):
        idArr = widget.id.split(',')
        x = int(idArr[0])
        y = int(idArr[1])

        if self.virtualBoard.get_team(x, y) == 'red':
            if self.virtualBoard.vBoard[y][x].king:
                widget.background_normal = ".\\assets\\images\\redKing.png"
            else:
                widget.background_normal = ".\\assets\\images\\redPawn.png"

        else:
            if self.virtualBoard.get_king(x, y):
                widget.background_normal = ".\\assets\\images\\blackKing.png"
            else:
                widget.background_normal = ".\\assets\\images\\blackPawn.png"

    def piece_release(self, widget):
        #self.activePieceId = None
        pass

    def board_release(self, widget):
        pass

    def switchTeam(self):
        if self.activeTeam == "red":
            self.activeTeam = "black"
        else:
            self.activeTeam = "red"


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
                if returns[0]:
                    coords = (returns[1], returns[2])
                    possibleList.append(coords)
                    print("found a jump from %d, %d to %d, %d" % (x, y, returns[1], returns[2]))
        if len(possibleList) == 0:
            print("no jumps found")
        return possibleList

    def check_jump(self, x, y, team):
        #TODO Write code to check for jumps across board
        #checking jump
        if self.vBoard[y][x] is not None:
            piece = self.vBoard[y][x]

            #if correct team (player ready to move)
            if piece.team == team:

                #check for jumps from target piece
                #check to see if adj to enemy piece
                withinRange = 0 < y + 2 < 8 and 0 < x + 2 < 8
                if team == "red":
                    withinRangeDown = 0 < y - 1 < 8
                    withinRangeUp = 0 < y + 1 < 8
                    withinRangeLeft = 0 < x + 1 < 8
                    withinRangeRight = 0 < x - 1 < 8

                    # target is up-left
                    if withinRangeUp and withinRangeLeft:
                        enemyUpLeft = self.vBoard[y + 1][x + 1] is not None and self.vBoard[y + 1][x + 1].team != team

                    else:
                        enemyUpLeft = False

                    # target is up-right
                    if withinRangeUp and withinRangeRight:
                        enemyUpRight = self.vBoard[y + 1][x - 1] is not None and self.vBoard[y + 1][x - 1].team != team

                    else:
                        enemyUpRight = False

                    if withinRangeDown and (withinRangeLeft or withinRangeRight):
                        if piece.king and not (enemyUpLeft or enemyUpRight):
                            # target is down-left
                            if withinRangeLeft:
                                enemyDownLeft = self.vBoard[y - 1][x + 1] is not None and self.vBoard[y - 1][
                                    x + 1].team != team
                            # target is down-right
                            else:
                                enemyDownRight = self.vBoard[y - 1][x - 1] is not None and self.vBoard[y - 1][
                                    x - 1].team != team

                        else:
                            enemyDownLeft = enemyDownRight = False
                    else:
                        enemyDownLeft = enemyDownRight = False

                #black
                else:
                    withinRangeUp = 0 < y - 1 < 8
                    withinRangeDown = 0 < y + 1 < 8
                    withinRangeLeft = 0 < x + 1 < 8
                    withinRangeRight = 0 < x - 1 < 8
                    # target is up-left
                    if withinRangeUp and withinRangeLeft:
                        enemyUpLeft = self.vBoard[y - 1][x + 1] is not None and self.vBoard[y - 1][x + 1].team != team

                    else:
                        enemyUpLeft = False

                    # target is up-right
                    if withinRangeUp and withinRangeRight:
                        enemyUpRight = self.vBoard[y - 1][x - 1] is not None and self.vBoard[y - 1][x - 1].team != team

                    else:
                        enemyUpRight = False

                    if withinRangeDown and (withinRangeLeft or withinRangeRight):
                        if piece.king and not (enemyUpLeft or enemyUpRight):
                            # target is down-left
                            if withinRangeLeft:
                                enemyDownLeft = self.vBoard[y + 1][x + 1] is not None and self.vBoard[y + 1][
                                    x + 1].team != team
                            # target is down-right
                            else:
                                enemyDownRight = self.vBoard[y + 1][x - 1] is not None and self.vBoard[y + 1][
                                    x - 1].team != team

                        else:
                            enemyDownLeft = enemyDownRight = False
                    else:
                        enemyDownLeft = enemyDownRight = False

                #if enemy exists
                if enemyUpLeft or enemyUpRight or enemyDownLeft or enemyDownRight:
                    print("\nJump function:\nUpLeft: ", enemyUpLeft, "\nUpRight: ", enemyUpRight, "\nDownLeft: ",
                          enemyDownLeft, "\nDownRight: ", enemyDownRight)
                    #TODO Optimize boolean checks, reduce to functions probably
                    #check if the following tile is empty

                    if team == "red":
                        withinRangeDown = 0 < y - 2 < 8
                        withinRangeUp = 0 < y + 2 < 8
                        withinRangeLeft = 0 < x + 2 < 8
                        withinRangeRight = 0 < x - 2 < 8
                        if enemyUpLeft:
                            if withinRangeUp and withinRangeLeft:
                                if self.vBoard[y+2][x+2] is None:
                                    return True, x+2, y+2
                            else:
                                return [False]

                        if enemyUpRight:
                            if withinRangeUp and withinRangeRight:
                                if self.vBoard[y+2][x-2] is None:
                                    return True, x-2, y+2
                            else:
                                return [False]

                        if enemyDownLeft:
                            if withinRangeDown and withinRangeLeft:
                                if self.vBoard[y-2][x+2] is None:
                                    return True, x+2, y-2
                            else:
                                return [False]

                        if enemyDownRight:
                            if withinRangeDown and withinRangeRight:
                                if self.vBoard[y-2][x-2] is None:
                                    return True, x-2, y-2
                            else:
                                return [False]

                    #black
                    else:
                        print("black piece has enemies")
                        withinRangeUp = 0 < y - 2 < 8
                        withinRangeDown = 0 < y + 2 < 8
                        withinRangeLeft = 0 < x + 2 < 8
                        withinRangeRight = 0 < x - 2 < 8
                        if enemyUpLeft:
                            if withinRangeUp and withinRangeLeft:
                                if self.vBoard[y-2][x+2] is None:
                                    return True, x+2, y-2
                                else:
                                    print(y-2, x+2, " is occupied")
                            else:
                                return [False]

                        if enemyUpRight:
                            if withinRangeUp and withinRangeRight:
                                if self.vBoard[y-2][x-2] is None:
                                    print("valid jump")
                                    return True, x-2, y-2
                                else:
                                    print(y-2, x-2, " is occupied")
                            else:
                                return [False]

                        if enemyDownLeft:
                            if withinRangeDown and withinRangeLeft:
                                if self.vBoard[y+2][x+2] is None:
                                    return True, x+2, y+2
                            else:
                                return [False]

                        if enemyDownRight:
                            if withinRangeDown and withinRangeRight:
                                if self.vBoard[y+2][x-2] is None:
                                    return True, x-2, y+2
                            else:
                                return [False]

        return [False]


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

        self.vBoard[middleY][middleY] = None

        self.vBoard[toY][toX] = piece
        self.vBoard[fromY][fromX] = None
        pass

    def announce_piece(self, x, y):
        piece = self.vBoard[int(x)][int(y)]
        if piece is not None:
            print(piece.team, " piece at %d, %d" % (x, y), "\n")
        else:
            print("No piece at %d, %d" % (x, y), "\n")

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
                    toReturn += ' '
            toReturn += '\n'
        return toReturn



class CheckersApp(App):
    def build(self):
        Window.size = (maxSizeWidth, maxSizeWidth*11/10)
        self.screenSlider = None
        self.screenSize = 0
        self.screen = CheckerScreen()
        print(self.screen.ids)
        return self.screen

    def home_menu(self):
        scope = self.screen.ids['home']
        box = BoxLayout(orientation='horizontal')
        toAdd = Button(text="Start Human Game")
        toAdd.bind(on_release=self.screen.human_game_button)
        box.add_widget(toAdd)

        toAdd = Button(text="Destroy Game")
        toAdd.bind(on_release=self.screen.del_board)
        box.add_widget(toAdd)
        scope.add_widget(box)
        pass

    def game_menu(self):
        scope = self.screen.ids['game']
        box = BoxLayout(orientation='horizontal')

        self.screenSlider = Slider(min=minSizeWidth, max=maxSizeWidth, value=Window.size[0])
        box.add_widget(self.screenSlider)
        if self.screen.activeGame:
            self.screenSlider.set_disabled(True)

        butt1 = Button(text="Adjust screen resolution")
        butt1.bind(on_release=self.resizeWindow)

        box.add_widget(butt1)

        butt2 = Button(text="Select AI")
        butt2.bind(on_release=self.notImplmented)
        box.add_widget(butt2)


        gary = Button(text="Gary",
                      background_normal="gary.png")
        gary.bind(on_release=self.gary)
        box.add_widget(gary)

        scope.add_widget(box)

    def resizeWindow(self, widget):
        windowSize = (self.screenSlider.value, self.screenSlider.value*11/10)
        Window.size = windowSize

    def notImplmented(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popGary = Popup(title='This not implemented yet', size_hint=(.5, .5), content=Label(text='Stay tuned for checkpoint 3', size=(100, 100)))
        popGary.open()

    def gary(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popGary = Popup(title='This is Gary', size_hint=(.5, .5), content=Image(source="gary.png", size=(100, 100)))
        popGary.open()

'''
def children(branch, depth, alpha, beta):
    global tree
    global root
    global pruned
    i = 0
    for child in branch:
        if type(child) is list:
            (nalpha, nbeta) = children(child, depth + 1, alpha, beta)
            if depth % 2 == 1:
                beta = nalpha if nalpha < beta else beta
            else:
                alpha = nbeta if nbeta > alpha else alpha
            branch[i] = alpha if depth % 2 == 0 else beta
            i += 1
        else:
            if depth % 2 == 0 and alpha < child:
                alpha = child
            if depth % 2 == 1 and beta > child:
                beta = child
            if alpha >= beta:
                pruned += 1
                break
    if depth == root:
        tree = alpha if root == 0 else beta
    return (alpha, beta)

def alphabeta(in_tree=tree, start=root, upper=-15, lower=15):
    global tree
    global pruned
    global root

    (alpha, beta) = children(tree, start, upper, lower)

    if __name__ == "__main__":
        print ("(alpha, beta): ", alpha, beta)
        print ("Result: ", tree)
        print ("Times pruned: ", pruned)

    return (alpha, beta, tree, pruned)
'''

if __name__ == '__main__':
    Builder.load_file(pathToKvlang)
    app = CheckersApp()
    app.run()


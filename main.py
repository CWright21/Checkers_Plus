from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.lang import Builder
from kivy.clock import Clock
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
from gametree import GameTree
from gametree import GameNode
from alphabeta import AlphaBeta
from virtualboard import VirtualBoard
from virtualboard import Piece
from gametree import Coord

pathToKvlang = ".\\assets\\kvlang\\Checkers.kv"
pathToBlackGrid = ".\\assets\\images\\black_grid.jpg"
pathToWhiteGrid = ".\\assets\\images\\white_grid.jpg"
boardSize = 8
gridXVals = [1, 2, 3, 4, 5, 6, 7, 8]
gridYVals = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

maxSizeWidth = 1000
minSizeWidth = 650
windowSize = (650, 715)


class CheckerScreen(Widget):
    tabMenu = ObjectProperty(None)

    def __init__(self):
        super(CheckerScreen, self).__init__()
        self.activeGame = False
        self.board = None
        self.aiDiff = 0

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
        self.virtualBoard.set_ai_difficulty(self.aiDiff)
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
                    gridId = str(c) + ',' + str(r)
                    print(gridId)
                    inst = ToggleButton(
                        background_normal=".\\assets\\images\\black_grid.jpg",
                        background_down=".\\assets\\images\\down_grid.jpg",
                        group='board',
                        id=gridId
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
                        if self.virtualBoard.a_bDiff > 0:
                            toAdd.disabled = True
                            toAdd.background_disabled_normal = ".\\assets\\images\\redPawn.png"
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
                    gridId = str(c) + ',' + str(r)
                    print(gridId)
                    inst = ToggleButton(
                        background_normal=".\\assets\\images\\white_grid.jpg",
                        background_down=".\\assets\\images\\down_grid.jpg",
                        group='board',
                        id=gridId
                    )
                    inst.bind(on_press=self.board_press)
                    inst.bind(on_release=self.board_release)
                    self.board.add_widget(inst)
                    black = not black

                    #adding blank spaces in image overlay
                    self.pieces.add_widget(Label())

        print(self.pieces.ids)
        if self.aiDiff > 0:
            pass

    def board_press(self, widget):
        print(self.virtualBoard)
        sizeOfGrid = list(widget.parent.size)
        print("Size of grid: ", sizeOfGrid)
        print("Size of screen: ", widget.parent.size)
        print("id: ", widget.id)
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
            self.move_piece_human(fromX, fromY, toX, toY, widget)

    def move_piece_ai(self, widget):
        if self.activeTeam == 'red':
            move = self.virtualBoard.do_ai_move()
            self.move_piece_ai_helper(move.frm.x, move.frm.y, move.to.x, move.to.y)
            possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
            self.possibleList = []
            for move in possibleJumpMoves:
                self.possibleList.append(move.to)
        else:
            print('not ai turn')

    def move_piece_ai_helper(self, fromX, fromY, toX, toY):
        id = (str(toY) + ',' + str(toX))
        fromId = (str(fromX) + ',' + str(fromY))
        print(id)
        for grid in self.board.children:
            if grid.id == id:
                print(grid.pos)
                pos = grid.pos
                print("pos after", pos)
        self.activePieceId = str(fromX)+','+str(fromY)
        '''
        for child in self.pieces.children:
            print(child.id)
            if child.id == str(fromX)+','+str(fromY):
                self.activePieceId = child.id
        '''
        #self.force_move_piece(fromX, fromY, toX, toY, widget, fromId)

        for child in self.pieces.children:
            print('active', self.activePieceId, 'child', child.id)
            if child.id == self.activePieceId:
                piece = child
                break

        if self.virtualBoard.get_team(toX, toY) == 'red' and toY == 7:
            self.virtualBoard.king_piece(toX, toY)
            print("ai king")
            piece.background_disabled_normal = ".\\assets\\images\\redKing.png"

        elif self.virtualBoard.get_team(toX, toY) == "black" and toY == 0:
            self.virtualBoard.king_piece(toX, toY)
            piece.background_disabled_normal = ".\\assets\\images\\blackKing.png"

        print('pos before', piece.pos)
        piece.pos = pos
        piece.id = (str(toX) + ',' + str(toY))
        self.switchTeam()
        self.reset_piece_picture(piece)
        self.activePieceId = None
        temp = self.virtualBoard.check_for_game_end()
        if temp[0]:
            self.ids["center_text"].text = ("%s won!!" % (temp[1]))
            self.del_board(None)

        if abs(fromX-toX) == 2 and abs(fromY-toY) == 2:
            if toX > fromX:
                middleX = toX - 1
            else:
                middleX = toX + 1

            if toY > fromY:
                middleY = toY - 1
            else:
                middleY = toY + 1

            for child in self.pieces.children:
                print(child.id, str(middleX) + ',' + str(middleY), " | ", end='')
                if child.id == str(middleX) + ',' + str(middleY):
                    print("found child")
                    print(piece.id, piece.opacity)
                    child.opacity = .5
                    child.pos = (0, 0)
                    child.id = '9,9'
                    child.disabled = True
                    break

        pass

    def force_move_piece(self, fromX, fromY, toX, toY, widget, id):
        pass

    def move_piece_human(self, fromX, fromY, toX, toY, widget):
        print(self.pieces.children)
        if self.activePieceId is not None:
            for child in self.pieces.children:
                if child.id == self.activePieceId:
                    piece = child

            print("pos before", piece.pos)

            isValidJump = False
            for coords in self.possibleList:
                if Coord(toX, toY) == (coords):
                    isValidJump = True
            print("move is a jump ", isValidJump)
            print(self.possibleList)
            print(self.virtualBoard.check_move(fromX, fromY, toX, toY, self.activeTeam))
            if len(self.possibleList) == 0 and self.virtualBoard.check_move(fromX, fromY, toX, toY, self.activeTeam):

                self.virtualBoard.move_piece(fromX, fromY, toX, toY)
                piece.pos = widget.pos
                print("pos after move", piece.pos)
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
                temp = self.virtualBoard.check_for_game_end()
                if temp[0]:
                    self.ids["center_text"].text = ("%s won!!" % (temp[1]))
                    self.del_board(None)
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)

            # TODO maybe double jump
            elif isValidJump and (abs(fromX-toX) == 2 or abs(fromY-toY) == 2):
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
                    print(child.id, str(middleX) + ',' + str(middleY), " | ", end='')
                    if child.id == str(middleX) + ',' + str(middleY):
                        print("found child")
                        print(piece.id, piece.opacity)
                        child.opacity = .5
                        child.pos = (0,0)
                        child.id = '9,9'
                        child.disabled = True
                        break
                print()

                self.switchTeam()
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None
                temp = self.virtualBoard.check_for_game_end()
                if temp[0]:
                    self.ids["center_text"].text = ("%s won!!" % (temp[1]))
                    self.del_board(None)
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)
                if self.aiDiff > 0 and self.activeTeam == 'red':
                    pass

            else:
                print("invalid move", end = '')
                infotext = "invalid move"
                if len(self.possibleList) > 0:
                    print()
                    print('jumps:', self.possibleList[0])
                    print("there are valid jumps")
                    infotext += ", there is/are valid jump(s)"
                else:
                    print("make sure it is your turn")
                    infotext += ", make sure it is your turn"
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None
                self.ids["center_text"].text = (infotext)

    def piece_press(self, widget):
        if self.activePieceId is None:
            print("Pressed piece at: ", widget.id)
            print(self.virtualBoard.announce_piece(int(widget.id[2:]), int(widget.id[0:1])))
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


class CheckersApp(App):
    def build(self):
        Window.size = (maxSizeWidth, maxSizeWidth*11/10)
        self.screenSlider = None
        self.screenSize = 0
        self.screen = CheckerScreen()
        print(self.screen.ids)
        return self.screen

    # TODO change button text for start game
    def home_menu(self):
        scope = self.screen.ids['home']
        box = BoxLayout(orientation='horizontal')
        toAdd = Button(text="Start Human Game")
        toAdd.bind(on_release=self.screen.human_game_button)
        box.add_widget(toAdd)

        toAdd = Button(text="Destroy Game")
        toAdd.bind(on_release=self.screen.del_board)
        box.add_widget(toAdd)

        toAdd = Button(text='Do Next Ai Move')
        toAdd.bind(on_release=self.screen.move_piece_ai)
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
        butt2.bind(on_press=self.pickAI)
        box.add_widget(butt2)


        gary = Button(text="Gary",
                      background_normal="gary.png")
        gary.bind(on_release=self.gary)
        box.add_widget(gary)

        scope.add_widget(box)

    def resizeWindow(self, widget):
        windowSize = (self.screenSlider.value, self.screenSlider.value*11/10)
        Window.size = windowSize

    def pickAI(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popButtonLayout = BoxLayout(orientation='vertical')
        buttonToAdd = ToggleButton(text="Easy", id='easy', group='aiDiff')
        if self.screen.aiDiff == 1:
            buttonToAdd.state = 'down'
        buttonToAdd.bind(on_press=self.aiSelect)
        popButtonLayout.add_widget(buttonToAdd)

        buttonToAdd = ToggleButton(text="Medium", id='med', group='aiDiff')
        if self.screen.aiDiff == 2:
            buttonToAdd.state = 'down'
        buttonToAdd.bind(on_press=self.aiSelect)
        popButtonLayout.add_widget(buttonToAdd)

        buttonToAdd = ToggleButton(text="Hard", id='hard', group='aiDiff')
        if self.screen.aiDiff == 3:
            buttonToAdd.state = 'down'
        buttonToAdd.bind(on_press=self.aiSelect)
        popButtonLayout.add_widget(buttonToAdd)

        popAI= Popup(title='Pick an AI', size_hint=(.5, .5), content=(popButtonLayout))
        popAI.open()

    def gary(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popGary = Popup(title='This is Gary', size_hint=(.5, .5), content=Image(source="gary.png", size=(100, 100)))
        popGary.open()

    def aiSelect(self, widget):
        if widget.id == 'easy':
            self.screen.aiDiff = 1
        elif widget.id == 'med':
            self.screen.aiDiff = 2
        elif widget.id == 'hard':
            self.screen.aiDiff = 5
        elif widget.id == 'none':
            self.screen.aiDiff = -1
        print(self.screen.aiDiff)

# TODO add options for AI only game?

# TODO refine codebase further to seperate code more effectivly

if __name__ == '__main__':
    Builder.load_file(pathToKvlang)
    app = CheckersApp()
    app.run()


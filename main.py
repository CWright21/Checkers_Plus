from kivy.config import Config
Config.set('graphics', 'resizable', 0)

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
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
sizes = [(1500, 1650), (1000, 1100), (750, 825), (500, 550)]
windowSize = (500, 550)
maxSizeWidth = 1000
minSizeWidth = 650



class CheckerScreen(Widget):
    tabMenu = ObjectProperty(None)

    def __init__(self):
        super(CheckerScreen, self).__init__()
        self.virtualBoard = VirtualBoard()
        self.board = self.ids.board
        self.pieces = self.ids.pieces

        black = True
        for c in range(8):
            for r in range(8):
                if c > 0 and r == 0:
                    black = not black

                if black:
                    inst = ToggleButton(
                        background_normal=".\\assets\\images\\black_grid.jpg",
                        background_down=".\\assets\\images\\down_grid.jpg",
                        group='board'
                    )
                    inst.bind(on_press=self.board_press)
                    inst.bind(on_release=self.board_release)
                    self.board.add_widget(inst)
                    black = not black

                    #adding piece image overlay
                    if c < 3:
                        self.pieces.add_widget(Image(source=".\\assets\\images\\redPawn.png"))
                        # adding piece to virtual board
                        self.virtualBoard.add_piece_to_board(c, r, Piece('red'))

                    elif c >= 5:
                        self.pieces.add_widget(Image(source=".\\assets\\images\\blackPawn.png"))
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

    def board_press(self, widget):
        sizeOfGrid = list(widget.parent.size)
        sizeOfGrid[0] /= 8
        sizeOfGrid[1] /= 8
        print("Widget pos:  %d, %d" % (widget.pos[0], widget.pos[1]))
        x = gridXVals[round(widget.pos[0] / sizeOfGrid[0])]
        y = gridYVals[-(round(widget.pos[1] / sizeOfGrid[1]) + 1)]
        print("Clicked grid: %s, %s" % (x, y))
        self.virtualBoard.announce_piece(round(widget.pos[0] / sizeOfGrid[0]),
                                         8-(round(widget.pos[1] / sizeOfGrid[1])+1))


    def board_release(self, widget):
        pass


class Piece:
    def __init__(self, team):
        self.team = team
        self.king = False

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
        self.vBoard[y][x] = piece

    def move_piece(self, fromX, fromY, toX, toY):
        piece = None
        piece = self.vBoard[fromY][fromX]
        self.vBoard[fromY][fromX] = None
        self.vBoard[toY][toX] = piece

    def check_move(self, fromX, fromY, toX, toY, team):
        # is piece at starting coords
        isAtStart = self.vBoard[fromY][fromX] is not None

        # is there a piece aat ending coords
        endOpen = self.vBoard[toY][toX] is None

        # is the piece yours
        correctTeam = self.vBoard[fromY][fromX].team == team

        # is valid direction to move (x +/- 1, y + 1)
        validPawnMove = (fromY == toY+1 and toX+1 == fromX) or \
        (fromY == toY-1 and toX+1 == fromX)

        # if king and valid king move (x +/- 1, y - 1)
        validKingMove = self.vBoard[fromY][fromX].king and \
        (fromY == toY + 1 and toX - 1 == fromX) or \
        (fromY == toY - 1 and toX - 1 == fromX)

        return isAtStart and endOpen and correctTeam and (validPawnMove or validKingMove)

    def check_for_jumps(self):
        pass

    def announce_piece(self, x, y):
        piece = self.vBoard[int(x)][int(y)]
        if piece is not None:
            print(piece.team, " piece at %d, %d" % (x, y), "\n")
        else:
            print("No piece at %d, %d" % (x, y), "\n")

class CheckersApp(App):
    def build(self):
        Window.size = (minSizeWidth, minSizeWidth*11/10)
        self.screenSlider = None
        self.screenSize = 0
        self.screen = CheckerScreen()
        print(self.screen.ids)
        return self.screen

    def home_menu(self):
        scope = self.screen.ids['home']
        box = BoxLayout(orientation='horizontal')
        box.add_widget(Button(text="PlaceHolder home menu button"))
        box.add_widget(Button(text="Another Placeholder"))
        scope.add_widget(box)
        pass

    def game_menu(self):
        scope = self.screen.ids['game']
        box = BoxLayout(orientation='horizontal')

        self.screenSlider = Slider(min=minSizeWidth, max=maxSizeWidth, value=minSizeWidth)
        box.add_widget(self.screenSlider)

        butt1 = Button(text="Adjust screen resolution")
        butt1.bind(on_release=self.resizeWindow)

        box.add_widget(butt1)
        box.add_widget(Button(text="Yet Another Placeholder"))

        gary = Button(text="Gary",
                      background_normal="gary.png")
        gary.bind(on_release=self.gary)
        box.add_widget(gary)

        scope.add_widget(box)

    def resizeWindow(self, widget):
        self.screenSize += 1
        if self.screenSize >= len(sizes):
            self.screenSize = 0
        Window.size = sizes[self.screenSize]

        windowSize = (self.screenSlider.value, self.screenSlider.value*11/10)
        Window.size = windowSize

    def gary(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popGary = Popup(title='This is Gary', size_hint=(.5, .5), content=Image(source="gary.png", size=(100, 100)))
        popGary.open()

if __name__ == '__main__':
    Builder.load_file(pathToKvlang)
    app = CheckersApp()
    app.run()


from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
# Force input to mouse, required before other imports, prevents multiple pointing devices inputing simultainiously

# Start Imports

import time
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
from virtualboard import VirtualBoard
from virtualboard import Piece
from gametree import Coord
import os
from learning import LearningModel          # Need in memory for loading files using pickle
from learning import TransitionTable        # Need in memory for loading files using pickle
from learning import TransitionEntry        # Need in memory for loading files using pickle
from kivy.uix.textinput import TextInput

# End Imports

pathToKvlang = ".\\assets\\kvlang\\Checkers.kv"       # Path to kvlang file
gridXVals = [1, 2, 3, 4, 5, 6, 7, 8]                  # Global names of grid coords, for ease of editing
gridYVals = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # Global names of grid coords, for ease of editing

maxSizeWidth = 1000                                   # Global max screen width
minSizeWidth = 650                                    # Global min screen width


class CheckerScreen(Widget):
    tabMenu = ObjectProperty(None)                    # tabMenu Defined in kvlang

    '''
        pre: None
        post: Screen is initialized
        desc: Constructor for screen
    '''
    def __init__(self):
        super(CheckerScreen, self).__init__()
        self.activeGame = False                       # Activegame if checkers game is in progress
        self.board = None                             # Board contains the checkerboard buttons
        self.aiDiff = 0                               # Ai difficulty


    '''
        pre: screen is initialized
        post: board is generated on screen
        desc: button helper that allows for the initialization of the board by kivy button. 
    '''
    def generate_game_button(self, widget):
        self.init_board()

    '''
        pre: Board is Initialized
        post: Board is deleted
        desc: Deletes board from screen and memory
    '''
    def del_board(self, widget):
        if self.board is not None:
            if self.aiDiff == -2:                  # if learning ai
                self.virtualBoard.learning.save()  # save but without Reinforce
            self.board.clear_widgets()             # del
            self.pieces.clear_widgets()            # del
            self.ids['board'].opacity = 0          # hide board
            self.activeGame = False                # No active

    '''
        pre: None
        post: Board is initialized/constructed
        desc: creates the board given a constructed screen
    '''
    def init_board(self):
        self.possibleList = []                                 # List of possible moves
        self.ids['board'].opacity = 1                          # Show board
        self.ids['center_text'].color = 0, 0, 0, 1             # Alert text color is black
        self.ids['center_text'].text = ''                      # Alert text is blank
        self.virtualBoard = VirtualBoard()
        self.board = self.ids.board                            # assign hard ref to board
        self.board.clear_widgets()                             # ensure board is clear (should be already)
        self.virtualBoard.set_ai_difficulty(self.aiDiff)
        self.pieces = self.ids.pieces
        self.pieces.clear_widgets()                            # ensure no pieces (should be already)

        if self.aiDiff == -2:
            self.virtualBoard.addLearningAi(self.learningAi)

        self.activeGame = True
        self.activePieceId = None
        self.activeTeam = "red"

        # Start Generate Grid
        # Go through grid layout alternating black and white grid colors
        # adding pieces on the correct grid squares as needed
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

                    # adding piece image button overlay
                    if c < 3:
                        toAdd = Button(id=str(r) + "," + str(c),
                                       background_normal=".\\assets\\images\\bluePawn.png")
                        toAdd.bind(on_press=self.piece_press)
                        toAdd.bind(on_release=self.piece_release)

                        # if ai game disable interact
                        if self.virtualBoard.a_bDiff > 0:
                            toAdd.disabled = True
                            toAdd.background_disabled_normal = ".\\assets\\images\\bluePawn.png"
                        self.pieces.add_widget(toAdd)

                        # adding piece to virtual board
                        self.virtualBoard.add_piece_to_board(c, r, Piece('red'))

                    elif c >= 5:
                        toAdd = Button(background_normal=".\\assets\\images\\whitePawn.png",
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

        # End generate Grid

    '''
        pre: Board is initialized
        post: If active piece , then call move piece method
        desc: If there is an active piece, ie pressed piece, then call the move piece method and check for game end.
    '''
    def board_press(self, widget):
        idArr2 = widget.id.split(',')
        y = int(idArr2[0])
        x = int(idArr2[1])
        print(self.virtualBoard)
        self.virtualBoard.announce_piece(x, y)

        if self.activePieceId is not None:
            idArr = self.activePieceId.split(',')
            fromX = int(idArr[0])
            fromY = int(idArr[1])
            self.move_piece_human(fromX, fromY, x, y, widget)
            if not self.virtualBoard.check_for_game_end()[0]:
                self.move_piece_ai(widget)

    '''
        pre: Board is initialized
        post: Ai moved a piece
        desc: call respective AI move methods after ensuring they are the active team, hard coded active team 
            verification due to gui being for human vs. human or human vs. AI.
    '''
    def move_piece_ai(self, widget):
        if self.aiDiff > 0:
            if self.activeTeam == 'red':
                move = self.virtualBoard.do_ai_move()
                self.move_piece_ai_helper(move.frm.x, move.frm.y, move.to.x, move.to.y)

                # generate possible jumps for next move
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)
            else:
                print('not ai turn')

        elif self.aiDiff == -2:
            if self.activeTeam == 'red':
                move = self.virtualBoard.do_ai_move()
                self.move_piece_ai_helper(move.frm.x, move.frm.y, move.to.x, move.to.y)

                # generate possible jumps for next move
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)
            else:
                print('not ai turn')

    '''
        pre: move_piece_ai called
        post: piece fromX, fromY is moved toX, toY
        desc: Helper method for move_piece_ai
    '''
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

        for child in self.pieces.children:
            print('active', self.activePieceId, 'child', child.id)
            if child.id == self.activePieceId:
                piece = child
                break

        # Start king if move to back
        if self.virtualBoard.get_team(toX, toY) == 'red' and toY == 7:
            self.virtualBoard.king_piece(toX, toY)
            print("ai king")
            piece.background_disabled_normal = ".\\assets\\images\\blueKing.png"

        elif self.virtualBoard.get_team(toX, toY) == "black" and toY == 0:
            self.virtualBoard.king_piece(toX, toY)
            piece.background_disabled_normal = ".\\assets\\images\\whiteKing.png"
        # End king

        piece.pos = pos
        piece.id = (str(toX) + ',' + str(toY))
        self.switch_team()
        self.reset_piece_picture(piece)
        self.activePieceId = None
        self.ids["center_text"].text = ("The AI moved the blue piece at %d%s to %d%s" % (
            fromX + 1, gridYVals[fromY], toX + 1, gridYVals[toY]))
        temp = self.virtualBoard.check_for_game_end()
        if temp[0]:
            self.ids["center_text"].text = ("%s won!!" % (temp[1]))
            self.del_board(None)

        # Start jump handle
        if abs(fromX-toX) == 2 and abs(fromY-toY) == 2:
            if toX > fromX:
                middleX = toX - 1
            else:
                middleX = toX + 1

            if toY > fromY:
                middleY = toY - 1
            else:
                middleY = toY + 1

            # weak de-ref middle child
            for child in self.pieces.children:
                print(child.id, str(middleX) + ',' + str(middleY), " | ", end='')
                if child.id == str(middleX) + ',' + str(middleY):
                    print("found child")
                    print(piece.id, piece.opacity)
                    child.opacity = 0
                    child.pos = (0, 0)
                    child.id = '9,9'
                    child.disabled = True
                    break

            # alert msg
            if self.activeTeam == 'red':
                temp = 'blue'
            else:
                temp = 'white'
            self.ids["center_text"].text = ("The AI jumped the %s piece at %d%s to %d%s" % (
                temp, fromX + 1, gridYVals[fromY], toX + 1, gridYVals[toY]))

        # End jump handle

    '''
        pre: None
        post: None
        desc: Unimplemented, unneeded
    '''
    """
    def force_move_piece(self, fromX, fromY, toX, toY, widget, id):
        pass
    """

    '''
        pre: Board is initialized
        post: if valid move, piece moved fromX, fromY to toX, toY
        desc: 
    '''
    def move_piece_human(self, fromX, fromY, toX, toY, widget):

        # Start normal move
        if self.activePieceId is not None:
            # find active piece
            for child in self.pieces.children:
                if child.id == self.activePieceId:
                    piece = child


            isValidJump = False
            for coords in self.possibleList:
                if Coord(toX, toY) == (coords):
                    isValidJump = True

            if len(self.possibleList) == 0 and self.virtualBoard.check_move(fromX, fromY, toX, toY, self.activeTeam):

                # move piece in virtual board and change pos and id
                self.virtualBoard.move_piece(fromX, fromY, toX, toY)
                piece.pos = widget.pos
                piece.id = str(toX) + ',' + str(toY)

                # Start king if move to back
                if self.activeTeam == "red" and toY == 7:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\blueKing.png"

                elif self.activeTeam == "black" and toY == 0:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\whiteKing.png"
                # End king

                # Alert msg
                if self.activeTeam == 'red':
                    temp = 'blue'
                else:
                    temp = 'white'
                self.ids["center_text"].text = ("Moved the %s piece from %d%s to %d%s" % (temp, fromX+1, gridYVals[fromY], toX+1, gridYVals[toY]))

                self.switch_team()
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None

                # game end?
                temp = self.virtualBoard.check_for_game_end()
                if temp[0]:
                    self.ids["center_text"].text = ("%s won!!" % (temp[1]))
                    self.del_board(None)
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)

                # generate next moves
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)

            # End normal move

            # Start jump
            elif isValidJump and (abs(fromX-toX) == 2 or abs(fromY-toY) == 2):
                self.possibleList = []

                # move piece in virtual board and change pos and id
                self.virtualBoard.execute_jump(fromX, fromY, toX, toY)
                piece.pos = widget.pos
                piece.id = str(toX) + ',' + str(toY)

                # Start king if move to back
                if self.activeTeam == "red" and toY == 7:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\blueKing.png"

                elif self.activeTeam == "black" and toY == 0:
                    self.virtualBoard.king_piece(toX, toY)
                    piece.background_normal = ".\\assets\\images\\whiteKing.png"
                # end king

                # alert msg
                if self.activeTeam == 'red':
                    temp = 'blue'
                else:
                    temp = 'white'
                self.ids["center_text"].text = ("Jumped the %s piece from %d%s to %d%s" % (
                    temp, fromX + 1, gridYVals[fromY], toX + 1, gridYVals[toY]))

                # Start handle jumped piece
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
                        child.opacity = 0
                        child.pos = (0, 0)
                        child.id = '9,9'
                        child.disabled = True
                        break
                # End handle jumped piece

                self.switch_team()
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None

                # game end?
                temp = self.virtualBoard.check_for_game_end()

                # alert msg
                if temp[0]:
                    self.ids["center_text"].text = ("%s won!!" % (temp[1]))
                    self.del_board(None)
                possibleJumpMoves = self.virtualBoard.check_jumps(self.activeTeam)
                self.possibleList = []
                for move in possibleJumpMoves:
                    self.possibleList.append(move.to)
                if self.aiDiff > 0 and self.activeTeam == 'red':
                    pass

            # end jump

            # Start Bad move
            else:
                print("invalid move", end = '')
                infotext = "invalid move"
                if len(self.possibleList) > 0:
                    print()
                    print('jumps:', self.possibleList[0])
                    print("there are valid jumps")
                    infotext += ", there is/are valid jump(s)"
                else:
                    print("it might not be your turn")
                    infotext += ", it might not be your turn"
                widget.state = 'normal'
                self.reset_piece_picture(piece)
                self.activePieceId = None
                self.ids["center_text"].text = (infotext)

            # End Bad Move
    '''
        pre: None
        post: active piece set
        desc: handle piece press, set active piece and alert new piece
    '''
    def piece_press(self, widget):
        if self.activePieceId is None:
            idArr = widget.id.split(',')
            x = int(idArr[0])
            y = int(idArr[1])
            print("Pressed piece at: ", widget.id)
            print(self.virtualBoard.announce_piece(x, y))
            self.ids["center_text"].text = ("Pressed piece at: " + widget.id)
            self.activePieceId = widget.id
            self.piece_down(widget)

        else:
            if not (self.activePieceId == widget.id):
                print("Pressed piece at: ", widget.id)
                self.ids["center_text"].text = ("Pressed piece at: " + widget.id)
                for child in self.pieces.children:
                    if child.id == self.activePieceId:
                        self.reset_piece_picture(child)
                self.activePieceId = widget.id
                self.piece_down(widget)

            else:
                self.activePieceId = None
                self.ids["center_text"].text = ""
                self.reset_piece_picture(widget)

    '''
        pre: None
        post: widget picture reset to un pressed ver.
        desc: call on piece to reset its picture to initial state
    '''
    def reset_piece_picture(self, widget):
        idArr = widget.id.split(',')
        x = int(idArr[0])
        y = int(idArr[1])

        if self.virtualBoard.get_team(x, y) == 'red':
            if self.virtualBoard.vBoard[y][x].king:
                widget.background_normal = ".\\assets\\images\\blueKing.png"
            else:
                widget.background_normal = ".\\assets\\images\\bluePawn.png"

        else:
            if self.virtualBoard.get_king(x, y):
                widget.background_normal = ".\\assets\\images\\whiteKing.png"
            else:
                widget.background_normal = ".\\assets\\images\\whitePawn.png"

    '''
        pre: None
        post: set picture to down ver.
        desc: sets piece picture to down ver.
    '''
    def piece_down(self, widget):
        idArr = widget.id.split(',')
        x = int(idArr[0])
        y = int(idArr[1])
        if self.virtualBoard.get_team(x, y) == 'red':
            if self.virtualBoard.get_king(x, y):
                widget.background_normal = ".\\assets\\images\\blueKingDown.png"
            else:
                widget.background_normal = ".\\assets\\images\\bluePawnDown.png"

        elif self.virtualBoard.get_team(x, y) == 'black':
            if self.virtualBoard.get_king(x, y):
                widget.background_normal = ".\\assets\\images\\whiteKingDown.png"
            else:
                widget.background_normal = ".\\assets\\images\\whitePawnDown.png"

    '''
        pre: None
        post: None
        desc: Unused
    '''
    def piece_release(self, widget):
        pass

    '''
        pre: None
        post: None
        desc: Unused
    '''
    def board_release(self, widget):
        pass

    '''
        pre: None
        post: Toggle betwen active team
        desc: Switches teams
    '''
    def switch_team(self):
        if self.activeTeam == "red":
            self.activeTeam = "black"
        else:
            self.activeTeam = "red"


class CheckersApp(App):
    def build(self):
        Window.size = (maxSizeWidth, maxSizeWidth*11/10)
        self.screenSlider = None
        self.screenSize = 0
        self.title = 'Checkers+'
        self.screen = CheckerScreen()
        print(self.screen.ids)
        return self.screen

    '''
        pre: None
        post: None
        desc: Unused
    '''
    def hide_logo(self, widget=None):
        pass

    '''
        pre: None
        post: None
        desc: Unused
    '''
    def show_logo(self, widget=None):
        pass

    '''
        pre: None
        post: None
        desc: Generates home menu and populates it
    '''
    def home_menu(self):
        self.hide_logo()

        startText = "Start Human Game"
        if self.screen.aiDiff > 0:
            startText = "Set-up AI Game"

        if self.screen.aiDiff == -2:
            startText = 'Set-up Training Game With ' + self.screen.learningAi.name

        scope = self.screen.ids['home']

        box = BoxLayout(orientation='horizontal')

        def change_start_text(widget):
            widget.text = "Restart Game"
            if self.screen.aiDiff > 0 or self.screen.aiDiff == -2:
                widget.disabled = True

                def remove_start_butt(widget):
                    box.remove_widget(widget)
                    box.children[-1].disabled = False

                toAdd = Button(text='Start')
                toAdd.bind(on_press=self.screen.move_piece_ai)
                toAdd.bind(on_release=remove_start_butt)
                box.add_widget(toAdd)
            box.children[-2].disabled = False

        toAdd = Button(text=startText)
        toAdd.bind(on_press=self.screen.generate_game_button)
        toAdd.bind(on_release=change_start_text)
        box.add_widget(toAdd)

        toAdd = Button(text="End Game", disabled=True)
        toAdd.bind(on_press=self.screen.del_board)
        toAdd.bind(on_release=self.show_logo)
        box.add_widget(toAdd)


        scope.add_widget(box)
        pass

    '''
        pre: None
        post: None
        desc: Generates game menu and populates it
    '''
    def game_menu(self):
        scope = self.screen.ids['game']
        box = BoxLayout(orientation='horizontal')

        self.screenSlider = Slider(min=minSizeWidth, max=maxSizeWidth, value=Window.size[0])
        box.add_widget(self.screenSlider)
        if self.screen.activeGame:
            self.screenSlider.set_disabled(True)

        butt1 = Button(text="Adjust screen resolution")
        butt1.bind(on_release=self.resize_window)

        box.add_widget(butt1)

        butt2 = Button(text="Select AI")
        butt2.bind(on_press=self.pick_AI)
        box.add_widget(butt2)

        gary = Button(text="Gary",
                      background_normal=".\\assets\\images\\gary.png")
        gary.bind(on_release=self.gary)
        box.add_widget(gary)

        scope.add_widget(box)

    '''
        pre: None
        post: None
        desc: resize window to slider selection
    '''
    def resize_window(self, widget):
        windowSize = (self.screenSlider.value, self.screenSlider.value*11/10)
        Window.size = windowSize

    '''
        pre: None
        post: None
        desc: generate and display select ai popup, button action
    '''
    def pick_AI(self, widget):
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

        buttonToAdd = ToggleButton(text="None", id='none', group='aiDiff')
        if self.screen.aiDiff == -1:
            buttonToAdd.state = 'down'
        buttonToAdd.bind(on_press=self.aiSelect)
        popButtonLayout.add_widget(buttonToAdd)

        buttonToAdd = ToggleButton(text="Learning", id='learning', group='aiDiff')
        if self.screen.aiDiff == -2:
            buttonToAdd.state = 'down'
        buttonToAdd.bind(on_press=self.learningSelect)
        popButtonLayout.add_widget(buttonToAdd)

        popAI = Popup(title='Pick an AI', size_hint=(.5, .5), content=(popButtonLayout))
        popAI.open()

    '''
        pre: None
        post: None
        desc: Gary!
    '''
    def gary(self, widget):
        popSize = list(widget.parent.size)
        popSize[0] /= 2
        popSize[1] /= 2
        popGary = Popup(title='This is Gary', size_hint=(.5, .5), content=Image(source=".\\assets\\images\\gary.png", size=(100, 100)))
        popGary.open()

    '''
        pre: None
        post: None
        desc: selector for ai diff
    '''
    def aiSelect(self, widget):
        if widget.id == 'easy':
            self.screen.aiDiff = 1
        elif widget.id == 'med':
            self.screen.aiDiff = 2
        elif widget.id == 'hard':
            self.screen.aiDiff = 3
        elif widget.id == 'none':
            self.screen.aiDiff = -1
        print(self.screen.aiDiff)

    '''
        pre: None
        post: None
        desc: generate learning slection menu, button action
    '''
    def learningSelect(self, widget):
        self.screen.aiDiff = -2

        # Start learning ai pop up
        listOfFile = os.listdir('.\\learning\\')
        buttonLabels = list()
        for entry in listOfFile:
            buttonLabels.append(entry.replace('.ai', ''))

        learningButtonLayout = BoxLayout(orientation='vertical')

        for i in range(len(buttonLabels)):
            buttonToAdd = Button(text=buttonLabels[i], id=buttonLabels[i])
            buttonToAdd.bind(on_press=self.modelSelect)
            learningButtonLayout.add_widget(buttonToAdd)

        # create a new one
        buttonToAdd = Button(text='Create New', id='new')
        buttonToAdd.bind(on_press=self.newModel)
        learningButtonLayout.add_widget(buttonToAdd)

        self.selectorPop = Popup(title='Pick a Learning Ai or create to create one', size_hint=(.5, .5),
                                 content=learningButtonLayout)
        self.selectorPop.open()

        # End learning ai pop up

    '''
        pre: None
        post: None
        desc: select model button action
    '''
    def modelSelect(self, widget):
        print(widget.id)
        self.screen.learningAi = LearningModel(str(widget.id))
        self.selectorPop.dismiss()

    '''
        pre: None
        post: None
        desc: generate menu for leanring ai creation, button action
    '''
    def newModel(self, widget):
        creationLayout = BoxLayout(orientation='vertical')

        innerLayout = GridLayout(cols=2)
        label = Label(text='Name: ', halign='right', valign='middle', padding=[0,0])
        label.text_size = label.size
        innerLayout.add_widget(label)
        textinput = TextInput(text='Name', multiline=False)
        textinput.bind(on_text_validate=self.validateText)
        innerLayout.add_widget(textinput)
        self.nameInput = textinput


        label = Label(text='Learning Factor: ')
        innerLayout.add_widget(label)
        learningFactor = Slider(min=.1, max=1, value=1)
        self.learningFactor = learningFactor
        innerLayout.add_widget(learningFactor)

        creationLayout.add_widget(innerLayout)

        buttonToAdd = Button(text='Create', id='create')
        buttonToAdd.bind(on_press=self.createNew)
        creationLayout.add_widget(buttonToAdd)

        self.creatorPop = Popup(title='Fill out the fields to create new Learning Ai', size_hint=(.5, .5),
                                content=creationLayout)
        self.creatorPop.bind(on_dismiss=self.selectorPop.dismiss)
        self.creatorPop.open()

    '''
        pre: None
        post: None
        desc: handle creation of new ai and dismiss popup, button action
    '''
    def createNew(self, widget):
        self.screen.learningAi = LearningModel(self.nameInput.text, self.learningFactor.value)
        self.creatorPop.dismiss()

    '''
        pre: None
        post: None
        desc: Unused, button action
    '''
    def validateText(self, widget):
        pass

# TODO add options for AI only game?

# TODO refine codebase further to seperate code more effectivly

if __name__ == '__main__':
    Builder.load_file(pathToKvlang)
    app = CheckersApp()
    app.run()


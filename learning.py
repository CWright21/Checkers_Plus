import pickle
from os import path
from virtualboard import VirtualBoard
from alphabeta import AlphaBeta
import random


class TransitionEntry:
    #pre: take in 2 boards in string form
    #post: creats obj
    def __init__(self, fromBoard, toState, val, id):
        self.fromState = fromBoard
        self.toState = toState
        self.deltaVal = val
        self.move = id
        pass


class TransitionTable:
    def __init__(self, learningFactor):
        self.table = []
        self.learningFactor = learningFactor

    '''
        pre: None
        post: None
        desc: Unimplemented
    '''
    def sort_table(self, target):
        #TODO implement sorting for faster search?
        pass

    '''
        pre: board states old and new, val to initialize at and a move id
        post: None
        desc: adds entry to table
    '''
    def add_entry(self, oldBoard, newBoard, val, id):
        if random.random() < self.learningFactor:
            for entry in self.table:
                if str(entry.move) == str(id):
                    entry.deltaVal += val
                    print('reinforcing known transition', id.__str__(), 'with', val)
                    return
            self.table.append(TransitionEntry(oldBoard, newBoard, val, id))
            print('Creating new transition', id.__str__(), 'with val', val)
        else:
            print('Randomly chose not to learn')
        print("table:", self.table)

    '''
        pre: board state named state
        post: None
        desc: returns best match found or none if no matches
    '''
    def check_for_match(self, state):
        currBest = None
        currVal = float('-inf')
        for entry in self.table:
            if entry.fromState == state and entry.deltaVal > currVal:
                currBest = entry.move
                currVal = entry.deltaVal
        return currBest


class LearningModel:
    def __init__(self, name, learningFactor = 1):
        fileLoaction = ".\\learning\\" + name + ".ai"
        if path.exists(fileLoaction):
            self.transTable = pickle.load(open(fileLoaction, 'rb'))
            print('table:', self.transTable.table)

        else:
            self.transTable = TransitionTable(learningFactor)
        self.boardList = []
        self.moveList = []
        self.name = name
        pass

    '''
        pre: bool true if won
        post: None
        desc: reinforces game +1 to winning moves -1 to losing
    '''
    def reinforce_game(self, won):
        if won:
            value = 1
        else:
            value = 0
        print(len(self.boardList),self.boardList)
        print(len(self.moveList),self.moveList)
        for i in range(len(self.boardList)-1):
            self.learn(self.boardList[i], self.boardList[i+1], value, self.moveList[i])

    '''
        pre: board states old and new, val to initialize at and a move id
        post: None
        desc: passes to add entry
    '''
    def learn(self, oldBoard, newBoard, val, id):
        self.transTable.add_entry(oldBoard, newBoard, val, id)

    '''
        pre: current board state
        post: None
        desc: choses a move based on current board state
    '''
    def choose_move(self, board):
        if len(self.boardList) == 0:
            self.boardList.append(board)

        match = self.match_state(board)
        if match is None:
            one_tree = board.generate_game_tree('red', 0)
            alg = AlphaBeta(one_tree)
            match = alg.alpha_beta_search(alg.root)
        board.move_piece(match.frm.x, match.frm.y, match.to.x, match.to.y)
        self.boardList.append(board)
        self.moveList.append(match)
        return match

    '''
        pre: curr board
        post: None
        desc: passes to check match
    '''
    def match_state(self, board):
        return self.transTable.check_for_match(board)

    '''
        pre: None
        post: None
        desc: saves to file using pickle
    '''
    def save(self):
        pickle.dump(self.transTable, open(".\\learning\\" + self.name + ".ai", 'wb'))


def main():
    pass

if __name__ == "__main__":
    ai = LearningModel("tester")
"""
    filename = '.\\assets\\test_files\\testBoardStates.txt'
    print("hello world! " + filename)
    testBoard = VirtualBoard()
    testBoard.parse_data_as_text(filename)
    #print(testBoard)
    tree = testBoard.generate_game_tree('red', 3)
    a_b = AlphaBeta(tree)
    move = a_b.alpha_beta_search(a_b.root)
    oldState = testBoard
    testBoard.move_piece(move.frm.x, move.frm.y, move.to.x, move.frm.y)
    val = 0
    ai.learn(oldState, testBoard, val, move)

    #move = ai.choose_move(testBoard)


    ai.save()
"""


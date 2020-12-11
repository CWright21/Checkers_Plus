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

    def sort_table(self, target):
        #TODO implement sorting for faster search?
        pass

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

    def check_for_match(self, state):
        currBest = None
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

    def reinforce_game(self, won):
        if won:
            value = 1
        else:
            value = 0
        print(len(self.boardList),self.boardList)
        print(len(self.moveList),self.moveList)
        for i in range(len(self.boardList)-1):
            self.learn(self.boardList[i], self.boardList[i+1], value, self.moveList[i])

    def learn(self, oldBoard, newBoard, val, id):
        self.transTable.add_entry(oldBoard, newBoard, val, id)

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

    def match_state(self, board):
        return self.transTable.check_for_match(board)

    def save(self):
        pickle.dump(self.transTable, open(".\\learning\\" + self.name + ".ai", 'wb'))


def main():
    pass

if __name__ == "__main__":
    ai = LearningModel("tester")
'''
    filename = 'testBoardStates.txt'
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
'''


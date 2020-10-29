class AlphaBeta:
    # print utility value of root node (assuming it is max)
    # print names of all nodes visited during search, disabled normally to reduce runtime
    def __init__(self, game_tree):
        self.game_tree = game_tree  # GameTree
        self.root = game_tree.root  # GameNode
        return

    def alpha_beta_search(self, node):
        inf = float('inf')
        best_val = -inf
        beta = inf

        children = self.getChildren(node)
        best_state = None
        for state in children:
            value = self.min_value(state, best_val, beta)
            print(value)
            if value > best_val:
                best_val = value
                best_state = state
        print("A_B :  Utility Value of Root Node: = " + str(best_val))
        print("A_B :  Best State is: ", best_state.name)
        return best_state.name

    def max_value(self, node, alpha, beta):
        print("A_B –> MAX: Visited Node :: " + str(node.name))
        if self.isTerminal(node):
            return self.getUtility(node)
        inf = float('inf')
        value = -inf

        children = self.getChildren(node)
        for state in children:
            value = max(value, self.min_value(state, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, node, alpha, beta):
        print("A_B –> MIN: Visited Node :: " + str(node.name))
        if self.isTerminal(node):
            return self.getUtility(node)
        inf = float('inf')
        value = inf

        successors = self.getChildren(node)
        for state in successors:
            value = min(value, self.max_value(state, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value
    #                     #
    #   UTILITY METHODS   #
    #                     #

    # successor states in a game tree are the child nodes…
    def getChildren(self, node):
        assert node is not None
        return node.children

    # return true if the node has NO children (successor states)
    # return false if the node has children (successor states)
    def isTerminal(self, node):
        assert node is not None
        return len(node.children) == 0

    def getUtility(self, node):
        assert node is not None
        return node.value

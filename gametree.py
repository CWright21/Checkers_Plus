class GameNode:
    def __init__(self, name, value=0, parent=None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children = []

    def addChild(self, child):
        self.children.append(child)


class GameTree:
    def __init__(self, states):
        self.root = GameNode(states.pop(0))
        for state in states:
            self.parse_subtree(state, self.root)

    def parse_subtree(self, states, parent):
        #base
        if type(states) is tuple:
            leaf = GameNode(states[0])
            leaf.parent = parent
            parent.addChild(leaf)
            if len(states==2):
                leaf.value = states[1]
            return

        #recursive
        node = GameNode(states.pop(0))
        node.parent = parent
        parent.addChild(node)
        for state in states:
            self.parse_subtree(state, node)
        return

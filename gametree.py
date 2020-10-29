class Move:
    def __init__(self, fromCoords, toCoords):
        self.frm = fromCoords
        self.to = toCoords

    def __str__(self):
        return str(self.frm) + '-' + str(self.to)


class GameNode:
    def __init__(self, name, value=0, parent=None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children = []

    def addChild(self, child):
        self.children.append(child)


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return str(self.x) + ',' + str(self.y)


class GameTree:
    '''
    Generates a tree from a list of states starting with states[0] as the root
    each node has format [me, [children]] with each terminal node sent as a tuple with its value as its 'child'
    ex. [a, [b, (d, 1)], (c, 2)]
    is
       a
      / \
     b   2(c)
     |
     1(d)
    '''
    def __init__(self, parsed):
        #states = ['A', ['B', ('D', 3), ('E', 5)], ['C', ['F', ['I',('K',0), ('L', 7)],('J',5)], ['G', ('M',7), ('N',8)], ('H',4)]]
        print("start", parsed)
        print()
        name = 'current'
        #print(parsed)
        self.root = GameNode(name)
        for children in parsed:
            self.parse_subtree(children, self.root)

    def parse_subtree(self, children, parent):
        #base
        #print("Children", children)

        if type(children) is tuple:
            leaf = GameNode(children[0])
            leaf.parent = parent
            parent.addChild(leaf)
            leaf.value = children[1]
            return

        i = 0
        while i < len(children):
            child = children[i]
            #print("children[%d]" % i, child)

            #recursive
            #print(child)
            node = GameNode(child)
            node.parent = parent
            parent.addChild(node)
            for nestedChild in children[i+1]:
                self.parse_subtree(nestedChild, node)
            i += 2


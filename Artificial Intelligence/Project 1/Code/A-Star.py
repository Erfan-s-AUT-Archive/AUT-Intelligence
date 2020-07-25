import re, copy, itertools


class Person:
    def __init__(self, height, row: str):
        self.height = height
        self.row = row


class Jafar:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y


class Node:
    def __init__(
        self,
        permutation: list,
        jafar: Jafar,
        depth: int = 0,
        last_move: str = None,
        parent=None,
    ):
        self.permutation = permutation
        self.jafar = jafar
        self.parent = parent
        self.last_move = last_move
        if parent:
            self.depth = parent.depth + 1
        else:
            self.depth = 0


m, n = 0, 0


def read_input():
    grid = []
    location = None
    with open("twomove.txt", "r") as f:
        global m, n
        n, m = (int(x) for x in f.readline().split(" ") if x != "\n")
        split_str = "[0-9]+"
        for i in range(n):
            row = []
            raw_row = f.readline()[:-1].split(" ")[:m]
            for index, item in enumerate(raw_row):
                if item != "#":
                    x = re.split(split_str, item)
                    row.append(Person(int(item[: item.find(x[1])]), x[1]))
                else:
                    row.append(Person(float("inf"), "#"))
                    location = Jafar(index, i)
            grid.append(row)
    start = Node(grid, location)
    return start


def same_as_grandparent(parent: Node, current: list):
    if parent.parent != None:
        grand_iter = parent.parent.permutation
        for i in range(n):
            for j in range(m):
                if (
                    grand_iter[i][j].height != current[i][j].height
                    or grand_iter[i][j].row != current[i][j].row
                ):
                    return False
        return True

    return False


def move(node: Node, deltaX, deltaY, child_nodes: list, move_str):
    X, Y = node.jafar.X, node.jafar.Y
    new_iter = copy.deepcopy(node.permutation)
    new_iter[Y + deltaY][X + deltaX], new_iter[Y][X] = (
        new_iter[Y][X],
        new_iter[Y + deltaY][X + deltaX],
    )
    if not same_as_grandparent(node, new_iter):
        child_nodes.append(
            Node(new_iter, Jafar(X + deltaX, Y + deltaY), last_move=move_str, parent=node)
        )


def generate_children(node: Node):
    child_nodes = []
    X, Y = node.jafar.X, node.jafar.Y
    if Y < n - 1:
        move(node, 0, 1, child_nodes, "up")
    if Y > 0:
        move(node, 0, -1, child_nodes, "down")
    if X < m - 1:
        move(node, 1, 0, child_nodes, "right")
    if X > 0:
        move(node, -1, 0, child_nodes, "left")

    return child_nodes


def check_goal(node: Node):
    it = node.permutation
    in_order = all(
        it[i][j].height > it[i][j + 1].height for i in range(n) for j in range(m - 1)
    )
    in_row = all(
        it[i][j].row == it[i][j + 1].row or it[i][j].row == "#"
        for i in range(n)
        for j in range(m - 1)
    )
    return node.jafar.X == 0 and in_order and in_row


def generate_goal_permutations(root: Node):
    it = root.permutation
    by_row = {chr(i + 97): [] for i in range(n)}
    for i in range(n):
        for j in range(m):
            current = it[i][j]
            if current.row != "#":
                by_row.get(current.row).append(current)

    goal = []
    for _, value in by_row.items():
        goal.append(sorted(value, key=lambda k: k.height, reverse=True))

    min(goal, key=len).insert(0, Person(float("inf"), "#"))

    goals = [list(perm) for perm in list(itertools.permutations(goal))]
    return [Node(gl, None) for gl in goals]


def find_location_in_permutation(person: Person, goal_node: Node):
    it = goal_node.permutation
    for i in range(n):
        for j in range(m):
            if str(it[i][j].height) + it[i][j].row == str(person.height) + person.row:
                return j, i
    return -1, -1


def manhattan_distance(X1, Y1, X2, Y2):
    return abs(X1 - X2) + abs(Y1 - Y2)


def get_displacement(node: Node, goal_node: Node):
    it = node.permutation
    sum_displacement = 0
    for i in range(n):
        for j in range(m):
            oX, oY = find_location_in_permutation(it[i][j], goal_node)
            sum_displacement += manhattan_distance(j, i, oX, oY)
    return sum_displacement


def heuristic(node: Node, goals: list):
    min_displacement = float("inf")
    for goal_node in goals:
        current_displacement = get_displacement(node, goal_node)
        if current_displacement < min_displacement:
            min_displacement = current_displacement
    return min_displacement


def new_level(list_of_nodes, goals = None):
    next_nodes = []
    for node in list_of_nodes:
        next_nodes += generate_children(node)
    if goals:
        next_nodes = sorted(next_nodes, key=lambda k: k.depth + heuristic(k, goals))

    return next_nodes


def print_permutation(node: Node):
    it = node.permutation
    for i in range(n):
        print_str = ""
        for j in range(m):
            if it[i][j].row == "#":
                print_str += "# "
            else:
                print_str += str(it[i][j].height) + it[i][j].row + " "
        print(print_str)
    print(node.last_move)
    print()


def a_star(root: Node, goals):
    levels = [root]
    while True:
        for node in levels:
            # print_permutation(node)
            if check_goal(node):
                return node
        levels = new_level(levels, goals)


def print_result(result: Node):
    if result:
        print("depth: " + str(result.depth))
        while result.parent:
            print_permutation(result)
            result = result.parent
    else:
        print("NO ANSWER FOUND")


def print_result_forwards(result: Node):
    if result:
        print("Depth: " + str(result.depth))
        nodes_list = []
        while result.parent:
            nodes_list.insert(0, result)
            result = result.parent
        nodes_list.insert(0, result)
        for node in nodes_list:
            print_permutation(node)
    else:
        print("NO ANSWER FOUND")

def main():
    root = read_input()
    goals = generate_goal_permutations(root)
    result = a_star(root, goals)
    print_result_forwards(result)


if __name__ == "__main__":
    main()

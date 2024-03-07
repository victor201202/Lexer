from .NFA import NFA

EPSILON = ''
index = 0


class Tree:
    nfa = NFA({''}, {0}, 0, {}, {0})

    def __init__(self, data):
        self.children = []
        self.data = data


def cons_char(ch, index):
    if ch == '[a-z]':
        chars = "abcdefghijklmnopqrstuvwxyz"
        new_D = {}
        new_S = set()
        for char in chars:
            new_D[index, char] = {index + 1}
            new_S.add(char)

        return NFA(new_S, {index, index + 1}, index, new_D, {index + 1})
    elif ch == '[A-Z]':
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        new_D = {}
        new_S = set()
        for char in chars:
            new_D[index, char] = {index + 1}
            new_S.add(char)
        return NFA(new_S, {index, index + 1}, index, new_D, {index + 1})
    elif ch == '[0-9]':
        chars = "0123456789"
        new_D = {}
        new_S = set()
        for char in chars:
            new_D[index, char] = {index + 1}
            new_S.add(char)
        return NFA(new_S, {index, index + 1}, index, new_D, {index + 1})
    elif ch[0] == '\\':
        return NFA(set(ch[1]), {index, index + 1}, index, {(index, ch[1]): {index + 1}}, {index + 1})
    else:
        return NFA(set(ch), {index, index + 1}, index, {(index, ch): {index + 1}}, {index + 1})


def cons_star(nfa: NFA, index):
    new_S = nfa.S
    new_K = nfa.K
    new_K.add(index)
    new_K.add(index + 1)
    new_q0 = index
    new_D = nfa.d
    new_F = {index + 1}
    F = nfa.F.copy().pop()
    new_D[F, EPSILON] = {nfa.q0, index + 1}
    new_D[index, EPSILON] = {index + 1, nfa.q0}
    return NFA(new_S, new_K, new_q0, new_D, new_F)


def cons_concat(nfas: list[NFA]):
    new_S = nfas[0].S
    new_K = nfas[0].K
    new_q0 = nfas[0].q0
    new_D = nfas[0].d
    new_F = nfas[len(nfas) - 1].F
    for i in range(1, len(nfas)):
        new_S.update(nfas[i].S)
        new_K.update(nfas[i].K)
        new_D.update(nfas[i].d)
        aux_F = nfas[i - 1].F.copy()
        new_D[aux_F.pop(), EPSILON] = {nfas[i].q0}
    return NFA(new_S, new_K, new_q0, new_D, new_F)


def cons_nfas(t: Tree) -> None:
    global index
    if len(t.children) == 0:
        t.nfa = cons_char(t.data, index)
        index = index + 2
        return None
    for i in range(len(t.children)):
        cons_nfas(t.children[i])
    if t.data == '|':
        t.nfa = cons_or(t.children[0].nfa, t.children[1].nfa, index)
        index = index + 2
    elif t.data == '.':
        nfas = []
        for tree in t.children:
            nfas.append(tree.nfa)
        t.nfa = cons_concat(nfas)
    elif t.data == '*':
        t.nfa = cons_star(t.children[0].nfa, index)
        index = index + 2
    elif t.data == '?':
        t.nfa = cons_question(t.children[0].nfa, index)
        index = index + 2
    elif t.data == '+':
        t.nfa = cons_plus(t.children[0].nfa, index)
        index = index + 2
    return None


def cons_or(nfa1: NFA, nfa2: NFA, index):
    new_S = nfa1.S.union(nfa2.S)
    new_K = nfa1.K.union(nfa2.K)
    new_K.add(index)
    new_K.add(index + 1)
    new_D = nfa1.d | nfa2.d
    new_q0 = index
    new_F = {index + 1}
    new_D[index, EPSILON] = {nfa1.q0, nfa2.q0}
    for state in nfa1.F:
        new_D[state, EPSILON] = {index + 1}
    for state in nfa2.F:
        new_D[state, EPSILON] = {index + 1}
    return NFA(new_S, new_K, new_q0, new_D, new_F)


def cons_question(nfa, index):
    new_S = nfa.S
    new_K = nfa.K
    new_K.add(index)
    new_K.add(index + 1)
    new_q0 = index
    new_D = nfa.d
    new_F = {index + 1}
    F = nfa.F.copy().pop()
    new_D[F, EPSILON] = {index + 1}
    new_D[index, EPSILON] = {index + 1, nfa.q0}
    return NFA(new_S, new_K, new_q0, new_D, new_F)


def cons_plus(nfa, index):
    new_S = nfa.S
    new_K = nfa.K
    new_K.add(index)
    new_K.add(index + 1)
    new_q0 = index
    new_D = nfa.d
    new_F = {index + 1}
    F = nfa.F.copy().pop()
    new_D[F, EPSILON] = {nfa.q0, index + 1}
    new_D[index, EPSILON] = {nfa.q0}
    return NFA(new_S, new_K, new_q0, new_D, new_F)


root = Tree('')


class Regex:
    def thompson(self) -> NFA[int]:
        cons_nfas(root)
        return root.nfa


def abstract_square(regex: str):
    rexes = []
    count = 1
    regex2 = regex
    remove_paren = True
    while remove_paren:
        no_close = 0
        start_index = -1
        end_index = -1
        remove_paren = False
        for i in range(len(regex)):
            if i > 0:
                if regex[i] == '[' and regex[i - 1] != '\\':
                    if no_close == 0:
                        start_index = i
                    no_close = no_close + 1
                if regex[i] == ']' and regex[i - 1] != '\\':
                    no_close = no_close - 1
                    if no_close == 0:
                        end_index = i
                if start_index != -1 and end_index != -1:
                    rexes.append(regex2[start_index:end_index + 1])
                    regex2 = regex2.replace(regex2[start_index:end_index + 1], 'L', 1)
                    count = count + 1
                    regex = regex2
                    remove_paren = True
                    break
            else:
                if regex[i] == '[':
                    start_index = i
                    no_close = no_close + 1
    return regex2, rexes


def abstract_paren(regex: str):
    rexes = []
    count = 1
    regex2 = regex
    remove_paren = True
    while remove_paren:
        no_close = 0
        start_index = -1
        end_index = -1
        remove_paren = False
        for i in range(len(regex)):
            if i > 0:
                if regex[i] == '(' and regex[i - 1] != '\\':
                    if no_close == 0:
                        start_index = i
                    no_close = no_close + 1
                if regex[i] == ')' and regex[i - 1] != '\\':
                    no_close = no_close - 1
                    if no_close == 0:
                        end_index = i
                if start_index != -1 and end_index != -1:
                    rexes.append(regex2[start_index + 1:end_index])
                    regex2 = regex2.replace(regex2[start_index:end_index + 1], 'R', 1)
                    count = count + 1
                    regex = regex2
                    remove_paren = True
                    break
            else:
                if regex[i] == '(':
                    start_index = i
                    no_close = no_close + 1
    return regex2, rexes


def abstract_or(regex2: str):
    regex3 = regex2
    rexes = []
    for i in range(len(regex2)):
        if regex2[i] == '|':
            rexes.append(regex2[0: i])
            regex3 = regex2.replace(regex2[0:i], 'O', 1)
            rexes.append(regex2[i + 1:])
            regex3 = regex3.replace(regex2[i + 1:], 'O', 1)
            break
    return regex3, rexes


def abstract_Q(regex: str):
    regex2 = str()
    Q = []
    pos = regex.find('?')
    if pos == -1:
        return regex, Q
    regex2 = regex
    while pos != -1:
        Q.append(regex2[pos - 1])
        regex2 = regex2.replace(regex2[pos - 1: pos + 1], 'Q', 1)
        pos = regex2.find('?')
    return regex2, Q


def abstract_P(regex: str):
    regex2 = str()
    P = []
    pos = regex.find('+')
    if pos == -1:
        return regex, P
    regex2 = regex
    while pos != -1:
        P.append(regex2[pos - 1])
        regex2 = regex2.replace(regex2[pos - 1: pos + 1], 'P', 1)
        pos = regex2.find('+')
    return regex2, P


def abstract_S(regex: str):
    regex2 = str()
    S = []
    pos = regex.find('*')
    if pos == -1:
        return regex, S
    regex2 = regex
    while pos != -1:
        S.append(regex2[pos - 1])
        regex2 = regex2.replace(regex2[pos - 1: pos + 1], 'S', 1)
        pos = regex2.find('*')
    return regex2, S


def abstract_special(regex: str):
    regex2 = str()
    S = []
    pos = regex.find('\\')
    if pos == -1:
        return regex, S
    regex2 = regex
    while pos != -1:
        S.append(regex2[pos: pos + 2])
        regex2 = regex2.replace(regex2[pos: pos + 2], 'Z', 1)
        pos = regex2.find('\\')
    return regex2, S


def print_tree(t: Tree, index: int) -> None:
    for i in range(index):
        print("-", end='')
    print(t.data)
    if len(t.children) == 0:
        return None
    index = index + 1
    for x in t.children:
        print_tree(x, index)
    return None


def cons_tree(t: Tree, index: int) -> None:
    if len(t.children) == 0:
        aux_t = cons_node(t.data)
        t.data = aux_t.data
        t.children = aux_t.children
        return None
    for i in range(len(t.children)):
        cons_tree(t.children[i], index)
    return None


def cons_node(regex2: str):
    t = Tree('')
    if regex2.find('(') != -1:
        regex2, PAREN = abstract_paren(regex2)
    if regex2.find('|') != -1:
        regex2, OR = abstract_or(regex2)
        t.data = '|'
        for i in range(len(OR)):
            aux_child = OR[i]
            child = ''
            for ch in aux_child:
                if ch == 'R':
                    child = child + '(' + PAREN.pop(0) + ')'
                else:
                    child = child + ch
            t.children.append(Tree(child))
    else:
        regex2, L = abstract_square(regex2)
        regex2, Z = abstract_special(regex2)
        regex2, S = abstract_S(regex2)
        regex2, Q = abstract_Q(regex2)
        regex2, P = abstract_P(regex2)
        if len(regex2) > 1:
            t.data = '.'
            for ch in regex2:
                if ch == 'R':
                    t.children.append(Tree('(' + PAREN.pop(0) + ')'))
                elif ch == 'Q':
                    aux_ch = Q.pop(0)
                    t2 = Tree('?')
                    if aux_ch == 'R':
                        t2.children.append(Tree(PAREN.pop(0)))
                    elif aux_ch == 'L':
                        t2.children.append(Tree(L.pop(0)))
                    elif aux_ch == 'Z':
                        t2.children.append(Tree(Z.pop(0)))
                    else:
                        t2.children.append(Tree(aux_ch))
                    t.children.append(t2)
                elif ch == 'S':
                    aux_ch = S.pop(0)
                    t2 = Tree('*')
                    if aux_ch == 'R':
                        t2.children.append(Tree(PAREN.pop(0)))
                    elif aux_ch == 'L':
                        t2.children.append(Tree(L.pop(0)))
                    elif aux_ch == 'Z':
                        t2.children.append(Tree(Z.pop(0)))
                    else:
                        t2.children.append(Tree(aux_ch))
                    t.children.append(t2)
                elif ch == 'P':
                    aux_ch = P.pop(0)
                    t2 = Tree('+')
                    if aux_ch == 'R':
                        t2.children.append(Tree(PAREN.pop(0)))
                    elif aux_ch == 'L':
                        t2.children.append(Tree(L.pop(0)))
                    elif aux_ch == 'Z':
                        t2.children.append(Tree(Z.pop(0)))
                    else:
                        t2.children.append(Tree(aux_ch))
                    t.children.append(t2)
                elif ch == 'L':
                    t.children.append(Tree(L.pop(0)))
                elif ch == 'Z':
                    t.children.append(Tree(Z.pop(0)))
                else:
                    t.children.append(Tree(ch))
        else:
            if regex2 == 'R':
                t.data = PAREN.pop(0)
            elif regex2 == 'Q':
                t.data = '?'
                aux_reg = Q.pop(0)
                if aux_reg == 'R':
                    t.children.append(Tree(PAREN.pop(0)))
                elif aux_reg == 'L':
                    t.children.append(Tree(L.pop(0)))
                elif aux_reg == 'Z':
                    t.children.append(Tree(Z.pop(0)))
                else:
                    t.children.append(Tree(aux_reg))
            elif regex2 == 'S':
                t.data = '*'
                aux_reg = S.pop(0)
                if aux_reg == 'R':
                    t.children.append(Tree(PAREN.pop(0)))
                elif aux_reg == 'L':
                    t.children.append(Tree(L.pop(0)))
                elif aux_reg == 'Z':
                    t.children.append(Tree(Z.pop(0)))
                else:
                    t.children.append(Tree(aux_reg))
            elif regex2 == 'P':
                t.data = '+'
                aux_reg = P.pop(0)
                if aux_reg == 'R':
                    t.children.append(Tree(PAREN.pop(0)))
                elif aux_reg == 'L':
                    t.children.append(Tree(L.pop(0)))
                elif aux_reg == 'Z':
                    t.children.append(Tree(Z.pop(0)))
                else:
                    t.children.append(Tree(aux_reg))
            elif regex2 == 'L':
                t.data = L.pop(0)
            elif regex2 == 'Z':
                t.data = Z.pop(0)
            else:
                t.data = regex2
    return t


def strip_spaces(regex: str):
    regex2 = str()
    for i in range(len(regex)):
        if i > 0:
            if regex[i] != ' ' or (regex[i] == ' ' and regex[i - 1] == '\\'):
                regex2 = regex2 + regex[i]
        elif regex[i] != ' ':
            regex2 = regex2 + regex[i]
    return regex2


def parse_regex(regex: str) -> Regex:
    regex = strip_spaces(regex)
    global root
    root = cons_node(regex)
    for i in range(len(regex) * 2):
        cons_tree(root, 0)
    return Regex()

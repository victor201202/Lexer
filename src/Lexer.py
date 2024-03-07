from src.DFA import DFA
from src.NFA import NFA
from src.Regex import parse_regex

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs
state_regex = {}


def find_line_by_index(input_string, target_index):
    lines = input_string.split('\n')
    current_index = 0
    line_number = 0

    for line in lines:
        line_length = len(line) + 1
        if current_index + line_length > target_index:
            return line_number, target_index - current_index

        current_index += line_length
        line_number += 1
    return -1, -1


def extract_numbers(input_string):
    numbers = []
    current_number = ''
    is_negative = False

    for char in input_string:
        if char.isdigit():
            current_number += char
        elif char == '-' and not current_number:
            is_negative = True
        elif char == ',':
            num = int(current_number)
            if is_negative:
                num = -num
            numbers.append(num)
            current_number = ''
            is_negative = False

    num = int(current_number)
    if is_negative:
        num = -num
    numbers.append(num)

    return numbers


class Lexer:
    dfa = DFA(set(), {-1}, -1, {}, set())

    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        nfa = NFA(set(), {-1}, -1, {}, set())
        for tuple in spec:
            aux_nfa = parse_regex(tuple[1]).thompson()
            state_regex[int(list(aux_nfa.F)[0])] = tuple[0]
            nfa.S = nfa.S.union(aux_nfa.S)
            nfa.K = nfa.K.union(aux_nfa.K)
            nfa.d = nfa.d | aux_nfa.d
            nfa.F = nfa.F.union(aux_nfa.F)
            if (nfa.q0, EPSILON) in nfa.d:
                nfa.d[nfa.q0, EPSILON].add(aux_nfa.q0)
                pass
            else:
                nfa.d[nfa.q0, EPSILON] = {aux_nfa.q0}
        self.dfa = nfa.subset_construction()
        pass

    def run_dfa(self, word):
        prev_states = []
        state = self.dfa.q0

        for i in range(len(word)):
            ch = word[i]
            if (state, ch) in self.dfa.d:
                prev_states.append(state)
                state = self.dfa.d[state, ch]
            else:
                state = "err"
                break

        return state, prev_states

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)
        tokens = []
        start_index = 0
        error = False
        while start_index < len(word) and not error:
            end_index = start_index + 1
            state, prev_states = self.run_dfa(word[start_index:end_index])

            if state == "err":
                tokens.clear()
                line, column = find_line_by_index(word, end_index - 1)
                tokens.append(("", "No viable alternative at character {}, line {}".format(column, line)))
                error = True
                continue

            while state != str(999) and end_index <= len(word):
                end_index = end_index + 1
                state, prev_states = self.run_dfa(word[start_index:end_index])
                if state == "err":
                    tokens.clear()
                    line, column = find_line_by_index(word, end_index - 1)
                    tokens.append(("", "No viable alternative at character {}, line {}".format(column, line)))
                    error = True
                    break
            if error:
                break
            if state == str(999):
                count = 0
                found = False
                for i in range(1, len(prev_states) + 1):
                    if found:
                        break
                    count = count + 1
                    aux_list = extract_numbers(prev_states[-i])
                    aux_list.sort()
                    for s in aux_list:
                        if s in state_regex:
                            found = True
                            tokens.append((state_regex[s], word[start_index:end_index - count]))
                            break
                if not found:
                    tokens.clear()
                    line, column = find_line_by_index(word, end_index - 1)
                    tokens.append(("", "No viable alternative at character {}, line {}".format(column, line)))
                    error = True

                start_index = end_index - count
            else:
                aux_list = extract_numbers(state)
                aux_list.sort()
                found = False
                for s in aux_list:
                    if s in state_regex:
                        tokens.append((state_regex[s], word[start_index:end_index]))
                        found = True
                        break
                if not found:
                    count = 0
                    found = False
                    for i in range(1, len(prev_states) + 1):
                        if found:
                            break
                        count = count + 1
                        aux_list = extract_numbers(prev_states[-i])
                        aux_list.sort()
                        for s in aux_list:
                            if s in state_regex:
                                found = True
                                tokens.append((state_regex[s], word[start_index:end_index - count]))
                                break
                    if not found:
                        tokens.clear()
                        line, column = find_line_by_index(word, end_index - 1)
                        tokens.append(("", "No viable alternative at character EOF, line {}".format(line)))
                        error = True

                    start_index = end_index - count
                else:
                    start_index = end_index
        return tokens

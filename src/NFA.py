from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        l = []
        q = []

        l.append(state)
        if (state, EPSILON) in self.d:
            for x in self.d[state, EPSILON]:
                q.append(x)

        while len(q) != 0:
            x = q.pop(0)
            if x not in l:
                l.append(x)
            if (x, EPSILON) in self.d:
                for y in self.d[x, EPSILON]:
                    if y not in l:
                        q.append(y)
        return set(l)

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        d = {}
        q = []
        visited = {}
        for s in self.S:
            d[str(999), s] = str(999)
        new_K = set()
        new_F = set()
        new_K.add(str(999))
        new_q0 = set(sorted(self.epsilon_closure(self.q0)))
        is_final = False
        for state in new_q0:
            if state in self.F:
                is_final = True
        if is_final:
            new_F.add(str(new_q0))

        q.append(new_q0)
        new_K.add(str(new_q0))
        while len(q) != 0:
            states_group = q.pop(0)
            for s in self.S:
                # print(s)
                next_group = []
                is_final = False
                for state in states_group:
                    if (state, s) in self.d:
                        zzz = self.d[state, s]
                        for z_state in zzz:
                            closure = self.epsilon_closure(z_state)
                            for close in closure:
                                if close not in next_group:
                                    next_group.append(close)
                                    if close in self.F:
                                        is_final = True

                next_group.sort()
                if len(next_group) != 0:
                    if is_final:
                        new_F.add(str(set(next_group)))
                    d[str(states_group), s] = str(set(next_group))

                    key = (str(next_group), s)
                    if key not in visited:
                        visited[key] = 1
                        q.append(set(next_group))
                        new_K.add(str(set(next_group)))
                else:
                    d[str(states_group), s] = str(999)

        return DFA(self.S, new_K, str(new_q0), d, new_F)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass

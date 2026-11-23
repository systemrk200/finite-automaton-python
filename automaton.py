class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = list(states)
        self.alphabet = set(alphabet)
        self.start_state = start_state
        self.final_states = set(final_states)
        self.transitions = {}
        for source, symbol, target in transitions:
            if source not in self.states or target not in self.states:
                raise ValueError(f"Переход ({source}, {symbol}, {target}) использует неизвестное состояние")
            if symbol not in self.alphabet:
                raise ValueError(f"Символ «{symbol}» не входит в алфавит")
            self.transitions.setdefault((source, symbol), set()).add(target)
        if start_state not in self.states:
            raise ValueError(f"Начальное состояние «{start_state}» не входит в список состояний")
        unknown_finals = self.final_states - set(self.states)
        if unknown_finals:
            raise ValueError(f"Финальные состояния не найдены: {', '.join(sorted(unknown_finals))}")

    def step(self, current, symbol):
        result = set()
        for state in current:
            result |= self.transitions.get((state, symbol), set())
        return result

    def run(self, word):
        path = [{self.start_state}]
        for symbol in word:
            if symbol not in self.alphabet:
                raise ValueError(f"Символ «{symbol}» не входит в алфавит")
            path.append(self.step(path[-1], symbol))
            if not path[-1]:
                break
        return path

    def accepts(self, word):
        path = self.run(word)
        return len(path) == len(word) + 1 and bool(path[-1] & self.final_states)

    def edge_labels(self):
        labels = {}
        for (source, symbol), targets in self.transitions.items():
            for target in targets:
                labels.setdefault((source, target), []).append(symbol)
        return labels

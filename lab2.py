
class FiniteAutomaton:

    def __init__(self, states, alphabet, transitions, start, final_states):
        self.states = states              # множество состояний
        self.alphabet = alphabet          # алфавит
        self.transitions = transitions    # (состояние, символ) → [список состояний]
        self.start = start                # начальное состояние
        self.final_states = final_states  # финальные состояния

    def is_deterministic(self):
        """
        Автомат детерминированный (DFA), если из каждого состояния
        по каждому символу ведёт МАКСИМУМ ОДИН переход.
        Если хотя бы один переход ведёт в два состояния → NDFA.
        """
        for (state, symbol), next_states in self.transitions.items():
            if len(next_states) > 1:
                return False
        return True

    def to_grammar(self):
        """
        Конвертирует конечный автомат в регулярную грамматику.
        Правила построения:
          Переход delta(A, a) = B         →  правило  A → aB
          Если B — финальное состояние    →  правило  A → a  (тоже добавляем)
        """
        rules = {}

        for (state, symbol), next_states in self.transitions.items():
            if state not in rules:
                rules[state] = []

            for next_state in next_states:
                # Основное правило: A → aB
                rules[state].append(f"{symbol}{next_state}")

                # Если следующее состояние финальное → добавляем A → a
                if next_state in self.final_states:
                    rules[state].append(symbol)

        return rules

    def to_dfa(self):
        """
        Конвертирует NDFA в DFA методом построения подмножеств.

        Идея: каждое состояние DFA = МНОЖЕСТВО состояний NDFA.
        Например, если из q1 по 'c' можно попасть и в q1 и в q2,
        то в DFA это одно состояние {q1, q2} = "q1q2".
        """
        # Начинаем с множества {start}
        start_set = frozenset([self.start])
        queue = [start_set]
        visited = set()

        dfa_transitions = {}
        dfa_final_states = set()

        while queue:
            current_set = queue.pop(0)

            if current_set in visited:
                continue
            visited.add(current_set)

            # Если это множество содержит финальное состояние → оно финальное в DFA
            if current_set & self.final_states:
                dfa_final_states.add(current_set)

            # Для каждого символа: куда можно попасть из текущего множества?
            for symbol in self.alphabet:
                next_set = set()

                for state in current_set:
                    if (state, symbol) in self.transitions:
                        next_set.update(self.transitions[(state, symbol)])

                if next_set:
                    next_frozen = frozenset(next_set)
                    dfa_transitions[(current_set, symbol)] = next_frozen

                    if next_frozen not in visited:
                        queue.append(next_frozen)

        # Переименовываем: {q0} → "q0",  {q1,q2} → "q1q2"
        def name(s):
            return "".join(sorted(s))

        dfa_transitions_named = {}
        for (s, sym), ns in dfa_transitions.items():
            dfa_transitions_named[(name(s), sym)] = name(ns)

        dfa_states = set(name(s) for s in visited)
        dfa_finals = set(name(s) for s in dfa_final_states)
        dfa_start  = name(start_set)

        return dfa_states, dfa_transitions_named, dfa_start, dfa_finals

#  ЗАПУСК

# Создаём NDFA из условия варианта 14
# Переходы: (состояние, символ) → [список возможных состояний]
ndfa_transitions = {
    ('q0', 'a'): ['q0'],
    ('q0', 'b'): ['q1'],
    ('q1', 'c'): ['q1', 'q2'],   # ← ДВА состояния = NDFA!
    ('q2', 'a'): ['q0'],
    ('q1', 'a'): ['q1'],
}

fa = FiniteAutomaton(
    states        = {'q0', 'q1', 'q2'},
    alphabet      = {'a', 'b', 'c'},
    transitions   = ndfa_transitions,
    start         = 'q0',
    final_states  = {'q2'}
)

# ── Задание a: DFA или NDFA? ──────────────────────────
print("=" * 50)
print("  Задание a: Детерминированность")
print("=" * 50)
if fa.is_deterministic():
    print("  Автомат: DFA (детерминированный)")
else:
    print("  Автомат: NDFA (недетерминированный)")
    print("  Причина: delta(q1, c) = {q1, q2}")
    print("  Из одного состояния по одному символу")
    print("  можно попасть в ДВА разных состояния.")

# ── Задание b: Автомат → Грамматика ──────────────────
print()
print("=" * 50)
print("  Задание b: Грамматика из автомата")
print("=" * 50)
grammar_rules = fa.to_grammar()
for nonterminal, rules in sorted(grammar_rules.items()):
    for rule in rules:
        print(f"  {nonterminal} -> {rule}")

# ── Задание c: NDFA → DFA ─────────────────────────────
print()
print("=" * 50)
print("  Задание c: Конвертация NDFA → DFA")
print("  (метод построения подмножеств)")
print("=" * 50)
dfa_states, dfa_trans, dfa_start, dfa_finals = fa.to_dfa()

print(f"  Состояния DFA : {sorted(dfa_states)}")
print(f"  Начальное     : {dfa_start}")
print(f"  Финальные     : {sorted(dfa_finals)}")
print()
print("  Переходы DFA:")
for (state, sym), next_state in sorted(dfa_trans.items()):
    mark = " <- финальное" if state in dfa_finals else ""
    print(f"    delta({state}, {sym}) -> {next_state}{mark}")

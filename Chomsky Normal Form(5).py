from itertools import combinations


class Grammar:
    """
    Context-free grammar.

    productions: dict[str, list[list[str]]]
        Maps each non-terminal to a list of right-hand sides.
        Each rhs is a list of symbols.  [] represents ε.
    """

    def __init__(self, non_terminals, terminals, productions, start):
        self.non_terminals = set(non_terminals)
        self.terminals = set(terminals)
        self.productions = {k: [list(r) for r in v] for k, v in productions.items()}
        self.start = start
        self._counter = 0

    # ── internal helpers ─────────────────────────────────────────────────────

    def _fresh(self):
        while True:
            self._counter += 1
            name = f'X{self._counter}'
            if name not in self.non_terminals and name not in self.terminals:
                return name

    def _add_rule(self, nt, rule):
        if rule not in self.productions.get(nt, []):
            self.productions.setdefault(nt, []).append(rule)

    # ── step 1 ───────────────────────────────────────────────────────────────

    def eliminate_epsilon(self):
        """
        Remove all ε-productions.

        First find every nullable non-terminal (one that can derive ε),
        then for each production add versions where some or all nullable
        symbols are dropped.  The ε rules themselves are removed at the end.
        Returns the set of nullable symbols found.
        """
        nullable = set()
        changed = True
        while changed:
            changed = False
            for nt, rules in self.productions.items():
                if nt in nullable:
                    continue
                for rule in rules:
                    if rule == [] or all(s in nullable for s in rule):
                        nullable.add(nt)
                        changed = True
                        break

        for nt in list(self.productions.keys()):
            original = list(self.productions[nt])
            for rule in original:
                positions = [i for i, s in enumerate(rule) if s in nullable]
                for k in range(1, len(positions) + 1):
                    for combo in combinations(positions, k):
                        new_rule = [s for i, s in enumerate(rule) if i not in combo]
                        if new_rule:
                            self._add_rule(nt, new_rule)

        for nt in self.productions:
            self.productions[nt] = [r for r in self.productions[nt] if r]

        return nullable

    # ── step 2 ───────────────────────────────────────────────────────────────

    def eliminate_unit_productions(self):
        """
        Remove all unit productions A → B where B is a single non-terminal.

        For each non-terminal A, compute the set of non-terminals reachable
        through unit productions (the unit closure).  A's new rule-set is the
        union of all non-unit rules from every member of that closure.
        """

        def unit_reach(start_nt):
            visited = {start_nt}
            stack = [start_nt]
            while stack:
                cur = stack.pop()
                for rule in self.productions.get(cur, []):
                    if (len(rule) == 1
                            and rule[0] in self.non_terminals
                            and rule[0] not in visited):
                        visited.add(rule[0])
                        stack.append(rule[0])
            return visited

        new_p = {nt: [] for nt in self.non_terminals}
        for nt in self.non_terminals:
            for sym in unit_reach(nt):
                for rule in self.productions.get(sym, []):
                    is_unit = len(rule) == 1 and rule[0] in self.non_terminals
                    if not is_unit and rule not in new_p[nt]:
                        new_p[nt].append(rule)
        self.productions = new_p

    # ── step 3 ───────────────────────────────────────────────────────────────

    def eliminate_inaccessible(self):
        """
        Remove every symbol that cannot be reached from the start symbol.

        A simple BFS/DFS from the start collects all reachable non-terminals;
        everything else is dropped.
        Returns the set of removed symbols.
        """
        reachable = {self.start}
        stack = [self.start]
        while stack:
            nt = stack.pop()
            for rule in self.productions.get(nt, []):
                for sym in rule:
                    if sym in self.non_terminals and sym not in reachable:
                        reachable.add(sym)
                        stack.append(sym)

        removed = self.non_terminals - reachable
        self.non_terminals = reachable
        for nt in removed:
            self.productions.pop(nt, None)
        return removed

    # ── step 4 ───────────────────────────────────────────────────────────────

    def eliminate_nonproductive(self):
        """
        Remove every symbol that cannot derive any string of terminals.

        A symbol is productive if at least one of its rules consists entirely
        of terminals and already-productive non-terminals.
        Returns the set of removed symbols.
        """
        productive = set()
        changed = True
        while changed:
            changed = False
            for nt, rules in self.productions.items():
                if nt in productive:
                    continue
                for rule in rules:
                    if all(s in self.terminals or s in productive for s in rule):
                        productive.add(nt)
                        changed = True
                        break

        removed = self.non_terminals - productive
        self.non_terminals = productive
        for nt in removed:
            self.productions.pop(nt, None)
        for nt in list(self.productions.keys()):
            self.productions[nt] = [
                r for r in self.productions[nt]
                if all(s in self.terminals or s in productive for s in r)
            ]
        return removed

    # ── step 5 ───────────────────────────────────────────────────────────────

    def to_cnf(self):
        """
        Convert to Chomsky Normal Form.

        Two kinds of new variables are introduced:
          - terminal proxies  T_x → x  (one per distinct terminal)
          - pair variables    P → A B  (one per distinct ordered pair of NTs,
                                        created during right-to-left binarisation)

        Rules of length 1 that are already A → a are left unchanged.
        Rules of length ≥ 2 first have every terminal replaced by its proxy,
        then are collapsed right-to-left until only a two-symbol rhs remains.
        """
        tv = {}   # terminal  →  proxy NT
        pv = {}   # (A, B)    →  pair NT

        def get_tv(t):
            if t not in tv:
                v = self._fresh()
                tv[t] = v
                self.non_terminals.add(v)
            return tv[t]

        def get_pv(a, b):
            if (a, b) not in pv:
                v = self._fresh()
                pv[(a, b)] = v
                self.non_terminals.add(v)
            return pv[(a, b)]

        result = {}
        for nt, rules in self.productions.items():
            result[nt] = []
            for rule in rules:
                if len(rule) == 1:
                    result[nt].append(rule)
                else:
                    syms = [get_tv(s) if s in self.terminals else s for s in rule]
                    while len(syms) > 2:
                        v = get_pv(syms[-2], syms[-1])
                        syms = syms[:-2] + [v]
                    result[nt].append(syms)

        for t, v in tv.items():
            result[v] = [[t]]
        for (a, b), v in pv.items():
            result[v] = [[a, b]]

        self.productions = result

    # ── verification ─────────────────────────────────────────────────────────

    def is_cnf(self):
        """Return True if every production is either A → a or A → B C."""
        for nt, rules in self.productions.items():
            for rule in rules:
                if len(rule) == 1:
                    if rule[0] not in self.terminals:
                        return False
                elif len(rule) == 2:
                    if any(s in self.terminals for s in rule):
                        return False
                else:
                    return False
        return True

    # ── display ──────────────────────────────────────────────────────────────

    def fmt(self):
        lines = []
        for nt in sorted(self.productions):
            parts = [' '.join(r) if r else 'ε' for r in self.productions[nt]]
            lines.append(f'  {nt} → {" | ".join(parts)}')
        return '\n'.join(lines)

    def print_grammar(self):
        print(self.fmt())

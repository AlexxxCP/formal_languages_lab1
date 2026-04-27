from cnf import Grammar


def convert(g):
    print("Original")
    g.print_grammar()
    print()

    nullable = g.eliminate_epsilon()
    print(f"Step 1 — epsilon removed  (nullable: {sorted(nullable)})")
    g.print_grammar()
    print()

    g.eliminate_unit_productions()
    print("Step 2 — unit productions removed")
    g.print_grammar()
    print()

    removed_inac = g.eliminate_inaccessible()
    label = sorted(removed_inac) if removed_inac else "none"
    print(f"Step 3 — inaccessible removed  ({label})")
    g.print_grammar()
    print()

    removed_np = g.eliminate_nonproductive()
    label = sorted(removed_np) if removed_np else "none"
    print(f"Step 4 — non-productive removed  ({label})")
    g.print_grammar()
    print()

    g.to_cnf()
    print("Step 5 — Chomsky Normal Form")
    g.print_grammar()
    print(f"  verified CNF: {g.is_cnf()}")
    print()


BAR = "=" * 56

# ── Variant 14 ────────────────────────────────────────────────
print(BAR)
print("Variant 14")
print("G = ({S,A,B,C,D}, {a,b}, P, S)")
print(BAR)

g14 = Grammar(
    non_terminals={'S', 'A', 'B', 'C', 'D'},
    terminals={'a', 'b'},
    productions={
        'S': [['a', 'B'], ['A']],
        'A': [['b', 'A', 'a'], ['a', 'S'], ['a']],
        'B': [['A', 'b', 'B'], ['B', 'S'], ['a'], []],   # [] = ε
        'C': [['B', 'A']],
        'D': [['a']],
    },
    start='S',
)
convert(g14)


# ── Bonus: a second grammar to show generality ────────────────
print(BAR)
print("Bonus — arbitrary grammar")
print("G = ({S,A,B,C}, {a,b,c}, P, S)")
print(BAR)

g_bonus = Grammar(
    non_terminals={'S', 'A', 'B', 'C'},
    terminals={'a', 'b', 'c'},
    productions={
        'S': [['A', 'B'], ['B', 'C']],
        'A': [['B', 'A'], ['a']],
        'B': [['C', 'C'], ['b'], []],
        'C': [['A', 'B'], ['a']],
    },
    start='S',
)
convert(g_bonus)

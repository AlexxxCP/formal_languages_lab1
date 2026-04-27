"""
main.py — demonstrates the regex generator on Variant 2 patterns

Run:
    python3 main.py
"""

from regex import tokenise, generate, show_processing

# ── Variant 2 patterns ─────────────────────────────────────────────────────────

PATTERNS = [
    "M?N{2}(O|P){3}Q*R*",
    "(X|Y|Z){3}8+(9|0)",
    "(H|I)(J|K)L*N?",
]

READABLE = [
    "M?  N²  (O|P)³  Q*  R*",
    "(X|Y|Z)³  8+  (9|0)",
    "(H|I)  (J|K)  L*  N?",
]


# ── Section 1: token stream ────────────────────────────────────────────────────

print("--- Token stream for each pattern ---\n")

for pat, readable in zip(PATTERNS, READABLE):
    print(f"pattern:  {pat}")
    print(f"readable: {readable}")
    tokens = tokenise(pat)
    for tok in tokens:
        print(f"  {tok}")
    print()


# ── Section 2: generated samples ──────────────────────────────────────────────

print("--- Generated samples (10 per pattern) ---\n")

for pat, readable in zip(PATTERNS, READABLE):
    samples = [generate(pat) for _ in range(10)]
    print(f"pattern:  {pat}")
    print(f"readable: {readable}")
    print(f"samples:  {', '.join(samples)}\n")


# ── Section 3: step-by-step trace (bonus) ─────────────────────────────────────

print("--- Step-by-step processing trace (bonus) ---")

for pat in PATTERNS:
    show_processing(pat)


# ── Section 4: interactive mode ───────────────────────────────────────────────

print("--- Interactive mode ---")
print("Enter a pattern to generate strings from it, or 'quit' to exit.")
print("Syntax: literals  ?  *  +  {n}  (A|B|C)")
print("Example: A?(B|C){2}D*\n")

while True:
    try:
        pat = input("pattern> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        break
    if not pat:
        continue
    if pat.lower() in ("quit", "exit", "q"):
        print("Bye!")
        break
    try:
        show_processing(pat)
        print("5 more samples:", ", ".join(generate(pat) for _ in range(5)), "\n")
    except Exception as e:
        print(f"error: {e}\n")

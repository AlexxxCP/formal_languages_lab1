import random
import sys
import io
from regex import tokenise, generate, show_processing, MAX_REPEAT

random.seed(42)   # fixed seed so the report is reproducible

PATTERNS = [
    ("M?N{2}(O|P){3}Q*R*",  "M?  N²  (O|P)³  Q*  R*"),
    ("(X|Y|Z){3}8+(9|0)",   "(X|Y|Z)³  8+  (9|0)"),
    ("(H|I)(J|K)L*N?",      "(H|I)  (J|K)  L*  N?"),
]


# ── capture helpers ────────────────────────────────────────────────────────────

def capture_tokens(pattern):
    lines = []
    for tok in tokenise(pattern):
        lines.append(f"  {tok}")
    return "\n".join(lines)


def capture_samples(pattern, n=10):
    return ", ".join(generate(pattern) for _ in range(n))


def capture_trace(pattern):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    show_processing(pattern)
    sys.stdout = old
    return buf.getvalue().strip()


# ── build report ──────────────────────────────────────────────────────────────

tok1  = capture_tokens(PATTERNS[0][0])
tok2  = capture_tokens(PATTERNS[1][0])
tok3  = capture_tokens(PATTERNS[2][0])

s1    = capture_samples(PATTERNS[0][0])
s2    = capture_samples(PATTERNS[1][0])
s3    = capture_samples(PATTERNS[2][0])

tr1   = capture_trace(PATTERNS[0][0])
tr2   = capture_trace(PATTERNS[1][0])
tr3   = capture_trace(PATTERNS[2][0])

report = f"""# Laboratory Work #3 — Regular Expressions

**Course:** Formal Languages & Finite Automata  
**Student:** Luchiciov Alexei
**Group:** FAF-241

---

## Objectives

1. Understand what regular expressions are and what they are used for.
2. Write a program that dynamically generates valid strings from a given regular expression — not hardcoded outputs, but a real interpreter.
3. Bonus: implement a function that shows the step-by-step processing sequence of a regular expression.

---

## Theory

A **regular expression** is a compact notation for describing a set of strings — formally called a *regular language*. They are built from three primitives:

- a literal character matches exactly that character
- `R|S` (alternation) matches either R or S
- `RS` (concatenation) matches R followed by S
- `R*` (Kleene star) matches R zero or more times

Everything else is shorthand derived from these three rules:

| Notation | Meaning |
|----------|---------|
| `R?` | zero or one occurrence of R |
| `R+` | one or more occurrences of R |
| `R{{n}}` | exactly *n* occurrences of R |
| `(A\\|B\\|C)` | one of the listed alternatives |

Regular expressions have a direct relationship with finite automata — every regular expression can be converted into an NFA (Thompson's construction), and every DFA accepts exactly the strings described by some regular expression. In practice this means that recognising whether a string matches a pattern is equivalent to simulating a finite automaton on that string.

Regular expressions are used everywhere: input validation, lexical analysis (the first stage of every compiler), search and replace in text editors, log parsing, URL routing, and protocol specification.

---

## Variant 2 — Patterns

The three patterns assigned to Variant 2 are given in handwritten superscript notation. They are translated into the program's syntax using `{{n}}` for exact repetition (`^n` would be ambiguous when the next character is itself a digit):

| # | Handwritten | Program syntax | Description |
|---|-------------|----------------|-------------|
| 1 | M?N²(O\\|P)³Q\\*R\\* | `M?N{{2}}(O\\|P){{3}}Q*R*` | optional M, two N's, three O/P choices, any Q's, any R's |
| 2 | (X\\|Y\\|Z)³8⁺(9\\|0) | `(X\\|Y\\|Z){{3}}8+(9\\|0)` | three X/Y/Z choices, one-or-more 8's, a 9 or 0 |
| 3 | (H\\|I)(J\\|K)L\\*N? | `(H\\|I)(J\\|K)L*N?` | H or I, then J or K, any number of L's, optional N |

Cross-check against the examples given in the assignment:

| String | Pattern | Valid? | Explanation |
|--------|---------|--------|-------------|
| MNNOOOQR | `M?N{{2}}(O\\|P){{3}}Q*R*` | ✅ | M×1, N×2, O×3, Q×1, R×1 |
| NNPPPQQQRRR | `M?N{{2}}(O\\|P){{3}}Q*R*` | ✅ | M×0, N×2, P×3, Q×3, R×3 |
| XXX89 | `(X\\|Y\\|Z){{3}}8+(9\\|0)` | ✅ | X×3, 8×1, 9 |
| YYY88889 | `(X\\|Y\\|Z){{3}}8+(9\\|0)` | ✅ | Y×3, 8×4, 9 |
| HJLLN | `(H\\|I)(J\\|K)L*N?` | ✅ | H, J, L×2, N×1 |
| IKLLLLL | `(H\\|I)(J\\|K)L*N?` | ✅ | I, K, L×5, N×0 |

---

## Implementation

### Design

The program is split into two files. `regex.py` contains all the core logic; `main.py` is the demo runner.

```
pattern string
      |
      v
  tokenise()        -- parser: breaks the pattern into a list of Token objects
      |
      v
  generate()        -- generator: walks the tokens, resolves quantifiers randomly
      |
      v
  show_processing() -- bonus: same walk, but prints each step before building the result
```

None of the functions contain any knowledge of the specific Variant-2 patterns. Any pattern string can be passed in.

### Token class

Each element of the pattern becomes a `Token` with three fields:

```python
class Token:
    def __init__(self, kind, value, quantifier):
        self.kind       = kind        # 'char' | 'group'
        self.value      = value       # str  | list[str]
        self.quantifier = quantifier  # '1' | '?' | '*' | '+' | ('n', int)
```

Quantifier values:

| Value | Meaning |
|-------|---------|
| `'1'` | exactly once (default) |
| `'?'` | 0 or 1 |
| `'*'` | 0 to MAX\\_REPEAT |
| `'+'` | 1 to MAX\\_REPEAT |
| `('n', k)` | exactly k |

`MAX_REPEAT` is set to {MAX_REPEAT} so that `*` and `+` never produce infinitely long strings.

### Tokeniser

`tokenise()` scans the pattern left to right with a position index:

- When it sees `(`, it uses a depth counter to find the matching `)`, splits the body on `|` to get the alternatives, then reads the quantifier that follows.
- For any other character it reads one literal, then reads its quantifier.
- `_read_quantifier()` handles `?`, `*`, `+`, and `{{n}}`. The curly-brace form is unambiguous because `{{` and `}}` cannot appear as literal characters in the pattern.

```python
def tokenise(pattern):
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == '(':
            depth, j = 1, i + 1
            while j < len(pattern) and depth > 0:
                if   pattern[j] == '(': depth += 1
                elif pattern[j] == ')': depth -= 1
                j += 1
            alternatives = pattern[i + 1:j - 1].split('|')
            quant, skip  = _read_quantifier(pattern, j)
            tokens.append(Token('group', alternatives, quant))
            i = j + skip
        elif ch not in ')|?*+{{':
            i += 1
            quant, skip = _read_quantifier(pattern, i)
            tokens.append(Token('char', ch, quant))
            i += skip
        else:
            i += 1
    return tokens
```

### Generator

`generate()` walks the token list and builds the output string. `_resolve()` turns a quantifier into a concrete integer using `random.randint` for `?`, `*`, and `+`:

```python
def generate(pattern):
    parts = []
    for token in tokenise(pattern):
        n = _resolve(token.quantifier)
        if token.kind == 'char':
            parts.append(token.value * n)
        else:
            parts.extend(random.choice(token.value) for _ in range(n))
    return ''.join(parts)
```

### Bonus — step-by-step trace

`show_processing()` works the same way as `generate()` but prints each decision before accumulating the result:

```python
def show_processing(pattern):
    print(f"\\nPattern: {{pattern}}")
    tokens = tokenise(pattern)
    parts  = []
    for step, token in enumerate(tokens, 1):
        n = _resolve(token.quantifier)
        if token.kind == 'char':
            piece = token.value * n
            print(f"  step {{step}}: char '{{token.value}}', {{_quant_label(token.quantifier)}}, chose {{n}} -> '{{piece}}'")
        else:
            chosen = [random.choice(token.value) for _ in range(n)]
            piece  = ''.join(chosen)
            alts   = ' | '.join(token.value)
            print(f"  step {{step}}: group ({{alts}}), {{_quant_label(token.quantifier)}}, chose {{n}} -> '{{piece}}'")
        parts.append(piece)
    print(f"  result: {{''.join(parts)}}\\n")
```

---

## How to Run

Requires Python 3.8 or newer. No third-party packages needed.

```bash
python3 main.py
```

The program runs four sections automatically: token stream, generated samples, step-by-step trace, and an interactive prompt.

---

## Results

### Token stream

**Pattern 1 — `M?N{{2}}(O|P){{3}}Q*R*`**
```
{tok1}
```

**Pattern 2 — `(X|Y|Z){{3}}8+(9|0)`**
```
{tok2}
```

**Pattern 3 — `(H|I)(J|K)L*N?`**
```
{tok3}
```

### Generated samples (10 per pattern)

**Pattern 1 — `M?N{{2}}(O|P){{3}}Q*R*`**
```
{s1}
```

**Pattern 2 — `(X|Y|Z){{3}}8+(9|0)`**
```
{s2}
```

**Pattern 3 — `(H|I)(J|K)L*N?`**
```
{s3}
```

### Step-by-step trace (bonus)

**Pattern 1**
```
{tr1}
```

**Pattern 2**
```
{tr2}
```

**Pattern 3**
```
{tr3}
```

---

## Project Structure

```
laboratory-work-3/
├── regex.py            — Token class, tokenise(), generate(), show_processing()
├── main.py             — four demo sections and interactive prompt
└── generate_report.py  — generates this report automatically
```

---

## Relation to Finite Automata

Generating strings from a regular expression is the inverse of the recognition problem, but it exercises the same structure. The tokeniser is a hand-written DFA where each branch corresponds to a state:

| State | Entry condition | What it does |
|-------|----------------|--------------|
| GROUP | `(` | depth-count to find `)`, collect alternatives, read quantifier |
| CHAR | any literal | read one character, read quantifier |
| QUANTIFIER | `?`, `*`, `+`, `{{` | classify and consume the quantifier |

The generator then runs a second pass equivalent to simulating an NFA on a randomly chosen path — at each alternation it picks a branch, at each Kleene star it picks a repetition count within the allowed bounds.

---

## Difficulties

The main difficulty was the notation for exact repetition. The first version used `^n` (e.g. `(X|Y|Z)^38+(9|0)`), but the parser read `^38` as "repeat 38 times" and never saw the character `8` at all. Switching to `{{n}}` fixed this completely because curly braces are not valid literal characters, so the parser always knows it is reading a repetition count.

---

## Conclusions

- The generator correctly produces strings matching all three Variant-2 patterns, verified against the assignment examples.
- The implementation is fully dynamic — the pattern is parsed at runtime, and adding a new pattern requires no code changes.
- The step-by-step trace makes it easy to follow which decision was made at each point in the pattern.
- The interactive mode lets any custom pattern be tested immediately without restarting the program.

---

## References

Cretu Dumitru, Vasile Drumea, Irina Cojuhari — FLFA course materials.  
Hopcroft, Motwani, Ullman — *Introduction to Automata Theory, Languages, and Computation*, 3rd ed., Chapter 3.  
Wikipedia — Regular expression: https://en.wikipedia.org/wiki/Regular_expression  

---

**Date:** March 2026  
**Repository:** [GitHub Link]
"""

with open("REPORT.md", "w", encoding="utf-8") as f:
    f.write(report)

print("REPORT.md written successfully.")

# Laboratory Work #4 — Regular Expressions

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
| `R{n}` | exactly n occurrences of R |
| `(A\|B\|C)` | one of the listed alternatives |

Regular expressions have a direct relationship with finite automata — every regular expression can be converted into an NFA via Thompson's construction, and every DFA accepts exactly the strings described by some regular expression. In practice this means that recognising whether a string matches a pattern is equivalent to simulating a finite automaton on that string.

Regular expressions are used everywhere: input validation, lexical analysis (the first stage of every compiler), search and replace in text editors, log parsing, URL routing, and protocol specification.

---

## Implementation

### Language and Variant

The program targets **Variant 2**, which defines three patterns in handwritten superscript notation. Rather than targeting an existing language, a small custom pattern syntax is used — this makes every quantifier form exercisable without the ambiguity of standard regex dialects. The patterns use `{n}` for exact repetition, `?`/`+`/`*` for standard quantifiers, and `(A|B|C)` for alternation.

| # | Handwritten | Program syntax | Description |
|---|-------------|----------------|-------------|
| 1 | M?N²(O\|P)³Q\*R\* | `M?N{2}(O\|P){3}Q*R*` | optional M, two N's, three O/P choices, any Q's, any R's |
| 2 | (X\|Y\|Z)³8⁺(9\|0) | `(X\|Y\|Z){3}8+(9\|0)` | three X/Y/Z choices, one-or-more 8's, a 9 or 0 |
| 3 | (H\|I)(J\|K)L\*N? | `(H\|I)(J\|K)L*N?` | H or I, then J or K, any number of L's, optional N |

Cross-check against the examples given in the assignment:

| String | Pattern | Valid? | Explanation |
|--------|---------|--------|-------------|
| MNNOOOQR | `M?N{2}(O\|P){3}Q*R*` | ✅ | M×1, N×2, O×3, Q×1, R×1 |
| NNPPPQQQRRR | `M?N{2}(O\|P){3}Q*R*` | ✅ | M×0, N×2, P×3, Q×3, R×3 |
| XXX89 | `(X\|Y\|Z){3}8+(9\|0)` | ✅ | X×3, 8×1, 9 |
| YYY88889 | `(X\|Y\|Z){3}8+(9\|0)` | ✅ | Y×3, 8×4, 9 |
| HJLLN | `(H\|I)(J\|K)L*N?` | ✅ | H, J, L×2, N×1 |
| IKLLLLL | `(H\|I)(J\|K)L*N?` | ✅ | I, K, L×5, N×0 |

### Design

The program is split into two files. `regex.py` contains all the core logic; `main.py` is the demo runner.

```
pattern string
      |
      v
  tokenise()        -- parser: breaks the pattern into a list of Token tuples
      |
      v
  generate()        -- generator: walks the tokens, resolves quantifiers randomly
      |
      v
  show_processing() -- bonus: same walk, but prints each step before building the result
```

None of the functions contain any knowledge of the specific Variant 2 patterns. Any pattern string can be passed in.

### Token Structure

Each element of the pattern becomes a tuple with three fields:

```python
(kind, value, quantifier)
#  'char' | 'group'
#  str    | list[str]
#  '1' | '?' | '*' | '+' | ('n', int)
```

Quantifier values:

| Value | Meaning |
|-------|---------|
| `'1'` | exactly once (default) |
| `'?'` | 0 or 1 |
| `'*'` | 0 to MAX_REPEAT |
| `'+'` | 1 to MAX_REPEAT |
| `('n', k)` | exactly k |

`MAX_REPEAT` is set to 5 so that `*` and `+` never produce infinitely long strings.

### Tokeniser

`tokenise()` scans the pattern left to right with a position index:

- When it sees `(`, it uses a depth counter to find the matching `)`, splits the body on `|` to get the alternatives, then reads the quantifier that follows.
- For any other character it reads one literal, then reads its quantifier.
- `parse_quantifier()` handles `?`, `*`, `+`, and `{n}`. The curly-brace form is unambiguous because `{` and `}` cannot appear as literal characters in the pattern.

```python
def tokenise(pattern):
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == '(':
            depth, j = 1, i + 1
            while j < len(pattern) and depth > 0:
                if pattern[j] == '(':   depth += 1
                elif pattern[j] == ')': depth -= 1
                j += 1
            alternatives = pattern[i + 1:j - 1].split('|')
            quant, skip = parse_quantifier(pattern, j)
            tokens.append(('group', alternatives, quant))
            i = j + skip
        elif ch not in ')|?*+{':
            i += 1
            quant, skip = parse_quantifier(pattern, i)
            tokens.append(('char', ch, quant))
            i += skip
        else:
            i += 1
    return tokens
```

### Generator

`generate()` walks the token list and builds the output string. `repeat_count()` turns a quantifier into a concrete integer using `random.randint` for `?`, `*`, and `+`:

```python
def generate(pattern):
    parts = []
    for kind, value, quant in tokenise(pattern):
        n = repeat_count(quant)
        if kind == 'char':
            parts.append(value * n)
        else:
            parts.extend(random.choice(value) for _ in range(n))
    return ''.join(parts)
```

### Bonus — Step-by-step Trace

`show_processing()` works identically to `generate()` but prints each decision before accumulating the result:

```python
def show_processing(pattern):
    print(f"Pattern: {pattern}")
    tokens = tokenise(pattern)
    parts = []
    for step, (kind, value, quant) in enumerate(tokens, 1):
        n = repeat_count(quant)
        if kind == 'char':
            piece = value * n
            print(f"  step {step}: char '{value}', {quant_description(quant)}, chose {n} -> '{piece}'")
        else:
            chosen = [random.choice(value) for _ in range(n)]
            piece = ''.join(chosen)
            print(f"  step {step}: group ({' | '.join(value)}), {quant_description(quant)}, chose {n} -> '{piece}'")
        parts.append(piece)
    print(f"  result: {''.join(parts)}")
```

---

## How to Run

Requires Python 3.8 or newer, no third-party packages.

```bash
python3 main.py
```

The program runs four sections automatically: token stream, generated samples, step-by-step trace, and an interactive prompt.

---

## Results

### Token Stream

**Pattern 1 — `M?N{2}(O|P){3}Q*R*`**

```
Token(kind='char',  value='M',        quantifier='?')
Token(kind='char',  value='N',        quantifier=('n', 2))
Token(kind='group', value=['O', 'P'], quantifier=('n', 3))
Token(kind='char',  value='Q',        quantifier='*')
Token(kind='char',  value='R',        quantifier='*')
```

**Pattern 2 — `(X|Y|Z){3}8+(9|0)`**

```
Token(kind='group', value=['X', 'Y', 'Z'], quantifier=('n', 3))
Token(kind='char',  value='8',             quantifier='+')
Token(kind='group', value=['9', '0'],      quantifier='1')
```

**Pattern 3 — `(H|I)(J|K)L*N?`**

```
Token(kind='group', value=['H', 'I'], quantifier='1')
Token(kind='group', value=['J', 'K'], quantifier='1')
Token(kind='char',  value='L',        quantifier='*')
Token(kind='char',  value='N',        quantifier='?')
```

### Generated Samples (10 per pattern)

**Pattern 1 — `M?N{2}(O|P){3}Q*R*`**

```
NNOPOQR, NNOPO, NNOOOQQQQQRRRRR, MNNOPPR, MNNPPOQRR, NNOPOQQRR, MNNOPOQQQ, MNNPOORRRRR, NNPOORRR, MNNPPOQQRR
```

**Pattern 2 — `(X|Y|Z){3}8+(9|0)`**

```
XZY89, ZZX880, YYZ888889, ZYX889, YYY89, ZZY880, YZY880, XXZ888880, ZZY888880, YXX888880
```

**Pattern 3 — `(H|I)(J|K)L*N?`**

```
HJ, HKLLLL, IKLLLLN, IJLLLLL, IKN, IJLLL, IJLLLL, IJLN, HJLLLLN, IJN
```

### Step-by-step Trace (Bonus)

**Pattern 1 — `M?N{2}(O|P){3}Q*R*`**

```
Pattern: M?N{2}(O|P){3}Q*R*
  step 1: char 'M', 0 or 1 (optional), chose 0 -> ''
  step 2: char 'N', exactly 2, chose 2 -> 'NN'
  step 3: group (O | P), exactly 3, chose 3 -> 'OPO'
  step 4: char 'Q', 0 to 5 (zero or more), chose 1 -> 'Q'
  step 5: char 'R', 0 to 5 (zero or more), chose 1 -> 'R'
  result: NNOPOQR
```

**Pattern 2 — `(X|Y|Z){3}8+(9|0)`**

```
Pattern: (X|Y|Z){3}8+(9|0)
  step 1: group (X | Y | Z), exactly 3, chose 3 -> 'ZXZ'
  step 2: char '8', 1 to 5 (one or more), chose 5 -> '88888'
  step 3: group (9 | 0), exactly 1, chose 1 -> '9'
  result: ZXZ888889
```

**Pattern 3 — `(H|I)(J|K)L*N?`**

```
Pattern: (H|I)(J|K)L*N?
  step 1: group (H | I), exactly 1, chose 1 -> 'I'
  step 2: group (J | K), exactly 1, chose 1 -> 'J'
  step 3: char 'L', 0 to 5 (zero or more), chose 0 -> ''
  step 4: char 'N', 0 or 1 (optional), chose 0 -> ''
  result: IJ
```

---

## Project Structure

```
laboratory-work-4/
├── regex.py   — Token structure, tokenise(), generate(), show_processing()
├── main.py    — four demo sections and interactive prompt
└── README.md  — this report
```

---

## Relation to Finite Automata

Generating strings from a regular expression is the inverse of the recognition problem, but it exercises the same structure. The tokeniser is a hand-written DFA where each branch corresponds to a state:

| State | Entry condition | What it does |
|-------|----------------|--------------|
| GROUP | `(` | depth-count to find `)`, collect alternatives, read quantifier |
| CHAR | any literal | read one character, read quantifier |
| QUANTIFIER | `?`, `*`, `+`, `{` | classify and consume the quantifier symbol |

The generator then runs a second pass equivalent to simulating an NFA on a randomly chosen path — at each alternation it picks a branch, at each Kleene star it picks a repetition count within the allowed bounds. This mirrors the NFA simulation studied in Lab 2, where non-deterministic choices correspond exactly to `random.choice()` calls here.

---

## Difficulties

The main difficulty was the notation for exact repetition. The first version used `^n` (e.g. `(X|Y|Z)^38+(9|0)`), but the parser read `^38` as "repeat 38 times" and never saw the character `8` at all. Switching to `{n}` fixed this completely because curly braces are not valid literal characters in the pattern, so the parser always knows it is reading a repetition count and not a literal.

---

## Conclusions

- The generator correctly produces strings matching all three Variant 2 patterns, verified against the assignment examples.
- The implementation is fully dynamic — the pattern is parsed at runtime, and adding a new pattern requires no code changes.
- All five quantifier forms (`1`, `?`, `*`, `+`, `{n}`) are handled uniformly through a single `repeat_count()` function.
- The step-by-step trace makes it easy to follow which decision was made at each point in the pattern.
- The interactive mode lets any custom pattern be tested immediately without restarting the program.
- The implementation visibly mirrors NFA theory: each alternation group corresponds to a non-deterministic branch studied in Lab 2.

---

## References

Cretu Dumitru, Vasile Drumea, Irina Cojuhari — FLFA course materials.  
Hopcroft, Motwani, Ullman — *Introduction to Automata Theory, Languages, and Computation*, 3rd ed., Chapter 3.  
Wikipedia — Regular expression: https://en.wikipedia.org/wiki/Regular_expression

---

**Date:** March 2026  
**Repository:** [GitHub Link]

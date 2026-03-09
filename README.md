# Laboratory Work #1 - Formal Languages and Finite Automata
**Course:** Formal Languages & Finite Automata  
**Variant:** 14  
**Date:** February 2026

---

## Objectives
1. Understand formal language components (alphabet, grammar, productions)
2. Implement a Grammar class that generates valid strings
3. Convert Grammar to Finite Automaton
4. Implement string validation using the Finite Automaton

---

## Grammar Specification

Variant 14:

```
VN = {S, B, D}          // Non-terminal symbols
VT = {a, b, c, d}       // Terminal symbols
S  = S                  // Start symbol

Production Rules (P):
    S → aS              // Can repeat 'a' at start
    S → bB              // Transition to state B
    B → cB              // Can repeat 'c'
    B → d               // Terminal production
    B → aD              // Transition to state D
    D → aB              // Transition back to B
    D → b               // Terminal production
```

This is a right-linear regular grammar (Type 3 in Chomsky hierarchy).

---

## Implementation

### 1. Grammar Class (`grammar.py`)

**Features:**
- Stores grammar components (VN, VT, P, S)
- `generate_string()` — Randomly generates valid strings by applying production rules
- `to_finite_automaton()` — Converts grammar to equivalent FA

**Algorithm for string generation:**
1. Start with symbol S
2. Randomly select applicable production rule
3. Apply rule and replace non-terminal
4. Repeat until only terminals remain

### 2. Finite Automaton Class (`finite_automaton.py`)

**Features:**
- Stores FA components (Q, Σ, δ, q0, F)
- `string_belong_to_language()` — Validates if string is accepted

**Algorithm for validation:**
1. Start from initial state q0
2. Read each symbol and follow transitions
3. Accept if final state F is reached after reading entire string

### 3. Main Program (`main.py`)

Demonstrates all functionality:
- Creates Grammar instance
- Generates 5 example strings
- Converts Grammar → FA
- Tests validation on multiple test strings

---

## How to Run

**Requirements:** Python 3.8+

```bash
# Run the program
python3 lab1.py
```

**Expected Output:**
- 5 generated valid strings
- Finite Automaton transitions table
- Validation results for test strings

---

## Results

### Generated Strings Examples
```
1. bd
2. aaaabd
3. bab
4. abcccd
5. abd
```

### Automaton Structure

**States (Q):** `{S, B, D, F}`  
**Alphabet (Σ):** `{a, b, c, d}`  
**Initial State (q0):** `S`  
**Final States (F):** `{F}`  

**Transition Function (δ):**

| State     | a | b    | c | d    |
|-----------|---|------|---|------|
| S (start) | S | B    | - | -    |
| B         | D | -    | B | F ✓  |
| D         | B | F ✓  | - | -    |
| F ✓       | - | -    | - | -    |

`F ✓` = transition to final/accepting state

### String Validation Examples

**Accepted strings:**

- `bd` ✓ — Path: `S →(b) B →(d) F`
- `abd` ✓ — Path: `S →(a) S →(b) B →(d) F`
- `bab` ✓ — Path: `S →(b) B →(a) D →(b) F`
- `abcccd` ✓ — Path: `S →(a) S →(b) B →(c)→(c)→(c) B →(d) F`
- `aaaabd` ✓ — Path: `S →(a)→(a)→(a)→(a) S →(b) B →(d) F`

**Rejected strings:**

- `abc` ✗ — B has no transition on `c` after `a`
- `aaa` ✗ — No terminal state reached
- `ba`  ✗ — B has no transition on `a` alone
- `cd`  ✗ — No transition from S on `c`
- `""`  ✗ — Empty string never reaches final state

---

## Conversion Process: Grammar → FA

**Conversion Rules:**
- Each non-terminal becomes a state
- Add one final state `F`
- For rule `A → aB`: create transition `δ(A, a) = B`
- For rule `A → a`:  create transition `δ(A, a) = F`

**Example:**
- Production `S → aS` becomes `δ(S, a) = S` (self-loop)
- Production `B → d`  becomes `δ(B, d) = F` (to final state)

---

## Language Properties

**Accepted String Patterns:**

`a*b(c*d)` — Any number of 'a's, then 'b', then any 'c's, ending with 'd'
- Examples: `bd`, `abd`, `aaaabd`, `abcccd`

`a*ba(ab)*b` — Through D state, ending in 'b'
- Examples: `bab`, `abab`

**Minimal String:** `bd` (length = 2)

**Key Characteristics:**
- Must start with `a` (repeated) or `b`
- Must end with `b` or `d` (terminal productions)
- Regular language (can be recognized by finite automaton)

---

## Conclusions

✅ Successfully implemented Grammar class for Variant 14  
✅ String generation algorithm works correctly with recursive productions  
✅ Grammar to FA conversion follows standard rules  
✅ Finite Automaton correctly validates all test strings  
✅ Demonstrated equivalence between regular grammar and finite automaton  

**Key Learning:**
- Regular grammars can be mechanically converted to finite automata
- Both representations describe the same language
- FA provides efficient string validation (O(n) time complexity)

---

## References
- Course materials: *"Formal Languages & Finite Automata"* by Cretu Dumitru
- Hopcroft, J. E., et al. (2006). *Introduction to Automata Theory, Languages, and Computation*

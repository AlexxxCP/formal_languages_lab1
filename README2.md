# Laboratory Work #2 - Determinism in Finite Automata. NDFA to DFA. Chomsky Hierarchy.
**Course:** Formal Languages & Finite Automata  
**Variant:** 14  Luchiciov Alexei FAF-241


---

## Objectives
1. Understand what determinism means in finite automata
2. Classify the grammar from Lab 1 based on Chomsky hierarchy
3. Convert a Finite Automaton to a regular grammar
4. Determine whether the given FA is deterministic or non-deterministic
5. Implement conversion from NDFA to DFA

---

## Given Finite Automaton

Variant 14:

```
Q  = {q0, q1, q2}       // States
∑  = {a, b, c}          // Alphabet
F  = {q2}               // Final states
q0 = q0                 // Start state

Transition function (δ):
    δ(q0, a) = q0       // Self-loop on 'a'
    δ(q0, b) = q1       // Move to q1 on 'b'
    δ(q1, c) = q1       // Self-loop on 'c'  ← same input, two outputs = NDFA!
    δ(q1, c) = q2       // Move to q2 on 'c' ←
    δ(q2, a) = q0       // Move back to q0
    δ(q1, a) = q1       // Self-loop on 'a'
```

---

## Chomsky Hierarchy Classification (Grammar from Lab 1)

The grammar from Variant 14 (Lab 1):

```
VN = {S, B, D}
VT = {a, b, c, d}

Production Rules:
    S → aS
    S → bB
    B → cB
    B → d
    B → aD
    D → aB
    D → b
```

**Classification rules:**
- **Type 3** (Regular):           all rules are `A → a` or `A → aB`
- **Type 2** (Context-Free):      left side is always a single non-terminal
- **Type 1** (Context-Sensitive): left side length ≤ right side length
- **Type 0** (Unrestricted):      no restrictions

**Result:** ✅ **Type 3 — Regular Grammar**

Every rule is either `A → a` (single terminal) or `A → aB` (terminal + non-terminal).  
This satisfies the definition of a right-linear regular grammar.

---

## Implementation

### 1. Chomsky Classification (`classify()`)

**Algorithm:**
1. Check if every left-hand side is a single non-terminal
2. Check if every right-hand side is `a` or `aB`
3. If both conditions hold → Type 3 (Regular)
4. If only condition 1 holds → Type 2 (Context-Free)
5. Otherwise → Type 1 or Type 0

### 2. FA to Grammar Conversion (`to_grammar()`)

**Conversion Rules:**
- Each state becomes a non-terminal
- `δ(A, a) = B`        →  rule `A → aB`
- `δ(A, a) = B` where B is final  →  also add rule `A → a`

**Example:**
- `δ(q0, b) = q1`  becomes  `q0 → bq1`
- `δ(q1, c) = q2`  becomes  `q1 → cq2` and `q1 → c` (since q2 is final)

### 3. Determinism Check (`is_deterministic()`)

An automaton is **deterministic (DFA)** if for every state and every symbol  
there is **at most one** possible next state.

If any `(state, symbol)` pair leads to **two or more** states → **NDFA**.

### 4. NDFA to DFA Conversion (`to_dfa()`)

Uses the **Subset Construction** (Powerset) method:

**Algorithm:**
1. Start with the set `{q0}` as the initial DFA state
2. For each symbol, compute which NDFA states are reachable
3. Each reachable set becomes a new DFA state
4. A DFA state is final if it contains any NDFA final state
5. Repeat until no new states are found

---

## How to Run

**Requirements:** Python 3.8+

```bash
# Run the program
python3 lab2.py
```

**Expected Output:**
- Determinism check result
- Grammar rules derived from the automaton
- DFA states, transitions and final states

---

## Results

### Task a — Determinism Check

```
Automaton: NDFA (non-deterministic)
Reason: δ(q1, c) = {q1, q2}
From one state on one symbol → TWO different next states.
```

| (State, Symbol) | Next States  | Deterministic? |
|-----------------|--------------|----------------|
| (q0, a)         | {q0}         | ✓ Yes          |
| (q0, b)         | {q1}         | ✓ Yes          |
| (q1, c)         | {q1, q2}     | ✗ No — NDFA!   |
| (q1, a)         | {q1}         | ✓ Yes          |
| (q2, a)         | {q0}         | ✓ Yes          |

**Conclusion:** The automaton is **NDFA** because `δ(q1, c)` produces two states.

---

### Task b — FA to Regular Grammar

Derived grammar rules from the automaton:

```
q0 → aq0
q0 → bq1
q1 → cq1
q1 → cq2
q1 → c        ← added because q2 is a final state
q1 → aq1
q2 → aq0
```

| Non-terminal | Rule    | Description                          |
|--------------|---------|--------------------------------------|
| q0           | → aq0   | Self-loop on 'a'                     |
| q0           | → bq1   | Move to q1 on 'b'                    |
| q1           | → cq1   | Self-loop on 'c'                     |
| q1           | → cq2   | Move to q2 on 'c'                    |
| q1           | → c     | Terminal rule (q2 is final)          |
| q1           | → aq1   | Self-loop on 'a'                     |
| q2           | → aq0   | Move back to q0 on 'a'               |

---

### Task c — NDFA to DFA (Subset Construction)

**Step-by-step construction:**

Starting from `{q0}`, we compute reachable sets for each symbol:

| NDFA Set       | Symbol | Reachable Set  | DFA State Name |
|----------------|--------|----------------|----------------|
| {q0}           | a      | {q0}           | q0             |
| {q0}           | b      | {q1}           | q1             |
| {q1}           | a      | {q1}           | q1             |
| {q1}           | c      | {q1, q2}       | q1q2  ← final! |
| {q1, q2}       | a      | {q0, q1}       | q0q1           |
| {q1, q2}       | c      | {q1, q2}       | q1q2           |
| {q0, q1}       | a      | {q0, q1}       | q0q1           |
| {q0, q1}       | b      | {q1}           | q1             |
| {q0, q1}       | c      | {q1, q2}       | q1q2           |

**Resulting DFA:**

```
States:       {q0, q1, q1q2, q0q1}
Start state:  q0
Final states: {q1q2}    ← contains q2 (final in NDFA)

Transition table:
    δ(q0,   a) → q0
    δ(q0,   b) → q1
    δ(q1,   a) → q1
    δ(q1,   c) → q1q2
    δ(q1q2, a) → q0q1
    δ(q1q2, c) → q1q2
    δ(q0q1, a) → q0q1
    δ(q0q1, b) → q1
    δ(q0q1, c) → q1q2
```

| State       | a    | b  | c    | Final? |
|-------------|------|----|------|--------|
| q0 (start)  | q0   | q1 | -    | No     |
| q1          | q1   | -  | q1q2 | No     |
| q1q2        | q0q1 | -  | q1q2 | ✓ Yes  |
| q0q1        | q0q1 | q1 | q1q2 | No     |

---

## Key Difference: NDFA vs DFA

| Feature              | NDFA (original)         | DFA (converted)          |
|----------------------|-------------------------|--------------------------|
| States               | {q0, q1, q2}            | {q0, q1, q1q2, q0q1}    |
| Ambiguous transition | δ(q1, c) = {q1, q2}     | δ(q1, c) = q1q2 (single) |
| Final states         | {q2}                    | {q1q2}                   |
| Deterministic?       | ✗ No                    | ✓ Yes                    |

---

## Conclusions

✅ Successfully classified the grammar as **Type 3 (Regular)** in Chomsky hierarchy  
✅ Successfully converted the Finite Automaton to a regular grammar  
✅ Correctly identified the automaton as **NDFA** due to `δ(q1, c) = {q1, q2}`  
✅ Successfully converted NDFA → DFA using the Subset Construction method  
✅ The resulting DFA has 4 states and accepts the same language as the original NDFA  

**Key Learning:**
- An NDFA and its equivalent DFA always accept the same language
- Subset Construction may increase the number of states
- Every NDFA can be converted to an equivalent DFA

---

## References
- Course materials: *"Formal Languages & Finite Automata"* by Cretu Dumitru
- Hopcroft, J. E., et al. (2006). *Introduction to Automata Theory, Languages, and Computation*

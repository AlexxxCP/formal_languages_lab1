Laboratory Work #1 - Formal Languages and Finite Automata
Course: Formal Languages & Finite Automata
Variant: 14
Date: February 2026
Objectives
•	Understand formal language components (alphabet, grammar, productions)
•	Implement a Grammar class that generates valid strings
•	Convert Grammar to Finite Automaton
•	Implement string validation using the Finite Automaton
Grammar Specification
Variant 14:

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

This is a right-linear regular grammar (Type 3 in Chomsky hierarchy).

Non-terminal	Production	Description
S	→ aS	Can repeat 'a' at start
S	→ bB	Transition to state B
B	→ cB	Can repeat 'c'
B	→ d	Terminal production
B	→ aD	Transition to state D
D	→ aB	Transition back to B
D	→ b	Terminal production
Implementation
1. Grammar Class
Features:
•	Stores grammar components (VN, VT, P, S)
•	generate_string() — Randomly generates valid strings by applying production rules
•	to_finite_automaton() — Converts grammar to equivalent FA

Algorithm for string generation:
•	Start with symbol S
•	Randomly select applicable production rule
•	Apply rule and replace non-terminal
•	Repeat until only terminals remain
2. Finite Automaton Class
Features:
•	Stores FA components (Q, Σ, δ, q0, F)
•	string_belong_to_language() — Validates if string is accepted

Algorithm for validation:
•	Start from initial state q0
•	Read each symbol and follow transitions
•	Accept if final state F is reached after reading entire string
3. Main Program
Demonstrates all functionality:
•	Creates Grammar instance
•	Generates 5 example strings
•	Converts Grammar → FA
•	Tests validation on multiple test strings
How to Run
Requirements: Python 3.8+

# Run the program
python3 lab1.py

Expected Output:
•	5 generated valid strings
•	Finite Automaton transitions table
•	Validation results for test strings
Results
Generated Strings Examples
1. bd
2. aaaabd
3. bab
4. abcccd
5. abd
Automaton Structure
States (Q): {S, B, D, F}
Alphabet (Σ): {a, b, c, d}
Initial State (q0): S
Final States (F): {F}

Transition Function (δ):

State	a	b	c	d
S (start)	S	-	-	B
B	D	F ✓	B	-
D	B	F ✓	-	-
F ✓	-	-	-	-

F ✓ = transition to final/accepting state
String Validation Examples

String	Path / Reason	Result
bd	S →(b) B →(d) F	✓ Accepted
aaaabd	S →(a)→(a)→(a)→(a) S →(b) B →(d) F	✓ Accepted
bab	S →(b) B →(a) D →(b) F	✓ Accepted
abcccd	S →(a) S →(b) B →(c)→(c)→(c) B →(d) F	✓ Accepted
abd	S →(a) S →(b) B →(d) F	✓ Accepted
abc	No transition from B on 'c' after 'a'	✗ Rejected
aaa	No terminal reached	✗ Rejected
ba	B has no transition on 'a' alone	✗ Rejected
cd	No transition from S on 'c'	✗ Rejected
""	Empty string, never reaches final state	✗ Rejected
Conversion Process: Grammar → FA
Conversion Rules:
•	Each non-terminal becomes a state
•	Add one final state F
•	For rule A → aB: create transition δ(A, a) = B
•	For rule A → a:  create transition δ(A, a) = F

Example:
•	Production S → aS  becomes  δ(S, a) = S  (self-loop)
•	Production B → d   becomes  δ(B, d) = F  (to final state)
Language Properties
Accepted String Patterns:

a*b(c*d | aB) — Any number of 'a's, then 'b', leads to B
•	Examples: bd, abd, aaaabd

a*ba(ab|b) — Through D state, ending in 'b'
•	Examples: bab, abab

Key Characteristics:
•	Must start with 'a' (repeated) or 'b'
•	Must end with 'b' or 'd' (terminal productions)
•	Regular language (can be recognized by finite automaton)
•	Minimal string: bd (length = 2)
Conclusions
•	✅ Successfully implemented Grammar class for Variant 14
•	✅ String generation algorithm works correctly with recursive productions
•	✅ Grammar to FA conversion follows standard rules
•	✅ Finite Automaton correctly validates all test strings
•	✅ Demonstrated equivalence between regular grammar and finite automaton

Key Learning:
•	Regular grammars can be mechanically converted to finite automata
•	Both representations describe the same language
•	FA provides efficient string validation (O(n) time complexity)
References
•	Course materials: "Formal Languages & Finite Automata" by Cretu Dumitru
•	Hopcroft, J. E., et al. (2006). Introduction to Automata Theory, Languages, and Computation

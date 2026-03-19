# Laboratory Work #3 — Lexer & Scanner

**Course:** Formal Languages & Finite Automata  
**Student:** Luchiciov Alexei
**Group:** FAF-241

---

## Objectives

1. Understand what lexical analysis is and what role it plays in language processing.
2. Study the internal structure of a lexer/tokenizer.
3. Build a working lexer and demonstrate it on real input.

---

## Theory

Lexical analysis is the very first stage of compilation. A **lexer** (also called a scanner or tokenizer) reads a raw stream of characters and groups them into meaningful units called **tokens**. Every token has two parts: a **type** that describes the category (number, operator, keyword, etc.) and a **value** which is the literal text that was matched.

Consider the statement `let x = 42`. A lexer breaks it into: `KEYWORD("let")`, `IDENTIFIER("x")`, `ASSIGN("=")`, `INTEGER("42")`. The parser that comes after never has to deal with individual characters — it works entirely with this token list.

Lexers are closely related to finite automata. Recognising a number, for instance, is equivalent to a DFA that starts in an initial state, transitions on each digit, and accepts when it sees a non-digit. Recognising a keyword works the same way as recognising an identifier but with an extra acceptance check against a reserved-word table. The `tokenize()` dispatch loop in this implementation is essentially a hand-written DFA: each branch represents a different automaton state, and transitions happen one character at a time.

---

## Implementation

### Language Choice

The lexer targets **TinyLang**, a small custom language invented for this lab. The motivation for designing a custom language rather than implementing a subset of an existing one is that it allows every token category to be exercised naturally without the noise and edge cases of a real language. TinyLang includes variable declarations, arithmetic, conditionals, loops, function definitions with type annotations, list literals, comments, and string escape sequences.

### Token Types

| Type | Example |
|------|---------|
| `KEYWORD` | `let`, `fn`, `if`, `while`, `return` |
| `IDENTIFIER` | `x`, `result`, `greet` |
| `INTEGER` | `0`, `42`, `100` |
| `FLOAT` | `3.14`, `9.5` |
| `STRING` | `"hello world"` |
| `BOOLEAN` | `true`, `false` |
| `PLUS`, `MINUS` | `+`, `-` |
| `STAR`, `SLASH` | `*`, `/` |
| `PERCENT` | `%` |
| `POWER` | `**` |
| `EQ`, `NEQ` | `==`, `!=` |
| `LT`, `GT`, `LTE`, `GTE` | `<`, `>`, `<=`, `>=` |
| `ASSIGN` | `=` |
| `ARROW` | `->` |
| `LPAREN`, `RPAREN` | `(`, `)` |
| `LBRACE`, `RBRACE` | `{`, `}` |
| `LBRACKET`, `RBRACKET` | `[`, `]` |
| `COMMA`, `COLON`, `SEMICOLON`, `DOT` | `,`, `:`, `;`, `.` |
| `COMMENT` | `# ...` |
| `NEWLINE` | `\n` |
| `EOF` | end of input |
| `UNKNOWN` | `@`, `$` |

### Keyword Table

```python
KEYWORDS = {
    "let", "fn", "return", "if", "elif", "else",
    "while", "for", "in", "break", "continue",
    "print", "and", "or", "not",
    "int", "float", "bool", "str",
    "true", "false", "null",
}
```

Both identifiers and keywords look the same at scan time — sequences of alphanumeric characters and underscores. The distinction is made after the full word is read: the lexer checks the table and emits `BOOLEAN` for `true`/`false`, `KEYWORD` for any other reserved word, and `IDENTIFIER` otherwise.

### Token Class

```python
class Token:
    def __init__(self, token_type, value, line, col):
        self.type  = token_type
        self.value = value
        self.line  = line
        self.col   = col
```

Line and column numbers are stored in every token. This allows later compilation stages to produce error messages that point to the exact position in the source file.

### Lexer Structure

The `Lexer` class keeps three pieces of state: the position index `pos`, the current `line`, and the current `col`. The `advance()` method moves `pos` forward by one character and increments `line` or `col` accordingly whenever a newline is crossed.

The main method `tokenize()` runs a loop until `pos` reaches the end of the input:

- Spaces, tabs, and carriage returns are skipped. Newlines produce `NEWLINE` tokens.
- `#` triggers `scan_comment()`, which consumes everything until the end of the line.
- `"` triggers `scan_string()`, which handles escape sequences (`\"`, `\\`, `\n`, `\t`) and raises `LexerError` if the string is not closed.
- A digit starts `scan_number()`. After collecting all digits the scanner checks for a `.` followed by another digit; if found it continues to collect the decimal part and returns `FLOAT`, otherwise `INTEGER`.
- A letter or underscore starts `scan_identifier_or_keyword()`. After the word is assembled the keyword table lookup decides the token type.
- Two-character operators (`**`, `==`, `!=`, `<=`, `>=`, `->`) are checked using `peek()` before falling through to single-character operator matching.
- Any character not matched by the above rules produces an `UNKNOWN` token. The character is still consumed, which guarantees the loop always makes progress and terminates.

The loop appends an `EOF` token at the end.

### main.py

Six TinyLang code snippets are passed through the lexer and the resulting token streams are printed to stdout. The snippets are designed so that together they exercise every token type at least once.

---

## How to Run

Requires Python 3.8 or newer, no third-party packages.

```bash
python3 main.py
```

---

## Results

### Sample 1 — Variable declarations and arithmetic

Input:
```
let x = 42
let y = 3.14
let result = x * y + 100 ** 2
```

Output:
```
Token(KEYWORD      'let'       line=1, col=1)
Token(IDENTIFIER   'x'         line=1, col=5)
Token(ASSIGN       '='         line=1, col=7)
Token(INTEGER      '42'        line=1, col=9)
Token(KEYWORD      'let'       line=2, col=1)
Token(IDENTIFIER   'y'         line=2, col=5)
Token(ASSIGN       '='         line=2, col=7)
Token(FLOAT        '3.14'      line=2, col=9)
Token(KEYWORD      'let'       line=3, col=1)
Token(IDENTIFIER   'result'    line=3, col=5)
Token(ASSIGN       '='         line=3, col=12)
Token(IDENTIFIER   'x'         line=3, col=14)
Token(STAR         '*'         line=3, col=16)
Token(IDENTIFIER   'y'         line=3, col=18)
Token(PLUS         '+'         line=3, col=20)
Token(INTEGER      '100'       line=3, col=22)
Token(POWER        '**'        line=3, col=26)
Token(INTEGER      '2'         line=3, col=29)
Token(EOF          ''          line=4, col=1)
```

### Sample 2 — Function definition and call

Input:
```
fn add(a, b) {
    return a + b
}

let sum = add(10, 20)
print(sum)
```

Output:
```
Token(KEYWORD      'fn'        line=1, col=1)
Token(IDENTIFIER   'add'       line=1, col=4)
Token(LPAREN       '('         line=1, col=7)
Token(IDENTIFIER   'a'         line=1, col=8)
Token(COMMA        ','         line=1, col=9)
Token(IDENTIFIER   'b'         line=1, col=11)
Token(RPAREN       ')'         line=1, col=12)
Token(LBRACE       '{'         line=1, col=14)
Token(KEYWORD      'return'    line=2, col=5)
Token(IDENTIFIER   'a'         line=2, col=12)
Token(PLUS         '+'         line=2, col=14)
Token(IDENTIFIER   'b'         line=2, col=16)
Token(RBRACE       '}'         line=3, col=1)
Token(KEYWORD      'let'       line=5, col=1)
Token(IDENTIFIER   'sum'       line=5, col=5)
Token(ASSIGN       '='         line=5, col=9)
Token(IDENTIFIER   'add'       line=5, col=11)
Token(LPAREN       '('         line=5, col=14)
Token(INTEGER      '10'        line=5, col=15)
Token(COMMA        ','         line=5, col=17)
Token(INTEGER      '20'        line=5, col=19)
Token(RPAREN       ')'         line=5, col=21)
Token(KEYWORD      'print'     line=6, col=1)
Token(LPAREN       '('         line=6, col=6)
Token(IDENTIFIER   'sum'       line=6, col=7)
Token(RPAREN       ')'         line=6, col=10)
Token(EOF          ''          line=7, col=1)
```

### Sample 3 — Conditionals and comparison operators

Input:
```
let age = 18
if age >= 18 and age <= 65 {
    print("working age")
} elif age < 18 {
    print("minor")
} else {
    print("retired")
}
```

Selected output:
```
Token(KEYWORD      'if'        line=2, col=1)
Token(IDENTIFIER   'age'       line=2, col=4)
Token(GTE          '>='        line=2, col=8)
Token(INTEGER      '18'        line=2, col=11)
Token(KEYWORD      'and'       line=2, col=14)
Token(LTE          '<='        line=2, col=22)
Token(INTEGER      '65'        line=2, col=25)
Token(KEYWORD      'elif'      line=4, col=3)
Token(LT           '<'         line=4, col=12)
Token(KEYWORD      'else'      line=6, col=3)
```

### Sample 4 — While loop and modulo

Input:
```
let i = 0
while i < 10 {
    if i % 2 == 0 {
        print(i)
    }
    i = i + 1
}
```

Selected output:
```
Token(KEYWORD      'while'     line=2, col=1)
Token(LT           '<'         line=2, col=9)
Token(PERCENT      '%'         line=3, col=10)
Token(EQ           '=='        line=3, col=14)
```

### Sample 5 — Strings, booleans, comments

Input:
```
# This is a comment
let name = "Daniil"
let greeting = "Hello, " + name
let active = true
let score = 9.5
print(greeting)
```

Selected output:
```
Token(COMMENT      '# This is a comment'  line=1, col=1)
Token(STRING       'Daniil'               line=2, col=12)
Token(STRING       'Hello, '              line=3, col=16)
Token(BOOLEAN      'true'                 line=4, col=14)
Token(FLOAT        '9.5'                  line=5, col=13)
```

### Sample 6 — Type annotations, for loop, unknown characters

Input:
```
fn greet(name: str) -> str {
    return "Hi, " + name
}
for item in [1, 2, 3] {
    print(item)
}
let bad = @unknown$
```

Selected output:
```
Token(COLON        ':'         line=1, col=14)
Token(ARROW        '->'        line=1, col=21)
Token(KEYWORD      'for'       line=4, col=1)
Token(KEYWORD      'in'        line=4, col=10)
Token(LBRACKET     '['         line=4, col=13)
Token(RBRACKET     ']'         line=4, col=21)
Token(UNKNOWN      '@'         line=9, col=11)
Token(UNKNOWN      '$'         line=9, col=19)
```

---

## Project Structure

```
laboratory-work-3/
├── lexer.py    — token types, Token, LexerError, Lexer
├── main.py     — six sample programs and their token output
└── README.md   — this report
```

---

## Relation to Finite Automata

The `tokenize()` loop is a hand-coded deterministic finite automaton. Each branch corresponds to a state, and `advance()` is the transition function. The table below makes this explicit:

| State | Entry condition | Loop condition | Exit / emit |
|-------|----------------|----------------|-------------|
| NUMBER | first digit | more digits | non-digit; sub-state for `.` → FLOAT |
| WORD | letter or `_` | alphanumeric / `_` | non-alphanumeric; keyword lookup |
| STRING | `"` | any char ≠ `"` | closing `"` → STRING |
| COMMENT | `#` | any char ≠ `\n` | newline or EOF → COMMENT |
| OPERATOR | `*=!<>-` | peek next char | emit 1- or 2-char token |

This is why finite automata and lexers are taught as a pair — a lexer is essentially a DFA written out explicitly in code.

---

## Conclusions

The lab produced a complete lexer for TinyLang. The following points summarise the outcome:

- All 25 token types are handled, including two-character operators that require one character of lookahead.
- The number scanner correctly separates integers from floats by checking for a digit after the decimal point.
- String scanning supports the four standard escape sequences and reports unterminated strings with a precise source location.
- Comments are kept as tokens rather than silently dropped, which allows downstream stages to attach documentation to an AST if desired.
- Every token carries a line and column number for accurate error reporting.
- Unknown characters produce `UNKNOWN` tokens instead of terminating with an exception, so the lexer always processes the entire input.
- The implementation visibly mirrors DFA theory: each recognition routine corresponds to an automaton that was studied in Lab 2.

---

## References

Cretu Dumitru, Vasile Drumea, Irina Cojuhari — FLFA course materials.  
Aho, Lam, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools*, 2nd ed., Chapter 3.  
Wikipedia — Lexical analysis: https://en.wikipedia.org/wiki/Lexical_analysis

---

**Date:** March 2026  
**Repository:** [GitHub Link]

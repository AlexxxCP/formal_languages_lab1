# Laboratory Work #6 — Parser & Building an Abstract Syntax Tree

**Course:** Formal Languages & Finite Automata  
**Student:** Luchiciov Alexei  
**Group:** FAF-241

---

## Objectives

1. Get familiar with parsing, what it is and how it can be programmed.
2. Get familiar with the concept of Abstract Syntax Tree (AST).
3. In addition to what was done in Lab 3:
   1. Use a `TokenType` class and regular expressions for lexical analysis.
   2. Implement the necessary data structures for an AST for the TinyLang programs from Lab 3.
   3. Implement a simple recursive-descent parser that extracts syntactic information from input text.

---

## Theory

Parsing is the process of analysing a sequence of tokens and determining its grammatical structure according to a formal grammar. A **parser** takes the flat token list that a lexer produces and organises it into a hierarchical structure. That structure is usually a **parse tree**, which captures every detail of the source text, or an **Abstract Syntax Tree (AST)**, which keeps only the semantically relevant parts.

An AST is a tree in which every interior node represents an operation or construct (e.g. a binary addition, an `if` statement, a function definition) and every leaf node represents a literal value or a name. Nodes that are significant only for parsing — parentheses, commas, keywords like `then` — are not stored in the AST. This makes the tree compact and easy to traverse in later compilation stages.

The parser implemented here uses **recursive descent**, a top-down parsing technique where each grammar rule is mapped directly to a function. Operator precedence is encoded by the call hierarchy: a low-precedence rule calls a higher-precedence rule, so higher-precedence operators end up deeper in the tree and are therefore evaluated first.

---

## Implementation

### Language Choice

The parser targets **TinyLang**, the same language designed for Lab 3. Because the lexer already handles all token categories, the parser can focus entirely on grammar and tree construction.

### Regex-based Lexer Update

The lexer from Lab 3 was rewritten to use Python's `re` module. A single master regular expression is compiled from an ordered list of named patterns:

```python
_TOKEN_SPEC = [
    ("FLOAT",   r"\d+\.\d+"),
    ("INTEGER", r"\d+"),
    ("STRING",  r'"(?:[^"\\]|\\.)*"'),
    ("POWER",   r"\*\*"),
    ("EQ",      r"=="),
    ...
    ("WORD",    r"[A-Za-z_]\w*"),
    ("UNKNOWN", r"."),
]

_MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pat})" for name, pat in _TOKEN_SPEC)
)
```

`_MASTER_RE.finditer()` scans the input in a single pass. The order of patterns matters: `FLOAT` must come before `INTEGER`, `**` before `*`, `STRING` before `UNTERMINATED_STRING`, and so on. This is the standard "maximal munch" strategy — always match the longest possible token.

### AST Node Hierarchy

All nodes inherit from a common `ASTNode` base class and are implemented as Python `@dataclass` instances for clean field access and automatic `__repr__`.

**Literals and identifiers:**

| Node | Fields |
|------|--------|
| `IntegerLiteral` | `value: int` |
| `FloatLiteral` | `value: float` |
| `StringLiteral` | `value: str` |
| `BooleanLiteral` | `value: bool` |
| `NullLiteral` | — |
| `Identifier` | `name: str` |
| `ListLiteral` | `elements: List[ASTNode]` |

**Expressions:**

| Node | Fields |
|------|--------|
| `BinaryOp` | `left`, `op: str`, `right` |
| `UnaryOp` | `op: str`, `operand` |
| `FunctionCall` | `name: str`, `args: List[ASTNode]` |

**Statements:**

| Node | Fields |
|------|--------|
| `LetStatement` | `name: str`, `value` |
| `AssignStatement` | `name: str`, `value` |
| `ReturnStatement` | `value: Optional[ASTNode]` |
| `PrintStatement` | `value` |
| `IfStatement` | `condition`, `then_body`, `elif_clauses`, `else_body` |
| `ElifClause` | `condition`, `body` |
| `WhileStatement` | `condition`, `body` |
| `ForStatement` | `var: str`, `iterable`, `body` |
| `BreakStatement` | — |
| `ContinueStatement` | — |
| `FunctionDef` | `name`, `params`, `return_type`, `body` |
| `Param` | `name: str`, `type_annotation: Optional[str]` |
| `Program` | `statements: List[ASTNode]` |

### Parser Structure

The `Parser` class is initialised with the token list from the lexer (newlines and comments are filtered out as they carry no syntactic meaning). Three low-level helpers drive the scan:

- `_current()` — returns the token at the current position without consuming it.
- `_advance()` — consumes and returns the current token.
- `_expect(type, value)` — consumes the current token if it matches, otherwise raises `ParseError`.

The entry point `parse()` calls `_parse_statement()` in a loop until `EOF` and wraps the result in a `Program` node.

### Grammar and Operator Precedence

The grammar is implemented as a set of mutually recursive functions. Lower-precedence rules appear higher in the call chain:

```
program        := statement*
statement      := let | fn | if | while | for | return
                | print | break | continue | assign | expr
let            := 'let' IDENT '=' expr
assign         := IDENT '=' expr
fn             := 'fn' IDENT '(' params? ')' ('->' type)? block
if             := 'if' expr block ('elif' expr block)* ('else' block)?
while          := 'while' expr block
for            := 'for' IDENT 'in' expr block
block          := '{' statement* '}'
expr           := or
or             := and ('or' and)*
and            := not ('and' not)*
not            := 'not' not | comparison
comparison     := additive (CMP_OP additive)*
additive       := multiplicative (('+' | '-') multiplicative)*
multiplicative := power (('*' | '/' | '%') power)*
power          := unary ('**' unary)*        -- right-associative
unary          := '-' unary | primary
primary        := INTEGER | FLOAT | STRING | BOOLEAN | 'null'
               | IDENT ('(' args? ')')?
               | '[' (expr (',' expr)*)? ']'
               | '(' expr ')'
```

`**` is right-associative: `_parse_power` calls itself recursively instead of looping.

### ParseError

```python
class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        super().__init__(
            f"ParseError at line {token.line}, col {token.col}: {message}"
        )
```

Every error includes the line and column of the offending token, taken directly from the `Token` objects produced by the lexer.

### main.py

Six TinyLang programs are parsed and their ASTs are printed as indented trees. The output format uses the dataclass field names as labels, making the tree structure immediately readable.

---

## How to Run

Requires Python 3.8 or newer, no third-party packages.

```bash
python main.py
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
--- Sample 1 — Variable declarations and arithmetic ---
Program
  statements:
    LetStatement
      name = 'x'
      value:
        IntegerLiteral
          value = 42
    LetStatement
      name = 'y'
      value:
        FloatLiteral
          value = 3.14
    LetStatement
      name = 'result'
      value:
        BinaryOp
          left:
            BinaryOp
              left:
                Identifier
                  name = 'x'
              op = '*'
              right:
                Identifier
                  name = 'y'
          op = '+'
          right:
            BinaryOp
              left:
                IntegerLiteral
                  value = 100
              op = '**'
              right:
                IntegerLiteral
                  value = 2
```

`100 ** 2` is nested deeper than `+`, correctly reflecting that `**` has higher precedence. The left subtree of `+` is the `*` node, not a flat list — the tree directly encodes evaluation order.

### Sample 2 — Function definition and call

Input:
```
fn add(a, b) {
    return a + b
}
let sum = add(10, 20)
print(sum)
```

Selected output:
```
FunctionDef
  name = 'add'
  params:
    Param
      name = 'a'
      type_annotation = None
    Param
      name = 'b'
      type_annotation = None
  return_type = None
  body:
    ReturnStatement
      value:
        BinaryOp
          left:
            Identifier
              name = 'a'
          op = '+'
          right:
            Identifier
              name = 'b'
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
IfStatement
  condition:
    BinaryOp
      left:
        BinaryOp
          left:
            Identifier
              name = 'age'
          op = '>='
          right:
            IntegerLiteral
              value = 18
      op = 'and'
      right:
        BinaryOp
          left:
            Identifier
              name = 'age'
          op = '<='
          right:
            IntegerLiteral
              value = 65
  then_body: ...
  elif_clauses:
    ElifClause
      condition: ...
  else_body: ...
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
WhileStatement
  condition:
    BinaryOp
      left:
        Identifier
          name = 'i'
      op = '<'
      right:
        IntegerLiteral
          value = 10
  body:
    IfStatement
      condition:
        BinaryOp
          left:
            BinaryOp
              left:
                Identifier
                  name = 'i'
              op = '%'
              right:
                IntegerLiteral
                  value = 2
          op = '=='
          right:
            IntegerLiteral
              value = 0
    AssignStatement
      name = 'i'
      value:
        BinaryOp ...
```

### Sample 5 — Strings, booleans, comments

Input:
```
# greeting program
let name = "Daniil"
let greeting = "Hello, " + name
let active = true
let score = 9.5
print(greeting)
```

Selected output:
```
LetStatement
  name = 'active'
  value:
    BooleanLiteral
      value = True
LetStatement
  name = 'score'
  value:
    FloatLiteral
      value = 9.5
```

The comment is filtered before parsing and does not appear in the AST.

### Sample 6 — Type annotations, for loop, list literal

Input:
```
fn greet(name: str) -> str {
    return "Hi, " + name
}
for item in [1, 2, 3] {
    print(item)
}
```

Selected output:
```
FunctionDef
  name = 'greet'
  params:
    Param
      name = 'name'
      type_annotation = 'str'
  return_type = 'str'
  body: ...
ForStatement
  var = 'item'
  iterable:
    ListLiteral
      elements:
        IntegerLiteral
          value = 1
        IntegerLiteral
          value = 2
        IntegerLiteral
          value = 3
  body:
    PrintStatement ...
```

---

## Project Structure

```
laboratory-work-6/
├── lexer.py      — regex-based lexer (updated from Lab 3)
├── ast_nodes.py  — AST node dataclasses
├── parser.py     — recursive-descent parser
├── main.py       — six sample programs and their AST output
└── README.md     — this report
```

---

## Relation to Formal Grammars

Recursive descent maps a context-free grammar directly to code. Each non-terminal becomes a function; each alternative in a production becomes a branch inside that function. The table below shows the correspondence for the expression grammar:

| Grammar rule | Parser method | Technique |
|---|---|---|
| `expr → or` | `_parse_expression` | delegation |
| `or → and ('or' and)*` | `_parse_or` | iterative loop |
| `and → not ('and' not)*` | `_parse_and` | iterative loop |
| `not → 'not' not \| comparison` | `_parse_not` | recursive (prefix) |
| `comparison → additive (CMP additive)*` | `_parse_comparison` | iterative loop |
| `power → unary ('**' unary)*` | `_parse_power` | recursive (right-assoc) |
| `primary → INTEGER \| …` | `_parse_primary` | token switch |

Right-associativity of `**` is achieved by having `_parse_power` call itself recursively on the right operand rather than looping, which causes the deepest `**` to be evaluated first.

---

## Conclusions

The lab produced a complete parser for TinyLang that builds a full Abstract Syntax Tree:

- The lexer was updated to use a single compiled regular expression (`re.compile` with named groups), making the tokenisation rule set declarative and easy to extend.
- All AST node types are implemented as Python `@dataclass` instances, giving clean field access and automatic string representation without boilerplate.
- The recursive-descent parser directly encodes the formal grammar of TinyLang. Operator precedence and associativity are a natural consequence of the call hierarchy, not an extra implementation concern.
- `ParseError` carries the line and column of the offending token, making error messages precise.
- The parser correctly handles all constructs from Lab 3: variable declarations, arithmetic with full precedence, function definitions with type annotations and return types, `if`/`elif`/`else`, `while`, `for`, list literals, and function calls.
- Comments and newlines are stripped before parsing; they have no syntactic role and do not appear in the AST.

---

## References

Cretu Dumitru, Vasile Drumea, Irina Cojuhari — FLFA course materials.  
Aho, Lam, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools*, 2nd ed., Chapters 4–5.  
Wikipedia — Parsing: https://en.wikipedia.org/wiki/Parsing  
Wikipedia — Abstract Syntax Tree: https://en.wikipedia.org/wiki/Abstract_syntax_tree

---

**Date:** April 2026  
**Repository:** [GitHub Link]

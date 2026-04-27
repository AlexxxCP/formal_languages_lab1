from dataclasses import fields

from lexer  import Lexer
from parser import Parser
import ast_nodes


def print_ast(node, indent=0):
    pad  = "    " * indent
    name = type(node).__name__

    if not isinstance(node, ast_nodes.ASTNode):
        print(f"{pad}{node!r}")
        return

    try:
        fs = fields(node)
    except TypeError:
        print(f"{pad}{name}")
        return

    if not fs:
        print(f"{pad}{name}")
        return

    print(f"{pad}{name}")
    for f in fs:
        val = getattr(node, f.name)
        if isinstance(val, list):
            print(f"{pad}  {f.name}:")
            for item in val:
                print_ast(item, indent + 1)
        elif isinstance(val, ast_nodes.ASTNode):
            print(f"{pad}  {f.name}:")
            print_ast(val, indent + 1)
        else:
            print(f"{pad}  {f.name} = {val!r}")


def run(title, source):
    print(f"--- {title} ---")
    print(source.strip())
    print()
    tokens = Lexer(source).tokenize()
    tree   = Parser(tokens).parse()
    print_ast(tree)
    print()

run("Sample 1 — Variable declarations and arithmetic", """
let x = 42
let y = 3.14
let result = x * y + 100 ** 2
""")

run("Sample 2 — Function definition and call", """
fn add(a, b) {
    return a + b
}
let sum = add(10, 20)
print(sum)
""")

run("Sample 3 — Conditionals and comparison operators", """
let age = 18
if age >= 18 and age <= 65 {
    print("working age")
} elif age < 18 {
    print("minor")
} else {
    print("retired")
}
""")

run("Sample 4 — While loop and modulo", """
let i = 0
while i < 10 {
    if i % 2 == 0 {
        print(i)
    }
    i = i + 1
}
""")

run("Sample 5 — Strings, booleans, comments", """
# greeting program
let name = "Daniil"
let greeting = "Hello, " + name
let active = true
let score = 9.5
print(greeting)
""")

run("Sample 6 — Type annotations, for loop, list literal", """
fn greet(name: str) -> str {
    return "Hi, " + name
}
for item in [1, 2, 3] {
    print(item)
}
""")

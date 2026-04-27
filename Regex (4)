"""
regex.py — pattern tokeniser and string generator

Supported syntax:
    literals      — any character that is not a meta-symbol
    (A|B|C)       — alternation: pick one alternative
    {n}           — exactly n repetitions
    ?             — zero or one
    *             — zero or more  (capped at MAX_REPEAT)
    +             — one or more   (capped at MAX_REPEAT)
"""

import random

MAX_REPEAT = 5


# ── Token ──────────────────────────────────────────────────────────────────────

class Token:
    def __init__(self, kind, value, quantifier):
        self.kind       = kind        # 'char' | 'group'
        self.value      = value       # str  | list[str]
        self.quantifier = quantifier  # '1' | '?' | '*' | '+' | ('n', int)

    def __repr__(self):
        q = self.quantifier
        if isinstance(q, tuple):
            q_str = f"exactly {q[1]}"
        elif q == '1': q_str = "exactly 1"
        elif q == '?': q_str = "0 or 1"
        elif q == '*': q_str = f"0 to {MAX_REPEAT}"
        elif q == '+': q_str = f"1 to {MAX_REPEAT}"
        else:          q_str = str(q)

        if self.kind == 'char':
            return f"Token(CHAR  '{self.value}'  {q_str})"
        else:
            alts = ' | '.join(self.value)
            return f"Token(GROUP ({alts})  {q_str})"


# ── Tokeniser ──────────────────────────────────────────────────────────────────

def _read_quantifier(pattern, pos):
    """Return (quantifier, chars_consumed) starting at pos."""
    if pos >= len(pattern):
        return '1', 0
    ch = pattern[pos]
    if ch == '?': return '?', 1
    if ch == '*': return '*', 1
    if ch == '+': return '+', 1
    if ch == '{':
        close = pattern.find('}', pos + 1)
        if close == -1:
            raise ValueError(f"unclosed '{{' at position {pos}")
        n_str = pattern[pos + 1:close]
        if not n_str.isdigit():
            raise ValueError(f"expected integer inside {{}}, got '{n_str}'")
        return ('n', int(n_str)), close - pos + 1
    return '1', 0


def tokenise(pattern):
    """Parse a pattern string into a list of Token objects."""
    tokens = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]

        if ch == '(':
            # find matching closing parenthesis
            depth, j = 1, i + 1
            while j < len(pattern) and depth > 0:
                if   pattern[j] == '(': depth += 1
                elif pattern[j] == ')': depth -= 1
                j += 1
            alternatives = pattern[i + 1:j - 1].split('|')
            quant, skip  = _read_quantifier(pattern, j)
            tokens.append(Token('group', alternatives, quant))
            i = j + skip

        elif ch not in ')|?*+{':
            i += 1
            quant, skip = _read_quantifier(pattern, i)
            tokens.append(Token('char', ch, quant))
            i += skip

        else:
            i += 1  # skip stray meta characters

    return tokens


# ── Generator ──────────────────────────────────────────────────────────────────

def _resolve(quantifier):
    """Turn a quantifier into a concrete repetition count."""
    if quantifier == '1':   return 1
    if quantifier == '?':   return random.randint(0, 1)
    if quantifier == '*':   return random.randint(0, MAX_REPEAT)
    if quantifier == '+':   return random.randint(1, MAX_REPEAT)
    if isinstance(quantifier, tuple) and quantifier[0] == 'n':
        return quantifier[1]
    raise ValueError(f"unknown quantifier: {quantifier!r}")


def generate(pattern):
    """Generate one valid string that matches the pattern."""
    parts = []
    for token in tokenise(pattern):
        n = _resolve(token.quantifier)
        if token.kind == 'char':
            parts.append(token.value * n)
        else:
            parts.extend(random.choice(token.value) for _ in range(n))
    return ''.join(parts)


# ── Step-by-step trace (bonus) ─────────────────────────────────────────────────

def _quant_label(quantifier):
    if quantifier == '1':   return "exactly 1"
    if quantifier == '?':   return "0 or 1 (optional)"
    if quantifier == '*':   return f"0 to {MAX_REPEAT} (zero or more)"
    if quantifier == '+':   return f"1 to {MAX_REPEAT} (one or more)"
    if isinstance(quantifier, tuple) and quantifier[0] == 'n':
        return f"exactly {quantifier[1]}"
    return str(quantifier)


def show_processing(pattern):
    """Print a step-by-step trace of how the pattern is processed, then return the result."""
    print(f"\nPattern: {pattern}")

    tokens = tokenise(pattern)
    parts  = []

    for step, token in enumerate(tokens, 1):
        n = _resolve(token.quantifier)

        if token.kind == 'char':
            piece = token.value * n
            print(f"  step {step}: char '{token.value}', {_quant_label(token.quantifier)}, chose {n} -> '{piece}'")
        else:
            chosen = [random.choice(token.value) for _ in range(n)]
            piece  = ''.join(chosen)
            alts   = ' | '.join(token.value)
            print(f"  step {step}: group ({alts}), {_quant_label(token.quantifier)}, chose {n} -> '{piece}'")

        parts.append(piece)

    result = ''.join(parts)
    print(f"  result: {result}\n")
    return result

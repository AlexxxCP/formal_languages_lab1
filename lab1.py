import random

# ══════════════════════════════════════════════════════
#  Лабораторная работа №1  |  Вариант 14
#  Грамматика:
#    VN = {S, B, D}   — нетерминалы
#    VT = {a, b, c, d} — терминалы
#    Правила:
#      S → aS | bB
#      B → cB | d | aD
#      D → aB | b
# ══════════════════════════════════════════════════════


class Grammar:

    def __init__(self):
        # Нетерминальные символы (внутренние состояния)
        self.VN = {'S', 'B', 'D'}

        # Терминальные символы (буквы алфавита)
        self.VT = {'a', 'b', 'c', 'd'}

        # Стартовый символ
        self.start = 'S'

        # Правила грамматики: каждый нетерминал → список вариантов замены
        self.rules = {
            'S': ['aS', 'bB'],
            'B': ['cB', 'd', 'aD'],
            'D': ['aB', 'b']
        }

    def generate_string(self):
        # Начинаем со стартового символа
        word = self.start

        # Повторяем пока в слове есть нетерминалы
        while any(c in self.VN for c in word):
            for i, c in enumerate(word):
                if c in self.VN:
                    # Выбираем случайное правило для этого нетерминала
                    replacement = random.choice(self.rules[c])
                    # Заменяем нетерминал на выбранное правило
                    word = word[:i] + replacement + word[i+1:]
                    break  # начинаем следующий проход сначала

        return word

    def to_finite_automaton(self):
        # Переходы автомата: (состояние, символ) → следующее состояние
        transitions = {}

        for state, productions in self.rules.items():
            for prod in productions:
                if len(prod) == 1:
                    # Правило вида B → d (только терминал) → идём в финальное состояние
                    transitions[(state, prod)] = 'F'
                else:
                    # Правило вида S → aB → δ(S, a) = B
                    transitions[(state, prod[0])] = prod[1]

        # Создаём и возвращаем автомат
        return FiniteAutomaton(transitions, self.start)


class FiniteAutomaton:

    def __init__(self, transitions, start_state):
        self.transitions = transitions   # таблица переходов
        self.start = start_state         # начальное состояние
        self.final = 'F'                 # единственное финальное состояние

    def check(self, word):
        # Начинаем с начального состояния
        state = self.start

        for char in word:
            if (state, char) in self.transitions:
                # Переходим в следующее состояние
                state = self.transitions[(state, char)]
            else:
                # Перехода нет → слово не принадлежит языку
                return False

        # Слово принято только если закончили в финальном состоянии
        return state == self.final


# ══════════════════════════════════════════════════════
#  Запуск программы
# ══════════════════════════════════════════════════════

# 1. Создаём грамматику
g = Grammar()

# 2. Генерируем 5 строк
print("--- 5 сгенерированных строк ---")
strings = []
for i in range(5):
    s = g.generate_string()
    strings.append(s)
    print(f"  {i+1}. {s}")

# 3. Конвертируем грамматику в конечный автомат
fa = g.to_finite_automaton()
print("\n--- Таблица переходов автомата ---")
for (state, symbol), next_state in fa.transitions.items():
    print(f"  δ({state}, {symbol}) → {next_state}")

# 4. Проверяем сгенерированные строки (все должны быть True)
print("\n--- Проверка сгенерированных строк (ожидаем True) ---")
for s in strings:
    print(f"  '{s}' → {fa.check(s)}")

# 5. Проверяем неверные строки (все должны быть False)
print("\n--- Проверка неверных строк (ожидаем False) ---")
for s in ["abc", "aaa", "ba", "cd", ""]:
    print(f"  '{s}' → {fa.check(s)}")

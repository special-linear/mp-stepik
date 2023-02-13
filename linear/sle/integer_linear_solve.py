from linear.matrix import Matrix, random_glnz, integer_linear_solve
import random
import itertools as it
import more_itertools as mit
from operator import mul
from math import ceil


def generate():
    problems = []
    systems_handcrafted = [
        Matrix([[2, 0, 4, 6, 8, 2], [0, 0, 1, 2, 3, 3], [0, 0, 0, 0, 0, 0], [0, 0, 0, 3, 5, 4]])
    ]
    systems_solvable = []
    systems_nonsoluble = []
    for m, n in [(3, 3), (3, 5), (5, 3), (10, 20), (20, 10), (1, 10)]:
        for _ in range(3):
            s = min(m, n)
            ds = random.choices(range(1, 5), k=random.randint(ceil(s / 2), s))
            ds = it.accumulate(ds, mul)
            ds = list(mit.padded(ds, 0, s))
            d = Matrix([[ds[i] if i == j else 0 for j in range(n)] for i in range(m)])
            c1, c2 = (random_glnz(size) for size in (m, n))
            b_list = list(mit.padded(([x * random.randint(-3, 3)] for x in ds), [0], m))
            b = Matrix(b_list)
            a = d @ c2
            systems_solvable.append(c1 @ Matrix.hstack(a, b))
            b = b + Matrix([[1]] * m)
            systems_nonsoluble.append(c1 @ Matrix.hstack(a, b))
    for s in it.chain(systems_handcrafted, systems_solvable, systems_nonsoluble):
        clue = s.serialize() if integer_linear_solve(s) is not None else None
        problems.append((s.input_repr(), clue))
    return problems


def check(reply, clue):
    if reply == 'No solutions':
        if clue is None:
            return True
        return False, 'Ответ "No solutions", хотя система разрешима.'
    else:
        if clue is None:
            return False, 'Ответ не "No solutions", хотя система неразрешима.'
        try:
            x = Matrix.parse_matrix_reply(reply)
            ab = Matrix(clue, entries_type=tuple)
            a = ab[:, :-1]
            b = ab[:, -1]
            x_shape = x.shape()
            if x_shape[1] != 1:
                return False, 'Решение должно быть столбцом (матрицей ширины 1).'
            if x_shape[0] != a.shape()[1]:
                return False, 'Высота столбца решений должна совпадать с шириной (нерасширенной) матрицы системы.'
            if any(v.denominator != 1 for row in x.entries for v in row):
                return False, 'Ответ включает нецелые числа.'
            if a @ x == b:
                return True
            return False, 'Столбец не удовлетворяет данной системе уравнений.'
        except ValueError as e:
            return False, e.args[0]


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    ab = Matrix(entries)
    sol = integer_linear_solve(ab)
    return str(sol) if sol is not None else 'No solutions'

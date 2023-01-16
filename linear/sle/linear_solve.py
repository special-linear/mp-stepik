from linear.matrix import Matrix, randmat, linear_solve, random_glnq, random_rref
import itertools as it
from fractions import Fraction


def generate():
    sles_handcrafted = [
        Matrix([[1, 0, 2, 3], [0, 1, 5, 7]]),
        Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [0, 0, 0, 9]])
    ]
    sles_solvable = []
    sles_nonsolvable = []
    for m, n in [(3, 3), (4, 4), (5, 5), (5, 10), (10, 5), (10, 20), (20, 10), (50, 100), (100, 50)]:
        num_pivots = round(min(m, n) * 0.75)
        a = random_rref(m, n, num_pivots)
        while True:
            x = (Fraction(1, 3) if n < 10 else Fraction(1, 2) if n < 20 else 1) * Matrix(randmat(n, 1, 5))
            ab = Matrix.hstack(a, a @ x)
            c = random_glnq(m)
            cab = c @ ab
            if all(e.denominator == 1 for row in cab.entries for e in row):
                sol_entries = next(zip(*linear_solve(cab).entries))
                if m >= 10 or n >= 10 or any(e.denominator != 1 for e in sol_entries):
                    sles_solvable.append(cab)
                    break
        while True:
            b = Matrix(randmat(m, 1, 2))
            if b[-1] != 0 and a[-1, -1] == 0:
                ab = Matrix.hstack(a, b)
                sles_nonsolvable.append(c @ ab)
                break
    sles = it.chain(sles_handcrafted, sles_solvable, sles_nonsolvable)
    problems = [(ab.input_repr(), ab.serialize() if linear_solve(ab) is not None else None) for ab in sles]
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
            if a @ x == b:
                return True
            return False, 'Столбец не удовлетворяет данной системе уравнений.'
        except ValueError as e:
            return False, e.args[0]


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    sol = linear_solve(Matrix(entries))
    return str(sol) if sol is not None else 'No solutions'


for dataset, clue in generate():
    print(check(solve(dataset), clue))

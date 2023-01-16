import random
import itertools as it
from linear.matrix import Matrix, randmat


def generate():
    problems = [
        ('-3 0 -3 -3\n-3 -1 -2 -3\n-2 -3 1 2',
         (((1, 1), (0, 1), (1, 1), (0, 1)), ((0, 1), (1, 1), (-1, 1), (0, 1)), ((0, 1), (0, 1), (0, 1), (1, 1)))),
        ('0 1 0 1\n0 0 -1 0\n-1 1 1 0\n-1 0 -1 -1',
         (((1, 1), (0, 1), (0, 1), (1, 1)), ((0, 1), (1, 1), (0, 1), (1, 1)), ((0, 1), (0, 1), (1, 1), (0, 1)), ((0, 1), (0, 1), (0, 1), (0, 1))))
    ]
    matrices = []
    for m, n in [(10, 10), (20, 20), (30, 30), (40, 40), (50, 50), (20, 80), (80, 20), (1, 10), (10, 1)]:
        matrices.append(randmat(m, n, entries_lim=10 ** 2))
    matrices_with_zero_rows = []
    matrices_with_zero_columns = []
    for a in matrices:
        b = [row if random.randint(0, 1) == 0 else [0]*len(row) for row in a]
        matrices_with_zero_rows.append(b)
        c = list(zip(*[row if random.randint(0, 1) == 0 else [0]*len(row) for row in zip(*a)]))
        matrices_with_zero_columns.append(c)
    matrices_with_zero_columns.append([[0]*100 for _ in range(100)])
    for a in it.chain(matrices, matrices_with_zero_rows, matrices_with_zero_columns):
        problem = '\n'.join(' '.join(map(str, row)) for row in a)
        problems.append((problem, Matrix(a).ref(reduced=True).serialize()))
    return problems


def check(reply, clue):
    try:
        a = Matrix.parse_matrix_reply(reply)
        if a.is_row_echelon_form():
            b = Matrix(clue, entries_type=tuple)
            if a.ref(reduced=True) == b:
                return True
            else:
                return False, 'Строчная эшелонированная форма не соответствует исходной матрице.'
        else:
            return False, 'Матрица не в строчной эшелонированной форме.'
    except ValueError as e:
        return False, e.args[0]


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    return str(Matrix(entries).ref(reduced=False))

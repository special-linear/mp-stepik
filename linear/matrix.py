from fractions import Fraction
from math import inf, gcd
import itertools as it
import more_itertools as mit
from functools import reduce
from operator import methodcaller, mul
import re
import random


class Matrix:
    def __init__(self, entries, entries_type=int):
        converter = None
        if issubclass(entries_type, int):
            converter = Fraction
        elif issubclass(entries_type, tuple):
            def converter(x): return Fraction(*x)
        self.entries = [list(map(converter, row)) for row in entries]

    def __getitem__(self, item):
        m, n = self.shape()
        if isinstance(item, (int, slice)):
            if m == 1:
                return self.entries[0][item]
            elif n == 1:
                return self.entries[item][0]
            else:
                raise IndexError('Один индекс не для столбца или строки.')
        elif isinstance(item, tuple) and len(item) == 2:
            i1, i2 = item
            if all(isinstance(i, int) for i in item):
                return self.entries[item[0]][item[1]]
            elif isinstance(i1, int) and isinstance(i2, slice):
                return Matrix([self.entries[i1][i2]])
            elif isinstance(i1, slice) and isinstance(i2, int):
                return Matrix([[row[i2]] for row in self.entries[i1]])
            elif isinstance(i1, slice) and isinstance(i2, slice):
                return Matrix([row[i2] for row in self.entries[i1]])
            else:
                raise IndexError('Некорректный индекс.')
        else:
            raise IndexError('Некорректный индекс.')

    def shape(self):
        return len(self.entries), len(self.entries[0])

    def __eq__(self, other):
        return self.entries == other.entries

    def __str__(self):
        entries_strs = [list(map(str, row)) for row in self.entries]
        col_widths = [max(map(len, col)) for col in zip(*entries_strs)]
        rows_strs = (' '.join('{}'.format(r.ljust(w)) for r, w in zip(row, col_widths)) for row in entries_strs)
        rows_strs = list(map('[{}]'.format, rows_strs))
        return '[{}]'.format('\n '.join(rows_strs)) if len(rows_strs) > 1 else rows_strs[0]

    def input_repr(self):
        return '\n'.join(' '.join(map(str, row)) for row in self.entries)

    def serialize(self):
        return tuple(tuple((x.numerator, x.denominator) for x in row) for row in self.entries)

    @staticmethod
    def parse_matrix_row_reply(entries_str, frac_regex=re.compile('(-?\d+)(?:/(\d+))?$')):
        matches = [frac_regex.match(s) for s in entries_str.strip().split()]
        if all(matches):
            entries = [(int(m.group(1)), int(m.group(2)) if m.group(2) is not None else None) for m in matches]
            if all(e[1] is None or e[1] != 1 for e in entries):
                if all(e[0] != 0 or e[1] is None for e in entries):
                    if all(e[1] is None or gcd(*e) == 1 for e in entries):
                        return [Fraction(*entry) for entry in entries]
                    else:
                        raise ValueError('Элементы матрицы представлены некорректно (сократимые дроби).')
                else:
                    raise ValueError('Нулевые элементы матрицы представлены некорректно.')
            else:
                raise ValueError('Элементы матрицы представлены некорректно (единичные знаменатели).')
        else:
            raise ValueError('Элементы матрицы представлены некорректно.')

    @staticmethod
    def parse_matrix_reply(reply):
        if reply[0] == '[' and reply[-1] == ']':
            reply_lines = list(map(methodcaller('strip'), reply[1:-1].splitlines()))
            if len(reply_lines) == 1:
                s = reply_lines[0]
                if s[0] == '[' or s[1] == ']':
                    raise ValueError('Матрица из одной строки неверно обрамлена.')
                else:
                    entries = Matrix.parse_matrix_row_reply(s)
                    return Matrix([entries])
            else:
                if all(s[0] == '[' and s[-1] == ']' for s in reply_lines):
                    reply_lines_stripped = [s[1:-1] for s in reply_lines]
                    entries = list(map(Matrix.parse_matrix_row_reply, reply_lines_stripped))
                    if mit.all_equal(len(row) for row in entries):
                        return Matrix(entries)
                    else:
                        raise ValueError('Строки матрицы имеют различные длины.')
                else:
                    raise ValueError('Строки матрицы неверно обрамлены.')
        else:
            raise ValueError('Матрица неверно обрамлена.')

    @staticmethod
    def hstack(*matrices):
        entries = list(m.entries for m in matrices)
        if mit.all_equal(m.shape()[0] for m in matrices):
            return Matrix([list(it.chain(*rows)) for rows in zip(*entries)])
        else:
            raise IndexError('Матрицы имеют различные высоты.')

    @staticmethod
    def vstack(*matrices):
        entries = list(m.entries for m in matrices)
        if mit.all_equal(m.shape()[1] for m in matrices):
            return Matrix(it.chain.from_iterable(entries))
        else:
            raise IndexError('Матрицы имеют различные ширины.')

    @staticmethod
    def identity(n):
        return Matrix(((int(i == j) for j in range(n)) for i in range(n)))

    @staticmethod
    def zeros(m, n):
        return Matrix([[0] * n] * m)

    def transpose(self):
        return Matrix(zip(*self.entries))

    def row_mult(self, i, x):
        self.entries[i] = [x * a for a in self.entries[i]]
        return self

    def row_swap(self, i, j):
        self.entries[i], self.entries[j] = self.entries[j], self.entries[i]
        return self

    def row_add(self, i, j, x):
        self.entries[i] = [a + x * b for a, b in zip(self.entries[i], self.entries[j])]
        return self

    def ref(self, reduced=False, output_pivots=False):
        a = Matrix(self.entries)
        m = len(a.entries)
        n = len(a.entries[0])
        pr, pc = 0, 0  # pivot row and pivot column
        pivots = []
        while pr < m and pc < n:
            new_pr = min(range(pr, m), key=lambda i: abs(a.entries[i][pc] or inf))
            if a.entries[new_pr][pc] in (0, inf):
                pc += 1
            else:
                pivots.append(pc)
                a.row_swap(pr, new_pr)
                for r in range(pr + 1, m):
                    a.row_add(r, pr, -a.entries[r][pc] / a.entries[pr][pc])
                if reduced:
                    a.row_mult(pr, 1 / a.entries[pr][pc])
                pc += 1
                pr += 1
        if reduced:
            for pr, pc in reversed(list(enumerate(pivots))):
                for r in range(pr):
                    a.row_add(r, pr, -a.entries[r][pc])
        return (a, pivots) if output_pivots else a

    def is_row_echelon_form(self):
        pivots = [next((i for i, x in enumerate(row) if x), None) for row in self.entries]
        return all(d is None or isinstance(c, int) and isinstance(d, int) and c < d for c, d in mit.pairwise(pivots))

    def __add__(self, other):
        m1, n1 = self.shape()
        m2, n2 = other.shape()
        if m1 == m2 and n1 == n2:
            s = ((e1 + e2 for e1, e2 in zip(row1, row2)) for row1, row2 in zip(self.entries, other.entries))
            return Matrix(s)
        else:
            raise IndexError('Размеры матриц несовместимы для сложения: {}x{} and {}x{}'.format(m1, n1, m2, n2))

    def __rmul__(self, other):
        return Matrix([[other * e for e in row] for row in self.entries])

    def __neg__(self):
        return Matrix(((-e for e in row) for row in self.entries))

    def __matmul__(self, other):
        m1, n1 = self.shape()
        m2, n2 = other.shape()
        if n1 == m2:
            prod = [[sum(r * c for r, c in zip(row, col)) for col in zip(*other.entries)] for row in self.entries]
            return Matrix(prod)
        else:
            raise IndexError('Размеры матриц несовместимы для умножения: {}x{} и {}x{}.'.format(m1, n1, m2, n2))

    def inv(self):
        m, n = self.shape()
        if m == n:
            ai = Matrix.hstack(self, Matrix.identity(m))
            rref, pivots = ai.ref(reduced=True, output_pivots=True)
            if pivots[-1] == m - 1:
                return rref[:, n:]
            else:
                raise ValueError('Матрица необратима.')
        else:
            raise IndexError('Неквадратная матрица.')

    def det(self):
        m, n = self.shape()
        if m == n:
            ref = self.ref()
            return reduce(mul, (ref[i, i] for i in range(n)))
        else:
            raise IndexError('Определитель определен для квадратных матриц, дана {}x{}.'.format(m, n))


def linear_solve(mat: Matrix):
    rref, pivots = mat.ref(reduced=True, output_pivots=True)
    n = rref.shape()[1] - 1
    if pivots[-1] == n:
        return None
    else:
        x = [0] * n
        for i, p in enumerate(pivots):
            x[p] = rref.entries[i][n]
    return Matrix(zip(*[x]))


def kernel_basis(mat: Matrix, output_pivots=False):
    m, n = mat.shape()
    rref, pivots = mat.ref(reduced=True, output_pivots=True)
    pivots_set = set(pivots)
    entries = []
    for j in range(n):
        if j not in pivots_set:
            col = [0] * n
            col[j] = 1
            for i, p in enumerate(pivots):
                if p < j:
                    col[p] = -rref[i, j]
            entries.append(col)
    basis = Matrix(zip(*entries))
    return (basis, pivots) if output_pivots else basis


def randmat(m, n, entries_lim=3):
    return [random.choices(range(-entries_lim, entries_lim + 1), k=n) for _ in range(m)]


def random_glnq(n, entries_lim=3):
    a = Matrix([[0]])
    while a.det() == 0:
        a = Matrix(randmat(n, n, entries_lim=entries_lim))
    return a


def random_glnq_small_det(n, entries_lim=3, det_lim=5):
    a = Matrix([[0]])
    while not(0 < abs(a.det()) <= det_lim):
        a = Matrix(randmat(n, n, entries_lim=entries_lim))
    return a


def random_rref(m, n, pivots_num, entries_lim=3, output_pivots=False):
    pivots = [0] + list(sorted(random.sample(range(1, n), k=pivots_num - 1)))
    pivots_set = set(pivots)
    entries = [[0] * n for _ in range(m)]
    for i in range(m):
        if i < len(pivots):
            entries[i][pivots[i]] = 1
            for j in range(pivots[i] + 1, n):
                if j not in pivots_set:
                    entries[i][j] = random.choice((1, -1)) * random.randint(1, entries_lim)
    a = Matrix(entries)
    return (a, pivots) if output_pivots else a

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
            def converter(x):
                return Fraction(*x)
        self.entries = [list(map(converter, row)) for row in entries]

    def __getitem__(self, item):
        m, n = self.shape()
        if isinstance(item, int):
            if m == 1:
                return self.entries[0][item]
            elif n == 1:
                return self.entries[item][0]
            else:
                raise IndexError('Один индекс не для столбца или строки.')
        elif isinstance(item, slice):
            if m == 1:
                return Matrix([self.entries[0][item]])
            elif n == 1:
                return Matrix(self.entries[item])
            else:
                raise IndexError('Один индекс не для столбца или строки.')
        elif isinstance(item, tuple) and len(item) == 2:
            i1, i2 = item
            if all(isinstance(i, int) for i in item):
                return self.entries[i1][i2]
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

    def __setitem__(self, key, value):
        m, n = self.shape()
        if isinstance(key, int):
            if m == 1:
                self.entries[0][key] = value
            elif n == 1:
                self.entries[key][0] = value
            else:
                raise IndexError('Один индекс не для столбца или строки.')
        elif isinstance(key, slice):
            if m == 1:
                self[0, key] = value
            elif n == 1:
                self[key, 0] = value
            else:
                raise IndexError('Один индекс не для столбца или строки.')
        elif isinstance(key, tuple) and len(key) == 2:
            i1, i2 = key
            if all(isinstance(i, int) for i in key):
                self.entries[i1][i2] = value
            elif isinstance(i1, int) and isinstance(i2, slice):
                self.entries[i1][i2] = value.entries[0]
            elif isinstance(i1, slice) and isinstance(i2, int):
                for i, row in enumerate(self.entries[i1]):
                    row[i2] = value[i, 0]
            elif isinstance(i1, slice) and isinstance(i2, slice):
                for row_self, row_val in zip(self.entries[i1], value.entries):
                    row_self[i2] = row_val
            else:
                raise IndexError('Некорректный индекс.')
        else:
            raise IndexError('Некорректный индекс.')

    def cols(self):
        return (self[:, j] for j in range(self.shape()[1]))

    def rows(self):
        return (self[i, :] for i in range(self.shape()[0]))

    def shape(self):
        return len(self.entries), len(self.entries[0])

    def __eq__(self, other):
        return self.entries == other.entries

    def __bool__(self):
        return any(any(row) for row in self.entries)

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

    def col_mult(self, i, x):
        for row in self.entries:
            row[i] *= x
        return self

    def col_swap(self, i, j):
        for row in self.entries:
            row[i], row[j] = row[j], row[i]
        return self

    def col_add(self, i, j, x):
        for row in self.entries:
            row[i] += x * row[j]
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


def lcm(*numbers):
    a = list(numbers)
    while len(a) > 1:
        last = a.pop()
        prev = a[-1]
        a[-1] = last * prev // gcd(last, prev)
    return a[0]


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
            denom_common = lcm(*[x.denominator for x in col])
            col = [x * denom_common for x in col]
            numer_gcd = reduce(gcd, [x.numerator for x in col])
            col = [x // numer_gcd for x in col]
            entries.append(col)
    basis = None
    if entries:
        basis = Matrix(zip(*entries))
    return (basis, pivots) if output_pivots else basis


def integer_linear_solve(ab: Matrix):
    a = ab[:, :-1]
    b = ab[:, -1]
    m, n = a.shape()
    c2 = Matrix.identity(n)
    jt = -1
    for t in range(m):
        # choose a pivot
        for j in range(jt + 1, n):
            new_jt_found = False
            for k in range(t, m):
                if a[k, j] != 0:
                    jt = j
                    if k != t:
                        a.row_swap(t, k)
                        b.row_swap(t, k)
                    if jt != t:
                        a.col_swap(t, jt)
                        c2.col_swap(t, jt)
                        jt = t
                    new_jt_found = True
                    break
            if new_jt_found:
                break
        else:
            break
        # improve the pivot and eliminate entries
        steps = 0
        while (any(a.entries[t][t + 1:]) or any(row[jt] for row in a.entries[t + 1:])) and steps <= 3:
            steps += 1
            # improvint the column
            for k in range(t + 1, m):
                at, ak = a[t, jt], a[k, jt]
                if ak:
                    d, x, y = extgcd(at, ak)
                    bez = Matrix([[x, y], [-ak // d, at // d]])
                    bez_slice = slice(t, k + 1, k - t)
                    a[bez_slice, :] = bez @ a[bez_slice, :]
                    b[bez_slice] = bez @ b[bez_slice]
            # improving the column
            for j in range(jt + 1, n):
                at, aj = a[t, jt], a[t, j]
                if aj:
                    d, x, y = extgcd(at, aj)
                    bez = Matrix([[x, -aj // d], [y, at // d]])
                    bez_slice = slice(jt, j + 1, j - jt)
                    a[:, bez_slice] = a[:, bez_slice] @ bez
                    c2[:, bez_slice] = c2[:, bez_slice] @ bez
    a_diag = list(map(int, (a[i, i] for i in range(min(m, n)))))
    a_diag_extended = list(mit.padded(a_diag, 0, m))
    b_list = [int(b[i]) for i in range(m)]
    if all(di == 0 and bi == 0 or di != 0 and bi % di == 0 for di, bi in zip(a_diag_extended, b_list)):
        sol_first_entries = [[bi // di if di else 0] for di, bi in zip(a_diag, b_list)]
        return c2 @ Matrix(list(mit.padded(sol_first_entries, [0], n)))
    else:
        return None


def extgcd(a: int, b: int):
    """return (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0


def randmat(m, n, entries_lim=3):
    return [random.choices(range(-entries_lim, entries_lim + 1), k=n) for _ in range(m)]


def random_glnq(n, entries_lim=3):
    a = Matrix([[0]])
    while a.det() == 0:
        a = Matrix(randmat(n, n, entries_lim=entries_lim))
    return a


def random_glnq_small_det(n, entries_lim=3, det_lim=5):
    a = Matrix([[0]])
    while not (0 < abs(a.det()) <= det_lim):
        a = Matrix(randmat(n, n, entries_lim=entries_lim))
    return a


def random_glnz(n):
    a = Matrix.identity(n)
    for i in range(8):
        c = Matrix([
            [random.choice((1, -1)) if i == j else random.randint(-1, 1) if i < j else 0 for j in range(n)]
            for i in range(n)])
        if i % 2:
            c = c.transpose()
        a = c @ a
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

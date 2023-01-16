from linear.matrix import Matrix, linear_solve
import itertools as it
import more_itertools as mit
from functools import reduce
import random
import re


def poly_mul(f, g):
    return tuple(sum(f[i] * g[k - i] for i in range(max(0, k - len(g) + 1), min(k + 1, len(f))))
                 for k in range(len(f) + len(g) - 1))


def horner(f, c):
    gr = []
    for a in reversed(f):
        b = b * c + a if gr else a
        gr.append(b)
    return tuple(gr[-2::-1]), gr[-1]


def generate():
    problems = ['3 -15 8\n1 2 2 1']
    for degrees in [(1, 1, 1), (2, 2), (1, 2, 3, 4), (3, 3, 3, 3, 3)]:
        points = random.sample(range(-5, 6), k=len(degrees))
        f_deg = random.randint(1, sum(degrees) - 1)
        f = random.choices(range(-5, 6), k=f_deg) + [random.randint(1, 5)]
        f_str = ' '.join(map(str, f))
        g_str = ' '.join(map(str, mit.interleave(points, degrees)))
        problems.append('{}\n{}'.format(f_str, g_str))
    return problems


def check(reply, clue):
    if reply == clue:
        return True
    reply_lines = reply.splitlines()
    clue_lines = clue.splitlines()
    if len(reply_lines) != len(clue_lines):
        return False, 'Неверное количество строк в ответе.'
    line_re = re.compile('(-?\d+): ([-\d/ ]+)$')
    line_matches = [line_re.match(line) for line in reply_lines]
    if not all(line_matches):
        return False, 'Неверный формат строк.'
    values_strs = [m.group(2).split() for m in line_matches]
    if not all(len(row) == len(clue_line.split()) - 1 for row, clue_line in zip(values_strs, clue_lines)):
        return False, 'Неверное число элементов в строке.'
    values_re = re.compile('(-?\d+(/\d+)?)$')
    values_matches = [values_re.match(vs) for row in values_strs for vs in row]
    if not all(values_matches):
        return False, 'Неверное представление элементов строки.'
    return False, 'Неверный ответ.'


def solve(dataset):
    f_str, g_str = dataset.splitlines()
    f = list(map(int, f_str.split()))
    g_factors = list(mit.chunked(map(int, g_str.split()), 2))
    points = [gf[0] for gf in g_factors]
    powers = [gf[1] for gf in g_factors]
    num_vars = sum(powers)
    g = reduce(poly_mul, it.chain.from_iterable(it.repeat((-c, 1), n) for c, n in g_factors))
    columns_transposed = []
    for c, n in g_factors:
        h = g
        for _ in range(n):
            h = horner(h, c)[0]
            columns_transposed.append(list(mit.padded(h, fillvalue=0, n=num_vars)))
    columns_transposed.append(list(mit.padded(f, fillvalue=0, n=num_vars)))
    ab = Matrix(zip(*columns_transposed))
    coeffs = linear_solve(ab).transpose().entries[0]
    return '\n'.join('{}: {}'.format(p, ' '.join(map(str, ais))) for p, ais in zip(points, mit.split_into(coeffs, powers)))

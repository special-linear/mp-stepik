from operator import add, mul
from functools import reduce
from itertools import zip_longest
from random import randint, choice, sample
import re


def prod(seq):
    return reduce(mul, seq)


def horner(f, c):
    gr = []
    for a in reversed(f):
        b = b * c + a if gr else a
        gr.append(b)
    return tuple(gr[-2::-1]), gr[-1]


def poly_mul(f, g):
    return tuple(sum(f[i] * g[k - i] for i in range(max(0, k - len(g) + 1), min(k + 1, len(f))))
                 for k in range(len(f) + len(g) - 1))


def interpolate(xs, vs):
    fs, ds = [], []
    for i, xi in enumerate(xs):
        fi, di = (vs[i],), 1
        for j in range(len(xs)):
            if j != i:
                fi = poly_mul(fi, (-xs[j], 1))
                di *= (xs[i] - xs[j])
        fs.append(fi)
        ds.append(di)
    pds = prod(ds)
    fds = [poly_mul(fi, (pds // di,)) for fi, di in zip(fs,ds)]
    fpds = reduce(lambda f1, f2: tuple(map(add, f1, f2)), fds)
    f = [c // pds for c in fpds]
    while f[-1] == 0 and len(f) > 1:
        del f[-1]
    return tuple(f)


def generate():
    problems = [('0 1 2\n1 2 5', (1, 0, 1))]
    for num_problem in range(1, 10):
        deg = min(num_problem, 5, 15 - 2 * num_problem)
        num_points = min(num_problem + 1, 7)
        good_poly = False
        while not good_poly:
            f = [randint(-5, 5) for _ in range(deg)] + [choice((1, -1)) * randint(1, 5)] if num_problem < 9 else (0,)
            xs = sample(range(-10, 10), k=num_points)
            ds = [prod(xs[i] - xs[j] for j in range(len(xs)) if i != j) for i in range(len(xs))]
            pds = prod(ds)
            good_poly = all(abs(c * pds) < 2**60 for c in f)
        vs = [horner(f, x)[1] for x in xs]
        problem = '\n'.join(' '.join(map(str, data)) for data in (xs, vs))
        problems.append((problem, f))
    return problems


def check(reply, clue):
    clue = tuple(clue)
    f_strs = reply.strip().split()
    coeff_regex = re.compile('-?\d+$')
    if all(coeff_regex.match(c) for c in f_strs):
        f = tuple(map(int, f_strs))
        if f == clue:
            return True
        elif tuple(reversed(f)) == clue:
            return False, 'Возможно, неверный формат вывода многочленов (порядок).'
        elif len(f) > len(clue) and all(a == b for a, b in zip_longest(f, clue, fillvalue=0)):
            return False, 'Возможно, неверный формат вывода многочленов (степень и нулевые коэффициенты).'
        elif len(f) == 0 and clue == (0,):
            return False, 'Неправильно ты, дядя Федор, нулевые многочлены записываешь!'
        else:
            return False, 'Неверный ответ.'
    else:
        return False, 'Неверный формат вывода (целые коэффициенты, пробелы, etc.). {}'.format(reply)


def solve(dataset):
    xs, vs = (tuple(map(int, s.split())) for s in dataset.splitlines())
    return ' '.join(map(str, interpolate(xs, vs)))

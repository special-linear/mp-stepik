from linear.matrix import Matrix, linear_solve
from fractions import Fraction
from math import factorial, gcd
import itertools as it
import more_itertools as mit
from operator import mul
import random
import re


def horner(f, c):
    gr = []
    for a in reversed(f):
        b = b * c + a if gr else a
        gr.append(b)
    return tuple(gr[-2::-1]), gr[-1]


def generate():
    problems_handcrafted = [
        [[0, 1], [1, 4], [2, 9]],
        [[2, 1, 1, 2, 6, 24]],
        [[1, 6, 4], [2, 11]],
    ]
    problems_full_deg = []
    problems_small_deg = []
    for degrees in [(1, 1, 1, 1, 1, 1), (2, 2, 2), (10,), (1, 2, 3, 4, 5), (5, 4, 3, 2, 1)]:
        if len(degrees) > 1:
            points = random.sample(range(-5, 6), k=len(degrees))
        else:
            points = [random.randint(1, 5)]
        conditions = [[p] + random.choices(range(-5, 6), k=d) for p, d in zip(points, degrees)]
        problems_full_deg.append(conditions)
        f = random.choices(range(-5, 6), k=sum(degrees) // 2) + [random.randint(1, 3)]
        conditions = []
        for p, d in zip(points, degrees):
            cond = []
            h = f
            for k in range(d):
                h, v = horner(h, p)
                cond.append(factorial(k) * v)
                if not h:
                    break
            conditions.append([p] + list(mit.padded(cond, fillvalue=0, n=d)))
        problems_small_deg.append(conditions)
    problems_zero = [
        [[0, 0, 0, 0 ,0]],
        [[1, 0], [2, 0], [3, 0]],
        [[1, 0, 0], [2, 0, 0]],
        [[1, 0, 0, 0, 0, 0, 1], [-1, 0, 0, 0, 0, 0, 1]],
    ]
    problems = it.chain(problems_handcrafted, problems_full_deg, problems_small_deg, problems_zero)
    return ['\n'.join(' '.join(map(str, cond)) for cond in conditions) for conditions in problems]


def check(reply: str, clue:str):
    if reply == clue:
        return True
    if '\n' in reply:
        return False, 'Ответ содержит более одной строки.'
    entry_re = re.compile('(-?\d+)(/(\d+))?$')
    entries_strs = reply.split()
    entries_matches = [entry_re.match(es) for es in entries_strs]
    if not all(entries_matches):
        return False, 'Неверный формат элементов ответа.'
    if any(gcd(int(m.group(1)), int(m.group(3))) != 1 for m in entries_matches):
        return False, 'Неверный формат вывода рациональных чисел.'
    coeffs = list(map(Fraction, entries_strs))
    if ' '.join(map(str, reversed(coeffs))) == clue:
        return False, 'Вероятно, неправильный порядок коэффициентов многочлена.'
    coeffs_stripped = coeffs[:]
    while coeffs_stripped[-1] == 0 and len(coeffs_stripped) > 1:
        del coeffs_stripped[-1]
    if ' '.join(map(str, coeffs_stripped)) == clue:
        return False, 'Неверный формат ответа: нулевые старшие коэффициенты.'
    clue_entries = clue.split()
    if all(rs == cs for rs, cs in zip(entries_strs, clue.split())):
        if len(entries_strs) < len(clue_entries):
            return False, 'Ответ выведен не полностью.'
        return False, 'Ответ содержит лишние элементы.'
    if reply.strip() == '' and clue == '0':
        return False, 'Неправильно ты, дядя Федор, нулевые многочлены записываешь.'
    return False, 'Ответ неверный.'


def solve(dataset):
    conditions = [list(map(int, line.split())) for line in dataset.splitlines()]
    cond_lens = list(map(len, conditions))
    f_deg = sum(cond_lens) - len(conditions) - 1
    dc = [1] * (f_deg + 1)
    diffs_coeffs = [dc]
    for k in range(1, max(cond_lens) - 1):
        dc = list(map(mul, it.islice(dc, 1, None), it.count(1)))
        diffs_coeffs.append(dc)
    equations = []
    for cond in conditions:
        c, *vs = cond
        powers = [1] + list(it.accumulate(it.repeat(c, f_deg), mul))
        for v, dc in zip(vs, diffs_coeffs):
            eqn = [0] * (f_deg + 1 - len(dc)) + list(map(mul, powers, dc)) + [v]
            equations.append(eqn)
    sol = linear_solve(Matrix(equations))
    f = sol.transpose().entries[0]
    while f[-1] == 0 and len(f) > 1:
        del f[-1]
    return ' '.join(map(str, f))

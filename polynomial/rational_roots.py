from itertools import chain
from operator import neg
from math import gcd
import re
from collections import Counter
from random import randint, choice


def horner(f, c):
    gr = []
    for a in reversed(f):
        b = b * c + a if gr else a
        gr.append(b)
    return tuple(gr[-2::-1]), gr[-1]


def divisors(n):
    return [k for k in range(1, abs(n) // 2 + 1) if n % k == 0] + [n]


def root_multiplicity(f, c):
    m = -1
    r = 0
    while r == 0:
        f, r = horner(f, c)
        m += 1
    return m


def rational_roots(f):
    numers = divisors(next((a for a in f if a), f[0]))
    numers = list(chain(numers, map(neg, numers)))
    denoms = divisors(f[-1])
    deg = len(f) - 1
    roots = []
    all_roots_found = False
    if f[0] == 0:
        roots.append(((0, 1), root_multiplicity(f, 0)))
    for q in denoms:
        fq = tuple(a * q**(deg - i) for i, a in enumerate(f))
        for p in numers:
            if gcd(p, q) == 1:
                m = root_multiplicity(fq, p)
                if m > 0:
                    roots.append(((p, q), m))
                    if sum(r[1] for r in roots) == deg:
                        all_roots_found = True
                        break
        if all_roots_found:
            break
    return roots


def poly_mul(f, g):
    return tuple(sum(f[i] * g[k - i] for i in range(max(0, k - len(g) + 1), min(k + 1, len(f))))
                 for k in range(len(f) + len(g) - 1))


def generate():
    problems = [('4 4 -15 -18', [((1 ,2), 1), ((-2, 3), 2)])]
    for num_problem in range(29):
        roots = []
        num_roots = min(4, 1 + num_problem)
        if 10 <= num_problem < 25:
            num_roots = 0
        while len(roots) < num_roots:
            p = choice((-1, 1)) * randint(1, 9)
            q = randint(1, 9)
            if gcd(p, q) == 1 and (p, q) not in roots:
                roots.append((p, q))
        roots = [(r, randint(1, 3)) for r in roots]
        if num_problem >= 20:
            roots.append(((0, 1), randint(2, 3)))
        f = (1,)
        for r, m in roots:
            for i in range(m):
                f = poly_mul(f, (-r[0], r[1]))
        for i in range(randint(0, 2)):
            g = None
            while not g or rational_roots(g):
                g = tuple(choice((-1, 1)) * randint(1, 5) for j in range(randint(3, 4)))
            f = poly_mul(f, g)
        problems.append((' '.join(map(str, f)), roots))
    return problems


def check(reply, clue):
    if reply == 'No roots':
        if clue == []:
            return True
        elif len(clue) == 1 and clue[0][0] == 0:
            return (False, 'Не учтен единственный корень 0.')
        else:
            return (False, 'Не обнаружены существующие рациональные корни.')
    else:
        reply_root_strs = reply.splitlines()
        reply_roots = Counter()
        root_regex = re.compile('(-?\d+)/(\d+) (\d+)$')
        for reply_root_str in reply_root_strs:
            match = root_regex.match(reply_root_str)
            if match:
                p, q, m = map(int, match.groups())
                reply_roots[(p, q)] = m
            else:
                return (False, 'Неверный формат ответа.')
        clue_roots = Counter()
        # not simply Counter(dict(clue)) because JSON deserialization turns the clue from generate() into a nested list
        for entry in clue:
            r, m = entry[0], entry[1]
            clue_roots[tuple(r)] = m
        if reply_roots == clue_roots:
            return True
        elif 0 in clue_roots and 0 not in reply_roots:
            return (False, 'Не учтен корень 0.')
        elif set(reply_roots.keys()) == set(clue_roots.keys()):
            return (False, 'Неверно вычислены кратности.')
        else:
            return (False, 'Указаны не все корни или указаны лишние корни.')


def solve(dataset):
    f = tuple(map(int, dataset.split()))
    roots = rational_roots(f)
    if roots:
        return '\n'.join('{}/{} {}'.format(r[0], r[1], m) for r, m in roots)
    else:
        return 'No roots'

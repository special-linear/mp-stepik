from random import randint, choice


def horner(f, c):
    gr = []
    for a in reversed(f):
        b = b * c + a if gr else a
        gr.append(b)
    return tuple(gr[-2::-1]), gr[-1]


def taylor(f, c):
    g = []
    while f:
        f, b = horner(f, c)
        g.append(b)
    return tuple(g)


def poly_mul(f, g):
    return tuple(sum(f[i] * g[k - i] for i in range(max(0, k - len(g) + 1), min(k + 1, len(f))))
                 for k in range(len(f) + len(g) - 1))


def generate():
    problems = []
    for i in range(9):
        f = tuple([randint(-99, 99) for j in range(i)] + [choice((1, -1)) * randint(1, 99)])
        c = choice((1, -1)) * randint(1, 99)
        problem = '{}\n{}'.format(' '.join(map(str, f)), c)
        solution = ' '.join(map(str, taylor(f, c)))
        problems.append((problem, solution))
    return problems


def check(reply, clue):
    return reply.strip() == clue.strip()


def solve(dataset):
    f, c = dataset.splitlines()
    f = tuple(map(int, f.split()))
    c = int(c)
    return ' '.join(map(str, taylor(f, c)))
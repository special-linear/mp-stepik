from linear.matrix import Matrix, randmat
import random


def generate():
    matrices_handcrafted = [
        [[1, 0], [0, 1], [0, 0]]
    ]
    problems = [(a.input_repr(), a.serialize()) for a in map(Matrix, matrices_handcrafted)]
    for h, w in [(4, 3), (5, 1), (5, 2), (5, 4), (10, 5), (10, 9), (20, 3), (20, 15), (20, 19)]:
        cols_independend = False
        while not cols_independend:
            a = Matrix(randmat(h, w, entries_lim=10))
            cols_independend = a.ref(output_pivots=True)[1][-1] == w - 1
        problems.append((a.input_repr(), a.serialize()))
    return problems


def check(reply, clue):
    try:
        b = Matrix.parse_matrix_reply(reply)
        a = Matrix(clue, entries_type=tuple)
        ab = Matrix.hstack(a, b)
        ab_shape = ab.shape()
        if ab_shape[0] != ab_shape[1]:
            return False, "Неверное количество векторов в ответе."
        if ab.ref(output_pivots=True)[1][-1] != ab_shape[0] - 1:
            return False, "Не все векторы в ответе линейно независимы с векторами исходного набора."
        return True
    except ValueError as e:
        return False, e.args[0]


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    a = Matrix(entries)
    h, w = a.shape()
    is_basis = False
    while not is_basis:
        completion = Matrix([random.choices(range(-10, 11), k=h - w) for _ in range(h)])
        is_basis = Matrix.hstack(a, completion).ref(output_pivots=True)[1][-1] == h - 1
    return str(completion)

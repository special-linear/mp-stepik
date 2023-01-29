from linear.matrix import Matrix, random_rref, random_glnq


# the input is a matrix, the problem is to pick a maximal linearly independent subset of columns
# output is the list of numbers of columns (numbering from 0)


def generate():
    matrices_handcrafted = [
        [[1, 2, 3], [4, 5, 0], [6, 0, 0]],
        [[1, 0, 1, 1], [0, 1, 1, 1], [0, 0, 0, 1]]
    ]
    problems = [
        (a.input_repr(), (len(a.ref(output_pivots=True)[1]), a.serialize())) for a in map(Matrix, matrices_handcrafted)
    ]
    for m, n, pivots_num in [(3, 5, 3), (4, 4, 3), (5, 10, 5), (20, 50, 10), (1, 10, 1), (10, 1, 1)]:
        rref = random_rref(m, n, pivots_num=pivots_num)
        c = random_glnq(m)
        a = c @ rref
        problems.append((a.input_repr(), (pivots_num, a.serialize())))
    return problems


def check(reply, clue):
    if '\n' in reply:
        return False, 'Ответ содержит более одной строки.'
    reply_entries_strs = reply.split()
    if not all(es.isdecimal() for es in reply_entries_strs):
        return False, 'Ответ содержит нечисловые значения.'
    pivots_num, a_entries = clue
    if len(reply_entries_strs) > pivots_num:
        return False, 'Ответ содержит неверное количество индексов (есть лишние).'
    if len(reply_entries_strs) < pivots_num:
        return False, 'Ответ содержит неверное количество индексов (меньше требуемого).'
    reply_entries = list(map(int, reply_entries_strs))
    a = Matrix(a_entries, entries_type=tuple)
    m, n = a.shape()
    if not all(0 <= i < n for i in reply_entries):
        return False, 'Ответ содержит некорректные индексы.'
    reply_columns = Matrix.hstack(*[a[:, i] for i in reply_entries])
    if len(reply_columns.ref(output_pivots=True)[1]) != len(reply_entries):
        return False, 'Указанные столбцы линейно зависимы.'
    return True


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    a = Matrix(entries)
    print(a)
    pivots = a.ref(output_pivots=True)[1]
    return ' '.join(map(str, pivots))


for dataset, clue in generate():

    sol = solve(dataset)
    print(check(sol, clue))

# print(check('1 2 3 a b c \n   d\n \n\n\n sf dgd', 0))
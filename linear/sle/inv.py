from linear.matrix import Matrix, random_glnq, random_glnq_small_det


def generate():
    matrices = [Matrix([[1, 2], [3, 4]])]
    matrices += [random_glnq_small_det(n, entries_lim=10 // n + 1, det_lim=10**4) for n in range(2, 21)]
    problems = [(a.input_repr(), a.serialize()) for a in matrices]
    return problems


def check(reply, clue):
    try:
        reply_mat = Matrix.parse_matrix_reply(reply)
        m, n = reply_mat.shape()
        if m != n:
            return False, 'Ответ не является квадратной матрицей'
        if m != len(clue):
            return False, 'Размер матрицы в ответе не совпадает с размером матрицы в задаче.'
        clue_mat = Matrix(clue, entries_type=tuple)
        idn = Matrix.identity(n)
        return clue_mat @ reply_mat == idn or (False, 'Матрица в ответе не является обратной к матрице в задаче.')
    except ValueError as e:
        return False, e.args[0]


def solve(dataset):
    entries = (map(int, row.split()) for row in dataset.splitlines())
    a = Matrix(entries)
    return str(a.inv())


for dataset, clue in generate():
    sol = solve(dataset)
    print(sol)
    print(check(sol, clue))
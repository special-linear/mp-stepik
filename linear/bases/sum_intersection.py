from linear.matrix import Matrix, kernel_basis, random_rref, random_glnq


def generate():
    matrices = [
        (Matrix([[1, 0, 1], [0, 1, 1], [0, 0, 0]]), Matrix([[0, 0], [1, 0], [0, 1]])),
        (Matrix([[1, 0, 1], [0, 1, 1], [0, 0, 0]]), Matrix([[0, 0, 0], [1, 0, 1], [0, 1, 1]])),
        (Matrix([[1,0], [0, 1], [0, 0], [0, 0]]), Matrix([[0, 0], [0, 0], [1, 0], [0, 1]])),
    ]
    for m, n1, n2 in [(4, 3, 3), (5, 4, 4), (5, 4, 3), (10, 7, 7)]:
        a1 = Matrix.vstack(random_glnq(n1), Matrix.zeros(m - n1, n1))
        a2 = Matrix.vstack(Matrix.zeros(m - n2, n2), random_glnq(n2))
        a = random_glnq(m, entries_lim=2) @ Matrix.hstack(a1, a2)
        matrices.append((a[:, :n1], a[:, -n2:]))
    for m, n1, n2, pivots_num in [(3, 3, 3, 3), (4, 4, 3, 3), (5, 5, 5, 5), (3, 3, 3, 2), (10, 10, 10, 5)]:
        rref = random_rref(m, n1 + n2, pivots_num=pivots_num)
        a = random_glnq(m, entries_lim=2) @ rref
        matrices.append((a[:, :n1], a[:, -n2:]))
    for m, n1, n2 in [(4, 2, 2), (5, 3, 2), (10, 3, 3), (5, 1, 2), (5, 2, 1), (5, 1, 1)]:
        a1 = Matrix.vstack(random_glnq(n1), Matrix.zeros(m - n1, n1))
        a2 = Matrix.vstack(Matrix.zeros(m - n2, n2), random_glnq(n2))
        a = random_glnq(m, entries_lim=2) @ Matrix.hstack(a1, a2)
        matrices.append((a[:, :n1], a[:, -n2:]))
    return [('{}\n\n{}'.format(a1.input_repr(), a2.input_repr()), (a1.serialize(), a2.serialize())) for a1, a2 in matrices]


def check(reply, clue):
    if '\n\n' not in reply:
        return False, 'Неверный формат ответа.'
    answer_parts = reply.split('\n\n')
    if len(answer_parts) != 2:
        return False, 'Неверный формат ответа (количество разделенных пустыми строками частей).'
    sum_basis_str, int_basis_str = answer_parts
    a1, a2 = (Matrix(a, entries_type=tuple) for a in clue)
    sum_basis_correct, int_basis_correct = sum_intersection(a1, a2)
    try:
        sum_basis = Matrix.parse_matrix_reply(sum_basis_str)
        if sum_basis.shape()[0] != a1.shape()[0]:
            return False, 'Высота столбцов в базисе суммы не совпадает с высотой исходных столбцов.'
        if sum_basis.ref(output_pivots=True)[1][-1] != sum_basis.shape()[1] - 1:
            return False, 'Столбцы матрицы, отвечающей базису суммы, линейно зависимы.'
        if sum_basis.shape()[1] != sum_basis_correct.shape()[1]:
            return False, 'Размерность суммы вычислена неверно.'
        if Matrix.hstack(sum_basis, sum_basis_correct).ref(output_pivots=True)[1][-1] != sum_basis.shape()[1] - 1:
            return False, 'Указанный базис суммы порождает неверное подпространство.'
        # all checks for the sum basis should be done at this point
        if int_basis_str == 'Zero':
            if int_basis_correct is not None:
                return False, 'Пересечение нетривиально вопреки ответу.'
        else:
            if int_basis_correct.shape()[1] == 0:
                return False, 'Пересечение нулевое, а в ответе не "Zero".'
            int_basis = Matrix.parse_matrix_reply(int_basis_str)
            if int_basis.shape()[0] != a1.shape()[0]:
                return False, 'Высота столбцов в базисе пересечения не совпадает с высотой исходных столбцов.'
            if int_basis.ref(output_pivots=True)[1][-1] != int_basis.shape()[1] - 1:
                return False, 'Столбцы матрицы, отвечающей базису пересечения, линейно зависимы.'
            if int_basis.shape()[1] != int_basis_correct.shape()[1]:
                return False, 'Размерность пересечения вычислена неверно.'
            if Matrix.hstack(int_basis, int_basis_correct).ref(output_pivots=True)[1][-1] != int_basis.shape()[1] - 1:
                return False, 'Указанный базис пересечения порождает неверное подпространство.'
        return True
    except ValueError as e:
        return False, e.args[0]


def sum_intersection(a1, a2):
    m, n = a1.shape()
    a = Matrix.hstack(a1, a2)
    a_ker_basis, pivots = kernel_basis(a, output_pivots=True)
    sum_basis = Matrix.hstack(*[a[:, i] for i in pivots])
    int_basis = None
    if a_ker_basis is not None:
        int_generators = a1 @ a_ker_basis[:n, :]
        int_generators_pivots = int_generators.ref(output_pivots=True)[1]
        int_basis = Matrix.hstack(*[int_generators[:, i] for i in int_generators_pivots])
    return sum_basis, int_basis


def solve(dataset):
    matrices_strs = dataset.split('\n\n')
    entries = ((map(int, row.split()) for row in entries_strs.splitlines()) for entries_strs in matrices_strs)
    a1, a2 = map(Matrix, entries)
    sum_basis, int_basis = sum_intersection(a1, a2)
    return '{}\n\n{}'.format(sum_basis, str(int_basis) if int_basis is not None else 'Zero')

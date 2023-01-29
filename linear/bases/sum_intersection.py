from linear.matrix import Matrix, kernel_basis, random_rref, random_glnq


# input is two matrices of the same height separated by a blank line
# return two matrices whose columns form bases for the sum and intersection of the images
# output is two matrices separated by a blank line


def generate():
    matrices = []
    for m, n1, n2 in [(4, 3, 3), (5, 4, 4), (5, 4, 3), (10, 7, 7)]:
        a1 = Matrix.vstack(random_glnq(n1), Matrix.zeros(m - n1, n1))
        a2 = Matrix.vstack(Matrix.zeros(m - n2, n2), random_glnq(n2))
        a = random_glnq(m, entries_lim=2) @ Matrix.hstack(a1, a2)
        matrices.append((a[:, :n1], a[:, -n2:]))
    for m, n1, n2, pivots_num in [(3, 3, 3, 3), (4, 4, 3, 3), (5, 5, 5, 5), (10, 10, 10, 5)]:
        rref = random_rref(m, n1 + n2, pivots_num=pivots_num)
        a = random_glnq(m, entries_lim=2) @ rref
        matrices.append((a[:, :n1], a[:, -n2:]))
    for m, n1, n2 in [(4, 2, 2), (5, 3, 2), (10, 3, 3), (5, 1, 2), (5, 2, 1), (5, 1, 1)]:
        a1 = Matrix.vstack(random_glnq(n1), Matrix.zeros(m - n1, n1))
        a2 = Matrix.vstack(Matrix.zeros(m - n2, n2), random_glnq(n2))
        a = random_glnq(m, entries_lim=2) @ Matrix.hstack(a1, a2)
        matrices.append((a[:, :n1], a[:, -n2:]))
    return ['{}\n\n{}'.format(a1.input_repr(), a2.input_repr()) for a1, a2 in matrices]


def check(reply, clue):
    pass


def solve(dataset):
    matrices_strs = dataset.split('\n\n')
    entries = ((map(int, row.split()) for row in entries_strs.splitlines()) for entries_strs in matrices_strs)
    a1, a2 = map(Matrix, entries)
    m, n = a1.shape()
    a = Matrix.hstack(a1, a2)
    a_ker_basis, pivots = kernel_basis(a, output_pivots=True)
    sum_basis = Matrix.hstack(*[a[:, i] for i in pivots])
    int_basis = a1 @ a_ker_basis[:n, :]
    int_basis = Matrix.hstack(*filter(bool, int_basis.cols())) or Matrix.zeros(m, 1)
    return '{}\n\n{}'.format(sum_basis, int_basis)
